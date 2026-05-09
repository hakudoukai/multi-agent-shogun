#!/usr/bin/env python3
"""
hakudokai_paylight_integration.py — paylight 連携 stub (Phase C-1, DD-041 §7)

paylight cashless (SCO グループ、博道会 1 院契約済) との API 連携 stub。
本 sandbox 範囲では mock 応答 + interface 定義 + 手数料計算 + reconciliation ロジック。
本番 paylight API 接続は別 Phase (副医院長 / 山ちゃん 法令適合 / API key 管理 後)。

設計:
- 入力: patient_id + invoice_amount + treatment_summary
- 処理:
  1. clinic_payment_settings から paylight_enabled / fee_rate / merchant_id 取得
  2. (mock): paylight API 呼出を simulate、txn_id を生成
  3. 手数料計算 (default 1.05%)
  4. 決済成功時 daily_report_patients INSERT (payment_method='app', fast_payment_status=NULL)
  5. 電子領収書 / 明細書生成は別 service (本 stub では interface 定義のみ)
- reconciliation: paylight 明細 (CSV/API) と daily_report_patients の突合 (本 stub では未実装、CLI で個別実行可)

Usage:
  hakudokai_paylight_integration.py --check-config --clinic-id <id>
  hakudokai_paylight_integration.py --invoice --patient-id <uuid> --amount 5000 --summary "SPT"
  hakudokai_paylight_integration.py --reconcile --report-id <uuid>  # paylight 明細突合 (stub)
  --mock デフォルト ON (本 stub 範囲、本番接続は --no-mock + paylight credential 付き、別 Phase)

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import uuid
from datetime import datetime, date, timezone, timedelta

# audit-fix(phase-c1) Critical #2 (L1-E): JST timezone 統一
# zoneinfo は Python 3.9+ で標準、tzdata は Windows で必要 (pip install tzdata)
try:
    from zoneinfo import ZoneInfo  # type: ignore
    _JST = ZoneInfo("Asia/Tokyo")
except Exception:
    _JST = timezone(timedelta(hours=9))


def _now_jst() -> datetime:
    return datetime.now(_JST)


def _today_jst() -> date:
    return _now_jst().date()

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[paylight] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

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
            "[paylight] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _abort_if_pii(text: str, label: str) -> None:
    if not text or scan_for_pii is None:
        return
    try:
        matches = list(scan_for_pii(text))
    except Exception:
        return
    if matches:
        sys.stderr.write(
            f"[paylight] PII detected in {label}, abort INSERT (matches={len(matches)})\n"
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
        sys.stderr.write(f"[paylight] clinic_payment_settings query failed: {exc}\n")
        return None


def _mock_paylight_charge(merchant_id: str, amount: float,
                          patient_id: str, summary: str,
                          treatment_date: date) -> dict:
    """paylight API 呼び出しを mock。本番接続は別 Phase。

    返却: {success, txn_id, amount, fee, net_amount, receipt_url}

    Codex audit C-1-6 #2 修正: txn_id seed から datetime.now() を除去、
    deterministic seed (merchant + patient + amount + treatment_date) で
    再試行時に同一 txn_id を生成、daily_report_patients_paylight_txn_uidx
    UNIQUE と組合せて二重請求を防止。
    """
    seed = f"{merchant_id}|{patient_id}|{amount:.2f}|{treatment_date.isoformat()}"
    txn_id = "mock_pl_" + hashlib.sha256(seed.encode()).hexdigest()[:16]
    return {
        "success": True,
        "txn_id": txn_id,
        "amount": amount,
        "currency": "JPY",
        "merchant_id": merchant_id,
        "summary_redacted": summary[:60] if summary else "",
        "receipt_url_stub": f"https://mock.paylight.local/receipt/{txn_id}",
        "is_mock": True,
    }


def _next_seq_and_column(sb, daily_report_id: str) -> tuple[int, str]:
    """audit-fix(phase-c1) Critical #3 (L1-B): daily 単位の next-seq + 50 件超で右列切替.

    左列 50 名まで埋まったら右列に移行 (左右 50 名 = 100 名 / 日)。
    fast_payment 側と一貫した採番ルール、daily_report_patients_seq_uidx と整合.
    """
    if not daily_report_id:
        return 1, "left"
    try:
        # 左列の最大 seq_no を取得
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
        # 左列満杯 → 右列
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
    insurance_delta: float = 0.0,
    self_pay_delta: float = 0.0,
    misc_delta: float = 0.0,
    payments_delta: float = 0.0,
    app_payment_delta: float = 0.0,
    patient_delta: int = 1,
) -> None:
    """audit-fix(phase-c1) Critical #1 (L1-A): daily_report ヘッダ集計値 atomic 増分.

    Loop 4 修正 (Codex Loop 3 fail-open Critical): RPC 失敗を握り潰さず raise.
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


def _ensure_daily_report(sb, clinic_id: str, report_date: date, dry_run: bool) -> str | None:
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
        sys.stderr.write(f"[paylight] daily_report fetch failed: {exc}\n")
        return None
    if dry_run:
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
            res2 = (
                sb.table("daily_report")
                .select("id")
                .eq("clinic_id", clinic_id)
                .eq("report_date", report_date.isoformat())
                .execute()
            )
            return res2.data[0]["id"] if res2.data else None
        sys.stderr.write(f"[paylight] daily_report INSERT failed: {exc}\n")
        return None


def _check_config(sb, clinic_id: str) -> int:
    settings = _fetch_clinic_settings(sb, clinic_id)
    if not settings:
        sys.stdout.write(
            f"[paylight] clinic_payment_settings not found for clinic_id={clinic_id}\n"
        )
        return 1
    sys.stdout.write(f"[paylight] === clinic_id={clinic_id} ===\n")
    for k in ("paylight_enabled", "paylight_merchant_id",
              "paylight_fee_rate", "paylight_endpoint"):
        sys.stdout.write(f"  {k}: {settings.get(k)}\n")
    return 0


def _do_invoice(sb, args) -> int:
    settings = _fetch_clinic_settings(sb, args.clinic_id)
    if not settings:
        sys.stderr.write(f"[paylight] clinic_payment_settings not found\n")
        return 1
    if not settings.get("paylight_enabled"):
        sys.stderr.write(
            f"[paylight] paylight_enabled=false for clinic_id={args.clinic_id}、"
            f"window 会計フローへ委譲\n"
        )
        return 1

    merchant_id = settings.get("paylight_merchant_id") or "MOCK_MERCHANT"
    fee_rate = float(settings.get("paylight_fee_rate") or 0.0105)

    # PII guard: summary に患者氏名等が含まれないか scan
    _abort_if_pii(args.summary, "summary")

    # audit-fix(phase-c1) Critical #2 (L1-E): JST 既定値で当日記帳、UTC 早朝の前日誤記帳防止
    treatment_date = _today_jst()
    if not args.no_mock:
        result = _mock_paylight_charge(merchant_id, args.amount, args.patient_id,
                                       args.summary or "", treatment_date)
    else:
        sys.stderr.write(
            "[paylight] --no-mock requires real paylight API credential、"
            "本 sandbox 範囲外 (副医院長 / 山ちゃん 法令適合審査経由で別 Phase)\n"
        )
        return 4

    if not result.get("success"):
        sys.stderr.write(f"[paylight] mock charge failed: {result}\n")
        return 4

    fee = round(args.amount * fee_rate, 2)
    net = round(args.amount - fee, 2)

    sys.stdout.write(
        f"[paylight] mock charge ok txn_id={result['txn_id']} amount={args.amount} "
        f"fee={fee} net={net} (fee_rate={fee_rate:.4f})\n"
    )

    daily_report_id = _ensure_daily_report(sb, args.clinic_id, treatment_date, args.dry_run)
    # Gemini Pass 1 修正: daily_report_id None 時の早期 return (P0002 露出防止)
    if not daily_report_id and not args.dry_run:
        sys.stderr.write("[paylight] daily_report ensure failed\n")
        return 4

    # audit-fix(phase-c1) Critical #3 (L1-B): seq_no/column_side 動的採番
    # 同日複数 app 会計の row 衝突を防止、左右 50 名構成に整合
    if daily_report_id:
        seq_no, column_side = _next_seq_and_column(sb, daily_report_id)
    else:
        seq_no, column_side = 1, "left"

    if args.dry_run:
        sys.stderr.write(f"[paylight] (dry-run) atomic RPC payload prepared, INSERT skip\n")
        return 0

    # Codex audit C-1-6 #2: paylight_txn_id partial UNIQUE 23505 conflict を idempotent skip
    # Loop 5 修正 (Codex Loop 4 Critical #1+#2): rpc_insert_patient_with_header_increment で
    # detail INSERT + header 増分を 1 transaction 化 + seq_uidx UNIQUE で seq race 検出可能
    final_seq = seq_no
    final_col = column_side
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
                "p_request_amount": float(args.amount),
                "p_received_amount": float(args.amount),
                "p_credit_amount": float(args.amount),
                "p_payment_method": "app",
                "p_fast_payment_status": None,
                "p_paylight_txn_id": result["txn_id"],
                "p_notes": "paylight mock charge",
                "p_self_pay_delta": 0.0,
                "p_insurance_delta": 0.0,
                "p_misc_delta": 0.0,
                "p_payments_delta": float(args.amount),
                "p_app_payment_delta": float(args.amount),
                "p_patient_delta": 1,
            }).execute()
            break
        except Exception as exc:
            msg = str(exc)
            # 1. paylight_txn 重複 → idempotent skip (最優先判定、silent-loss 防止)
            if "daily_report_patients_paylight_txn_uidx" in msg:
                sys.stdout.write(
                    f"[paylight] idempotency conflict (paylight_txn_id 既存)、INSERT skip\n"
                    f"  txn_id={result['txn_id']}\n"
                )
                return 0
            # 2. seq_no race → 再採番 retry (seq_uidx UNIQUE 制約あり、Loop 5 で migration 追加)
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
                        f"[paylight] seq_no race conflict, retry attempt={seq_attempt+1}/{SEQ_RETRY_MAX} new_seq={final_seq} col={final_col}\n"
                    )
                    continue
                sys.stderr.write(
                    f"[paylight] seq_no race conflict retry exhausted ({SEQ_RETRY_MAX} attempts)、INSERT abort\n"
                    f"  txn_id={result['txn_id']} report_id={daily_report_id}\n"
                )
                return 4
            # 3. その他例外 (header 更新失敗 P0002 含む) → transaction 自動 rollback、明示エラー終了
            sys.stderr.write(f"[paylight] atomic INSERT+header failed: {exc}\n")
            return 4

    if rpc_res and rpc_res.data:
        sys.stdout.write(
            f"[paylight] atomic INSERT+header ok id={rpc_res.data} "
            f"seq_no={final_seq} column={final_col}\n"
            f"  daily_report header app_payment_received/payments_total/income_total/patient_count incremented (1 transaction)\n"
            f"  next: 電子領収書/明細書生成 (別 service) + 患者アプリ送付\n"
            f"  (現 stub では mock URL: {result['receipt_url_stub']})\n"
        )
        return 0
    return 4


def _do_reconcile(sb, args) -> int:
    """paylight 明細と daily_report_patients の突合 stub。

    本 stub は report_id 内で paylight_txn_id != NULL の row 数 + 合計金額を集計するのみ。
    本番運用は paylight API or CSV 取込との照合 (別 Phase)。
    """
    try:
        res = (
            sb.table("daily_report_patients")
            .select("paylight_txn_id,received_amount")
            .eq("daily_report_id", args.report_id)
            .not_.is_("paylight_txn_id", "null")
            .execute()
        )
        rows = res.data or []
        total = sum(float(r.get("received_amount") or 0) for r in rows)
        sys.stdout.write(
            f"[paylight] reconcile (stub): report_id={args.report_id[:8]}... "
            f"paylight_txn={len(rows)} total={total}\n"
        )
        sys.stdout.write(
            "  本番運用: paylight API/CSV と本数値を照合、差異 → 副医院長 escalation (別 Phase)\n"
        )
        return 0
    except Exception as exc:
        sys.stderr.write(f"[paylight] reconcile failed: {exc}\n")
        return 4


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai paylight 連携 stub (DD-041 §7)")
    sub = parser.add_mutually_exclusive_group(required=True)
    sub.add_argument("--check-config", action="store_true")
    sub.add_argument("--invoice", action="store_true",
                     help="patient へ請求 + paylight charge (mock)")
    sub.add_argument("--reconcile", action="store_true",
                     help="paylight 明細と daily_report 突合 (stub)")

    parser.add_argument("--clinic-id", default=CLINIC_ID)
    parser.add_argument("--patient-id", help="patient_master.id (uuid)")
    parser.add_argument("--amount", type=float, help="請求金額")
    parser.add_argument("--summary", default="", help="治療概要 (PII guard 通過必須)")
    parser.add_argument("--report-id", help="--reconcile 時の daily_report.id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-mock", action="store_true",
                        help="本番 paylight API 接続 (本 sandbox 範囲外、別 Phase)")
    args = parser.parse_args(argv)

    sb = _supabase_client()

    if args.check_config:
        return _check_config(sb, args.clinic_id)

    if args.invoice:
        if not args.patient_id or args.amount is None:
            sys.stderr.write("[paylight] --invoice requires --patient-id and --amount\n")
            return 2
        # audit-fix(phase-c1) Major (L2): --amount 非正数 validation
        if args.amount <= 0:
            sys.stderr.write(
                f"[paylight] --amount must be > 0 (got {args.amount})\n"
            )
            return 2
        return _do_invoice(sb, args)

    if args.reconcile:
        if not args.report_id:
            sys.stderr.write("[paylight] --reconcile requires --report-id\n")
            return 2
        return _do_reconcile(sb, args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
