#!/usr/bin/env python3
"""
hakudokai_heartbeat.py — 博道会 heartbeat sender (Phase B-2 task 3)

各 role が pc_handshake に shogun_kind=heartbeat record を定期 INSERT する。
不達検知 (5min 以上 heartbeat 無し) は別 script (hakudokai_heartbeat_check.py)
で副医院長 escalation を発射する。

Usage:
  hakudokai_heartbeat.py                      # role 自動検出 (~/.openclaw/role.json)
  hakudokai_heartbeat.py --role kouchan       # 明示指定
  hakudokai_heartbeat.py --once               # 1 回のみ送信して終了
  hakudokai_heartbeat.py --interval 300       # 5min 間隔ループ (default)

設計上の注意:
- shogun_kind="heartbeat" は VALID_KINDS には含まないが、context_data jsonb 拡張として記録
- to_pc=fukuincho (副医院長集約宛)、message_type=status_update、priority=low
- requires_response=False (副医院長の応答不要)
- content は短文 (PII 検出回避)
- idempotency_key は `heartbeat-{role}-{bucket_sec}-{bucket}` で重複抑止
  bucket_sec = max(60, --interval 値)、bucket = floor(epoch / bucket_sec)
  default --interval 300 で実質 5min bucket

License: MIT (shogun upstream credit 保持)
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
        "[heartbeat] supabase-py not installed. pip install 'supabase>=2.0.0'\n"
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
    """heartbeat content に PII が検出されたら INSERT 中止 (Phase R1 二重防御の継承)。"""
    if not text or scan_for_pii is None:
        return
    try:
        matches = list(scan_for_pii(text))
    except Exception:
        return
    if matches:
        sys.stderr.write(
            f"[heartbeat] PII detected in {label}, abort INSERT (matches={len(matches)})\n"
        )
        raise SystemExit(5)


def _resolve_role() -> str:
    role = os.environ.get("HAKUDOKAI_ROLE")
    if role:
        return role.lower()
    role_file = os.path.expanduser("~/.openclaw/role.json")
    if os.path.isfile(role_file):
        try:
            with open(role_file, encoding="utf-8") as fh:
                cfg = json.load(fh)
            r = cfg.get("role")
            if r:
                return r.lower()
        except Exception as exc:
            sys.stderr.write(f"[heartbeat] role.json parse failed: {exc}\n")
    raise SystemExit("[heartbeat] cannot resolve role")


def _resolve_from_pc(role: str) -> str:
    """yama は Phase A 同居 (fukuincho) / Phase B 独立 (HAKUDOKAI_YAMA_PC) と同じ規約。"""
    yama_pc = os.environ.get("HAKUDOKAI_YAMA_PC", "fukuincho")
    table = {
        "fukuincho": "fukuincho",
        "yama": yama_pc,
        "kuro": "second_pc",
        "sakura": "second_pc",
        "kouchan": "main_pc",
    }
    return table.get(role, role)


def _supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
    )
    if not url or not key:
        raise SystemExit(
            "[heartbeat] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY env missing."
        )
    return create_client(url, key)


def _heartbeat_table_exists(sb) -> bool:
    """Phase B-4 続編 task 7: pc_handshake_heartbeat (migrations/003 適用済) の存在確認。
    存在すれば sender / checker 両方が pc_handshake_heartbeat を書込/参照する。
    無ければ Phase A 後方互換で pc_handshake へ書込。
    """
    try:
        sb.table("pc_handshake_heartbeat").select("id").limit(1).execute()
        return True
    except Exception:
        return False


def _send_heartbeat(sb, role: str, from_pc: str, interval_sec: int,
                    dry_run: bool = False) -> str | None:
    """1 回 heartbeat を INSERT。idempotency_key は role + bucket で重複抑止。

    Codex audit B-2-3 #3 修正: bucket 幅 = max(60, interval_sec) を使う
    (interval_sec 設定値そのものを bucket 幅とすることで仕様一致)。
    `--dry-run` で副作用なしテスト可能。

    Codex audit B-4-EXT #1 修正: pc_handshake_heartbeat (migrations/003 適用済) 存在で自動切替、
    sender/checker 両者が同 table を参照することで中間状態の不整合を回避。
    """
    now = datetime.now(timezone.utc)
    bucket_sec = max(60, interval_sec)
    bucket = int(now.timestamp() // bucket_sec)
    idem = f"heartbeat-{role}-{bucket_sec}-{bucket}"
    content = f"[heartbeat] role={role} ts={now.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    # Phase R1 PII guard 継承 (短文固定だが規律として scan)
    _abort_if_pii(content, "content")

    # Codex audit B-4-EXT #1: 専用 table 存在で Phase B 経路へ自動切替
    use_dedicated = _heartbeat_table_exists(sb)
    if dry_run:
        target = "pc_handshake_heartbeat" if use_dedicated else "pc_handshake"
        sys.stderr.write(
            f"[heartbeat] (dry-run) would insert role={role} idem={idem} target={target}\n"
        )
        return None

    if use_dedicated:
        # Phase B 経路: pc_handshake_heartbeat へ直接 INSERT (専用 schema)
        payload = {
            "clinic_id": CLINIC_ID,
            "role": role,
            "from_pc": from_pc,
            "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "interval_sec": interval_sec,
            "bucket_sec": bucket_sec,
            "bucket": bucket,
            "idempotency_key": idem,
        }
        try:
            res = sb.table("pc_handshake_heartbeat").insert(payload).execute()
            if res.data:
                return res.data[0]["id"]
        except Exception as exc:
            msg = str(exc)
            if "duplicate key" in msg or "23505" in msg or "idempotency" in msg.lower():
                return None
            sys.stderr.write(f"[heartbeat] dedicated insert failed: {exc}\n")
        return None

    # Phase A 経路: pc_handshake へ context_data 経由で INSERT (後方互換)
    payload = {
        "from_pc": from_pc,
        "to_pc": "fukuincho",
        "priority": "low",
        "topic": f"heartbeat {role}",
        "content": content,
        "message_type": "status_update",
        "requires_response": False,
        "clinic_id": CLINIC_ID,
        "context_data": {
            "shogun_kind": "heartbeat",
            "role": role,
            "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "interval_sec": interval_sec,
            "bucket_sec": bucket_sec,
            "idempotency_key": idem,
        },
    }
    try:
        res = sb.table("pc_handshake").insert(payload).execute()
        if res.data:
            return res.data[0]["id"]
    except Exception as exc:
        msg = str(exc)
        # idempotency_key UNIQUE conflict は許容 (同 bucket 内重複)
        if "duplicate key" in msg or "23505" in msg or "idempotency" in msg.lower():
            return None
        sys.stderr.write(f"[heartbeat] insert failed: {exc}\n")
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="hakudokai heartbeat sender")
    parser.add_argument("--role", default=None, choices=(*VALID_ROLES, None))
    parser.add_argument("--once", action="store_true", help="send once and exit")
    parser.add_argument(
        "--interval", type=int,
        default=int(os.environ.get("HAKUDOKAI_HEARTBEAT_INTERVAL", "300")),
        help="seconds between heartbeats (default: 300=5min)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="副作用なし (INSERT 実行せず、payload 計算のみ)",
    )
    args = parser.parse_args(argv)

    role = args.role or _resolve_role()
    if role not in VALID_ROLES:
        raise SystemExit(f"[heartbeat] invalid role '{role}'")
    from_pc = _resolve_from_pc(role)

    sb = _supabase_client()
    sys.stderr.write(
        f"[heartbeat] role={role} from_pc={from_pc} interval={args.interval}s clinic={CLINIC_ID}\n"
    )

    while True:
        hid = _send_heartbeat(sb, role, from_pc, args.interval, dry_run=args.dry_run)
        if hid:
            sys.stderr.write(f"[heartbeat] sent #{hid[:8]}\n")
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
