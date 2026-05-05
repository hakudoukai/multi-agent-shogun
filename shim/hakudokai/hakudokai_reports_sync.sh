#!/usr/bin/env bash
# hakudokai_reports_sync.sh — レポート/タスク状態 逆方向同期 (SecondPC → MainPC via Supabase)
#
# SecondPC上で稼働。queue/reports/ と queue/tasks/ を監視。
# ashigaru2/8 のレポートやタスクstatus更新を検知し、
# Supabase pc_handshake に file_sync として送信。
# MainPC側の secondpc_watcher_poll.py が file_sync を検知し、ローカルに書き出す。
#
# task_sync.sh のミラー実装。方向と監視対象のみ差分。
#
# Usage: bash shim/hakudokai/hakudokai_reports_sync.sh [--interval 2]

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INTERVAL=2
ONCE=false
HEALTHCHECK_FILE="/tmp/hakudokai_reports_sync.health"
HASH_DIR="/tmp/hakudokai_reports_sync_hashes"

# SecondPC agents whose reports/tasks to watch
SECONDPC_AGENTS="ashigaru2 ashigaru8"

while [ $# -gt 0 ]; do
  case "$1" in
    --once) ONCE=true; shift ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Auto-source Supabase env + clinic_id (L1/G1 fix)
if [ -f "$HOME/.hakudokai/env" ]; then
  [ -z "${SUPABASE_URL:-}" ] && SUPABASE_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ] && SUPABASE_SERVICE_ROLE_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  [ -z "${HAKUDOKAI_CLINIC_ID:-}" ] && HAKUDOKAI_CLINIC_ID=$(grep '^HAKUDOKAI_CLINIC_ID=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  export SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
fi
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-}"

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "[reports_sync] ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required" >&2
  exit 1
fi

# GS1 fix: clinic_id fail-fast (same strictness as SUPABASE credentials)
if [ -z "$CLINIC_ID" ]; then
  echo "[reports_sync] ERROR: HAKUDOKAI_CLINIC_ID required (set in ~/.hakudokai/env or env var)" >&2
  exit 1
fi

SUPABASE_API="${SUPABASE_URL}/rest/v1"
mkdir -p "$HASH_DIR"

SYNC_COUNT=0
FAIL_COUNT=0
START_TIME=$(date +%s)
MAX_FILE_BYTES=1048576  # 1MB — S1 fix: prevent DoS via oversized files

log() {
  echo "[reports_sync][$(date '+%H:%M:%S')] $1" >&2
}

# Compute md5 hash of a file (returns empty if file doesn't exist)
file_hash() {
  if [ -f "$1" ]; then
    md5sum "$1" 2>/dev/null | cut -d' ' -f1
  else
    echo ""
  fi
}

# Read previous hash for a file
prev_hash() {
  local hash_file="${HASH_DIR}/$(echo "$1" | md5sum | cut -d' ' -f1)"
  if [ -f "$hash_file" ]; then
    cat "$hash_file"
  else
    echo ""
  fi
}

# Save current hash
save_hash() {
  local hash_file="${HASH_DIR}/$(echo "$1" | md5sum | cut -d' ' -f1)"
  echo "$2" > "$hash_file"
}

# Upload files to Supabase pc_handshake as file_sync message (reverse direction)
upload_file_sync() {
  local agent="$1"
  shift
  # Remaining args are file paths to sync

  # S1 fix: check file sizes before upload
  local f_path
  for f_path in "$@"; do
    if [ -f "$f_path" ]; then
      local fsize
      fsize=$(stat -c%s "$f_path" 2>/dev/null || echo 0)
      if [ "$fsize" -gt "$MAX_FILE_BYTES" ]; then
        log "ERROR: file too large (${fsize} bytes > ${MAX_FILE_BYTES}): $f_path"
        return 1
      fi
    fi
  done

  # SR6 fix: pass variables via env, not bash string interpolation in Python
  local payload
  payload=$(SYNC_SCRIPT_DIR="$SCRIPT_DIR" SYNC_AGENT="$agent" SYNC_CLINIC_ID="$CLINIC_ID" \
    python3 -c "
import json, sys, os

script_dir = os.environ['SYNC_SCRIPT_DIR']
agent = os.environ['SYNC_AGENT']
clinic_id = os.environ['SYNC_CLINIC_ID']

files = []
for path in sys.argv[1:]:
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            content = f.read()
        rel = os.path.relpath(path, script_dir)
        files.append({'path': rel, 'content': content})

if not files:
    sys.exit(1)

payload = {
    'message_type': 'file_sync',
    'from_pc': 'second_pc',
    'to_pc': 'main_pc',
    'topic': f'reports_sync_{agent}',
    'content': json.dumps({'target_agent': agent, 'files': files}, ensure_ascii=False),
    'requires_response': False,
    'priority': 'high',
    'clinic_id': clinic_id,
    'bypass_5round_limit': False,
    'is_meta_only': False
}
print(json.dumps(payload, ensure_ascii=False))
" "$@" 2>/dev/null)

  if [ -z "$payload" ]; then
    log "WARN: no files to sync for $agent"
    return 1
  fi

  # POST to Supabase
  local http_code
  http_code=$(curl -sS -o /dev/null -w "%{http_code}" -X POST \
    "${SUPABASE_API}/pc_handshake" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "$payload" 2>/dev/null)

  if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
    return 0
  else
    log "UPLOAD FAILED: HTTP $http_code for $agent"
    return 1
  fi
}

# Check and sync a single agent's report + task YAML
check_and_sync() {
  local agent="$1"
  local report_file="${SCRIPT_DIR}/queue/reports/${agent}_report.yaml"
  local task_file="${SCRIPT_DIR}/queue/tasks/${agent}.yaml"
  local files_to_sync=()
  local changed=false

  # SR8 fix: snapshot hashes before upload to avoid race condition
  local report_hash="" task_hash=""

  # Check report file
  if [ -f "$report_file" ]; then
    report_hash=$(file_hash "$report_file")
    local prev
    prev=$(prev_hash "$report_file")
    if [ "$report_hash" != "$prev" ] || [ -z "$prev" ]; then
      files_to_sync+=("$report_file")
      changed=true
      log "CHANGE detected: ${agent}_report.yaml (hash: ${prev:0:8}→${report_hash:0:8})"
    fi
  fi

  # Check task file (status updates: assigned→done etc.)
  if [ -f "$task_file" ]; then
    task_hash=$(file_hash "$task_file")
    local prev
    prev=$(prev_hash "$task_file")
    if [ "$task_hash" != "$prev" ] || [ -z "$prev" ]; then
      files_to_sync+=("$task_file")
      changed=true
      log "CHANGE detected: ${agent}.yaml (hash: ${prev:0:8}→${task_hash:0:8})"
    fi
  fi

  if [ "$changed" = "false" ]; then
    return 0
  fi

  # Upload
  if upload_file_sync "$agent" "${files_to_sync[@]}"; then
    # Save pre-computed snapshot hashes (not re-read after upload)
    [ -n "$report_hash" ] && save_hash "$report_file" "$report_hash"
    [ -n "$task_hash" ] && save_hash "$task_file" "$task_hash"
    SYNC_COUNT=$((SYNC_COUNT + 1))
    log "SYNCED: ${agent} (${#files_to_sync[@]} files)"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    log "SYNC FAILED: ${agent}"
  fi
}

log "started (interval=${INTERVAL}s, agents: ${SECONDPC_AGENTS})"
echo "{\"alive\":true,\"ts\":$(date +%s),\"syncs\":0,\"fails\":0}" > "$HEALTHCHECK_FILE"

# Initial sync: upload current state
log "Initial sync..."
for agent in $SECONDPC_AGENTS; do
  check_and_sync "$agent"
done
log "Initial sync complete (synced=${SYNC_COUNT}, failed=${FAIL_COUNT})"

if [ "$ONCE" = "true" ]; then
  exit 0
fi

# Use inotifywait if available, otherwise fall back to polling
if command -v inotifywait &>/dev/null; then
  log "Using inotifywait mode"

  while true; do
    # Watch for modifications to reports and task YAMLs
    inotifywait -q -t 30 \
      -e modify -e create -e moved_to \
      "${SCRIPT_DIR}/queue/reports/" \
      "${SCRIPT_DIR}/queue/tasks/" \
      2>/dev/null || true

    # Check all SecondPC agents
    for agent in $SECONDPC_AGENTS; do
      check_and_sync "$agent"
    done

    # Healthcheck
    local_uptime=$(($(date +%s) - START_TIME))
    echo "{\"alive\":true,\"ts\":$(date +%s),\"uptime\":${local_uptime},\"syncs\":${SYNC_COUNT},\"fails\":${FAIL_COUNT}}" > "$HEALTHCHECK_FILE"
  done
else
  log "inotifywait not available, using poll mode (${INTERVAL}s)"

  while true; do
    sleep "$INTERVAL"

    for agent in $SECONDPC_AGENTS; do
      check_and_sync "$agent"
    done

    # Healthcheck every cycle (SR10 fix: not count-dependent)
    local_uptime=$(($(date +%s) - START_TIME))
    echo "{\"alive\":true,\"ts\":$(date +%s),\"uptime\":${local_uptime},\"syncs\":${SYNC_COUNT},\"fails\":${FAIL_COUNT}}" > "$HEALTHCHECK_FILE"
  done
fi
