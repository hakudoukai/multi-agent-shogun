#!/usr/bin/env bash
# hakudokai_secondpc_watcher.sh — SecondPC→MainPC Supabase通信路 watcher
#
# pc_handshake (from_pc='second_pc', to_pc='main_pc' OR 'broadcast')
# を5秒間隔でSELECTし、宛先エージェントのinboxに転記。
#
# Usage: bash shim/hakudokai/hakudokai_secondpc_watcher.sh [--interval 5]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
POLL_SCRIPT="${SCRIPT_DIR}/shim/hakudokai/hakudokai_secondpc_watcher_poll.py"
INTERVAL=5
ONCE=false
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"
HEARTBEAT_INTERVAL=30

while [ $# -gt 0 ]; do
  case "$1" in
    --once) ONCE=true; shift ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Auto-source from ~/.hakudokai/env if not set
if [ -z "${SUPABASE_URL:-}" ] && [ -f "$HOME/.hakudokai/env" ]; then
  SUPABASE_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  SUPABASE_SERVICE_ROLE_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  export SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
fi

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "[secondpc_watcher] ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required" >&2
  exit 1
fi

SUPABASE_API="${SUPABASE_URL}/rest/v1"
PROCESSED_FILE="/tmp/hakudokai_secondpc_watcher_processed.txt"
RESPONSE_TMP="/tmp/hakudokai_secondpc_watcher_response.json"
HEALTHCHECK_FILE="/tmp/hakudokai_secondpc_watcher.health"
touch "$PROCESSED_FILE"

POLL_COUNT=0
FAIL_COUNT=0
CONSECUTIVE_FAILS=0
LAST_HEARTBEAT=$(date +%s)
START_TIME=$(date +%s)

log() {
  echo "[secondpc_watcher][$(date '+%H:%M:%S')] $1" >&2
}

heartbeat() {
  local now=$(date +%s)
  local elapsed=$((now - LAST_HEARTBEAT))
  if [ "$elapsed" -ge "$HEARTBEAT_INTERVAL" ]; then
    local uptime=$((now - START_TIME))
    log "HEARTBEAT: uptime=${uptime}s polls=${POLL_COUNT} fails=${FAIL_COUNT} consecutive_fails=${CONSECUTIVE_FAILS}"
    echo "{\"alive\":true,\"ts\":$(date +%s),\"uptime\":${uptime},\"polls\":${POLL_COUNT},\"fails\":${FAIL_COUNT}}" > "$HEALTHCHECK_FILE"
    LAST_HEARTBEAT=$now
  fi
}

log "started (interval=${INTERVAL}s, once=${ONCE}, clinic=${CLINIC_ID})"
echo "{\"alive\":true,\"ts\":$(date +%s),\"uptime\":0,\"polls\":0,\"fails\":0}" > "$HEALTHCHECK_FILE"

while true; do
  POLL_COUNT=$((POLL_COUNT + 1))

  if curl -sS --connect-timeout 10 --max-time 15 \
    "${SUPABASE_API}/pc_handshake?select=id,from_pc,to_pc,topic,content,priority,message_type,created_at&or=(to_pc.eq.main_pc,to_pc.eq.broadcast)&from_pc=eq.second_pc&acknowledged_at=is.null&clinic_id=eq.${CLINIC_ID}&order=created_at.asc&limit=10" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -o "$RESPONSE_TMP" 2>/dev/null; then

    if python3 "$POLL_SCRIPT" "$RESPONSE_TMP" "$PROCESSED_FILE" "$SCRIPT_DIR" "$SUPABASE_API" "$SUPABASE_SERVICE_ROLE_KEY" 2>&1; then
      CONSECUTIVE_FAILS=0
    else
      FAIL_COUNT=$((FAIL_COUNT + 1))
      CONSECUTIVE_FAILS=$((CONSECUTIVE_FAILS + 1))
      log "POLL_SCRIPT FAILED (consecutive=${CONSECUTIVE_FAILS})"
    fi
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    CONSECUTIVE_FAILS=$((CONSECUTIVE_FAILS + 1))
    log "CURL FAILED (consecutive=${CONSECUTIVE_FAILS})"
  fi

  heartbeat

  if [ "$ONCE" = "true" ]; then
    break
  fi
  sleep "$INTERVAL"
done
