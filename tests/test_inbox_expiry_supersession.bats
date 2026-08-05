#!/usr/bin/env bats
# test_inbox_expiry_supersession.bats — Lane B (subtask_residual_laneB_notify_repair_a7_20260715)
#
# Root cause (Task A / subtask_p0_laneC_notice_resend_rootcause_a7_20260715):
# Phase-3 escalation (scripts/inbox_watcher.sh) resets FIRST_UNREAD_SEEN on every
# cycle for a still-unread message, regardless of whether that message's content
# is stale/superseded. A stale standby-notice with no expiry/supersession marker
# therefore re-triggers nudge/Escape/clear forever.
#
# Fix: optional expires_at/supersedes fields (scripts/inbox_write.sh new_msg) are
# consumed by get_unread_count_fast()/get_unread_info() (scripts/inbox_watcher.sh)
# to auto-mark expired/superseded messages read=true BEFORE unread count, nudge,
# Escape, /clear, FIRST_UNREAD_SEEN timer, and stop-hook's `read: false` grep ever
# see them. Zero changes to the Phase-3 codex(1242)/command-layer(1247)/general(1253)
# branches themselves — all three consume the same expiry-aware upstream functions,
# so a single implementation covers all three uniformly (this is intentional: see
# queue/reports/ashigaru7_laneB_notify_repair_20260715.md for rationale).
#
# RED-first: this suite was first run against the pre-implementation backups
# (/tmp/.../scratchpad/laneB_backup_20260715_142955/*.bak-residual-20260715_142955)
# to confirm RED (expiry/supersession cases fail — feature did not exist), then
# against the live edited scripts/*.sh to confirm GREEN. See consolidated report
# for the RED run transcript (test command + exit code + pass/fail counts).

setup_file() {
    export PROJECT_ROOT
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"

    export WATCHER_SCRIPT="${LANEB_WATCHER_SCRIPT:-$PROJECT_ROOT/scripts/inbox_watcher.sh}"
    export INBOX_WRITE_SCRIPT="${LANEB_INBOX_WRITE_SCRIPT:-$PROJECT_ROOT/scripts/inbox_write.sh}"

    [ -f "$WATCHER_SCRIPT" ] || return 1
    [ -f "$INBOX_WRITE_SCRIPT" ] || return 1
    "$VENV_PYTHON" -c "import yaml" 2>/dev/null || return 1
}

setup() {
    export TEST_TMPDIR
    TEST_TMPDIR="$(mktemp -d "$BATS_TMPDIR/laneB_test.XXXXXX")"

    export TEST_INBOX="$TEST_TMPDIR/test_agent.yaml"
    cat > "$TEST_INBOX" << 'YAML'
messages: []
YAML

    export TEST_HARNESS="$TEST_TMPDIR/harness.sh"
    cat > "$TEST_HARNESS" << 'HARNESS'
#!/bin/bash
AGENT_ID="test_agent"
PANE_TARGET="test:0.0"
CLI_TYPE="claude"
INBOX="$TEST_INBOX"
LOCKFILE="${INBOX}.lock"
SCRIPT_DIR="$PROJECT_ROOT"

export __INBOX_WATCHER_TESTING__=1
source "$WATCHER_SCRIPT"
HARNESS
    chmod +x "$TEST_HARNESS"

    # inbox_write.sh integration tests need a SCRIPT_DIR-relative wrapper
    # (same technique as tests/test_inbox_write.bats), pointed at TEST_TMPDIR
    # so writes never touch the real queue/inbox/.
    export TEST_WRITE_DIR="$TEST_TMPDIR/write_scripts"
    mkdir -p "$TEST_WRITE_DIR"
    sed "s|SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")/..*|SCRIPT_DIR=\"$TEST_TMPDIR\"|" \
        "$INBOX_WRITE_SCRIPT" > "$TEST_WRITE_DIR/inbox_write.sh"
    chmod +x "$TEST_WRITE_DIR/inbox_write.sh"
    ln -sf "$PROJECT_ROOT/.venv" "$TEST_TMPDIR/.venv"
    mkdir -p "$TEST_TMPDIR/queue/inbox"
    export TEST_INBOX_WRITE="$TEST_WRITE_DIR/inbox_write.sh"
    export TEST_INBOX_DIR="$TEST_TMPDIR/queue/inbox"
    export HOME_OPENCLAW_GUARD="$TEST_TMPDIR/.openclaw_home"
}

teardown() {
    rm -rf "$TEST_TMPDIR"
}

# =============================================================================
# CASE 1 [general-ashigaru branch]: normal unread, no expiry/supersedes — must
# still be delivered exactly once, no regression (task's explicit "退行禁" requirement).
# =============================================================================
@test "LB-01 [general-ashigaru]: plain unread message (no expiry/supersedes) counts as unread" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_plain
    from: karo
    timestamp: "2026-07-15T10:00:00"
    type: task_assigned
    content: normal task
    read: false
YAML
    run bash -c "source '$TEST_HARNESS'; get_unread_count_fast"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert p["count"] == 1, p
print("LB-01: PASS")
PY
}

# =============================================================================
# CASE 2 [codex branch equivalent]: expires_at in the past → excluded from count,
# and get_unread_info() persists read=true on disk.
# =============================================================================
@test "LB-02 [codex]: expired message excluded from count and marked read on disk" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_expired
    from: shogun-second
    timestamp: "2026-07-14T16:41:00"
    type: task_assigned
    content: stale standby notice
    read: false
    expires_at: "2000-01-01T00:00:00"
YAML
    run bash -c "source '$TEST_HARNESS'; get_unread_count_fast"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert p["count"] == 0, p
print("LB-02a: PASS")
PY

    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output" "$TEST_INBOX"
import json, sys, yaml
p = json.loads(sys.argv[1])
assert p["count"] == 0, p
with open(sys.argv[2]) as f:
    data = yaml.safe_load(f)
assert data["messages"][0]["read"] is True, data
print("LB-02b: PASS")
PY
}

# =============================================================================
# CASE 3 [command-layer branch equivalent]: supersedes marks the older message
# read=true even though the older message was never itself read.
# =============================================================================
@test "LB-03 [command-layer]: supersedes marks the superseded message read on disk" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_old_notice
    from: shogun-second
    timestamp: "2026-07-14T17:31:00"
    type: task_assigned
    content: old standby notice
    read: false
  - id: msg_new_notice
    from: shogun-second
    timestamp: "2026-07-15T13:51:00"
    type: task_assigned
    content: supersedes old notice
    read: false
    supersedes: msg_old_notice
YAML
    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output" "$TEST_INBOX"
import json, sys, yaml
p = json.loads(sys.argv[1])
assert p["count"] == 1, p
with open(sys.argv[2]) as f:
    data = yaml.safe_load(f)
by_id = {m["id"]: m for m in data["messages"]}
assert by_id["msg_old_notice"]["read"] is True, by_id
assert by_id["msg_new_notice"]["read"] is False, by_id
print("LB-03: PASS")
PY
}

# =============================================================================
# CASE 4: expires_at in the future must NOT be auto-expired (no over-expiry).
# =============================================================================
@test "LB-04: future expires_at is not expired yet — still counted as unread" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_future
    from: karo
    timestamp: "2026-07-15T10:00:00"
    type: task_assigned
    content: not yet expired
    read: false
    expires_at: "2099-01-01T00:00:00"
YAML
    run bash -c "source '$TEST_HARNESS'; get_unread_count_fast"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert p["count"] == 1, p
print("LB-04: PASS")
PY
}

# =============================================================================
# CASE 5: supersedes pointing at a nonexistent id must not crash and must not
# incorrectly suppress anything — the superseding message itself still counts.
# =============================================================================
@test "LB-05: supersedes referencing a nonexistent id is a safe no-op" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_dangling
    from: karo
    timestamp: "2026-07-15T10:00:00"
    type: task_assigned
    content: supersedes nothing real
    read: false
    supersedes: msg_does_not_exist
YAML
    run bash -c "source '$TEST_HARNESS'; get_unread_count_fast"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert p["count"] == 1, p
print("LB-05: PASS")
PY
}

# =============================================================================
# CASE 6 [existing-schema backward compat]: messages predating this schema
# (no expires_at/supersedes keys at all, not even null) must not crash and
# must behave exactly as before.
# =============================================================================
@test "LB-06 [backward-compat]: pre-existing messages without expiry keys work unchanged" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_legacy
    from: karo
    timestamp: "2026-01-01T00:00:00"
    type: task_assigned
    content: legacy message predating schema
    read: false
YAML
    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert p["count"] == 1, p
print("LB-06: PASS")
PY
}

# =============================================================================
# CASE 7 [normal new-unread delivery, exactly once — no regression]: specials
# (clear_command) are still consumed exactly once, unaffected by the new
# expire/supersede mutation pass sharing the same atomic-write block.
#
# SUPERSEDED (W201, ashigaru3, 2026-08-04, 委員長殿裁可 msg_20260804_191210_11930ef7):
# This test asserts that get_unread_info() ALONE consumes (read=True) a
# clear_command on first call. That was the root cause of W201: a
# busy-guard-deferred clear_command was already committed read=True before
# send_cli_command ever ran, so "deferred to next cycle" silently meant lost
# forever. Left intentionally red (rule 9 — the failing test is the cost of
# the fix, not a defect; see
# docs/incident_logs/2026-08-04_w201_inbox_watcher_cure_a3.md §5).
# Successor test (asserts the corrected contract): "LB-07b" below.
# =============================================================================
@test "LB-07: clear_command special is still consumed exactly once (no regression)" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_clear
    from: karo
    timestamp: "2026-07-15T10:00:00"
    type: clear_command
    content: /clear
    read: false
YAML
    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert len(p["specials"]) == 1, p
PY

    # Second call: the special was already marked read → must not reappear.
    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert len(p["specials"]) == 0, p
assert p["count"] == 0, p
print("LB-07: PASS")
PY
}

# =============================================================================
# CASE 7b [W201 fix]: get_unread_info() alone must NOT consume a clear_command.
# It survives repeated calls unread until mark_message_processed() commits it
# — which process_unread() only calls after confirming actual execution.
# =============================================================================
@test "LB-07b: clear_command special survives repeated get_unread_info (W201 fix, no consume-on-extract)" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_clear
    from: karo
    timestamp: "2026-07-15T10:00:00"
    type: clear_command
    content: /clear
    read: false
YAML
    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert len(p["specials"]) == 1, p
PY

    # Second (and third) call: extraction alone is not consumption — the
    # special must still be present, unlike the superseded LB-07 contract.
    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert len(p["specials"]) == 1, p
assert p["specials"][0]["id"] == "msg_clear", p
PY

    # Only mark_message_processed (post-execution commit) consumes it.
    run bash -c "source '$TEST_HARNESS'; mark_message_processed msg_clear; get_unread_info"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert len(p["specials"]) == 0, p
assert p["count"] == 0, p
print("LB-07b: PASS")
PY
}

# =============================================================================
# CASE 8 [stop-hook exclusion]: after auto-expiry, the on-disk `read: false`
# count that stop_hook_inbox.sh's grep heuristic relies on is naturally zero —
# no changes needed to stop_hook_inbox.sh itself.
# =============================================================================
@test "LB-08 [stop-hook]: expired message removed from 'read: false' grep count after get_unread_info" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_expired_for_hook
    from: shogun-second
    timestamp: "2026-07-14T16:41:00"
    type: task_assigned
    content: stale standby notice
    read: false
    expires_at: "2000-01-01T00:00:00"
YAML
    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]

    run grep -c 'read: false' "$TEST_INBOX"
    [ "$status" -eq 1 ]  # grep -c exits 1 when count is 0
    [ "$output" -eq 0 ]
}

# =============================================================================
# CASE 9 [inbox_write.sh integration]: INBOX_EXPIRES_AT / INBOX_SUPERSEDES_ID
# env vars are written through to the message; absent by default (None), and
# not vulnerable to shell injection (routed via os.environ.get, not interpolation).
# =============================================================================
@test "LB-09 [inbox_write integration]: expires_at/supersedes env vars round-trip; absent by default" {
    run bash "$TEST_INBOX_WRITE" "test_agent" "no expiry" "task_assigned" "karo"
    [ "$status" -eq 0 ]

    INBOX_EXPIRES_AT="2099-01-01T00:00:00" INBOX_SUPERSEDES_ID="msg_dummy" \
        run bash "$TEST_INBOX_WRITE" "test_agent" "with expiry \$(whoami) \`id\`" "task_assigned" "karo"
    [ "$status" -eq 0 ]

    "$VENV_PYTHON" - << 'PY' "$TEST_INBOX_DIR/test_agent.yaml"
import sys, yaml
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
msgs = data["messages"]
assert msgs[0].get("expires_at") is None, msgs[0]
assert msgs[0].get("supersedes") is None, msgs[0]
assert msgs[1]["expires_at"] == "2099-01-01T00:00:00", msgs[1]
assert msgs[1]["supersedes"] == "msg_dummy", msgs[1]
# injection safety: literal shell metacharacters must survive as plain text
assert "$(whoami)" in msgs[1]["content"], msgs[1]["content"]
print("LB-09: PASS")
PY
}
