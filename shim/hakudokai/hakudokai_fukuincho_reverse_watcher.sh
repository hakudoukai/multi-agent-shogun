#!/usr/bin/env bash
# hakudokai_fukuincho_reverse_watcher.sh — shogun→副医院長 通知デーモン
#
# shogun が Supabase pc_handshake に INSERT したメッセージを
# 副医院長 (fukuincho) CLI の inbox に配信し、tmux nudge で起こす。
#
# 既存の hakudokai_fukuincho_watcher.sh の逆方向版。
#
# Usage: bash shim/hakudokai/hakudokai_fukuincho_reverse_watcher.sh [--interval 5]
# 前提: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 環境変数

# ★単一 instance guard (副院長令 24a47356、defense-in-depth)★:
#   gunshi 当初 真因確定 msg_141706「reverse_watcher 2 instance 同時稼働」は msg_141814
#   で撤回された (pgrep -fc が自身 bash の relay 文中 watcher 名 string を誤カウント、
#   ps -eo args 精査で実 watcher は 1 instance のみ確認、PID 3293704)。
#   ただし「watcher に flock -n 単一 instance guard が無いのは事実 (将来 多重起動時の
#   予防として有用)」(gunshi msg_141814 verbatim) ゆえ、★将来予防策・深度防御として★
#   flock -n を追加する。OS レベル単一 instance を強制、2 番目以降の起動は即座 exit 0
#   (race 根絶)。現時点の二重投稿真因ではない (前 turn 認識訂正済) が land 妥当。
_WATCHER_LOCK_FILE="/tmp/hakudokai_fukuincho_reverse_watcher.lock"
exec 200>"$_WATCHER_LOCK_FILE"
if ! flock -n 200; then
    echo "[$(date -Iseconds)] [reverse_watcher] another instance running (lock=$_WATCHER_LOCK_FILE), exit 0" >&2
    exit 0
fi

# ★SIGTERM/SIGINT handler (副院長令 fd832bcc)★:
#   systemd 等から graceful な停止指示が来た時に flock を自動解放、exit 0 で終了。
#   trap 設定後の bash exit で fd 200 (exec ... > 経由) は自動 close → flock 自動解放。
#   message は journalctl で観測可能、shutdown 起因の意図停止と異常停止の区別を可能にする。
_watcher_graceful_exit() {
    echo "[$(date -Iseconds)] [reverse_watcher] $1 received, graceful exit 0 (lock auto-released)" >&2
    exit 0
}
trap '_watcher_graceful_exit SIGTERM' SIGTERM
trap '_watcher_graceful_exit SIGINT' SIGINT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$SCRIPT_DIR/shim/hakudokai/lib/sb_auth.sh"
POLL_INTERVAL="${2:-5}"
PROCESSED_FILE="/tmp/hakudokai_fukuincho_reverse_processed.txt"
HEALTH_FILE="/tmp/hakudokai_fukuincho_reverse_health.json"
LOG="/tmp/hakudokai_fukuincho_reverse_watcher.log"
FUKUINCHO_PANE="${FUKUINCHO_PANE:-fukuincho:0.0}"
FAIL_COUNT=0
MAX_FAILS=5
POLL_COUNT=0

# Manual disable flags (Watcher Design Principles 必須項目)
GLOBAL_DISABLE="$HOME/.openclaw/global_disable"
WATCHER_DISABLE="$HOME/.openclaw/disable_fukuincho_reverse_watcher"

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

  # Manual disable flag check (Watcher Design Principles 必須項目)
  if [ -f "$GLOBAL_DISABLE" ] || [ -f "$WATCHER_DISABLE" ]; then
    log "DISABLED by flag file — exiting gracefully"
    rm -f "$HEALTH_FILE"
    exit 0
  fi

  POLL_COUNT=$((POLL_COUNT + 1))

  # Query: messages TO fukuincho that are not yet acknowledged
  RESPONSE=$(sb_curl -sS -w "\n%{http_code}" \
    "${SUPABASE_URL}/rest/v1/pc_handshake?to_pc=eq.fukuincho&acknowledged_at=is.null&order=created_at.asc&limit=5" \
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
  env SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
    python3 "${SCRIPT_DIR}/shim/hakudokai/hakudokai_fukuincho_reverse_poll.py" \
    "$TEMP_RESPONSE" \
    "$PROCESSED_FILE" \
    "$SCRIPT_DIR" \
    "${SUPABASE_URL}" \
    "$FUKUINCHO_PANE"

  # ntfy notification for 理事長 (Desktop副医院長は自動受信できないため)
  python3 "${SCRIPT_DIR}/shim/hakudokai/hakudokai_escalation.py" \
    notify --level L2 --summary "副医院長宛メッセージ到着" 2>/dev/null &

  # Heartbeat log every 10 polls
  if [ $((POLL_COUNT % 10)) -eq 0 ]; then
    log "HEARTBEAT: polls=${POLL_COUNT}, fails=${FAIL_COUNT}"
  fi

  update_health
done
