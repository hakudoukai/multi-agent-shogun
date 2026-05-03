#!/usr/bin/env python3
"""
hakudokai_heartbeat_check.py — 博道会 heartbeat 不達検知 (Phase B-2 task 3)

各 role の最新 heartbeat タイムスタンプを取得し、threshold 超過時に
副医院長 escalation を pc_handshake INSERT (shogun_kind=escalation, priority=urgent)。

cron 設定例 (setup-departure.md task 3 参照):
  */10 * * * * cd /path/to/hakudokai-shogun && \\
    python3 scripts/hakudokai_heartbeat_check.py --threshold-min 15

Usage:
  hakudokai_heartbeat_check.py [--threshold-min N] [--dry-run] [--escalate]

設計上の注意:
- threshold-min default 15: heartbeat sender が 5min 間隔の場合、3 連続欠損で escalation
- escalation 重複防止: 同 role 1h 以内に既送信なら抑制 (idempotency_key で UNIQUE)
- --dry-run: 検知のみ、INSERT しない (運用テスト用)
- --escalate なし: status report のみ stdout、副医院長 INSERT しない (default safe mode)

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
        "[heartbeat_check] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)

# Phase R1 PII detector を再利用 (Codex audit B-2-3 #4 修正)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
try:
    from hakudokai_pii_detector import scan_for_pii  # type: ignore
except ImportError:
    scan_for_pii = None  # type: ignore


VALID_ROLES = ("fukuincho", "yama", "kuro", "sakura", "kouchan")
CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


def _abort_if_pii(text: str, label: str) -> None:
    """escalation content に PII が混入した場合 INSERT 中止。"""
    if not text or scan_for_pii is None:
        return
    try:
        matches = list(scan_for_pii(text))
    except Exception:
        return
    if matches:
        sys.stderr.write(
            f"[heartbeat_check] PII detected in {label}, abort INSERT (matches={len(matches)})\n"
        )
        raise SystemExit(5)


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[heartbeat_check] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _heartbeat_table_exists(sb) -> bool:
    """Phase B-4 続編 task 7: pc_handshake_heartbeat (migrations/003 適用済) の存在確認。

    存在すれば自動切替で参照し、無ければ Phase A 後方互換で pc_handshake から検索。
    判定には select 1 行を試みる。エラーは「未存在」扱い。
    """
    try:
        sb.table("pc_handshake_heartbeat").select("id").limit(1).execute()
        return True
    except Exception:
        return False


def _latest_heartbeat_per_role(sb, lookback_min: int) -> dict[str, datetime | None]:
    """role 毎の最新 heartbeat 時刻を取得。

    Phase B-4 続編 task 7: pc_handshake_heartbeat (専用 table) があれば自動切替、
    無ければ Phase A 後方互換で pc_handshake.context_data->>'shogun_kind' = 'heartbeat' 検索。
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=lookback_min)).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest: dict[str, datetime | None] = {role: None for role in VALID_ROLES}

    if _heartbeat_table_exists(sb):
        # Phase B 経路: pc_handshake_heartbeat 専用 table 参照
        res = (
            sb.table("pc_handshake_heartbeat")
            .select("role,from_pc,ts")
            .eq("clinic_id", CLINIC_ID)
            .gte("ts", cutoff)
            .order("ts", desc=True)
            .limit(500)
            .execute()
        )
        for row in res.data or []:
            role = row.get("role") or row.get("from_pc")
            if role not in latest:
                continue
            ts_str = row.get("ts")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except Exception:
                continue
            if latest[role] is None or ts > latest[role]:
                latest[role] = ts
        return latest

    # Phase A 後方互換経路: pc_handshake から shogun_kind=heartbeat 抽出
    res = (
        sb.table("pc_handshake")
        .select("from_pc,context_data,created_at")
        .eq("clinic_id", CLINIC_ID)
        .gte("created_at", cutoff)
        .order("created_at", desc=True)
        .limit(500)
        .execute()
    )
    for row in res.data or []:
        ctx = row.get("context_data") or {}
        if ctx.get("shogun_kind") != "heartbeat":
            continue
        role = ctx.get("role") or row.get("from_pc")
        if role not in latest:
            continue
        ts_str = row.get("created_at")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            continue
        if latest[role] is None or ts > latest[role]:
            latest[role] = ts
    return latest


def _is_escalation_recent(sb, role: str, hours: int = 1) -> bool:
    """同 role への escalation を直近 hours 以内に既送信済か。"""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    res = (
        sb.table("pc_handshake")
        .select("id,context_data,created_at")
        .eq("clinic_id", CLINIC_ID)
        .gte("created_at", cutoff)
        .like("topic", f"%heartbeat 不達 {role}%")
        .limit(1)
        .execute()
    )
    return bool(res.data)


def _send_escalation(sb, role: str, last_seen: datetime | None,
                     threshold_min: int, dry_run: bool) -> str | None:
    """副医院長へ escalation INSERT。"""
    now = datetime.now(timezone.utc)
    last = last_seen.strftime("%Y-%m-%dT%H:%M:%SZ") if last_seen else "never"
    elapsed = (
        f"{int((now - last_seen).total_seconds() / 60)} min"
        if last_seen else "unknown"
    )
    content = (
        f"[heartbeat 不達検知] role={role} threshold={threshold_min}min "
        f"last_seen={last} elapsed={elapsed}. 該当 role の inbox_watcher / "
        f"departure script / PC 状態を確認してください。"
    )
    # Phase R1 PII guard 継承 (Codex audit B-2-3 #4)
    _abort_if_pii(content, "content")
    bucket = int(now.timestamp() // 3600)
    idem = f"heartbeat-escalation-{role}-{bucket}"
    payload = {
        "from_pc": "main_pc",
        "to_pc": "fukuincho",
        "priority": "urgent",
        "topic": f"heartbeat 不達 {role} (threshold {threshold_min}min)",
        "content": content,
        "message_type": "status_update",
        "requires_response": True,
        "clinic_id": CLINIC_ID,
        "context_data": {
            "shogun_kind": "escalation",
            "target_role": role,
            "threshold_min": threshold_min,
            "last_seen": last,
            "elapsed": elapsed,
            "idempotency_key": idem,
        },
    }
    if dry_run:
        sys.stderr.write(
            f"[heartbeat_check] (dry-run) escalation: role={role} elapsed={elapsed}\n"
        )
        return None
    try:
        res = sb.table("pc_handshake").insert(payload).execute()
        if res.data:
            return res.data[0]["id"]
    except Exception as exc:
        sys.stderr.write(f"[heartbeat_check] escalation insert failed: {exc}\n")
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai heartbeat 不達検知")
    parser.add_argument(
        "--threshold-min", type=int, default=15,
        help="heartbeat 不達と判定する経過分 (default: 15min)",
    )
    parser.add_argument(
        "--lookback-min", type=int, default=120,
        help="heartbeat 検索範囲分 (default: 120min)",
    )
    parser.add_argument(
        "--escalate", action="store_true",
        help="不達時 副医院長 escalation INSERT を有効化 (default: status report のみ)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="--escalate と組合わせて INSERT 実行せず確認のみ",
    )
    args = parser.parse_args(argv)

    sb = _supabase_client()
    latest = _latest_heartbeat_per_role(sb, args.lookback_min)
    now = datetime.now(timezone.utc)

    findings = []
    for role in VALID_ROLES:
        ts = latest.get(role)
        if ts is None:
            findings.append((role, None, "missing"))
            continue
        elapsed_min = (now - ts).total_seconds() / 60
        if elapsed_min > args.threshold_min:
            findings.append((role, ts, f"stale {int(elapsed_min)}min"))
        else:
            findings.append((role, ts, f"alive {int(elapsed_min)}min"))

    sys.stdout.write("[heartbeat_check] === status ===\n")
    for role, ts, status in findings:
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ") if ts else "-"
        sys.stdout.write(f"  {role}: {status} (last_seen={ts_str})\n")

    if args.escalate:
        for role, ts, status in findings:
            if not status.startswith(("stale", "missing")):
                continue
            if _is_escalation_recent(sb, role):
                sys.stderr.write(f"[heartbeat_check] {role}: escalation recent, skip\n")
                continue
            hid = _send_escalation(sb, role, ts, args.threshold_min, args.dry_run)
            if hid:
                sys.stdout.write(f"[heartbeat_check] escalation sent #{hid[:8]} role={role}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
