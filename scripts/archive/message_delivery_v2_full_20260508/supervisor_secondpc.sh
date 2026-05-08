#!/usr/bin/env bash
# scripts/message_delivery_v2/supervisor_secondpc.sh — SecondPC 用永続 supervisor
#
# MainPC 版 supervisor.sh と同型、agent list + pane mapping のみ SecondPC 用にカスタマイズ。
# CLAUDE.md §18.1 SecondPC 配置 (前田 + 足軽5/6/7、+1 足軽8) に整合。
#
# Usage (SecondPC 上で):
#   nohup bash scripts/message_delivery_v2/supervisor_secondpc.sh > logs/message_delivery_v2/supervisor_secondpc.log 2>&1 &
#   disown
#
# 設計: docs/message_delivery_v2_design_2026-05-08.md §2.1 + cross-PC bridge との協調
# 理事長殿御命令『SecondPC cycle2 開始』(2026-05-08 19:30) 反映

set -euo pipefail

_SUPERVISOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_SUPERVISOR_PROJECT_ROOT="$(cd "${_SUPERVISOR_DIR}/../.." && pwd)"
cd "${_SUPERVISOR_PROJECT_ROOT}"

source "${_SUPERVISOR_PROJECT_ROOT}/scripts/lib/inbox_path.sh"
source "${_SUPERVISOR_PROJECT_ROOT}/scripts/message_delivery_v2/heartbeat.sh"

export AGENT_ID="_supervisor_secondpc"
export WATCHER_PID=$$
WATCHER_STARTED_AT=$(date -Iseconds)
export WATCHER_STARTED_AT

LOG_DIR="${_SUPERVISOR_PROJECT_ROOT}/logs/message_delivery_v2"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/supervisor_secondpc_$(date +%Y%m%d).log"

GLOBAL_DISABLE="${HOME}/.openclaw/global_disable"
SUPERVISOR_DISABLE="${HOME}/.openclaw/disable_supervisor_secondpc"

CHECK_INTERVAL=30
HEARTBEAT_THRESHOLD=300
MAX_RESTART_COUNT=5
RESTART_RESET_INTERVAL=86400

# SecondPC pane mapping (= CLAUDE.md §18.1 SecondPC 配置)
# 前田 (家老) + 足軽5/6/7、+1 足軽8 (非常時)
declare -A WATCHER_PANES=(
    [maeda]="multiagent:0.0"
    [ashigaru5]="multiagent:0.1"
    [ashigaru6]="multiagent:0.2"
    [ashigaru7]="multiagent:0.3"
)
declare -A WATCHER_CLI=(
    [maeda]="claude"
    [ashigaru5]="claude"
    [ashigaru6]="claude"
    [ashigaru7]="claude"
)

declare -A RESTART_COUNT
declare -A LAST_RESTART_AT
for agent in "${!WATCHER_PANES[@]}"; do
    RESTART_COUNT[$agent]=0
    LAST_RESTART_AT[$agent]=0
done

log_json() {
    local level="$1"
    local msg="$2"
    shift 2
    local extra="${*:-}"
    local ts
    ts=$(date -Iseconds)
    printf '{"ts":"%s","level":"%s","component":"supervisor_secondpc","pid":%d,"msg":"%s","extra":"%s"}\n' \
        "$ts" "$level" "$WATCHER_PID" "$msg" "$extra" >> "$LOG_FILE"
}

check_disable() {
    if [[ -f "$GLOBAL_DISABLE" ]]; then
        log_json INFO "global_disable_active" "sleep 30s"
        sleep 30
        return 1
    fi
    if [[ -f "$SUPERVISOR_DISABLE" ]]; then
        log_json INFO "supervisor_secondpc_disable_active" "sleep 30s"
        sleep 30
        return 1
    fi
    return 0
}

pane_exists() {
    local pane="$1"
    tmux list-panes -a -F "#{session_name}:#{window_index}.#{pane_index}" 2>/dev/null | grep -qx "$pane"
}

watcher_running() {
    local agent="$1"
    pgrep -f "scripts/message_delivery_v2/watcher.sh ${agent} " >/dev/null 2>&1
}

spawn_watcher() {
    local agent="$1"
    local pane="${WATCHER_PANES[$agent]}"
    local cli="${WATCHER_CLI[$agent]}"

    if ! pane_exists "$pane"; then
        log_json WARN "pane_not_exist" "agent=${agent} pane=${pane}"
        return 1
    fi

    local watcher_log="${LOG_DIR}/watcher_${agent}_$(date +%Y%m%d).log"
    nohup bash "${_SUPERVISOR_PROJECT_ROOT}/scripts/message_delivery_v2/watcher.sh" \
        "$agent" "$pane" "$cli" >> "$watcher_log" 2>&1 &
    disown
    local new_pid=$!

    log_json INFO "watcher_spawned" "agent=${agent} pid=${new_pid} pane=${pane}"
    return 0
}

escalate() {
    local agent="$1"
    local count="$2"
    log_json ERROR "escalation" "agent=${agent} restart_count=${count}"
    {
        echo "$(date -Iseconds) 🚨 SecondPC watcher ${agent} dead ${count} 回連続再起動超過、人手介入要"
    } >> "${LOG_DIR}/escalation_secondpc_$(date +%Y%m%d).log"
    # cross-PC bridge 経由で MainPC 信長 inbox にも escalation (= 反省点 r 対応、別 cmd で実装)
}

log_json INFO "supervisor_secondpc_start" "version=${HEARTBEAT_VERSION:-unknown} agents=${#WATCHER_PANES[@]}"

trap 'log_json INFO "supervisor_secondpc_exit" "reason=signal"; exit 0' TERM INT

while true; do
    if ! check_disable; then
        continue
    fi

    write_heartbeat "$AGENT_ID" "monitoring"

    now_epoch=$(date +%s)
    for agent in "${!WATCHER_PANES[@]}"; do
        last=${LAST_RESTART_AT[$agent]:-0}
        if [[ $((now_epoch - last)) -ge $RESTART_RESET_INTERVAL ]]; then
            RESTART_COUNT[$agent]=0
        fi

        if [[ ${RESTART_COUNT[$agent]} -ge $MAX_RESTART_COUNT ]]; then
            if [[ $((now_epoch - last)) -lt 1800 ]]; then
                continue
            fi
            log_json INFO "circuit_breaker_cooldown_passed" "agent=${agent}"
            RESTART_COUNT[$agent]=0
        fi

        if is_heartbeat_stale "$agent" "$HEARTBEAT_THRESHOLD"; then
            if watcher_running "$agent"; then
                log_json WARN "heartbeat_stale_but_process_alive" "agent=${agent}"
                continue
            fi

            if spawn_watcher "$agent"; then
                RESTART_COUNT[$agent]=$((${RESTART_COUNT[$agent]} + 1))
                LAST_RESTART_AT[$agent]=$now_epoch
                log_json INFO "auto_restart" "agent=${agent} count=${RESTART_COUNT[$agent]}"

                if [[ ${RESTART_COUNT[$agent]} -ge $MAX_RESTART_COUNT ]]; then
                    escalate "$agent" "${RESTART_COUNT[$agent]}"
                fi
            else
                log_json ERROR "spawn_failed" "agent=${agent}"
            fi
        fi
    done

    sleep $CHECK_INTERVAL
done
