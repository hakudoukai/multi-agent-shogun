#!/usr/bin/env bash
# hakudokai_fukuincho_reverse_watcher.sh — 将軍→副医院長 通知デーモン
#
# 将軍(shogun)がSupabase pc_handshakeにINSERTしたメッセージを
# 副医院長(fukuincho) CLIのinboxに配信し、tmux nudgeで起こす。
#
# 既存の hakudokai_fukuincho_watcher.sh の逆方向版。
#
# Usage: bash shim/hakudokai/hakudokai_fukuincho_reverse_watcher.sh [--interval 5]
# 前提: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 環境変数

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
POLL_INTERVAL="${2:-5}"
PROCESSED_FILE="/tmp/hakudokai_fukuincho_reverse_processed.txt"
HEALTH_FILE="/tmp/hakudokai_fukuincho_reverse_health.json"
LOG="/tmp/hakudokai_fukuincho_reverse_watcher.log"
FUKUINCHO_PANE="${FUKUINCHO_PANE:-fukuincho:0.0}"
FAIL_COUNT=0
MAX_FAILS=5
POLL_COUNT=0

# Auto-source Supabase env
if [ -z "${SUPABASE_URL:-}" ] && [ -f "$HOME/.hakudokai/env" ]; then
  SUPABASE_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  SUPABASE_SERVICE_ROLE_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  export SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
fi

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required" >&2
  exit 1
fi

touch "$PROCESSED_FILE"

log() {
  echo "[fukuincho_reverse][$(date '+%H:%M:%S')] $1" | tee -a "$LOG" >&2
}

update_health() {
  cat > "$HEALTH_FILE" <<EOJSON
{
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "poll_count": ${POLL_COUNT},
  "fail_count": ${FAIL_COUNT},
  "status": "running",
  "interval": ${POLL_INTERVAL}
}
EOJSON
}

log "started (interval=${POLL_INTERVAL}s, pane=${FUKUINCHO_PANE})"

while true; do
  sleep "$POLL_INTERVAL"
  POLL_COUNT=$((POLL_COUNT + 1))

  # Query: messages TO fukuincho that are not yet acknowledged
  RESPONSE=$(curl -sS -w "\n%{http_code}" \
    "${SUPABASE_URL}/rest/v1/pc_handshake?to_pc=eq.fukuincho&acknowledged_at=is.null&order=created_at.asc&limit=5" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" 2>/dev/null)

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | sed '$d')

  if [ "$HTTP_CODE" != "200" ]; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
    log "poll FAILED (HTTP ${HTTP_CODE}, fail_count=${FAIL_COUNT})"
    if [ "$FAIL_COUNT" -ge "$MAX_FAILS" ]; then
      log "ALERT: ${MAX_FAILS} consecutive failures"
    fi
    update_health
    continue
  fi

  FAIL_COUNT=0

  # Check for empty response
  if [ "$BODY" = "[]" ] || [ -z "$BODY" ]; then
    update_health
    continue
  fi

  # Write response to temp file for Python processing
  TEMP_RESPONSE="/tmp/hakudokai_fukuincho_reverse_response.json"
  echo "$BODY" > "$TEMP_RESPONSE"

  # Process with Python
  python3 "${SCRIPT_DIR}/shim/hakudokai/hakudokai_fukuincho_reverse_poll.py" \
    "$TEMP_RESPONSE" \
    "$PROCESSED_FILE" \
    "$SCRIPT_DIR" \
    "${SUPABASE_URL}" \
    "${SUPABASE_SERVICE_ROLE_KEY}" \
    "$FUKUINCHO_PANE"

  # Heartbeat log every 10 polls
  if [ $((POLL_COUNT % 10)) -eq 0 ]; then
    log "HEARTBEAT: polls=${POLL_COUNT}, fails=${FAIL_COUNT}"
  fi

  update_health
done
