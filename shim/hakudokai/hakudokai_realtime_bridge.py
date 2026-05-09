#!/usr/bin/env python3
"""
hakudokai_realtime_bridge.py — 博道会 cross-PC realtime bridge

Bridges MainPC (信長 shogun) and SecondPC (副医院長 fukuincho) via Supabase.
Uses asyncpg advisory lock (pg_try_advisory_lock) to establish MainPC as leader.

Modes:
  leader  — MainPC holds advisory lock + bridges messages
  worker  — SecondPC (or MainPC when lock unavailable) bridges without lock

Usage:
  python3 hakudokai_realtime_bridge.py [--poll-interval N]

Env:
  SUPABASE_DB_URL        — PostgreSQL DSN (asyncpg, for advisory lock)
  SUPABASE_URL           — REST endpoint
  SUPABASE_SERVICE_ROLE_KEY — REST key
  HAKUDOKAI_PC_ROLE      — 'main_pc' or 'fukuincho' (default: fukuincho)
  HAKUDOKAI_CLINIC_ID    — clinic identifier (default: hakudoukai_main)

License: MIT (shogun upstream credit 保持)
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

try:
    import asyncpg
except ImportError:
    sys.stderr.write(
        "[realtime_bridge] asyncpg not installed. pip install asyncpg\n"
    )
    sys.exit(2)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("hakudokai_realtime_bridge")

ADVISORY_LOCK_KEY = "shogun-leader"
CLINIC_ID = os.environ.get("HAKUDOKAI_CLINIC_ID", "hakudoukai_main")


def _get_env() -> tuple[str, str, str, str]:
    """Return (db_url, rest_url, rest_key, pc_role).

    Reads from environment first, then ~/.hakudokai/env fallback.
    """
    db_url = os.environ.get("SUPABASE_DB_URL", "")
    rest_url = os.environ.get("SUPABASE_URL", "")
    rest_key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY", "")
    )
    pc_role = os.environ.get("HAKUDOKAI_PC_ROLE", "fukuincho")

    if not all([db_url, rest_url, rest_key]):
        env_file = os.path.expanduser("~/.hakudokai/env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SUPABASE_DB_URL=") and not db_url:
                        db_url = line.split("=", 1)[1]
                    elif line.startswith("SUPABASE_URL=") and not rest_url:
                        rest_url = line.split("=", 1)[1]
                    elif line.startswith("SUPABASE_SERVICE_ROLE_KEY=") and not rest_key:
                        rest_key = line.split("=", 1)[1]
                    elif line.startswith("HAKUDOKAI_PC_ROLE=") and not pc_role:
                        pc_role = line.split("=", 1)[1]

    return db_url, rest_url, rest_key, pc_role


async def _acquire_advisory_lock(conn: asyncpg.Connection) -> bool:
    """Try pg_try_advisory_lock(hashtext('shogun-leader')).

    Returns True if lock was acquired (= this PC is leader).
    """
    row = await conn.fetchrow(
        "SELECT pg_try_advisory_lock(hashtext($1)) AS acquired",
        ADVISORY_LOCK_KEY,
    )
    return bool(row["acquired"])


async def _release_advisory_lock(conn: asyncpg.Connection) -> None:
    await conn.execute(
        "SELECT pg_advisory_unlock(hashtext($1))",
        ADVISORY_LOCK_KEY,
    )


def _fetch_pending_messages(rest_url: str, rest_key: str) -> list[dict]:
    """Fetch unacknowledged pc_handshake messages for this PC."""
    pc_role = os.environ.get("HAKUDOKAI_PC_ROLE", "fukuincho")
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=10)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    query = (
        f"{rest_url}/rest/v1/pc_handshake"
        f"?to_pc=eq.{pc_role}"
        f"&acknowledged_at=is.null"
        f"&created_at=gte.{cutoff}"
        f"&clinic_id=eq.{CLINIC_ID}"
        f"&order=created_at.asc&limit=20"
    )
    try:
        req = urllib.request.Request(query)
        req.add_header("Authorization", f"Bearer {rest_key}")
        req.add_header("apikey", rest_key)
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode())
    except Exception as exc:
        log.warning("fetch_pending failed: %s", exc)
        return []


def _acknowledge_message(rest_url: str, rest_key: str, msg_id: str) -> bool:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = json.dumps({"acknowledged_at": now}).encode()
    try:
        req = urllib.request.Request(
            f"{rest_url}/rest/v1/pc_handshake?id=eq.{msg_id}",
            data=data,
            method="PATCH",
        )
        req.add_header("Authorization", f"Bearer {rest_key}")
        req.add_header("apikey", rest_key)
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "return=minimal")
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as exc:
        log.warning("ack_message %s failed: %s", msg_id, exc)
        return False


def _dispatch_message(msg: dict) -> None:
    """Process a received cross-PC message (bridge delivery)."""
    topic = msg.get("topic", "")
    content = msg.get("content", "")
    from_pc = msg.get("from_pc", "?")
    msg_type = msg.get("message_type", "?")
    log.info("bridge recv [%s] from=%s topic=%s :: %s", msg_type, from_pc, topic, content[:100])


async def _bridge_loop(
    rest_url: str,
    rest_key: str,
    poll_interval: int,
    stop_event: asyncio.Event,
    is_leader: bool,
) -> None:
    """Main polling loop: fetch + ack cross-PC messages."""
    mode = "leader" if is_leader else "worker"
    log.info("bridge loop started (mode=%s, poll=%ds)", mode, poll_interval)
    while not stop_event.is_set():
        try:
            messages = await asyncio.get_event_loop().run_in_executor(
                None, _fetch_pending_messages, rest_url, rest_key
            )
            for msg in messages:
                _dispatch_message(msg)
                await asyncio.get_event_loop().run_in_executor(
                    None, _acknowledge_message, rest_url, rest_key, msg["id"]
                )
        except Exception as exc:
            log.warning("bridge_loop iteration error: %s", exc)

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=poll_interval)
        except asyncio.TimeoutError:
            pass

    log.info("bridge loop stopped (mode=%s)", mode)


async def _run(poll_interval: int) -> None:
    db_url, rest_url, rest_key, pc_role = _get_env()
    stop_event = asyncio.Event()

    def _handle_signal(sig: int, _frame: object) -> None:
        log.info("signal %d received — initiating graceful shutdown", sig)
        stop_event.set()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    pool: asyncpg.Pool | None = None
    lock_conn: asyncpg.Connection | None = None
    is_leader = False

    if pc_role == "main_pc":
        if not db_url:
            log.error("SUPABASE_DB_URL required for MainPC advisory lock — set env and retry")
            sys.exit(1)
        try:
            pool = await asyncpg.create_pool(db_url, min_size=1, max_size=3)
            lock_conn = await pool.acquire()
            is_leader = await _acquire_advisory_lock(lock_conn)
            if is_leader:
                log.info("advisory lock acquired — running as leader (main_pc)")
            else:
                log.warning(
                    "pg_try_advisory_lock returned false — another process holds shogun-leader lock. "
                    "Continuing as worker mode."
                )
                await pool.release(lock_conn)
                lock_conn = None
        except Exception as exc:
            log.warning(
                "asyncpg pool/lock setup failed (%s) — continuing as worker mode", exc
            )
            if pool is not None:
                await pool.close()
                pool = None
            lock_conn = None
    else:
        log.info("pc_role=%s — running as worker (no advisory lock)", pc_role)

    try:
        await _bridge_loop(rest_url, rest_key, poll_interval, stop_event, is_leader)
    finally:
        if lock_conn is not None:
            try:
                await _release_advisory_lock(lock_conn)
                log.info("advisory lock released")
            except Exception as exc:
                log.warning("advisory_unlock failed: %s", exc)
            try:
                await pool.release(lock_conn)
            except Exception:
                pass
        if pool is not None:
            try:
                await pool.close()
                log.info("asyncpg pool closed")
            except Exception as exc:
                log.warning("pool.close() failed: %s", exc)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="hakudokai cross-PC realtime bridge")
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=5,
        metavar="N",
        help="polling interval in seconds (default: 5)",
    )
    args = parser.parse_args()

    asyncio.run(_run(args.poll_interval))


if __name__ == "__main__":
    main()
