# message_delivery_v3 — 完全ゼロベース再設計書

> 起案: 信長 (織田信長 / shogun)
> 日時: 2026-05-08 20:00 JST
> 命令:
>   - 理事長殿御命令『完全に根本から改善、応急手当てしない』(2026-05-08 19:35)
>   - 理事長殿御命令『とことんやりなさい。中途半端は日に死を招く』(2026-05-08 20:00)
> 対象 cmd: cmd_message_delivery_v3_zerobase_001 (= 新規起案、cmd_inbox_watcher_zerobase_redesign_001 v2 を archive)
> F001 一時 lift 継続: 家臣群停止 + 全 v2 watcher kill 済、信長単独執筆
> 監査依頼先: 家康 (Codex Pro 一次監査) + 本多 (Codex Pro 二次審査) + **黒田官兵衛** (議長監査、理事長殿明示直命 2026-05-08 20:05 で v3 機会に招聘) + Codex 6軸 + Gemini 8観点

## 0. v3 設計思想 — 「Bash 構造的脆弱性の根絶」

v2 (Bash 実装) は本日 1 日で以下の致命的問題を露呈:

| 問題 | 真因 | v3 対応 |
|------|------|--------|
| watcher 4 度 silent death | bash subshell `$$` race + `set -e` early exit | **Python asyncio + 例外境界明示** |
| heartbeat tmp file race | 複数 subshell が同 tmp_path 衝突 | **fcntl.flock + os.replace() (atomic)** |
| zombie watcher hang | inotifywait blocking で disable check 遅延 | **asyncio.timeout + signal handler** |
| ESCALATION /clear 暴発 | bash の if-then-elif 連鎖で副作用見逃し | **state machine 明示 + 全 transition test** |
| supervisor 死活判定不全 | process 生存のみで heartbeat 連動なし | **process AND heartbeat AND watcher.alive=true の and 条件** |
| send-keys 直叩き混在 | bash で grep enforce のみ | **Python wrapper + decorator で構造的 enforce** |
| migration 手動 | bash で逐次 rm + cp の手作業 | **migrate.py 完備 + dry-run + reverse mode** |
| cross-PC dedup 分裂 | local YAML 同期不在 | **Supabase agent_message_dedup table 共有** |
| pane drift 未検知 | bash で都度 tmux display-message | **pane_registry.yaml 動的読込 + 4-way audit class** |

### 4 大原則

1. **言語: Python 3.11+** — type hints + asyncio + dataclasses で型安全 + race 構造的回避
2. **永続化: systemd + cron sentinel** — supervisor 自身の死亡も systemd Restart=always で自動復活、cron で多重監視
3. **観測可能性: structured logging + correlation_id 必須** — 全 critical path で trace 可
4. **fail-safe: 全例外境界明示** — silent failure 禁止、全例外を log + alert

## 1. v2 反省点と v3 対応 mapping

| v2 反省点 | v3 対応箇所 |
|----------|------------|
| a) silent death | systemd unit + cron sentinel + heartbeat staleness 三層検知 |
| b) inotifywait timeout 不整合 | asyncio.streams + inotify_simple、timeout 明示制御 |
| c) send-keys 連発 → Codex interruption | safe_nudge.py の `@with_cooldown` decorator 強制、120s strict |
| d) TUI 空白時の無効 nudge | pane_state machine (NONEMPTY/EMPTY/STALE/UNKNOWN) で書面 mode 自動 fallback |
| e) clear_command 強引 retry | 3-way handshake (= ready_for_clear ack 必須、ack timeout 時は alert + 手動承認) |
| f) post-reset Session Start 衝突 | ready_for_dispatch ack 必須、Session Start 完了確認まで nudge 抑制 |
| g) dedup 不在 | Supabase agent_message_dedup table、TTL 24h、両 PC 共有 |
| h) retry 無限ループ | retry cap 5 + dead_letter table、escalation 必須 |
| i) heartbeat 不在 | queue/watchers/<agent>.health JSON、60s 間隔、staleness 5min 死亡判定 |
| j) lock file stale 残存 | fcntl.flock のみ使用、PID-aware、起動時 stale cleanup |
| k) sleep fallback 混在 | 採用せず、両 OS で inotify_simple/fswatch 必須、不可時は起動 FAIL |
| l) macOS/Linux 分岐 | adapter pattern (FileWatcher abstract class、Linux/macOS subclass) |
| m) cli_adapter drift | pane_registry.yaml の cli フィールドを唯一の真値、pane_current_command との不一致は warn のみ |
| n) pane identity 検証なし | safe_nudge.py の `@with_pane_identity_verify` decorator、全 send-keys で 4-way audit |
| o) dead_letter queue 不在 | queue/dead_letter/<agent>/<msg_id>.yaml、Supabase 連動 |
| p) self-send 即 ack 不在 | watcher.process_message() で from==to 即 ack |
| q) wake-up nudge と書面経路の不整合 | pane_state machine で TUI 状態に応じて自動切替 |
| r) cross-PC bridge 戻り ACK 不在 | Supabase agent_message_events table で両 PC 共有 transition |
| s) 既存修復 commit の積み重ね効果限定 | v3 で全 v2 commit 知見を design_decisions.md に集約 |
| t) inbox symlink 経路 | INBOX_VERSION=v2 (= queue/inbox_v2/<agent>.yaml workspace 内固定) |
| u) bulk_ack/inbox_write/watcher の path SSoT 不在 | scripts/lib_v3/inbox_path.py 共通 module |
| v) Codex Supabase polling fallback 不在 | codex_polling_fallback.py、watcher 死亡時のみ enable、F004 例外条項明記 |
| w) Codex TUI 長文 send-keys 不確定 | safe_nudge.py で長文 → 短縮版 + 詳細 path 提示の自動 2 段階送信 |
| x) ESCALATION 強引 /clear で別 CLI 破壊 | ESCALATION 廃止、ready_for_clear ack 必須、agent 自身の判断尊重 |
| y) zombie watcher hang | watcher AND heartbeat fresh の and 条件、process 生存だけでは "alive" 判定不可 |
| z) bash race condition (本 v3 設計時新発見) | Python の dataclasses + asyncio.Lock で構造的回避 |

## 2. アーキテクチャ

```
┌────────────────────────────────────────────────────────────────────┐
│ message_delivery_v3 (Python)                                      │
│                                                                    │
│  ┌──────────────────┐    ┌─────────────────────────────────┐      │
│  │ systemd unit      │───>│ supervisor.py (asyncio)         │      │
│  │ Restart=always    │    │ - watcher pool 管理              │      │
│  │ + cron sentinel   │    │ - heartbeat staleness 5min      │      │
│  │   (= 多重監視)    │    │ - zombie 検知 (process AND HB)  │      │
│  └──────────────────┘    │ - retry cap 5 + escalation       │      │
│                            │ - drift 検知 → spawn 拒否         │      │
│                            └─────────────────────────────────┘      │
│                                       │                            │
│                                       ▼                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ watcher.py (per agent、asyncio worker)                       │  │
│  │ - inotify_simple で inbox 監視                                │  │
│  │ - 起動時 initial_sweep (=既存 unread 全件処理)               │  │
│  │ - heartbeat 60s 間隔書込                                      │  │
│  │ - process_message: schema/dedup/retry_cap/safe_nudge 連鎖    │  │
│  │ - 自然交代 5400s + graceful exit                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                       │                            │
│                                       ▼                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ safe_nudge.py (decorator wrapper)                            │  │
│  │ @with_global_disable_check                                   │  │
│  │ @with_pane_identity_verify (4-way audit)                     │  │
│  │ @with_cooldown(seconds=120)                                  │  │
│  │ @with_codex_guard (Codex pane のみ)                          │  │
│  │ @with_state_logging                                          │  │
│  │ async def nudge(agent, pane, cli, text, corr_id) -> Result   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ codex_guard.py — Codex pane interruption guard               │  │
│  │ class PaneState(Enum):                                       │  │
│  │   ALLOW / QUEUED / BLOCKED_WORKING / BLOCKED_SANDBOX /       │  │
│  │   PANE_DRIFT / TUI_EMPTY / BASH_SHELL                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ shared lib (scripts/lib_v3/)                                 │  │
│  │ - inbox_path.py (SSoT path 解決)                             │  │
│  │ - pane_registry.py (yaml 動的読込 + drift detect)            │  │
│  │ - logger.py (structured JSON + correlation_id)               │  │
│  │ - dataclasses.py (Message / Watcher / Heartbeat 全定義)      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ data plane                                                   │  │
│  │ - queue/inbox_v2/<agent>.yaml (workspace 内、symlink 排除)   │  │
│  │ - queue/watchers/<agent>.health (JSON、fcntl.flock)          │  │
│  │ - Supabase agent_message_dedup (両 PC 共有、TTL 24h)         │  │
│  │ - Supabase agent_message_events (transition ledger)          │  │
│  │ - queue/dead_letter/<agent>/<msg_id>.yaml + Supabase mirror  │  │
│  │ - queue/session_health/<agent>.yaml (TUI 状態 + ack flags)   │  │
│  │ - queue/control_plane.yaml (manual override + emergency)     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

## 3. コンポーネント仕様

### 3.1 supervisor.py — systemd unit + cron sentinel 配下の永続 manager

```python
# scripts/message_delivery_v3/supervisor.py
import asyncio
from dataclasses import dataclass
from typing import Dict
from lib_v3.pane_registry import PaneRegistry
from lib_v3.logger import logger
from .heartbeat import is_heartbeat_stale, write_heartbeat
from .watcher_pool import WatcherPool

@dataclass
class SupervisorConfig:
    check_interval: int = 30
    heartbeat_threshold: int = 300
    max_restart_count: int = 5
    restart_reset_interval: int = 86400  # 24h
    circuit_breaker_cooldown: int = 1800  # 30min

async def main_loop(config: SupervisorConfig):
    registry = PaneRegistry.load()
    pool = WatcherPool(registry)
    while True:
        if check_disable_flags():
            logger.info("supervisor disabled, graceful exit")
            return  # systemd が Restart=always で再起動
        await write_heartbeat("_supervisor", action="monitoring")
        await pool.audit_and_spawn()
        await asyncio.sleep(config.check_interval)

if __name__ == "__main__":
    asyncio.run(main_loop(SupervisorConfig()))
```

### 3.2 watcher.py — 単一 agent worker

```python
# scripts/message_delivery_v3/watcher.py
import asyncio
import signal
from dataclasses import dataclass
from inotify_simple import INotify, flags
from lib_v3.inbox_path import get_inbox_path
from lib_v3.logger import logger, with_correlation_id
from .heartbeat import HeartbeatLoop
from .message_processor import process_message
from .pane_state import resolve_cli_from_registry

@dataclass
class WatcherConfig:
    agent_id: str
    pane_target: str
    natural_rotation_sec: int = 5400  # 90min

async def main(cfg: WatcherConfig):
    cli = resolve_cli_from_registry(cfg.agent_id)  # registry SSoT、drift detect
    inbox_path = get_inbox_path(cfg.agent_id)

    # heartbeat thread (asyncio task)
    hb = HeartbeatLoop(cfg.agent_id, interval=60)
    hb_task = asyncio.create_task(hb.run())

    # graceful shutdown
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    try:
        # initial sweep (= v2 P1 真因の構造的解決)
        async for msg in scan_unread(inbox_path):
            await process_message(msg, cfg, cli)

        # inotify event-driven loop
        with INotify() as inotify:
            wd = inotify.add_watch(inbox_path, flags.MODIFY | flags.CREATE | flags.MOVED_TO)
            async for events in async_inotify_iter(inotify, stop_event):
                async for msg in scan_unread(inbox_path):
                    await process_message(msg, cfg, cli)

                # natural rotation check
                if hb.uptime_sec() >= cfg.natural_rotation_sec:
                    logger.info("natural rotation")
                    return  # systemd / supervisor が再 spawn
    finally:
        hb_task.cancel()
        await hb.write_final("watcher_exit")
```

### 3.3 safe_nudge.py — decorator stack で構造的 enforce

```python
# scripts/message_delivery_v3/safe_nudge.py
from functools import wraps
import asyncio
from lib_v3.pane_registry import verify_pane_identity
from lib_v3.cooldown import check_cooldown, set_cooldown
from .codex_guard import codex_pre_flight, PaneState

class NudgeResult(Enum):
    DELIVERED = 0
    QUEUED = 1
    BLOCKED = 2
    PANE_DRIFT = 3
    BOOK_MODE = 4
    BASH_SHELL = 5

def with_global_disable_check(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if global_disable_active():
            return NudgeResult.BLOCKED
        return await func(*args, **kwargs)
    return wrapper

def with_pane_identity_verify(func):
    @wraps(func)
    async def wrapper(agent, pane, *args, **kwargs):
        if not verify_pane_identity(agent, pane):
            return NudgeResult.PANE_DRIFT
        return await func(agent, pane, *args, **kwargs)
    return wrapper

def with_cooldown(seconds: int = 120):
    def deco(func):
        @wraps(func)
        async def wrapper(agent, *args, **kwargs):
            if not check_cooldown(agent, seconds):
                return NudgeResult.QUEUED
            result = await func(agent, *args, **kwargs)
            if result == NudgeResult.DELIVERED:
                set_cooldown(agent)
            return result
        return wrapper
    return deco

def with_codex_guard(func):
    @wraps(func)
    async def wrapper(agent, pane, cli, *args, **kwargs):
        if cli == "codex":
            state = await codex_pre_flight(agent, pane)
            if state != PaneState.ALLOW:
                return state.to_nudge_result()
        return await func(agent, pane, cli, *args, **kwargs)
    return wrapper

@with_global_disable_check
@with_pane_identity_verify
@with_cooldown(seconds=120)
@with_codex_guard
async def safe_nudge(agent: str, pane: str, cli: str, text: str, corr_id: str = None) -> NudgeResult:
    # 長文 → 2 段階送信 (= v2 反省点 w 対応)
    if cli == "codex" and len(text) > 100:
        await write_book_mode_entry(agent, text, corr_id)
        return NudgeResult.BOOK_MODE
    # tmux send-keys 実行
    proc = await asyncio.create_subprocess_exec(
        "tmux", "send-keys", "-t", pane, text, "Enter"
    )
    await proc.wait()
    return NudgeResult.DELIVERED if proc.returncode == 0 else NudgeResult.BLOCKED
```

### 3.4 codex_guard.py — Pane state machine

```python
# scripts/message_delivery_v3/codex_guard.py
from enum import Enum
import asyncio
import re

class PaneState(Enum):
    ALLOW = 0
    BLOCKED_WORKING = 1
    BLOCKED_SANDBOX_PROMPT = 2
    PANE_DRIFT = 3
    TUI_EMPTY = 4
    BASH_SHELL = 5

    def to_nudge_result(self) -> "NudgeResult":
        # mapping
        pass

WORKING_PATTERN = re.compile(r'• Working \(\d+[smh]')
SANDBOX_PATTERN = re.compile(r'Yes, proceed|Press enter to confirm|tell Codex what to do differently')
BASH_PROMPT_PATTERN = re.compile(r'^\S+@\S+:.*\$\s*$', re.MULTILINE)

async def codex_pre_flight(agent: str, pane: str) -> PaneState:
    proc = await asyncio.create_subprocess_exec(
        "tmux", "capture-pane", "-t", pane, "-p",
        stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    capture = stdout.decode("utf-8", errors="replace")
    tail = "\n".join(capture.split("\n")[-20:])

    # 各 state 検出 (順序重要、特殊 → 一般)
    non_empty_lines = sum(1 for line in capture.split("\n") if line.strip())
    if non_empty_lines < 2:
        return PaneState.TUI_EMPTY
    if BASH_PROMPT_PATTERN.search(tail):
        return PaneState.BASH_SHELL
    if SANDBOX_PATTERN.search(tail):
        return PaneState.BLOCKED_SANDBOX_PROMPT
    if WORKING_PATTERN.search(tail):
        return PaneState.BLOCKED_WORKING

    return PaneState.ALLOW
```

### 3.5 heartbeat.py — fcntl.flock + atomic write

```python
# scripts/message_delivery_v3/heartbeat.py
import asyncio
import fcntl
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class HeartbeatRecord:
    schema_version: str = "v3.0"
    agent_id: str = ""
    watcher_pid: int = 0
    version: str = "v3.0.0"
    alive: bool = True
    started_at: str = ""
    uptime_sec: int = 0
    last_action: str = "idle"
    last_seen_at: str = ""
    tui_capture_state: str = "unknown"
    ready_for_clear: bool = True
    ready_for_dispatch: bool = True
    restart_count_24h: int = 0

async def write_heartbeat(agent_id: str, action: str = "idle") -> bool:
    """fcntl.flock + os.replace で atomic、race 構造的回避"""
    record = HeartbeatRecord(
        agent_id=agent_id,
        watcher_pid=os.getpid(),
        last_action=action,
        last_seen_at=current_iso(),
        # ... other fields
    )
    health_path = Path(get_health_path(agent_id))
    tmp_path = health_path.with_suffix(f".tmp.{os.getpid()}.{os.urandom(8).hex()}")

    try:
        with open(tmp_path, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(asdict(record), f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, health_path)  # atomic
        return True
    except Exception as e:
        logger.error(f"heartbeat write failed: {e}", agent=agent_id)
        return False
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

def is_zombie(agent_id: str) -> bool:
    """process 生存 AND heartbeat fresh の and 条件で zombie 判定 (= v2 反省点 y)"""
    pid_alive = process_alive(get_watcher_pid(agent_id))
    hb_fresh = not is_heartbeat_stale(agent_id, threshold=300)
    return pid_alive and not hb_fresh  # 生きてるが heartbeat 古い = zombie
```

### 3.6 lib_v3/pane_registry.py — pane_registry.yaml SSoT 動的読込

```python
# scripts/lib_v3/pane_registry.py
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class PaneEntry:
    agent_id: str
    persona: str
    cli: str
    pc: str
    tmux_target: str
    role: str
    status: str

class PaneRegistry:
    def __init__(self):
        self._entries: Dict[str, PaneEntry] = {}
        self._tmux_to_agent: Dict[str, str] = {}

    @classmethod
    def load(cls, path: Path = Path("queue/pane_registry.yaml")) -> "PaneRegistry":
        with open(path) as f:
            data = yaml.safe_load(f)
        instance = cls()
        for entry in data.get("pane_registry", {}).get("panes", []):
            pe = PaneEntry(**entry)
            instance._entries[pe.agent_id] = pe
            instance._tmux_to_agent[pe.tmux_target] = pe.agent_id
        return instance

    def resolve_cli(self, agent_id: str) -> Optional[str]:
        entry = self._entries.get(agent_id)
        return entry.cli if entry else None

    def verify_pane_identity(self, agent_id: str, tmux_target: str) -> bool:
        """4-way audit (= tmux env + registry + shell mirror + python mirror)"""
        # tmux env @agent_id
        actual = subprocess.run(
            ["tmux", "display-message", "-t", tmux_target, "-p", "#{@agent_id}"],
            capture_output=True, text=True
        ).stdout.strip()
        expected = self._tmux_to_agent.get(tmux_target)
        if actual != agent_id or actual != expected:
            logger.error("pane_drift", expected=agent_id, actual=actual, tmux_target=tmux_target)
            return False
        return True
```

## 4. データ構造

### 4.1 inbox message schema (= v2 と同形、Supabase に mirror)

```yaml
messages:
  - id: msg_20260508_200300_a1b2c3d4
    timestamp: "2026-05-08T20:03:00+09:00"
    correlation_id: 01HZ5...  # UUIDv7
    from: shogun
    to: hideyoshi
    type: cmd_new
    content: "..."
    delivery_state: pending
    read: false
    schema_version: "3.0"
```

### 4.2 Supabase agent_message_dedup table

```sql
CREATE TABLE agent_message_dedup (
    msg_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '24 hours',
    ack_by TEXT NOT NULL,
    pc_origin TEXT NOT NULL CHECK (pc_origin IN ('MainPC', 'SecondPC'))
);
CREATE INDEX idx_dedup_expires ON agent_message_dedup(expires_at);
```

### 4.3 Supabase agent_message_events (= 蓬蓮草 v2 ledger 統合)

```sql
CREATE TABLE agent_message_events (
    event_id BIGSERIAL PRIMARY KEY,
    msg_id TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    delivery_state TEXT NOT NULL CHECK (delivery_state IN
        ('pending','delivered','read','acted','reported','audited','closed','dead_letter')),
    transitioned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pc_origin TEXT NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_events_msg_id ON agent_message_events(msg_id);
CREATE INDEX idx_events_corr_id ON agent_message_events(correlation_id);
```

## 5. 移行計画 — Stage A 〜 G + Rollback

| Stage | 内容 | 検証 | rollback |
|-------|------|------|---------|
| A | v3 単独起動、v2 並走、shadow read 24h | 配達一致率 99.9% | v3 停止、v2 単独 |
| B | dual-write (v2→v3 mirror、digest 確認) | 24h、msg loss 0 | 旧 v2 真値復元 |
| C | write freeze on v2 | hook で v2 reject 検証 | freeze 解除 |
| D | canonical switch to v3 | 全 agent 1h v3 動作 | migrate.py reverse |
| E | archive v2 (= scripts/archive/v2_full/) | rollback path 確保 | archive から復元 |
| F | SecondPC sync | cross-PC delivery 99.9% | bridge 旧経路維持 |
| G | docs + AGENTS.md update | grep で v2 path 残存 0 | revert |

## 6. observability

- 全 module が `lib_v3/logger.py` 経由で structured JSON 出力
- correlation_id 必須付与
- `logs/message_delivery_v3/<component>_<date>.log`
- Supabase `agent_message_events` で transition trace
- dashboard.md に health summary 統合

## 7. 自動復旧 SH パターン

| パターン | v3 実装 |
|---------|---------|
| SH1 Circuit Breaker | supervisor.py の watcher restart cap=5 + cooldown 30min |
| SH2 Exponential Backoff | retry 1s → 2s → 4s → 8s → 16s |
| SH3 Fallback | TUI 空白時 → book_mode (Supabase fallback) |
| SH4 Stale Lock | fcntl.flock + 起動時 cleanup |
| SH6 Self-Restart | systemd Restart=always + cron sentinel + manual disable flag 尊重 |
| SH8 Idempotent Retry | Supabase agent_message_dedup |

危険 D1-D6 全件不適用 (= 該当なし)。

## 8. テスト計画

### 8.1 unit (pytest)
- `tests_v3/unit/test_safe_nudge.py` (decorator stack の各層検証)
- `tests_v3/unit/test_codex_guard.py` (PaneState 全 7 状態)
- `tests_v3/unit/test_heartbeat.py` (fcntl + atomic write、race fixture)
- `tests_v3/unit/test_pane_registry.py` (4-way audit、drift fixture)
- `tests_v3/unit/test_dedup.py` (Supabase mock + TTL)
- `tests_v3/unit/test_dead_letter.py` (escalation flow)

### 8.2 integration (pytest + bats)
- `tests_v3/integration/test_supervisor_lifecycle.py` (spawn/kill/respawn)
- `tests_v3/integration/test_watcher_natural_rotation.py` (5400s)
- `tests_v3/integration/test_e2e_delivery.py` (inbox_write → watcher → safe_nudge)
- `tests_v3/integration/test_codex_pane_handling.py` (sandbox prompt / Working / book_mode)
- `tests_v3/integration/test_zombie_detection.py` (process 生存 + heartbeat 古い → zombie 判定)

### 8.3 shadow mode (Phase 3)
- 24h v2 + v3 並走、配達一致率 99.9%

### 8.4 PDCA
- max 5 cycle、家康 6軸 + 信長 self + 本多 governance + Codex self + Gemini 8観点

## 9. 期限管理 — 時間制約なし

| Phase | 内容 | 担当 |
|-------|------|------|
| Phase 0'' | 反省点全件再洗い直し (a〜z) | 信長 + 家康監査 + 本多 governance |
| Phase 1'' | 本書 (v3 設計書) | 信長執筆、三者監査 |
| Phase 2'' | Python prototype + pytest | 信長 + 家康/本多/Gemini 監査 |
| Phase 3'' | shadow mode 24h | 全員観察 |
| Phase 4'' | cutover (= v2 archive) | 信長 + 家康監査 |
| Phase 5'' | retrospective + 安定化 | 本多 + 家康 |

各 Phase 三者監査 PASS まで次へ進まず、PDCA cap 5。

## 10. 残 risk + 既知制約

| ID | risk | 対応 |
|----|------|------|
| R-aa | Python asyncio の error swallowing | except ブロック明示 + 再 raise |
| R-ab | inotify_simple の Linux 依存 | adapter pattern で macOS fswatch |
| R-ac | Supabase ratelimit | local cache + retry backoff |
| R-ad | systemd 依存 | rootless systemd or upstart fallback |
| R-ae | Python venv の deploy 同期 | requirements.txt + bootstrap script |

## 11. v2 との関係

- v2 (Bash) は本 cmd 完遂時 archive (= scripts/archive/message_delivery_v2_full_20260508/)
- v2 で蓄積した 24/24 bats PASS の知見は v3 pytest fixture に転写
- v2 commit 履歴 (6abe359 → 9ee927a → bd99604 → e661fec → 24a53ef → 4a70d88 → 7b144ca → f7b78a0 → 2e6a11b) を design_decisions.md に保存

## 12. 信長最終進言

上様、v2 (Bash) は短時間で動かす目的では機能したが、構造的脆弱性 (subshell race / set -e fragility / inotify blocking で disable 遅延 / process 生存だけの死活判定) が本日露呈。

v3 (Python asyncio + systemd + Supabase 共有) で根絶する。応急処置でなく、原理から作り直す。

時間制約なし、慎重に三者監査を経て進める。御裁可なれば cmd_message_delivery_v3_zerobase_001 として正式起案、Phase 0'' から開始する所存。

---

*信長 (織田信長) 2026-05-08 20:00 JST、v3 ゼロベース設計書執筆完遂、家康/本多 三者監査依頼予定*
