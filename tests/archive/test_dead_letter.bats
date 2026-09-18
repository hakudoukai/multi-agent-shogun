#!/usr/bin/env bats
# test_dead_letter.bats — message_delivery_v2 dead_letter.sh unit tests
#
# 信長殿直命 msg_20260508_191339_1c0c756f 準拠。
# scripts/message_delivery_v2/dead_letter.sh の API を検証する。
#
# Tests:
#   T-001: increment_retry で count が増加する (0 → 1 → 2)
#   T-002: is_over_retry_cap が retry_count >= 5 で true (= 0)
#   T-003: is_over_retry_cap が retry_count < 5 で false (= 1)
#   T-004: move_to_dead_letter で queue/dead_letter/<agent>/<msg_id>.yaml 作成
#   T-005: benign reason (dedup_skip) で escalation 抑制
#   T-006: benign reason (self_send) で escalation 抑制
#   T-007: benign reason (expired_ttl) で escalation 抑制
#   T-008: その他 reason で 信長 inbox に critical_alert 送信

SCRIPT_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
DLQ_SH="$SCRIPT_DIR/scripts/message_delivery_v2/dead_letter.sh"

setup_file() {
    [ -f "$DLQ_SH" ] || return 1
}

setup() {
    TEST_PROJECT_ROOT="$(mktemp -d "$BATS_TMPDIR/dlq_test.XXXXXX")"
    mkdir -p \
        "$TEST_PROJECT_ROOT/queue/dead_letter" \
        "$TEST_PROJECT_ROOT/queue/watchers" \
        "$TEST_PROJECT_ROOT/queue/inbox" \
        "$TEST_PROJECT_ROOT/scripts"

    # stub inbox_write.sh — 引数を escalation_log に追記
    ESCALATION_LOG="$TEST_PROJECT_ROOT/escalation.log"
    : > "$ESCALATION_LOG"
    cat > "$TEST_PROJECT_ROOT/scripts/inbox_write.sh" <<EOF
#!/usr/bin/env bash
echo "ESCALATED: \$@" >> "$ESCALATION_LOG"
EOF
    chmod +x "$TEST_PROJECT_ROOT/scripts/inbox_write.sh"

    # source 後に内部 path を一時 project root へ向ける
    set +u
    # shellcheck disable=SC1090
    source "$DLQ_SH"
    set -u
    _DLQ_PROJECT_ROOT="$TEST_PROJECT_ROOT"
    DLQ_BASE="$TEST_PROJECT_ROOT/queue/dead_letter"
    RETRY_STATE_DIR="$TEST_PROJECT_ROOT/queue/watchers"
    export _DLQ_PROJECT_ROOT DLQ_BASE RETRY_STATE_DIR
}

teardown() {
    [ -n "${TEST_PROJECT_ROOT:-}" ] && [ -d "$TEST_PROJECT_ROOT" ] && rm -rf "$TEST_PROJECT_ROOT"
}

@test "T-001: increment_retry で count が 0 → 1 → 2 と増加する" {
    run increment_retry "ashigaru1" "msg_inc_001"
    [ "$status" -eq 0 ]
    [ "$output" -eq 1 ]

    run increment_retry "ashigaru1" "msg_inc_001"
    [ "$output" -eq 2 ]

    run get_retry_count "ashigaru1" "msg_inc_001"
    [ "$output" -eq 2 ]
}

@test "T-002: is_over_retry_cap が retry_count = 5 で true (return 0)" {
    echo "5" > "$RETRY_STATE_DIR/ashigaru1.retry.msg_cap_001"
    run is_over_retry_cap "ashigaru1" "msg_cap_001"
    [ "$status" -eq 0 ]
}

@test "T-003: is_over_retry_cap が retry_count = 4 で false (return 1)" {
    echo "4" > "$RETRY_STATE_DIR/ashigaru1.retry.msg_under_001"
    run is_over_retry_cap "ashigaru1" "msg_under_001"
    [ "$status" -eq 1 ]
}

@test "T-004: move_to_dead_letter で queue/dead_letter/<agent>/<msg_id>.yaml 作成" {
    echo "5" > "$RETRY_STATE_DIR/ashigaru2.retry.msg_dlq_001"

    run move_to_dead_letter "ashigaru2" "msg_dlq_001" "retry_exceeded" "test content"
    [ "$status" -eq 0 ]

    local dlq_file="$DLQ_BASE/ashigaru2/msg_dlq_001.yaml"
    [ -f "$dlq_file" ]

    grep -q '^msg_id: msg_dlq_001$' "$dlq_file"
    grep -q '^agent_id: ashigaru2$' "$dlq_file"
    grep -q '^reason: retry_exceeded$' "$dlq_file"
    grep -q '^retry_count: 5$' "$dlq_file"
    grep -q '^retry_cap: 5$' "$dlq_file"

    # retry state cleanup
    [ ! -f "$RETRY_STATE_DIR/ashigaru2.retry.msg_dlq_001" ]
}

@test "T-005: benign reason (dedup_skip) で escalation 抑制 + escalation_sent: false" {
    run move_to_dead_letter "ashigaru1" "msg_benign_dedup" "dedup_skip" "x"
    [ "$status" -eq 0 ]

    # 信長 inbox 呼出なし
    run grep -c 'ESCALATED' "$ESCALATION_LOG"
    [ "$output" -eq 0 ]

    # dlq file 内 escalation_sent: false のまま
    grep -q '^escalation_sent: false$' "$DLQ_BASE/ashigaru1/msg_benign_dedup.yaml"
}

@test "T-006: benign reason (self_send) で escalation 抑制" {
    run move_to_dead_letter "ashigaru1" "msg_benign_self" "self_send" "x"
    [ "$status" -eq 0 ]

    run grep -c 'ESCALATED' "$ESCALATION_LOG"
    [ "$output" -eq 0 ]
    grep -q '^escalation_sent: false$' "$DLQ_BASE/ashigaru1/msg_benign_self.yaml"
}

@test "T-007: benign reason (expired_ttl) で escalation 抑制" {
    run move_to_dead_letter "ashigaru1" "msg_benign_ttl" "expired_ttl" "x"
    [ "$status" -eq 0 ]

    run grep -c 'ESCALATED' "$ESCALATION_LOG"
    [ "$output" -eq 0 ]
    grep -q '^escalation_sent: false$' "$DLQ_BASE/ashigaru1/msg_benign_ttl.yaml"
}

@test "T-008: その他 reason (retry_exceeded) で 信長 inbox に critical_alert 送信 + escalation_sent: true" {
    echo "5" > "$RETRY_STATE_DIR/ashigaru3.retry.msg_alert_001"

    run move_to_dead_letter "ashigaru3" "msg_alert_001" "retry_exceeded" "fail content"
    [ "$status" -eq 0 ]

    # 信長 inbox stub が呼ばれた
    [ -s "$ESCALATION_LOG" ]
    grep -q 'shogun' "$ESCALATION_LOG"
    grep -q 'critical_alert' "$ESCALATION_LOG"
    grep -q 'dead_letter_handler' "$ESCALATION_LOG"

    # dlq file 内 escalation_sent: true に更新
    grep -q '^escalation_sent: true$' "$DLQ_BASE/ashigaru3/msg_alert_001.yaml"
}
