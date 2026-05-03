#!/usr/bin/env python3
"""
hakudokai_billing_tier.py — subscription_tier 別機能制限ロジック (Phase B-4 続編 task 8)

docs/regulatory.md §4 で仕様化された T15/T17/T19 subscription_tier に応じた
機能制限を適用する。tier 判定 + tier 別 quota check + audit trail。

設計:
  - clinic_master.subscription_tier (migrations/001) を参照
  - tier 別の handshake quota / skill_candidate / heartbeat 等の上限を定義
  - 上限超過時は副医院長 escalation INSERT (重複抑止 1h)
  - tier 変更時は migrations/004 の trigger が clinic_subscription_audit に自動記録

Usage:
  hakudokai_billing_tier.py --check                       # 現 clinic の tier + 機能一覧
  hakudokai_billing_tier.py --check --clinic-id marquise
  hakudokai_billing_tier.py --quota-check feature=handshake  # quota 違反検出
  hakudokai_billing_tier.py --upgrade --to T17              # tier upgrade (副医院長スコープ)

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[billing_tier] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)


CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")

# Phase B-4 続編 task 8: tier 別機能 (docs/regulatory.md §4 仕様骨子に対応)
TIER_FEATURES = {
    "T15": {
        "label": "T15 (15万円)",
        "handshake_quota_monthly": 50_000,
        "skill_candidate_enabled": False,
        "dev_lessons_shared": False,
        "heartbeat_monitoring": False,
        "yama_independent": False,
        "departure_script": False,
        "clinic_switch": False,
    },
    "T17": {
        "label": "T17 (17万円)",
        "handshake_quota_monthly": 100_000,
        "skill_candidate_enabled": True,
        "dev_lessons_shared": True,
        "heartbeat_monitoring": True,
        "yama_independent": False,
        "departure_script": False,
        "clinic_switch": False,
    },
    "T19": {
        "label": "T19 (19万円)",
        "handshake_quota_monthly": 200_000,
        "skill_candidate_enabled": True,
        "dev_lessons_shared": True,
        "heartbeat_monitoring": True,
        "yama_independent": True,
        "departure_script": True,
        "clinic_switch": True,
    },
}

# upgrade chain: T15 → T17 → T19 (downgrade も同 chain で可)
TIER_ORDER = ("T15", "T17", "T19")


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[billing_tier] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _fetch_clinic(sb, clinic_id: str) -> dict | None:
    try:
        res = (
            sb.table("clinic_master")
            .select("clinic_id,clinic_name,subscription_tier,active,billing_start_at")
            .eq("clinic_id", clinic_id)
            .execute()
        )
        return res.data[0] if res.data else None
    except Exception as exc:
        sys.stderr.write(f"[billing_tier] clinic_master query failed: {exc}\n")
        return None


def _count_handshake_this_month(sb, clinic_id: str) -> int:
    """当月 handshake 数を概算 (heartbeat 除外、quota 算定用)。"""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cutoff = month_start.strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        res = (
            sb.table("pc_handshake")
            .select("id", count="exact")
            .eq("clinic_id", clinic_id)
            .gte("created_at", cutoff)
            .not_.like("topic", "heartbeat %")
            .execute()
        )
        return res.count or 0
    except Exception as exc:
        sys.stderr.write(f"[billing_tier] handshake count failed: {exc}\n")
        return -1


def _is_quota_escalation_recent(sb, clinic_id: str, hours: int = 1) -> bool:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        res = (
            sb.table("pc_handshake")
            .select("id")
            .eq("clinic_id", clinic_id)
            .gte("created_at", cutoff)
            .like("topic", f"%billing quota 超過 {clinic_id}%")
            .limit(1)
            .execute()
        )
        return bool(res.data)
    except Exception:
        return False


def _send_quota_escalation(sb, clinic_id: str, tier: str, used: int, quota: int) -> str | None:
    """quota 超過時 副医院長 escalation を INSERT (重複抑止 1h)。"""
    if _is_quota_escalation_recent(sb, clinic_id):
        sys.stderr.write(f"[billing_tier] escalation recent, skip\n")
        return None
    now = datetime.now(timezone.utc)
    bucket = int(now.timestamp() // 3600)
    idem = f"billing-quota-{clinic_id}-{bucket}"
    payload = {
        "from_pc": "main_pc",
        "to_pc": "fukuincho",
        "priority": "urgent",
        "topic": f"billing quota 超過 {clinic_id} ({tier})",
        "content": (
            f"[billing tier quota 超過] clinic={clinic_id} tier={tier} "
            f"used={used} quota={quota} (当月 handshake、heartbeat 除外)。"
            f"tier upgrade or 一時 quota 緩和を判定してください。"
        ),
        "message_type": "status_update",
        "requires_response": True,
        "clinic_id": clinic_id,
        "context_data": {
            "shogun_kind": "escalation",
            "kind": "billing_quota_exceed",
            "tier": tier,
            "used": used,
            "quota": quota,
            "idempotency_key": idem,
        },
    }
    try:
        res = sb.table("pc_handshake").insert(payload).execute()
        return res.data[0]["id"] if res.data else None
    except Exception as exc:
        msg = str(exc)
        if "duplicate key" in msg or "23505" in msg or "idempotency" in msg.lower():
            sys.stderr.write(f"[billing_tier] escalation idempotency conflict, skip\n")
            return None
        sys.stderr.write(f"[billing_tier] escalation INSERT failed: {exc}\n")
        return None


def _print_check(clinic: dict | None, clinic_id: str) -> int:
    if not clinic:
        sys.stderr.write(
            f"[billing_tier] clinic_id={clinic_id} not in clinic_master "
            f"(migrations/001 未適用 or clinic 未登録)\n"
        )
        return 1
    tier = clinic.get("subscription_tier", "T15")
    feat = TIER_FEATURES.get(tier, TIER_FEATURES["T15"])
    sys.stdout.write(f"[billing_tier] === clinic={clinic_id} tier={tier} ===\n")
    sys.stdout.write(f"  name: {clinic.get('clinic_name','-')}\n")
    sys.stdout.write(f"  active: {clinic.get('active', False)}\n")
    sys.stdout.write(f"  billing_start_at: {clinic.get('billing_start_at','(unset)')}\n")
    sys.stdout.write(f"  features:\n")
    for k, v in feat.items():
        sys.stdout.write(f"    {k}: {v}\n")
    return 0


def _quota_check(sb, clinic_id: str, feature: str, escalate: bool) -> int:
    clinic = _fetch_clinic(sb, clinic_id)
    if not clinic:
        sys.stderr.write(f"[billing_tier] clinic_id={clinic_id} not found\n")
        return 1
    tier = clinic.get("subscription_tier", "T15")
    feat = TIER_FEATURES.get(tier, TIER_FEATURES["T15"])
    if feature == "handshake":
        used = _count_handshake_this_month(sb, clinic_id)
        if used < 0:
            return 4
        quota = feat.get("handshake_quota_monthly", 0)
        ratio = (used / quota) if quota > 0 else 1.0
        sys.stdout.write(
            f"[billing_tier] quota check: clinic={clinic_id} tier={tier} "
            f"used={used} quota={quota} ratio={ratio:.2%}\n"
        )
        if used > quota:
            sys.stdout.write("[billing_tier] STATUS: 🔴 EXCEEDED\n")
            if escalate:
                hid = _send_quota_escalation(sb, clinic_id, tier, used, quota)
                if hid:
                    sys.stdout.write(f"[billing_tier] escalation sent #{hid[:8]}\n")
            return 5
        if ratio > 0.9:
            sys.stdout.write("[billing_tier] STATUS: 🟡 WARNING (>90%)\n")
            return 0
        sys.stdout.write("[billing_tier] STATUS: 🟢 OK\n")
        return 0
    sys.stderr.write(f"[billing_tier] unknown feature '{feature}'\n")
    return 2


def _upgrade(sb, clinic_id: str, target_tier: str, reason: str | None) -> int:
    """tier upgrade/downgrade。clinic_master.subscription_tier 更新で
    migrations/004 trigger が clinic_subscription_audit へ自動記録。
    """
    if target_tier not in TIER_ORDER:
        sys.stderr.write(f"[billing_tier] invalid tier '{target_tier}'\n")
        return 2
    clinic = _fetch_clinic(sb, clinic_id)
    if not clinic:
        sys.stderr.write(f"[billing_tier] clinic_id={clinic_id} not found\n")
        return 1
    current = clinic.get("subscription_tier", "T15")
    if current == target_tier:
        sys.stdout.write(f"[billing_tier] no change (current={current})\n")
        return 0
    try:
        sb.table("clinic_master").update({
            "subscription_tier": target_tier,
        }).eq("clinic_id", clinic_id).execute()
        sys.stdout.write(
            f"[billing_tier] clinic={clinic_id} tier {current} → {target_tier} "
            f"updated. clinic_subscription_audit trigger fired (migrations/004)。\n"
        )
        # 注: change_reason / changed_by は trigger 側で source='system_update' になる。
        # 詳細記録が必要な場合は audit table へ直接追記 (本 CLI 範囲外、副医院長スコープ)
        if reason:
            sys.stdout.write(f"  reason (note): {reason}\n")
        return 0
    except Exception as exc:
        sys.stderr.write(f"[billing_tier] UPDATE failed: {exc}\n")
        return 4


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai subscription_tier 別機能制限")
    parser.add_argument("--clinic-id", default=CLINIC_ID,
                        help="対象 clinic (default: HAKUDOKAI_CLINIC_ID)")
    sub = parser.add_mutually_exclusive_group(required=True)
    sub.add_argument("--check", action="store_true",
                     help="現 clinic の tier + 機能一覧表示")
    sub.add_argument("--quota-check", metavar="feature=NAME",
                     help="quota check を実行 (feature=handshake)")
    sub.add_argument("--upgrade", action="store_true",
                     help="tier upgrade/downgrade (副医院長スコープ)")
    parser.add_argument("--to", choices=TIER_ORDER, help="--upgrade 時の target tier")
    parser.add_argument("--reason", help="--upgrade 時の理由 note")
    parser.add_argument("--escalate", action="store_true",
                        help="--quota-check 時、超過なら副医院長 escalation INSERT")
    args = parser.parse_args(argv)

    sb = _supabase_client()

    if args.check:
        clinic = _fetch_clinic(sb, args.clinic_id)
        return _print_check(clinic, args.clinic_id)

    if args.quota_check:
        feature = args.quota_check.split("=", 1)[-1] if "=" in args.quota_check else args.quota_check
        return _quota_check(sb, args.clinic_id, feature, args.escalate)

    if args.upgrade:
        if not args.to:
            sys.stderr.write("[billing_tier] --upgrade requires --to <T15|T17|T19>\n")
            return 2
        return _upgrade(sb, args.clinic_id, args.to, args.reason)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
