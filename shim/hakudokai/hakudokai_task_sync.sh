#!/usr/bin/env bash
# hakudokai_task_sync.sh — タスクYAML自動同期 (MainPC → SecondPC via Supabase)
#
# queue/tasks/ を inotifywait で監視。SecondPC agent (ashigaru2, ashigaru8) の
# YAML が変更されたら、内容を Supabase pc_handshake に file_sync として送信。
# 参照される context ファイルも同梱する。
#
# SecondPC 側の secondpc_receiver_poll.py が file_sync を検知し、
# ローカルに YAML を書き出す。
#
# Usage: bash shim/hakudokai/hakudokai_task_sync.sh [--interval 2]

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INTERVAL=2
ONCE=false
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"
HEALTHCHECK_FILE="/tmp/hakudokai_task_sync.health"
HASH_DIR="/tmp/hakudokai_task_sync_hashes"

# SecondPC agents to watch
SECONDPC_AGENTS="ashigaru2 ashigaru8"

while [ $# -gt 0 ]; do
  case "$1" in
    --once) ONCE=true; shift ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Auto-source Supabase env
if [ -z "${SUPABASE_URL:-}" ] && [ -f "$HOME/.hakudokai/env" ]; then
  SUPABASE_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  SUPABASE_SERVICE_ROLE_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  export SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
fi

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo "[task_sync] ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required" >&2
  exit 1
fi

SUPABASE_API="${SUPABASE_URL}/rest/v1"
mkdir -p "$HASH_DIR"

SYNC_COUNT=0
FAIL_COUNT=0
START_TIME=$(date +%s)

log() {
  echo "[task_sync][$(date '+%H:%M:%S')] $1" >&2
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

# Upload files to Supabase pc_handshake as file_sync message
upload_file_sync() {
  local agent="$1"
  shift
  # Remaining args are file paths to sync

  # Build JSON payload with Python (handles escaping correctly)
  local payload
  payload=$(python3 -c "
import json, sys, os

files = []
for path in sys.argv[1:]:
    if os.path.exists(path):
        with open(path) as f:
            content = f.read()
        # Use relative path from project root
        rel = os.path.relpath(path, '$SCRIPT_DIR')
        files.append({'path': rel, 'content': content})

if not files:
    sys.exit(1)

payload = {
    'message_type': 'file_sync',
    'from_pc': 'main_pc',
    'to_pc': 'second_pc',
    'topic': 'file_sync_${agent}',
    'content': json.dumps({'target_agent': '${agent}', 'files': files}, ensure_ascii=False),
    'requires_response': False,
    'priority': 'high',
    'clinic_id': '${CLINIC_ID}',
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

# Extract project name from task YAML (project: field)
get_project_name() {
  local yaml_file="$1"
  grep '^\s*project:' "$yaml_file" 2>/dev/null | head -1 | sed 's/.*project:\s*//' | tr -d '\r" '
}

# Check and sync a single agent's task YAML
check_and_sync() {
  local agent="$1"
  local task_file="${SCRIPT_DIR}/queue/tasks/${agent}.yaml"

  if [ ! -f "$task_file" ]; then
    return 0
  fi

  local current prev
  current=$(file_hash "$task_file")
  prev=$(prev_hash "$task_file")

  if [ "$current" = "$prev" ] && [ -n "$prev" ]; then
    return 0  # No change
  fi

  log "CHANGE detected: ${agent}.yaml (hash: ${prev:0:8}→${current:0:8})"

  # Collect files to sync
  local files_to_sync=("$task_file")

  # Check for referenced context file
  local project_name
  project_name=$(get_project_name "$task_file")
  if [ -n "$project_name" ]; then
    local ctx_file="${SCRIPT_DIR}/context/${project_name}.md"
    if [ -f "$ctx_file" ]; then
      # Only include context if it also changed (or first sync)
      local ctx_current ctx_prev
      ctx_current=$(file_hash "$ctx_file")
      ctx_prev=$(prev_hash "$ctx_file")
      if [ "$ctx_current" != "$ctx_prev" ] || [ -z "$ctx_prev" ]; then
        files_to_sync+=("$ctx_file")
        save_hash "$ctx_file" "$ctx_current"
        log "  + context/${project_name}.md"
      fi
    fi
  fi

  # Upload
  if upload_file_sync "$agent" "${files_to_sync[@]}"; then
    save_hash "$task_file" "$current"
    SYNC_COUNT=$((SYNC_COUNT + 1))
    log "SYNCED: ${agent} (${#files_to_sync[@]} files)"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    log "SYNC FAILED: ${agent}"
  fi
}

# Also sync CLAUDE.md if changed (needed by all SecondPC agents)
check_claudemd() {
  local claudemd="${SCRIPT_DIR}/CLAUDE.md"
  if [ ! -f "$claudemd" ]; then
    return 0
  fi

  local current prev
  current=$(file_hash "$claudemd")
  prev=$(prev_hash "$claudemd")

  if [ "$current" = "$prev" ] && [ -n "$prev" ]; then
    return 0
  fi

  log "CHANGE detected: CLAUDE.md"

  # Upload for all SecondPC agents
  for agent in $SECONDPC_AGENTS; do
    upload_file_sync "$agent" "$claudemd"
  done
  save_hash "$claudemd" "$current"
}

log "started (interval=${INTERVAL}s, agents: ${SECONDPC_AGENTS})"
echo "{\"alive\":true,\"ts\":$(date +%s),\"syncs\":0,\"fails\":0}" > "$HEALTHCHECK_FILE"

# Initial sync: upload current state
log "Initial sync..."
for agent in $SECONDPC_AGENTS; do
  check_and_sync "$agent"
done
check_claudemd
log "Initial sync complete (synced=${SYNC_COUNT}, failed=${FAIL_COUNT})"

if [ "$ONCE" = "true" ]; then
  exit 0
fi

# Use inotifywait if available, otherwise fall back to polling
if command -v inotifywait &>/dev/null; then
  log "Using inotifywait mode"

  while true; do
    # Watch for modifications to task YAMLs and CLAUDE.md
    inotifywait -q -t 30 \
      -e modify -e create -e moved_to \
      "${SCRIPT_DIR}/queue/tasks/" \
      "${SCRIPT_DIR}/CLAUDE.md" \
      2>/dev/null || true

    # Check all SecondPC agents
    for agent in $SECONDPC_AGENTS; do
      check_and_sync "$agent"
    done
    check_claudemd

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
    check_claudemd

    # Healthcheck every 15 cycles
    if [ $(( (SYNC_COUNT + FAIL_COUNT) % 15 )) -eq 0 ] || [ $SYNC_COUNT -eq 0 ]; then
      local_uptime=$(($(date +%s) - START_TIME))
      echo "{\"alive\":true,\"ts\":$(date +%s),\"uptime\":${local_uptime},\"syncs\":${SYNC_COUNT},\"fails\":${FAIL_COUNT}}" > "$HEALTHCHECK_FILE"
    fi
  done
fi
