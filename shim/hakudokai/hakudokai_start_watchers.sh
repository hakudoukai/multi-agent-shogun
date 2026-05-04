#!/usr/bin/env bash
# hakudokai_start_watchers.sh — 全watcher一括起動 + watchdog常駐
#
# Usage: bash shim/hakudokai/hakudokai_start_watchers.sh
#
# 起動するもの:
#   1. hakudokai_fukuincho_watcher.sh (Supabase→shogun inbox)
#   2. inbox_watcher.sh × 3 (karo, ashigaru1, gunshi)
#   3. hakudokai_watchdog.sh (死活監視 + 自動再起動)
#
# 前提:
#   - SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 環境変数
#   - inotify-tools インストール済
#   - tmux sessions (shogun, multiagent) 起動済

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

log() {
  echo "[start_watchers][$(date '+%H:%M:%S')] $1"
}

# Validate env
# Auto-source from ~/.hakudokai/env if not set
if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  if [ -f "$HOME/.hakudokai/env" ]; then
    log "Sourcing Supabase env from ~/.hakudokai/env"
    SUPABASE_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
    SUPABASE_SERVICE_ROLE_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
    export SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
  fi
fi

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required" >&2
  echo "Hint: Create ~/.hakudokai/env with SUPABASE_URL=... and SUPABASE_SERVICE_ROLE_KEY=..." >&2
  exit 1
fi

if ! command -v inotifywait &>/dev/null; then
  echo "ERROR: inotifywait not found. Install: sudo apt install inotify-tools" >&2
  exit 1
fi

# Kill existing watchers to prevent duplicates
# Note: pkill here is infrastructure-level (Lord-invoked), not agent-invoked (D006 scope外)
log "Cleaning up existing watcher processes..."
pkill -f "hakudokai_fukuincho_watcher.sh" 2>/dev/null || true
pkill -f "hakudokai_fukuincho_reverse_watcher.sh" 2>/dev/null || true
pkill -f "hakudokai_watchdog.sh" 2>/dev/null || true
for agent in karo ashigaru1 gunshi shogun; do
  pkill -f "inbox_watcher.sh ${agent}" 2>/dev/null || true
done
sleep 1

# 1. Start fukuincho_watcher
log "Starting fukuincho_watcher..."
nohup env SUPABASE_URL="$SUPABASE_URL" SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
  bash "${SCRIPT_DIR}/shim/hakudokai/hakudokai_fukuincho_watcher.sh" --interval 5 \
  >> /tmp/hakudokai_fukuincho_watcher.log 2>&1 </dev/null &
sleep 2
if pgrep -f "hakudokai_fukuincho_watcher.sh" > /dev/null 2>&1; then
  log "fukuincho_watcher: OK"
else
  log "fukuincho_watcher: FAILED"
fi

# 2. Start inbox_watcher.sh per agent (including shogun)
for entry in "karo multiagent:0.0" "ashigaru1 multiagent:0.1" "gunshi multiagent:0.8" "shogun shogun:0.0"; do
  agent=$(echo "$entry" | cut -d' ' -f1)
  pane=$(echo "$entry" | cut -d' ' -f2)
  logfile="/tmp/inbox_watcher_${agent}.log"
  log "Starting inbox_watcher[$agent]..."
  nohup bash "${SCRIPT_DIR}/scripts/inbox_watcher.sh" "$agent" "$pane" claude \
    >> "$logfile" 2>&1 </dev/null &
  sleep 1
done

sleep 2
for agent in karo ashigaru1 gunshi shogun; do
  if pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then
    log "inbox_watcher[$agent]: OK"
  else
    log "inbox_watcher[$agent]: FAILED"
  fi
done

# 3. Start fukuincho reverse watcher (shogun → fukuincho)
log "Starting fukuincho_reverse_watcher..."
nohup env SUPABASE_URL="$SUPABASE_URL" SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
  bash "${SCRIPT_DIR}/shim/hakudokai/hakudokai_fukuincho_reverse_watcher.sh" --interval 5 \
  >> /tmp/hakudokai_fukuincho_reverse_watcher.log 2>&1 </dev/null &
sleep 2
if pgrep -f "hakudokai_fukuincho_reverse_watcher.sh" > /dev/null 2>&1; then
  log "fukuincho_reverse_watcher: OK"
else
  log "fukuincho_reverse_watcher: FAILED"
fi

# 4. Start watchdog
log "Starting watchdog..."
nohup env SUPABASE_URL="$SUPABASE_URL" SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
  bash "${SCRIPT_DIR}/shim/hakudokai/hakudokai_watchdog.sh" --interval 30 \
  >> /tmp/hakudokai_watchdog.log 2>&1 </dev/null &
sleep 2
if pgrep -f "hakudokai_watchdog.sh" > /dev/null 2>&1; then
  log "watchdog: OK"
else
  log "watchdog: FAILED"
fi

# Summary
log "=== STARTUP SUMMARY ==="
log "fukuincho_watcher: $(pgrep -f 'hakudokai_fukuincho_watcher.sh' | head -1 || echo DEAD)"
log "fukuincho_reverse: $(pgrep -f 'hakudokai_fukuincho_reverse_watcher.sh' | head -1 || echo DEAD)"
log "inbox_watcher[karo]: $(pgrep -f 'inbox_watcher.sh karo' | head -1 || echo DEAD)"
log "inbox_watcher[ashigaru1]: $(pgrep -f 'inbox_watcher.sh ashigaru1' | head -1 || echo DEAD)"
log "inbox_watcher[gunshi]: $(pgrep -f 'inbox_watcher.sh gunshi' | head -1 || echo DEAD)"
log "inbox_watcher[shogun]: $(pgrep -f 'inbox_watcher.sh shogun' | head -1 || echo DEAD)"
log "watchdog: $(pgrep -f 'hakudokai_watchdog.sh' | head -1 || echo DEAD)"
log "=== ALL DONE ==="
