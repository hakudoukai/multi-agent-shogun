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
#
# cycle2 fix 追加シナリオ (信長殿 msg_145251 watcher 2 件欠陥対処):
#   H-009 codex persona pane で pane_current_command='node' 検出 → alert なし
#         (= ERR-PERSONA-CLI-001 誤検知修正、AGENTS.md 444650b 整合)
#   H-010 TEST_MODE=1 で send_shogun_inbox_alert が真の inbox_write を抑制
#         (= bats test fixture 漏出による信長 inbox 流入防止)

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

    # cycle2 fix: TEST_MODE で send_shogun_inbox_alert を suppress
    # (= bats test fixture が信長 inbox に漏出するのを防止)。
    # TEST_INBOX_WRITE_LOG に呼出記録を残し、test 内で抑制を検証可能にする。
    export TEST_MODE=1
    export TEST_INBOX_WRITE_LOG="$BATS_TMPDIR_TEST/test_inbox_write.log"
    : > "$TEST_INBOX_WRITE_LOG"

    # disable flag 経路を fixture HOME に隔離 (= ~/.openclaw を上書き)
    export HOME="$BATS_TMPDIR_TEST/home"
    mkdir -p "$HOME/.openclaw"

    # PATH 先頭に stub bin を置き、tmux/curl/pgrep/pstree を fixture stub に差替。
    export STUB_BIN="$BATS_TMPDIR_TEST/bin"
    mkdir -p "$STUB_BIN"
    export PATH="$STUB_BIN:$PATH"

    # 既定 stub 群 (= claude/codex pane 存在シナリオを模擬、agent-down/inbox-overflow alert を抑制)
    # cycle2 fix: display-message は -p '#{...}' format 別に応答 (= persona check で
    # pane_current_command を直接判定する logic に対応、TMUX_STUB_PANE_CMD で test 制御可)。
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
    fmt=""
    shift
    while [ $# -gt 0 ]; do
      case "$1" in
        -p) shift; fmt="${1:-}"; shift ;;
        *)  shift ;;
      esac
    done
    case "$fmt" in
      *pane_current_command*) echo "${TMUX_STUB_PANE_CMD:-}" ;;
      *pane_pid*)             echo "99999" ;;
      *)                      echo "99999" ;;
    esac
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

# ─── H-009: cycle2 fix — pane_current_command='node' は codex 扱い (誤検知修正) ──
@test "H-009: codex persona pane で pane_current_command='node' 検出 → ERR-PERSONA-CLI-001 alert なし (cycle2 fix)" {
    # codex CLI は ~/.npm-global/bin/codex 経由で node child process として動作 → pane_current_command='node'
    # cycle1 logic では pstree fallback で node のみだと "other" 扱い → 誤 alert
    # cycle2 fix: pane_current_command の case 文で node|codex を codex 確定にする
    export TMUX_STUB_PANE_CMD="node"

    # pstree も "other" (= 誤検知側) を返す stub に置換、case 判定が優先することを検証
    cat > "$STUB_BIN/pstree" <<'STUB'
#!/usr/bin/env bash
echo "bash(99999)---node(99998)"
STUB
    chmod +x "$STUB_BIN/pstree"

    run bash "$SCRIPT" --quiet
    # node は codex の child process ゆえ codex 扱い、persona alert 発火せず
    ! grep -q "ERR-PERSONA-CLI-001" "$HEALTH_CHECK_LOG"
    grep -q '"event":"persona_cli_detected"' "$HEALTH_CHECK_STRUCT_LOG"
    grep -q '"cli":"codex"' "$HEALTH_CHECK_STRUCT_LOG"
    # TEST_MODE=1 ゆえ inbox_write は呼ばれない (本 case では alert 自体ないが二重保証)
    [ ! -s "$TEST_INBOX_WRITE_LOG" ]
}

# ─── H-010: cycle2 fix — TEST_MODE=1 で inbox_write 漏出抑制 ─────────────
@test "H-010: TEST_MODE=1 で send_shogun_inbox_alert が真の inbox_write を抑制 (cycle2 fix)" {
    # H-005 同型条件で persona alert を発火させ、TEST_MODE による suppress を検証。
    # 真の inbox_write.sh が呼ばれず、TEST_INBOX_WRITE_LOG に呼出記録のみ残ることを確認。
    cat > "$STUB_BIN/pstree" <<'STUB'
#!/usr/bin/env bash
echo "bash(99999)---claude(99997)"
STUB
    chmod +x "$STUB_BIN/pstree"

    # setup() で TEST_MODE=1 / TEST_INBOX_WRITE_LOG=空ファイル 設定済
    run bash "$SCRIPT" --quiet
    [ "$status" -eq 1 ]
    grep -q "ERR-PERSONA-CLI-001" "$HEALTH_CHECK_LOG"
    # send_shogun_inbox_alert が呼ばれ、TEST_MODE gate で suppress された記録があること
    grep -q "shogun" "$TEST_INBOX_WRITE_LOG"
    grep -q "ERR-PERSONA-CLI-001" "$TEST_INBOX_WRITE_LOG"
    # 真の signal: queue/inbox/shogun.yaml は touch されない (= 漏出ゼロ)
    # (本 fixture は HOME 隔離済ゆえ間接的検証のみ可能、TEST_INBOX_WRITE_LOG に
    #  記録ありかつ実 inbox_write.sh が呼ばれていないことが gate の核心保証)
}
