#!/usr/bin/env python3
"""
hakudokai_patient_notification.py — 患者通知 (Phase C-2, DD-041 §5)

メール / SMS / LINE / push / app_inbox 統合配信、DD-044 (Quartetto 連携 + 領収書 PDF) との
役割境界:
  - 本 script: 通知 dispatch + delivery_status 管理 + idempotency
  - DD-044 連携: 明細入り領収書 PDF 配信 (本 stub では reference link 経由、PDF 生成は別 service)
  - Web 予約連携: 予約システム interface (本 stub は web_booking endpoint stub)

PII guard:
  - subject / body は **template_key + variables (jsonb)** で生成、患者氏名/住所等を直書きしない
  - template_key は固定 (例: 'recall_30day' / 'receipt_attached' / 'payment_reminder')
  - variables には patient_id 等 uuid のみ、または masked 値

Usage:
  hakudokai_patient_notification.py --send --patient-id <uuid> --channel email --template recall_30day
  hakudokai_patient_notification.py --check-status --patient-id <uuid>     # 配信履歴
  hakudokai_patient_notification.py --queue-receipt --patient-id <uuid> --report-id <uuid>
  hakudokai_patient_notification.py --book-link --patient-id <uuid>        # Web 予約 deep link 生成

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[patient_notify] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
# Phase C-2 全体設計やり直し: PII detector 必須 import (optional 廃止、fail-close)
try:
    from hakudokai_pii_detector import scan_for_pii  # type: ignore
except ImportError as exc:
    sys.stderr.write(
        f"[patient_notify] FATAL: hakudokai_pii_detector required but not importable: {exc}\n"
    )
    sys.exit(3)


CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")

VALID_CHANNELS = ("email", "sms", "line", "push", "app_inbox")
VALID_PURPOSES = ("general", "reminder", "receipt", "payment_request", "recall", "treatment_explanation")

# 通知 template (PII 直書き禁止、variables は uuid / masked 値のみ)
NOTIFICATION_TEMPLATES = {
    "recall_30day": {
        "purpose": "recall",
        "subject_key": "次回ご来院のご案内",
    },
    "recall_90day": {
        "purpose": "recall",
        "subject_key": "次回メンテナンスのご案内",
    },
    "receipt_attached": {
        "purpose": "receipt",
        "subject_key": "領収書のお届け",
    },
    "payment_reminder": {
        "purpose": "payment_request",
        "subject_key": "お支払いのご案内",
    },
    "treatment_explanation": {
        "purpose": "treatment_explanation",
        "subject_key": "治療内容のご説明",
    },
    "appointment_reminder": {
        "purpose": "reminder",
        "subject_key": "ご予約日のご案内",
    },
    "general_message": {
        "purpose": "general",
        "subject_key": "医院からのお知らせ",
    },
}


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[patient_notify] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _abort_if_pii(text: str, label: str) -> None:
    """Phase C-2 全体設計やり直し: fail-close PII guard (silent skip 撲滅)."""
    if not text:
        return
    try:
        matches = list(scan_for_pii(text))
    except Exception as exc:
        sys.stderr.write(f"[patient_notify] PII scanner error in {label}: {exc}\n")
        raise SystemExit(5) from exc
    if matches:
        sys.stderr.write(
            f"[patient_notify] PII detected in {label}, abort INSERT (matches={len(matches)})\n"
        )
        raise SystemExit(5)


def _build_idempotency_key(clinic_id: str, patient_id: str, channel: str,
                           template_key: str, variables: dict | None = None,
                           bucket_hours: int = 1) -> str:
    """1h bucket で同一 patient × channel × template × variables の重複抑止。

    Gemini Pass 1 修正: variables (report_id 等) をシードに含めて、同一テンプレートでも
    内容が異なる通知 (例: 領収書 #1 と #2) を別 idempotency key に分離。silent-loss 防止.
    """
    now = datetime.now(timezone.utc)
    bucket = int(now.timestamp() // (bucket_hours * 3600))
    # variables を deterministic に hash 化 (uuid/数値/boolean のみ、PII guard 通過済前提)
    if variables:
        var_seed = "|".join(f"{k}={variables[k]}" for k in sorted(variables.keys()))
        var_hash = hashlib.sha256(var_seed.encode()).hexdigest()[:8]
    else:
        var_hash = "novars"
    seed = f"{clinic_id}|{patient_id}|{channel}|{template_key}|{var_hash}|{bucket}"
    digest = hashlib.sha256(seed.encode()).hexdigest()[:16]
    return f"notify-{channel}-{template_key}-{digest}"


def _check_patient_settings(sb, clinic_id: str, patient_id: str, channel: str) -> bool:
    """patient_app_settings.notify_<channel> opt-in 確認。

    Phase C-2 全体設計やり直し (Codex Loop 1 Major #4 根治): fail-close 化.
    旧 `except: return True` (graceful 配信許可) は opt-out 患者にも配信する根本欠陥.
    DB/API 障害時は **配信拒否** (False) で患者保護を最優先.
    """
    try:
        res = (
            sb.table("patient_app_settings")
            .select("notify_email,notify_sms,notify_line,notify_push,chat_enabled")
            .eq("clinic_id", clinic_id)
            .eq("patient_id", patient_id)
            .execute()
        )
        if not res.data:
            # 設定なし = default opt-in (notify_email/sms/push=true、line=false)
            return channel != "line"
        s = res.data[0]
        return bool(s.get(f"notify_{channel}", channel != "line"))
    except Exception as exc:
        # Phase C-2 修正: fail-close (旧 return True で opt-out 破棄を防止)
        sys.stderr.write(
            f"[patient_notify] settings fetch error → fail-close (send 拒否): {exc}\n"
        )
        return False


def _send_notification(sb, args) -> int:
    if args.template not in NOTIFICATION_TEMPLATES:
        sys.stderr.write(
            f"[patient_notify] unknown template '{args.template}'、定義済 template:\n"
        )
        for k in NOTIFICATION_TEMPLATES.keys():
            sys.stderr.write(f"  - {k}\n")
        return 2

    if args.channel not in VALID_CHANNELS:
        sys.stderr.write(f"[patient_notify] invalid channel '{args.channel}'\n")
        return 2

    template = NOTIFICATION_TEMPLATES[args.template]
    purpose = template["purpose"]

    # opt-in 確認 (push / app_inbox は notify_push に集約 simplification)
    settings_channel = "push" if args.channel in ("push", "app_inbox") else args.channel
    if not _check_patient_settings(sb, args.clinic_id, args.patient_id, settings_channel):
        sys.stdout.write(
            f"[patient_notify] patient opt-out (notify_{settings_channel}=false)、send skip\n"
        )
        return 0

    # Codex audit C-2-6 #1 修正: variables jsonb で report_id 等の masked 値を永続化
    # PII guard: variables には uuid / boolean / 数値のみ、氏名/住所等は含めない
    # Codex audit C-2-6 Loop 2 #1 修正: --extra-var の各 value に _abort_if_pii() 適用
    variables: dict = {}
    if args.report_id:
        # report_id は uuid 想定 (PII guard 簡易確認: scan 通過、検出なら abort)
        _abort_if_pii(args.report_id, "variables.report_id")
        variables["report_id"] = args.report_id
    if args.extra_var:
        # --extra-var key=value 形式 (template_key 拡張用、PII guard 通過後のみ)
        for kv in args.extra_var.split(","):
            kv = kv.strip()
            if "=" not in kv:
                continue
            k, v = kv.split("=", 1)
            k_clean = k.strip()
            v_clean = v.strip()
            # Codex audit C-2-6 Loop 2 #1: 各 extra_var value に PII guard 適用、検出時 abort
            _abort_if_pii(v_clean, f"variables.{k_clean}")
            variables[k_clean] = v_clean

    # Gemini Pass 1 修正: idempotency_key に variables を含めて、同一テンプレートでも内容違いを別 key 化
    idem = _build_idempotency_key(
        args.clinic_id, args.patient_id, args.channel, args.template, variables
    )
    payload = {
        "clinic_id": args.clinic_id,
        "patient_id": args.patient_id,
        "channel": args.channel,
        "purpose": purpose,
        "template_key": args.template,
        "variables": variables,
        "idempotency_key": idem,
        "delivery_status": "queued",
    }
    # subject / body は本 stub では template_key 経由で外部 service が生成 (本実装は別 Phase)
    # variables (jsonb) は外部 service が template fill 時に参照
    # 検出 keyword (PII) は template_key + uuid のみで構成、scan 不要

    if args.dry_run:
        sys.stderr.write(f"[patient_notify] (dry-run) payload prepared idem={idem}\n")
        return 0

    try:
        res = sb.table("patient_notification_log").insert(payload).execute()
        sys.stdout.write(
            f"[patient_notify] queued id={res.data[0]['id']} channel={args.channel} "
            f"template={args.template} idem={idem}\n"
            f"  next: 外部 service が template_key で subject/body 生成 + 配信実行\n"
        )
        return 0
    except Exception as exc:
        msg = str(exc)
        if ("duplicate key" in msg or "23505" in msg
                or "patient_notification_idem_uniq" in msg):
            sys.stdout.write(
                f"[patient_notify] idempotency conflict (1h bucket 内重複)、INSERT skip\n"
            )
            return 0
        sys.stderr.write(f"[patient_notify] INSERT failed: {exc}\n")
        return 4


def _check_status(sb, args) -> int:
    try:
        res = (
            sb.table("patient_notification_log")
            .select("id,channel,purpose,template_key,delivery_status,delivered_at,created_at")
            .eq("clinic_id", args.clinic_id)
            .eq("patient_id", args.patient_id)
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        rows = res.data or []
        sys.stdout.write(f"[patient_notify] history ({len(rows)}):\n")
        for r in rows:
            sys.stdout.write(
                f"  {r['created_at'][:19]} #{r['id'][:8]} [{r['channel']}/{r['purpose']}] "
                f"{r['template_key']} status={r['delivery_status']}\n"
            )
        return 0
    except Exception as exc:
        sys.stderr.write(f"[patient_notify] history fetch failed: {exc}\n")
        return 4


def _queue_receipt(sb, args) -> int:
    """DD-044 連携: 明細入り領収書 PDF 配信を queue (本 stub では log のみ、PDF 生成は別 service)。"""
    if not args.report_id:
        sys.stderr.write("[patient_notify] --queue-receipt requires --report-id\n")
        return 2
    args.template = "receipt_attached"
    args.channel = args.channel or "app_inbox"
    return _send_notification(sb, args)


def _book_link(args) -> int:
    """Web 予約 deep link stub (患者アプリ → 既存予約システム)。"""
    if not args.patient_id:
        sys.stderr.write("[patient_notify] --book-link requires --patient-id\n")
        return 2
    # PII 直書き禁止のため、deep link には patient_id (uuid) のみ含める
    url = (
        f"https://booking.dentalbi.local/{args.clinic_id}/book"
        f"?patient_ref={args.patient_id}"
    )
    sys.stdout.write(f"[patient_notify] book_link: {url}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai patient 通知 (DD-041 §5 + DD-044 連動)")
    sub = parser.add_mutually_exclusive_group(required=True)
    sub.add_argument("--send", action="store_true", help="通知 dispatch")
    sub.add_argument("--check-status", action="store_true", help="配信履歴")
    sub.add_argument("--queue-receipt", action="store_true",
                     help="DD-044 連携: 領収書 PDF 配信 queue")
    sub.add_argument("--book-link", action="store_true", help="Web 予約 deep link 生成")

    parser.add_argument("--clinic-id", default=CLINIC_ID)
    parser.add_argument("--patient-id", help="patient_master.id (uuid)")
    parser.add_argument("--channel", choices=VALID_CHANNELS, help="通知 channel")
    parser.add_argument("--template", help="通知 template_key")
    parser.add_argument("--report-id", help="--queue-receipt 時の daily_report.id (variables.report_id 永続化)")
    parser.add_argument("--extra-var", help="--send 時の追加 variables (key=value,key2=value2 形式、PII guard 通過後のみ)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.book_link:
        return _book_link(args)

    sb = _supabase_client()

    if args.send:
        if not (args.patient_id and args.channel and args.template):
            sys.stderr.write(
                "[patient_notify] --send requires --patient-id --channel --template\n"
            )
            return 2
        return _send_notification(sb, args)

    if args.check_status:
        if not args.patient_id:
            sys.stderr.write("[patient_notify] --check-status requires --patient-id\n")
            return 2
        return _check_status(sb, args)

    if args.queue_receipt:
        if not args.patient_id:
            sys.stderr.write("[patient_notify] --queue-receipt requires --patient-id\n")
            return 2
        return _queue_receipt(sb, args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
