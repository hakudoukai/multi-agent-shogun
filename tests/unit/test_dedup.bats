#!/usr/bin/env bats
# test_dedup.bats — message_delivery_v2 dedup.sh unit tests
#
# 信長殿直命 msg_20260508_191339_1c0c756f 準拠。
# scripts/message_delivery_v2/dedup.sh の API を検証する。
#
# Tests:
#   T-001: dedup_record 後 dedup_already_processed → 0 (= already)
#   T-002: 未記録 msg_id → 1 (= not processed)
#   T-003: dedup_cleanup で expires_at 過去 entry 削除
#   T-004: dedup_count が正しい数を返す
#   T-005: dedup_record は idempotent (重複 record しても count 増えない)

SCRIPT_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
DEDUP_SH="$SCRIPT_DIR/scripts/message_delivery_v2/dedup.sh"

setup_file() {
    [ -f "$DEDUP_SH" ] || return 1
    command -v python3 >/dev/null 2>&1 || return 1
    python3 -c "import yaml" 2>/dev/null || return 1
}

setup() {
    TEST_TMP="$(mktemp -d "$BATS_TMPDIR/dedup_test.XXXXXX")"
    mkdir -p "$TEST_TMP/queue"

    # source 後に DEDUP_TABLE を上書き (= production の queue/message_dedup.yaml には触らない)
    set +u
    # shellcheck disable=SC1090
    source "$DEDUP_SH"
    set -u
    DEDUP_TABLE="$TEST_TMP/queue/message_dedup.yaml"
    export DEDUP_TABLE
}

teardown() {
    [ -n "${TEST_TMP:-}" ] && [ -d "$TEST_TMP" ] && rm -rf "$TEST_TMP"
}

@test "T-001: dedup_record 後 dedup_already_processed が 0 (= already) を返す" {
    dedup_record "msg_test_001" "delivered"
    run dedup_already_processed "msg_test_001"
    [ "$status" -eq 0 ]
}

@test "T-002: 未記録 msg_id で dedup_already_processed が 1 (= not processed) を返す" {
    run dedup_already_processed "msg_unknown_xyz"
    [ "$status" -eq 1 ]
}

@test "T-003: dedup_cleanup で expires_at 過去 entry が削除される" {
    # 過去 expire entry を直接書込 (= 期限切れ)
    cat > "$DEDUP_TABLE" <<'EOF'
processed:
  - msg_id: msg_expired_001
    processed_at: "2020-01-01T00:00:00+09:00"
    ack_by: delivered
    expires_at: "2020-01-02T00:00:00+09:00"
  - msg_id: msg_active_002
    processed_at: "2099-01-01T00:00:00+09:00"
    ack_by: delivered
    expires_at: "2099-12-31T00:00:00+09:00"
EOF

    dedup_cleanup

    # 期限切れは消え、active のみ残る
    run dedup_already_processed "msg_expired_001"
    [ "$status" -eq 1 ]
    run dedup_already_processed "msg_active_002"
    [ "$status" -eq 0 ]
}

@test "T-004: dedup_count が現在 entry 数と一致する" {
    dedup_record "msg_count_a" "delivered"
    dedup_record "msg_count_b" "delivered"
    dedup_record "msg_count_c" "delivered"
    run dedup_count
    [ "$status" -eq 0 ]
    [ "$output" -eq 3 ]
}

@test "T-005: dedup_record は idempotent (= 同一 msg_id 二度 record しても 1 件)" {
    dedup_record "msg_idem_001" "delivered"
    dedup_record "msg_idem_001" "delivered"
    run dedup_count
    [ "$output" -eq 1 ]
}
