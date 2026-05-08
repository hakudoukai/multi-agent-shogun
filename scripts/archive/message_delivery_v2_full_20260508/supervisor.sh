#!/usr/bin/env bash
# scripts/message_delivery_v2/supervisor.sh — 永続 supervisor (Phase 2 MVP)
#
# Phase 0 反省点 a/i (= silent death + heartbeat 不在) への根本対応。
# watcher を常時 spawn 監視、heartbeat staleness 検知 → 自動再起動 → cap 5 で escalation。
#
# Usage:
#   nohup bash scripts/message_delivery_v2/supervisor.sh > logs/supervisor.log 2>&1 &
#   disown
#
# 設計: docs/message_delivery_v2_design_2026-05-08.md §2.1
# 安全装置: §15 SH パターン (SH1 Circuit Breaker / SH6 Self-Restart 限定)
#
# MVP 範囲 (Phase 2 cycle1):
#   - pane_registry.yaml から MainPC Claude 系 5 体取得 + 既存運用 6 体に整合
#   - 30 秒間隔で heartbeat staleness check (300 秒 threshold)
#   - 死亡検知 → 自動 spawn (= bash watcher.sh)
#   - restart count 5 超過で escalation (= 信長 inbox + ntfy + dashboard)
#   - global_disable / supervisor_disable フラグ尊重
#   - 自身も heartbeat 書込 (= meta heartbeat、agent_id="_supervisor")
#
# 後続 (cycle2-3):
#   - pane identity 4-way verify 統合
#   - SecondPC 対応 (= 別 supervisor or 拡張)
#   - Codex 系 (家康・本多) 専用判定
#   - drift 検知 alert

set -euo pipefail

# project root + lib 読込
_SUPERVISOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_SUPERVISOR_PROJECT_ROOT="$(cd "${_SUPERVISOR_DIR}/../.." && pwd)"
cd "${_SUPERVISOR_PROJECT_ROOT}"

source "${_SUPERVISOR_PROJECT_ROOT}/scripts/lib/inbox_path.sh"
source "${_SUPERVISOR_PROJECT_ROOT}/scripts/message_delivery_v2/heartbeat.sh"

# 環境変数
export AGENT_ID="_supervisor"
export WATCHER_PID=$$
WATCHER_STARTED_AT=$(date -Iseconds)
export WATCHER_STARTED_AT

LOG_DIR="${_SUPERVISOR_PROJECT_ROOT}/logs/message_delivery_v2"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/supervisor_$(date +%Y%m%d).log"

# 安全装置
GLOBAL_DISABLE="${HOME}/.openclaw/global_disable"
SUPERVISOR_DISABLE="${HOME}/.openclaw/disable_supervisor_v2"

# Phase 0 反省点 a 対応: 30 秒間隔で監視、5 分 (300s) 経過で死亡判定
CHECK_INTERVAL=30
HEARTBEAT_THRESHOLD=300
MAX_RESTART_COUNT=5
RESTART_RESET_INTERVAL=86400  # 24h

# MVP: hardcode で MainPC Claude 系 5 体 + 信長 + 真田 (家康・本多 = Codex で別途判定)
# 将来的に pane_registry.yaml から動的取得 (cmd_section18_topology_consensus_001 完遂後)
declare -A WATCHER_PANES=(
    [hideyoshi]="multiagent:0.0"
    [ashigaru1]="multiagent:0.1"
    [ashigaru2]="multiagent:0.2"
    [ashigaru3]="multiagent:0.4"
    [takenaka]="multiagent:0.5"
    [sanada]="multiagent:2.0"
    [ieyasu]="multiagent:0.3"
    [honda]="multiagent:1.0"
)
declare -A WATCHER_CLI=(
    [hideyoshi]="claude"
    [ashigaru1]="claude"
    [ashigaru2]="claude"
    [ashigaru3]="claude"
    [takenaka]="claude"
    [sanada]="claude"
    [ieyasu]="codex"
    [honda]="codex"
)

# restart count tracking
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
    printf '{"ts":"%s","level":"%s","component":"supervisor","pid":%d,"msg":"%s","extra":"%s"}\n' \
        "$ts" "$level" "$WATCHER_PID" "$msg" "$extra" >> "$LOG_FILE"
}

# disable flag chk (= 検出時 exit 0、graceful 停止経路)
# 旧設計の sleep 30 永久ループは廃止 (= 反省点新規: supervisor が exit せず restart 困難)
check_disable() {
    if [[ -f "$GLOBAL_DISABLE" ]]; then
        log_json INFO "global_disable_exit" "flag=${GLOBAL_DISABLE}"
        write_heartbeat "$AGENT_ID" "disabled_global_exit"
        exit 0
    fi
    if [[ -f "$SUPERVISOR_DISABLE" ]]; then
        log_json INFO "supervisor_disable_exit" "flag=${SUPERVISOR_DISABLE}"
        write_heartbeat "$AGENT_ID" "disabled_specific_exit"
        exit 0
    fi
    return 0
}

# pane 存在確認
pane_exists() {
    local pane="$1"
    tmux list-panes -a -F "#{session_name}:#{window_index}.#{pane_index}" 2>/dev/null | grep -qx "$pane"
}

# watcher プロセス検出
watcher_running() {
    local agent="$1"
    pgrep -f "scripts/message_delivery_v2/watcher.sh ${agent} " >/dev/null 2>&1
}

# spawn watcher
spawn_watcher() {
    local agent="$1"
    local pane="${WATCHER_PANES[$agent]}"
    local cli="${WATCHER_CLI[$agent]}"

    # pane 存在確認 (Phase 0 反省点 n 対応の最低限版)
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

# escalation
escalate() {
    local agent="$1"
    local count="$2"
    log_json ERROR "escalation" "agent=${agent} restart_count=${count}"
    # 信長 inbox + dashboard 記録 (= 簡易版、cycle2 で完全実装)
    local msg="🚨 watcher ${agent} dead ${count} 回連続再起動超過、人手介入要"
    {
        echo "$(date -Iseconds) $msg"
    } >> "${LOG_DIR}/escalation_$(date +%Y%m%d).log"
}

# main loop
log_json INFO "supervisor_start" "version=${HEARTBEAT_VERSION} agents=${#WATCHER_PANES[@]}"

trap 'log_json INFO "supervisor_exit" "reason=signal"; exit 0' TERM INT

while true; do
    if ! check_disable; then
        continue
    fi

    # 自身の heartbeat
    write_heartbeat "$AGENT_ID" "monitoring"

    # 各 watcher 監視
    now_epoch=$(date +%s)
    for agent in "${!WATCHER_PANES[@]}"; do
        # restart count reset (24h 経過で reset)
        last=${LAST_RESTART_AT[$agent]:-0}
        if [[ $((now_epoch - last)) -ge $RESTART_RESET_INTERVAL ]]; then
            RESTART_COUNT[$agent]=0
        fi

        # cap 超過 chk
        if [[ ${RESTART_COUNT[$agent]} -ge $MAX_RESTART_COUNT ]]; then
            # 30 分 cooldown で再試行 (= SH1 Circuit Breaker)
            if [[ $((now_epoch - last)) -lt 1800 ]]; then
                continue
            fi
            log_json INFO "circuit_breaker_cooldown_passed" "agent=${agent}"
            RESTART_COUNT[$agent]=0
        fi

        # heartbeat staleness chk
        if is_heartbeat_stale "$agent" "$HEARTBEAT_THRESHOLD"; then
            # process 存在 chk
            if watcher_running "$agent"; then
                log_json WARN "heartbeat_stale_but_process_alive" "agent=${agent}"
                continue
            fi

            # 自動再起動
            if spawn_watcher "$agent"; then
                RESTART_COUNT[$agent]=$((${RESTART_COUNT[$agent]} + 1))
                LAST_RESTART_AT[$agent]=$now_epoch
                log_json INFO "auto_restart" "agent=${agent} count=${RESTART_COUNT[$agent]}"

                # cap 到達で escalation
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
