#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# shogun_report_watcher.sh — 監査者報告 fallback 通知 watcher
#
# 目的:
#   家康/本多/黒田/真田/竹中 の各 report.yaml が更新された際、
#   信長 inbox に通知を fallback 配信する。
#   (本多 v3 HND-T1V3-004 要求の verdict 通知漏れ対策)
#
# 設計:
#   - inotifywait -m で queue/reports/ ディレクトリを常時監視
#   - 対象 5 ファイル (ieyasu/honda/kuroda/sanada/takenaka_report.yaml) を抽出
#   - modify / close_write / moved_to イベント検知時に通知
#   - dedup: sha256 head8 を state.json に保存、同一なら skip
#   - cooldown: last_notified_ts から 60s 未満なら skip
#   - F004 順守: sleep polling 禁止、inotifywait のみ
#   - graceful shutdown: SIGINT/SIGTERM で inotifywait を kill
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS_DIR="${SHOGUN_REPORT_WATCHER_DIR:-$SCRIPT_DIR/queue/reports}"
STATE_FILE="${SHOGUN_REPORT_WATCHER_STATE:-/tmp/.shogun_report_watcher_state.json}"
COOLDOWN_SEC="${SHOGUN_REPORT_WATCHER_COOLDOWN:-60}"
INBOX_WRITE="$SCRIPT_DIR/scripts/inbox_write.sh"
LOG_PREFIX="[shogun_report_watcher]"

TARGETS=(
  "ieyasu_report.yaml"
  "honda_report.yaml"
  "kuroda_report.yaml"
  "sanada_report.yaml"
  "takenaka_report.yaml"
)

# Pre-flight checks
if ! command -v inotifywait >/dev/null 2>&1; then
  echo "$LOG_PREFIX ERROR: inotifywait not found. Install: sudo apt install inotify-tools" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "$LOG_PREFIX ERROR: python3 not found (required for state management)" >&2
  exit 1
fi
if ! command -v sha256sum >/dev/null 2>&1; then
  echo "$LOG_PREFIX ERROR: sha256sum not found" >&2
  exit 1
fi
if [ ! -x "$INBOX_WRITE" ] && [ ! -f "$INBOX_WRITE" ]; then
  echo "$LOG_PREFIX ERROR: inbox_write.sh not found at $INBOX_WRITE" >&2
  exit 1
fi
mkdir -p "$REPORTS_DIR"

# Initialize state file
if [ ! -f "$STATE_FILE" ]; then
  echo '{}' > "$STATE_FILE"
fi

# ─── helpers ────────────────────────────────────────────────────
is_target() {
  local name="$1"
  for t in "${TARGETS[@]}"; do
    [ "$name" = "$t" ] && return 0
  done
  return 1
}

get_checksum() {
  local f="$1"
  if [ -f "$f" ]; then
    sha256sum "$f" | awk '{print substr($1,1,8)}'
  else
    echo "missing"
  fi
}

# Best-effort: extract latest entry id from YAML report.
# Different reports use different field names; check audit_id → task_id → id → hash.
# Returns the LAST occurrence (latest entry in append-style logs).
get_latest_audit_id() {
  local f="$1"
  [ -f "$f" ] || { echo "unknown"; return; }
  local id
  for field in audit_id task_id id; do
    id=$(grep -E "^[[:space:]]*-?[[:space:]]*${field}:[[:space:]]*" "$f" 2>/dev/null \
         | tail -1 \
         | sed -E "s/^[[:space:]]*-?[[:space:]]*${field}:[[:space:]]*//; s/[\"']//g; s/[[:space:]]+$//; s/#.*$//; s/[[:space:]]+$//")
    if [ -n "$id" ]; then
      echo "$id"
      return 0
    fi
  done
  echo "unknown"
}

# state I/O via python3 (jq not assumed)
state_read_field() {
  local key="$1" field="$2"
  python3 - "$STATE_FILE" "$key" "$field" <<'PY'
import json, sys
path, key, field = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    with open(path) as f:
        d = json.load(f)
except Exception:
    d = {}
entry = d.get(key) or {}
print(entry.get(field, ""))
PY
}

state_write() {
  local key="$1" checksum="$2" last_ts="$3"
  python3 - "$STATE_FILE" "$key" "$checksum" "$last_ts" <<'PY'
import json, sys, os, tempfile
path, key, checksum, last_ts = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
try:
    with open(path) as f:
        d = json.load(f)
except Exception:
    d = {}
d[key] = {"checksum": checksum, "last_notified_ts": int(last_ts)}
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", prefix=".sw_", suffix=".tmp")
try:
    with os.fdopen(fd, "w") as f:
        json.dump(d, f)
    os.replace(tmp, path)
except Exception:
    if os.path.exists(tmp):
        os.unlink(tmp)
    raise
PY
}

notify_shogun() {
  local report_name="$1" audit_id="$2"
  local content="[${report_name}] 更新検知、最新 audit_id=${audit_id}"
  if [ -x "$INBOX_WRITE" ]; then
    "$INBOX_WRITE" shogun "$content" notification shogun_report_watcher \
      || echo "$LOG_PREFIX WARN: inbox_write failed for $report_name" >&2
  else
    bash "$INBOX_WRITE" shogun "$content" notification shogun_report_watcher \
      || echo "$LOG_PREFIX WARN: inbox_write failed for $report_name" >&2
  fi
}

handle_event() {
  local report_name="$1"
  local path="$REPORTS_DIR/$report_name"
  local checksum prev_checksum last_ts now diff audit_id

  checksum=$(get_checksum "$path")
  prev_checksum=$(state_read_field "$report_name" "checksum")
  last_ts=$(state_read_field "$report_name" "last_notified_ts")
  now=$(date +%s)

  # dedup: same content checksum → skip
  if [ -n "$prev_checksum" ] && [ "$prev_checksum" = "$checksum" ]; then
    echo "$LOG_PREFIX dedup skip: $report_name (checksum=$checksum)" >&2
    return 0
  fi

  # cooldown: last notification within COOLDOWN_SEC → skip
  if [ -n "$last_ts" ]; then
    diff=$(( now - last_ts ))
    if [ "$diff" -lt "$COOLDOWN_SEC" ]; then
      echo "$LOG_PREFIX cooldown skip: $report_name (${diff}s < ${COOLDOWN_SEC}s)" >&2
      # update checksum anyway so we don't re-notify same content after cooldown
      state_write "$report_name" "$checksum" "$last_ts"
      return 0
    fi
  fi

  audit_id=$(get_latest_audit_id "$path")
  echo "$LOG_PREFIX notify: $report_name checksum=$checksum audit_id=$audit_id" >&2
  notify_shogun "$report_name" "$audit_id"
  state_write "$report_name" "$checksum" "$now"
}

# ─── graceful shutdown ──────────────────────────────────────────
WATCH_PID=""
shutdown() {
  echo "$LOG_PREFIX shutdown signal received, terminating watcher..." >&2
  if [ -n "$WATCH_PID" ] && kill -0 "$WATCH_PID" 2>/dev/null; then
    kill "$WATCH_PID" 2>/dev/null || true
    wait "$WATCH_PID" 2>/dev/null || true
  fi
  exit 0
}
trap shutdown SIGINT SIGTERM

# ─── main loop ──────────────────────────────────────────────────
echo "$LOG_PREFIX started — dir=$REPORTS_DIR cooldown=${COOLDOWN_SEC}s state=$STATE_FILE" >&2

# Watch parent dir so we catch creates/atomic-writes (rename) for files that
# may not exist yet. inotifywait -m is event-driven, no sleep polling (F004).
# Use process substitution + FD3 so we can capture inotifywait's PID for graceful shutdown.
exec 3< <(inotifywait -m -q \
  -e modify -e close_write -e moved_to -e create \
  --format '%f|%e' \
  "$REPORTS_DIR")
WATCH_PID=$!

while IFS='|' read -r -u 3 fname events; do
  [ -z "$fname" ] && continue
  is_target "$fname" || continue
  echo "$LOG_PREFIX event: file=$fname events=$events" >&2
  handle_event "$fname" || echo "$LOG_PREFIX WARN: handle_event error for $fname" >&2
done

shutdown
