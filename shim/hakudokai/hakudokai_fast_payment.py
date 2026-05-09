#!/usr/bin/env python3
"""
hakudokai_fast_payment.py — 高速会計判定 (Phase C-1, DD-041 §6)

子供医療費助成対象の患者を年齢 × clinic_payment_settings から自動判定し、
固定額で daily_report_patients に INSERT する。レセコン入力完了を待たない。

設計:
- 入力: patient_id + clinic_id + treatment_date + (option) self_pay_amount
- 処理:
  1. clinic_payment_settings から fast_payment_enabled / age_max / fixed_amount 取得
  2. patient_master から年齢取得 (PII guard 経由、直値非保持)
  3. 年齢 ≤ age_max なら子供 / それ以外なら大人
  4. 子供: daily_report_patients INSERT (fast_payment_status='pending', received_amount=fixed_amount)
  5. 大人: 通常会計判定 (本 script 範囲外、scripts/hakudokai_paylight_integration.py 等へ委譲)
- PII guard: patient_id (uuid) のみ参照、氏名/住所は直書きしない

Usage:
  hakudokai_fast_payment.py --patient-id <uuid> --clinic-id <id> --treatment-date 2026-05-02
  hakudokai_fast_payment.py --patient-id <uuid> --clinic-id <id> --treatment-date 2026-05-02 --self-pay 1500
  hakudokai_fast_payment.py --check-config --clinic-id <id>     # clinic_payment_settings 表示
  hakudokai_fast_payment.py --dry-run ...                        # INSERT skip

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, date, timezone, timedelta

# audit-fix(phase-c1) Critical #4 (L1-E): JST timezone 統一
# UTC 既定値だと JST 00:00-08:59 で前日記帳になる
try:
    from zoneinfo import ZoneInfo  # type: ignore
    _JST = ZoneInfo("Asia/Tokyo")
except Exception:
    _JST = timezone(timedelta(hours=9))


def _today_jst() -> date:
    return datetime.now(_JST).date()

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[fast_payment] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

# Phase R1 PII detector を再利用
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
try:
    from hakudokai_pii_detector import scan_for_pii  # type: ignore
except ImportError:
    scan_for_pii = None  # type: ignore


CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[fast_payment] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _abort_if_pii(text: str, label: str) -> None:
    """PII 混入検出時 abort (Phase R1 二重防御の継承)。"""
    if not text or scan_for_pii is None:
        return
    try:
        matches = list(scan_for_pii(text))
    except Exception:
        return
    if matches:
        sys.stderr.write(
            f"[fast_payment] PII detected in {label}, abort INSERT (matches={len(matches)})\n"
        )
        raise SystemExit(5)


def _fetch_clinic_settings(sb, clinic_id: str) -> dict | None:
    try:
        res = (
            sb.table("clinic_payment_settings")
            .select("*")
            .eq("clinic_id", clinic_id)
            .execute()
        )
        return res.data[0] if res.data else None
    except Exception as exc:
        sys.stderr.write(f"[fast_payment] clinic_payment_settings query failed: {exc}\n")
        return None


def _fetch_patient_age(sb, patient_id: str, treatment_date: date) -> int | None:
    """patient_master から date_of_birth 取得して年齢計算。
    PII guard: 氏名 / 住所は SELECT しない、生年月日のみ取得。
    """
    try:
        res = (
            sb.table("patient_master")
            .select("id,date_of_birth")
            .eq("id", patient_id)
            .execute()
        )
        if not res.data:
            return None
        dob_str = res.data[0].get("date_of_birth")
        if not dob_str:
            return None
        # ISO date or yyyy-mm-dd
        try:
            dob = datetime.strptime(dob_str[:10], "%Y-%m-%d").date()
        except Exception:
            return None
        age = treatment_date.year - dob.year
        if (treatment_date.month, treatment_date.day) < (dob.month, dob.day):
            age -= 1
        return age
    except Exception as exc:
        sys.stderr.write(f"[fast_payment] patient_master query failed: {exc}\n")
        return None


def _ensure_daily_report(sb, clinic_id: str, report_date: date, dry_run: bool) -> str | None:
    """clinic_id × report_date の daily_report row が無ければ新規作成、id 返却。"""
    try:
        res = (
            sb.table("daily_report")
            .select("id")
            .eq("clinic_id", clinic_id)
            .eq("report_date", report_date.isoformat())
            .execute()
        )
        if res.data:
            return res.data[0]["id"]
    except Exception as exc:
        sys.stderr.write(f"[fast_payment] daily_report fetch failed: {exc}\n")
        return None
    if dry_run:
        sys.stderr.write(f"[fast_payment] (dry-run) would INSERT daily_report\n")
        return None
    try:
        res = sb.table("daily_report").insert({
            "clinic_id": clinic_id,
            "report_date": report_date.isoformat(),
            "status": "draft",
        }).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as exc:
        msg = str(exc)
        if "duplicate key" in msg or "23505" in msg:
            # 並行 INSERT の race、再 SELECT で取得
            res2 = (
                sb.table("daily_report")
                .select("id")
                .eq("clinic_id", clinic_id)
                .eq("report_date", report_date.isoformat())
                .execute()
            )
            return res2.data[0]["id"] if res2.data else None
        sys.stderr.write(f"[fast_payment] daily_report INSERT failed: {exc}\n")
        return None


def _next_seq_and_column(sb, daily_report_id: str) -> tuple[int, str]:
    """Phase C-1 全体設計やり直し: paylight 側と統一した seq/column 採番.

    左列 50 名まで埋まったら右列に移行 (左右 50 名 = 100 名 / 日).
    daily_report_patients_seq_uidx UNIQUE と整合.
    """
    if not daily_report_id:
        return 1, "left"
    try:
        left_res = (
            sb.table("daily_report_patients")
            .select("seq_no")
            .eq("daily_report_id", daily_report_id)
            .eq("column_side", "left")
            .order("seq_no", desc=True)
            .limit(1)
            .execute()
        )
        left_max = int(left_res.data[0]["seq_no"]) if left_res.data else 0
        if left_max < 50:
            return left_max + 1, "left"
        right_res = (
            sb.table("daily_report_patients")
            .select("seq_no")
            .eq("daily_report_id", daily_report_id)
            .eq("column_side", "right")
            .order("seq_no", desc=True)
            .limit(1)
            .execute()
        )
        right_max = int(right_res.data[0]["seq_no"]) if right_res.data else 0
        return right_max + 1, "right"
    except Exception:
        return 1, "left"


def _increment_daily_report_header(
    sb, daily_report_id: str, clinic_id: str, *,
    self_pay_delta: float = 0.0,
    insurance_delta: float = 0.0,
    misc_delta: float = 0.0,
    payments_delta: float = 0.0,
    app_payment_delta: float = 0.0,
    patient_delta: int = 1,
) -> None:
    """audit-fix(phase-c1) Critical #1 (L1-A): daily_report ヘッダ集計値 atomic 増分.

    Loop 4 修正 (Codex Loop 3 fail-open Critical): RPC 失敗を握り潰さず raise,
    caller 側で fail-close (return 4) させる. RPC は RETURNS integer + 0 row 時 EXCEPTION,
    例外を Python へ伝播させて main flow を停止.
    """
    if not daily_report_id:
        raise RuntimeError("daily_report_id is required for header increment")
    sb.rpc("rpc_increment_daily_report_header", {
        "p_daily_report_id": daily_report_id,
        "p_clinic_id": clinic_id,
        "p_self_pay_delta": self_pay_delta,
        "p_insurance_delta": insurance_delta,
        "p_misc_delta": misc_delta,
        "p_payments_delta": payments_delta,
        "p_app_payment_delta": app_payment_delta,
        "p_patient_delta": patient_delta,
    }).execute()


def _judge_age_category(age: int | None, settings: dict | None) -> str:
    """子供 (subsidy 対象) / 大人 / unknown を判定。"""
    if age is None or settings is None:
        return "unknown"
    if not settings.get("fast_payment_enabled"):
        return "adult"
    age_max = settings.get("fast_payment_age_max")
    if age_max is None:
        return "adult"
    if age <= int(age_max):
        return "child_subsidy"
    return "adult"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai 高速会計判定 (DD-041 §6)")
    parser.add_argument("--patient-id", help="patient_master.id (uuid)")
    parser.add_argument("--clinic-id", default=CLINIC_ID)
    parser.add_argument("--treatment-date",
                        default=_today_jst().isoformat(),
                        help="ISO date (default: today JST)")
    parser.add_argument("--self-pay", type=float, default=0.0,
                        help="自費追加分 (option、子供でも自費発生時)")
    parser.add_argument("--check-config", action="store_true",
                        help="clinic_payment_settings 表示のみ")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    sb = _supabase_client()
    settings = _fetch_clinic_settings(sb, args.clinic_id)

    if args.check_config:
        if not settings:
            sys.stdout.write(
                f"[fast_payment] clinic_payment_settings not found for clinic_id={args.clinic_id}\n"
                f"  hint: migrations/005 + INSERT clinic_payment_settings row\n"
            )
            return 1
        sys.stdout.write(f"[fast_payment] === clinic_id={args.clinic_id} ===\n")
        for k in ("fast_payment_enabled", "fast_payment_subsidy_region",
                  "fast_payment_age_max", "fast_payment_fixed_amount",
                  "paylight_enabled", "paylight_fee_rate"):
            sys.stdout.write(f"  {k}: {settings.get(k)}\n")
        return 0

    if not args.patient_id:
        sys.stderr.write("[fast_payment] --patient-id required (or --check-config)\n")
        return 2

    # audit-fix(phase-c1) Major (L2): --self-pay 非正数 validation
    if args.self_pay < 0:
        sys.stderr.write(
            f"[fast_payment] --self-pay must be >= 0 (got {args.self_pay})\n"
        )
        return 2

    try:
        treatment_date = datetime.strptime(args.treatment_date, "%Y-%m-%d").date()
    except Exception:
        sys.stderr.write(f"[fast_payment] invalid --treatment-date '{args.treatment_date}'\n")
        return 2

    age = _fetch_patient_age(sb, args.patient_id, treatment_date)
    category = _judge_age_category(age, settings)
    sys.stdout.write(
        f"[fast_payment] patient_id={args.patient_id[:8]}... age={age} category={category}\n"
    )

    if category != "child_subsidy":
        sys.stdout.write(
            f"[fast_payment] not child subsidy target、通常会計フローへ委譲 "
            f"(scripts/hakudokai_paylight_integration.py 等)\n"
        )
        return 0

    fixed_amount = float(settings.get("fast_payment_fixed_amount") or 0)
    if fixed_amount <= 0:
        sys.stderr.write(
            f"[fast_payment] fast_payment_fixed_amount unset or zero、設定見直し必要\n"
        )
        return 4

    received = fixed_amount + args.self_pay

    daily_report_id = _ensure_daily_report(sb, args.clinic_id, treatment_date, args.dry_run)
    if not daily_report_id and not args.dry_run:
        sys.stderr.write("[fast_payment] daily_report ensure failed\n")
        return 4

    # Phase C-1 全体設計やり直し: paylight 同様の左右 50 名採番、placeholder 撲滅
    final_seq, final_col = _next_seq_and_column(sb, daily_report_id) if daily_report_id else (1, "left")

    # PII guard: notes に氏名/住所が混入しないか scan
    notes = f"high-speed payment, age={age} treated={treatment_date.isoformat()}"
    _abort_if_pii(notes, "notes")

    sys.stdout.write(
        f"[fast_payment] decision: child_subsidy fixed={fixed_amount} self_pay={args.self_pay} "
        f"total={received} → atomic INSERT+header (1 transaction)\n"
    )

    if args.dry_run:
        sys.stderr.write(f"[fast_payment] (dry-run) atomic RPC payload prepared, INSERT skip\n")
        return 0

    # Codex audit C-1-6 #1: daily_report_patients_fast_payment_uidx で重複防止、23505 idempotent skip
    # Loop 5 修正 (Codex Loop 4 Critical #1): rpc_insert_patient_with_header_increment で
    # detail INSERT + header 増分を 1 transaction 化、原子的整合保証
    # Loop 6 修正 (Codex Loop 5 regression): seq_uidx 衝突を idempotent skip と誤分類しない
    #   - paylight 同様の判定順 (fast_payment_uidx 限定 idempotent → seq_uidx retry → 一般エラー)
    SEQ_RETRY_MAX = 3
    rpc_res = None
    for seq_attempt in range(1, SEQ_RETRY_MAX + 1):
        try:
            rpc_res = sb.rpc("rpc_insert_patient_with_header_increment", {
                "p_clinic_id": args.clinic_id,
                "p_daily_report_id": daily_report_id,
                "p_seq_no": final_seq,
                "p_column_side": final_col,
                "p_patient_id": args.patient_id,
                "p_points": 0,
                "p_request_amount": float(received),
                "p_received_amount": float(received),
                "p_credit_amount": 0.0,
                "p_payment_method": "fast_payment",
                "p_fast_payment_status": "pending",
                "p_paylight_txn_id": None,
                "p_notes": notes,
                "p_self_pay_delta": float(received),
                "p_insurance_delta": 0.0,
                "p_misc_delta": 0.0,
                "p_payments_delta": float(received),
                "p_app_payment_delta": 0.0,
                "p_patient_delta": 1,
            }).execute()
            break
        except Exception as exc:
            msg = str(exc)
            # 1. fast_payment_uidx 重複 (同一患者・同一日 fast_payment) → idempotent skip 限定判定
            if "daily_report_patients_fast_payment_uidx" in msg:
                sys.stdout.write(
                    f"[fast_payment] idempotency conflict (同一患者・同一日 fast_payment 既存)、INSERT skip\n"
                )
                return 0
            # 2. seq_uidx 衝突 → 再採番 retry (silent-loss 防止)
            is_seq_conflict = (
                "daily_report_patients_seq_uidx" in msg
                or ("23505" in msg and "seq" in msg.lower())
            )
            if is_seq_conflict:
                if seq_attempt < SEQ_RETRY_MAX:
                    if daily_report_id:
                        new_seq, new_col = _next_seq_and_column(sb, daily_report_id)
                        final_seq, final_col = new_seq, new_col
                    sys.stderr.write(
                        f"[fast_payment] seq_no race conflict, retry attempt={seq_attempt+1}/{SEQ_RETRY_MAX} new_seq={final_seq} col={final_col}\n"
                    )
                    continue
                sys.stderr.write(
                    f"[fast_payment] seq_no race conflict retry exhausted ({SEQ_RETRY_MAX} attempts)、INSERT abort\n"
                )
                return 4
            # 3. その他例外 (header P0002 含む) → transaction 自動 rollback、明示エラー
            sys.stderr.write(f"[fast_payment] atomic INSERT+header failed: {exc}\n")
            return 4

    if rpc_res and rpc_res.data:
        sys.stdout.write(
            f"[fast_payment] atomic INSERT+header ok id={rpc_res.data} seq_no={final_seq} column={final_col}\n"
            f"  daily_report header self_pay_total/payments_total/income_total/patient_count incremented (1 transaction)\n"
            f"  next: レセコン入力完了後 fast_payment_status='finalized' へ更新 + 正式明細書アプリ送付\n"
        )
        return 0
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
