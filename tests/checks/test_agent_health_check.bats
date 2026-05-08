#!/usr/bin/env bats
# test_agent_health_check.bats
#
# scripts/agent_health_check.sh の bats 自動テスト
# (cmd_agent_health_check_unified_001、信長殿 msg_134138 R1 統合命令)。
#
# Phase 5 γ-3 (codex persona 検知) + Phase F (token 上限接近 escalation)
# + 共通 helper (cooldown / shogun inbox / Supabase error_log) を網羅。
#
# シナリオ:
#   H-001 disable_health_check flag → 即時 exit 0、check 実行なし
#   H-002 global_disable flag → 即時 exit 0
#   H-003 SUPABASE_URL 未設定 → exit 2 + ERR-INFRA-002 log
#   H-004 codex persona pane で codex CLI 検出 → alert なし
#   H-005 codex persona pane で claude CLI 検出 → ERR-PERSONA-CLI-001 alert
#   H-006 token 200k+ session 検出 → ERR-TOKEN-WARN-001 alert
#   H-007 token 240k+ session 検出 → ERR-TOKEN-CRITICAL-001 alert
#   H-008 cooldown 抑制 → 5min 以内の 2 回目 alert は発火せず

setup_file() {
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
    export PROJECT_ROOT
    export SCRIPT="$PROJECT_ROOT/scripts/agent_health_check.sh"
    [ -f "$SCRIPT" ] || return 1
}

setup() {
    BATS_TMPDIR_TEST="$(mktemp -d "${BATS_RUN_TMPDIR:-/tmp}/agent_health_check_test.XXXXXX")"
    export BATS_TMPDIR_TEST

    # fixture 用 directory
    export HEALTH_CHECK_LOG="$BATS_TMPDIR_TEST/health.log"
    export HEALTH_CHECK_STRUCT_LOG="$BATS_TMPDIR_TEST/struct.log"
    export HEALTH_CHECK_COOLDOWN_DIR="$BATS_TMPDIR_TEST/cooldown"
    export HEALTH_CHECK_TOKEN_PROJECT_DIR="$BATS_TMPDIR_TEST/jsonl"
    mkdir -p "$HEALTH_CHECK_COOLDOWN_DIR" "$HEALTH_CHECK_TOKEN_PROJECT_DIR"

    # 既定 env (= disable flag は別 fixture に置換、SUPABASE は dummy)
    export SUPABASE_URL="http://dummy.invalid"
    export SUPABASE_SERVICE_ROLE_KEY="dummy_key"

    # disable flag 経路を fixture HOME に隔離 (= ~/.openclaw を上書き)
    export HOME="$BATS_TMPDIR_TEST/home"
    mkdir -p "$HOME/.openclaw"

    # PATH 先頭に stub bin を置き、tmux/curl/pgrep/pstree を fixture stub に差替。
    export STUB_BIN="$BATS_TMPDIR_TEST/bin"
    mkdir -p "$STUB_BIN"
    export PATH="$STUB_BIN:$PATH"

    # 既定 stub 群 (= claude/codex pane 存在シナリオを模擬、agent-down/inbox-overflow alert を抑制)
    cat > "$STUB_BIN/tmux" <<'STUB'
#!/usr/bin/env bash
case "$1" in
  list-panes)
    # -F フラグ有無で出力切替 (= agent-down check には "claude" 返却)
    if printf '%s\n' "$@" | grep -q -- '-F'; then
      echo "claude"
    fi
    exit 0
    ;;
  display-message)
    echo 99999
    ;;
  *) exit 0 ;;
esac
STUB
    chmod +x "$STUB_BIN/tmux"

    cat > "$STUB_BIN/pstree" <<'STUB'
#!/usr/bin/env bash
# 既定: codex 階層を返す (= persona check OK)
echo "bash(99999)---node(99998)---codex(99997)"
STUB
    chmod +x "$STUB_BIN/pstree"

    cat > "$STUB_BIN/curl" <<'STUB'
#!/usr/bin/env bash
# Supabase 通信は no-op で空 array
echo "[]"
exit 0
STUB
    chmod +x "$STUB_BIN/curl"

    cat > "$STUB_BIN/ssh" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
    chmod +x "$STUB_BIN/ssh"

    # codex persona pane 配置を 1 件に絞る (= fixture 制御性)
    export HEALTH_CHECK_CODEX_PANES="multiagent:0.3:ieyasu"
}

teardown() {
    rm -rf "$BATS_TMPDIR_TEST" 2>/dev/null || true
}

# ─── H-001: disable_health_check flag → 即時 exit 0 ─────────────────────
@test "H-001: disable_health_check flag → 即時 exit 0、check 実行なし" {
    touch "$HOME/.openclaw/disable_health_check"
    run bash "$SCRIPT" --quiet
    [ "$status" -eq 0 ]
    [ ! -f "$HEALTH_CHECK_LOG" ] || ! grep -q "alerts:" "$HEALTH_CHECK_LOG"
}

# ─── H-002: global_disable flag → 即時 exit 0 ───────────────────────────
@test "H-002: global_disable flag → 即時 exit 0" {
    touch "$HOME/.openclaw/global_disable"
    run bash "$SCRIPT" --quiet
    [ "$status" -eq 0 ]
}

# ─── H-003: SUPABASE_URL 未設定 → exit 2 + ERR-INFRA-002 ────────────────
@test "H-003: SUPABASE_URL 未設定 → exit 2 + ERR-INFRA-002 log" {
    unset SUPABASE_URL
    run bash "$SCRIPT" --quiet
    [ "$status" -eq 2 ]
    grep -q "ERR-INFRA-002" "$HEALTH_CHECK_LOG"
    grep -q "missing_env=SUPABASE_URL" "$HEALTH_CHECK_LOG"
}

# ─── H-004: codex persona pane で codex CLI 検出 → alert なし ──────────
@test "H-004: codex persona pane で codex CLI 検出 → ERR-PERSONA-CLI-001 alert なし" {
    run bash "$SCRIPT" --quiet
    # exit 1 (= ntfy alert) ではなく、persona alert は無いはず
    grep -q "ERR-PERSONA-CLI-001" "$HEALTH_CHECK_LOG" && return 1
    grep -q '"event":"persona_cli_detected"' "$HEALTH_CHECK_STRUCT_LOG"
    grep -q '"cli":"codex"' "$HEALTH_CHECK_STRUCT_LOG"
}

# ─── H-005: codex persona pane で claude CLI 検出 → ERR-PERSONA-CLI-001 ─
@test "H-005: codex persona pane で claude CLI 検出 → ERR-PERSONA-CLI-001 alert" {
    # pstree stub を claude 階層に差替
    cat > "$STUB_BIN/pstree" <<'STUB'
#!/usr/bin/env bash
echo "bash(99999)---claude(99997)"
STUB
    chmod +x "$STUB_BIN/pstree"

    run bash "$SCRIPT" --quiet
    grep -q "ERR-PERSONA-CLI-001" "$HEALTH_CHECK_LOG"
    grep -q "ieyasu" "$HEALTH_CHECK_LOG"
    [ "$status" -eq 1 ]
}

# ─── H-006: token 200k+ session 検出 → ERR-TOKEN-WARN-001 alert ────────
@test "H-006: token 200k+ session 検出 → ERR-TOKEN-WARN-001 alert" {
    # fixture jsonl: 220k tokens 相当を 1 行
    local sid="warntest1234"
    cat > "$HEALTH_CHECK_TOKEN_PROJECT_DIR/${sid}.jsonl" <<'JSONL'
{"message":{"usage":{"input_tokens":1,"cache_creation_input_tokens":1000,"cache_read_input_tokens":219000,"output_tokens":50}}}
JSONL
    # mtime を現在に強制 (= find -mmin -10 マッチ)
    touch "$HEALTH_CHECK_TOKEN_PROJECT_DIR/${sid}.jsonl"

    run bash "$SCRIPT" --quiet
    grep -q "ERR-TOKEN-WARN-001" "$HEALTH_CHECK_LOG"
    grep -q "warntes" "$HEALTH_CHECK_LOG"
    [ "$status" -eq 1 ]
}

# ─── H-007: token 240k+ session 検出 → ERR-TOKEN-CRITICAL-001 alert ────
@test "H-007: token 240k+ session 検出 → ERR-TOKEN-CRITICAL-001 alert" {
    local sid="crittest1234"
    cat > "$HEALTH_CHECK_TOKEN_PROJECT_DIR/${sid}.jsonl" <<'JSONL'
{"message":{"usage":{"input_tokens":1,"cache_creation_input_tokens":1000,"cache_read_input_tokens":250000,"output_tokens":50}}}
JSONL
    touch "$HEALTH_CHECK_TOKEN_PROJECT_DIR/${sid}.jsonl"

    run bash "$SCRIPT" --quiet
    grep -q "ERR-TOKEN-CRITICAL-001" "$HEALTH_CHECK_LOG"
    grep -q "crittes" "$HEALTH_CHECK_LOG"
    [ "$status" -eq 1 ]
}

# ─── H-008: cooldown 抑制 → 5min 以内の 2 回目 alert は発火せず ────────
@test "H-008: cooldown 抑制 → 5min 以内の 2 回目 alert は発火せず" {
    local sid="cooldown1234"
    cat > "$HEALTH_CHECK_TOKEN_PROJECT_DIR/${sid}.jsonl" <<'JSONL'
{"message":{"usage":{"input_tokens":1,"cache_creation_input_tokens":1000,"cache_read_input_tokens":250000,"output_tokens":50}}}
JSONL
    touch "$HEALTH_CHECK_TOKEN_PROJECT_DIR/${sid}.jsonl"

    # 1 回目 → alert 発火 + cooldown file 作成
    run bash "$SCRIPT" --quiet
    [ "$status" -eq 1 ]
    grep -q "ERR-TOKEN-CRITICAL-001" "$HEALTH_CHECK_LOG"
    [ -f "$HEALTH_CHECK_COOLDOWN_DIR/token_crit_cooldown.last" ]

    # 2 回目 → cooldown により ERR-TOKEN-CRITICAL-001 は発火せず
    # (= 他 check 由来 alert は許容、本 test の関心は cooldown による specific alert 抑制)
    : > "$HEALTH_CHECK_LOG"
    run bash "$SCRIPT" --quiet
    ! grep -q "ERR-TOKEN-CRITICAL-001" "$HEALTH_CHECK_LOG"
}
