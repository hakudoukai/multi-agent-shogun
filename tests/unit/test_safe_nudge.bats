#!/usr/bin/env bats
# tests/unit/test_safe_nudge.bats — safe_nudge.sh unit tests
#
# 信長直命 (msg_20260508_191339) 配達本体 cycle2 担当。
# 対象: scripts/message_delivery_v2/safe_nudge.sh
#
# 検証ケース (5):
#   T-SN-001: cooldown 120s 内 → exit 1 (queued)
#   T-SN-002: pane_drift (claude path) → exit 3
#   T-SN-003: global_disable flag → exit 2
#   T-SN-004: 長文 nudge (>100 chars, codex) → exit 4 (book_mode_fallback)
#   T-SN-005: 正常 nudge → exit 0 (delivered) + cooldown file 更新
#
# tmux は mock 経由 (PATH 切替)、scripts は sandbox にコピーして実行。
# global_disable check には HOME を $FAKE_HOME に差し替えて実 ~/.openclaw を汚染しない。

setup_file() {
    export MDV2_SOURCE_ROOT
    MDV2_SOURCE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
    [ -f "$MDV2_SOURCE_ROOT/scripts/message_delivery_v2/safe_nudge.sh" ] || return 1
    [ -f "$MDV2_SOURCE_ROOT/scripts/message_delivery_v2/codex_guard.sh" ] || return 1
}

setup() {
    load '../test_helper/mock_tmux_pane.bash'
    setup_tmux_mock
    setup_mdv2_sandbox
}

# --- T-SN-001: cooldown 120s 内 → exit 1 (queued) ---

@test "T-SN-001: safe_nudge returns 1 (queued) when cooldown is active" {
    mock_pane_set "test:0.0" "test_agent" "claude"

    # claude pane は codex_guard を通らない → cooldown check 直行可能
    # 直前 nudge を「今」として記録
    date +%s > "$MDV2_SANDBOX/queue/watchers/test_agent.last_nudge"

    HOME="$FAKE_HOME" run bash "$MDV2_SAFE_NUDGE" \
        test_agent test:0.0 claude "inbox3"

    [ "$status" -eq 1 ]

    # send-keys は実行されていない (queued なので)
    ! grep -q "send-keys.*inbox3" "$MOCK_LOG"

    # JSON log に queued 記録
    log_file="$MDV2_SANDBOX/logs/message_delivery_v2/safe_nudge_$(date +%Y%m%d).log"
    [ -f "$log_file" ]
    grep -q '"result":"queued"' "$log_file"
}

# --- T-SN-002: pane_drift (claude path) → exit 3 ---

@test "T-SN-002: safe_nudge returns 3 (pane_drift) when @agent_id mismatches" {
    # claude path: pane の @agent_id が AGENT_ID と一致しないと exit 3
    mock_pane_set "test:0.0" "other_agent" "claude"

    HOME="$FAKE_HOME" run bash "$MDV2_SAFE_NUDGE" \
        test_agent test:0.0 claude "inbox3"

    [ "$status" -eq 3 ]

    # pane_drift 検出時は send-keys 絶対拒否
    ! grep -q "send-keys.*inbox3" "$MOCK_LOG"

    log_file="$MDV2_SANDBOX/logs/message_delivery_v2/safe_nudge_$(date +%Y%m%d).log"
    grep -q '"result":"pane_drift"' "$log_file"
}

# --- T-SN-003: global_disable flag → exit 2 ---

@test "T-SN-003: safe_nudge returns 2 (blocked) when global_disable flag exists" {
    # global_disable check は CLI 種別に関係なく最優先
    touch "$FAKE_HOME/.openclaw/global_disable"
    mock_pane_set "test:0.0" "test_agent" "claude"

    HOME="$FAKE_HOME" run bash "$MDV2_SAFE_NUDGE" \
        test_agent test:0.0 claude "inbox3"

    [ "$status" -eq 2 ]

    # global_disable 時は tmux に一切触らない (cooldown / send-keys なし)
    ! grep -q "send-keys" "$MOCK_LOG"

    log_file="$MDV2_SANDBOX/logs/message_delivery_v2/safe_nudge_$(date +%Y%m%d).log"
    grep -q "global_disable" "$log_file"
}

# --- T-SN-004: 長文 nudge (>100 chars, codex) → exit 4 (book_mode_fallback) ---

@test "T-SN-004: safe_nudge returns 4 (book_mode_fallback) for long codex nudge" {
    # codex path: codex_guard を pass する状態にしておく必要あり
    mock_pane_set "test:0.0" "test_agent" "codex"
    # codex_guard が pass する典型 idle 状態 (> 1 non-empty lines, no Working/sandbox/bash prompt)
    export MOCK_CAPTURE_PANE=$'codex idle\nsome help line\n> '

    # cooldown は 120 秒以上前にして codex_guard cooldown も pass させる
    echo $(($(date +%s) - 200)) > "$MDV2_SANDBOX/queue/watchers/test_agent.last_nudge"

    # 100 文字超 nudge (= 反省点 w 対応 — Codex 長文 submit 不確定回避)
    long_nudge=""
    for _ in $(seq 1 30); do
        long_nudge="${long_nudge}abcd "
    done
    # 30 * 5 = 150 chars
    [ "${#long_nudge}" -gt 100 ]

    HOME="$FAKE_HOME" run bash "$MDV2_SAFE_NUDGE" \
        test_agent test:0.0 codex "$long_nudge"

    [ "$status" -eq 4 ]

    # send-keys は実行されない (book mode に fallback)
    ! grep -q "send-keys" "$MOCK_LOG"

    # session_health の book_mode jsonl に記録される
    book_log="$MDV2_SANDBOX/queue/session_health/test_agent.book_mode.jsonl"
    [ -f "$book_log" ]
    grep -q '"reason":"long_nudge_codex"' "$book_log"

    log_file="$MDV2_SANDBOX/logs/message_delivery_v2/safe_nudge_$(date +%Y%m%d).log"
    grep -q '"result":"book_mode"' "$log_file"
}

# --- T-SN-005: 正常 nudge → exit 0 (delivered) + cooldown file 更新 ---

@test "T-SN-005: safe_nudge returns 0 (delivered) and updates cooldown file on success" {
    mock_pane_set "test:0.0" "test_agent" "claude"

    cooldown_file="$MDV2_SANDBOX/queue/watchers/test_agent.last_nudge"
    # cooldown ファイル不在 → 初回 nudge シナリオ
    [ ! -f "$cooldown_file" ]

    HOME="$FAKE_HOME" run bash "$MDV2_SAFE_NUDGE" \
        test_agent test:0.0 claude "inbox3"

    [ "$status" -eq 0 ]

    # send-keys が呼ばれる (Enter 引数つき)
    grep -q "send-keys.* inbox3 Enter" "$MOCK_LOG"

    # cooldown file が現在時刻で更新される
    [ -f "$cooldown_file" ]
    cooldown_ts=$(cat "$cooldown_file")
    now=$(date +%s)
    diff=$((now - cooldown_ts))
    # 0 〜 5 秒以内
    [ "$diff" -ge 0 ]
    [ "$diff" -le 5 ]

    log_file="$MDV2_SANDBOX/logs/message_delivery_v2/safe_nudge_$(date +%Y%m%d).log"
    grep -q '"result":"delivered"' "$log_file"
}
