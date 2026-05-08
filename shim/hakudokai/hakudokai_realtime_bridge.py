#!/usr/bin/env python3
# hakudokai_realtime_bridge.py — Tier 1 v2 Phase C
#
# Supabase Realtime channel 'shogun-bridge' subscriber:
#   1. Presence: 各 PC alive 状態を Phoenix Tracker CRDT で散布、自動 self-heal
#   2. postgres_changes: pc_handshake INSERT を購読 (= push 型同期、polling 不要)
#   3. partition detection: 5min 以上 leave で alert
#
# 既存 polling watcher (hakudokai_fukuincho_watcher / secondpc_watcher 等) と並走。
# Realtime 障害時は polling watcher が fallback (= §15 SH3 graceful degradation)。
#
# Usage:
#   nohup python3 shim/hakudokai/hakudokai_realtime_bridge.py > /tmp/realtime_bridge.log 2>&1 &
#
# 前提:
#   - SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (~/.hakudokai/env)
#   - HAKUDOKAI_PC_ROLE (= MainPC | SecondPC)
#   - pip install realtime (Supabase Python Realtime client)
#
# 設計: docs/tier1_v2_minimal_extension_design_2026-05-08.md §1.2

import os
import sys
import time
import json
import logging
import asyncio
import signal
from pathlib import Path
from datetime import datetime, timezone

# ─── env loading (= ~/.hakudokai/env auto-source) ───
HOME = os.environ.get("HOME", "")
ENV_FILE = Path(HOME) / ".hakudokai" / "env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().rstrip("\r"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PC_ROLE = os.environ.get("HAKUDOKAI_PC_ROLE", "MainPC")
DISABLE_FLAG = Path(HOME) / ".openclaw" / "disable_realtime_bridge"
GLOBAL_DISABLE = Path(HOME) / ".openclaw" / "global_disable"

# ─── logging ───
SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent
LOG_FILE = SCRIPT_DIR / "logs" / f"realtime_bridge_{datetime.now().strftime('%Y%m%d')}.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='{"ts":"%(asctime)s","level":"%(levelname)s","component":"realtime_bridge","msg":"%(message)s"}',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("realtime_bridge")

# ─── partition state ───
last_seen_peers: dict[str, float] = {}  # pc_role -> last_seen epoch
PARTITION_THRESHOLD_SEC = 300  # 5 min


def check_disable_flags() -> bool:
    """global_disable or specific disable flag check"""
    if GLOBAL_DISABLE.exists():
        logger.info("global_disable flag detected, exiting")
        return True
    if DISABLE_FLAG.exists():
        logger.info("realtime_bridge disable flag detected, exiting")
        return True
    return False


def handle_presence_sync(payload):
    """Presence state 同期 (各 PC の online 状態)"""
    state = payload.get("state", {}) if isinstance(payload, dict) else {}
    for key, presences in state.items():
        last_seen_peers[key] = time.time()
        logger.info(f"presence_sync: {key} online ({len(presences)} sessions)")


def handle_presence_join(payload):
    key = payload.get("key", "?") if isinstance(payload, dict) else "?"
    last_seen_peers[key] = time.time()
    logger.info(f"presence_join: {key}")


def handle_presence_leave(payload):
    key = payload.get("key", "?") if isinstance(payload, dict) else "?"
    logger.warning(f"presence_leave: {key}")
    # Note: leave は ungraceful disconnect 時即発火、5min 後に partition_alert で確定


def handle_postgres_changes(payload):
    """pc_handshake INSERT 購読: push 型 cross-PC delivery"""
    if not isinstance(payload, dict):
        return
    record = payload.get("data", {}).get("record", {}) if isinstance(payload.get("data"), dict) else {}
    msg_type = record.get("msg_type", "?")
    to_pc = record.get("to_pc", "?")
    if to_pc == PC_ROLE or to_pc == "broadcast":
        logger.info(f"pc_handshake INSERT: type={msg_type} to={to_pc} seq={record.get('seq')}")
        # 既存 polling watcher (fukuincho_watcher / secondpc_watcher) が処理する経路と並走
        # Realtime push が先なら polling は idempotency_key で skip (= dedup)


async def partition_check_loop():
    """5 min 以上 leave した peer を検知"""
    while True:
        if check_disable_flags():
            return
        now = time.time()
        for pc, last_seen in list(last_seen_peers.items()):
            age = now - last_seen
            if age >= PARTITION_THRESHOLD_SEC:
                logger.error(f"partition_detected: {pc} last_seen {age:.0f}s ago (>={PARTITION_THRESHOLD_SEC}s)")
                # graceful degradation: ntfy alert + dashboard 更新は別 daemon (= activity_monitor) が拾う
        await asyncio.sleep(60)


async def main():
    if check_disable_flags():
        return
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set, exiting")
        return

    try:
        from realtime import AsyncRealtimeClient
    except ImportError:
        logger.error("realtime python client not installed; install via: pip install realtime")
        # fallback: polling watcher が引き続き動作するゆえ critical でない
        return

    # Realtime endpoint URL 構築
    rt_url = SUPABASE_URL.replace("https://", "wss://").replace("http://", "ws://") + "/realtime/v1"
    client = AsyncRealtimeClient(rt_url, SUPABASE_KEY)

    try:
        await client.connect()
    except Exception as e:
        logger.error(f"realtime connect failed: {e}")
        return

    channel = client.channel("shogun-bridge")

    # Presence (= 各 PC alive 状態)
    channel.on_presence_sync(handle_presence_sync)
    channel.on_presence_join(handle_presence_join)
    channel.on_presence_leave(handle_presence_leave)

    # postgres_changes (= pc_handshake INSERT push)
    channel.on_postgres_changes(
        event="INSERT",
        schema="public",
        table="pc_handshake",
        callback=handle_postgres_changes,
    )

    # subscribe + presence track
    await channel.subscribe()
    await channel.track({
        "pc_role": PC_ROLE,
        "online_at": datetime.now(timezone.utc).isoformat(),
        "host": os.uname().nodename,
    })
    logger.info(f"shogun-bridge subscribed + presence tracked as {PC_ROLE}")

    # graceful shutdown
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    # partition check task
    partition_task = asyncio.create_task(partition_check_loop())

    # main wait loop with disable flag periodic check
    while not stop_event.is_set():
        if check_disable_flags():
            break
        await asyncio.sleep(30)

    # cleanup
    partition_task.cancel()
    try:
        await client.close()
    except Exception:
        pass
    logger.info("shogun-bridge shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("interrupted")
    except Exception as e:
        logger.error(f"fatal: {e}", exc_info=True)
        sys.exit(1)
