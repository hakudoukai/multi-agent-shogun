#!/usr/bin/env python3
"""
hakudokai_inbox_watcher.py — Supabase pc_handshake polling watcher.

shogun (yohey-w v4.6.0) の scripts/inbox_watcher.sh の Supabase 化版。
inotifywait + tmux send-keys は廃止し、5sec polling + idle flag + 緊急停止で
2PC 跨ぐエージェント間通知を実現する。

設計 (差分整理レポート §3、実装計画書 §4):
  Phase 1: 自身の inbox poll (5sec)、unread あれば標準出力に notify。
  Phase 2: idle flag (touch / rm) で busy/idle 判定、busy 中は notify 抑制。
  Phase 3 (/clear 強制) は採用しない (進行中作業消失のため)。
           緊急停止は副院長 urgent_stop で対応。

Idle flag (file 存在 = idle):
  /tmp/hakudokai_idle_${ROLE} (default), or $IDLE_FLAG_DIR/hakudokai_idle_${ROLE}
  busy 中はこの file を削除し、idle 復帰時に touch する。

Disable flags (Stop Hook と共通):
  ~/.openclaw/disable_auto_continue_${ROLE}     per-role 緊急停止
  ~/.openclaw/global_disable                    全自動連動 緊急停止

Required env:
    SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY)
    HAKUDOKAI_ROLE (or ~/.openclaw/role.json)

Usage:
    hakudokai_inbox_watcher.py [--once] [--interval 5] [--max-events 50]

License: MIT (shogun 原作者クレジット保持)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    from supabase import create_client
except ImportError:
    sys.stderr.write(
        "[inbox_watcher] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
    )
    sys.exit(2)


def _build_role_to_pc() -> dict:
    """Phase B-1: yama 独立化対応 (PHASE_B_ROADMAP §1 task 4)。

    Phase A 同居運用: yama → fukuincho (default)。
    Phase B 独立スレ運用: HAKUDOKAI_YAMA_PC env で別 PC 識別子に切替可能。
    後方互換のため未設定時は Phase A 挙動。
    """
    yama_pc = os.environ.get("HAKUDOKAI_YAMA_PC", "fukuincho")
    return {
        "fukuincho": "fukuincho",
        "yama": yama_pc,
        "kuro": "second_pc",
        "sakura": "second_pc",
        "kouchan": "main_pc",
    }


ROLE_TO_PC = _build_role_to_pc()


def _load_role_json() -> dict:
    role_file = os.path.expanduser("~/.openclaw/role.json")
    if not os.path.isfile(role_file):
        return {}
    with open(role_file, encoding="utf-8") as fh:
        return json.load(fh)


def _resolve_role() -> str:
    role = os.environ.get("HAKUDOKAI_ROLE")
    if role:
        return role.lower()
    cfg = _load_role_json()
    role = cfg.get("role")
    if role:
        return role.lower()
    raise SystemExit(
        "[inbox_watcher] cannot resolve role. "
        "Set HAKUDOKAI_ROLE env or create ~/.openclaw/role.json."
    )


def _idle_flag_path(role: str) -> str:
    # Codex audit fix #6: IDLE_FLAG_DIR の優先順位を env > role.json > /tmp デフォルトで参照
    base = os.environ.get("IDLE_FLAG_DIR")
    if not base:
        cfg = _load_role_json()
        base = cfg.get("idle_flag_dir") or "/tmp"
    return os.path.join(base, f"hakudokai_idle_{role}")


# Phase R2 (Gemini audit f0641407 #5 root-cause): notified_cache を file 依存 →
# Supabase table へ移行。両 PC 同期 + container 再起動・file 破損対策。
# 旧 file path (~/.openclaw/notified_${role}.json) は migration 後 deprecated、
# 互換維持のため初回起動時に Supabase へ import (best-effort)。

CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")
NOTIFIED_BY_PC = os.environ.get("HAKUDOKAI_PC_ID", "")  # main_pc / second_pc / fukuincho 等


def _notified_cache_path(role: str) -> str:
    """Legacy file path (deprecated since R2). Used only for one-time import."""
    base = os.path.expanduser(os.environ.get(
        "HAKUDOKAI_CACHE_DIR", "~/.openclaw"
    ))
    return os.path.join(base, f"notified_{role}.json")


def _load_notified_cache_from_db(sb, role: str) -> set[str]:
    """Phase R2: Supabase hakudokai_notified_cache から既通知 handshake_id を読込。
    最近 7 日分のみ load (古いものは pg_cron/watchdog で cleanup_old_notified_cache 経由削除)。
    """
    from datetime import datetime, timezone, timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    try:
        res = (
            sb.table("hakudokai_notified_cache")
            .select("handshake_id")
            .eq("clinic_id", CLINIC_ID)
            .eq("role", role)
            .gte("notified_at", cutoff)
            .limit(2000)
            .execute()
        )
        return {row["handshake_id"] for row in (res.data or []) if row.get("handshake_id")}
    except Exception as exc:
        sys.stderr.write(f"[inbox_watcher] DB cache load failed (fallback empty): {exc}\n")
        return set()


def _import_legacy_file_cache(sb, role: str) -> int:
    """Phase R2 一回限りの legacy file → Supabase migration。
    旧 file が存在すれば内容を hakudokai_notified_cache へ upsert、file は名称変更で deprecated marking。
    """
    path = _notified_cache_path(role)
    if not os.path.isfile(path):
        return 0
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        ids = data.get("ids", []) if isinstance(data, dict) else []
        if not ids:
            # Phase R4 Codex audit fix #5: 空 file も deprecated rename で無限リトライ防止
            try:
                os.replace(path, path + ".deprecated_phase_r2_empty")
            except OSError:
                pass
            return 0
        rows = [
            {
                "clinic_id": CLINIC_ID,
                "role": role,
                "handshake_id": hid,
                "notified_by_pc": NOTIFIED_BY_PC or "legacy_import",
            }
            for hid in ids
        ]
        sb.table("hakudokai_notified_cache").upsert(
            rows, on_conflict="clinic_id,role,handshake_id"
        ).execute()
        # file を rename で deprecated マーキング
        os.replace(path, path + ".deprecated_phase_r2")
        return len(rows)
    except Exception as exc:
        # Phase R4 Codex audit fix #5: parse 失敗 file も rename で無限リトライ防止
        sys.stderr.write(f"[inbox_watcher] legacy import failed (non-fatal): {exc}\n")
        try:
            os.replace(path, path + ".deprecated_phase_r2_corrupt")
        except OSError:
            pass
        return 0


def _record_notified_in_db(sb, role: str, handshake_ids: list[str]) -> list[str]:
    """Phase R4 Codex audit fix #3 (strict): 通知 race の loser を排除。
    INSERT ON CONFLICT DO NOTHING (ignore_duplicates=True) で実 INSERT された
    handshake_id のみ返す。UNIQUE constraint で他 instance が先に INSERT 済の id は除外。
    呼び出し側はこの戻り値で実際に「自身が race に勝った」分のみ notify する。
    """
    if not handshake_ids:
        return []
    rows = [
        {
            "clinic_id": CLINIC_ID,
            "role": role,
            "handshake_id": hid,
            "notified_by_pc": NOTIFIED_BY_PC or "unknown",
        }
        for hid in handshake_ids
    ]
    try:
        # ignore_duplicates=True で UNIQUE conflict 時は何もしない、実 INSERT 行のみ返却
        res = (
            sb.table("hakudokai_notified_cache")
            .upsert(rows, on_conflict="clinic_id,role,handshake_id", ignore_duplicates=True)
            .execute()
        )
        inserted_ids = [row.get("handshake_id") for row in (res.data or []) if row.get("handshake_id")]
        return inserted_ids
    except Exception as exc:
        sys.stderr.write(f"[inbox_watcher] notified_cache upsert failed: {exc}\n")
        return []


def _is_idle(role: str) -> bool:
    return os.path.isfile(_idle_flag_path(role))


def _is_disabled(role: str) -> tuple[bool, str]:
    """Return (disabled, reason). Used by Stop Hook & watcher."""
    home = os.path.expanduser("~")
    global_flag = os.path.join(home, ".openclaw", "global_disable")
    role_flag = os.path.join(home, ".openclaw", f"disable_auto_continue_{role}")
    if os.path.isfile(global_flag):
        return True, f"global_disable detected ({global_flag})"
    if os.path.isfile(role_flag):
        return True, f"role disable detected ({role_flag})"
    return False, ""


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit("[inbox_watcher] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing.")
    return create_client(url, key)


def _fetch_unread(sb, to_pc: str, max_events: int, clinic_id: str = "hakudoukai_main"):
    """Fetch unread (acknowledged_at IS NULL) handshakes targeted at the role's pc.

    Phase R4 Codex audit fix #2: clinic_id filter を SELECT に必須化、multi-tenant
    boundary を Read 側でも適用 (Write 側 INSERT clinic_id 自動付与済との一貫性)。
    """
    res = (
        sb.table("pc_handshake")
        .select("id,from_pc,to_pc,priority,topic,context_data,created_at,message_type,requires_response,clinic_id")
        .or_(f"to_pc.eq.{to_pc},to_pc.eq.broadcast")
        .eq("clinic_id", clinic_id)
        .is_("acknowledged_at", "null")
        .order("priority", desc=True)
        .order("created_at", desc=False)
        .limit(max_events)
        .execute()
    )
    return res.data or []


def _format_notify(role: str, item: dict) -> str:
    ctx = item.get("context_data") or {}
    kind = ctx.get("shogun_kind", "?") if isinstance(ctx, dict) else "?"
    cmd_id = ctx.get("cmd_id", "") if isinstance(ctx, dict) else ""
    head = f"[hakudokai_inbox][{role}] unread {item.get('priority','?')} {item.get('message_type','?')} kind={kind}"
    if cmd_id:
        head += f" cmd={cmd_id}"
    head += f" id={item.get('id','?')[:8]} from={item.get('from_pc','?')}"
    head += f" topic={(item.get('topic') or '')[:60]}"
    return head


def _emit_notify(items: list[dict], role: str) -> None:
    """Print notifications to stdout. Stop Hook / Claude Code が読み取り、
    自動でターン継続のシグナルとして使う。"""
    if not items:
        return
    payload = {
        "role": role,
        "ts": datetime.now(timezone.utc).isoformat(),
        "unread_count": len(items),
        "items": [
            {
                "id": it.get("id"),
                "priority": it.get("priority"),
                "from_pc": it.get("from_pc"),
                "to_pc": it.get("to_pc"),
                "message_type": it.get("message_type"),
                "shogun_kind": (it.get("context_data") or {}).get("shogun_kind") if isinstance(it.get("context_data"), dict) else None,
                "topic": it.get("topic"),
                "requires_response": it.get("requires_response"),
                "created_at": it.get("created_at"),
            }
            for it in items
        ],
    }
    sys.stdout.write("HAKUDOKAI_INBOX_NOTIFY=" + json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai inbox watcher (Supabase polling).")
    parser.add_argument("--once", action="store_true", help="poll once and exit")
    parser.add_argument("--interval", type=int, default=int(os.environ.get("HAKUDOKAI_POLL_INTERVAL", "5")),
                        help="polling interval in seconds (default: 5)")
    parser.add_argument("--max-events", type=int, default=20, help="max events per poll (default: 20)")
    parser.add_argument("--respect-busy", action="store_true",
                        help="suppress notify if idle flag absent (busy)")
    parser.add_argument("--quiet", action="store_true", help="suppress informational logs")
    args = parser.parse_args(argv)

    role = _resolve_role()
    to_pc = ROLE_TO_PC.get(role)
    if not to_pc:
        raise SystemExit(f"[inbox_watcher] unknown role '{role}'. valid: {sorted(ROLE_TO_PC)}")

    sb = _supabase_client()

    # Phase R2: Supabase 永続 cache を初期化、必要なら legacy file から one-time import
    imported = _import_legacy_file_cache(sb, role)
    if imported and not args.quiet:
        sys.stderr.write(f"[inbox_watcher] legacy file cache imported {imported} ids → Supabase\n")
    notified_cache = _load_notified_cache_from_db(sb, role)

    if not args.quiet:
        sys.stderr.write(
            f"[inbox_watcher] role={role} clinic={CLINIC_ID} to_pc={to_pc} interval={args.interval}s "
            f"once={args.once} respect_busy={args.respect_busy} "
            f"cache_size={len(notified_cache)} (Supabase-backed)\n"
        )

    while True:
        disabled, reason = _is_disabled(role)
        if disabled:
            sys.stderr.write(f"[inbox_watcher] disabled: {reason}; sleeping\n")
            if args.once:
                return 0
            time.sleep(args.interval)
            continue

        if args.respect_busy and not _is_idle(role):
            if not args.quiet:
                sys.stderr.write(f"[inbox_watcher] role busy (no idle flag), suppressing notify\n")
        else:
            try:
                items = _fetch_unread(sb, to_pc, args.max_events, clinic_id=CLINIC_ID)
            except Exception as exc:
                sys.stderr.write(f"[inbox_watcher] fetch error: {exc}\n")
                items = []
            # Phase R4 Codex audit fix #3: race condition 抑止
            # 複数 watcher 同時起動時、notify 直前に DB 側 notified_cache を再参照して
            # 直近 30秒以内に他 instance が記録した id を排除。UNIQUE upsert は最終防御。
            candidate_ids = [it["id"] for it in items if it.get("id") and it["id"] not in notified_cache]
            if candidate_ids:
                try:
                    res = (
                        sb.table("hakudokai_notified_cache")
                        .select("handshake_id")
                        .eq("clinic_id", CLINIC_ID)
                        .eq("role", role)
                        .in_("handshake_id", candidate_ids)
                        .execute()
                    )
                    db_already = {row["handshake_id"] for row in (res.data or [])}
                    if db_already:
                        notified_cache |= db_already
                except Exception as exc:
                    sys.stderr.write(f"[inbox_watcher] race precheck failed (non-fatal): {exc}\n")
            new_items = [it for it in items if it.get("id") and it["id"] not in notified_cache]
            if new_items:
                # Phase R4 strict: upsert ignore_duplicates → 実 INSERT 行のみ notify
                # race loser は upsert 結果が空、winner のみが自身の id を取り戻して notify
                inserted_ids = _record_notified_in_db(sb, role, [it["id"] for it in new_items])
                inserted_set = set(inserted_ids)
                won_items = [it for it in new_items if it["id"] in inserted_set]
                if won_items:
                    _emit_notify(won_items, role)
                    for it in won_items:
                        sys.stderr.write(_format_notify(role, it) + "\n")
                        notified_cache.add(it["id"])
                # race loser 分は他 watcher が notify 済 → 自身の cache にも記録 (重複 notify 防止)
                for it in new_items:
                    if it["id"] not in inserted_set:
                        notified_cache.add(it["id"])
            elif items and not args.quiet:
                sys.stderr.write(
                    f"[inbox_watcher] {len(items)} unread items already notified (suppressed)\n"
                )

        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
