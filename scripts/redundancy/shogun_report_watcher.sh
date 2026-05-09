#!/usr/bin/env bash
# scripts/redundancy/shogun_report_watcher.sh
#
# Monitors auditor report YAMLs and notifies shogun when updated.
# Features: inotify-only (no sleep polling), dedup, cooldown with pending_checksum
# for guaranteed post-cooldown delivery, singleton via flock.
#
# Cycle2: SRW-C1 pending_checksum, SRW-C2 flock, HND-SRW-C3 dedup precision,
#         HND-SRW-C4 YAML verdict parse, HND-SRW-C5 TODO for cycle3.
#
# TODO(HND-SRW-C5 cycle3): Migrate inotifywait background process to coproc
# for cleaner resource lifecycle management and better portability.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPORTS_DIR="$PROJECT_ROOT/queue/reports"
STATE_FILE="/tmp/.shogun_report_watcher_state.json"
LOCK_FILE="/tmp/.shogun_report_watcher.lock"
COOLDOWN_SECS=60

# ── Singleton lock (SRW-C2 / HND-SRW-C2) ───────────────────────────────────
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    echo "shogun_report_watcher: another instance is already running, exiting" >&2
    exit 1
fi

# ── Target reports ──────────────────────────────────────────────────────────
WATCH_REPORTS=(
    "ieyasu_report.yaml"
    "honda_report.yaml"
    "kuroda_report.yaml"
    "sanada_report.yaml"
    "takenaka_report.yaml"
)

# ── State helpers ───────────────────────────────────────────────────────────
_init_state() {
    [[ -f "$STATE_FILE" ]] || echo '{}' > "$STATE_FILE"
}

_get_state() {
    local key="$1" field="$2"
    python3 - <<PYEOF 2>/dev/null
import json
try:
    data = json.load(open("$STATE_FILE"))
    print(data.get("$key", {}).get("$field", ""), end="")
except Exception:
    print("", end="")
PYEOF
}

_set_state() {
    local key="$1" field="$2" value="$3"
    python3 - <<PYEOF 2>/dev/null
import json
try:
    data = json.load(open("$STATE_FILE"))
except Exception:
    data = {}
data.setdefault("$key", {})["$field"] = "$value"
json.dump(data, open("$STATE_FILE", "w"), ensure_ascii=False)
PYEOF
}

# Parse verdict/status from report YAML for richer notification (HND-SRW-C4)
_parse_verdict() {
    local file="$1"
    python3 - <<PYEOF 2>/dev/null
import yaml, sys
try:
    with open("$file") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        sys.exit(0)
    verdict = data.get("verdict", data.get("status", ""))
    task_id = data.get("task_id", "")
    parts = []
    if verdict:
        parts.append(f"verdict={verdict}")
    if task_id:
        parts.append(f"task={task_id}")
    print(" ".join(parts), end="")
except Exception:
    print("", end="")
PYEOF
}

_get_checksum() {
    local file="$1"
    if [[ -f "$file" ]]; then
        sha256sum "$file" | awk '{print $1}'
    else
        echo ""
    fi
}

# ── Notification sender ─────────────────────────────────────────────────────
_send_notification() {
    local report_name="$1" checksum="$2" extra="$3"
    local short_hash="${checksum:0:12}"
    local msg="[report_watcher] ${report_name} 更新検知。${extra:+${extra} }checksum=${short_hash}"
    bash "$PROJECT_ROOT/scripts/inbox_write.sh" shogun "$msg" notification shogun_report_watcher
}

# ── Process a file-change event ─────────────────────────────────────────────
_process_change() {
    local filepath="$1"
    local report_name
    report_name="$(basename "$filepath")"

    # Only handle target reports
    local is_target=0
    local r
    for r in "${WATCH_REPORTS[@]}"; do
        [[ "$report_name" == "$r" ]] && { is_target=1; break; }
    done
    [[ "$is_target" -eq 0 ]] && return

    local current_checksum
    current_checksum="$(_get_checksum "$filepath")"
    [[ -z "$current_checksum" ]] && return

    local last_checksum
    last_checksum="$(_get_state "$report_name" "last_checksum")"

    # Dedup: content unchanged (HND-SRW-C3)
    [[ "$current_checksum" == "$last_checksum" ]] && return

    local last_notified_at
    last_notified_at="$(_get_state "$report_name" "last_notified_at")"

    local now
    now="$(date +%s)"

    # Cooldown guard
    if [[ -n "$last_notified_at" ]] && (( now - last_notified_at < COOLDOWN_SECS )); then
        # Within cooldown: park as pending WITHOUT touching last_checksum (SRW-C1 / HND-SRW-C1)
        _set_state "$report_name" "pending_checksum" "$current_checksum"
        return
    fi

    # Send notification
    local verdict_info
    verdict_info="$(_parse_verdict "$filepath")"
    _send_notification "$report_name" "$current_checksum" "$verdict_info"
    _set_state "$report_name" "last_checksum" "$current_checksum"
    _set_state "$report_name" "last_notified_at" "$now"
    _set_state "$report_name" "pending_checksum" ""
}

# ── Flush pending notifications whose cooldown has expired ──────────────────
_flush_pending() {
    local now
    now="$(date +%s)"

    local r
    for r in "${WATCH_REPORTS[@]}"; do
        local pending
        pending="$(_get_state "$r" "pending_checksum")"
        [[ -z "$pending" ]] && continue

        local last_notified_at
        last_notified_at="$(_get_state "$r" "last_notified_at")"
        [[ -z "$last_notified_at" ]] && continue

        if (( now - last_notified_at >= COOLDOWN_SECS )); then
            local filepath="$REPORTS_DIR/$r"
            local current_checksum
            current_checksum="$(_get_checksum "$filepath")"

            if [[ "$current_checksum" == "$pending" ]]; then
                # Cooldown expired: deliver the deferred notification
                local verdict_info
                verdict_info="$(_parse_verdict "$filepath")"
                _send_notification "$r" "$current_checksum" "${verdict_info:+${verdict_info} }(cooldown後送)"
                _set_state "$r" "last_checksum" "$current_checksum"
                _set_state "$r" "last_notified_at" "$now"
                _set_state "$r" "pending_checksum" ""
            else
                # File changed again since pending was saved; discard stale pending
                _set_state "$r" "pending_checksum" ""
            fi
        fi
    done
}

# ── Cleanup ─────────────────────────────────────────────────────────────────
EVENT_FIFO=""

_cleanup() {
    exec 3<&- 2>/dev/null || true
    [[ -n "$EVENT_FIFO" && -p "$EVENT_FIFO" ]] && rm -f "$EVENT_FIFO"
}
trap _cleanup EXIT INT TERM

# ── Main ─────────────────────────────────────────────────────────────────────
_main() {
    _init_state

    # Build watch path array
    local watch_paths=()
    local r
    for r in "${WATCH_REPORTS[@]}"; do
        watch_paths+=("$REPORTS_DIR/$r")
    done

    EVENT_FIFO="$(mktemp -u /tmp/.shogun_watcher_fifo.XXXXXX)"
    mkfifo "$EVENT_FIFO"

    echo "shogun_report_watcher: starting, watching ${#WATCH_REPORTS[@]} reports" >&2

    # Launch inotifywait writer into FIFO
    inotifywait -m -q -e close_write,moved_to --format '%w%f' \
        "${watch_paths[@]}" > "$EVENT_FIFO" 2>/dev/null &

    # Open read-end on fd 3 (this unblocks the background inotifywait writer)
    exec 3< "$EVENT_FIFO"

    # Event loop: read with timeout to periodically flush pending notifications
    local filepath rc
    while true; do
        filepath=""
        if IFS= read -r -t "$COOLDOWN_SECS" filepath <&3; then
            _process_change "$filepath"
        else
            rc=$?
            if (( rc <= 128 )); then
                # EOF: inotifywait died unexpectedly
                echo "shogun_report_watcher: inotifywait exited, stopping" >&2
                break
            fi
            # rc > 128 → read timeout: fall through to _flush_pending
        fi
        _flush_pending
    done

    exec 3<&-
}

_main
