#!/usr/bin/env bash
# hakudokai_kuro_desktop_watcher.sh — Desktopクロちゃん(Claude.ai) ↔ 将軍 双方向通信路
#
# 2つの方向を1つのデーモンで処理:
#   1. Desktop kuro → main_pc: from_pc=kuro_desktop のメッセージを将軍inboxに転記
#   2. main_pc → Desktop kuro: to_pc=kuro_desktop のメッセージをntfy通知
#
# Usage: bash shim/hakudokai/hakudokai_kuro_desktop_watcher.sh [--interval 5]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
POLL_INTERVAL="${2:-5}"
LOG="/tmp/hakudokai_kuro_desktop_watcher.log"
HEALTH_FILE="/tmp/hakudokai_kuro_desktop_watcher.health"

# Direction 1: Desktop kuro → main_pc
PROCESSED_INBOUND="/tmp/hakudokai_kuro_desktop_inbound_processed.txt"
RESPONSE_INBOUND="/tmp/hakudokai_kuro_desktop_inbound_response.json"

# Direction 2: main_pc → Desktop kuro
PROCESSED_OUTBOUND="/tmp/hakudokai_kuro_desktop_outbound_processed.txt"
RESPONSE_OUTBOUND="/tmp/hakudokai_kuro_desktop_outbound_response.json"

POLL_COUNT=0
FAIL_COUNT=0

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

SUPABASE_API="${SUPABASE_URL}/rest/v1"

touch "$PROCESSED_INBOUND" "$PROCESSED_OUTBOUND"

log() {
  echo "[kuro_desktop][$(date '+%H:%M:%S')] $1" | tee -a "$LOG" >&2
}

GLOBAL_DISABLE="$HOME/.openclaw/global_disable"
WATCHER_DISABLE="$HOME/.openclaw/disable_kuro_desktop_watcher"

log "started (interval=${POLL_INTERVAL}s)"

while true; do
  sleep "$POLL_INTERVAL"

  # Manual disable flag check (Watcher Design Principles)
  if [ -f "$GLOBAL_DISABLE" ] || [ -f "$WATCHER_DISABLE" ]; then
    log "DISABLED by flag file — exiting gracefully"
    rm -f "$HEALTH_FILE"
    exit 0
  fi

  POLL_COUNT=$((POLL_COUNT + 1))

  # === Direction 1: Desktop kuro → main_pc ===
  # Poll for messages FROM kuro_desktop TO main_pc/broadcast
  if curl -sS --connect-timeout 10 --max-time 15 \
    "${SUPABASE_API}/pc_handshake?select=id,from_pc,to_pc,topic,content,priority,message_type,created_at&or=(to_pc.eq.main_pc,to_pc.eq.broadcast)&from_pc=eq.kuro_desktop&acknowledged_at=is.null&order=created_at.asc&limit=10" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -o "$RESPONSE_INBOUND" 2>/dev/null; then

    python3 "${SCRIPT_DIR}/shim/hakudokai/hakudokai_kuro_desktop_poll.py" \
      "$RESPONSE_INBOUND" \
      "$PROCESSED_INBOUND" \
      "$SCRIPT_DIR" \
      "$SUPABASE_API" \
      "$SUPABASE_SERVICE_ROLE_KEY" \
      "inbound" 2>&1 | tee -a "$LOG"
  fi

  # === Direction 2: main_pc → Desktop kuro ===
  # Poll for messages TO kuro_desktop that are unacknowledged
  if curl -sS --connect-timeout 10 --max-time 15 \
    "${SUPABASE_API}/pc_handshake?to_pc=eq.kuro_desktop&acknowledged_at=is.null&order=created_at.asc&limit=5" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -o "$RESPONSE_OUTBOUND" 2>/dev/null; then

    python3 "${SCRIPT_DIR}/shim/hakudokai/hakudokai_kuro_desktop_poll.py" \
      "$RESPONSE_OUTBOUND" \
      "$PROCESSED_OUTBOUND" \
      "$SCRIPT_DIR" \
      "$SUPABASE_API" \
      "$SUPABASE_SERVICE_ROLE_KEY" \
      "outbound" 2>&1 | tee -a "$LOG"
  fi

  # Heartbeat every 10 polls
  if [ $((POLL_COUNT % 10)) -eq 0 ]; then
    log "HEARTBEAT: polls=${POLL_COUNT}"
  fi

  # Health file
  cat > "$HEALTH_FILE" <<EOJSON
{
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "poll_count": ${POLL_COUNT},
  "status": "running",
  "interval": ${POLL_INTERVAL}
}
EOJSON

done
