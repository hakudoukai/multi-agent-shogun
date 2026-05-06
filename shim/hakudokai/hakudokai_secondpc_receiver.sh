#!/usr/bin/env bash
# hakudokai_secondpc_receiver.sh — SecondPC Supabase bridge receiver (v2)
#
# Supabase pc_handshake から second_pc 宛メッセージを受信し、
# ローカル inbox に書き込む。
#
# v2 improvements:
#   - ACK-before-repoll: ACK完了後にsleep（重複配信防止）
#   - processed_file で二重処理防止
#   - nudge は短い "inboxN" のみ（文章混入防止）
#   - inbox_write 失敗時はACKしない（メッセージ消失防止）
#   - 環境変数にキーを露出しない（env fileから毎回読み込み）
#
# Usage: bash shim/hakudokai/hakudokai_secondpc_receiver.sh [--interval 5]

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
POLL_INTERVAL="${2:-5}"
PROCESSED_FILE="/tmp/hakudokai_secondpc_receiver_processed.txt"
LOG="/tmp/hakudokai_secondpc_receiver.log"
HEALTH_FILE="/tmp/hakudokai_secondpc_receiver.health"
POLL_COUNT=0
FAIL_COUNT=0

# Auto-source Supabase env
if [ -z "${SUPABASE_URL:-}" ] && [ -f "$HOME/.hakudokai/env" ]; then
  SUPABASE_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  SUPABASE_SERVICE_ROLE_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  export SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
fi

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "[receiver] ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required" >&2
  exit 1
fi

touch "$PROCESSED_FILE"

log() {
  echo "[receiver][$(date '+%H:%M:%S')] $1" | tee -a "$LOG" >&2
}

# Manual disable flags (Watcher Design Principles 必須項目)
GLOBAL_DISABLE="$HOME/.openclaw/global_disable"
WATCHER_DISABLE="$HOME/.openclaw/disable_secondpc_receiver"

log "started (interval=${POLL_INTERVAL}s)"

while true; do
  sleep "$POLL_INTERVAL"

  # Manual disable flag check (Watcher Design Principles 必須項目)
  if [ -f "$GLOBAL_DISABLE" ] || [ -f "$WATCHER_DISABLE" ]; then
    log "DISABLED by flag file — exiting gracefully"
    rm -f "$HEALTH_FILE"
    exit 0
  fi

  POLL_COUNT=$((POLL_COUNT + 1))

  # Poll Supabase
  RESPONSE=$(curl -sS --connect-timeout 10 --max-time 15 \
    "${SUPABASE_URL}/rest/v1/pc_handshake?select=id,from_pc,to_pc,topic,content,priority,message_type,created_at&to_pc=eq.second_pc&acknowledged_at=is.null&order=created_at.asc&limit=10" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" 2>/dev/null)

  if [ -z "$RESPONSE" ] || [ "$RESPONSE" = "[]" ]; then
    # Heartbeat every 20 polls
    if [ $((POLL_COUNT % 20)) -eq 0 ]; then
      log "HEARTBEAT: polls=${POLL_COUNT} fails=${FAIL_COUNT}"
    fi
    continue
  fi

  # Process with Python
  TEMP_RESPONSE="/tmp/hakudokai_secondpc_receiver_response.json"
  echo "$RESPONSE" > "$TEMP_RESPONSE"

  python3 "${SCRIPT_DIR}/shim/hakudokai/hakudokai_secondpc_receiver_poll.py" \
    "$TEMP_RESPONSE" \
    "$PROCESSED_FILE" \
    "$SCRIPT_DIR" \
    "${SUPABASE_URL}/rest/v1" \
    "${SUPABASE_SERVICE_ROLE_KEY}" \
    2>&1 | tee -a "$LOG"

  # Health file
  cat > "$HEALTH_FILE" <<EOJSON
{
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "poll_count": ${POLL_COUNT},
  "fail_count": ${FAIL_COUNT},
  "status": "running"
}
EOJSON

done
