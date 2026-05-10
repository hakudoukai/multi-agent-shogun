#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# agent_health_check.sh — agent / daemon 死活 + 復活
#
# 検知 → 即時起動 (= 鉄則 1)
# 対象:
#   - audit_queue_worker daemon
#   - hakudokai bridge process
#   - watcher_supervisor
#   - inbox_watcher 全数 (10 件)
#   - shogun pane (= 信長/家康 main session)
# ════════════════════════════════════════════════════════════════
set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

log() { echo "[$(date -Iseconds)] [health] $*"; }

# audit_queue_worker daemon
if ! pgrep -f "scripts/audit_queue_worker.sh" >/dev/null 2>&1; then
    log "❌ audit_queue_worker dead、起動"
    bash scripts/start_audit_workers.sh 2>&1 | sed 's/^/  /'
else
    log "✅ audit_queue_worker 稼働"
fi

# bridge process
if ! pgrep -f "hakudokai_realtime_bridge" >/dev/null 2>&1; then
    log "❌ bridge process dead、起動"
    if [ -f shim/hakudokai/hakudokai_realtime_bridge.py ]; then
        nohup setsid python3 -u shim/hakudokai/hakudokai_realtime_bridge.py --poll-interval 3 \
            < /dev/null > /tmp/realtime_bridge.log 2>&1 &
        disown
        log "  bridge PID $!"
    fi
else
    log "✅ bridge 稼働"
fi

# watcher_supervisor
if ! pgrep -f "scripts/watcher_supervisor.sh" >/dev/null 2>&1; then
    log "❌ watcher_supervisor dead、起動"
    nohup setsid bash scripts/watcher_supervisor.sh < /dev/null >> "$LOG_DIR/watcher_supervisor.log" 2>&1 &
    disown
    log "  supervisor PID $!"
    sleep 5
else
    log "✅ watcher_supervisor 稼働"
fi

# inbox_watcher 数
WCOUNT=$(pgrep -fc "scripts/inbox_watcher.sh" 2>/dev/null || echo 0)
log "inbox_watcher: $WCOUNT 件"
if [ "$WCOUNT" -lt 10 ]; then
    log "  ⚠ 期待 10 件、不足 → supervisor が auto spawn 待ち"
fi

# shogun pane
if ! tmux has-session -t shogun 2>/dev/null; then
    log "❌ shogun session 不在、復活"
    bash scripts/recover_shogun.sh --main 2>&1 | sed 's/^/  /'
else
    log "✅ shogun session 既存"
fi

log "agent_health_check 完遂"
