#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# inbox_watcher.sh — メールボックス監視＆起動シグナル配信
# Usage: bash scripts/inbox_watcher.sh <agent_id> <pane_target> [cli_type]
# Example: bash scripts/inbox_watcher.sh karo multiagent:0.0 claude
#
# 設計思想:
#   メッセージ本体はファイル（inbox YAML）に書く = 確実
#   起動シグナルは tmux send-keys（テキストとEnterを分離送信）
#   エージェントが自分でinboxをReadして処理する
#   冪等: 2回届いてもunreadがなければ何もしない
#
# inotifywait でファイル変更を検知（イベント駆動、ポーリングではない）
# Fallback 1: 30秒タイムアウト（WSL2 inotify不発時の安全網）
# Fallback 2: rc=1処理（Claude Code atomic write = tmp+rename でinode変更時）
#
# エスカレーション（未読メッセージが放置されている場合）:
#   0〜2分: 通常nudge（send-keys）。ただしWorking中はスキップ
#   2〜4分: Escape×2 + nudge（カーソル位置バグ対策）
#   4分〜 : /clear送信（5分に1回まで。強制リセット+YAML再読）
# ═══════════════════════════════════════════════════════════════

# ─── Testing guard ───
# When __INBOX_WATCHER_TESTING__=1, only function definitions are loaded.
# Argument parsing, inotifywait check, and main loop are skipped.
# Test code sets variables (AGENT_ID, PANE_TARGET, CLI_TYPE, INBOX) externally.
if [ "${__INBOX_WATCHER_TESTING__:-}" != "1" ]; then
    set -euo pipefail

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    AGENT_ID="$1"
    PANE_TARGET="$2"
    CLI_TYPE="${3:-claude}"  # CLI種別（claude/codex/copilot）。未指定→claude（後方互換）

    INBOX="$SCRIPT_DIR/queue/inbox/${AGENT_ID}.yaml"
    LOCKFILE="${INBOX}.lock"

    if [ -z "$AGENT_ID" ] || [ -z "$PANE_TARGET" ]; then
        echo "Usage: inbox_watcher.sh <agent_id> <pane_target> [cli_type]" >&2
        exit 1
    fi

    # Initialize inbox if not exists
    if [ ! -f "$INBOX" ]; then
        mkdir -p "$(dirname "$INBOX")"
        echo "messages: []" > "$INBOX"
    fi

    echo "[$(date)] inbox_watcher started — agent: $AGENT_ID, pane: $PANE_TARGET, cli: $CLI_TYPE" >&2

    # Fix 2026-05-07: 起動時に typing skip counter をクリアする
    # (= 旧プロセスが skip 5/5 で終了 → 新プロセスが起動瞬間に「skip cap reached」で
    # FORCE nudge 発動するバグの根本対策。プロセス間の counter 引き継ぎを断つ)
    rm -f "/tmp/inbox_watcher_typing_skip_${AGENT_ID}" 2>/dev/null

    # Fix: CLI starts at welcome screen = idle. Create idle flag so watcher
    # doesn't false-busy deadlock waiting for a stop_hook that never fires.
    if [[ "$CLI_TYPE" == "claude" ]]; then
        touch "${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}"
        echo "[$(date)] Created initial idle flag for $AGENT_ID (CLI starts idle)" >&2
    fi

    # Source cli_adapter for get_startup_prompt() (Codex needs startup prompt after /new)
    _cli_adapter="${SCRIPT_DIR}/lib/cli_adapter.sh"
    if [ -f "$_cli_adapter" ]; then
        source "$_cli_adapter"
        echo "[$(date)] cli_adapter.sh loaded (get_startup_prompt available)" >&2
    fi

    # Source shared agent status library (busy/idle detection)
    _agent_status_lib="${SCRIPT_DIR}/lib/agent_status.sh"
    if [ -f "$_agent_status_lib" ]; then
        source "$_agent_status_lib"
    fi

    # Detect OS and select file-watching backend
    INBOX_WATCHER_OS="$(uname -s)"
    if [ "$INBOX_WATCHER_OS" = "Darwin" ]; then
        # macOS: use fswatch instead of inotifywait
        if ! command -v fswatch &>/dev/null; then
            echo "[inbox_watcher] ERROR: fswatch not found. Install: brew install fswatch" >&2
            exit 1
        fi
        WATCH_BACKEND="fswatch"
        if ! command -v gtimeout &>/dev/null; then
            echo "[inbox_watcher] WARN: gtimeout not found. Using sleep-based fallback (higher CPU). Recommended: brew install coreutils" >&2
        fi
    else
        # Linux: use inotifywait
        if ! command -v inotifywait &>/dev/null; then
            echo "[inbox_watcher] ERROR: inotifywait not found. Install: sudo apt install inotify-tools" >&2
            exit 1
        fi
        WATCH_BACKEND="inotifywait"
    fi
    echo "[$(date)] File watch backend: $WATCH_BACKEND" >&2
fi

# ─── timeout command compatibility wrapper (macOS support) ───
if ! command -v timeout &>/dev/null; then
  if command -v gtimeout &>/dev/null; then
    timeout() { gtimeout "$@"; }
  else
    # Pure bash fallback: timeout DURATION COMMAND [ARGS...]
    timeout() {
      local duration="$1"; shift
      "$@" &
      local pid=$!
      ( sleep "$duration" && kill "$pid" 2>/dev/null ) &
      local watcher=$!
      wait "$pid" 2>/dev/null
      local rc=$?
      kill "$watcher" 2>/dev/null
      wait "$watcher" 2>/dev/null
      return $rc
    }
  fi
fi

# ─── Escalation state ───
# Time-based escalation: track how long unread messages have been waiting
FIRST_UNREAD_SEEN=${FIRST_UNREAD_SEEN:-0}
LAST_CLEAR_TS=${LAST_CLEAR_TS:-0}
ESCALATE_PHASE1=${ESCALATE_PHASE1:-120}
ESCALATE_PHASE2=${ESCALATE_PHASE2:-240}
ESCALATE_COOLDOWN=${ESCALATE_COOLDOWN:-300}

# ─── Nudge throttle ───
# Avoid spamming the same "inboxN" into the pane every timeout tick.
LAST_NUDGE_TS=${LAST_NUDGE_TS:-0}
LAST_NUDGE_COUNT=${LAST_NUDGE_COUNT:-""}
NUDGE_COOLDOWN_SEC=${NUDGE_COOLDOWN_SEC:-60}
# Codex は「思考中に入力が入ると即拾う」挙動があり、思考がループすることがあるため長めにする。
NUDGE_COOLDOWN_SEC_CODEX=${NUDGE_COOLDOWN_SEC_CODEX:-300}
NUDGE_FINGERPRINT_FILE=${NUDGE_FINGERPRINT_FILE:-/tmp/inbox_watcher_nudge_fingerprint_${AGENT_ID:-unknown}}

# ─── Context reset tracking ───
# Tracks whether we've sent /new or /clear for the current task_assigned batch.
# Resets to 0 when all messages are read (FIRST_UNREAD_SEEN → 0).
NEW_CONTEXT_SENT=${NEW_CONTEXT_SENT:-0}
# Tracks whether we sent a startup prompt (Codex) that includes full recovery.
# When set, skip follow-up nudge for this cycle (agent already knows what to do).
STARTUP_PROMPT_SENT=${STARTUP_PROMPT_SENT:-0}

# ─── Phase feature flags (cmd_107 Phase 1/2/3) ───
# ASW_PHASE:
#   1 = self-watch base (compatible)
#   2 = disable normal nudge by default
#   3 = FINAL_ESCALATION_ONLY (send-keys is fallback only)
ASW_PHASE=${ASW_PHASE:-2}
ASW_DISABLE_NORMAL_NUDGE=${ASW_DISABLE_NORMAL_NUDGE:-$([ "${ASW_PHASE}" -ge 2 ] && echo 1 || echo 0)}
ASW_FINAL_ESCALATION_ONLY=${ASW_FINAL_ESCALATION_ONLY:-$([ "${ASW_PHASE}" -ge 3 ] && echo 1 || echo 0)}
FINAL_ESCALATION_ONLY=${FINAL_ESCALATION_ONLY:-$ASW_FINAL_ESCALATION_ONLY}
ASW_NO_IDLE_FULL_READ=${ASW_NO_IDLE_FULL_READ:-1}
# Optional safety toggles:
# - ASW_DISABLE_ESCALATION=1: disable phase2/phase3 escalation actions
# - ASW_PROCESS_TIMEOUT=0: do not process unread on timeout ticks (event-only)
ASW_DISABLE_ESCALATION=${ASW_DISABLE_ESCALATION:-0}
ASW_PROCESS_TIMEOUT=${ASW_PROCESS_TIMEOUT:-1}

# ─── Metrics hooks (FR-006 / NFR-003) ───
# unread_latency_sec / read_count / estimated_tokens are intentionally explicit
READ_COUNT=${READ_COUNT:-0}
READ_BYTES_TOTAL=${READ_BYTES_TOTAL:-0}
ESTIMATED_TOKENS_TOTAL=${ESTIMATED_TOKENS_TOTAL:-0}
METRICS_FILE=${METRICS_FILE:-${SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}/queue/metrics/${AGENT_ID:-unknown}_selfwatch.yaml}

update_metrics() {
    local bytes_read="${1:-0}"
    local now
    now=$(date +%s)

    READ_COUNT=$((READ_COUNT + 1))
    READ_BYTES_TOTAL=$((READ_BYTES_TOTAL + bytes_read))
    ESTIMATED_TOKENS_TOTAL=$((ESTIMATED_TOKENS_TOTAL + ((bytes_read + 3) / 4)))

    local unread_latency_sec=0
    if [ "$FIRST_UNREAD_SEEN" -gt 0 ] 2>/dev/null; then
        unread_latency_sec=$((now - FIRST_UNREAD_SEEN))
    fi

    mkdir -p "$(dirname "$METRICS_FILE")" 2>/dev/null || true
    cat > "$METRICS_FILE" <<EOF
agent_id: "${AGENT_ID:-unknown}"
timestamp: "$(date '+%Y-%m-%dT%H:%M:%S%z')"
unread_latency_sec: $unread_latency_sec
read_count: $READ_COUNT
bytes_read: $READ_BYTES_TOTAL
estimated_tokens: $ESTIMATED_TOKENS_TOTAL
EOF
}

disable_normal_nudge() {
    # Phase 2+: suppress nudge ONLY when agent is busy.
    # If agent is idle, nudge is needed (stop hook won't fire for idle agents).
    if [ "${ASW_DISABLE_NORMAL_NUDGE:-0}" != "1" ]; then
        return 1  # Phase 1: never suppress
    fi
    # Phase 2+: check if agent is idle via flag file
    if [ -f "${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}" ]; then
        return 1  # Agent is IDLE → don't suppress, send nudge
    fi
    return 0  # Agent is BUSY → suppress, stop hook will deliver
}

should_throttle_nudge() {
    local unread_count="${1:-0}"
    local now
    now=$(date +%s)

    local effective_cli
    effective_cli=$(get_effective_cli_type)

    # Once a Claude nudge has been submitted for an unchanged inbox, do not
    # submit it again merely because a time-based cooldown elapsed. API 503
    # retries can leave Claude idle-looking while the same user message is
    # already queued. Persist the inbox fingerprint across watcher restarts;
    # any read/new-message mutation changes the SHA and permits a fresh nudge.
    if [[ "$effective_cli" == "claude" ]] && [ -f "$INBOX" ]; then
        local current_sha current_fingerprint previous_fingerprint
        current_sha=$(sha256sum "$INBOX" 2>/dev/null | awk '{print $1}')
        current_fingerprint="${unread_count}|${current_sha}"
        previous_fingerprint=$(cat "$NUDGE_FINGERPRINT_FILE" 2>/dev/null || true)
        if [ -n "$current_sha" ] && [ "$previous_fingerprint" = "$current_fingerprint" ]; then
            echo "[$(date)] [SKIP] Unchanged inbox nudge already submitted for $AGENT_ID: inbox${unread_count}" >&2
            return 0
        fi
    fi

    local cooldown_sec="${NUDGE_COOLDOWN_SEC:-60}"
    if [[ "$effective_cli" == "codex" ]]; then
        cooldown_sec="${NUDGE_COOLDOWN_SEC_CODEX:-300}"
    elif [[ "$effective_cli" == "claude" ]]; then
        # Claude Code: same cooldown as default (60s).
        # Stop hook is supplementary, not primary — nudge immediately.
        cooldown_sec="${NUDGE_COOLDOWN_SEC_CLAUDE:-60}"
    fi

    # Standard throttle: skip if same count within cooldown window.
    if [ "${LAST_NUDGE_COUNT:-}" = "$unread_count" ] && [ "${LAST_NUDGE_TS:-0}" -gt 0 ]; then
        local age=$((now - LAST_NUDGE_TS))
        if [ "$age" -lt "${cooldown_sec}" ]; then
            echo "[$(date)] [SKIP] Throttling nudge for $AGENT_ID: inbox${unread_count} (${age}s < ${cooldown_sec}s, cli=$effective_cli)" >&2
            return 0
        fi
    fi

    LAST_NUDGE_COUNT="$unread_count"
    LAST_NUDGE_TS="$now"
    return 1
}

record_nudge_fingerprint() {
    local unread_count="${1:-0}"
    [ -f "$INBOX" ] || return 0
    local current_sha
    current_sha=$(sha256sum "$INBOX" 2>/dev/null | awk '{print $1}')
    [ -n "$current_sha" ] || return 0
    ( umask 077; printf '%s\n' "${unread_count}|${current_sha}" > "$NUDGE_FINGERPRINT_FILE" )
}

is_valid_cli_type() {
    case "${1:-}" in
        claude|codex|copilot|kimi) return 0 ;;
        *) return 1 ;;
    esac
}

get_effective_cli_type() {
    local pane_cli_raw=""
    local pane_cli=""

    pane_cli_raw=$(timeout 2 tmux show-options -p -t "$PANE_TARGET" -v @agent_cli 2>/dev/null || true)
    pane_cli=$(echo "$pane_cli_raw" | tr -d '\r' | head -n1 | tr -d '[:space:]')

    if is_valid_cli_type "$pane_cli"; then
        if is_valid_cli_type "${CLI_TYPE:-}" && [ "$pane_cli" != "${CLI_TYPE}" ]; then
            echo "[$(date)] [WARN] CLI drift detected for $AGENT_ID: arg=${CLI_TYPE}, pane=${pane_cli}. Using pane value." >&2
        fi
        echo "$pane_cli"
        return 0
    fi

    if is_valid_cli_type "${CLI_TYPE:-}"; then
        if [ -n "$pane_cli" ]; then
            echo "[$(date)] [WARN] Invalid pane @agent_cli for $AGENT_ID: '${pane_cli}'. Falling back to arg=${CLI_TYPE}." >&2
        fi
        echo "${CLI_TYPE}"
        return 0
    fi

    # Fail-closed: when CLI is unknown, take codex-safe path (no C-c, /clear->/new)
    echo "[$(date)] [WARN] CLI unresolved for $AGENT_ID (pane='${pane_cli:-<empty>}', arg='${CLI_TYPE:-<empty>}'). Fallback=codex-safe." >&2
    echo "codex"
}

normalize_special_command() {
    local msg_type="${1:-}"
    local raw_content="${2:-}"

    case "$msg_type" in
        clear_command)
            echo "/clear"
            ;;
        model_switch)
            if [[ "$raw_content" =~ ^/model[[:space:]]+[^[:space:]].* ]]; then
                echo "$raw_content"
            else
                echo "[$(date)] [SKIP] Invalid model_switch payload for $AGENT_ID: ${raw_content:-<empty>}" >&2
            fi
            ;;
        cli_restart)
            # cli_restart is handled externally by switch_cli.sh, not via send_cli_command.
            # Emit a marker so the main loop can call switch_cli.sh.
            echo "__CLI_RESTART__:${raw_content}"
            ;;
    esac
}

enqueue_recovery_task_assigned() {
    (
        if command -v flock &>/dev/null; then flock -x 200; else _ld="${LOCKFILE}.d"; _i=0; while ! mkdir "$_ld" 2>/dev/null; do sleep 0.1; _i=$((_i+1)); [ $_i -ge 300 ] && break; done; trap "rmdir '$_ld' 2>/dev/null" EXIT; fi
        INBOX_PATH="$INBOX" AGENT_ID="$AGENT_ID" "$SCRIPT_DIR/.venv/bin/python3" - << 'PY'
import datetime
import os
import uuid
import yaml

inbox = os.environ.get("INBOX_PATH", "")
agent_id = os.environ.get("AGENT_ID", "agent")

try:
    with open(inbox, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    messages = data.get("messages", []) or []

    # Dedup guard: keep only one pending auto-recovery hint at a time.
    for m in reversed(messages):
        if (
            m.get("from") == "inbox_watcher"
            and m.get("type") == "task_assigned"
            and m.get("read", False) is False
            and "[auto-recovery]" in (m.get("content") or "")
        ):
            print("SKIP_DUPLICATE")
            raise SystemExit(0)

    # Task YAML status guard: skip auto-recovery if task is cancelled or idle.
    # This prevents restarting a task that 家老 intentionally cancelled via clear_command.
    task_yaml_path = os.path.join(
        os.path.dirname(os.path.dirname(inbox)), "tasks", f"{agent_id}.yaml"
    )
    if os.path.exists(task_yaml_path):
        try:
            with open(task_yaml_path, "r", encoding="utf-8") as tf:
                task_data = yaml.safe_load(tf) or {}
            task_status = str(task_data.get("status") or "").strip().strip("'\"")
            if task_status in ("cancelled", "idle"):
                print(f"SKIP_CANCELLED:{task_status}")
                raise SystemExit(0)
        except SystemExit:
            raise
        except Exception:
            pass  # If task YAML is unreadable, proceed with auto-recovery as safety net

    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    msg = {
        "content": (
            f"[auto-recovery] /clear 後の再着手通知。"
            f"queue/tasks/{agent_id}.yaml を再読し、assigned タスクを即時再開せよ。"
        ),
        "from": "inbox_watcher",
        "id": f"msg_auto_recovery_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "read": False,
        "timestamp": now.replace(microsecond=0).isoformat(),
        "type": "task_assigned",
    }
    messages.append(msg)
    data["messages"] = messages

    # symlink保護: realpath経由で canonical 解決後に atomic replace
    # (2026-05-08 split-brain 事故対策、commit dd706ad と同型 fix)
    inbox_canonical = os.path.realpath(inbox)
    tmp_path = f"{inbox_canonical}.tmp.{os.getpid()}"
    with open(tmp_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
    os.replace(tmp_path, inbox_canonical)
    print(msg["id"])
except Exception:
    # Best-effort safety net only. Primary /clear delivery must not fail here.
    print("ERROR")
PY
    ) 200>"$LOCKFILE" 2>/dev/null
}

no_idle_full_read() {
    local trigger="${1:-timeout}"
    [ "${ASW_NO_IDLE_FULL_READ:-1}" = "1" ] || return 1
    [ "$trigger" = "timeout" ] || return 1
    [ "${FIRST_UNREAD_SEEN:-0}" -eq 0 ] || return 1
    return 0
}

# summary-first: unread_count fast-path before full read
# expiry/supersession-aware (read-only — no lock, no write; mirrors the
# mutation predicate in get_unread_info() so the fast path never reports a
# false-positive count for stale notices that get_unread_info would exclude).
get_unread_count_fast() {
    INBOX_PATH="$INBOX" "$SCRIPT_DIR/.venv/bin/python3" - << 'PY'
import datetime
import json
import os
import yaml

inbox = os.environ.get("INBOX_PATH", "")
try:
    with open(inbox, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    messages = data.get("messages", []) or []
    now_iso = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat()
    by_id = {m.get("id"): m for m in messages if m.get("id")}
    superseded_ids = {m.get("supersedes") for m in messages if m.get("supersedes") in by_id}

    def _effectively_unread(m):
        if m.get("read", False):
            return False
        if m.get("id") in superseded_ids:
            return False
        expires_at = m.get("expires_at")
        if expires_at and now_iso >= expires_at:
            return False
        return True

    unread_count = sum(1 for m in messages if _effectively_unread(m))
    print(json.dumps({"count": unread_count}))
except Exception:
    print(json.dumps({"count": 0}))
PY
}

# ─── Extract unread message info (lock-free read) ───
# Returns JSON lines: {"count": N, "has_special": true/false, "specials": [...]}
# Test anchor for bats awk pattern: get_unread_info\\(\\)
get_unread_info() {
    (
        if command -v flock &>/dev/null; then flock -x 200; else _ld="${LOCKFILE}.d"; _i=0; while ! mkdir "$_ld" 2>/dev/null; do sleep 0.1; _i=$((_i+1)); [ $_i -ge 300 ] && break; done; trap "rmdir '$_ld' 2>/dev/null" EXIT; fi
        INBOX_PATH="$INBOX" "$SCRIPT_DIR/.venv/bin/python3" - << 'PY'
import datetime
import json
import os
import yaml

inbox = os.environ.get("INBOX_PATH", "")
try:
    with open(inbox, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    messages = data.get("messages", []) or []

    # Auto-expire/auto-supersede (backward compatible: messages without
    # expires_at/supersedes are unaffected). Expired or superseded messages
    # are flipped to read=true HERE, before unread/specials/normal_count are
    # computed, so they are transparently excluded from unread count, nudge,
    # Escape, /clear, FIRST_UNREAD_SEEN timer reset, and stop-hook's
    # `read: false` grep — with zero changes needed to the Phase-3 escalation
    # branches themselves. expires_at uses the same "%Y-%m-%dT%H:%M:%S"
    # format as inbox_write.sh's TIMESTAMP, compared lexicographically.
    now_iso = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat()
    by_id = {m.get("id"): m for m in messages if m.get("id")}
    superseded_ids = {m.get("supersedes") for m in messages if m.get("supersedes") in by_id}
    expire_supersede_changed = False
    for m in messages:
        if m.get("read", False):
            continue
        is_superseded = m.get("id") in superseded_ids
        expires_at = m.get("expires_at")
        is_expired = bool(expires_at) and now_iso >= expires_at
        if is_superseded or is_expired:
            m["read"] = True
            expire_supersede_changed = True

    unread = [m for m in messages if not m.get("read", False)]
    special_types = ("clear_command", "model_switch", "cli_restart")
    specials = [m for m in unread if m.get("type") in special_types]

    # W201 root-cause cure: specials are intentionally NOT marked read=True
    # here (consume-before-commit removed). Marking at extraction time meant
    # a busy-guard-deferred clear_command was already committed read=True in
    # the file before the caller ever attempted to send it — the log said
    # "deferred to next cycle" but the next cycle's `unread` filter above
    # skips read=True messages forever, so the command was silently lost.
    # Specials are now marked read only after the caller (process_unread)
    # confirms actual successful execution, via mark_message_processed().
    if expire_supersede_changed:
        # symlink保護: realpath経由で canonical 解決後に atomic replace
        # (2026-05-08 split-brain 事故対策、commit dd706ad と同型 fix)
        inbox_canonical = os.path.realpath(inbox)
        tmp_path = f"{inbox_canonical}.tmp.{os.getpid()}"
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        os.replace(tmp_path, inbox_canonical)

    normal_count = len(unread) - len(specials)
    normal_msgs = [m for m in unread if m.get("type") not in special_types]
    has_task_assigned = any(m.get("type") == "task_assigned" for m in normal_msgs)
    payload = {
        "count": normal_count,
        "has_task_assigned": has_task_assigned,
        "specials": [{"id": m.get("id", ""), "from": m.get("from", ""), "type": m.get("type", ""), "content": m.get("content", "")} for m in specials],
    }
    print(json.dumps(payload))
except Exception:
    print(json.dumps({"count": 0, "specials": []}))
PY
    ) 200>"$LOCKFILE" 2>/dev/null
}

# ─── Mark a single special message read (post-execution commit only) ───
# W201 root-cause cure (発注①): read=True for a special (clear_command/
# model_switch/cli_restart) must be committed ONLY after the caller has
# confirmed it was actually executed. Never call this speculatively.
# Locked + scoped to one message id (by id, not a blanket sweep) so a
# concurrent inbox_write.sh append from another agent is never clobbered.
mark_message_processed() {
    local msg_id="$1"
    [ -n "$msg_id" ] || return 0
    (
        if command -v flock &>/dev/null; then flock -x 200; else _ld="${LOCKFILE}.d"; _i=0; while ! mkdir "$_ld" 2>/dev/null; do sleep 0.1; _i=$((_i+1)); [ $_i -ge 300 ] && break; done; trap "rmdir '$_ld' 2>/dev/null" EXIT; fi
        INBOX_PATH="$INBOX" MSG_ID="$msg_id" "$SCRIPT_DIR/.venv/bin/python3" - << 'PY'
import os
import yaml

inbox = os.environ.get("INBOX_PATH", "")
msg_id = os.environ.get("MSG_ID", "")
try:
    with open(inbox, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    messages = data.get("messages", []) or []
    changed = False
    for m in messages:
        if m.get("id") == msg_id and not m.get("read", False):
            m["read"] = True
            changed = True
            break
    if changed:
        inbox_canonical = os.path.realpath(inbox)
        tmp_path = f"{inbox_canonical}.tmp.{os.getpid()}"
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        os.replace(tmp_path, inbox_canonical)
except Exception:
    pass
PY
    ) 200>"$LOCKFILE" 2>/dev/null
}

# ─── Return an undeliverable special message to its sender ───
# W201 root-cause cure (発注③・W201追補②B-4 Return-Path): a special command
# that could not be executed (unrecognized type/content, or send_cli_command
# failure) must not vanish silently. It is consumed here (read=True — so it
# is not retried forever under a stale definition of "processing") and a
# failure notice is written back to the sender's own inbox via
# inbox_write.sh.
#
# B-4 Return-Path (project_documents id=60d41aee-5128-427d-82ae-dc0946d94682
# v1.1) requires more than "sent" — it requires arrival to be confirmed via
# a SEPARATE channel before the warning obligation is discharged. What this
# function does is a partial, honest step toward that: it re-reads the
# sender's inbox FILE (a channel independent of inbox_write.sh's own exit
# code) to confirm the notice actually landed on disk, and logs a distinct
# WARNING if it did not — so a silent inbox_write.sh failure is not
# mistaken for a delivered notice. This is NOT full B-4 compliance: it
# confirms the write landed, not that the human/agent recipient has become
# aware of it (that would require tracking read=true on this specific
# notice in a later watcher cycle, which is out of scope for this cure —
# see the portability/handoff note in the W201 report for why).
return_message_to_sender() {
    local msg_id="$1" msg_from="$2" msg_type="$3" reason="$4"
    echo "[$(date)] [RETURN-TO-SENDER] $AGENT_ID: undeliverable ${msg_type} (id=${msg_id}) — ${reason}" >&2
    if [ -n "$msg_from" ]; then
        bash "$SCRIPT_DIR/scripts/inbox_write.sh" "$msg_from" \
            "配送失敗通知: ${AGENT_ID} 宛 ${msg_type} (id=${msg_id}) を実行できませなんだ。理由=${reason}" \
            "delivery_failed" "$AGENT_ID" 2>&1 | while IFS= read -r line; do
            echo "[$(date)] [RETURN-TO-SENDER] $line" >&2
        done
        # Independent-channel landing check (not human-arrival confirmation —
        # see comment above): re-read the sender's inbox file itself.
        local sender_inbox="$SCRIPT_DIR/queue/inbox/${msg_from}.yaml"
        if [ -f "$sender_inbox" ] && grep -qF "$msg_id" "$sender_inbox" 2>/dev/null; then
            echo "[$(date)] [RETURN-TO-SENDER] landing confirmed via file re-read: ${sender_inbox} contains a reference to ${msg_id}" >&2
        else
            echo "[$(date)] [RETURN-TO-SENDER] WARNING: could not confirm delivery_failed notice landed in ${sender_inbox} (msg_id=${msg_id}) — inbox_write.sh may have failed silently" >&2
        fi
    else
        echo "[$(date)] [RETURN-TO-SENDER] no 'from' field on message (id=${msg_id}) — cannot notify sender" >&2
    fi
    mark_message_processed "$msg_id"
}

# ─── Send CLI command via pty direct write ───
# For /clear and /model only. These are CLI commands, not conversation messages.
# CLI_TYPE別分岐: claude→そのまま, codex→/clear対応・/modelスキップ,
#                  copilot→Ctrl-C+再起動・/modelスキップ
# 実行時にtmux paneの @agent_cli を再確認し、ドリフト時はpane値を優先する。
# ─── Send text+Enter to pane with delivery verification (W205 root cure) ───
# Shared by send_cli_command()'s branches. Sends `text`, presses Enter, then
# re-captures the pane to confirm `text` is no longer sitting unsent in the
# input line — the same verify-by-absence check already used by the nudge
# path (send_wakeup), reused here rather than reinvented (Anti-Duplication).
# Retries up to 2x with C-u clear + resend on failure. Every send-keys call
# on the command/Enter path is checked for its own exit status too — no
# `|| true` on the keystrokes that carry the actual command, so a failed
# injection surfaces as a real return 1 instead of being silently absorbed.
# Returns 0 only on confirmed delivery, 1 if every attempt failed.
send_keys_verified() {
    local text="$1"
    local enter_gap="${2:-0.3}"
    local max_retries=2
    local attempt=0
    local rc=1
    local skv_cli
    skv_cli=$(get_effective_cli_type)
    while [ $attempt -le $max_retries ]; do
        # ★送信前門★ (令25 ⑴) — codex 路のみ。claude 路は一字も変えぬ (既知の穴、票 §3-4)。
        if [[ "$skv_cli" == "codex" ]]; then
            if ! codex_presend_gate "$text" "$PANE_TARGET"; then
                echo "[$(date)] [DEFER] send_keys_verified 見送り (presend=$CODEX_PRESEND_STATE): $text" >&2
                return 1
            fi
        else
            timeout 5 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null
            sleep 0.2
        fi
        if ! timeout 5 tmux send-keys -t "$PANE_TARGET" "$text" 2>/dev/null; then
            echo "[$(date)] WARNING: send-keys text injection failed (attempt $((attempt+1))): $text" >&2
            attempt=$((attempt+1))
            continue
        fi
        sleep "$enter_gap"
        if ! timeout 5 tmux send-keys -t "$PANE_TARGET" Enter 2>/dev/null; then
            echo "[$(date)] WARNING: send-keys Enter injection failed (attempt $((attempt+1))): $text" >&2
            attempt=$((attempt+1))
            continue
        fi
        sleep 0.5
        local pane_content
        pane_content=$(timeout 3 tmux capture-pane -t "$PANE_TARGET" -p 2>/dev/null | tail -5)
        if echo "$pane_content" | grep -qF -- "$text"; then
            echo "[$(date)] WARNING: '$text' still visible unsent in pane after Enter, retrying (attempt $((attempt+1)))" >&2
            attempt=$((attempt+1))
            continue
        fi
        rc=0
        break
    done
    if [ "$rc" -ne 0 ]; then
        echo "[$(date)] ERROR: send_keys_verified exhausted $max_retries retries, Enter never confirmed landed: $text" >&2
    fi
    return "$rc"
}

send_cli_command() {
    local cmd="$1"
    local effective_cli
    effective_cli=$(get_effective_cli_type)

    # cli_restart: delegate to switch_cli.sh (full /exit → relaunch cycle)
    if [[ "$cmd" == __CLI_RESTART__:* ]]; then
        local restart_args="${cmd#__CLI_RESTART__:}"
        echo "[$(date)] [CLI-RESTART] Delegating to switch_cli.sh for $AGENT_ID: ${restart_args}" >&2
        bash "${SCRIPT_DIR}/scripts/switch_cli.sh" "$AGENT_ID" $restart_args 2>&1 | while IFS= read -r line; do  # SCRIPT_DIR=project_root
            echo "[$(date)] [switch_cli] $line" >&2
        done
        # Update effective CLI type after restart
        CLI_TYPE=$(tmux show-options -p -t "$PANE_TARGET" -v @agent_cli 2>/dev/null || echo "$CLI_TYPE")
        return 0
    fi

    # Safety: never inject CLI commands into the shogun pane.
    # 信長 is controlled by the Lord; keystroke injection can clobber human input.
    if [ "$AGENT_ID" = "shogun" ]; then
        echo "[$(date)] [SKIP] shogun: suppressing CLI command injection ($cmd)" >&2
        return 0
    fi

    # W205 root-cause cure: busy guard now covers EVERY command this function
    # sends (/clear, /model, codex /new, copilot restart) — not just /clear.
    # Typing into a pane mid-Working appends keystrokes to text the CLI is
    # still composing/rendering; the previous code only guarded /clear,
    # leaving /model and codex/copilot paths free to type during Working.
    # Returns 2 (distinct from the 1 used for genuine injection/verification
    # failure below) so callers can tell "busy, retry next cycle — leave the
    # source message unread" apart from "actually failed to deliver, return
    # to sender." Conflating the two here would reintroduce the exact
    # consume-before-commit bug W201 fixed, just for model_switch/cli_restart
    # instead of clear_command: process_unread()'s else-branch calls
    # return_message_to_sender(), which marks the message read=True — a busy
    # agent's queued /model would then be silently lost on the very next
    # cycle instead of retried.
    if agent_is_busy; then
        echo "[$(date)] [SKIP] Agent $AGENT_ID is busy (Working) — CLI command deferred to next cycle: $cmd" >&2
        return 2
    fi

    # CLI別コマンド変換
    local actual_cmd="$cmd"
    case "$effective_cli" in
        codex)
            # Codex: /clear不存在→/newで新規会話開始, /model非対応→スキップ
            # /clearはCodexでは未定義コマンドでCLI終了してしまうため、/newに変換
            if [[ "$cmd" == "/clear" ]]; then
                # Guard: skip duplicate /new if already sent for this batch
                if [ "${NEW_CONTEXT_SENT:-0}" -eq 1 ]; then
                    echo "[$(date)] [SKIP] Codex /new already sent for $AGENT_ID — skipping duplicate clear_command" >&2
                    return 0
                fi
                echo "[$(date)] [SEND-KEYS] Codex /clear→/new: starting new conversation for $AGENT_ID" >&2
                # ★送信前門★ (令25 ⑴): "x" は それ自体が composer へ一文字書き込む。
                #   ∴ 門は "x" の ★前★。書きかけが在れば "x" すら撃たぬ。
                if ! codex_presend_gate "" "$PANE_TARGET"; then
                    echo "[$(date)] [DEFER] Codex /new 見送り for $AGENT_ID (presend=$CODEX_PRESEND_STATE)" >&2
                    return 1
                fi
                # Dismiss suggestion UI first (typing "x" clears autocomplete prompt).
                # These two are best-effort UI resets, not the command itself —
                # a failure here just means the dismiss/clear no-ops, harmless.
                timeout 5 tmux send-keys -t "$PANE_TARGET" "x" 2>/dev/null || true
                sleep 0.3
                # ★"x" を消してから send_keys_verified へ渡す★:
                #   渡さねば 其の中の門が「"x" = 他者の draft」と誤読して永久に見送り申す
                #   (旧実装は先頭の無条件 C-u が偶々此れを消して居た)。
                timeout 5 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
                sleep 0.2
                if ! send_keys_verified "/new" 0.3; then
                    echo "[$(date)] ERROR: Codex /new delivery not confirmed for $AGENT_ID" >&2
                    return 1
                fi
                sleep 3
                # Send startup prompt immediately (don't defer to context-reset cycle)
                send_codex_startup_prompt
                NEW_CONTEXT_SENT=1
                return 0
            fi
            if [[ "$cmd" == /model* ]]; then
                echo "[$(date)] Skipping $cmd (not supported on codex)" >&2
                return 0
            fi
            ;;
        copilot)
            # Copilot: /clearはCtrl-C+再起動, /model非対応→スキップ
            if [[ "$cmd" == "/clear" ]]; then
                echo "[$(date)] [SEND-KEYS] Copilot /clear: sending Ctrl-C + restart for $AGENT_ID" >&2
                if ! timeout 5 tmux send-keys -t "$PANE_TARGET" C-c 2>/dev/null; then
                    echo "[$(date)] ERROR: Copilot C-c injection failed for $AGENT_ID" >&2
                    return 1
                fi
                sleep 2
                if ! send_keys_verified "copilot --yolo" 0.3; then
                    echo "[$(date)] ERROR: Copilot restart delivery not confirmed for $AGENT_ID" >&2
                    return 1
                fi
                sleep 3
                return 0
            fi
            if [[ "$cmd" == /model* ]]; then
                echo "[$(date)] Skipping $cmd (not supported on copilot)" >&2
                return 0
            fi
            ;;
        # claude: commands pass through as-is
    esac

    echo "[$(date)] [SEND-KEYS] Sending CLI command to $AGENT_ID ($effective_cli): $actual_cmd" >&2
    # Clear stale input first, then send command (text and Enter separated for Codex TUI)
    # Codex CLI: C-c when idle causes CLI to exit — skip it
    if [[ "$effective_cli" != "codex" ]]; then
        if ! timeout 5 tmux send-keys -t "$PANE_TARGET" C-c 2>/dev/null; then
            echo "[$(date)] WARNING: C-c pre-clear injection failed for $AGENT_ID (proceeding anyway)" >&2
        fi
        sleep 0.5
    fi
    # /clear needs longer gap before Enter — CLI prompt may not be ready at 0.3s
    local enter_gap=0.3
    if [[ "$actual_cmd" == "/clear" || "$actual_cmd" == "/new" ]]; then
        enter_gap=1.0
    fi
    if ! send_keys_verified "$actual_cmd" "$enter_gap"; then
        echo "[$(date)] ERROR: CLI command delivery not confirmed for $AGENT_ID: $actual_cmd" >&2
        return 1
    fi

    # /clear needs extra wait time before follow-up
    if [[ "$actual_cmd" == "/clear" ]]; then
        LAST_CLEAR_TS=$(date +%s)
        sleep 3
    else
        sleep 1
    fi
}

# ─── Send Codex startup prompt after /new ───
# Waits for agent to become idle, then sends a startup prompt that includes
# full recovery steps (identify, read task YAML, read inbox, start work).
# Called from both send_cli_command (clear_command) and send_context_reset.
is_no_auto_clear_agent() {
    case "$AGENT_ID" in
        shogun|shogun-second|shogun-third|karo|karo-second|karo-third|gunshi|gunshi-second|gunshi-third|ashigaru5|ashigaru6|ashigaru7|ashigaru8)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

send_codex_startup_prompt() {
    # Poll until agent becomes idle (prompt ready) instead of fixed sleep.
    # Max 15s (3 attempts × 5s). If still busy after 15s, proceed anyway.
    local attempt
    for attempt in 1 2 3; do
        sleep 5
        if ! agent_is_busy; then
            echo "[$(date)] [STARTUP] $AGENT_ID idle after ${attempt}×5s — sending startup prompt" >&2
            break
        fi
        echo "[$(date)] [STARTUP] $AGENT_ID still busy after ${attempt}×5s — retrying" >&2
    done
    if agent_is_busy; then
        echo "[$(date)] [STARTUP] $AGENT_ID still busy after 15s — proceeding with startup prompt anyway" >&2
    fi

    local startup_prompt=""
    if type get_startup_prompt &>/dev/null; then
        startup_prompt=$(get_startup_prompt "$AGENT_ID" 2>/dev/null || true)
    fi
    if [[ -z "$startup_prompt" ]]; then
        startup_prompt="Session Start — do ALL of this in one turn, do NOT stop early: 1) tmux display-message to identify yourself. 2) Read queue/tasks/${AGENT_ID}.yaml. 3) Read queue/inbox/${AGENT_ID}.yaml, mark read:true. 4) Read context_files. 5) Execute the assigned task to completion — edit files, run commands, write reports. Keep working until done."
    fi
    echo "[$(date)] [STARTUP] Sending startup prompt to $AGENT_ID (codex): ${startup_prompt:0:80}..." >&2
    # ★送信前門★ (令25 ⑴): 此処に「己の prefix」は無い ∴ 空 composer のみ通す。
    #   書きかけが在れば startup prompt も送らぬ (混合便を作らぬ・draft を消さぬ)。
    if ! codex_presend_gate "" "$PANE_TARGET"; then
        echo "[$(date)] [DEFER] startup prompt 見送り for $AGENT_ID (presend=$CODEX_PRESEND_STATE) — STARTUP_PROMPT_SENT は立てぬ" >&2
        return 1
    fi
    # Dismiss suggestion UI, then send startup prompt
    timeout 5 tmux send-keys -t "$PANE_TARGET" "x" 2>/dev/null || true
    sleep 0.3
    timeout 5 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
    sleep 0.3
    timeout 5 tmux send-keys -l -t "$PANE_TARGET" "$startup_prompt" 2>/dev/null || true
    sleep 0.3
    timeout 5 tmux send-keys -t "$PANE_TARGET" Enter 2>/dev/null || true
    STARTUP_PROMPT_SENT=1
}

# ─── Send context reset before new task ───
# Called when task_assigned is detected in unread messages.
# Sends the appropriate "new conversation" command per CLI type to clear
# stale context from the previous task.
# CLI mapping: claude→/clear, codex→/new, copilot→/clear, kimi→/clear
send_context_reset() {
    local effective_cli
    effective_cli=$(get_effective_cli_type)

    # Safety: never auto-reset context for command-layer agents.
    # Only ashigaru should receive automatic context resets (clear stale task context).
    # 信長 (human-controlled), 家老 (coordinator state), 家康 (strategic state)
    # all maintain complex running context that should not be wiped automatically.
    if is_no_auto_clear_agent; then
        echo "[$(date)] [SKIP] $AGENT_ID: suppressing automatic context reset during SecondPC role recovery" >&2
        return 0
    fi

    # 副院長令 fc3a5b0b RC-1 cure (2026-06-07): busy 中は /clear を送らず defer。
    # 旧 bug: busy 中でも /clear 貫通 (L681 proceeding anyway) → a3-3 の思考途中で割込み消失。
    # busy 解除後の次 cycle で再評価。return 1 = caller に "未送信 retry 必要" を伝える。
    if agent_is_busy; then
        echo "[$(date)] [DEFER] $AGENT_ID: agent busy — postponing context reset (RC-1 cure)" >&2
        return 1
    fi

    local reset_cmd
    case "$effective_cli" in
        codex)    reset_cmd="/new" ;;
        claude)   reset_cmd="/clear" ;;
        copilot)  reset_cmd="/clear" ;;
        kimi)     reset_cmd="/clear" ;;
        *)        reset_cmd="/new" ;;  # safe default (codex-safe)
    esac

    echo "[$(date)] [CONTEXT-RESET] Sending $reset_cmd before task_assigned for $AGENT_ID ($effective_cli)" >&2

    # Codex: send /new + startup prompt as a single atomic operation.
    # When called from clear_command path, NEW_CONTEXT_SENT=1 prevents reaching here.
    # When called for standalone task_assigned, this is the only /new send.
    if [[ "$effective_cli" == "codex" ]]; then
        # ★送信前門★ (令25 ⑴): 書きかけが在れば /new も送らぬ。
        #   /new は 会話を捨てる不可逆の令 ∴ 尚更 draft を跨いで撃ってはならぬ。
        #   return 1 = caller へ「未送信・retry 要」を伝える (RC-1 契約と同じ)。
        if ! codex_presend_gate "" "$PANE_TARGET"; then
            echo "[$(date)] [DEFER] $AGENT_ID: context reset (/new) 見送り (presend=$CODEX_PRESEND_STATE)" >&2
            return 1
        fi
        # Dismiss suggestion UI + send /new
        timeout 5 tmux send-keys -t "$PANE_TARGET" "x" 2>/dev/null || true
        sleep 0.3
        timeout 5 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
        sleep 0.3
        timeout 5 tmux send-keys -t "$PANE_TARGET" "/new" 2>/dev/null || true
        sleep 0.3
        timeout 5 tmux send-keys -t "$PANE_TARGET" Enter 2>/dev/null || true
        sleep 3
        # Wait for idle + send startup prompt via shared helper
        send_codex_startup_prompt
        return 0
    fi

    # Non-Codex CLIs: send /clear and wait for idle
    # Send the command (text and Enter separated for TUI compatibility)
    timeout 5 tmux send-keys -t "$PANE_TARGET" "$reset_cmd" 2>/dev/null || true
    # Longer gap for /clear — CLI prompt rendering needs time
    sleep 1.0
    timeout 5 tmux send-keys -t "$PANE_TARGET" Enter 2>/dev/null || true
    # Mark /clear timestamp so agent_is_busy() treats it as busy during processing
    if [[ "$reset_cmd" == "/clear" ]]; then
        LAST_CLEAR_TS=$(date +%s)
    fi

    # Poll until agent becomes idle (prompt ready) instead of fixed sleep.
    # Max 15s (3 attempts × 5s). If still busy after 15s, proceed anyway.
    local attempt
    for attempt in 1 2 3; do
        sleep 5
        if ! agent_is_busy; then
            echo "[$(date)] [CONTEXT-RESET] $AGENT_ID idle after ${attempt}×5s — ready for nudge" >&2
            break
        fi
        echo "[$(date)] [CONTEXT-RESET] $AGENT_ID still busy after ${attempt}×5s — retrying" >&2
    done
    if agent_is_busy; then
        # 副院長令 fc3a5b0b RC-1 cure (2026-06-07): /clear 送信後 15s wait しても busy なら
        # post-reset nudge をスキップ (Claude Code Stop hook 経由配送に委任)。
        # return 2 = "sent but still busy, skip post-reset nudge" (caller で NEW_CONTEXT_SENT=1 立てるが nudge skip)
        echo "[$(date)] [CONTEXT-RESET] $AGENT_ID still busy after 15s — skip post-reset nudge (Stop hook will deliver)" >&2
        return 2
    fi
}

# ─── Agent self-watch detection ───
# Check if the agent has an active inotifywait on its inbox.
# If yes, the agent will self-wake — no nudge needed.
agent_has_self_watch() {
    # R2 recovery guard: command-layer role agents must be woken by the watcher.
    # Treating another inotifywait as "self-watch" caused karo-second delivery stalls.
    case "$AGENT_ID" in
        shogun|shogun-*|karo|karo-*|gunshi|gunshi-*) return 1 ;;
    esac

    # Codex/Copilot/Kimi CLIs cannot run self-watch. Only Claude Code agents can.
    local effective_cli
    effective_cli=$(get_effective_cli_type)
    if [[ "$effective_cli" != "claude" ]]; then
        return 1  # non-Claude CLIs never have self-watch
    fi
    # For Claude Code agents: check if an inotifywait exists that is NOT
    # a child of this inbox_watcher process (exclude our own watcher).
    local my_pgid
    my_pgid=$(ps -o pgid= -p $$ 2>/dev/null | tr -d ' ')
    local found=1  # default: not found
    while IFS= read -r pid; do
        local pid_pgid
        pid_pgid=$(ps -o pgid= -p "$pid" 2>/dev/null | tr -d ' ')
        if [[ "$pid_pgid" != "$my_pgid" ]]; then
            found=0  # found an inotifywait NOT from our process group
            break
        fi
    done < <(pgrep -f "inotifywait.*inbox/${AGENT_ID}.yaml" 2>/dev/null)
    return $found
}

# ─── Agent busy detection ───
# Check if the agent's CLI is currently processing (Working/thinking/etc).
# Sending nudge during Working causes text to queue but Enter to be lost.
# Returns 0 (true) if agent is busy, 1 if idle.
# Implementation: delegates to lib/agent_status.sh (shared library).
agent_is_busy() {
    # /clear cooldown: treat agent as busy for 30s after /clear was sent.
    # Claude Code's /clear takes 10-30s (CLAUDE.md reload + context init).
    # Without this, nudges sent during /clear processing queue up at the prompt
    # and cause race conditions (inbox1 arrives before /clear completes).
    local now_busy
    now_busy=$(date +%s)
    if [ "${LAST_CLEAR_TS:-0}" -gt 0 ] && [ "$((now_busy - LAST_CLEAR_TS))" -lt 30 ]; then
        return 0  # busy — /clear still processing
    fi

    local effective_cli
    effective_cli=$(get_effective_cli_type)
    if [[ "$effective_cli" == "claude" ]]; then
        # The idle flag is only a hint. It can remain stale while Claude is
        # retrying an API error, and treating that stale flag as authoritative
        # queues another inboxN every cooldown interval. Always honor the
        # current pane's busy status and its queued-message indicator first.
        local pane_state_rc
        if agent_is_busy_check "$PANE_TARGET"; then
            return 0
        else
            pane_state_rc=$?
        fi
        # A missing pane is not a safe target for keystroke injection.
        if [ "$pane_state_rc" -eq 2 ]; then
            return 0
        fi
        local pane_capture pane_tail
        # Store the full capture first: command substitution strips trailing
        # blank rows. Piping capture-pane directly to tail can otherwise make
        # the visible queued-message hint fall outside the inspected window.
        pane_capture=$(timeout 2 tmux capture-pane -t "$PANE_TARGET" -p 2>/dev/null || true)
        pane_tail=$(echo "$pane_capture" | tail -12)
        if echo "$pane_tail" | grep -qF 'Press up to edit queued message'; then
            return 0
        fi
        # フラグファイル方式: フラグなし=busy(return 0)、あり=idle(return 1)
        [ ! -f "${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}" ]
    else
        # 従来のpane解析（Codex等フォールバック）
        agent_is_busy_check "$PANE_TARGET"
    fi
}

# ─── Pane focus detection (human safety) ───
# If the target pane is currently active, avoid injecting keystrokes.
pane_is_active() {
    local active=""
    active=$(timeout 2 tmux display-message -p -t "$PANE_TARGET" '#{pane_active}' 2>/dev/null || true)
    [ "$active" = "1" ]
}

# ─── Session attach detection ───
# Function: session_has_client
# Description: Checks if the tmux session containing PANE_TARGET has at least
#   one client attached. Used to avoid suppressing send-keys when no human is
#   watching (e.g. single-pane shogun session where pane_is_active is always true).
# Arguments: none (uses global PANE_TARGET)
# Returns: 0 if at least one client is attached, 1 otherwise
session_has_client() {
    local session_name
    session_name=$(timeout 2 tmux display-message -p -t "$PANE_TARGET" '#{session_name}' 2>/dev/null || true)
    [ -n "$session_name" ] && [ "$(tmux list-clients -t "$session_name" 2>/dev/null | wc -l)" -gt 0 ]
}

# ─── Send wake-up nudge ───
# Layered approach:
#   1. If agent has active inotifywait self-watch → skip (agent wakes itself)
#   2. If agent is busy (Working) → skip (nudge during Working loses Enter)
#   3. tmux send-keys (短いnudgeのみ、timeout 5s)
# ─── Detect if user is currently typing in the pane ───
# 入力中検出: claude TUI の prompt「❯ <文字>」を capture-pane で確認。
# 文字が入っている = 理事長殿/エージェントが入力中 → nudge を skip して入力保護。
# Welcome screen の「Try "..."」suggestion は idle 扱い (実入力ではない)。
# 連続 N 回 typing で skip された場合、強制 nudge (緊急メッセージが届かない事故防止)。
#
# DD-169 patch (2026-06-02 karo-third F001 例外, shogun msg_20260602_182927 承認下):
#   旧版は grep -oE '❯[[:space:]]+[^[:space:]].*' で pane buffer 全体から非空 prompt 行を
#   抽出していたため、historical スクロール (e.g. `❯ /clear` 既往) を current prompt と
#   誤認 → system-wide typing false-positive で nudge 永久 skip (a3-1/a3-7 で実証)。
#   修正: 全 ❯ 行 (空含む) を抽出し tail -1 で ★bottom (= current cursor 位置) のみ★ 判定。
#   空 prompt は idle (return 1)、内容ある場合のみ typing 判定。
#
# Bypass flag (緊急時): INBOX_WATCHER_DISABLE_TYPING_CHECK=1 で typing 検出全体を無効化可。
is_user_typing() {
    local pane="$1"
    # Emergency bypass — typing 検出無効化 (root-cure 復旧用)
    if [ "${INBOX_WATCHER_DISABLE_TYPING_CHECK:-0}" = "1" ]; then
        return 1  # treat as idle always — allow nudge
    fi
    local current_prompt
    current_prompt=$(timeout 3 tmux capture-pane -t "$pane" -p -e -J 2>/dev/null \
        | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g; s/\x1b[()][AB012]//g; s/\x1b[78]//g' \
        | grep -E '^❯' \
        | tail -1)
    if [ -z "$current_prompt" ]; then
        return 1  # no prompt visible — allow nudge
    fi
    # NBSP (U+00A0, claude TUI が空 prompt 描画に使用) を通常空白へ正規化。
    # POSIX [:space:] は NBSP を含まぬため、これを行わぬと空 prompt が非空と誤判定される。
    local normalized
    normalized=$(echo "$current_prompt" | sed 's/\xc2\xa0/ /g')
    local content
    content=$(echo "$normalized" | sed 's/^❯[[:space:]]*//' | sed 's/[[:space:]]*$//')
    # 空 prompt (current cursor 位置) = idle
    if [ -z "$content" ]; then
        return 1
    fi
    # claude TUI の placeholder / affordance hint 行は ❯ で始まるが実入力ではない。
    # CLI 自身が描画する案内文ゆえ idle 扱い (= nudge を skip しない)。
    #   - 'Try "..."'                       : welcome 画面の suggestion
    #   - 'Press up to edit queued messages': メッセージ queue 時の案内
    #     (2026-06-02 ee4d6ce4 Step0: a3-1/a3-5 で「empty idle なのに常時 typing 誤検出」の真因。
    #      queue hint 行が ❯<NBSP>Press up... と column0 の ❯ で描画され grep '^❯'|tail -1 に拾われる)
    case "$content" in
        Try\ *)                                    return 1 ;;
        Press\ up\ to\ edit\ queued\ message*)      return 1 ;;
    esac
    return 0  # typing — defer nudge
}

# ─── Codex composer residue cleanup (工区1 ⒝① / 理事長令「通信経路恒久安定化」) ───
# 症状: codex TUI (v0.19.0) は C-m で submit した後も本文を composer に残す。
#       ∴ 残骸を「入力中」と誤読して以後の nudge を永久 skip する (is_user_typing)、
#       また着弾済 nudge を「送信失敗」と誤読して再送する (旧 grep -qF on tail -5)。
#       同型の実害は hermes 系 downlink watcher の docstring に実測記録あり
#       (/home/hakudokai/bin/hermes_downlink_watcher.py: 「自分が配った便の残り文字を
#        見て永久に処理中と誤判定する」)。
#
# ★掃除は「注入した prefix と composer 行が 完全一致」する時に限る★。
#   一字でも違えば触れぬ = 人/agent の本物 draft を破壊せぬ為 (最大の損害はこちら)。
#
# interface 契約 (a4 の負テスト設計 C-1〜C-4 に対する回答):
#   C-1: 掃除判定は本関数 ★一つ★ に閉じる。テストは本関数を直に呼ぶ事。
#   C-2: 注入 prefix は ★第1引数★ で受け取る (pane は第2引数、既定 $PANE_TARGET)。
#   C-3: 掃除の実行は `tmux send-keys ... C-u` として観測可能。
#        加えて判定結果を大域 CODEX_RESIDUE_STATE に置く
#        (cleaned / composer_mismatch / not_landed / no_composer / empty_prefix)。
#   C-4: ★正規化規則 (逐語)★ ―― 判定前に composer 行へ次を順に施す:
#        ⑴ NBSP (U+00A0) を通常空白へ変換
#        ⑵ 行頭の空白を除去
#        ⑶ 行頭の composer marker 一文字 (❯ U+276F または › U+203A) を除去
#        ⑷ 続く行頭の空白を除去
#        ⑸ ★行末の空白を除去★
#        比較は上記正規化後の ★文字列完全一致 (部分一致に非ず)★。
#        ⑸ の根拠 = 実測: `tmux capture-pane -p` は各行の行末空白を ★必ず落とす★
#        (`-N` 付きでのみ保持される)。∴ 本経路では「末尾スペース一つの差」は
#        ★観測channel上そもそも区別し得ぬ★。a4 票の ㈡ⓔ (`› inbox2 `) は
#        本規則の下で ★完全一致扱い = 掃除が走る★ が期待値に御座る。
#        (掃除を緩めたのではなく、capture が落とす物を測れぬと認めた形)
#
# ★判定は composer 行 ただ一行のみを見る★ (capture 全体を grep せぬ)。
#   着弾した nudge は ★会話面にも★ 在るゆえ、全体 grep では常に一致し掃除が暴発する。
# 着弾 (会話面に prefix 在り) を ★掃除の前提★ とする: 未着弾で消せば便が失われる。
#
# 返値: 0 = 掃除した / 1 = 掃除せず (理由は CODEX_RESIDUE_STATE)

# ─── composer 行の抽出 + 正規化 (C-4 逐語規則の ★唯一の実装★) ───
# 送信前門 (codex_presend_gate) と 送信後掃除 (codex_residue_cleanup) は
# ★同一の正規化★ を見る事 (Anti-Duplication / 二つの測りが食い違わぬ為)。
# ★結果は stdout ではなく 大域変数で返す★:
#   COMPOSER_CONTENT … 正規化済 composer 内容 (空文字 = composer は空)
#   COMPOSER_CAP     … capture 全文 / COMPOSER_LINENO … composer の行番号
#   理由 = `x=$(composer_line_normalized …)` は ★副シェル★ を作り、
#          其の中で置いた大域は呼び手へ戻らぬ。stdout 契約にすると
#          呼び手が COMPOSER_CAP を空のまま使う (= 着弾判定が壊れる)。
# 返値   : 0 = composer 行を得た / 1 = marker 不在 (capture 失敗を含む)
# NOTE: pipeline に `|| true` を付すは set -euo pipefail 下で
#       grep 不一致 (= marker 不在) が ★watcher daemon を殺す★ を防ぐ為。
composer_line_normalized() {
    local pane="${1:-$PANE_TARGET}"
    COMPOSER_CAP=""
    COMPOSER_LINENO=""
    COMPOSER_CONTENT=""
    COMPOSER_CAP=$(timeout 3 tmux capture-pane -t "$pane" -p 2>/dev/null || true)
    # composer = ★最下段★ の marker 行 (履歴中の古い marker 行を拾わぬ)
    COMPOSER_LINENO=$(printf '%s\n' "$COMPOSER_CAP" \
        | grep -nE '^[[:space:]]*(❯|›)' | tail -1 | cut -d: -f1 || true)
    if [ -z "$COMPOSER_LINENO" ]; then
        return 1
    fi
    # C-4 の正規化 ⑴〜⑸
    COMPOSER_CONTENT=$(printf '%s\n' "$COMPOSER_CAP" | sed -n "${COMPOSER_LINENO}p" \
        | sed 's/\xc2\xa0/ /g' \
        | sed 's/^[[:space:]]*//' \
        | sed 's/^[❯›]//' \
        | sed 's/^[[:space:]]*//' \
        | sed 's/[[:space:]]*$//')
    return 0
}

# ─── ★送信前の門★ (令25 ⑴ 根治) ───────────────────────────────
# 出自: 令①の範囲外を ★将軍second 裁で工区1へ拡張★ (msg_20260807_204202_d4f658ab ■1)。
#
# 直す物: 注入の直前に置かれた ★無条件★ の `send-keys C-u`。
#   C-u は composer 行を丸ごと消す。∴ 其の刹那に人/agent が書きかけの draft を
#   抱えて居れば ★一字残らず消える★。実害は仮想に非ず ―― 本改修の起票時、
#   hermes-honbucho:0.0 の composer は現に未送信の draft
#   (`[本部長 downlink] pc_handshake seq=155925`) を抱えて居り申した (実測)。
#
# 望む結末 (令 ㈠ 逐語):
#   ①本物の draft を一字も失わぬ ②混合便を作らぬ。
#   ∴ 掃除 (C-u) が許されるは ★composer が空★ か ★己の注入 prefix と完全一致★ の時のみ。
#   一字でも違えば ★触れず・注入も見送り★、後刻 retry+log の路とする。
#   (dirty composer への注入は 己の文と他者の文が繋がった ★混合便★ を生むゆえ禁)
#
# ★門は "x" (suggestion 消し) より ★前★ に置く事★:
#   "x" は それ自体が一文字を composer へ書き込む = draft を汚す。
#   ∴ 門を "x" の後に置けば 門が守るべき物を門の手前で壊す事に成り申す。
#
# 状態 (CODEX_PRESEND_STATE):
#   empty       … composer 空 → 掃除不要・注入可 (返値 0)
#   cleaned_own … 己の prefix と完全一致 → C-u 掃除の上 注入可 (返値 0)
#   dirty       … 他者の文在り → ★C-u も注入も為さぬ★ (返値 1)
#   no_composer … marker 不在 (capture 失敗/画面遷移中) → 安全側に見送る (返値 1)
#
# ★no_composer を「見送り」とする代償 (明示)★: composer を永久に見失う pane では
#   nudge が飢える。∴ 黙って落とさず ★毎回 log に出す★ (下記 [PRESEND] 行)。
#   飢餓が実測されたなら 其は本門の緩和ではなく ★marker 検出の拡張★ で直すべし。
#
# ★log に composer の中身を出さぬ★: 他者の draft は患者本文・secret を含み得る。
#   ∴ dirty 時は 長さ (len) のみを記す。
#
# 返値: 0 = 注入して良し / 1 = ★注入を見送れ (caller は送信せず defer せよ)★
codex_presend_gate() {
    local own_prefix="$1"
    local pane="${2:-$PANE_TARGET}"
    CODEX_PRESEND_STATE="unknown"

    if ! composer_line_normalized "$pane"; then
        CODEX_PRESEND_STATE="no_composer"
        echo "[$(date)] [PRESEND] composer 不検出 — 掃除も注入も為さず見送る for ${AGENT_ID:-?} (pane=$pane)" >&2
        return 1
    fi
    local content="$COMPOSER_CONTENT"

    if [ -z "$content" ]; then
        CODEX_PRESEND_STATE="empty"
        return 0
    fi

    if [ -n "$own_prefix" ] && [ "$content" = "$own_prefix" ]; then
        timeout 5 tmux send-keys -t "$pane" C-u 2>/dev/null || true
        sleep 0.2
        CODEX_PRESEND_STATE="cleaned_own"
        echo "[$(date)] [PRESEND] composer=己の注入 prefix と完全一致 — 掃除して注入 for ${AGENT_ID:-?} (prefix='${own_prefix}')" >&2
        return 0
    fi

    CODEX_PRESEND_STATE="dirty"
    echo "[$(date)] [PRESEND] ★composer に他者の draft 在り — C-u も注入も為さず見送る★ for ${AGENT_ID:-?} (pane=$pane, len=${#content})" >&2
    return 1
}

codex_residue_cleanup() {
    local prefix="$1"
    local pane="${2:-$PANE_TARGET}"
    CODEX_RESIDUE_STATE="unknown"

    if [ -z "$prefix" ]; then
        CODEX_RESIDUE_STATE="empty_prefix"
        return 1
    fi

    if ! composer_line_normalized "$pane"; then
        CODEX_RESIDUE_STATE="no_composer"
        return 1
    fi
    local content="$COMPOSER_CONTENT"

    # ★完全一致★ でなければ触れぬ (本物 draft 保護)
    if [ "$content" != "$prefix" ]; then
        CODEX_RESIDUE_STATE="composer_mismatch"
        return 1
    fi

    # 会話面着弾の確認 — composer 行を ★除いた★ 領域に prefix が在るか
    if ! printf '%s\n' "$COMPOSER_CAP" | sed "${COMPOSER_LINENO}d" | grep -qF -- "$prefix"; then
        CODEX_RESIDUE_STATE="not_landed"
        return 1
    fi

    timeout 5 tmux send-keys -t "$pane" C-u 2>/dev/null || true
    CODEX_RESIDUE_STATE="cleaned"
    echo "[$(date)] [RESIDUE] codex composer residue cleaned for ${AGENT_ID:-?} (prefix='${prefix}')" >&2
    return 0
}

send_wakeup() {
    local unread_count="$1"
    local nudge="inbox${unread_count}"

    if [ "${FINAL_ESCALATION_ONLY:-0}" = "1" ]; then
        echo "[$(date)] [SKIP] FINAL_ESCALATION_ONLY=1, suppressing normal nudge for $AGENT_ID" >&2
        return 0
    fi

    # /clear+nudge 連結バグ防止 (2026-05-07 真因対策):
    # /clear 送信後、claude が Welcome 画面遷移中に nudge を送ると
    # 「/clearinbox1」のような不正コマンドに連結される (実例: 5/7 18:00 ashigaru6)。
    # /clear 送信から 5 秒以内は nudge を抑制し、確実に画面遷移を待つ。
    if [ -n "${LAST_CLEAR_TS:-}" ]; then
        local _clear_elapsed=$(($(date +%s) - LAST_CLEAR_TS))
        if [ "$_clear_elapsed" -lt 5 ]; then
            echo "[$(date)] [SKIP] /clear sent ${_clear_elapsed}s ago for $AGENT_ID — deferring nudge (連結バグ防止)" >&2
            return 0
        fi
    fi

    # 優先度1: Agent self-watch — nudge不要（エージェントが自分で気づく）
    if agent_has_self_watch; then
        echo "[$(date)] [SKIP] Agent $AGENT_ID has active self-watch, no nudge needed" >&2
        return 0
    fi

    # 優先度1.5: 入力中検出 — 理事長殿の入力を nudge で破壊しない (連続skip上限あり)
    if is_user_typing "$PANE_TARGET"; then
        local skip_state_file="/tmp/inbox_watcher_typing_skip_${AGENT_ID}"
        local skip_count
        skip_count=$(cat "$skip_state_file" 2>/dev/null || echo 0)
        skip_count=$((skip_count + 1))
        echo "$skip_count" > "$skip_state_file"
        # 上限到達 (default 5 = 約 2.5分) で強制 nudge を許可 (緊急メッセージ事故防止)
        local max_typing_skip="${MAX_TYPING_SKIP:-5}"
        if [ "$skip_count" -le "$max_typing_skip" ]; then
            echo "[$(date)] [SKIP] $AGENT_ID is typing in pane — deferring nudge (skip ${skip_count}/${max_typing_skip})" >&2
            return 0
        fi
        echo "[$(date)] [FORCE] $AGENT_ID typing skip cap (${max_typing_skip}) reached — forcing nudge" >&2
        rm -f "$skip_state_file"
    else
        # 入力なくなった → counter リセット
        rm -f "/tmp/inbox_watcher_typing_skip_${AGENT_ID}" 2>/dev/null
    fi

    # 優先度2: Agent busy — nudge送信するとEnterが消失するためスキップ
    # Claude Code: Stop hook catches unread at turn end. Skip nudge to avoid Enter loss.
    # Exception: shogun — ntfy must be delivered immediately regardless of busy state.
    if agent_is_busy && [[ "$AGENT_ID" != "shogun" ]]; then
        local busy_cli_wakeup
        busy_cli_wakeup=$(get_effective_cli_type)
        if [[ "$busy_cli_wakeup" == "claude" ]]; then
            echo "[$(date)] [SKIP] Agent $AGENT_ID is busy (claude) — Stop hook will deliver, no nudge" >&2
        else
            echo "[$(date)] [SKIP] Agent $AGENT_ID is busy ($busy_cli_wakeup), deferring nudge" >&2
        fi
        return 0
    fi

    if should_throttle_nudge "$unread_count"; then
        return 0
    fi

    # 信長: deliver nudge via send-keys like other agents.
    # ntfy messages must reach Claude Code directly.

    # 優先度3: tmux send-keys（テキストとEnterを分離 — Codex TUI対策）
    echo "[$(date)] [SEND-KEYS] Sending nudge to $PANE_TARGET for $AGENT_ID" >&2

    # Codex suggestion UI dismissal: typing any character dismisses the autocomplete
    # suggestion prompt (› Implement {feature} etc.) that traps idle agents.
    # Sequence: "x" (dismiss suggestion) → C-u (clear input) → nudge → Enter
    local effective_cli_for_nudge
    effective_cli_for_nudge=$(get_effective_cli_type)
    if [[ "$effective_cli_for_nudge" == "codex" ]]; then
        # ★門は "x" の前★ — "x" は それ自体が composer へ一文字書き込むゆえ、
        # 門を後ろに置けば 守るべき draft を門の手前で汚す事に成り申す。
        if ! codex_presend_gate "$nudge" "$PANE_TARGET"; then
            echo "[$(date)] [DEFER] nudge 見送り for $AGENT_ID (presend=$CODEX_PRESEND_STATE) — 次 cycle で再評価" >&2
            return 0
        fi
        timeout 5 tmux send-keys -t "$PANE_TARGET" "x" 2>/dev/null || true
        sleep 0.3
        timeout 5 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
        sleep 0.3
    fi

    # 行クリア（残存テキスト除去）→ nudge送信 → Enter → 確認 → 最大2回リトライ
    local max_retries=2
    local attempt=0
    while [ $attempt -le $max_retries ]; do
        # ★codex 路★: 再試行の度に門を通す。前回注入の nudge は「己の物」ゆえ掃除可、
        #   其の間に人/agent が書き始めて居れば dirty → 触れず見送る。
        # ★claude 路★: 従来の無条件 C-u を一字も変えぬ (稼働中 9本の watcher を壊さぬ為)。
        #   ∴ claude 路は ★本改修で直っておらぬ既知の穴★ に御座る (票 §3-4 に明記)。
        if [[ "$effective_cli_for_nudge" == "codex" ]]; then
            if ! codex_presend_gate "$nudge" "$PANE_TARGET"; then
                echo "[$(date)] [DEFER] codex nudge 見送り for $AGENT_ID (presend=$CODEX_PRESEND_STATE) — 次 cycle で再評価" >&2
                return 0
            fi
        else
            # C-u で行をクリア
            timeout 5 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
            sleep 0.3
        fi
        # nudge 送信
        if ! timeout 5 tmux send-keys -t "$PANE_TARGET" "$nudge" 2>/dev/null; then
            echo "[$(date)] WARNING: send-keys nudge failed for $AGENT_ID (attempt $((attempt+1)))" >&2
            attempt=$((attempt+1))
            continue
        fi
        sleep 0.3
        timeout 5 tmux send-keys -t "$PANE_TARGET" Enter 2>/dev/null || true
        sleep 0.5
        # 送信確認。
        # ★codex 路 (工区1 ⒝①)★: 判定を composer 行 ただ一行に閉じる。
        #   旧 `capture | tail -5 | grep -qF "$nudge"` は ★会話面着弾★ と
        #   ★composer 残骸★ を区別できず、着弾成功を「失敗」と誤読して再送 →
        #   二重配送 + 無条件 C-u で draft 破壊、を招いていた。
        # ★claude 路★: 従来の判定を一字も変えぬ (稼働中 9本の watcher を壊さぬ為)。
        if [[ "$effective_cli_for_nudge" == "codex" ]]; then
            codex_residue_cleanup "$nudge" || true
            if [ "$CODEX_RESIDUE_STATE" = "not_landed" ]; then
                # composer が nudge を抱えたまま = Enter が効いて居らぬ → 再送
                echo "[$(date)] WARNING: codex nudge not landed (composer still holds it), retrying (attempt $((attempt+1)))" >&2
                attempt=$((attempt+1))
                continue
            fi
            if [ "$CODEX_RESIDUE_STATE" != "cleaned" ]; then
                # composer_mismatch / no_composer = ★他者の入力が在る かも知れぬ★。
                # 触れず・再送もせず (retry cap 内で終端、watcher-design 原則①)。
                echo "[$(date)] [RESIDUE] codex composer untouched for $AGENT_ID (state=$CODEX_RESIDUE_STATE)" >&2
            fi
        else
            local pane_content
            pane_content=$(timeout 3 tmux capture-pane -t "$PANE_TARGET" -p 2>/dev/null | tail -5 || echo "")
            if echo "$pane_content" | grep -qF "$nudge"; then
                # nudgeテキストが残存 → 送信失敗 → C-u クリアしてリトライ
                echo "[$(date)] WARNING: nudge text still visible in pane, retrying (attempt $((attempt+1)))" >&2
                timeout 5 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
                sleep 0.3
                attempt=$((attempt+1))
                continue
            fi
        fi
        # 送信成功
        # NOTE: アイドルフラグは削除しない。nudge送信≠エージェント起動確認。
        # フラグを消すと agent_is_busy()=true → 以降のnudge全スキップ → デッドロック。
        # フラグはエージェントが実際に作業開始した時に自然消滅する（stop_hook設計と整合）。
        record_nudge_fingerprint "$unread_count"
        echo "[$(date)] Wake-up sent to $AGENT_ID (${unread_count} unread, attempt $((attempt+1)))" >&2
        return 0
    done
    echo "[$(date)] WARNING: send-keys failed after $max_retries retries for $AGENT_ID" >&2
    return 0  # Never return 1 — set -euo pipefail would kill the watcher daemon
}

# ─── Send wake-up nudge with Escape prefix ───
# Phase 2 escalation: send Escape×2 + C-c to clear stuck input, then nudge.
# Addresses the "echo last tool call" cursor position bug and stale input.
send_wakeup_with_escape() {
    local unread_count="$1"
    local nudge="inbox${unread_count}"
    local effective_cli
    effective_cli=$(get_effective_cli_type)
    local c_ctrl_state="skipped"

    # Safety: never send Escape escalation to shogun. It can wipe the Lord's input.
    if [ "$AGENT_ID" = "shogun" ]; then
        echo "[$(date)] [SKIP] shogun: suppressing Escape escalation; sending plain nudge" >&2
        send_wakeup "$unread_count"
        return 0
    fi

    # Codex CLI: ESC は「中断」になりやすく、人間操作中の事故も多い。
    # Phase 2 の Escape エスカレーションは無効化し、通常 nudge のみに落とす。
    if [[ "$effective_cli" == "codex" ]]; then
        echo "[$(date)] [SKIP] codex: suppressing Escape escalation for $AGENT_ID; sending plain nudge" >&2
        send_wakeup "$unread_count"
        return 0
    fi

    # Claude Code: Stop hookがturn終了時にinbox未読を検出→自動処理する。
    # Escape送信は処理中のturnを中断させるため有害。Phase 2は通常nudgeに落とす。
    if [[ "$effective_cli" == "claude" ]]; then
        echo "[$(date)] [SKIP] claude: suppressing Escape escalation for $AGENT_ID (Stop hook handles delivery); sending plain nudge" >&2
        send_wakeup "$unread_count"
        return 0
    fi

    if [ "${FINAL_ESCALATION_ONLY:-0}" = "1" ]; then
        echo "[$(date)] [SKIP] FINAL_ESCALATION_ONLY=1, suppressing phase2 nudge for $AGENT_ID" >&2
        return 0
    fi

    if agent_has_self_watch; then
        return 0
    fi

    # Phase 2 still skips if agent is busy — Escape during Working would interrupt
    if agent_is_busy; then
        echo "[$(date)] [SKIP] Agent $AGENT_ID is busy (Working), deferring Phase 2 nudge" >&2
        return 0
    fi

    echo "[$(date)] [SEND-KEYS] ESCALATION Phase 2: Escape×2 + nudge for $AGENT_ID (cli=$effective_cli)" >&2
    # Escape×2 to exit any mode
    timeout 5 tmux send-keys -t "$PANE_TARGET" Escape Escape 2>/dev/null || true
    sleep 0.5
    # C-c to clear stale input (but Codex CLI terminates on C-c when idle, so skip it)
    if [[ "$effective_cli" != "codex" ]]; then
        timeout 5 tmux send-keys -t "$PANE_TARGET" C-c 2>/dev/null || true
        sleep 0.5
        c_ctrl_state="sent"
    fi
    if timeout 5 tmux send-keys -t "$PANE_TARGET" "$nudge" 2>/dev/null; then
        sleep 0.3
        timeout 5 tmux send-keys -t "$PANE_TARGET" Enter 2>/dev/null || true
        echo "[$(date)] Escape+nudge sent to $AGENT_ID (${unread_count} unread, cli=$effective_cli, C-c=$c_ctrl_state)" >&2
        return 0
    fi

    echo "[$(date)] WARNING: send-keys failed for Escape+nudge ($AGENT_ID)" >&2
    return 0  # Never return 1 — set -euo pipefail would kill the watcher daemon
}

# ─── Process cycle ───
process_unread() {
    local trigger="${1:-event}"

    # summary-first: unread_count fast-path (Phase 2/3 optimization)
    # unread_count fast-path lets us skip expensive full reads when idle.
    local fast_info
    fast_info=$(get_unread_count_fast)
    local fast_count
    fast_count=$(echo "$fast_info" | "$SCRIPT_DIR/.venv/bin/python3" -c "import sys,json; print(json.load(sys.stdin).get('count',0))" 2>/dev/null)

    if no_idle_full_read "$trigger" && [ "$fast_count" -eq 0 ] 2>/dev/null; then
        # no_idle_full_read guard: unread=0 and timeout path → no full inbox read
        if [ "$FIRST_UNREAD_SEEN" -ne 0 ]; then
            echo "[$(date)] All messages read for $AGENT_ID — escalation reset (fast-path)" >&2
        fi
        FIRST_UNREAD_SEEN=0
        NEW_CONTEXT_SENT=0
        # Ensure idle flag exists (fast-path recovery)
        touch "${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}" 2>/dev/null || true
        if ! agent_is_busy; then
            # 信長: only clear input when pane is not active (Lord is away)
            if [ "$AGENT_ID" = "shogun" ] && pane_is_active; then
                : # Lord may be typing — skip C-u
            elif [[ "$(get_effective_cli_type)" == "codex" ]]; then
                # ★令25 ⑴ 望む結末㈠ を此処へも及ぼす★ (足軽2号の裁量拡張・票 §3-5 に明示):
                #   本 C-u は「送信前」に非ず「idle 時の掃除」なれど、
                #   撃つ物は同じ C-u ＝ ★書きかけを一字残らず消す★ 事も同じに御座る。
                #   agent_is_busy=false は「手が空いておる」だけで
                #   「composer が空」の意に非ず (実測: hermes-honbucho は idle にして draft 保持)。
                #   ∴ 門を通し、空の時のみ撃つ。空なら C-u は無害な空撃ちゆえ実質「撃たぬ」。
                #   codex の残骸掃除は codex_residue_cleanup が別途担う ∴ 掃除力は落ちぬ。
                if codex_presend_gate "" "$PANE_TARGET"; then
                    timeout 2 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
                fi
            else
                timeout 2 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
            fi
        fi
        return 0
    fi

    local info
    info=$(get_unread_info)

    local read_bytes=0
    if [ -f "$INBOX" ]; then
        read_bytes=$(wc -c < "$INBOX" 2>/dev/null || echo 0)
    fi
    update_metrics "${read_bytes:-0}"

    # Handle special CLI commands first (/clear, /model)
    local specials
    specials=$(echo "$info" | "$SCRIPT_DIR/.venv/bin/python3" -c "
import sys, json
data = json.load(sys.stdin)
for s in data.get('specials', []):
    mid = s.get('id', '') or ''
    frm = s.get('from', '') or ''
    t = s.get('type', '')
    c = (s.get('content', '') or '').replace('\t', ' ').replace('\n', ' ').strip()
    print(f'{mid}\t{frm}\t{t}\t{c}')
" 2>/dev/null)

    local clear_seen=0
    local clear_sent=0  # tracks if /clear was actually sent (not just seen)
    if [ -n "$specials" ]; then
        local msg_id msg_from msg_type msg_content cmd
        while IFS=$'\t' read -r msg_id msg_from msg_type msg_content; do
            [ -n "$msg_type" ] || continue
            if [ "$msg_type" = "clear_command" ]; then
                clear_seen=1
                if is_no_auto_clear_agent; then
                    # W201: persistent suppression state, not a one-shot failure —
                    # left unread so it is naturally retried once the state clears
                    # (previously this branch inherited the eager read=True mark
                    # from get_unread_info() and silently dropped the message).
                    echo "[$(date)] [SKIP] $AGENT_ID: suppressing clear_command during SecondPC role recovery (id=${msg_id}, left unread)" >&2
                    continue
                fi
                # Busy guard: skip /clear if agent is currently processing.
                # Sending /clear during active work destroys in-progress context.
                # W201 root-cause cure (発注②): intentionally left unread here —
                # "deferred to next cycle" must actually mean the next cycle's
                # get_unread_info() sees it again, not that it was already
                # consumed and will never be seen again.
                if agent_is_busy && [[ "$AGENT_ID" != "shogun" ]]; then
                    echo "[$(date)] [SKIP] Agent $AGENT_ID is busy — /clear (clear_command) deferred to next cycle (id=${msg_id}, left unread)" >&2
                    continue
                fi
            fi
            cmd=$(normalize_special_command "$msg_type" "$msg_content")
            if [ -n "$cmd" ]; then
                local send_rc=0
                send_cli_command "$cmd" || send_rc=$?
                if [ "$send_rc" -eq 0 ]; then
                    mark_message_processed "$msg_id"
                    [ "$msg_type" = "clear_command" ] && clear_sent=1
                elif [ "$send_rc" -eq 2 ]; then
                    # Busy-defer (W205): left unread, no notification — this
                    # is routine, not a failure. Retried next cycle.
                    echo "[$(date)] [SKIP] $AGENT_ID: ${msg_type} (id=${msg_id}) deferred — agent busy, left unread" >&2
                else
                    return_message_to_sender "$msg_id" "$msg_from" "$msg_type" "send_cli_command failed (rc=${send_rc})"
                fi
            else
                return_message_to_sender "$msg_id" "$msg_from" "$msg_type" "normalize_special_command produced empty command (unrecognized type/content)"
            fi
        done <<< "$specials"
    fi

    # /clear は Codex で /new へ変換される。再起動直後の取りこぼし防止として
    # 追加 task_assigned を自動投入し、次サイクルで確実に wake-up 可能にする。
    # 案B+待機: 家老 がタスク YAML を cancelled に更新するまでの猶予を確保してから
    # status チェックを行い、cancelled/idle の場合はスキップする。
    # clear_sent（実際に送信）のみauto-recoveryを起動。busy時スキップは対象外。
    if [ "$clear_sent" -eq 1 ]; then
        # Wait for 家老 to update task YAML status (cancellation race condition mitigation).
        # send_cli_command already slept 3s for /clear; add 5s more = ~8s total before check.
        sleep 5
        local recovery_id
        recovery_id=$(enqueue_recovery_task_assigned)
        if [[ "$recovery_id" == SKIP_CANCELLED:* ]]; then
            echo "[$(date)] [AUTO-RECOVERY] skipped for $AGENT_ID — task is ${recovery_id#SKIP_CANCELLED:} (not restarting)" >&2
        elif [ -n "$recovery_id" ] && [ "$recovery_id" != "SKIP_DUPLICATE" ] && [ "$recovery_id" != "ERROR" ]; then
            echo "[$(date)] [AUTO-RECOVERY] queued task_assigned for $AGENT_ID ($recovery_id)" >&2
        fi
        info=$(get_unread_info)
        # CRITICAL FIX: After clear_command + /clear, reset cooldown and send immediate nudge.
        # Without this, agent sits at empty prompt with no idea it has inbox messages.
        LAST_CLEAR_TS=0
        LAST_NUDGE_TS=0
        LAST_NUDGE_COUNT=""
    fi

    # Send wake-up nudge for normal messages (with escalation)
    local normal_count
    normal_count=$(echo "$info" | "$SCRIPT_DIR/.venv/bin/python3" -c "import sys,json; print(json.load(sys.stdin).get('count',0))" 2>/dev/null)

    # Check if unread messages include task_assigned (for context reset)
    local has_task_assigned
    has_task_assigned=$(echo "$info" | "$SCRIPT_DIR/.venv/bin/python3" -c "import sys,json; print(1 if json.load(sys.stdin).get('has_task_assigned') else 0)" 2>/dev/null)

    if [ "$normal_count" -gt 0 ] 2>/dev/null; then
        local now
        now=$(date +%s)

        # When the agent is busy/thinking, do NOT escalate. Interrupting with Escape or /clear
        # can terminate the current thought. Also pause the escalation timer while busy so we
        # don't immediately jump to Phase 2/3 once it becomes idle.
        # Exception: shogun — ntfy must be delivered immediately.
        # Safety net: if busy detection persists for >5 min, assume false-busy (stale flag)
        # and force-create idle flag to allow nudge delivery.
        # 副院長令 fc3a5b0b RC-2 cure (2026-06-07): shogun 例外も前方一致化 (shogun-third/main/second)。
        if agent_is_busy && [[ "$AGENT_ID" != shogun* ]]; then
            local busy_cli
            busy_cli=$(get_effective_cli_type)
            # Stale busy safety net: if agent has been "busy" for >5 minutes with
            # unread messages, force-create idle flag. This recovers from false-busy
            # deadlock where stop_hook failed to create the flag.
            local stale_busy_limit=300  # 5 minutes
            if [ "${FIRST_UNREAD_SEEN:-0}" -gt 0 ] && [ "$((now - FIRST_UNREAD_SEEN))" -ge "$stale_busy_limit" ]; then
                echo "[$(date)] WARNING: $AGENT_ID busy for $((now - FIRST_UNREAD_SEEN))s with $normal_count unread — forcing idle flag (stale busy recovery)" >&2
                touch "${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}"
                # Fall through to normal nudge/escalation below
            else
                if [[ "$busy_cli" == "claude" ]]; then
                    # Claude Code: Stop hook will catch unread messages when the agent's
                    # turn ends. No nudge needed at all — just log and skip completely.
                    # Set FIRST_UNREAD_SEEN so the stale-busy safety net (above) can
                    # activate if the stop hook never fires.
                    if [ "${FIRST_UNREAD_SEEN:-0}" -eq 0 ]; then
                        FIRST_UNREAD_SEEN=$now
                    fi
                    echo "[$(date)] $normal_count unread for $AGENT_ID but agent is busy (claude) — Stop hook will deliver" >&2
                else
                    # Codex/Copilot/Kimi: No Stop hook. Pause escalation timer while busy.
                    FIRST_UNREAD_SEEN=$now
                    echo "[$(date)] $normal_count unread for $AGENT_ID but agent is busy ($busy_cli) — pausing escalation timer" >&2
                fi
                return 0
            fi
        fi

        # ─── Context reset before new task ───
        # Send /new or /clear once when task_assigned is first detected,
        # to clear stale context from the previous task.
        # Skip if: (1) already sent this batch, (2) clear_command already handled above,
        #          (3) agent is shogun (human-controlled).
        if [ "$has_task_assigned" = "1" ] && [ "$NEW_CONTEXT_SENT" -eq 0 ] && [ "$clear_seen" -eq 0 ]; then
            # 副院長令 fc3a5b0b: send_context_reset の return code を 3 系統で評価。
            # 0=送信完了 or command-layer guard skip → 通常 post-reset nudge
            # 1=busy defer (未送信) → NEW_CONTEXT_SENT 立てず次 cycle で retry
            # 2=送信済だが 15s 経っても busy → NEW_CONTEXT_SENT=1 立てて nudge skip (Stop hook 配送)
            send_context_reset
            local reset_rc=$?
            case "$reset_rc" in
                0)
                    NEW_CONTEXT_SENT=1
                    # CRITICAL FIX: After /clear, agent has fresh context and is at prompt.
                    # It does NOT know about inbox — must send nudge immediately.
                    # Reset throttle state so the nudge is not suppressed.
                    LAST_NUDGE_TS=0
                    LAST_NUDGE_COUNT=""
                    # Reset /clear cooldown so agent_is_busy() returns false for the nudge.
                    # send_context_reset() already waited for agent to become idle (15s max).
                    LAST_CLEAR_TS=0
                    # Send immediate nudge (agent needs this to start CLAUDE.md recovery)
                    echo "[$(date)] [POST-RESET] Sending immediate post-reset nudge to $AGENT_ID" >&2
                    send_wakeup "$normal_count"
                    FIRST_UNREAD_SEEN=$now
                    ;;
                1)
                    # busy defer — retry next cycle, do NOT mark NEW_CONTEXT_SENT
                    echo "[$(date)] [POST-RESET] $AGENT_ID: context reset deferred (busy) — retry next cycle (fc3a5b0b RC-1)" >&2
                    FIRST_UNREAD_SEEN=$now
                    ;;
                2)
                    # reset sent but agent still busy after 15s — skip nudge
                    NEW_CONTEXT_SENT=1
                    echo "[$(date)] [POST-RESET] $AGENT_ID: reset sent but still busy — Stop hook will deliver nudge (fc3a5b0b)" >&2
                    FIRST_UNREAD_SEEN=$now
                    ;;
            esac
            return 0
        fi

        # If startup prompt was just sent (Codex), skip follow-up nudge this cycle.
        # The prompt itself contains full recovery instructions (identify + read YAML + work).
        if [ "$STARTUP_PROMPT_SENT" -eq 1 ]; then
            STARTUP_PROMPT_SENT=0
            echo "[$(date)] [SKIP] Startup prompt just sent to $AGENT_ID — skipping nudge this cycle" >&2
            FIRST_UNREAD_SEEN=$now
            return 0
        fi

        # Track when we first saw unread messages
        if [ "$FIRST_UNREAD_SEEN" -eq 0 ]; then
            FIRST_UNREAD_SEEN=$now
        fi

        if [ "${ASW_DISABLE_ESCALATION:-0}" = "1" ]; then
            echo "[$(date)] $normal_count unread for $AGENT_ID (escalation disabled)" >&2
            if disable_normal_nudge; then
                echo "[$(date)] [SKIP] disable_normal_nudge=1, no normal nudge for $AGENT_ID" >&2
            else
                send_wakeup "$normal_count"
            fi
            return 0
        fi

        local age=$((now - FIRST_UNREAD_SEEN))

        if [ "$age" -lt "$ESCALATE_PHASE1" ]; then
            # Phase 1 (0-2 min): Standard nudge
            echo "[$(date)] $normal_count unread for $AGENT_ID (${age}s)" >&2
            if disable_normal_nudge; then
                echo "[$(date)] [SKIP] disable_normal_nudge=1, deferring to escalation-only path" >&2
            else
                send_wakeup "$normal_count"
            fi
        elif [ "$age" -lt "$ESCALATE_PHASE2" ]; then
            # Phase 2 (2-4 min): Escape + nudge
            echo "[$(date)] $normal_count unread for $AGENT_ID (${age}s — escalating: Escape+nudge)" >&2
            send_wakeup_with_escape "$normal_count"
        else
            # Phase 3 (4+ min): /clear (throttled to once per 5 min)
            if [ "$LAST_CLEAR_TS" -lt "$((now - ESCALATE_COOLDOWN))" ]; then
                local effective_cli
                effective_cli=$(get_effective_cli_type)
                if [[ "$effective_cli" == "codex" ]]; then
                    # Codex /clear -> /new は会話を切ってしまうため、安全側に倒す。
                    echo "[$(date)] ESCALATION Phase 3: $AGENT_ID unresponsive for ${age}s, but cli=codex — skipping /clear." >&2
                    FIRST_UNREAD_SEEN=$now  # Reset timer (no destructive action)
                    send_wakeup "$normal_count"
                elif [[ "$AGENT_ID" == "shogun" || "$AGENT_ID" == shogun-* || "$AGENT_ID" == "karo" || "$AGENT_ID" == karo-* || "$AGENT_ID" == "gunshi" || "$AGENT_ID" == gunshi-* ]]; then
                    # Command-layer agents (karo/gunshi/shogun, including PC-qualified ids): suppress /clear even in Phase 3
                    echo "[$(date)] [SKIP] ESCALATION Phase 3: $AGENT_ID suppressed (command-layer agent, ${age}s). Using Escape+nudge." >&2
                    FIRST_UNREAD_SEEN=$now  # Reset timer
                    send_wakeup_with_escape "$normal_count"
                else
                    echo "[$(date)] ESCALATION Phase 3: Agent $AGENT_ID unresponsive for ${age}s. Sending /clear." >&2
                    send_cli_command "/clear"
                    LAST_CLEAR_TS=$now
                    FIRST_UNREAD_SEEN=0  # Reset — will re-detect on next cycle
                    NEW_CONTEXT_SENT=0
                fi
            else
                # Cooldown active — fall back to Escape+nudge
                echo "[$(date)] $normal_count unread for $AGENT_ID (${age}s — /clear cooldown, using Escape+nudge)" >&2
                send_wakeup_with_escape "$normal_count"
            fi
        fi
    else
        # No unread messages — reset escalation tracker
        if [ "$FIRST_UNREAD_SEEN" -ne 0 ]; then
            echo "[$(date)] All messages read for $AGENT_ID — escalation reset" >&2
        fi
        FIRST_UNREAD_SEEN=0
        NEW_CONTEXT_SENT=0
        # Ensure idle flag exists when all messages are read.
        # Recovers from stop_hook_inbox.sh flag loss during block cycles.
        touch "${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}" 2>/dev/null || true
        # Clear stale nudge text from input field (Codex CLI prefills last input on idle).
        # Only send C-u when agent is idle — during Working it would be disruptive.
        if ! agent_is_busy; then
            # 信長: only clear input when pane is not active (Lord is away)
            if [ "$AGENT_ID" = "shogun" ] && pane_is_active; then
                : # Lord may be typing — skip C-u
            elif [[ "$(get_effective_cli_type)" == "codex" ]]; then
                # ★令25 ⑴ 望む結末㈠ を此処へも及ぼす★ (足軽2号の裁量拡張・票 §3-5 に明示):
                #   本 C-u は「送信前」に非ず「idle 時の掃除」なれど、
                #   撃つ物は同じ C-u ＝ ★書きかけを一字残らず消す★ 事も同じに御座る。
                #   agent_is_busy=false は「手が空いておる」だけで
                #   「composer が空」の意に非ず (実測: hermes-honbucho は idle にして draft 保持)。
                #   ∴ 門を通し、空の時のみ撃つ。空なら C-u は無害な空撃ちゆえ実質「撃たぬ」。
                #   codex の残骸掃除は codex_residue_cleanup が別途担う ∴ 掃除力は落ちぬ。
                if codex_presend_gate "" "$PANE_TARGET"; then
                    timeout 2 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
                fi
            else
                timeout 2 tmux send-keys -t "$PANE_TARGET" C-u 2>/dev/null || true
            fi
        fi
    fi
}

process_unread_once() {
    process_unread "startup"
}

# ─── Startup & Main loop (skipped in testing mode) ───
if [ "${__INBOX_WATCHER_TESTING__:-}" != "1" ]; then

# ─── Startup: process any existing unread messages ───
process_unread_once

# ─── Main loop: event-driven via inotifywait ───
# Timeout 30s: WSL2 /mnt/c/ can miss inotify events.
# Shorter timeout = faster escalation retry for stuck agents.
INOTIFY_TIMEOUT="${INOTIFY_TIMEOUT:-30}"

# Manual disable flags (Watcher Design Principles 必須項目)
GLOBAL_DISABLE_FLAG="$HOME/.openclaw/global_disable"
WATCHER_DISABLE_FLAG="$HOME/.openclaw/disable_inbox_watcher_${AGENT_ID}"

while true; do
    # Manual disable flag check (Watcher Design Principles 必須項目)
    if [ -f "$GLOBAL_DISABLE_FLAG" ] || [ -f "$WATCHER_DISABLE_FLAG" ]; then
        echo "[$(date)] inbox_watcher[$AGENT_ID] DISABLED by flag file — exiting gracefully" >&2
        exit 0
    fi

    # Block until file is modified OR timeout
    # Backend-specific file watching: inotifywait (Linux) or fswatch (macOS)
    set +e
    if [ "${WATCH_BACKEND:-inotifywait}" = "fswatch" ]; then
        # macOS: fswatch -1 exits after one event. Use timeout for safety net.
        # gtimeout (from coreutils) or perl fallback for macOS timeout
        if command -v gtimeout &>/dev/null; then
            gtimeout "$INOTIFY_TIMEOUT" fswatch -1 --event Updated --event Renamed "$INBOX" 2>/dev/null
            rc=$?
            # gtimeout returns 124 on timeout
            if [ "$rc" -eq 124 ]; then rc=2; else rc=0; fi
        else
            # Fallback: use background fswatch + sleep timeout
            fswatch -1 --event Updated --event Renamed "$INBOX" &>/dev/null &
            FSWATCH_PID=$!
            WAITED=0
            while [ "$WAITED" -lt "$INOTIFY_TIMEOUT" ] && kill -0 "$FSWATCH_PID" 2>/dev/null; do
                sleep 2
                WAITED=$((WAITED + 1))
            done
            if kill -0 "$FSWATCH_PID" 2>/dev/null; then
                kill "$FSWATCH_PID" 2>/dev/null
                wait "$FSWATCH_PID" 2>/dev/null
                rc=2  # timeout
            else
                wait "$FSWATCH_PID" 2>/dev/null
                rc=0  # event
            fi
        fi
    else
        # Linux: inotifywait (original behavior)
        inotifywait -q -t "$INOTIFY_TIMEOUT" -e modify -e close_write "$INBOX" 2>/dev/null
        rc=$?
    fi
    set -e

    # rc=0: event fired (instant delivery)
    # rc=1: watch invalidated — Claude Code uses atomic write (tmp+rename),
    #        which replaces the inode. inotifywait sees DELETE_SELF → rc=1.
    #        File still exists with new inode. Treat as event, re-watch next loop.
    # rc=2: timeout (30s safety net for WSL2 inotify gaps / macOS fswatch timeout)
    # All cases: check for unread, then loop back (re-watches new inode)
    sleep 0.3

    # Daemon resilience (2026-06-02 ee4d6ce4 Step0 death-restart root-cure):
    # process_unread runs under `set -euo pipefail`. Any unguarded command that
    # returns non-zero (e.g. a grep with no match in a pipeline → pipefail) would
    # otherwise kill the whole watcher daemon, causing the observed ~40s
    # death-restart loop. Guard with `|| true` so a single bad cycle never
    # terminates the long-lived loop. Errors still surface via stderr logs.
    if [ "$rc" -eq 2 ]; then
        if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then
            process_unread "timeout" || true
        fi
    else
        process_unread "event" || true
    fi

    # Token 飽和警告機構 (2026-05-07 制定):
    # claude pane に「/clear to save XXXk tokens」が表示されたら、
    # 200k 超の場合に agent の inbox に context size 警告を送付する。
    # 自動 /clear はせず、agent 自身の判断に委ねる (= 進捗ロスト防止)。
    # 重複送付防止のため LAST_TOKEN_WARN_TS で 30 分間隔に制限。
    if [[ "$CLI_TYPE" == "claude" ]] && [[ "$AGENT_ID" != "shogun" ]]; then
        _now_token=$(date +%s)
        _token_warn_cooldown=1800  # 30 min
        if [ "$((_now_token - ${LAST_TOKEN_WARN_TS:-0}))" -gt "$_token_warn_cooldown" ]; then
            _pane_text=$(timeout 3 tmux capture-pane -t "$PANE_TARGET" -p 2>/dev/null | tail -5 || echo "")
            # `|| true`: under `set -o pipefail`, a no-match grep returns 1 and would
            # kill the daemon via `set -e` (ee4d6ce4 Step0 death-restart root-cure).
            _token_match=$(echo "$_pane_text" | grep -oE '[0-9]+(\.[0-9]+)?k tokens' | head -1 || true)
            if [ -n "$_token_match" ]; then
                _token_num=$(echo "$_token_match" | grep -oE '[0-9]+(\.[0-9]+)?' || true)
                _token_int=${_token_num%.*}
                if [ "${_token_int:-0}" -ge 200 ]; then
                    echo "[$(date)] [TOKEN-WARN] $AGENT_ID context size ${_token_match} (>= 200k) — sending warning to inbox" >&2
                    bash "$SCRIPT_DIR/scripts/inbox_write.sh" "$AGENT_ID" \
                        "【context size 警告】貴殿の claude session は ${_token_match} 消費中。200k 超で減速の可能性。区切りの良い所で /clear で context リセット推奨 (進捗 commit 後)。" \
                        notification shogun 2>/dev/null || true
                    LAST_TOKEN_WARN_TS=$_now_token
                fi
            fi
        fi
    fi
done

fi  # end testing guard

# Source shared agent status library outside the testing guard so that
# agent_is_busy_check() is available in test mode too.
# In normal mode it was already sourced above; double-sourcing is harmless.
_agent_status_lib="${SCRIPT_DIR}/lib/agent_status.sh"
if [ -f "$_agent_status_lib" ] && ! type agent_is_busy_check &>/dev/null; then
    source "$_agent_status_lib"
fi

# ═══════════════════════════════════════════════════════════════
# 段階3 全自動ループ化 — detect_stale lib 化 reference (redo_002 RED-1 cure)
# ═══════════════════════════════════════════════════════════════
# redo: subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_002
#   gunshi-third governing RED-1 真因: 関数群が main loop (L1320 while true) の後ろに置かれ
#   通常実行で永久未到達 dead code、かつ CLI dispatcher が comment のみで実 code 不在。
#   ↓
#   cure: 関数群を scripts/lib/detect_stale.sh へ分離 (runtime 到達可能化) + CLI entrypoint
#         scripts/fukuincho_detect_stale_cli.sh を新規作成 (arg dispatch 実 code 化、RED-1)。
#         path traversal 防御は lib 側で corr_id sanitize (basename + regex、RED-2 cure)。
#
# ★絶対前提★: 本 reference は inbox_watcher.sh の既存 main loop (L1-L1411) と完全独立。
#              止血B (commit e0e98b7) 該当 line range (L625-639/L1138/L1174-1207/L1259-1264)
#              prefix-match guard + busy defer の挙動には ★一切触接しない★。
#
# 関数群正本: scripts/lib/detect_stale.sh
#   - detect_stale_evaluate_row()  trigger 候補評価 (status enum + 認可 + corr_id sanitize + in-flight)
#   - detect_stale_enqueue()       層③ omni engine 呼出 (correlation_id 継承)
#   - _detect_stale_sanitize_corr_id()  RED-2 cure (path traversal 防御)
# CLI 正本: scripts/fukuincho_detect_stale_cli.sh
#   - `bash scripts/fukuincho_detect_stale_cli.sh --detect-stale-handshake [--input <file>]`
#   - cron 60s polling から invoke される (設計 §2 (1)-(4) verbatim)
# ═══════════════════════════════════════════════════════════════
