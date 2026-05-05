#!/usr/bin/env bash
# diagnose.sh — Trouble Auto-Response Pipeline (CLAUDE.md S16)
# Usage: bash scripts/diagnose.sh [--dry-run] [--health] <ERR-CODE>
# Output: JSON structured diagnostics to stdout + dump file
set -euo pipefail

# === Constants ===
RUNBOOK_DIR="$(cd "$(dirname "$0")/../docs/runbooks" && pwd)"
DUMP_DIR="/tmp/error_dumps"
DEAD_LETTER_FILE="/tmp/dead_letter_errors.json"
DEDUPE_FILE="/tmp/diagnose_dedupe.json"
MORNING_DIGEST="/tmp/morning_digest.json"
ACTIONS_LOG="/tmp/runbook_actions.log"
DISABLE_FLAG="$HOME/.openclaw/disable_diagnose"
NIGHT_MODE_FLAG="$HOME/.openclaw/night_mode"
RETRY_CAP=3
DEDUPE_WINDOW=300  # 5 minutes

# === Argument Parsing ===
DRY_RUN=false
HEALTH_CHECK=false
ERROR_CODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --health)  HEALTH_CHECK=true; shift ;;
    -*)        echo "Unknown flag: $1" >&2; exit 1 ;;
    *)         ERROR_CODE="$1"; shift ;;
  esac
done

# === Utility Functions ===
gen_correlation_id() {
  python3 -c "import uuid; print(str(uuid.uuid4()))"
}

timestamp_iso() {
  date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z'
}

epoch_now() {
  date +%s
}

json_output() {
  local corr_id="$1" err_code="$2" status="$3" checks="$4" message="$5"
  cat <<ENDJSON
{
  "timestamp": "$(timestamp_iso)",
  "correlation_id": "$corr_id",
  "error_code": "$err_code",
  "status": "$status",
  "checks": $checks,
  "message": "$message",
  "dry_run": $DRY_RUN
}
ENDJSON
}

# Save dump file for later debugging
save_dump() {
  local corr_id="$1" content="$2"
  mkdir -p "$DUMP_DIR"
  local dump_path="$DUMP_DIR/diagnose_dump_${corr_id}.json"
  echo "$content" > "$dump_path"
  echo "$dump_path"
}

# Parse YAML front-matter field from runbook
parse_front_matter() {
  local file="$1" field="$2"
  sed -n '/^---/,/^---/p' "$file" | tr -d '\r' | grep "^${field}:" | head -1 | sed "s/^${field}: *//;s/\"//g"
}

# Check manual disable flag
check_disable() {
  if [[ -f "$DISABLE_FLAG" ]]; then
    echo '{"error":"diagnose.sh disabled via ~/.openclaw/disable_diagnose","status":"disabled"}' >&2
    exit 0
  fi
}

# Dedupe: skip if same error diagnosed within DEDUPE_WINDOW seconds
check_dedupe() {
  local err_code="$1"
  if [[ ! -f "$DEDUPE_FILE" ]]; then
    echo '{}' > "$DEDUPE_FILE"
  fi
  local now
  now=$(epoch_now)
  local last_run
  last_run=$(python3 -c "
import json, sys
with open('$DEDUPE_FILE') as f:
    d = json.load(f)
print(d.get('$err_code', 0))
" 2>/dev/null || echo "0")

  local elapsed=$(( now - last_run ))
  if [[ $elapsed -lt $DEDUPE_WINDOW && $elapsed -ge 0 ]]; then
    echo '{"status":"dedupe_skipped","error_code":"'"$err_code"'","seconds_since_last":'"$elapsed"'}'
    exit 0
  fi

  # Update dedupe record
  python3 -c "
import json
with open('$DEDUPE_FILE', 'r') as f:
    d = json.load(f)
d['$err_code'] = $now
with open('$DEDUPE_FILE', 'w') as f:
    json.dump(d, f)
"
}

# Night mode check: defer non-CRITICAL errors
check_night_mode() {
  local err_code="$1" severity="$2" night_policy="$3"
  if [[ ! -f "$NIGHT_MODE_FLAG" ]]; then
    return 0  # Not night mode, proceed normally
  fi

  # Night mode is ON
  if [[ "$night_policy" == "immediate" ]]; then
    return 0  # CRITICAL: always proceed
  fi

  # Defer to morning digest
  mkdir -p "$(dirname "$MORNING_DIGEST")"
  python3 -c "
import json, os, time
path = '$MORNING_DIGEST'
entry = {
    'error_code': '$err_code',
    'severity': '$severity',
    'deferred_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
    'epoch': int(time.time())
}
data = []
if os.path.exists(path):
    with open(path) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
data.append(entry)
with open(path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f'DEFERRED to morning_digest: {len(data)} entries total')
"
  echo "{\"status\":\"deferred_night_mode\",\"error_code\":\"$err_code\",\"severity\":\"$severity\"}"
  exit 0
}

# Add to dead-letter after retry_cap exhausted
add_dead_letter() {
  local err_code="$1" corr_id="$2" message="$3"
  python3 -c "
import json, os, time
path = '$DEAD_LETTER_FILE'
entry = {
    'error_code': '$err_code',
    'correlation_id': '$corr_id',
    'message': '$message',
    'timestamp': int(time.time()),
    'dead_lettered_at': time.strftime('%Y-%m-%dT%H:%M:%S%z')
}
data = []
if os.path.exists(path):
    with open(path) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
data.append(entry)
with open(path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"
}

# Extract code blocks from a runbook section
extract_commands() {
  local file="$1" section="$2"
  awk -v section="$section" '
    BEGIN { in_section=0; in_code=0 }
    /^## / { if (index($0, section)) { in_section=1 } else { in_section=0 } }
    in_section && /^```bash/ { in_code=1; next }
    in_section && in_code && /^```/ { in_code=0; next }
    in_section && in_code { print }
  ' "$file"
}

# === Health Check Mode ===
run_health_check() {
  local corr_id
  corr_id=$(gen_correlation_id)
  local results="[]"
  for runbook in "$RUNBOOK_DIR"/ERR-*.md; do
    local code
    code=$(parse_front_matter "$runbook" "error_code")
    local severity
    severity=$(parse_front_matter "$runbook" "severity")
    if [[ -z "$code" ]]; then continue; fi
    results=$(python3 -c "
import json
r = json.loads('$results' if '$results' != '[]' else '[]')
r.append({'error_code': '$code', 'severity': '$severity', 'runbook_exists': True})
print(json.dumps(r))
" 2>/dev/null || echo "$results")
  done

  local count
  count=$(find "$RUNBOOK_DIR" -name 'ERR-*.md' | wc -l)
  local output
  output=$(json_output "$corr_id" "HEALTH_CHECK" "ok" "$results" "All $count runbooks validated")
  save_dump "$corr_id" "$output" > /dev/null
  echo "$output"
}

# === Main Diagnosis ===
run_diagnosis() {
  local err_code="$1"
  local corr_id
  corr_id=$(gen_correlation_id)
  local runbook_path="$RUNBOOK_DIR/${err_code}.md"

  # Validate runbook exists
  if [[ ! -f "$runbook_path" ]]; then
    # Fallback: generic system check
    local checks
    checks=$(python3 -c "
import json, shutil, os
checks = []
# Disk
total, used, free = shutil.disk_usage('/')
checks.append({'name': 'disk_free_gb', 'value': round(free / (1024**3), 1), 'status': 'ok' if free > 1024**3 else 'warn'})
# Memory (rough)
try:
    with open('/proc/meminfo') as f:
        lines = f.readlines()
    mem_total = int([l for l in lines if 'MemTotal' in l][0].split()[1])
    mem_avail = int([l for l in lines if 'MemAvailable' in l][0].split()[1])
    checks.append({'name': 'mem_available_mb', 'value': round(mem_avail/1024), 'status': 'ok' if mem_avail > 512000 else 'warn'})
except Exception:
    checks.append({'name': 'mem_check', 'value': 'unavailable', 'status': 'skip'})
# Processes
checks.append({'name': 'load_avg', 'value': os.getloadavg()[0], 'status': 'ok' if os.getloadavg()[0] < 4 else 'warn'})
print(json.dumps(checks))
")
    local output
    output=$(json_output "$corr_id" "$err_code" "fallback_generic" "$checks" "No runbook found for $err_code - ran generic checks")
    save_dump "$corr_id" "$output" > /dev/null
    echo "$output"
    return 1
  fi

  # Parse runbook metadata
  local severity auto_fix night_policy
  severity=$(parse_front_matter "$runbook_path" "severity")
  auto_fix=$(parse_front_matter "$runbook_path" "auto_fix")
  night_policy=$(parse_front_matter "$runbook_path" "night_mode")

  # Night mode gate
  check_night_mode "$err_code" "$severity" "$night_policy"

  # Run diagnostic commands
  local diag_commands
  diag_commands=$(extract_commands "$runbook_path" "自動診断コマンド")
  local diag_output=""
  local checks="[]"

  if [[ -n "$diag_commands" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
      diag_output="[DRY-RUN] Would execute diagnostic commands from $runbook_path"
      checks=$(python3 -c "import json; print(json.dumps([{'name':'dry_run_diag','status':'skipped','detail':'$err_code diagnostics'}]))")
    else
      diag_output=$(bash -c "$diag_commands" 2>&1 || true)
      checks=$(python3 -c "
import json
output = '''$diag_output'''
lines = [l.strip() for l in output.splitlines() if l.strip()]
checks = []
for line in lines[:20]:
    if '=' in line:
        k, v = line.split('=', 1)
        checks.append({'name': k.lower(), 'value': v, 'status': 'info'})
    else:
        checks.append({'name': 'output', 'value': line[:200], 'status': 'info'})
if not checks:
    checks.append({'name': 'diag_result', 'value': 'no output', 'status': 'warn'})
print(json.dumps(checks))
" 2>/dev/null || echo '[{"name":"parse_error","status":"error"}]')
    fi
  fi

  # Auto-fix if enabled
  local fix_status="no_fix_attempted"
  if [[ "$auto_fix" == "true" ]]; then
    local fix_commands
    fix_commands=$(extract_commands "$runbook_path" "自動修復手順")

    if [[ -n "$fix_commands" ]]; then
      if [[ "$DRY_RUN" == "true" ]]; then
        fix_status="dry_run_skipped"
      else
        local attempt=0
        local fixed=false
        while [[ $attempt -lt $RETRY_CAP ]]; do
          attempt=$((attempt + 1))
          echo "$(timestamp_iso) [$corr_id] $err_code fix attempt $attempt/$RETRY_CAP" >> "$ACTIONS_LOG"
          if bash -c "$fix_commands" >> "$ACTIONS_LOG" 2>&1; then
            fixed=true
            fix_status="fixed_attempt_${attempt}"
            break
          fi
        done
        if [[ "$fixed" == "false" ]]; then
          fix_status="fix_failed_after_${RETRY_CAP}_attempts"
          add_dead_letter "$err_code" "$corr_id" "Auto-fix exhausted after $RETRY_CAP attempts"
        fi
      fi
    fi
  fi

  # Build final output
  local status="diagnosed"
  if [[ "$fix_status" == fix_failed_* ]]; then
    status="fix_failed"
  elif [[ "$fix_status" == fixed_* ]]; then
    status="auto_recovered"
  fi

  local output
  output=$(json_output "$corr_id" "$err_code" "$status" "$checks" "$fix_status")
  local dump_path
  dump_path=$(save_dump "$corr_id" "$output")

  echo "$output"

  # Log action
  echo "$(timestamp_iso) [$corr_id] $err_code status=$status fix=$fix_status dump=$dump_path" >> "$ACTIONS_LOG"

  # Return appropriate exit code
  if [[ "$status" == "fix_failed" ]]; then
    return 1
  fi
  return 0
}

# === Entry Point ===
check_disable

if [[ "$HEALTH_CHECK" == "true" ]]; then
  run_health_check
  exit $?
fi

if [[ -z "$ERROR_CODE" ]]; then
  echo "Usage: bash scripts/diagnose.sh [--dry-run] [--health] <ERR-CODE>" >&2
  echo "Example: bash scripts/diagnose.sh ERR-WATCHER-001" >&2
  exit 1
fi

# Validate error code format
if [[ ! "$ERROR_CODE" =~ ^ERR-[A-Z]+-[0-9]+$ ]]; then
  echo "{\"error\":\"Invalid error code format: $ERROR_CODE\",\"expected\":\"ERR-DOMAIN-NNN\"}" >&2
  exit 1
fi

check_dedupe "$ERROR_CODE"
run_diagnosis "$ERROR_CODE"
