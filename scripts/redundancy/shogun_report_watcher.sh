#!/usr/bin/env bash
# scripts/redundancy/shogun_report_watcher.sh
#
# Monitors auditor report YAMLs and notifies shogun when updated.
# Features: inotify-only (no sleep polling), dedup, cooldown with pending_checksum
# for guaranteed post-cooldown delivery, singleton via flock.
#
# Cycle2: SRW-C1 pending_checksum, SRW-C2 flock, HND-SRW-C3 dedup precision,
#         HND-SRW-C4 YAML verdict parse, HND-SRW-C5 TODO for cycle3.
# Cycle3: D002/D006 safety compliance (trap rm-rf → removed, kill → exec 3<&- FIFO close)
# Cycle4 (TODO HND-SRW-C5): Migrate inotifywait background process to coproc
# for cleaner resource lifecycle management and better portability.
# Cycle4 also: WATCH_REPORTS updated to 編成 v1.1 (kuroda/takenaka/naomasa/acha/ieyasu/honda)

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

# ── Target reports (編成 v1.1: MainPC 黒田/竹中 + SecondPC 直政/あちゃ/家康/本多) ────
WATCH_REPORTS=(
    "kuroda_report.yaml"
    "takenaka_report.yaml"
    "naomasa_report.yaml"
    "acha_report.yaml"
    "ieyasu_report.yaml"
    "honda_report.yaml"
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

# ── Coproc state (HND-SRW-C5 cycle4) ────────────────────────────────────────
# coproc fd refs stored in global so _cleanup can close them
INOTIFY_READ_FD=""

_cleanup() {
    # Close coproc read fd — sends EOF to inotifywait, letting it exit naturally
    [[ -n "$INOTIFY_READ_FD" ]] && eval "exec ${INOTIFY_READ_FD}<&-" 2>/dev/null || true
}
trap _cleanup EXIT INT TERM

# ── Main (cycle4: coproc replaces FIFO + background &) ───────────────────────
_main() {
    _init_state

    # Build watch path array
    local watch_paths=()
    local r
    for r in "${WATCH_REPORTS[@]}"; do
        watch_paths+=("$REPORTS_DIR/$r")
    done

    echo "shogun_report_watcher: starting (cycle4/coproc), watching ${#WATCH_REPORTS[@]} reports" >&2

    # Launch inotifywait as coproc (HND-SRW-C5)
    # INOTIFY_PROC[0] = read fd (inotifywait stdout), INOTIFY_PROC[1] = write fd (inotifywait stdin)
    # shellcheck disable=SC2034
    coproc INOTIFY_PROC {
        inotifywait -m -q -e close_write,moved_to --format '%w%f' \
            "${watch_paths[@]}" 2>/dev/null
    }
    INOTIFY_READ_FD="${INOTIFY_PROC[0]}"

    # Event loop: read with timeout to periodically flush pending notifications
    local filepath rc
    while true; do
        filepath=""
        if IFS= read -r -t "$COOLDOWN_SECS" filepath <&"${INOTIFY_PROC[0]}"; then
            _process_change "$filepath"
        else
            rc=$?
            if (( rc <= 128 )); then
                # EOF: inotifywait coproc exited unexpectedly
                echo "shogun_report_watcher: inotifywait coproc exited, stopping" >&2
                break
            fi
            # rc > 128 → read timeout: fall through to _flush_pending
        fi
        _flush_pending
    done
}

_main
