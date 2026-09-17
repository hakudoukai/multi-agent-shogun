#!/usr/bin/env bats
# tests/unit/test_safe_nudge_doppler.bats — safe_nudge.sh doppler-pane unit tests
#
# 対象: scripts/archive/message_delivery_v2_full_20260508/safe_nudge.sh
#   (tests/unit/test_safe_nudge.bats が指す scripts/message_delivery_v2/ は樹に無く、
#    其の setup_file は入口で落ちる。本 file は archive path を直に指す。)
#
# 背景: 入口条件 `CLI_TYPE == claude` (:83) と `pane_cmd != claude` (:90) が狭く、
#   ⒜ cli_type=doppler は身元検め(:85)ごと素通り → 名違ひ pane へ文が入る
#   ⒝ cli_type=claude + doppler 実装 pane は :90 で rc=3 → 艦隊全体が拒まれる
#   当て = :83 を ^(claude|doppler)$ へ、:90 を ^(claude|doppler|node)$ へ (2 行)。
#
# 検証ケース (7):
#   T-SND-001: cli=doppler / 名一致  / pane=doppler → 0 delivered, send-keys 1
#   T-SND-002: cli=doppler / 名違ひ  / pane=doppler → 3 pane_drift(expected=), send-keys 0  ★⒜の升★
#   T-SND-003: cli=claude  / 名一致  / pane=doppler → 0 delivered, send-keys 1              ★⒝の升★
#   T-SND-004: cli=claude  / 名一致  / pane=claude  → 0 delivered (従前不変)
#   T-SND-005: cli=claude  / 名違ひ  / pane=claude  → 3 pane_drift (従前不変)
#   T-SND-006: cli=doppler / 名一致  / pane=bash    → 3 pane_drift(expected_cmd=), send-keys 0
#   T-SND-007: queue/watchers 不在 → send-keys 1 の ★後★ に rc=1 (特性の記録 = 欠陥の写し・受入ではない)
#
# tmux は mock (tests/test_helper/mock_tmux_pane.bash の setup_tmux_mock) 経由。
# sandbox は script を <root>/scripts/message_delivery_v2/ へ置く (= ${_NUDGE_DIR}/../.. が根へ解ける深さ)。

setup_file() {
    export MDV2_SOURCE_ROOT
    MDV2_SOURCE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
    export SND_SRC="$MDV2_SOURCE_ROOT/scripts/archive/message_delivery_v2_full_20260508/safe_nudge.sh"
    [ -f "$SND_SRC" ] || return 1
}

setup() {
    load '../test_helper/mock_tmux_pane.bash'
    setup_tmux_mock
    setup_snd_sandbox
}

# archive の script を二段の深さへ置く sandbox (setup_mdv2_sandbox の path 違ひ版)
setup_snd_sandbox() {
    : "${BATS_TEST_TMPDIR:?BATS_TEST_TMPDIR must be set}"
    export SND_SANDBOX="${BATS_TEST_TMPDIR}/sandbox"
    mkdir -p "$SND_SANDBOX/scripts/message_delivery_v2"
    mkdir -p "$SND_SANDBOX/queue/watchers"
    mkdir -p "$SND_SANDBOX/queue/session_health"
    mkdir -p "$SND_SANDBOX/logs/message_delivery_v2"
    cp "$SND_SRC" "$SND_SANDBOX/scripts/message_delivery_v2/safe_nudge.sh"
    chmod +x "$SND_SANDBOX/scripts/message_delivery_v2/safe_nudge.sh"
    export SND_SAFE_NUDGE="$SND_SANDBOX/scripts/message_delivery_v2/safe_nudge.sh"
    export SND_LOG="$SND_SANDBOX/logs/message_delivery_v2/safe_nudge_$(date +%Y%m%d).log"
    export FAKE_HOME="${BATS_TEST_TMPDIR}/home"
    mkdir -p "$FAKE_HOME/.openclaw"
}

# send-keys が呼ばれた回数 (mock の呼ばれ台帳から。rc と別の道で着弾を測る)
snd_sendkeys_count() {
    grep -c 'send-keys' "$MOCK_LOG" 2>/dev/null || true
}

# log の欄の件数 (log file が未だ無ければ 0 ── :132 で落ちた時は log_event に届かぬ)
snd_log_count() {
    if [ -f "$SND_LOG" ]; then grep -c "$1" "$SND_LOG" || true; else echo 0; fi
}

@test "T-SND-001: cli=doppler, id match, pane cmd doppler -> 0 delivered" {
    mock_pane_set "test:0.0" "test_agent" "doppler"
    HOME="$FAKE_HOME" run bash "$SND_SAFE_NUDGE" test_agent test:0.0 doppler "inbox3"
    [ "$status" -eq 0 ]
    [ "$(snd_sendkeys_count)" -eq 1 ]
    grep -q '"result":"delivered"' "$SND_LOG"
}

@test "T-SND-002: cli=doppler, id MISMATCH -> 3 pane_drift, no send-keys (identity gate now applies)" {
    mock_pane_set "test:0.0" "other_agent" "doppler"
    HOME="$FAKE_HOME" run bash "$SND_SAFE_NUDGE" test_agent test:0.0 doppler "inbox3"
    [ "$status" -eq 3 ]
    [ "$(snd_sendkeys_count)" -eq 0 ]
    grep -q '"result":"pane_drift"' "$SND_LOG"
    grep -q 'expected=test_agent actual=other_agent' "$SND_LOG"
}

@test "T-SND-003: cli=claude, id match, pane cmd doppler -> 0 delivered (no longer rejected)" {
    mock_pane_set "test:0.0" "test_agent" "doppler"
    HOME="$FAKE_HOME" run bash "$SND_SAFE_NUDGE" test_agent test:0.0 claude "inbox3"
    [ "$status" -eq 0 ]
    [ "$(snd_sendkeys_count)" -eq 1 ]
    grep -q '"result":"delivered"' "$SND_LOG"
}

@test "T-SND-004: cli=claude, id match, pane cmd claude -> 0 delivered (unchanged)" {
    mock_pane_set "test:0.0" "test_agent" "claude"
    HOME="$FAKE_HOME" run bash "$SND_SAFE_NUDGE" test_agent test:0.0 claude "inbox3"
    [ "$status" -eq 0 ]
    [ "$(snd_sendkeys_count)" -eq 1 ]
}

@test "T-SND-005: cli=claude, id MISMATCH, pane cmd claude -> 3 pane_drift (unchanged)" {
    mock_pane_set "test:0.0" "other_agent" "claude"
    HOME="$FAKE_HOME" run bash "$SND_SAFE_NUDGE" test_agent test:0.0 claude "inbox3"
    [ "$status" -eq 3 ]
    [ "$(snd_sendkeys_count)" -eq 0 ]
    grep -q 'expected=test_agent actual=other_agent' "$SND_LOG"
}

@test "T-SND-006: cli=doppler, id match, pane cmd bash -> 3 pane_drift(expected_cmd), no send-keys" {
    mock_pane_set "test:0.0" "test_agent" "bash"
    HOME="$FAKE_HOME" run bash "$SND_SAFE_NUDGE" test_agent test:0.0 doppler "inbox3"
    [ "$status" -eq 3 ]
    [ "$(snd_sendkeys_count)" -eq 0 ]
    grep -q 'expected_cmd=claude actual_cmd=bash' "$SND_LOG"
}

# 特性の記録 (characterization): cooldown 書込 (:132) は send-keys (:122) の後に在り、
# 置き場が無いと set -e で落ちて rc=1 に成る。∴ rc=1 は「未着弾(cooldown)」と「着弾済(書込失敗)」の二義。
# 之は欠陥の写しであつて受入条件ではない。直しは別弾 (log の欄で分けよ)。
@test "T-SND-007: watchers dir absent -> send-keys happens, THEN rc=1 (documents the rc=1 ambiguity)" {
    mock_pane_set "test:0.0" "test_agent" "doppler"
    rmdir "$SND_SANDBOX/queue/watchers"
    HOME="$FAKE_HOME" run bash "$SND_SAFE_NUDGE" test_agent test:0.0 doppler "inbox3"
    [ "$status" -eq 1 ]
    [ "$(snd_sendkeys_count)" -eq 1 ]
    # 'queued' も 'delivered' も記録されぬ (log_event に届く前に落ちる)
    [ "$(snd_log_count '"result":"queued"')" -eq 0 ]
    [ "$(snd_log_count '"result":"delivered"')" -eq 0 ]
}
