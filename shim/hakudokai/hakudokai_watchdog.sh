#!/usr/bin/env bash
# hakudokai_watchdog.sh — プロセス死活監視 + 自動再起動 + フェイルセーフ (DD-142 §4.5/§7)
#
# 監視対象:
#   1. hakudokai_fukuincho_watcher.sh (Supabase→shogun inbox)
#   2. inbox_watcher.sh per agent (inotifywait→tmux nudge)
#
# DD-142 §4.5 フェイルセーフ3段階:
#   Stage 1: 死亡検出→60秒以内に自動再起動
#   Stage 2: 3回連続失敗→urgent_stop alert (手動搬送モード)
#   Stage 3: /tmp/hakudokai_health_dashboard.json 30秒更新
#
# DD-142 §7 自律改善ループ:
#   - 再起動失敗時にdev_lessonsへ自動記録
#   - recurrence>=3で改善提案自動dispatch
#
# Usage: bash shim/hakudokai/hakudokai_watchdog.sh [--interval 30]
# 前提: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 環境変数

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHECK_INTERVAL="${2:-30}"
MAX_RESTART_FAILS=3

# Auto-source Supabase env from ~/.hakudokai/env (CR stripped)
if [ -z "${SUPABASE_URL:-}" ] && [ -f "$HOME/.hakudokai/env" ]; then
  SUPABASE_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  SUPABASE_SERVICE_ROLE_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  export SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
fi

LOG="/tmp/hakudokai_watchdog.log"
DASHBOARD="/tmp/hakudokai_health_dashboard.json"
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"
SUPABASE_API="${SUPABASE_URL}/rest/v1"

# Agents to monitor inbox_watcher.sh for
INBOX_AGENTS="karo:multiagent:0.0 ashigaru1:multiagent:0.1 gunshi:multiagent:0.8 shogun:shogun:0.0"

# Restart failure counters (associative array)
declare -A RESTART_FAIL_COUNT
declare -A MANUAL_MODE
RESTART_FAIL_COUNT[fukuincho]=0
MANUAL_MODE[fukuincho]=false
RESTART_FAIL_COUNT[fukuincho_reverse]=0
MANUAL_MODE[fukuincho_reverse]=false
for entry in $INBOX_AGENTS; do
  agent="${entry%%:*}"
  RESTART_FAIL_COUNT[$agent]=0
  MANUAL_MODE[$agent]=false
done

# Stats
START_TIME=$(date +%s)
TOTAL_RESTARTS=0
TOTAL_ALERTS=0

log() {
  echo "[watchdog][$(date '+%H:%M:%S')] $1" | tee -a "$LOG" >&2
}

send_urgent_alert() {
  local target="$1"
  local msg="$2"
  TOTAL_ALERTS=$((TOTAL_ALERTS + 1))
  curl -sS -X POST \
    "${SUPABASE_API}/pc_handshake" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "{\"message_type\":\"urgent_stop\",\"from_pc\":\"main_pc\",\"to_pc\":\"fukuincho\",\"topic\":\"watchdog_failsafe\",\"content\":\"${msg}\",\"requires_response\":true,\"priority\":\"urgent\",\"clinic_id\":\"${CLINIC_ID}\",\"bypass_5round_limit\":false,\"is_meta_only\":false}" \
    2>/dev/null || log "ALERT SEND FAILED for ${target}"
  log "URGENT ALERT SENT: ${msg}"
}

record_dev_lesson() {
  local error_pattern="$1"
  local root_cause="$2"
  local resolution="$3"
  # Insert into dev_lessons table via Supabase
  local payload
  payload=$(cat <<EOJSON
{
  "error_pattern": "${error_pattern}",
  "root_cause": "${root_cause}",
  "resolution_attempted": "${resolution}",
  "source": "watchdog",
  "clinic_id": "${CLINIC_ID}",
  "created_at": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
}
EOJSON
)
  curl -sS -X POST \
    "${SUPABASE_API}/dev_lessons" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "$payload" 2>/dev/null \
    && log "dev_lesson recorded: ${error_pattern}" \
    || log "dev_lesson INSERT failed (table may not exist yet)"
}

start_fukuincho_watcher() {
  log "Starting fukuincho_watcher..."
  nohup env SUPABASE_URL="$SUPABASE_URL" SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
    bash "${SCRIPT_DIR}/shim/hakudokai/hakudokai_fukuincho_watcher.sh" --interval 5 \
    >> /tmp/hakudokai_fukuincho_watcher.log 2>&1 </dev/null &
  local pid=$!
  sleep 3
  if ps -p "$pid" > /dev/null 2>&1; then
    log "fukuincho_watcher STARTED (PID=$pid)"
    RESTART_FAIL_COUNT[fukuincho]=0
    TOTAL_RESTARTS=$((TOTAL_RESTARTS + 1))
    return 0
  else
    log "fukuincho_watcher FAILED TO START"
    return 1
  fi
}

start_inbox_watcher() {
  local agent="$1"
  local pane="$2"
  local logfile="/tmp/inbox_watcher_${agent}.log"
  log "Starting inbox_watcher for $agent ($pane)..."
  nohup bash "${SCRIPT_DIR}/scripts/inbox_watcher.sh" "$agent" "$pane" claude \
    >> "$logfile" 2>&1 </dev/null &
  local pid=$!
  sleep 2
  if ps -p "$pid" > /dev/null 2>&1; then
    log "inbox_watcher[$agent] STARTED (PID=$pid)"
    RESTART_FAIL_COUNT[$agent]=0
    TOTAL_RESTARTS=$((TOTAL_RESTARTS + 1))
    return 0
  else
    log "inbox_watcher[$agent] FAILED TO START"
    tail -3 "$logfile" >> "$LOG"
    return 1
  fi
}

start_fukuincho_reverse_watcher() {
  log "Starting fukuincho_reverse_watcher..."
  nohup env SUPABASE_URL="$SUPABASE_URL" SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
    bash "${SCRIPT_DIR}/shim/hakudokai/hakudokai_fukuincho_reverse_watcher.sh" --interval 5 \
    >> /tmp/hakudokai_fukuincho_reverse_watcher.log 2>&1 </dev/null &
  local pid=$!
  sleep 3
  if ps -p "$pid" > /dev/null 2>&1; then
    log "fukuincho_reverse_watcher STARTED (PID=$pid)"
    RESTART_FAIL_COUNT[fukuincho_reverse]=0
    TOTAL_RESTARTS=$((TOTAL_RESTARTS + 1))
    return 0
  else
    log "fukuincho_reverse_watcher FAILED TO START"
    return 1
  fi
}

check_and_restart_fukuincho_reverse() {
  if ! pgrep -f "hakudokai_fukuincho_reverse_watcher.sh" > /dev/null 2>&1; then
    if [ "${MANUAL_MODE[fukuincho_reverse]}" = "true" ]; then
      log "fukuincho_reverse DEAD — MANUAL MODE (skipping)"
      return 1
    fi
    if [ -f "$HOME/.openclaw/disable_fukuincho_reverse_watcher" ]; then
      log "fukuincho_reverse DEAD — DISABLED by flag (skipping restart)"
      return 1
    fi
    log "ALERT: fukuincho_reverse DEAD — restarting"
    if ! start_fukuincho_reverse_watcher; then
      RESTART_FAIL_COUNT[fukuincho_reverse]=$((RESTART_FAIL_COUNT[fukuincho_reverse] + 1))
      if [ "${RESTART_FAIL_COUNT[fukuincho_reverse]}" -ge "$MAX_RESTART_FAILS" ]; then
        MANUAL_MODE[fukuincho_reverse]=true
        send_urgent_alert "fukuincho_reverse" "fukuincho_reverse_watcher: ${MAX_RESTART_FAILS} restart failures. MANUAL MODE."
      fi
    fi
  fi
}

# DD-142 §4.5 Stage 1+2: check, restart, escalate
check_and_restart_fukuincho() {
  if ! pgrep -f "hakudokai_fukuincho_watcher.sh" > /dev/null 2>&1; then
    if [ "${MANUAL_MODE[fukuincho]}" = "true" ]; then
      log "fukuincho_watcher DEAD — MANUAL MODE (skipping restart)"
      return 1
    fi
    if [ -f "$HOME/.openclaw/disable_fukuincho_watcher" ]; then
      log "fukuincho_watcher DEAD — DISABLED by flag (skipping restart)"
      return 1
    fi
    log "ALERT: fukuincho_watcher DEAD — restarting (fail_count=${RESTART_FAIL_COUNT[fukuincho]})"
    if ! start_fukuincho_watcher; then
      RESTART_FAIL_COUNT[fukuincho]=$((RESTART_FAIL_COUNT[fukuincho] + 1))
      if [ "${RESTART_FAIL_COUNT[fukuincho]}" -ge "$MAX_RESTART_FAILS" ]; then
        MANUAL_MODE[fukuincho]=true
        send_urgent_alert "fukuincho" "fukuincho_watcher: ${MAX_RESTART_FAILS} consecutive restart failures. Entering MANUAL MODE. PID=$$ requires human intervention."
        record_dev_lesson \
          "fukuincho_watcher_restart_failure_x${MAX_RESTART_FAILS}" \
          "Process dies immediately after restart ${MAX_RESTART_FAILS} times" \
          "Escalated to urgent_stop. Manual intervention required."
      fi
    fi
  fi
}

check_and_restart_inbox() {
  local agent="$1"
  local pane="$2"
  if ! pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then
    if [ "${MANUAL_MODE[$agent]}" = "true" ]; then
      log "inbox_watcher[$agent] DEAD — MANUAL MODE (skipping restart)"
      return 1
    fi
    if [ -f "$HOME/.openclaw/disable_inbox_watcher_${agent}" ]; then
      log "inbox_watcher[$agent] DEAD — DISABLED by flag (skipping restart)"
      return 1
    fi
    log "ALERT: inbox_watcher[$agent] DEAD — restarting (fail_count=${RESTART_FAIL_COUNT[$agent]})"
    if ! start_inbox_watcher "$agent" "$pane"; then
      RESTART_FAIL_COUNT[$agent]=$((RESTART_FAIL_COUNT[$agent] + 1))
      if [ "${RESTART_FAIL_COUNT[$agent]}" -ge "$MAX_RESTART_FAILS" ]; then
        MANUAL_MODE[$agent]=true
        send_urgent_alert "$agent" "inbox_watcher[${agent}]: ${MAX_RESTART_FAILS} consecutive restart failures. Entering MANUAL MODE. PID=$$ requires human intervention."
        record_dev_lesson \
          "inbox_watcher_${agent}_restart_failure_x${MAX_RESTART_FAILS}" \
          "inbox_watcher for ${agent} dies immediately after restart ${MAX_RESTART_FAILS} times" \
          "Escalated to urgent_stop. Manual intervention required."
      fi
    fi
  fi
}

# DD-142 §4.5 Stage 3: Health dashboard
update_dashboard() {
  local now
  now=$(date +%s)
  local uptime=$((now - START_TIME))

  # Build per-process status
  local fukuincho_alive="false"
  pgrep -f "hakudokai_fukuincho_watcher.sh" > /dev/null 2>&1 && fukuincho_alive="true"
  local reverse_alive="false"
  pgrep -f "hakudokai_fukuincho_reverse_watcher.sh" > /dev/null 2>&1 && reverse_alive="true"

  local processes="\"fukuincho_watcher\":{\"alive\":${fukuincho_alive},\"manual_mode\":${MANUAL_MODE[fukuincho]},\"restart_fails\":${RESTART_FAIL_COUNT[fukuincho]}},\"fukuincho_reverse\":{\"alive\":${reverse_alive},\"manual_mode\":${MANUAL_MODE[fukuincho_reverse]},\"restart_fails\":${RESTART_FAIL_COUNT[fukuincho_reverse]}}"

  for entry in $INBOX_AGENTS; do
    agent="${entry%%:*}"
    local alive="false"
    pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1 && alive="true"
    processes="${processes},\"inbox_watcher_${agent}\":{\"alive\":${alive},\"manual_mode\":${MANUAL_MODE[$agent]},\"restart_fails\":${RESTART_FAIL_COUNT[$agent]}}"
  done

  cat > "$DASHBOARD" <<EOJSON
{
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "uptime_seconds": ${uptime},
  "total_restarts": ${TOTAL_RESTARTS},
  "total_alerts": ${TOTAL_ALERTS},
  "check_interval": ${CHECK_INTERVAL},
  "processes": {${processes}}
}
EOJSON
}

GLOBAL_DISABLE="$HOME/.openclaw/global_disable"
WATCHDOG_DISABLE="$HOME/.openclaw/disable_watchdog"

# Check disable flags before starting
if [ -f "$GLOBAL_DISABLE" ] || [ -f "$WATCHDOG_DISABLE" ]; then
  echo "[watchdog] DISABLED by flag file — refusing to start" >&2
  exit 0
fi

log "started (interval=${CHECK_INTERVAL}s, max_restart_fails=${MAX_RESTART_FAILS}, agents=${INBOX_AGENTS})"

# Initial health check
check_and_restart_fukuincho
check_and_restart_fukuincho_reverse
for entry in $INBOX_AGENTS; do
  agent="${entry%%:*}"
  pane="${entry#*:}"
  check_and_restart_inbox "$agent" "$pane"
done
update_dashboard

while true; do
  sleep "$CHECK_INTERVAL"

  # Respect manual disable flags (Watcher Design Principles)
  if [ -f "$GLOBAL_DISABLE" ] || [ -f "$WATCHDOG_DISABLE" ]; then
    log "DISABLED by flag file — exiting gracefully"
    rm -f "$DASHBOARD"
    exit 0
  fi

  check_and_restart_fukuincho
  check_and_restart_fukuincho_reverse

  for entry in $INBOX_AGENTS; do
    agent="${entry%%:*}"
    pane="${entry#*:}"
    check_and_restart_inbox "$agent" "$pane"
  done

  # DD-142 §4.5 Stage 3: Update health dashboard every cycle
  update_dashboard

  # Heartbeat
  log "HEARTBEAT: all checks complete"
done
