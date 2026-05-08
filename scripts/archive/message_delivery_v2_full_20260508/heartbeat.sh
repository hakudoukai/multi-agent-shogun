#!/usr/bin/env bash
# scripts/message_delivery_v2/heartbeat.sh — heartbeat 書込ライブラリ
#
# Phase 0 反省点 i (= heartbeat 不在で死亡検知不可) への対応。
# watcher / supervisor / agent session が定期的に health file を更新、外部から生死判定可能に。
#
# Usage:
#   source scripts/message_delivery_v2/heartbeat.sh
#   write_heartbeat "hideyoshi" "delivered_msg_xxx"
#
# 仕様: docs/message_delivery_v2_design_2026-05-08.md §2.5 / §3.4
# schema_version: 1.0

set -euo pipefail

# project root + lib 読込
_HEARTBEAT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_HEARTBEAT_PROJECT_ROOT="$(cd "${_HEARTBEAT_DIR}/../.." && pwd)"
source "${_HEARTBEAT_PROJECT_ROOT}/scripts/lib/inbox_path.sh"

HEARTBEAT_VERSION="v2.0.0"
HEARTBEAT_SCHEMA_VERSION="1.0"

# write_heartbeat <agent_id> <last_action> [<extra_kv>]
# health file (queue/watchers/<agent>.health) を atomic 書込
write_heartbeat() {
    local agent="$1"
    local last_action="${2:-idle}"
    local pid="${WATCHER_PID:-$$}"
    local started_at="${WATCHER_STARTED_AT:-$(date -Iseconds)}"
    local now
    now=$(date -Iseconds)

    local started_epoch
    started_epoch=$(date -d "$started_at" +%s 2>/dev/null || echo 0)
    local now_epoch
    now_epoch=$(date +%s)
    local uptime_sec=$((now_epoch - started_epoch))

    local restart_count="${RESTART_COUNT_24H:-0}"
    local tui_state="${TUI_CAPTURE_STATE:-unknown}"
    local ready_clear="${READY_FOR_CLEAR:-true}"
    local ready_dispatch="${READY_FOR_DISPATCH:-true}"

    local health_path
    health_path=$(get_health_path "$agent")
    # subshell PID 使用で race 回避 (= 反省点新規: $$ は parent shell 共有で衝突)
    local tmp_path="${health_path}.tmp.${BASHPID:-$$}.$RANDOM"

    # fail-safe: heartbeat 失敗で watcher exit させない (= set -e 環境でも吸収)
    {
        cat > "$tmp_path" <<EOF
{
  "schema_version": "${HEARTBEAT_SCHEMA_VERSION}",
  "agent_id": "${agent}",
  "watcher_pid": ${pid},
  "version": "${HEARTBEAT_VERSION}",
  "alive": true,
  "started_at": "${started_at}",
  "uptime_sec": ${uptime_sec},
  "last_action": "${last_action}",
  "last_seen_at": "${now}",
  "tui_capture_state": "${tui_state}",
  "ready_for_clear": ${ready_clear},
  "ready_for_dispatch": ${ready_dispatch},
  "restart_count_24h": ${restart_count}
}
EOF
        mv -f "$tmp_path" "$health_path" 2>/dev/null
    } 2>/dev/null || true
    rm -f "$tmp_path" 2>/dev/null
    return 0
}

# read_heartbeat <agent_id>
# returns: health JSON content, or empty if not found
read_heartbeat() {
    local agent="$1"
    local health_path
    health_path=$(get_health_path "$agent")
    if [[ -f "$health_path" ]]; then
        cat "$health_path"
    fi
}

# is_heartbeat_stale <agent_id> [<threshold_sec>]
# returns: 0 (stale) / 1 (fresh)
# default threshold: 300 sec (5 min)
is_heartbeat_stale() {
    local agent="$1"
    local threshold="${2:-300}"
    local health_path
    health_path=$(get_health_path "$agent")

    if [[ ! -f "$health_path" ]]; then
        return 0  # missing = stale
    fi

    local last_seen
    last_seen=$(grep -oP '"last_seen_at":\s*"\K[^"]+' "$health_path" 2>/dev/null || echo "")
    if [[ -z "$last_seen" ]]; then
        return 0
    fi

    local last_epoch
    last_epoch=$(date -d "$last_seen" +%s 2>/dev/null || echo 0)
    local now_epoch
    now_epoch=$(date +%s)
    local age=$((now_epoch - last_epoch))

    if [[ $age -ge $threshold ]]; then
        return 0  # stale
    else
        return 1  # fresh
    fi
}

# heartbeat_loop <agent_id> [<interval_sec>]
# 60 秒間隔で heartbeat 書込、SIGTERM で graceful 終了
heartbeat_loop() {
    local agent="$1"
    local interval="${2:-60}"

    trap 'echo "[heartbeat] graceful exit for $agent" >&2; exit 0' TERM INT

    while true; do
        write_heartbeat "$agent" "${LAST_ACTION:-idle}" || {
            echo "[heartbeat] write failed for $agent" >&2
        }
        sleep "$interval"
    done
}
