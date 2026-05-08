#!/usr/bin/env bash
# scripts/message_delivery_v2/watcher.sh — 新 watcher (Phase 2 cycle2 配達本体)
#
# Phase 0 反省点 a/b/i (= silent death / inotifywait timeout / heartbeat 不在)
# + cycle2 反省点 c/g/h/n/o/p/w/x (= safe_nudge / dedup / dead_letter / pane_drift / self_send / Codex submit / ESCALATION 暴発) への対応。
#
# 単一 agent の inbox を inotifywait で監視、新規 msg 検知 → safe_nudge 発火。
# 1-2 時間で自然交代 (= memory leak 回避)、heartbeat 60 秒間隔。
#
# Usage:
#   bash scripts/message_delivery_v2/watcher.sh <agent_id> <pane_target> <cli_type>
#
# 設計: docs/message_delivery_v2_design_2026-05-08.md §2.2

set -euo pipefail

# ──────────────────────────────────────────────────────────────────
# 引数 + 環境準備
# ──────────────────────────────────────────────────────────────────
if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <agent_id> <pane_target> <cli_type>" >&2
    exit 1
fi
AGENT_ID="$1"
PANE_TARGET="$2"
CLI_TYPE="$3"

_WATCHER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_WATCHER_PROJECT_ROOT="$(cd "${_WATCHER_DIR}/../.." && pwd)"
cd "${_WATCHER_PROJECT_ROOT}"

source "${_WATCHER_PROJECT_ROOT}/scripts/lib/inbox_path.sh"
source "${_WATCHER_PROJECT_ROOT}/scripts/message_delivery_v2/heartbeat.sh"
source "${_WATCHER_PROJECT_ROOT}/scripts/message_delivery_v2/dedup.sh"
source "${_WATCHER_PROJECT_ROOT}/scripts/message_delivery_v2/dead_letter.sh"

export AGENT_ID
export WATCHER_PID=$$
WATCHER_STARTED_AT=$(date -Iseconds)
export WATCHER_STARTED_AT
export TUI_CAPTURE_STATE="unknown"
export READY_FOR_CLEAR="true"
export READY_FOR_DISPATCH="true"

LOG_DIR="${_WATCHER_PROJECT_ROOT}/logs/message_delivery_v2"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/watcher_${AGENT_ID}_$(date +%Y%m%d).log"

GLOBAL_DISABLE="${HOME}/.openclaw/global_disable"
WATCHER_DISABLE="${HOME}/.openclaw/disable_watcher_${AGENT_ID}"
NATURAL_ROTATION_SEC=5400

INBOX_PATH=$(get_inbox_path "$AGENT_ID")

# ──────────────────────────────────────────────────────────────────
# 関数定義 (= main loop より前で全件定義、bash 逐次解釈順守)
# ──────────────────────────────────────────────────────────────────

log_json() {
    local level="$1"
    local msg="$2"
    shift 2
    local extra="${*:-}"
    local ts
    ts=$(date -Iseconds)
    printf '{"ts":"%s","level":"%s","agent":"%s","pid":%d,"msg":"%s","extra":"%s"}\n' \
        "$ts" "$level" "$AGENT_ID" "$WATCHER_PID" "$msg" "$extra" >> "$LOG_FILE"
}

cleanup() {
    log_json INFO "watcher_exit" "reason=signal"
    kill "${HEARTBEAT_LOOP_PID:-0}" 2>/dev/null || true
    exit 0
}

check_natural_rotation() {
    local now_epoch started_epoch uptime
    now_epoch=$(date +%s)
    started_epoch=$(date -d "$WATCHER_STARTED_AT" +%s)
    uptime=$((now_epoch - started_epoch))
    if [[ $uptime -ge $NATURAL_ROTATION_SEC ]]; then
        log_json INFO "natural_rotation" "uptime_sec=${uptime}"
        write_heartbeat "$AGENT_ID" "natural_rotation_exit"
        kill "${HEARTBEAT_LOOP_PID:-0}" 2>/dev/null || true
        exit 0
    fi
}

check_disable_flag() {
    if [[ -f "$GLOBAL_DISABLE" ]]; then
        log_json INFO "global_disable_active" "flag=${GLOBAL_DISABLE}"
        write_heartbeat "$AGENT_ID" "disabled_global"
        kill "${HEARTBEAT_LOOP_PID:-0}" 2>/dev/null || true
        exit 0
    fi
    if [[ -f "$WATCHER_DISABLE" ]]; then
        log_json INFO "watcher_disable_active" "flag=${WATCHER_DISABLE}"
        write_heartbeat "$AGENT_ID" "disabled_specific"
        kill "${HEARTBEAT_LOOP_PID:-0}" 2>/dev/null || true
        exit 0
    fi
}

# mark_msg_read <msg_id> <ack_by>
mark_msg_read() {
    local msg_id="$1"
    local ack_by="$2"
    python3 <<PYEOF
import yaml
try:
    with open("${INBOX_PATH}") as f:
        d = yaml.safe_load(f) or {}
    for m in d.get('messages', []):
        if m.get('id') == "${msg_id}" and not m.get('read', False):
            m['read'] = True
            m['acknowledged_by'] = "${ack_by}"
            m['delivery_state'] = "delivered" if "${ack_by}" == "delivered" else "closed"
    with open("${INBOX_PATH}", 'w') as f:
        yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False, width=10000)
except Exception:
    pass
PYEOF
}

# process_unread_messages — inbox の unread msg を順次処理
process_unread_messages() {
    local unread_msgs
    unread_msgs=$(python3 <<PYEOF
import yaml, json
try:
    with open("${INBOX_PATH}") as f:
        d = yaml.safe_load(f) or {}
    out = []
    for m in d.get('messages', []):
        if m.get('read', False):
            continue
        out.append({
            'id': m.get('id', ''),
            'from': m.get('from', ''),
            'to': m.get('to', '${AGENT_ID}'),
            'type': m.get('type', ''),
            'corr_id': m.get('correlation_id', ''),
        })
    print(json.dumps(out))
except Exception:
    print('[]')
PYEOF
)

    local unread_count
    unread_count=$(echo "$unread_msgs" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")

    log_json INFO "inbox_event" "unread_count=${unread_count}"
    LAST_ACTION="inbox_event_unread_${unread_count}"
    export LAST_ACTION

    if [[ "$unread_count" == "0" ]]; then
        return 0
    fi

    local idx=0
    while [[ $idx -lt $unread_count ]]; do
        local msg_id from_agent corr_id
        msg_id=$(echo "$unread_msgs" | python3 -c "import json,sys; print(json.load(sys.stdin)[${idx}]['id'])")
        from_agent=$(echo "$unread_msgs" | python3 -c "import json,sys; print(json.load(sys.stdin)[${idx}]['from'])")
        corr_id=$(echo "$unread_msgs" | python3 -c "import json,sys; print(json.load(sys.stdin)[${idx}]['corr_id'])")

        # self-send 即 ack (= 反省点 p)
        if [[ "$from_agent" == "$AGENT_ID" ]]; then
            log_json INFO "self_send_ack" "msg_id=${msg_id}"
            mark_msg_read "$msg_id" "self_send"
            idx=$((idx + 1))
            continue
        fi

        # dedup check (= 反省点 g)
        if dedup_already_processed "$msg_id"; then
            log_json WARN "duplicate_msg_skip" "msg_id=${msg_id}"
            mark_msg_read "$msg_id" "dedup_skip"
            idx=$((idx + 1))
            continue
        fi

        # retry cap check (= 反省点 h, o)
        if is_over_retry_cap "$AGENT_ID" "$msg_id"; then
            log_json ERROR "retry_cap_exceeded" "msg_id=${msg_id}"
            move_to_dead_letter "$AGENT_ID" "$msg_id" "retry_cap_exceeded"
            mark_msg_read "$msg_id" "dead_lettered"
            idx=$((idx + 1))
            continue
        fi

        # safe_nudge 発火 (= 反省点 c, n, w)
        local nudge_text="inbox${unread_count}"
        local nudge_rc=0
        set +e
        bash "${_WATCHER_PROJECT_ROOT}/scripts/message_delivery_v2/safe_nudge.sh" \
            "$AGENT_ID" "$PANE_TARGET" "$CLI_TYPE" "$nudge_text" "$corr_id" >/dev/null 2>&1
        nudge_rc=$?
        set -e

        case $nudge_rc in
            0)
                log_json INFO "delivered" "msg_id=${msg_id} corr_id=${corr_id}"
                mark_msg_read "$msg_id" "delivered"
                dedup_record "$msg_id" "delivered"
                ;;
            1)
                log_json WARN "queued_cooldown" "msg_id=${msg_id}"
                # 既読化せず次回 retry
                ;;
            2)
                log_json WARN "blocked_interruption_risk" "msg_id=${msg_id}"
                increment_retry "$AGENT_ID" "$msg_id" >/dev/null
                ;;
            3)
                log_json ERROR "pane_drift_detected" "msg_id=${msg_id}"
                move_to_dead_letter "$AGENT_ID" "$msg_id" "pane_drift"
                mark_msg_read "$msg_id" "dead_lettered"
                ;;
            4)
                log_json INFO "book_mode_fallback" "msg_id=${msg_id}"
                increment_retry "$AGENT_ID" "$msg_id" >/dev/null
                ;;
            5)
                log_json CRITICAL "bash_shell_detected" "msg_id=${msg_id} agent_codex_exited"
                move_to_dead_letter "$AGENT_ID" "$msg_id" "bash_shell_codex_exited"
                mark_msg_read "$msg_id" "dead_lettered"
                ;;
            *)
                log_json ERROR "safe_nudge_unknown_rc" "msg_id=${msg_id} rc=${nudge_rc}"
                increment_retry "$AGENT_ID" "$msg_id" >/dev/null
                ;;
        esac

        idx=$((idx + 1))
    done

    # TTL cleanup (= dedup table 24h)
    dedup_cleanup 2>/dev/null || true
}

# ──────────────────────────────────────────────────────────────────
# 起動シーケンス
# ──────────────────────────────────────────────────────────────────

log_json INFO "watcher_start" "pane=${PANE_TARGET} cli=${CLI_TYPE} version=${HEARTBEAT_VERSION:-unknown}"

# inbox path 確認
if [[ ! -f "$INBOX_PATH" ]]; then
    mkdir -p "$(dirname "$INBOX_PATH")"
    printf 'messages: []\n' > "$INBOX_PATH"
    log_json INFO "inbox_created" "path=${INBOX_PATH}"
fi

# heartbeat thread start
heartbeat_loop "$AGENT_ID" 60 &
HEARTBEAT_LOOP_PID=$!
trap cleanup TERM INT

# 初回 heartbeat
write_heartbeat "$AGENT_ID" "watcher_started"

# ──────────────────────────────────────────────────────────────────
# main loop
# ──────────────────────────────────────────────────────────────────

log_json INFO "main_loop_start" "inbox=${INBOX_PATH}"

while true; do
    check_disable_flag
    check_natural_rotation

    # inotifywait (no timeout、Phase 0 反省点 b 対応)
    if ! inotifywait -q -e modify,create,moved_to "$INBOX_PATH" >/dev/null 2>&1; then
        log_json WARN "inotifywait_failed" "error_backoff_5s"
        sleep 5
        continue
    fi

    # cycle2 配達本体 — schema check + dedup + retry cap + safe_nudge 発火
    process_unread_messages
done
