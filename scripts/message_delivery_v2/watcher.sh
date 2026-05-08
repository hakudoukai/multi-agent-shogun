#!/usr/bin/env bash
# scripts/message_delivery_v2/watcher.sh — 新 watcher (Phase 2 MVP)
#
# Phase 0 反省点 a/b/i (= silent death / inotifywait timeout / heartbeat 不在) への対応。
# 単一 agent の inbox を inotifywait で監視、新規 msg 検知 → safe_nudge 発火。
# 1-2 時間で自然交代 (= memory leak 回避)、heartbeat 60 秒間隔。
#
# Usage:
#   bash scripts/message_delivery_v2/watcher.sh <agent_id> <pane_target> <cli_type>
#
# 設計: docs/message_delivery_v2_design_2026-05-08.md §2.2
# 安全装置: §Watcher Design Principles 全項目順守
#
# MVP 範囲 (Phase 2 cycle1):
#   - inotifywait (no timeout) で永続稼働
#   - heartbeat 60s 書込
#   - 自然交代 5400s (= 90 分)
#   - global_disable フラグ尊重
#   - inbox 既読確認のみ (= safe_nudge は cycle2 で実装)
#
# 後続 (cycle2-3):
#   - safe_nudge wrapper 統合
#   - dedup table 連携
#   - dead-letter 移動
#   - schema 検証 gate

set -euo pipefail

# 引数
if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <agent_id> <pane_target> <cli_type>" >&2
    exit 1
fi
AGENT_ID="$1"
PANE_TARGET="$2"
CLI_TYPE="$3"

# project root + lib 読込
_WATCHER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_WATCHER_PROJECT_ROOT="$(cd "${_WATCHER_DIR}/../.." && pwd)"
cd "${_WATCHER_PROJECT_ROOT}"

source "${_WATCHER_PROJECT_ROOT}/scripts/lib/inbox_path.sh"
source "${_WATCHER_PROJECT_ROOT}/scripts/message_delivery_v2/heartbeat.sh"

# 環境変数 export (heartbeat.sh が参照)
export AGENT_ID
export WATCHER_PID=$$
export WATCHER_STARTED_AT
WATCHER_STARTED_AT=$(date -Iseconds)
export WATCHER_STARTED_AT
export TUI_CAPTURE_STATE="unknown"
export READY_FOR_CLEAR="true"
export READY_FOR_DISPATCH="true"

LOG_DIR="${_WATCHER_PROJECT_ROOT}/logs/message_delivery_v2"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/watcher_${AGENT_ID}_$(date +%Y%m%d).log"

# 安全装置
GLOBAL_DISABLE="${HOME}/.openclaw/global_disable"
WATCHER_DISABLE="${HOME}/.openclaw/disable_watcher_${AGENT_ID}"

# 自然交代 (Phase 0 反省点 a 対応: 永続稼働だが memory leak 回避で 5400s = 90 分で自然交代)
NATURAL_ROTATION_SEC=5400

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

# 起動時の sanity check
log_json INFO "watcher_start" "pane=${PANE_TARGET} cli=${CLI_TYPE} version=${HEARTBEAT_VERSION}"

# inbox path 確認
INBOX_PATH=$(get_inbox_path "$AGENT_ID")
if [[ ! -f "$INBOX_PATH" ]]; then
    # 初期化 (= inbox file 不在なら作成)
    mkdir -p "$(dirname "$INBOX_PATH")"
    printf 'messages: []\n' > "$INBOX_PATH"
    log_json INFO "inbox_created" "path=${INBOX_PATH}"
fi

# heartbeat thread start
heartbeat_loop "$AGENT_ID" 60 &
HEARTBEAT_LOOP_PID=$!

# graceful exit
cleanup() {
    log_json INFO "watcher_exit" "reason=signal"
    kill "$HEARTBEAT_LOOP_PID" 2>/dev/null || true
    exit 0
}
trap cleanup TERM INT

# 初回 heartbeat
write_heartbeat "$AGENT_ID" "watcher_started"

# 自然交代 chk
check_natural_rotation() {
    local now_epoch
    now_epoch=$(date +%s)
    local started_epoch
    started_epoch=$(date -d "$WATCHER_STARTED_AT" +%s)
    local uptime=$((now_epoch - started_epoch))
    if [[ $uptime -ge $NATURAL_ROTATION_SEC ]]; then
        log_json INFO "natural_rotation" "uptime_sec=${uptime}"
        write_heartbeat "$AGENT_ID" "natural_rotation_exit"
        kill "$HEARTBEAT_LOOP_PID" 2>/dev/null || true
        exit 0
    fi
}

# disable flag chk
check_disable_flag() {
    if [[ -f "$GLOBAL_DISABLE" ]]; then
        log_json INFO "global_disable_active" "flag=${GLOBAL_DISABLE}"
        write_heartbeat "$AGENT_ID" "disabled_global"
        kill "$HEARTBEAT_LOOP_PID" 2>/dev/null || true
        exit 0
    fi
    if [[ -f "$WATCHER_DISABLE" ]]; then
        log_json INFO "watcher_disable_active" "flag=${WATCHER_DISABLE}"
        write_heartbeat "$AGENT_ID" "disabled_specific"
        kill "$HEARTBEAT_LOOP_PID" 2>/dev/null || true
        exit 0
    fi
}

# inbox 監視 main loop
log_json INFO "main_loop_start" "inbox=${INBOX_PATH}"

while true; do
    check_disable_flag
    check_natural_rotation

    # inotifywait (no timeout、Phase 0 反省点 b 対応)
    if ! inotifywait -q -e modify,create,moved_to "$INBOX_PATH" >/dev/null 2>&1; then
        log_json WARN "inotifywait_failed" "fallback_sleep_5s"
        sleep 5
        continue
    fi

    # 新規 msg 処理 (MVP: log のみ、cycle2 で safe_nudge 発火)
    UNREAD_COUNT=$(python3 -c "
import yaml
try:
    with open('${INBOX_PATH}') as f:
        d = yaml.safe_load(f) or {}
    print(sum(1 for m in d.get('messages',[]) if not m.get('read', False)))
except Exception as e:
    print(0)
" 2>/dev/null)

    log_json INFO "inbox_event" "unread_count=${UNREAD_COUNT}"
    LAST_ACTION="inbox_event_unread_${UNREAD_COUNT}"
    export LAST_ACTION

    # MVP: TODO cycle2 で safe_nudge 統合
    # safe_nudge "$AGENT_ID" "$PANE_TARGET" "$CLI_TYPE" inbox_event "" ""
done
