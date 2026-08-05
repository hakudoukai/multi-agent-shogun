#!/usr/bin/env bats
# agent_selfwatch.bats — Agent self-watch unit tests (TDD Step 3)
#
# FR/NFR trace (tests/specs/agent_selfwatch_spec.md):
#   TC-FR-001,002,003,004,005,006,007,008,009,010,011,014
#   TC-NFR-002,003,008
#
# Note:
#   This file intentionally includes RED tests for yet-to-be-implemented
#   Phase 1-3 features (TDD flow: test first, implementation later).

setup_file() {
    export PROJECT_ROOT
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"

    export WATCHER_SCRIPT="$PROJECT_ROOT/scripts/inbox_watcher.sh"
    export INBOX_WRITE_SCRIPT="$PROJECT_ROOT/scripts/inbox_write.sh"
    export ASHIGARU_INSTR="$PROJECT_ROOT/instructions/generated/codex-ashigaru.md"

    [ -f "$WATCHER_SCRIPT" ] || return 1
    [ -f "$INBOX_WRITE_SCRIPT" ] || return 1
    [ -f "$ASHIGARU_INSTR" ] || return 1
    "$VENV_PYTHON" -c "import yaml" 2>/dev/null || return 1
}

setup() {
    export TEST_TMPDIR
    TEST_TMPDIR="$(mktemp -d "$BATS_TMPDIR/agent_selfwatch_test.XXXXXX")"

    export TEST_INBOX="$TEST_TMPDIR/test_agent.yaml"
    cat > "$TEST_INBOX" << 'YAML'
messages: []
YAML

    export MOCK_LOG="$TEST_TMPDIR/tmux_calls.log"
    > "$MOCK_LOG"

    export TEST_HARNESS="$TEST_TMPDIR/harness.sh"
    cat > "$TEST_HARNESS" << 'HARNESS'
#!/bin/bash
AGENT_ID="test_agent"
PANE_TARGET="test:0.0"
CLI_TYPE="${TEST_CLI_TYPE:-claude}"
INBOX="$TEST_INBOX"
LOCKFILE="${INBOX}.lock"
SCRIPT_DIR="$PROJECT_ROOT"
IDLE_FLAG_DIR="$TEST_TMPDIR"

tmux() {
    echo "tmux $*" >> "$MOCK_LOG"
    if echo "$*" | grep -q "capture-pane"; then
        echo "${MOCK_CAPTURE_PANE:-}"
        return 0
    fi
    if echo "$*" | grep -q "send-keys"; then
        return "${MOCK_SENDKEYS_RC:-0}"
    fi
    return 0
}

timeout() { shift; "$@"; }
sleep() { :; }
pgrep() { return "${MOCK_PGREP_RC:-1}"; }
export -f tmux timeout sleep pgrep

export __INBOX_WATCHER_TESTING__=1
source "$WATCHER_SCRIPT"
HARNESS
    chmod +x "$TEST_HARNESS"
}

teardown() {
    rm -rf "$TEST_TMPDIR"
}

@test "TC-FR-001 [RED]: process_unread_once is defined and called on startup" {
    grep -q "process_unread_once()" "$WATCHER_SCRIPT"
    grep -q "process_unread_once" "$WATCHER_SCRIPT"
}

@test "TC-FR-002: inotify + timeout fallback is configured" {
    grep -q "INOTIFY_TIMEOUT=" "$WATCHER_SCRIPT"
    grep -F -q 'inotifywait -q -t "$INOTIFY_TIMEOUT" -e modify -e close_write "$INBOX"' "$WATCHER_SCRIPT"
}

# SUPERSEDED (W201, ashigaru3, 2026-08-04, 委員長殿裁可 msg_20260804_191210_11930ef7):
# This test asserts the pre-fix "consume-before-commit" contract — that
# get_unread_info() itself commits read=True for clear_command/model_switch
# the moment they are extracted, before any execution is attempted. That
# contract was the root cause of W201 (a busy-guard-deferred clear_command
# was already committed read=True in the file, so the next cycle's `unread`
# filter skipped it forever — "deferred to next cycle" silently meant lost).
# Left intentionally red, not deleted or edited (rule 9: a broken test here
# is the cost of the fix, not a defect — see
# docs/incident_logs/2026-08-04_w201_inbox_watcher_cure_a3.md §5).
# Successor test (asserts the corrected contract): "TC-FR-003b" below.
@test "TC-FR-003: get_unread_info routes task/special messages correctly" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_task
    from: karo
    timestamp: "2026-02-09T21:00:00"
    type: task_assigned
    content: task
    read: false
  - id: msg_clear
    from: karo
    timestamp: "2026-02-09T21:00:01"
    type: clear_command
    content: /clear
    read: false
  - id: msg_model
    from: karo
    timestamp: "2026-02-09T21:00:02"
    type: model_switch
    content: /model opus
    read: false
YAML

    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]

    "$VENV_PYTHON" - << 'PY' "$output" "$TEST_INBOX"
import json, sys, yaml
payload = json.loads(sys.argv[1])
inbox_path = sys.argv[2]
assert payload["count"] == 1, payload
assert len(payload["specials"]) == 2, payload

with open(inbox_path) as f:
    data = yaml.safe_load(f)
by_id = {m["id"]: m for m in data["messages"]}
assert by_id["msg_task"]["read"] is False
assert by_id["msg_clear"]["read"] is True
assert by_id["msg_model"]["read"] is True
print("OK")
PY
}

# Successor of TC-FR-003 (W201 fix, ashigaru3, 2026-08-04): specials must
# NOT be consumed at extraction time. get_unread_info() may be called
# repeatedly with zero side effect on read state — only mark_message_processed()
# (called by process_unread() after confirmed execution) may commit read=True.
@test "TC-FR-003b: get_unread_info does not consume specials at extraction (W201 fix)" {
    cat > "$TEST_INBOX" << 'YAML'
messages:
  - id: msg_task
    from: karo
    timestamp: "2026-02-09T21:00:00"
    type: task_assigned
    content: task
    read: false
  - id: msg_clear
    from: karo
    timestamp: "2026-02-09T21:00:01"
    type: clear_command
    content: /clear
    read: false
  - id: msg_model
    from: karo
    timestamp: "2026-02-09T21:00:02"
    type: model_switch
    content: /model opus
    read: false
YAML

    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]

    "$VENV_PYTHON" - << 'PY' "$output" "$TEST_INBOX"
import json, sys, yaml
payload = json.loads(sys.argv[1])
inbox_path = sys.argv[2]
assert payload["count"] == 1, payload
assert len(payload["specials"]) == 2, payload

with open(inbox_path) as f:
    data = yaml.safe_load(f)
by_id = {m["id"]: m for m in data["messages"]}
assert by_id["msg_task"]["read"] is False
# W201 fix: extraction alone must NOT commit read=True for specials.
assert by_id["msg_clear"]["read"] is False, by_id["msg_clear"]
assert by_id["msg_model"]["read"] is False, by_id["msg_model"]
print("OK")
PY

    # Second call must return the SAME specials — proving no consume-on-read.
    run bash -c "source '$TEST_HARNESS'; get_unread_info"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$output"
import json, sys
p = json.loads(sys.argv[1])
assert len(p["specials"]) == 2, p
print("TC-FR-003b: PASS")
PY

    # mark_message_processed is the ONLY path that commits read=True.
    run bash -c "source '$TEST_HARNESS'; mark_message_processed msg_clear"
    [ "$status" -eq 0 ]
    "$VENV_PYTHON" - << 'PY' "$TEST_INBOX"
import sys, yaml
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
by_id = {m["id"]: m for m in data["messages"]}
assert by_id["msg_clear"]["read"] is True, by_id["msg_clear"]
assert by_id["msg_model"]["read"] is False, by_id["msg_model"]
print("mark_message_processed: PASS")
PY
}

@test "TC-FR-004 [RED]: read-update path uses lock/atomic protections" {
    body="$(awk '/get_unread_info\\(\\)/,/^}/' "$WATCHER_SCRIPT")"
    echo "$body" | grep -q "flock"
    echo "$body" | grep -q "os.replace"
}

@test "TC-FR-005: post-task inbox check rule is documented for ashigaru" {
    grep -q "MANDATORY Post-Task Inbox Check" "$ASHIGARU_INSTR"
}

@test "TC-FR-006 [RED]: metrics hooks are defined (unread_latency/read_count/estimated_tokens)" {
    grep -q "unread_latency_sec" "$WATCHER_SCRIPT"
    grep -q "read_count" "$WATCHER_SCRIPT"
    grep -q "estimated_tokens" "$WATCHER_SCRIPT"
}

@test "TC-FR-007 [RED]: feature flags for Phase 1/2/3 are defined" {
    grep -q "ASW_PHASE" "$WATCHER_SCRIPT"
    grep -q "ASW_" "$WATCHER_SCRIPT"
}

@test "TC-FR-008 [RED]: normal nudge can be disabled (Phase 2 behavior)" {
    grep -q "disable_normal_nudge" "$WATCHER_SCRIPT"
}

@test "TC-FR-009: special command compatibility for codex is preserved" {
    run bash -c "TEST_CLI_TYPE=codex; source '$TEST_HARNESS'; send_cli_command /clear"
    [ "$status" -eq 0 ]
    grep -q "send-keys -t test:0.0 /new" "$MOCK_LOG"
    grep -q "send-keys -t test:0.0 Enter" "$MOCK_LOG"

    > "$MOCK_LOG"
    run bash -c "TEST_CLI_TYPE=codex; source '$TEST_HARNESS'; send_cli_command '/model opus'"
    [ "$status" -eq 0 ]
    ! grep -q "/model opus" "$MOCK_LOG"
}

@test "TC-FR-016 (W205): busy guard now covers non-/clear commands too" {
    # Before this fix, only /clear was busy-guarded; /model went straight to
    # send-keys mid-Working. IDLE_FLAG_DIR default (no flag file) = busy for
    # effective_cli=claude (see agent_is_busy()'s flag-file branch).
    # rc=2 (distinct from rc=1 injection failure) so process_unread() knows
    # this is a routine defer-and-retry, not a return_message_to_sender case.
    run bash -c "source '$TEST_HARNESS'; send_cli_command '/model opus'"
    [ "$status" -eq 2 ]
    ! grep -q "/model opus" "$MOCK_LOG"
}

@test "TC-FR-017 (W205): idle agent + successful send-keys still delivers /clear" {
    touch "$TEST_TMPDIR/shogun_idle_test_agent"
    run bash -c "source '$TEST_HARNESS'; send_cli_command /clear"
    [ "$status" -eq 0 ]
    grep -q "send-keys -t test:0.0 /clear" "$MOCK_LOG"
    grep -q "send-keys -t test:0.0 Enter" "$MOCK_LOG"
}

@test "TC-FR-018 (W205): Enter delivery verification catches stuck unsent text" {
    # MOCK_CAPTURE_PANE simulates the command text still sitting unsent in
    # the input line after Enter (e.g. an autocomplete popup ate the Enter).
    # Previously this was never checked — send-keys \"succeeding\" (rc=0) was
    # treated as delivery. send_keys_verified must retry then report failure.
    touch "$TEST_TMPDIR/shogun_idle_test_agent"
    export MOCK_CAPTURE_PANE="/model opus"
    run bash -c "export MOCK_CAPTURE_PANE; source '$TEST_HARNESS'; send_cli_command '/model opus'"
    [ "$status" -eq 1 ]
    [[ "$output" == *"ERROR: CLI command delivery not confirmed"* ]]
}

@test "TC-FR-019 (W205): send-keys failure (rc!=0) is no longer swallowed by || true" {
    # Before this fix, \`tmux send-keys ... || true\` discarded a failed
    # injection and send_cli_command still fell through to \`return 0\`
    # (or, for /clear, to the busy-check-only \`return 1\`) — a send failure
    # and a successful send were indistinguishable to the caller.
    touch "$TEST_TMPDIR/shogun_idle_test_agent"
    export MOCK_SENDKEYS_RC=1
    run bash -c "export MOCK_SENDKEYS_RC; source '$TEST_HARNESS'; send_cli_command '/model opus'"
    [ "$status" -eq 1 ]
}

@test "TC-FR-010 [RED]: summary-first fast path exists (count/summary before full read)" {
    grep -q "summary-first" "$WATCHER_SCRIPT"
    grep -q "unread_count fast-path" "$WATCHER_SCRIPT"
}

@test "TC-FR-011 [RED]: send-keys is restricted to final escalation only" {
    grep -q "FINAL_ESCALATION_ONLY" "$WATCHER_SCRIPT"
}

@test "TC-FR-014 + TC-NFR-002: inbox_write IF and schema remain backward compatible" {
    # ★sandbox化 (2026-08-05 止血是正・止血命令の根治源)★:
    # 実 inbox_write.sh を直呼びすると canon fail-closed gate (leg B) が
    # target=test_agent を canon 外と判定し、実 queue/inbox/karo.yaml へ
    # delivery_failed 便を書いてしまう (実測: 該当4通が滞留)。
    # ∴ 健全例二つの技法をそのまま流用 (Anti-Duplication・新規手法を発明せず):
    #   ① test_inbox_write.bats の sed SCRIPT_DIR retarget
    #   ② test_shadow_mailbox_failclosed.bats の HOME override + disable_cross_pc_bridge
    local sandbox_dir="$TEST_TMPDIR/sandbox_tc_fr_014"
    local sandbox_script_dir="$sandbox_dir/scripts"
    mkdir -p "$sandbox_script_dir" "$sandbox_dir/queue/inbox"

    sed "s|SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")/..*|SCRIPT_DIR=\"$sandbox_dir\"|" \
        "$INBOX_WRITE_SCRIPT" > "$sandbox_script_dir/inbox_write.sh"
    chmod +x "$sandbox_script_dir/inbox_write.sh"
    ln -sf "$PROJECT_ROOT/.venv" "$sandbox_dir/.venv"

    # canon gate が通るよう test_agent/karo をこの sandbox 限りの名簿へ登録
    cat > "$sandbox_dir/queue/pane_registry.yaml" << 'REGISTRY'
pane_registry:
  panes:
    - agent_id: test_agent
    - agent_id: karo
REGISTRY

    # cross-PC bridge (inbox_write.sh L539-) は実 $HOME/.openclaw/disable_cross_pc_bridge
    # を見る。実 $HOME を書き換えず、fake home へ差し替えて無効化する (real $HOME 不触)。
    local real_home="$HOME"
    export HOME="$sandbox_dir/fake_home"
    mkdir -p "$HOME/.openclaw"
    touch "$HOME/.openclaw/disable_cross_pc_bridge"

    run bash "$sandbox_script_dir/inbox_write.sh" test_agent "compat-check" task_assigned karo

    export HOME="$real_home"

    [ "$status" -eq 0 ]

    "$VENV_PYTHON" - << 'PY' "$sandbox_dir/queue/inbox/test_agent.yaml"
import sys, yaml
p = sys.argv[1]
with open(p) as f:
    data = yaml.safe_load(f)
assert "messages" in data and isinstance(data["messages"], list)
msg = data["messages"][-1]
for k in ("id", "from", "timestamp", "type", "content", "read"):
    assert k in msg
assert msg["type"] == "task_assigned"
assert msg["from"] == "karo"
print("OK")
PY
}

@test "TC-NFR-003 [RED]: no-idle-full-read helper exists" {
    grep -q "no_idle_full_read" "$WATCHER_SCRIPT"
}

@test "TC-NFR-008: test file itself has no skip directives (SKIP=0 guard)" {
    ! grep -Eq '^[[:space:]]*skip([[:space:]]|$)' "$BATS_TEST_FILENAME"
}
