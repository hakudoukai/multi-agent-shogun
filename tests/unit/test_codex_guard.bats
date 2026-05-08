#!/usr/bin/env bats
# tests/unit/test_codex_guard.bats — codex_guard.sh unit tests
#
# 信長直命 (msg_20260508_191339) 配達本体 cycle2 担当。
# 対象: scripts/message_delivery_v2/codex_guard.sh
#
# 検証ケース (6):
#   T-CG-001: 'Yes, proceed' fixture → exit 2 (sandbox prompt)
#   T-CG-002: 'Working' fixture → exit 2 (working state)
#   T-CG-003: 'user@host:.../$ ' fixture → exit 5 (bash_shell)
#   T-CG-004: 空 capture → exit 4 (tui_empty)
#   T-CG-005: pane_drift → exit 3
#   T-CG-006: 正常 → exit 0
#
# tmux は mock 経由 (PATH 切替) で MOCK_* 環境変数で挙動制御。

setup_file() {
    export MDV2_SOURCE_ROOT
    MDV2_SOURCE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
    [ -f "$MDV2_SOURCE_ROOT/scripts/message_delivery_v2/codex_guard.sh" ] || return 1
}

setup() {
    load '../test_helper/mock_tmux_pane.bash'
    setup_tmux_mock
    setup_mdv2_sandbox
}

# --- T-CG-001: 'Yes, proceed' fixture → exit 2 ---

@test "T-CG-001: codex_guard returns 2 (sandbox prompt) when 'Yes, proceed' is in capture" {
    mock_pane_set "test:0.0" "test_agent" "node"
    # ≥ 2 non-empty lines + sandbox 確認 prompt が tail に出現
    export MOCK_CAPTURE_PANE=$'codex working state\nDo you want to allow this command?\nYes, proceed\nNo, deny'

    run bash "$MDV2_CODEX_GUARD" test_agent test:0.0

    [ "$status" -eq 2 ]
    echo "$output" | grep -qi "sandbox"
}

# --- T-CG-002: 'Working' fixture → exit 2 ---

@test "T-CG-002: codex_guard returns 2 (interruption_risk) when Working marker present" {
    mock_pane_set "test:0.0" "test_agent" "node"
    # Codex Working マーカー (= 反省点 c の典型)
    export MOCK_CAPTURE_PANE=$'some output\n• Working (12s • esc to interrupt)\nstill running'

    run bash "$MDV2_CODEX_GUARD" test_agent test:0.0

    [ "$status" -eq 2 ]
    echo "$output" | grep -qi "Working"
}

# --- T-CG-003: 'user@host:.../$ ' fixture → exit 5 ---

@test "T-CG-003: codex_guard returns 5 (bash_shell) when bash prompt detected" {
    mock_pane_set "test:0.0" "test_agent" "node"
    # Codex 終了 → bash shell に戻った状態 (= 反省点 x)
    export MOCK_CAPTURE_PANE=$'codex exited\nuser@host:~/projects/multi-agent-shogun$ '

    run bash "$MDV2_CODEX_GUARD" test_agent test:0.0

    [ "$status" -eq 5 ]
    echo "$output" | grep -qi "bash_shell"
}

# --- T-CG-004: 空 capture → exit 4 ---

@test "T-CG-004: codex_guard returns 4 (tui_empty) when capture is empty" {
    mock_pane_set "test:0.0" "test_agent" "node"
    # TUI 空白 (反省点 d) — 起動直後 / 表示飛び等
    export MOCK_CAPTURE_PANE=""

    run bash "$MDV2_CODEX_GUARD" test_agent test:0.0

    [ "$status" -eq 4 ]
    echo "$output" | grep -qi "tui_empty\|book mode"
}

# --- T-CG-005: pane_drift → exit 3 ---

@test "T-CG-005: codex_guard returns 3 (pane_drift) when @agent_id mismatches" {
    # pane は存在するが @agent_id が要求と一致しない (= 反省点 n 誤配)
    mock_pane_set "test:0.0" "wrong_agent" "node"
    export MOCK_CAPTURE_PANE=$'> idle\nready'

    run bash "$MDV2_CODEX_GUARD" test_agent test:0.0

    [ "$status" -eq 3 ]
    echo "$output" | grep -qi "pane_drift"
}

# --- T-CG-006: 正常 → exit 0 ---

@test "T-CG-006: codex_guard returns 0 (allow) when all guards pass" {
    mock_pane_set "test:0.0" "test_agent" "node"
    # idle Codex prompt (≥ 2 non-empty lines, no Working/sandbox/bash prompt)
    export MOCK_CAPTURE_PANE=$'codex ready\nawaiting input\n> '

    # cooldown は十分前にしておく (= cooldown でも exit 0 にはならず exit 1 になるため)
    echo $(($(date +%s) - 200)) > "$MDV2_SANDBOX/queue/watchers/test_agent.last_nudge"

    run bash "$MDV2_CODEX_GUARD" test_agent test:0.0

    [ "$status" -eq 0 ]
    echo "$output" | grep -qi "allow"
}
