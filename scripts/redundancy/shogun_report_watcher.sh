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
#     SRW-C1 (cycle2): cooldown 中の新規 checksum は pending_checksum として保留、
#       次 event 時に cooldown 経過していれば後送通知 (= 通知漏れ fallback の漏れ防止)
#   - SRW-C2 (cycle2): flock singleton lock — 多重起動禁止、二重通知防止
#   - F004 順守: sleep polling 禁止、inotifywait のみ
#   - graceful shutdown: SIGINT/SIGTERM で inotifywait を kill + lock 解放
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPORTS_DIR="${SHOGUN_REPORT_WATCHER_DIR:-$SCRIPT_DIR/queue/reports}"
STATE_FILE="${SHOGUN_REPORT_WATCHER_STATE:-/tmp/.shogun_report_watcher_state.json}"
LOCK_FILE="${SHOGUN_REPORT_WATCHER_LOCK:-/tmp/.shogun_report_watcher.lock}"
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
if ! command -v flock >/dev/null 2>&1; then
  echo "$LOG_PREFIX ERROR: flock not found (required for singleton lock)" >&2
  exit 1
fi
mkdir -p "$REPORTS_DIR"

# ─── SRW-C2 / HND-SRW-C2: singleton flock lock ────────────────
# Prevent multi-instance dual notifications. Acquire exclusive lock on FD 9.
# Released automatically on process exit (any reason).
exec 9>"$LOCK_FILE" || {
  echo "$LOG_PREFIX ERROR: cannot open lock file $LOCK_FILE" >&2
  exit 1
}
if ! flock -n 9; then
  echo "$LOG_PREFIX another instance already running (lock=$LOCK_FILE), exit 0" >&2
  exit 0
fi
echo "$LOG_PREFIX singleton lock acquired (lock=$LOCK_FILE, fd=9)" >&2

# ─── HND-SRW-C2: state critical section lock ──────────────────
# Wrap state read+modify+write+notify under FD 8 flock to prevent lost
# updates from any external process that might also touch STATE_FILE.
# Within our singleton, this is also a no-op safety net.
STATE_LOCK_FILE="${STATE_FILE}.lock"
exec 8>"$STATE_LOCK_FILE" || {
  echo "$LOG_PREFIX ERROR: cannot open state lock file $STATE_LOCK_FILE" >&2
  exit 1
}

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

# SRW-C4 / HND-SRW-C4: extract latest top-level audit/task id via yaml.safe_load.
# Goal: avoid grep mis-picking nested 'id:' (e.g. inside finding lists).
# Strategy:
#   1. Parse YAML with yaml.safe_load (already required by other scripts).
#   2. If document is a mapping: prefer audit_id > task_id > id at top-level.
#      Else if mapping has list values, prefer the LAST item's audit_id/task_id/id.
#   3. If document is a list: take the LAST item's audit_id/task_id/id.
#   4. Fallback: legacy regex (preserved for malformed yaml resilience).
#   5. Return "unknown" if nothing found.
get_latest_audit_id() {
  local f="$1"
  [ -f "$f" ] || { echo "unknown"; return; }
  local id
  id=$(python3 - "$f" <<'PY' 2>/dev/null
import sys, yaml
path = sys.argv[1]
try:
    with open(path) as fh:
        d = yaml.safe_load(fh)
except Exception:
    sys.exit(0)

def pick(obj):
    if isinstance(obj, dict):
        for k in ("audit_id", "task_id", "id"):
            v = obj.get(k)
            if isinstance(v, (str, int)):
                return str(v)
        # check list-valued children, take last
        for v in obj.values():
            if isinstance(v, list) and v:
                got = pick(v[-1])
                if got:
                    return got
        return None
    if isinstance(obj, list) and obj:
        return pick(obj[-1])
    return None

got = pick(d)
if got:
    print(got)
PY
  )
  if [ -n "$id" ]; then
    echo "$id"
    return 0
  fi
  # Fallback: legacy grep (cycle1 path), preserved for malformed yaml resilience.
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

# state I/O via python3 (jq not assumed). Schema (cycle2 v2):
#   {
#     "<report_name>": {
#       "last_notified_checksum": "<sha256-head8>" | "",
#       "last_notified_ts": <int> | 0,
#       "pending_checksum": "<sha256-head8>" | null,  # SRW-C1: cooldown 中保留
#       "pending_since": <int> | null                 # HND-SRW-C1: 保留開始時刻
#     }
#   }
# Backward compat: legacy "checksum" field (cycle1) maps to last_notified_checksum.
state_read_entry() {
  local key="$1"
  python3 - "$STATE_FILE" "$key" <<'PY'
import json, sys
path, key = sys.argv[1], sys.argv[2]
try:
    with open(path) as f:
        d = json.load(f)
except Exception:
    d = {}
e = d.get(key) or {}
last_ck = e.get("last_notified_checksum", e.get("checksum", "")) or ""
last_ts = e.get("last_notified_ts", 0) or 0
pending = e.get("pending_checksum") or ""
pending_since = e.get("pending_since", 0) or 0
# tab-separated for safe parsing in bash
print(f"{last_ck}\t{last_ts}\t{pending}\t{pending_since}")
PY
}

state_write_entry() {
  local key="$1" last_ck="$2" last_ts="$3" pending="$4" pending_since="$5"
  python3 - "$STATE_FILE" "$key" "$last_ck" "$last_ts" "$pending" "$pending_since" <<'PY'
import json, sys, os, tempfile
path, key, last_ck, last_ts, pending, pending_since = sys.argv[1:]
try:
    with open(path) as f:
        d = json.load(f)
except Exception:
    d = {}
entry = {
    "last_notified_checksum": last_ck,
    "last_notified_ts": int(last_ts) if last_ts else 0,
    "pending_checksum": pending if pending else None,
    "pending_since": int(pending_since) if pending_since else None,
}
d[key] = entry
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
  local current last_ck last_ts pending pending_since entry rest1 rest2 now diff audit_id

  # HND-SRW-C2: enter critical section under state lock (FD 8). All state
  # read+modify+write+notify happen exactly once per event under this lock.
  flock -x 8

  current=$(get_checksum "$path")
  entry=$(state_read_entry "$report_name")
  # parse tab-separated state: last_ck \t last_ts \t pending \t pending_since
  last_ck="${entry%%	*}"
  rest1="${entry#*	}"
  last_ts="${rest1%%	*}"
  rest2="${rest1#*	}"
  pending="${rest2%%	*}"
  pending_since="${rest2#*	}"
  # normalize when fields are missing (e.g. legacy schema)
  [ "$pending" = "$rest2" ] && pending=""
  [ "$pending_since" = "$rest2" ] && pending_since=""

  now=$(date +%s)

  # ─── dedup ───
  # SRW-C1: compare ONLY against last_notified_checksum (not pending).
  # pending is by definition undelivered → "current == pending" is a notify-eligible state.
  if [ -n "$last_ck" ] && [ "$last_ck" = "$current" ]; then
    echo "$LOG_PREFIX dedup skip: $report_name (last_notified=$current)" >&2
    flock -u 8
    return 0
  fi

  # ─── cooldown gate ───
  if [ "${last_ts:-0}" -gt 0 ] 2>/dev/null; then
    diff=$(( now - last_ts ))
    if [ "$diff" -lt "$COOLDOWN_SEC" ]; then
      # SRW-C1 / HND-SRW-C1: stash current as pending + record pending_since.
      # last_notified_* untouched → fixes cycle1 永久 skip bug.
      local new_pending_since="${pending_since:-$now}"
      [ -z "$pending" ] && new_pending_since="$now"  # first stash this cooldown window
      echo "$LOG_PREFIX cooldown skip: $report_name (${diff}s < ${COOLDOWN_SEC}s) — pending=$current since=$new_pending_since" >&2
      state_write_entry "$report_name" "$last_ck" "$last_ts" "$current" "$new_pending_since"
      flock -u 8
      return 0
    fi
  fi

  # ─── cooldown elapsed (or first event): deliver ───
  # The on-disk file already contains pending+all further updates → notifying
  # $current is the correct "latest state" delivery. pending was kept only as
  # a witness that an undelivered change exists; we now consume it.
  audit_id=$(get_latest_audit_id "$path")
  if [ -n "$pending" ] && [ "$pending" != "$current" ]; then
    echo "$LOG_PREFIX deliver post-cooldown (pending=$pending → current=$current): $report_name audit_id=$audit_id" >&2
  elif [ -n "$pending" ]; then
    echo "$LOG_PREFIX deliver post-cooldown (pending matches current): $report_name checksum=$current audit_id=$audit_id" >&2
  else
    echo "$LOG_PREFIX notify: $report_name checksum=$current audit_id=$audit_id" >&2
  fi
  notify_shogun "$report_name" "$audit_id"
  state_write_entry "$report_name" "$current" "$now" "" ""
  flock -u 8
}

# ─── graceful shutdown ──────────────────────────────────────────
# Releases the singleton flock automatically via FD 9 close on exit.
WATCH_PID=""
shutdown() {
  echo "$LOG_PREFIX shutdown signal received, terminating watcher..." >&2
  if [ -n "$WATCH_PID" ] && kill -0 "$WATCH_PID" 2>/dev/null; then
    kill "$WATCH_PID" 2>/dev/null || true
    wait "$WATCH_PID" 2>/dev/null || true
  fi
  # FD 9 close (= flock release) is implicit at exit
  exit 0
}
trap shutdown SIGINT SIGTERM

# ─── main loop ──────────────────────────────────────────────────
echo "$LOG_PREFIX started — dir=$REPORTS_DIR cooldown=${COOLDOWN_SEC}s state=$STATE_FILE" >&2

# Watch parent dir so we catch creates/atomic-writes (rename) for files that
# may not exist yet. inotifywait -m is event-driven, no sleep polling (F004).
# Use process substitution + FD3 so we can capture inotifywait's PID for graceful shutdown.
#
# HND-SRW-C5 TODO (cycle3+): the process-substitution + WATCH_PID dance is
# environment-sensitive (BASHPID timing, async-list FD bookkeeping). Consider
# replacing with a coproc or named-pipe pattern for more deterministic shutdown
# semantics. Tracked as a separate cmd, intentionally deferred per task spec.
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
