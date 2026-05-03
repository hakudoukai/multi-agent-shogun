#!/usr/bin/env bash
# hakudokai_fukuincho_watcher.sh — 副医院長→将軍 Supabase通信路 watcher
#
# pc_handshake (from_pc='fukuincho', to_pc='main_pc' OR 'broadcast')
# を5秒間隔でSELECTし、未読メッセージを shogun inbox に転記。
#
# 前提: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY が環境変数にセットされていること
# Usage: bash shim/hakudokai/hakudokai_fukuincho_watcher.sh [--once] [--interval 5]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
POLL_SCRIPT="${SCRIPT_DIR}/shim/hakudokai/hakudokai_fukuincho_poll.py"
INTERVAL=5
ONCE=false
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"

while [ $# -gt 0 ]; do
  case "$1" in
    --once) ONCE=true; shift ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "[fukuincho_watcher] ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required" >&2
  exit 1
fi

SUPABASE_API="${SUPABASE_URL}/rest/v1"
PROCESSED_FILE="/tmp/hakudokai_fukuincho_watcher_processed.txt"
RESPONSE_TMP="/tmp/hakudokai_fukuincho_watcher_response.json"
touch "$PROCESSED_FILE"

echo "[fukuincho_watcher] started (interval=${INTERVAL}s, once=${ONCE}, clinic=${CLINIC_ID})" >&2

while true; do
  curl -sS \
    "${SUPABASE_API}/pc_handshake?select=id,from_pc,to_pc,topic,content,priority,message_type,created_at&or=(to_pc.eq.main_pc,to_pc.eq.broadcast)&from_pc=eq.fukuincho&acknowledged_at=is.null&clinic_id=eq.${CLINIC_ID}&order=created_at.asc&limit=10" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -o "$RESPONSE_TMP" 2>/dev/null || { echo "[fukuincho_watcher] curl error" >&2; sleep "$INTERVAL"; continue; }

  python3 "$POLL_SCRIPT" "$RESPONSE_TMP" "$PROCESSED_FILE" "$SCRIPT_DIR" "$SUPABASE_API" "$SUPABASE_SERVICE_ROLE_KEY" 2>&1 || true

  if [ "$ONCE" = "true" ]; then
    break
  fi
  sleep "$INTERVAL"
done
