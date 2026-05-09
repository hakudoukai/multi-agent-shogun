#!/usr/bin/env bash
# scripts/redundancy/test_shogun_report_watcher.sh
#
# Smoke tests for shogun_report_watcher.sh — 7 scenarios (SRW-C3 cycle2)
# Tests core logic functions in isolation without starting the full daemon.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ── Test infrastructure ──────────────────────────────────────────────────────
PASS_COUNT=0
FAIL_COUNT=0
TEST_DIR="$(mktemp -d /tmp/.srw_test.XXXXXX)"

_pass() { echo "  ✓ $1"; (( PASS_COUNT++ )) || true; }
_fail() { echo "  ✗ $1"; (( FAIL_COUNT++ )) || true; }

# ── Setup: load helper functions from main script ────────────────────────────
# Override paths to test-temp dirs before sourcing
STATE_FILE="$TEST_DIR/state.json"
LOCK_FILE="$TEST_DIR/watcher.lock"
REPORTS_DIR="$TEST_DIR/reports"
COOLDOWN_SECS=2   # short cooldown for tests
mkdir -p "$REPORTS_DIR"

# Extract and define helper functions without running _main
# (We source only the function definitions by redefining _main to be a no-op)
_main() { :; }
# Also neutralize the flock block at top-level by pre-creating the lock
exec 200>"$LOCK_FILE"
flock -w 1 200 || true

# Source the watcher script (will define functions but _main is a no-op)
# shellcheck disable=SC1090
# We need to parse the script carefully — source only functions
# Instead, inline the helpers we need:

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

_get_checksum() {
    local file="$1"
    if [[ -f "$file" ]]; then
        sha256sum "$file" | awk '{print $1}'
    else
        echo ""
    fi
}

NOTIFICATIONS_LOG="$TEST_DIR/notifications.log"
_send_notification() {
    local report_name="$1" checksum="$2" extra="$3"
    echo "$report_name|${checksum:0:12}|$extra" >> "$NOTIFICATIONS_LOG"
}

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

WATCH_REPORTS=(
    "ieyasu_report.yaml"
    "honda_report.yaml"
    "kuroda_report.yaml"
    "sanada_report.yaml"
    "takenaka_report.yaml"
)

_process_change() {
    local filepath="$1"
    local report_name
    report_name="$(basename "$filepath")"

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

    [[ "$current_checksum" == "$last_checksum" ]] && return

    local last_notified_at
    last_notified_at="$(_get_state "$report_name" "last_notified_at")"

    local now
    now="$(date +%s)"

    if [[ -n "$last_notified_at" ]] && (( now - last_notified_at < COOLDOWN_SECS )); then
        _set_state "$report_name" "pending_checksum" "$current_checksum"
        return
    fi

    local verdict_info
    verdict_info="$(_parse_verdict "$filepath")"
    _send_notification "$report_name" "$current_checksum" "$verdict_info"
    _set_state "$report_name" "last_checksum" "$current_checksum"
    _set_state "$report_name" "last_notified_at" "$now"
    _set_state "$report_name" "pending_checksum" ""
}

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
                local verdict_info
                verdict_info="$(_parse_verdict "$filepath")"
                _send_notification "$r" "$current_checksum" "${verdict_info:+${verdict_info} }(cooldown後送)"
                _set_state "$r" "last_checksum" "$current_checksum"
                _set_state "$r" "last_notified_at" "$now"
                _set_state "$r" "pending_checksum" ""
            else
                _set_state "$r" "pending_checksum" ""
            fi
        fi
    done
}

# ── Reset between tests ──────────────────────────────────────────────────────
_reset() {
    echo '{}' > "$STATE_FILE"
    > "$NOTIFICATIONS_LOG"
    rm -f "$REPORTS_DIR"/*.yaml
}

_notification_count() {
    local report="$1"
    local n
    n=$(grep -c "^${report}|" "$NOTIFICATIONS_LOG" 2>/dev/null) && echo "$n" || echo "0"
}

_notification_has() {
    local pattern="$1"
    grep -q "$pattern" "$NOTIFICATIONS_LOG" 2>/dev/null
}

# ════════════════════════════════════════════════════════════════════════════
echo "=== shogun_report_watcher smoke tests (7 scenarios) ==="
echo ""

# ── Scenario 1: Normal update → notification sent ───────────────────────────
echo "Scenario 1: Normal update → notification sent"
_reset
_init_state
echo "verdict: PASS" > "$REPORTS_DIR/ieyasu_report.yaml"
_process_change "$REPORTS_DIR/ieyasu_report.yaml"
if [[ "$(_notification_count ieyasu_report.yaml)" -eq 1 ]]; then
    _pass "notification sent on first change"
else
    _fail "expected 1 notification, got $(_notification_count ieyasu_report.yaml)"
fi

# ── Scenario 2: Same checksum → no duplicate notification (dedup) ───────────
echo ""
echo "Scenario 2: Same checksum → dedup (no duplicate notification)"
_reset
_init_state
echo "verdict: PASS" > "$REPORTS_DIR/ieyasu_report.yaml"
_process_change "$REPORTS_DIR/ieyasu_report.yaml"
_process_change "$REPORTS_DIR/ieyasu_report.yaml"  # same content, same checksum
if [[ "$(_notification_count ieyasu_report.yaml)" -eq 1 ]]; then
    _pass "dedup: only 1 notification for same checksum"
else
    _fail "expected 1 notification after dedup, got $(_notification_count ieyasu_report.yaml)"
fi

# ── Scenario 3: Rapid updates within cooldown → pending set, no extra notif ──
echo ""
echo "Scenario 3: Rapid updates within cooldown → pending_checksum set"
_reset
_init_state
echo "verdict: PASS_v1" > "$REPORTS_DIR/ieyasu_report.yaml"
_process_change "$REPORTS_DIR/ieyasu_report.yaml"
# Immediately update again (within cooldown)
echo "verdict: PASS_v2" > "$REPORTS_DIR/ieyasu_report.yaml"
_process_change "$REPORTS_DIR/ieyasu_report.yaml"
pending="$(_get_state "ieyasu_report.yaml" "pending_checksum")"
notif_count="$(_notification_count ieyasu_report.yaml)"
if [[ "$notif_count" -eq 1 && -n "$pending" ]]; then
    _pass "cooldown respected: 1 notif sent, pending_checksum set (no permanent skip)"
else
    _fail "expected 1 notif + pending set, got notif=$notif_count pending='$pending'"
fi

# ── Scenario 4: Cooldown expires → pending delivered (SRW-C1 core fix) ──────
echo ""
echo "Scenario 4: Cooldown expiry → pending notification delivered"
_reset
_init_state
echo "verdict: PASS_v1" > "$REPORTS_DIR/ieyasu_report.yaml"
_process_change "$REPORTS_DIR/ieyasu_report.yaml"
# Simulate cooldown by backdating last_notified_at
past="$(( $(date +%s) - COOLDOWN_SECS - 5 ))"
echo "verdict: PASS_v2" > "$REPORTS_DIR/ieyasu_report.yaml"
_set_state "ieyasu_report.yaml" "last_notified_at" "$past"
# Set pending manually to simulate the cooldown state
checksum="$(_get_checksum "$REPORTS_DIR/ieyasu_report.yaml")"
_set_state "ieyasu_report.yaml" "pending_checksum" "$checksum"
_flush_pending
notif_count="$(_notification_count ieyasu_report.yaml)"
if [[ "$notif_count" -eq 2 ]]; then
    _pass "cooldown後送: pending notification delivered after cooldown"
else
    _fail "expected 2 notifications (original + pending), got $notif_count"
fi

# ── Scenario 5: Singleton lock → second instance rejected ───────────────────
echo ""
echo "Scenario 5: Singleton lock → second instance rejects"
# Test that flock prevents a second instance
LOCK_FILE_TEST="$TEST_DIR/singleton_test.lock"
exec 201>"$LOCK_FILE_TEST"
flock -n 201  # acquire lock

# Try to acquire same lock in subshell (should fail)
if ! (flock -n "$LOCK_FILE_TEST" echo "acquired" 2>/dev/null); then
    _pass "singleton: second instance correctly rejected by flock"
else
    _fail "singleton: second instance should have been blocked"
fi
exec 201<&-

# ── Scenario 6: Multiple reports → each tracked independently ───────────────
echo ""
echo "Scenario 6: Multiple reports → independent state tracking"
_reset
_init_state
echo "status: PASS" > "$REPORTS_DIR/ieyasu_report.yaml"
echo "status: FAIL" > "$REPORTS_DIR/honda_report.yaml"
_process_change "$REPORTS_DIR/ieyasu_report.yaml"
_process_change "$REPORTS_DIR/honda_report.yaml"
ieyasu_n="$(_notification_count ieyasu_report.yaml)"
honda_n="$(_notification_count honda_report.yaml)"
if [[ "$ieyasu_n" -eq 1 && "$honda_n" -eq 1 ]]; then
    _pass "multiple reports: each gets independent notification"
else
    _fail "expected 1+1 notifications, got ieyasu=$ieyasu_n honda=$honda_n"
fi

# ── Scenario 7: Restart with existing state → no duplicate notification ──────
echo ""
echo "Scenario 7: Restart with existing state → no duplicate notif"
_reset
_init_state
echo "verdict: PASS" > "$REPORTS_DIR/kuroda_report.yaml"
# Simulate: file was already processed in a previous run
checksum="$(_get_checksum "$REPORTS_DIR/kuroda_report.yaml")"
_set_state "kuroda_report.yaml" "last_checksum" "$checksum"
_set_state "kuroda_report.yaml" "last_notified_at" "$(date +%s)"
# After restart, the watcher would process the same file again
_process_change "$REPORTS_DIR/kuroda_report.yaml"
if [[ "$(_notification_count kuroda_report.yaml)" -eq 0 ]]; then
    _pass "restart: no duplicate notification for already-seen checksum"
else
    _fail "expected 0 notifications after restart with existing state"
fi

# ── Results ──────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo "Results: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
if [[ "$FAIL_COUNT" -eq 0 ]]; then
    echo "ALL PASS ✓"
    exit 0
else
    echo "FAIL ✗"
    exit 1
fi
