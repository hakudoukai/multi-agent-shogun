#!/usr/bin/env bats
# test_hermes2_deaddrop_stale_detector.bats
#
# hermes2 (環境部長) legacy dead-drop YAML の read-only stale 検知器 — TDD テスト
# 起点: 副委員長 work order hermes2-dead-drop-route-guard-work-order-20260721.md item 3
#
# 目的: queue/inbox/hermes2.yaml の未読件数の「新規増加」を検知するが、
# 検知器自身は配送 consumer にはならない (本文再送・既読化・削除は絶対禁止)。
# state は queue/inbox/ の外 (queue/metrics/) に保持し、対象 YAML には
# 一切書き込まない。

setup_file() {
    export PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export DETECTOR_SCRIPT="$PROJECT_ROOT/scripts/hermes2_deaddrop_stale_detector.sh"
    export VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"
    "$VENV_PYTHON" -c "import yaml" 2>/dev/null || return 1
}

setup() {
    export TEST_TMPDIR="$(mktemp -d "$BATS_TMPDIR/h2_stale_test.XXXXXX")"
    export TEST_INBOX_DIR="$TEST_TMPDIR/queue/inbox"
    export TEST_METRICS_DIR="$TEST_TMPDIR/queue/metrics"
    mkdir -p "$TEST_INBOX_DIR" "$TEST_METRICS_DIR"

    export TEST_SCRIPT_DIR="$TEST_TMPDIR/scripts"
    mkdir -p "$TEST_SCRIPT_DIR"
    sed "s|SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")/..*|SCRIPT_DIR=\"$TEST_TMPDIR\"|" \
        "$PROJECT_ROOT/scripts/hermes2_deaddrop_stale_detector.sh" > "$TEST_SCRIPT_DIR/hermes2_deaddrop_stale_detector.sh"
    chmod +x "$TEST_SCRIPT_DIR/hermes2_deaddrop_stale_detector.sh"
    ln -sf "$PROJECT_ROOT/.venv" "$TEST_TMPDIR/.venv"
    export TEST_DETECTOR="$TEST_SCRIPT_DIR/hermes2_deaddrop_stale_detector.sh"

    export HERMES2_INBOX="$TEST_INBOX_DIR/hermes2.yaml"
    export STALE_STATE_FILE="$TEST_METRICS_DIR/hermes2_deaddrop_stale_state.yaml"
}

teardown() {
    [ -n "$TEST_TMPDIR" ] && [ -d "$TEST_TMPDIR" ] && rm -rf "$TEST_TMPDIR"
}

_write_inbox_n_unread() {
    local n="$1"
    local total="${2:-$n}"
    "$VENV_PYTHON" - "$HERMES2_INBOX" "$n" "$total" <<'PYEOF'
import sys, yaml
path, n, total = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
n = min(n, total)
msgs = []
for i in range(total):
    msgs.append({
        "id": f"msg_test_{i}",
        "from": "some_producer",
        "timestamp": "2026-07-21T00:00:00",
        "type": "status_update",
        "content": f"test message {i}",
        "read": i >= n,  # first n are unread, rest are read
    })
with open(path, "w") as f:
    yaml.safe_dump({"messages": msgs}, f, allow_unicode=True)
PYEOF
}

# =============================================================================
# D-001: legacy hermes2.yaml absent → graceful zero-unread baseline, exit 0,
# detector must NOT create/touch queue/inbox/hermes2.yaml itself.
# =============================================================================

@test "D-001: hermes2.yaml absent → baseline established, exit 0, target file NOT created" {
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [ ! -f "$HERMES2_INBOX" ]
    [ -f "$STALE_STATE_FILE" ]
}

# =============================================================================
# D-002: first run with existing unread messages → baseline established
# (not treated as growth, since there is no prior state to compare against).
# =============================================================================

@test "D-002: first run with 7 unread messages → baseline established, exit 0" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"baseline"* ]]
    [ -f "$STALE_STATE_FILE" ]
}

# =============================================================================
# D-003: second run, unread count unchanged → OK, no growth, exit 0
# =============================================================================

@test "D-003: unread count unchanged across two runs → no growth, exit 0" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" != *"GROWTH"* ]]
}

# =============================================================================
# D-004: second run, unread count increased → stale growth detected, exit 1
# =============================================================================

@test "D-004: unread count increases across two runs → GROWTH detected, exit 1" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    _write_inbox_n_unread 9 9
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"GROWTH"* ]]
}

# =============================================================================
# D-005 / D-006: read-only guarantee — detector never mutates the target
# YAML file (no resend, no read-marking, no deletion) across repeated runs.
# =============================================================================

@test "D-005: detector never modifies hermes2.yaml content across multiple runs" {
    _write_inbox_n_unread 7 7
    before_sha="$(sha256sum "$HERMES2_INBOX" | awk '{print $1}')"

    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    after_sha="$(sha256sum "$HERMES2_INBOX" | awk '{print $1}')"
    [ "$before_sha" = "$after_sha" ]
}

@test "D-006: detector never marks messages read=true in hermes2.yaml" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    unread_after=$("$VENV_PYTHON" -c "
import yaml
with open('$HERMES2_INBOX') as f:
    data = yaml.safe_load(f)
print(sum(1 for m in data['messages'] if not m.get('read', False)))
")
    [ "$unread_after" -eq 7 ]
}

# =============================================================================
# D-007: 2 consecutive clean (no-growth) cycles → detector reports the
# 2-cycle confirmation explicitly (work order item 6 evidence requirement).
# =============================================================================

@test "D-007: 2 consecutive no-growth cycles → detector reports 2-cycle confirmation" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"consecutive_clean_cycles=2"* ]] || [[ "$output" == *"2-cycle"* ]]
}

# =============================================================================
# D-008: unread count decreases (e.g. manual triage) → not growth, exit 0
# =============================================================================

@test "D-008: unread count decreases across two runs → not growth, exit 0" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    _write_inbox_n_unread 3 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" != *"GROWTH"* ]]
}

# =============================================================================
# D-009: state file itself lives outside queue/inbox/ (never inside the
# directory the guard is protecting).
# =============================================================================

@test "D-009: state file is stored outside queue/inbox/" {
    _write_inbox_n_unread 1 1
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    case "$STALE_STATE_FILE" in
        "$TEST_INBOX_DIR"/*) false ;;
        *) true ;;
    esac
}

# =============================================================================
# D-010: finding H2-G1-STALE-DETECTOR-COUNT-ALIASING-002 — 未読件数が同数の
# まま「旧未読1件が既読化 (or 消滅)」+「新規未読1件が到着」する同数入替が
# 起きた場合、件数だけの比較では差分ゼロとなり検知漏れする。ID 集合の差分
# 比較であれば、前回未読 ID 集合に存在しなかった新規 ID の出現を検知できる。
# =============================================================================

_write_inbox_with_ids() {
    # $1.. = space-separated "id:read" pairs, e.g. "msg_0:False msg_1:True"
    "$VENV_PYTHON" - "$HERMES2_INBOX" "$@" <<'PYEOF'
import sys, yaml
path = sys.argv[1]
pairs = sys.argv[2:]
msgs = []
for pair in pairs:
    mid, read_flag = pair.split(":")
    msgs.append({
        "id": mid,
        "from": "some_producer",
        "timestamp": "2026-07-21T00:00:00",
        "type": "status_update",
        "content": f"test message {mid}",
        "read": read_flag == "True",
    })
with open(path, "w") as f:
    yaml.safe_dump({"messages": msgs}, f, allow_unicode=True)
PYEOF
}

@test "D-010: unread count stays constant but one unread ID is swapped for a new one → GROWTH detected, exit 1" {
    _write_inbox_with_ids \
        "msg_0:False" "msg_1:False" "msg_2:False" "msg_3:False" \
        "msg_4:False" "msg_5:False" "msg_6:False"
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"baseline"* ]]

    # msg_0 は既読化 (or triage 済) されて消え、代わりに新規 msg_new が
    # 未読で到着 → unread 件数は 7 のまま変わらない (count-neutral swap)。
    _write_inbox_with_ids \
        "msg_0:True" "msg_1:False" "msg_2:False" "msg_3:False" \
        "msg_4:False" "msg_5:False" "msg_6:False" "msg_new:False"
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"GROWTH"* ]]
}
