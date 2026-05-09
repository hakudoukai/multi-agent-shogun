#!/usr/bin/env python3
"""
hakudokai_patient_pwa.py — 患者 PWA stub (Phase C-2, DD-041 §1-§2)

歯式部位タップ受信 + 治療選択肢/比較表 fetch。本 stub は CLI から動作確認可、
実 PWA UI は DentalBI 本体側 (frontend React TSX) で別 Phase 実装。

設計:
- 入力: clinic_id + patient_id + tooth_no (FDI or 内部表記) + view_kind
- 処理:
  1. patient_app_session 検証 (option、本 stub は patient_id で簡易確認)
  2. patient_app_view_log INSERT (clinic_id boundary)
  3. tooth_no に対応する treatment_plan_items 取得 (DD-040 治療計画ナビ連動、本 stub は read のみ)
  4. 比較表 (保険 vs 自費) 構築 (本 stub は read + 表示のみ、生成は別 service)
  5. 患者画像 link 生成 (Supabase Storage 想定、本 stub は url stub)

Usage:
  hakudokai_patient_pwa.py --tap --patient-id <uuid> --clinic-id <id> --tooth-no 16
  hakudokai_patient_pwa.py --options --patient-id <uuid> --tooth-no 16    # 治療選択肢取得
  hakudokai_patient_pwa.py --comparison --patient-id <uuid> --tooth-no 16 [--plan-id <uuid>]  # 比較表 fetch (plan-id 指定時はその plan に絞込)
  hakudokai_patient_pwa.py --image-link --patient-id <uuid>               # 画像 link stub
  --dry-run で副作用なしテスト

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[patient_pwa] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
# Phase C-2 全体設計やり直し: PII detector 必須 import (optional 廃止、fail-close)
try:
    from hakudokai_pii_detector import scan_for_pii  # type: ignore
except ImportError as exc:
    sys.stderr.write(
        f"[patient_pwa] FATAL: hakudokai_pii_detector required but not importable: {exc}\n"
    )
    sys.exit(3)


CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[patient_pwa] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _abort_if_pii(text: str, label: str) -> None:
    """Phase C-2 全体設計やり直し: fail-close PII guard (silent skip 撲滅)."""
    if not text:
        return
    try:
        matches = list(scan_for_pii(text))
    except Exception as exc:
        sys.stderr.write(f"[patient_pwa] PII scanner error in {label}: {exc}\n")
        raise SystemExit(5) from exc
    if matches:
        sys.stderr.write(
            f"[patient_pwa] PII detected in {label}, abort INSERT (matches={len(matches)})\n"
        )
        raise SystemExit(5)


def _verify_session(sb, session_id: str, patient_id: str, clinic_id: str) -> bool:
    """Phase C-2 全体設計やり直し Pass 4: pwa.py 用 session verify (chat.py と同 logic)."""
    if not session_id:
        return False
    try:
        res = (
            sb.table("patient_app_session")
            .select("patient_id,clinic_id,revoked_at,expires_at")
            .eq("id", session_id)
            .eq("patient_id", patient_id)
            .eq("clinic_id", clinic_id)
            .maybeSingle()
            .execute()
        )
    except Exception as exc:
        sys.stderr.write(f"[patient_pwa] session verify error: {exc}\n")
        return False
    if not res.data:
        return False
    row = res.data
    if row.get("revoked_at") is not None:
        return False
    expires_at = row.get("expires_at")
    if expires_at:
        try:
            from datetime import datetime, timezone
            exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if exp < datetime.now(timezone.utc):
                return False
        except Exception:
            pass
    return True


def _log_view(sb, clinic_id: str, patient_id: str, view_kind: str,
              tooth_no: str | None, plan_item_id: str | None,
              session_id: str | None, payload: dict, dry_run: bool,
              internal_batch: bool = False) -> str | None:
    # Phase C-2 全体設計やり直し Pass 4 (Codex Pass 3 view_log NULL bypass 根治):
    # session_id 必須、internal_batch 明示時のみ bypass、chat.py と同パターン
    if not session_id:
        if not internal_batch:
            sys.stderr.write(
                "[patient_pwa] view_log requires --session-id (or --internal-batch for explicit CLI bypass)\n"
            )
            return None
        sys.stderr.write(
            "[patient_pwa] WARNING: --internal-batch bypass active for view_log\n"
        )
    elif not _verify_session(sb, session_id, patient_id, clinic_id):
        sys.stderr.write(
            f"[patient_pwa] session verify failed (session_id/{session_id[:8]}.../patient_id mismatch or revoked/expired)、view_log INSERT 拒否\n"
        )
        return None

    payload_json = json.dumps(payload, ensure_ascii=False)
    _abort_if_pii(payload_json, "view_log.payload")
    row = {
        "clinic_id": clinic_id,
        "patient_id": patient_id,
        "session_id": session_id,
        "view_kind": view_kind,
        "tooth_no": tooth_no,
        "treatment_plan_item_id": plan_item_id,
        "payload": payload,
    }
    if dry_run:
        sys.stderr.write(f"[patient_pwa] (dry-run) view_log payload prepared\n")
        return None
    try:
        res = sb.table("patient_app_view_log").insert(row).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as exc:
        sys.stderr.write(f"[patient_pwa] view_log INSERT failed: {exc}\n")
        return None


def _fetch_treatment_options(sb, clinic_id: str, patient_id: str, tooth_no: str,
                             plan_id: str | None = None) -> list[dict]:
    """DD-040 treatment_plans + treatment_plan_items から、当該 tooth に紐付く選択肢を取得。
    本 stub は read のみ、treatment_plans table 不在環境では空 list 返却。

    Codex audit C-2-6 #2 修正: plan_id 指定時はその plan に絞り込む (--comparison Usage と整合)。
    """
    try:
        q = (
            sb.table("treatment_plan_items")
            .select("id,plan_id,tooth_no,coverage_type,procedure_code,procedure_name,price,points,recommended_rank")
            .eq("clinic_id", clinic_id)
            .eq("tooth_no", tooth_no)
        )
        if plan_id:
            q = q.eq("plan_id", plan_id)
        res = q.order("recommended_rank").limit(20).execute()
        return res.data or []
    except Exception as exc:
        sys.stderr.write(
            f"[patient_pwa] treatment_plan_items fetch failed (Phase C-2 base): {exc}\n"
            f"  hint: DD-040 治療計画ナビ migration 適用後に動作。本 stub は空 list 返却。\n"
        )
        return []


def _build_comparison_table(options: list[dict]) -> dict:
    """保険 (coverage_type='insurance') vs 自費 (coverage_type='private') の比較表。"""
    insurance = [o for o in options if o.get("coverage_type") == "insurance"]
    private_p = [o for o in options if o.get("coverage_type") == "private"]
    return {
        "insurance": [
            {"name": o.get("procedure_name"), "price": o.get("price"), "points": o.get("points")}
            for o in insurance
        ],
        "private": [
            {"name": o.get("procedure_name"), "price": o.get("price")}
            for o in private_p
        ],
        "summary": {
            "insurance_count": len(insurance),
            "private_count": len(private_p),
        },
    }


def _image_link_stub(clinic_id: str, patient_id: str) -> str:
    """Supabase Storage 想定の患者画像 link stub。本 sandbox では URL のみ返却、署名付き URL 生成は別 Phase。"""
    return f"https://storage.supabase.local/{clinic_id}/patients/{patient_id}/images/latest.png"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai patient PWA stub (DD-041 §1-§2)")
    sub = parser.add_mutually_exclusive_group(required=True)
    sub.add_argument("--tap", action="store_true",
                     help="歯式部位 tap → view_log 記録 + 治療選択肢取得 + 比較表構築")
    sub.add_argument("--options", action="store_true",
                     help="治療選択肢のみ取得 (read-only)")
    sub.add_argument("--comparison", action="store_true",
                     help="比較表のみ構築 (read-only、--patient-id + --tooth-no 必須、--plan-id 任意で絞込)")
    sub.add_argument("--image-link", action="store_true",
                     help="患者画像 link stub")

    parser.add_argument("--clinic-id", default=CLINIC_ID)
    parser.add_argument("--patient-id", help="patient_master.id (uuid)")
    parser.add_argument("--tooth-no", help="FDI 番号 or 内部表記 (例: 16, 26)")
    parser.add_argument("--plan-id", help="--comparison 時の plan_id")
    # Phase C-2 全体設計やり直し Pass 4 (Codex Pass 3 view_log NULL bypass 根治):
    parser.add_argument("--session-id",
                        help="patient_app_session.id (--tap-tooth で必須、--internal-batch 時のみ省略可)")
    parser.add_argument("--internal-batch", action="store_true",
                        help="session 検証 bypass (内部 CLI/batch 専用、明示宣言)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    sb = _supabase_client()

    if args.image_link:
        if not args.patient_id:
            sys.stderr.write("[patient_pwa] --image-link requires --patient-id\n")
            return 2
        url = _image_link_stub(args.clinic_id, args.patient_id)
        sys.stdout.write(f"[patient_pwa] image_link: {url}\n")
        return 0

    if args.options:
        if not (args.patient_id and args.tooth_no):
            sys.stderr.write("[patient_pwa] --options requires --patient-id and --tooth-no\n")
            return 2
        options = _fetch_treatment_options(sb, args.clinic_id, args.patient_id, args.tooth_no)
        sys.stdout.write(f"[patient_pwa] options ({len(options)}):\n")
        for o in options:
            sys.stdout.write(
                f"  [{o.get('coverage_type')}] {o.get('procedure_code')} {o.get('procedure_name')} "
                f"price={o.get('price')} points={o.get('points')}\n"
            )
        return 0

    if args.comparison:
        if not (args.patient_id and args.tooth_no):
            sys.stderr.write("[patient_pwa] --comparison requires --patient-id and --tooth-no\n")
            return 2
        # Codex audit C-2-6 #2 修正: --plan-id を _fetch_treatment_options() に伝播 (絞込)
        options = _fetch_treatment_options(sb, args.clinic_id, args.patient_id,
                                           args.tooth_no, plan_id=args.plan_id)
        table = _build_comparison_table(options)
        sys.stdout.write(json.dumps(table, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0

    if args.tap:
        if not (args.patient_id and args.tooth_no):
            sys.stderr.write("[patient_pwa] --tap requires --patient-id and --tooth-no\n")
            return 2
        # Phase C-2 全体設計やり直し Pass 5 (Codex Pass 4 caller fail-close 根治):
        # session 必須化を caller 段階で先に判定、view_log 成功前に options/table 計算を実行しない
        if not args.session_id:
            if not args.internal_batch:
                sys.stderr.write(
                    "[patient_pwa] --tap requires --session-id (or --internal-batch for explicit CLI bypass)\n"
                )
                return 2
            sys.stderr.write(
                "[patient_pwa] WARNING: --tap with --internal-batch bypass active\n"
            )
        elif not _verify_session(sb, args.session_id, args.patient_id, args.clinic_id):
            sys.stderr.write(
                f"[patient_pwa] session verify failed for --tap、INSERT 拒否\n"
            )
            return 4
        options = _fetch_treatment_options(sb, args.clinic_id, args.patient_id, args.tooth_no)
        table = _build_comparison_table(options)
        view_id = _log_view(
            sb, args.clinic_id, args.patient_id, "tooth_tap",
            args.tooth_no, None, args.session_id,
            {"options_count": len(options), "comparison_summary": table["summary"]},
            args.dry_run,
            internal_batch=args.internal_batch,
        )
        # Phase C-2 Pass 5: view_id None なら fail-close (旧 success 扱い 撲滅)
        if view_id is None and not args.dry_run:
            sys.stderr.write(
                "[patient_pwa] --tap aborted: view_log INSERT failed or rejected (session/PII guard)\n"
            )
            return 4
        sys.stdout.write(
            f"[patient_pwa] tap recorded id={view_id} tooth={args.tooth_no} options={len(options)}\n"
        )
        sys.stdout.write(json.dumps(table, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
