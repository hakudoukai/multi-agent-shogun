#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# tests/test_shogun_report_watcher.sh — SRW-C3 smoke test runner
#
# Covers cycle2 acceptance criteria:
#   T1 modify event detection
#   T2 close_write event detection
#   T3 moved_to event (atomic write/rename) detection
#   T4 same-checksum dedup (= notify skipped)
#   T5 cooldown 中の連続 2 更新 → 1 通通知 + pending 後送 (SRW-C1)
#   T6 multi-instance singleton (= 2nd start exits 0) (SRW-C2)
#   T7 inbox_write.sh failure: log + watcher continues
#
# Pure bash (no bats dependency). Each scenario isolated via tempdir.
# Usage: bash tests/test_shogun_report_watcher.sh
# Exit 0 = all PASS, non-zero = at least one FAIL.
# ═══════════════════════════════════════════════════════════════

set -u  # not -e: tests must continue past failures

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WATCHER="$REPO_ROOT/scripts/redundancy/shogun_report_watcher.sh"

PASS_COUNT=0
FAIL_COUNT=0
FAILURES=()

log() { printf '  %s\n' "$*" >&2; }

# Per-test tempdir + mock inbox_write
setup_env() {
  local tmpdir; tmpdir=$(mktemp -d)
  mkdir -p "$tmpdir/queue/reports" "$tmpdir/scripts"
  cat > "$tmpdir/scripts/inbox_write.sh" <<'EOF'
#!/usr/bin/env bash
# Mock inbox_write — records call args to $MOCK_LOG.
echo "INBOX|target=$1|content=$2|type=$3|from=$4" >> "$MOCK_LOG"
exit 0
EOF
  chmod +x "$tmpdir/scripts/inbox_write.sh"
  echo "$tmpdir"
}

# Start watcher with isolated env. Echoes WATCHER_PID via stdout.
start_watcher() {
  local tmpdir="$1"
  local state_file="$2"
  local lock_file="$3"
  local cooldown="$4"
  local mock_log="$5"
  # Symlink real watcher into tmpdir's scripts/redundancy/ so SCRIPT_DIR resolves correctly
  mkdir -p "$tmpdir/scripts/redundancy"
  cp "$WATCHER" "$tmpdir/scripts/redundancy/shogun_report_watcher.sh"
  chmod +x "$tmpdir/scripts/redundancy/shogun_report_watcher.sh"
  (
    cd "$tmpdir"
    SHOGUN_REPORT_WATCHER_DIR="$tmpdir/queue/reports" \
    SHOGUN_REPORT_WATCHER_STATE="$state_file" \
    SHOGUN_REPORT_WATCHER_LOCK="$lock_file" \
    SHOGUN_REPORT_WATCHER_COOLDOWN="$cooldown" \
    MOCK_LOG="$mock_log" \
    exec "$tmpdir/scripts/redundancy/shogun_report_watcher.sh"
  ) >/dev/null 2>&1 &
  echo $!
}

# wait for first inotify ready (best-effort short wait)
warmup_watcher() {
  sleep 0.8
}

stop_watcher() {
  local pid="$1"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    kill -TERM "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  fi
}

count_inbox_lines() {
  local mock_log="$1"
  if [ -f "$mock_log" ]; then
    grep -c "^INBOX|" "$mock_log" 2>/dev/null || echo 0
  else
    echo 0
  fi
}

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    PASS_COUNT=$((PASS_COUNT+1))
    log "    ✅ $label: $actual"
    return 0
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILURES+=("$label: expected=$expected actual=$actual")
    log "    ❌ $label: expected=$expected actual=$actual"
    return 1
  fi
}

# ─── tests ──────────────────────────────────────────────────────

run_test() {
  local name="$1"; shift
  echo "──── $name ────" >&2
  "$@"
}

T1_modify_event() {
  local tmp state lock log pid
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  : > "$log"
  pid=$(start_watcher "$tmp" "$state" "$lock" 60 "$log")
  warmup_watcher
  echo "audit_id: aud_t1" > "$tmp/queue/reports/honda_report.yaml"
  sleep 0.6
  echo "audit_id: aud_t1_modify" > "$tmp/queue/reports/honda_report.yaml"
  sleep 0.6
  stop_watcher "$pid"
  local n; n=$(count_inbox_lines "$log")
  # Expect 2 notifies: initial create + content change (different checksums, no cooldown gating since both within ~0s but cooldown=60s).
  # Actually first triggers immediate notify (no last_ts), second falls under cooldown → pending. Expect 1.
  assert_eq "T1 modify event detected" 1 "$n"
  rm -rf "$tmp"
}

T2_close_write_event() {
  local tmp state lock log pid
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  : > "$log"
  pid=$(start_watcher "$tmp" "$state" "$lock" 60 "$log")
  warmup_watcher
  # Single create → close_write event triggers notify
  printf 'audit_id: aud_t2\n' > "$tmp/queue/reports/ieyasu_report.yaml"
  sleep 0.6
  stop_watcher "$pid"
  local n; n=$(count_inbox_lines "$log")
  assert_eq "T2 close_write event detected" 1 "$n"
  rm -rf "$tmp"
}

T3_moved_to_event() {
  local tmp state lock log pid
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  : > "$log"
  pid=$(start_watcher "$tmp" "$state" "$lock" 60 "$log")
  warmup_watcher
  # Atomic write: write to tmp file outside watch dir, mv into watch dir
  echo "audit_id: aud_t3" > "$tmp/staging.yaml"
  mv "$tmp/staging.yaml" "$tmp/queue/reports/kuroda_report.yaml"
  sleep 0.6
  stop_watcher "$pid"
  local n; n=$(count_inbox_lines "$log")
  # moved_to fires; may also fire close_write depending on filesystem.
  # Either way, dedup ensures notify count ≥ 1.
  if [ "$n" -ge 1 ]; then
    PASS_COUNT=$((PASS_COUNT+1))
    log "    ✅ T3 moved_to event detected: notifies=$n (≥1)"
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILURES+=("T3: expected≥1 actual=$n")
    log "    ❌ T3 moved_to event detected: actual=$n"
  fi
  rm -rf "$tmp"
}

T4_same_checksum_dedup() {
  local tmp state lock log pid
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  : > "$log"
  pid=$(start_watcher "$tmp" "$state" "$lock" 60 "$log")
  warmup_watcher
  # Write same content 3 times → only first should notify
  for _ in 1 2 3; do
    echo "audit_id: aud_t4_same" > "$tmp/queue/reports/sanada_report.yaml"
    sleep 0.4
  done
  stop_watcher "$pid"
  local n; n=$(count_inbox_lines "$log")
  assert_eq "T4 same-checksum dedup → 1 notify" 1 "$n"
  rm -rf "$tmp"
}

T5_pending_post_delivery() {
  # Critical SRW-C1 test:
  # 1. write A → notify (cooldown_start)
  # 2. write B during cooldown → pending=B, last_notified=A unchanged
  # 3. wait cooldown
  # 4. write C → cooldown elapsed, current=C ≠ last_notified A → notify
  # Expected: 2 total notifies (A initial + C post-cooldown).
  # Bug regression check: cycle1 would NOT notify on step 4 because B
  # had been saved as last_notified during step 2.
  local tmp state lock log pid
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  : > "$log"
  pid=$(start_watcher "$tmp" "$state" "$lock" 2 "$log")  # cooldown=2s for fast test
  warmup_watcher
  echo "audit_id: aud_A" > "$tmp/queue/reports/takenaka_report.yaml"
  sleep 0.5
  echo "audit_id: aud_B" > "$tmp/queue/reports/takenaka_report.yaml"
  sleep 0.5
  # Verify pending was saved (state inspection)
  local pending_seen
  pending_seen=$(python3 -c "
import json
try:
    d = json.load(open('$state'))
    e = d.get('takenaka_report.yaml', {})
    print(e.get('pending_checksum') or 'NONE')
except: print('NONE')
")
  if [ "$pending_seen" != "NONE" ] && [ -n "$pending_seen" ]; then
    PASS_COUNT=$((PASS_COUNT+1))
    log "    ✅ T5a pending_checksum stashed during cooldown: $pending_seen"
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILURES+=("T5a pending not stashed during cooldown")
    log "    ❌ T5a pending_checksum stashed: NONE"
  fi
  # wait for cooldown to expire (2s + buffer)
  sleep 2.5
  echo "audit_id: aud_C" > "$tmp/queue/reports/takenaka_report.yaml"
  sleep 0.6
  stop_watcher "$pid"
  local n; n=$(count_inbox_lines "$log")
  assert_eq "T5b post-cooldown delivery (SRW-C1)" 2 "$n"
  rm -rf "$tmp"
}

T6_singleton_lock() {
  local tmp state lock log pid1 pid2 rc2
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  : > "$log"
  pid1=$(start_watcher "$tmp" "$state" "$lock" 60 "$log")
  warmup_watcher
  # Try second start — must exit 0 quickly without acquiring lock.
  mkdir -p "$tmp/scripts/redundancy"
  if [ ! -f "$tmp/scripts/redundancy/shogun_report_watcher.sh" ]; then
    cp "$WATCHER" "$tmp/scripts/redundancy/shogun_report_watcher.sh"
    chmod +x "$tmp/scripts/redundancy/shogun_report_watcher.sh"
  fi
  ( cd "$tmp" &&
    SHOGUN_REPORT_WATCHER_DIR="$tmp/queue/reports" \
    SHOGUN_REPORT_WATCHER_STATE="$state" \
    SHOGUN_REPORT_WATCHER_LOCK="$lock" \
    SHOGUN_REPORT_WATCHER_COOLDOWN=60 \
    MOCK_LOG="$log" \
    bash "$tmp/scripts/redundancy/shogun_report_watcher.sh" >/dev/null 2>&1 ) &
  pid2=$!
  wait "$pid2"
  rc2=$?
  stop_watcher "$pid1"
  assert_eq "T6 second instance exits 0 (singleton)" 0 "$rc2"
  rm -rf "$tmp"
}

T8_dual_notification_idempotency() {
  # HND-SRW-C3: simulate "audit author already notified shogun via own
  # inbox_write + watcher fallback fires" — under same content, watcher
  # must produce exactly one notification per checksum change, not storm.
  # Also verify the notification content carries the audit_id (for downstream
  # idempotency by report+audit_id+checksum tuple).
  local tmp state lock log pid
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  : > "$log"
  pid=$(start_watcher "$tmp" "$state" "$lock" 60 "$log")
  warmup_watcher
  echo "audit_id: aud_idem_001" > "$tmp/queue/reports/honda_report.yaml"
  sleep 0.6
  # repeated identical writes → no further notifications
  for _ in 1 2 3 4 5; do
    echo "audit_id: aud_idem_001" > "$tmp/queue/reports/honda_report.yaml"
    sleep 0.2
  done
  stop_watcher "$pid"
  local n; n=$(count_inbox_lines "$log")
  assert_eq "T8a same-content storm → 1 notify" 1 "$n"
  # audit_id should be in the notification content
  if grep -q "aud_idem_001" "$log" 2>/dev/null; then
    PASS_COUNT=$((PASS_COUNT+1))
    log "    ✅ T8b notification content includes audit_id"
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILURES+=("T8b notification content missing audit_id")
    log "    ❌ T8b notification content missing audit_id"
  fi
  rm -rf "$tmp"
}

T9_yaml_parser_nested_id() {
  # HND-SRW-C4: yaml.safe_load picks top-level audit_id, not a nested
  # finding's "id:". Fixture has finding list with id values that would
  # confuse a naive grep.
  local tmp state lock log pid
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  : > "$log"
  pid=$(start_watcher "$tmp" "$state" "$lock" 60 "$log")
  warmup_watcher
  cat > "$tmp/queue/reports/sanada_report.yaml" <<'EOF'
audit_id: AUD_TOPLEVEL_KEEP
findings:
  - id: finding_first
    severity: low
  - id: finding_LAST_NESTED
    severity: high
EOF
  sleep 0.6
  stop_watcher "$pid"
  # The notification content must include AUD_TOPLEVEL_KEEP, NOT finding_LAST_NESTED.
  if grep -q "AUD_TOPLEVEL_KEEP" "$log" 2>/dev/null; then
    PASS_COUNT=$((PASS_COUNT+1))
    log "    ✅ T9a yaml parser picks top-level audit_id"
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILURES+=("T9a top-level audit_id not picked")
    log "    ❌ T9a top-level audit_id not picked"
  fi
  if grep -q "finding_LAST_NESTED" "$log" 2>/dev/null; then
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILURES+=("T9b nested finding id leaked into notify")
    log "    ❌ T9b nested finding id leaked"
  else
    PASS_COUNT=$((PASS_COUNT+1))
    log "    ✅ T9b nested finding id correctly NOT picked"
  fi
  rm -rf "$tmp"
}

T10_pending_since_timestamp() {
  # HND-SRW-C1: pending_since must be set (non-null) when a checksum
  # is stashed during cooldown. This is the "evidence trail" honda required.
  local tmp state lock log pid
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  : > "$log"
  pid=$(start_watcher "$tmp" "$state" "$lock" 5 "$log")  # 5s cooldown
  warmup_watcher
  echo "audit_id: aud_first" > "$tmp/queue/reports/takenaka_report.yaml"
  sleep 0.5
  # Trigger pending stash
  echo "audit_id: aud_second" > "$tmp/queue/reports/takenaka_report.yaml"
  sleep 0.5
  local pending_since
  pending_since=$(python3 -c "
import json
try:
    d = json.load(open('$state'))
    e = d.get('takenaka_report.yaml', {})
    print(e.get('pending_since') or 'NONE')
except: print('NONE')
")
  stop_watcher "$pid"
  if [ "$pending_since" != "NONE" ] && [ -n "$pending_since" ] && [ "$pending_since" -gt 0 ] 2>/dev/null; then
    PASS_COUNT=$((PASS_COUNT+1))
    log "    ✅ T10 pending_since recorded: $pending_since"
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILURES+=("T10 pending_since not recorded: $pending_since")
    log "    ❌ T10 pending_since not recorded: $pending_since"
  fi
  rm -rf "$tmp"
}

T7_inbox_write_failure() {
  local tmp state lock log pid
  tmp=$(setup_env)
  state="$tmp/state.json"
  lock="$tmp/lock"
  log="$tmp/inbox.log"
  # Replace mock with a failing version
  cat > "$tmp/scripts/inbox_write.sh" <<'EOF'
#!/usr/bin/env bash
echo "INBOX_FAIL|args=$*" >> "$MOCK_LOG"
exit 1
EOF
  chmod +x "$tmp/scripts/inbox_write.sh"
  : > "$log"
  pid=$(start_watcher "$tmp" "$state" "$lock" 60 "$log")
  warmup_watcher
  # Trigger event — watcher should call inbox_write (fails) but continue running
  echo "audit_id: aud_t7_a" > "$tmp/queue/reports/honda_report.yaml"
  sleep 0.6
  local alive_after_fail=0
  if kill -0 "$pid" 2>/dev/null; then alive_after_fail=1; fi
  # Trigger another (different content) — should attempt again, also fail, still alive
  echo "audit_id: aud_t7_b" > "$tmp/queue/reports/ieyasu_report.yaml"
  sleep 0.6
  local alive_after_2nd=0
  if kill -0 "$pid" 2>/dev/null; then alive_after_2nd=1; fi
  stop_watcher "$pid"
  local fail_calls; fail_calls=$(grep -c "^INBOX_FAIL|" "$log" 2>/dev/null || echo 0)
  assert_eq "T7a alive after 1st failure" 1 "$alive_after_fail"
  assert_eq "T7b alive after 2nd failure" 1 "$alive_after_2nd"
  if [ "$fail_calls" -ge 2 ]; then
    PASS_COUNT=$((PASS_COUNT+1))
    log "    ✅ T7c failure attempts logged: $fail_calls (≥2)"
  else
    FAIL_COUNT=$((FAIL_COUNT+1))
    FAILURES+=("T7c failure attempts: expected≥2 actual=$fail_calls")
    log "    ❌ T7c failure attempts: actual=$fail_calls"
  fi
  rm -rf "$tmp"
}

# ─── runner ────────────────────────────────────────────────────
[ -x "$WATCHER" ] || { echo "FATAL: watcher not found/executable: $WATCHER" >&2; exit 2; }
command -v inotifywait >/dev/null || { echo "FATAL: inotifywait not installed" >&2; exit 2; }
command -v python3 >/dev/null || { echo "FATAL: python3 not installed" >&2; exit 2; }
command -v flock >/dev/null || { echo "FATAL: flock not installed" >&2; exit 2; }

run_test "T1 modify event" T1_modify_event
run_test "T2 close_write event" T2_close_write_event
run_test "T3 moved_to event" T3_moved_to_event
run_test "T4 same-checksum dedup" T4_same_checksum_dedup
run_test "T5 cooldown pending+post-delivery (SRW-C1)" T5_pending_post_delivery
run_test "T6 singleton lock (SRW-C2)" T6_singleton_lock
run_test "T7 inbox_write failure resilience" T7_inbox_write_failure
run_test "T8 dual-notify idempotency (HND-SRW-C3)" T8_dual_notification_idempotency
run_test "T9 yaml parser top-level pick (HND-SRW-C4)" T9_yaml_parser_nested_id
run_test "T10 pending_since timestamp (HND-SRW-C1)" T10_pending_since_timestamp

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  shogun_report_watcher smoke test summary"
echo "  PASS: $PASS_COUNT"
echo "  FAIL: $FAIL_COUNT"
if [ "$FAIL_COUNT" -gt 0 ]; then
  echo "  failures:"
  for f in "${FAILURES[@]}"; do echo "    - $f"; done
fi
echo "════════════════════════════════════════════════════════════════"

[ "$FAIL_COUNT" -eq 0 ]
