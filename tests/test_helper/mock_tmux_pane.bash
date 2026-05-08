#!/usr/bin/env bash
# tests/test_helper/mock_tmux_pane.bash — tmux pane mocking helpers for bats
#
# message_delivery_v2 scripts (safe_nudge.sh / codex_guard.sh) を unit test するための
# tmux mock + sandbox 構築ヘルパ。PATH を切替えて `tmux` を MOCK_* 環境変数で
# 制御するスタブに置換する。
#
# 使い方:
#   load '../test_helper/mock_tmux_pane.bash'
#   setup() {
#       setup_tmux_mock          # PATH に mock tmux を差し込む
#       setup_mdv2_sandbox       # safe_nudge / codex_guard を sandbox にコピー
#   }
#   @test "..." {
#       export MOCK_PANE_LIST="test:0.0"
#       export MOCK_PANE_AGENT_ID="test_agent"
#       export MOCK_CAPTURE_PANE=$'> ready\nidle prompt'
#       HOME="$FAKE_HOME" run bash "$MDV2_SAFE_NUDGE" test_agent test:0.0 claude "inbox3"
#       [ "$status" -eq 0 ]
#   }
#
# 制御変数:
#   MOCK_PANE_LIST          list-panes が返す行 (改行区切り)
#   MOCK_PANE_AGENT_ID      display-message '#{@agent_id}' の値
#   MOCK_PANE_CMD           display-message '#{pane_current_command}' の値 (default: claude)
#   MOCK_CAPTURE_PANE       capture-pane の出力
#   MOCK_SENDKEYS_RC        send-keys の exit code (default: 0)
#   MOCK_LOG                tmux 呼出 log file path (auto-set)
#   MDV2_SANDBOX            sandbox project root (auto-set)
#   MDV2_SAFE_NUDGE         safe_nudge.sh path in sandbox (auto-set)
#   MDV2_CODEX_GUARD        codex_guard.sh path in sandbox (auto-set)
#   FAKE_HOME               $HOME 代替 (auto-set, .openclaw/ も作成済)

setup_tmux_mock() {
    : "${BATS_TEST_TMPDIR:?BATS_TEST_TMPDIR must be set (run via bats)}"

    export MOCK_BIN_DIR="${BATS_TEST_TMPDIR}/mock_bin"
    mkdir -p "$MOCK_BIN_DIR"

    export MOCK_LOG="${BATS_TEST_TMPDIR}/tmux_calls.log"
    : > "$MOCK_LOG"

    export MOCK_PANE_LIST=""
    export MOCK_PANE_AGENT_ID=""
    export MOCK_PANE_CMD="claude"
    export MOCK_CAPTURE_PANE=""
    export MOCK_SENDKEYS_RC=0

    cat > "$MOCK_BIN_DIR/tmux" << 'TMUX_MOCK'
#!/usr/bin/env bash
# Mock tmux — controlled by MOCK_* env vars. Logs every invocation to MOCK_LOG.
printf 'tmux %s\n' "$*" >> "${MOCK_LOG}"

cmd="${1:-}"
shift || true

case "$cmd" in
  list-panes)
    if [[ -n "${MOCK_PANE_LIST:-}" ]]; then
      printf '%s\n' "$MOCK_PANE_LIST"
    fi
    exit 0
    ;;
  display-message)
    fmt=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        -p)
          shift
          fmt="${1:-}"
          ;;
      esac
      shift || true
    done
    case "$fmt" in
      "#{@agent_id}")
        printf '%s\n' "${MOCK_PANE_AGENT_ID:-}"
        ;;
      "#{pane_current_command}")
        printf '%s\n' "${MOCK_PANE_CMD:-claude}"
        ;;
      *)
        printf '\n'
        ;;
    esac
    exit 0
    ;;
  capture-pane)
    if [[ -n "${MOCK_CAPTURE_PANE:-}" ]]; then
      printf '%s\n' "$MOCK_CAPTURE_PANE"
    fi
    exit 0
    ;;
  send-keys)
    exit "${MOCK_SENDKEYS_RC:-0}"
    ;;
  *)
    exit 0
    ;;
esac
TMUX_MOCK
    chmod +x "$MOCK_BIN_DIR/tmux"

    export PATH="$MOCK_BIN_DIR:$PATH"
}

setup_mdv2_sandbox() {
    : "${BATS_TEST_TMPDIR:?BATS_TEST_TMPDIR must be set}"
    : "${MDV2_SOURCE_ROOT:?MDV2_SOURCE_ROOT must point at project root}"

    export MDV2_SANDBOX="${BATS_TEST_TMPDIR}/sandbox"
    mkdir -p "$MDV2_SANDBOX/scripts/message_delivery_v2"
    mkdir -p "$MDV2_SANDBOX/queue/watchers"
    mkdir -p "$MDV2_SANDBOX/queue/session_health"
    mkdir -p "$MDV2_SANDBOX/logs/message_delivery_v2"

    cp "$MDV2_SOURCE_ROOT/scripts/message_delivery_v2/safe_nudge.sh" \
       "$MDV2_SANDBOX/scripts/message_delivery_v2/safe_nudge.sh"
    cp "$MDV2_SOURCE_ROOT/scripts/message_delivery_v2/codex_guard.sh" \
       "$MDV2_SANDBOX/scripts/message_delivery_v2/codex_guard.sh"
    chmod +x "$MDV2_SANDBOX/scripts/message_delivery_v2/safe_nudge.sh" \
             "$MDV2_SANDBOX/scripts/message_delivery_v2/codex_guard.sh"

    export MDV2_SAFE_NUDGE="$MDV2_SANDBOX/scripts/message_delivery_v2/safe_nudge.sh"
    export MDV2_CODEX_GUARD="$MDV2_SANDBOX/scripts/message_delivery_v2/codex_guard.sh"

    export FAKE_HOME="${BATS_TEST_TMPDIR}/home"
    mkdir -p "$FAKE_HOME/.openclaw"
}

mock_pane_set() {
    local pane="${1:-test:0.0}"
    local agent_id="${2:-test_agent}"
    local cmd="${3:-claude}"
    export MOCK_PANE_LIST="$pane"
    export MOCK_PANE_AGENT_ID="$agent_id"
    export MOCK_PANE_CMD="$cmd"
}

mock_log_grep_count() {
    local pattern="$1"
    local count
    count=$(grep -cE "$pattern" "$MOCK_LOG" 2>/dev/null || true)
    printf '%s\n' "${count:-0}"
}
