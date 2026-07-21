#!/usr/bin/env bats
# test_inbox_write_hermes2_guard.bats
#
# hermes2 (環境部長) 宛 dead-drop producer guard — TDD テスト
# 起点: 副委員長 work order hermes2-dead-drop-route-guard-work-order-20260721.md
#
# 目的: TARGET=="hermes2" の inbox_write.sh 呼び出しが、legacy
# queue/inbox/hermes2.yaml (consumer 不在 = 無期限 dead-drop) へ絶対に
# 書かず、正規 pc_handshake へ同期 INSERT するか、失敗時は fail-closed
# (legacy へフォールバックしない) することを保証する。
#
# 相談役 (hermes / hermes-main) は完全一致でないため対象外 — 誤変換
# negative test (T-105/T-106) で担保する。
#
# curl は stub に差し替え、実ネットワーク呼出は一切発生しない。

setup_file() {
    export PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export INBOX_WRITE_SCRIPT="$PROJECT_ROOT/scripts/inbox_write.sh"
    export VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"
    [ -f "$INBOX_WRITE_SCRIPT" ] || return 1
    "$VENV_PYTHON" -c "import yaml" 2>/dev/null || return 1
}

setup() {
    export TEST_TMPDIR="$(mktemp -d "$BATS_TMPDIR/inbox_write_h2_test.XXXXXX")"
    export TEST_INBOX_DIR="$TEST_TMPDIR/queue/inbox"
    mkdir -p "$TEST_INBOX_DIR"

    export TEST_SCRIPT_DIR="$TEST_TMPDIR/scripts"
    mkdir -p "$TEST_SCRIPT_DIR"
    mkdir -p "$TEST_TMPDIR/shim/hakudokai/lib"
    cp "$PROJECT_ROOT/shim/hakudokai/lib/sb_auth.sh" "$TEST_TMPDIR/shim/hakudokai/lib/sb_auth.sh"
    sed "s|SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")/..*|SCRIPT_DIR=\"$TEST_TMPDIR\"|" \
        "$PROJECT_ROOT/scripts/inbox_write.sh" > "$TEST_SCRIPT_DIR/inbox_write.sh"
    chmod +x "$TEST_SCRIPT_DIR/inbox_write.sh"
    ln -sf "$PROJECT_ROOT/.venv" "$TEST_TMPDIR/.venv"
    export TEST_INBOX_WRITE="$TEST_SCRIPT_DIR/inbox_write.sh"

    # Isolated pc_mapping config: single is_local PC "third_pc" (mirrors real
    # config/settings.yaml third_pc entry shape, minimized for the test).
    mkdir -p "$TEST_TMPDIR/config"
    cat > "$TEST_TMPDIR/config/settings.yaml" <<'YAML'
pc_mapping:
  third_pc:
    agents: [ashigaru-third-5, karo-third]
    is_local: true
    pc_id: third_pc
  second_pc:
    agents: [ashigaru5]
    supabase_bridge: true
    pc_id: second_pc
YAML

    # Isolate from the real operator's $HOME/.hakudokai/env and any real
    # ~/.openclaw/disable_cross_pc_bridge flag — tests must never read
    # production Supabase credentials or be affected by host-level flags.
    export FAKE_HOME="$TEST_TMPDIR/fakehome"
    mkdir -p "$FAKE_HOME"
    export HOME="$FAKE_HOME"

    # Deterministic fake Supabase credentials (never used for a real call —
    # curl is stubbed below).
    export SUPABASE_URL="https://stub.example.invalid"
    export SUPABASE_SERVICE_ROLE_KEY="stub-key-not-real"

    # curl stub: records call count + last payload, and answers according to
    # $CURL_STUB_MODE (success | fail_http | fail_curl). Never touches the
    # network.
    export CURL_STUB_BIN="$TEST_TMPDIR/bin"
    mkdir -p "$CURL_STUB_BIN"
    export CURL_STUB_CALLS="$TEST_TMPDIR/curl_calls.count"
    export CURL_STUB_PAYLOAD="$TEST_TMPDIR/curl_last_payload.json"
    : > "$CURL_STUB_CALLS"
    cat > "$CURL_STUB_BIN/curl" <<'STUB'
#!/usr/bin/env bash
echo -n "x" >> "$CURL_STUB_CALLS"

out_file=""
args=("$@")
i=0
while [ $i -lt ${#args[@]} ]; do
    case "${args[$i]}" in
        -o)
            i=$((i + 1))
            out_file="${args[$i]}"
            ;;
        --data-binary)
            i=$((i + 1))
            printf '%s' "${args[$i]}" > "$CURL_STUB_PAYLOAD"
            ;;
    esac
    i=$((i + 1))
done

mode="${CURL_STUB_MODE:-success}"
case "$mode" in
    success)
        [ -n "$out_file" ] && printf '' > "$out_file"
        printf '201'
        exit 0
        ;;
    fail_http)
        [ -n "$out_file" ] && printf '{"message":"stub rejected"}' > "$out_file"
        printf '400'
        exit 0
        ;;
    fail_curl)
        [ -n "$out_file" ] && printf '' > "$out_file"
        printf '000'
        exit 7
        ;;
esac
STUB
    chmod +x "$CURL_STUB_BIN/curl"
    export PATH="$CURL_STUB_BIN:$PATH"
    export CURL_STUB_MODE="success"
}

teardown() {
    [ -n "$TEST_TMPDIR" ] && [ -d "$TEST_TMPDIR" ] && rm -rf "$TEST_TMPDIR"
}

# =============================================================================
# T-101: canonical route success → legacy hermes2.yaml never created, exit 0
# =============================================================================

@test "T-101: target=hermes2 canonical INSERT succeeds → no legacy dead-drop file, exit 0" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "hermes2" "テストメッセージ" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ ! -f "$TEST_INBOX_DIR/hermes2.yaml" ]
    [[ "$output" == *"canonical pc_handshake"* ]]
}

# =============================================================================
# T-102: canonical route rejected by server (HTTP 400) → fail-closed
# =============================================================================

@test "T-102: target=hermes2 canonical INSERT HTTP failure → fail-closed, no legacy write, exit 1" {
    export CURL_STUB_MODE="fail_http"
    run bash "$TEST_INBOX_WRITE" "hermes2" "テストメッセージ" "status_update" "ashigaru-third-5"
    [ "$status" -eq 1 ]
    [ ! -f "$TEST_INBOX_DIR/hermes2.yaml" ]
    [[ "$output" == *"FAIL-CLOSED"* ]]
}

# =============================================================================
# T-102b: canonical route unreachable (curl transport failure) → fail-closed
# =============================================================================

@test "T-102b: target=hermes2 curl transport failure → fail-closed, no legacy write, exit 1" {
    export CURL_STUB_MODE="fail_curl"
    run bash "$TEST_INBOX_WRITE" "hermes2" "テストメッセージ" "status_update" "ashigaru-third-5"
    [ "$status" -eq 1 ]
    [ ! -f "$TEST_INBOX_DIR/hermes2.yaml" ]
    [[ "$output" == *"FAIL-CLOSED"* ]]
}

# =============================================================================
# T-103: no Supabase credentials available → fail-closed (never silently
# falls back to the legacy dead-drop file)
# =============================================================================

@test "T-103: target=hermes2 no Supabase env → fail-closed, no legacy write, exit 1" {
    unset SUPABASE_URL
    unset SUPABASE_SERVICE_ROLE_KEY
    run bash "$TEST_INBOX_WRITE" "hermes2" "テストメッセージ" "status_update" "ashigaru-third-5"
    [ "$status" -eq 1 ]
    [ ! -f "$TEST_INBOX_DIR/hermes2.yaml" ]
    [[ "$output" == *"FAIL-CLOSED"* ]]
    # curl must never have been invoked without credentials
    [ ! -s "$CURL_STUB_CALLS" ]
}

# =============================================================================
# T-104: disable_cross_pc_bridge flag present → fail-closed, curl never called
# =============================================================================

@test "T-104: target=hermes2 disable_cross_pc_bridge flag set → fail-closed, no legacy write, curl not called" {
    mkdir -p "$HOME/.openclaw"
    : > "$HOME/.openclaw/disable_cross_pc_bridge"
    run bash "$TEST_INBOX_WRITE" "hermes2" "テストメッセージ" "status_update" "ashigaru-third-5"
    [ "$status" -eq 1 ]
    [ ! -f "$TEST_INBOX_DIR/hermes2.yaml" ]
    [[ "$output" == *"FAIL-CLOSED"* ]]
    [ ! -s "$CURL_STUB_CALLS" ]
}

# =============================================================================
# T-105 / T-106: negative tests — 相談役 (hermes / hermes-main) は完全一致
# でないため guard の対象外。誤って canonical route へ吸われたり、legacy
# write がブロックされたりしてはならない (役職混同防止の中核テスト)。
# =============================================================================

@test "T-105: target=hermes (相談役, NOT hermes2) → guard does not trigger, normal legacy write occurs" {
    export CURL_STUB_MODE="fail_http"
    run bash "$TEST_INBOX_WRITE" "hermes" "相談役宛メッセージ" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ -f "$TEST_INBOX_DIR/hermes.yaml" ]
    [[ "$output" != *"FAIL-CLOSED"* ]]
    # canonical INSERT path (curl) must not even be reached synchronously by
    # the guard for this target — background _cross_pc_bridge may or may not
    # fire depending on pc_mapping, but the foreground exit/legacy-write must
    # not be affected by CURL_STUB_MODE=fail_http.
}

@test "T-106: target=hermes-main (相談役, NOT hermes2) → guard does not trigger, normal legacy write occurs" {
    export CURL_STUB_MODE="fail_http"
    run bash "$TEST_INBOX_WRITE" "hermes-main" "相談役宛メッセージ" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ -f "$TEST_INBOX_DIR/hermes-main.yaml" ]
    [[ "$output" != *"FAIL-CLOSED"* ]]
}

# =============================================================================
# T-107: dedupe / no double-insert — a single inbox_write.sh call for
# target=hermes2 must synchronously INSERT exactly once (not once from the
# guard AND once again from the generic background _cross_pc_bridge).
# =============================================================================

@test "T-107: target=hermes2 single call → canonical pc_handshake INSERT happens exactly once" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "hermes2" "重複防止テスト" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    # background jobs from this bats `run` subshell have exited by the time
    # `run` returns (bash waits for the script's own foreground execution;
    # any stray backgrounded _cross_pc_bridge for a *different* code path
    # would not apply here since the guard short-circuits before it).
    sleep 0.3
    calls=$(wc -c < "$CURL_STUB_CALLS")
    [ "$calls" -eq 1 ]
}

# =============================================================================
# T-108: payload correctness — to_pc=hermes2, message_type normalized to the
# pc_handshake CHECK allowlist, content carries the original text.
# =============================================================================

@test "T-108: target=hermes2 payload → to_pc=hermes2, allowlisted message_type, content preserved" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "hermes2" "ペイロード検証テスト" "custom_nonstandard_type" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ -f "$CURL_STUB_PAYLOAD" ]

    "$VENV_PYTHON" <<EOF
import json
with open('$CURL_STUB_PAYLOAD') as f:
    payload = json.load(f)

assert payload['to_pc'] == 'hermes2', payload
allowed = {"request_permission","grant_permission","decline_permission","status_update",
           "urgent_stop","question","answer","ack","file_sync"}
assert payload['message_type'] in allowed, payload['message_type']
assert 'ペイロード検証テスト' in payload['content'], payload['content']
assert 'hermes2' in payload['content'], payload['content']
print('T-108: PASS')
EOF
}

# =============================================================================
# T-109: unrelated target unaffected by the guard's presence (regression
# sanity check — normal legacy write path for a non-hermes2 target still
# behaves exactly as before).
# =============================================================================

@test "T-109: target=some_other_agent (unrelated) → normal legacy write, unaffected by hermes2 guard code" {
    export CURL_STUB_MODE="fail_curl"
    run bash "$TEST_INBOX_WRITE" "some_other_agent" "無関係メッセージ" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ -f "$TEST_INBOX_DIR/some_other_agent.yaml" ]
    [[ "$output" != *"FAIL-CLOSED"* ]]
}

# =============================================================================
# T-110..T-115: alias/表示名 正規化 (G1 REDO cycle2 finding
# H2-G1-ROLE-ALIAS-GUARD-MISSING-001) — 各 canonical alias について、
# canonical pc_handshake INSERT が exactly 1 回発生し、legacy dead-drop
# file (queue/inbox/<alias>.yaml) は 0 回 (=絶対に作られない) であることを
# 保証する。正本 = shim/hakudokai/hakudokai_fukuincho_reverse_poll.py の
# _format_codex_sender() (hermes2 → 環境部長 マッピング)。
# =============================================================================

@test "T-110: target=環境部長 (表示名) → canonical INSERT succeeds, no legacy dead-drop file under that name" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "環境部長" "表示名テスト" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ ! -f "$TEST_INBOX_DIR/環境部長.yaml" ]
    [[ "$output" == *"canonical pc_handshake"* ]]
    sleep 0.3
    calls=$(wc -c < "$CURL_STUB_CALLS")
    [ "$calls" -eq 1 ]
}

@test "T-111: target=hermes-2 (ASCII hyphen variant) → canonical INSERT succeeds, no legacy file" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "hermes-2" "hyphen変種テスト" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ ! -f "$TEST_INBOX_DIR/hermes-2.yaml" ]
    [[ "$output" == *"canonical pc_handshake"* ]]
    sleep 0.3
    calls=$(wc -c < "$CURL_STUB_CALLS")
    [ "$calls" -eq 1 ]
}

@test "T-112: target=hermes_2 (ASCII underscore variant) → canonical INSERT succeeds, no legacy file" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "hermes_2" "underscore変種テスト" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ ! -f "$TEST_INBOX_DIR/hermes_2.yaml" ]
    [[ "$output" == *"canonical pc_handshake"* ]]
    sleep 0.3
    calls=$(wc -c < "$CURL_STUB_CALLS")
    [ "$calls" -eq 1 ]
}

@test "T-113: target=HERMES2 (大文字変種) → canonical INSERT succeeds, no legacy file" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "HERMES2" "大文字変種テスト" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ ! -f "$TEST_INBOX_DIR/HERMES2.yaml" ]
    [[ "$output" == *"canonical pc_handshake"* ]]
    sleep 0.3
    calls=$(wc -c < "$CURL_STUB_CALLS")
    [ "$calls" -eq 1 ]
}

@test "T-114: target='hermes 2' (space区切り変種) → canonical INSERT succeeds, no legacy file" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "hermes 2" "space変種テスト" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ ! -f "$TEST_INBOX_DIR/hermes 2.yaml" ]
    [[ "$output" == *"canonical pc_handshake"* ]]
    sleep 0.3
    calls=$(wc -c < "$CURL_STUB_CALLS")
    [ "$calls" -eq 1 ]
}

@test "T-115: alias route payload → to_pc always normalized to hermes2 regardless of which alias triggered it" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "環境部長" "ペイロード正規化テスト" "status_update" "ashigaru-third-5"
    [ "$status" -eq 0 ]
    [ -f "$CURL_STUB_PAYLOAD" ]

    "$VENV_PYTHON" <<EOF
import json
with open('$CURL_STUB_PAYLOAD') as f:
    payload = json.load(f)
assert payload['to_pc'] == 'hermes2', payload
assert payload['topic'] == 'hermes2_deaddrop_guard_hermes2', payload['topic']
print('T-115: PASS')
EOF
}

# =============================================================================
# T-116..T-118: near-miss unknown 名 — hermes2/環境部長 に類似するが完全
#一致ではない名前は fail-closed (legacy へ絶対に進まない、curl も呼ばれ
# ない) であることを保証する (誤って新たな legacy alias file が生成され
# る事故の防止、work order item 4)。
# =============================================================================

@test "T-116: target=hermes22 (near-miss, NOT a recognized canonical alias) → fail-closed, no legacy file, curl not called" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "hermes22" "near-missテスト" "status_update" "ashigaru-third-5"
    [ "$status" -eq 1 ]
    [ ! -f "$TEST_INBOX_DIR/hermes22.yaml" ]
    [[ "$output" == *"FAIL-CLOSED"* ]]
    [ ! -s "$CURL_STUB_CALLS" ]
}

@test "T-117: target=hermes-office2 (near-miss, NOT a recognized canonical alias) → fail-closed, no legacy file" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "hermes-office2" "near-missテスト2" "status_update" "ashigaru-third-5"
    [ "$status" -eq 1 ]
    [ ! -f "$TEST_INBOX_DIR/hermes-office2.yaml" ]
    [[ "$output" == *"FAIL-CLOSED"* ]]
    [ ! -s "$CURL_STUB_CALLS" ]
}

@test "T-118: target=環境部長様 (near-miss partial match of 表示名) → fail-closed, no legacy file" {
    export CURL_STUB_MODE="success"
    run bash "$TEST_INBOX_WRITE" "環境部長様" "near-missテスト3" "status_update" "ashigaru-third-5"
    [ "$status" -eq 1 ]
    [ ! -f "$TEST_INBOX_DIR/環境部長様.yaml" ]
    [[ "$output" == *"FAIL-CLOSED"* ]]
    [ ! -s "$CURL_STUB_CALLS" ]
}

# =============================================================================
# T-119: sb_curl source/definition contract (Hermes authoritative audit
# hermes_authoritative_audit_seq132056_93727abe, missing_guard item 2:
# "Static/runtime assertion that sb_curl is defined after top-level
# initialization"). This is a direct regression guard for
# HERMES-AUTH-93727ABE-S1-HELPER-NOT-SOURCED-001: 93727abe added sb_curl
# call sites and shim/hakudokai/lib/sb_auth.sh, but the committed blob of
# scripts/inbox_write.sh never sourced it, so every canonical route failed
# closed with curl_status=127. T-101/T-107 alone cannot catch this specific
# defect class because they execute a per-test *copy* of the script
# (regenerated fresh in setup() from $INBOX_WRITE_SCRIPT every run), which
# would silently inherit a missing source line too, plus they only ever
# observe curl-stub behavior, not the source→definition contract itself.
#
# Method: mechanically extract (grep/sed against the real committed file —
# no hand copy, no drift) the "SB_AUTH_LIB=...; source "$SB_AUTH_LIB"" block
# from $INBOX_WRITE_SCRIPT's own top-level init, source only that block in
# isolation (with SCRIPT_DIR corrected for the fact that `source` gives the
# sourced file's own BASH_SOURCE[0], not the real script's), and assert
# sb_curl becomes a callable function strictly before the first sb_curl
# call site's line number in the real file.
# =============================================================================

@test "T-119: scripts/inbox_write.sh sources sb_auth.sh and defines sb_curl before first call site (missing_guard: source/definition contract)" {
    local scriptdir_line source_line first_call_line tail_start

    scriptdir_line=$(grep -n '^SCRIPT_DIR=' "$INBOX_WRITE_SCRIPT" | head -1 | cut -d: -f1)
    [ -n "$scriptdir_line" ]

    source_line=$(grep -n '^source "\$SB_AUTH_LIB"' "$INBOX_WRITE_SCRIPT" | head -1 | cut -d: -f1)
    [ -n "$source_line" ]

    first_call_line=$(grep -n 'sb_curl' "$INBOX_WRITE_SCRIPT" | head -1 | cut -d: -f1)
    [ -n "$first_call_line" ]
    [ "$source_line" -lt "$first_call_line" ]

    tail_start=$((scriptdir_line + 1))
    {
        echo 'set -e'
        echo "SCRIPT_DIR=\"$PROJECT_ROOT\""
        sed -n "${tail_start},${source_line}p" "$INBOX_WRITE_SCRIPT"
    } > "$TEST_TMPDIR/t119_head_init.sh"

    run bash -c "source '$TEST_TMPDIR/t119_head_init.sh' && type -t sb_curl"
    [ "$status" -eq 0 ]
    [ "$output" = "function" ]
}

# =============================================================================
# TC1: Codex cycle1 B1 detection tests — set -e 単独代入ハザードの分離立証
#
# 背景: T-101/T-102/T-102b は _hermes2_deaddrop_guard を常に
# `if _hermes2_deaddrop_guard ...; then` という★testedコンテキスト★経由で
# しか呼ばない (実運用の唯一の呼出し箇所と同じ形)。bash の仕様上、compound
# command/function が if の条件式として評価される時、その呼出し全体の間
# -e は無視される。そのため B1 (修正前の bare `http_status=$(cmd)` パター
# ン) は★現行の唯一の呼出し経路では実際には中断を起こさない★ことが実証
# 済み (T-102b は fix 前後で挙動不変)。既存テストのみでは B1 を検出でき
# ない — TC1 はこの検出できない穴を、内部パターンを bare (if/&&/||/! の
# いずれにも包まれない) コンテキストへ単離して直接埋める。
#
# TC1a: 現在のソース (scripts/inbox_write.sh) から該当ブロックを★sed/awk
#       で機械抽出★し (手書き複製によるドリフト防止)、bare コンテキスト
#       で実行 → curl transport failure でも中断せず到達点まで進むことを
#       確認する (regression guard: 将来 if ラップが誤って剥がされたら
#       このテストは fail する)。
# TC1b: 修正前 diff で削除された行と同一パターンを再現し、同条件で実行
#       → bare コンテキストでは set -e により到達点手前で中断すること
#       を実証する (「pre-fix code に対して FAIL する」という karo-third
#       指示の具体的充足、履歴的ハザードの直接立証)。
# =============================================================================

@test "TC1a: extracted current http_status capture block survives curl transport failure in a bare (non-if) set -e context" {
    local extracted
    extracted=$(awk '/local resp_file http_status curl_status/{p=1} p{print} p && /^    fi$/{exit}' "$INBOX_WRITE_SCRIPT")
    [ -n "$extracted" ]
    # 抽出ブロックが if でラップされていること自体も確認 (抽出失敗 = 別行を
    # 拾ってしまった、等のテスト自身のフォールスポジティブを防止)。
    [[ "$extracted" == *"if http_status=\$(SUPABASE_SERVICE_ROLE_KEY="* ]]

    local harness="$TEST_TMPDIR/tc1a_harness.sh"
    {
        echo '#!/usr/bin/env bash'
        echo 'set -e'
        echo "source \"$PROJECT_ROOT/shim/hakudokai/lib/sb_auth.sh\""
        echo 'sb_key="stub-key-not-real"'
        echo 'sb_url="https://stub.example.invalid"'
        echo 'payload="{\"stub\":true}"'
        echo '_isolated_capture_postfix() {'
        printf '%s\n' "$extracted"
        echo '    echo "REACHED_AFTER_CAPTURE curl_status=[$curl_status] http_status=[$http_status]"'
        echo '}'
        echo '_isolated_capture_postfix'
        echo 'echo "OUTER_SCRIPT_COMPLETED"'
    } > "$harness"

    export CURL_STUB_MODE="fail_curl"
    run bash "$harness"
    [[ "$output" == *"REACHED_AFTER_CAPTURE"* ]]
    [[ "$output" == *"curl_status=[7]"* ]]
    [[ "$output" == *"http_status=[]"* ]]
    [[ "$output" == *"OUTER_SCRIPT_COMPLETED"* ]]
}

@test "TC1b: pre-fix bare capture pattern (Codex cycle1 B1, historical) aborts before reaching handler in bare set -e context" {
    local harness="$TEST_TMPDIR/tc1b_harness.sh"
    {
        echo '#!/usr/bin/env bash'
        echo 'set -e'
        echo "source \"$PROJECT_ROOT/shim/hakudokai/lib/sb_auth.sh\""
        echo 'sb_key="stub-key-not-real"'
        echo 'sb_url="https://stub.example.invalid"'
        echo 'payload="{\"stub\":true}"'
        echo '_isolated_capture_prefix() {'
        echo '    local resp_file http_status curl_status'
        echo '    resp_file=$(mktemp)'
        echo '    http_status=$(SUPABASE_SERVICE_ROLE_KEY="$sb_key" sb_curl -sS -o "$resp_file" -w '"'"'%{http_code}'"'"' -X POST \'
        echo '        "${sb_url}/rest/v1/pc_handshake" \'
        echo '        -H "Content-Type: application/json" \'
        echo '        -H "Prefer: return=minimal" \'
        echo '        --data-binary "$payload" \'
        echo '        2>/dev/null)'
        echo '    curl_status=$?'
        echo '    echo "REACHED_AFTER_CAPTURE curl_status=[$curl_status] http_status=[$http_status]"'
        echo '}'
        echo '_isolated_capture_prefix'
        echo 'echo "OUTER_SCRIPT_COMPLETED"'
    } > "$harness"

    export CURL_STUB_MODE="fail_curl"
    run bash "$harness"
    [ "$status" -ne 0 ]
    [[ "$output" != *"REACHED_AFTER_CAPTURE"* ]]
    [[ "$output" != *"OUTER_SCRIPT_COMPLETED"* ]]
}

# =============================================================================
# T-120/T-121: anti-duplication fix verification —
# HERMES-AUTH-93727ABE-S1-HELPER-NOT-SOURCED-001 followup、軍師 Option B 設計
# 回答 (msg_20260721_140010_d713651b) 採用分の検証。
#
# 軍師指示: "_resolve_local_pc() を単一責務の共有 helper として新設し、
# _cross_pc_bridge/_hermes2_deaddrop_guard 双方を置換。直接相互呼出しは禁止。
# ... positive-path で両 caller が同 helper 結果を実際に使用したことを
# assert し、設定欠落/不正mappingは現行 fail-closed 契約を維持。"
#
# T-120 (structural, T-119 の grep 手法を踏襲): 重複していた local_pc lookup
# fingerprint がファイル中に厳密に1箇所のみ存在すること、両 caller の関数
# body が実際に _resolve_local_pc を呼んでいること、両者が直接相互呼出しを
# していないことを静的に検証する。
#
# T-121 (dynamic/positive-path): 単なる「出力値が一致する」assertion では
# 「たまたま独立実装が同じ値を計算しているだけ」を排除できない (二重実装が
# 残っていても設定が同一なら値は一致し得る)。そこで _resolve_local_pc を
# sentinel 値で override した上で両 caller を実際に呼び出し、override した
# 値がそのまま両者の payload (from_pc フィールド) に伝播することを確認する。
# もし両 caller のどちらかが独自に local_pc を再計算していれば、override は
# その caller の出力に影響せず、本テストは fail する。
# =============================================================================

@test "T-120: _resolve_local_pc is the sole local_pc lookup implementation; both callers invoke it; no direct mutual calls (anti-dup structural check, HERMES-AUTH-93727ABE-S1-HELPER-NOT-SOURCED-001 followup, gunshi Option B msg_20260721_140010_d713651b)" {
    local def_count fingerprint_count
    local rlp_start cb_start hg_start cb_end hg_end

    def_count=$(grep -c '^_resolve_local_pc() {' "$INBOX_WRITE_SCRIPT")
    [ "$def_count" -eq 1 ]

    fingerprint_count=$(grep -c "local_id = pc_cfg.get('pc_id', pc_name)" "$INBOX_WRITE_SCRIPT")
    [ "$fingerprint_count" -eq 1 ]

    rlp_start=$(grep -n '^_resolve_local_pc() {' "$INBOX_WRITE_SCRIPT" | head -1 | cut -d: -f1)
    cb_start=$(grep -n '^_cross_pc_bridge() {' "$INBOX_WRITE_SCRIPT" | head -1 | cut -d: -f1)
    hg_start=$(grep -n '^_hermes2_deaddrop_guard() {' "$INBOX_WRITE_SCRIPT" | head -1 | cut -d: -f1)
    [ -n "$rlp_start" ]
    [ -n "$cb_start" ]
    [ -n "$hg_start" ]
    [ "$rlp_start" -lt "$cb_start" ]
    [ "$cb_start" -lt "$hg_start" ]

    cb_end=$(tail -n "+$((cb_start + 1))" "$INBOX_WRITE_SCRIPT" | grep -n '^}$' | head -1 | cut -d: -f1)
    cb_end=$((cb_start + cb_end))
    hg_end=$(tail -n "+$((hg_start + 1))" "$INBOX_WRITE_SCRIPT" | grep -n '^}$' | head -1 | cut -d: -f1)
    hg_end=$((hg_start + hg_end))

    local cb_body hg_body
    cb_body=$(sed -n "${cb_start},${cb_end}p" "$INBOX_WRITE_SCRIPT")
    hg_body=$(sed -n "${hg_start},${hg_end}p" "$INBOX_WRITE_SCRIPT")

    [[ "$cb_body" == *"_resolve_local_pc"* ]]
    [[ "$hg_body" == *"_resolve_local_pc"* ]]

    # 直接相互呼出し禁止 (軍師指示の明示条件) — コメント中の言及 (説明目的)
    # は許容し、実際の呼出し文 (行頭で関数名を command として呼ぶ形) のみ
    # を検査する。
    run bash -c "grep -E '^[[:space:]]*_hermes2_deaddrop_guard\b' <<< \"\$1\"" _ "$cb_body"
    [ "$status" -ne 0 ]
    run bash -c "grep -E '^[[:space:]]*_cross_pc_bridge\b' <<< \"\$1\"" _ "$hg_body"
    [ "$status" -ne 0 ]
}

@test "T-121: overriding _resolve_local_pc propagates identically into both _cross_pc_bridge and _hermes2_deaddrop_guard payloads (positive-path proof of shared helper usage)" {
    local rlp_start rlp_end cb_start cb_end hg_start hg_end

    rlp_start=$(grep -n '^_resolve_local_pc() {' "$INBOX_WRITE_SCRIPT" | head -1 | cut -d: -f1)
    rlp_end=$(tail -n "+$((rlp_start + 1))" "$INBOX_WRITE_SCRIPT" | grep -n '^}$' | head -1 | cut -d: -f1)
    rlp_end=$((rlp_start + rlp_end))

    cb_start=$(grep -n '^_cross_pc_bridge() {' "$INBOX_WRITE_SCRIPT" | head -1 | cut -d: -f1)
    cb_end=$(tail -n "+$((cb_start + 1))" "$INBOX_WRITE_SCRIPT" | grep -n '^}$' | head -1 | cut -d: -f1)
    cb_end=$((cb_start + cb_end))

    hg_start=$(grep -n '^_hermes2_deaddrop_guard() {' "$INBOX_WRITE_SCRIPT" | head -1 | cut -d: -f1)
    hg_end=$(tail -n "+$((hg_start + 1))" "$INBOX_WRITE_SCRIPT" | grep -n '^}$' | head -1 | cut -d: -f1)
    hg_end=$((hg_start + hg_end))

    {
        sed -n "${rlp_start},${rlp_end}p" "$INBOX_WRITE_SCRIPT"
        sed -n "${cb_start},${cb_end}p" "$INBOX_WRITE_SCRIPT"
        sed -n "${hg_start},${hg_end}p" "$INBOX_WRITE_SCRIPT"
    } > "$TEST_TMPDIR/t121_funcs.sh"

    run bash -c "
        set -e
        SCRIPT_DIR='$TEST_TMPDIR'
        HOME='$FAKE_HOME'
        source '$TEST_TMPDIR/shim/hakudokai/lib/sb_auth.sh'
        source '$TEST_TMPDIR/t121_funcs.sh'
        _resolve_local_pc() { echo 'SENTINEL_PC_9f3e'; }
        _cross_pc_bridge 'ashigaru5' 'T-121 positive path (cross_pc_bridge)' 'status_update' 'ashigaru-third-5'
        cp '$CURL_STUB_PAYLOAD' '$TEST_TMPDIR/t121_cb_payload.json'
        : > '$CURL_STUB_PAYLOAD'
        _hermes2_deaddrop_guard 'T-121 positive path (hermes2_deaddrop_guard)' 'status_update' 'ashigaru-third-5' || true
        cp '$CURL_STUB_PAYLOAD' '$TEST_TMPDIR/t121_hg_payload.json'
    "
    [ "$status" -eq 0 ]
    [ -s "$TEST_TMPDIR/t121_cb_payload.json" ]
    [ -s "$TEST_TMPDIR/t121_hg_payload.json" ]

    run "$VENV_PYTHON" -c "
import json
with open('$TEST_TMPDIR/t121_cb_payload.json') as f:
    cb = json.load(f)
with open('$TEST_TMPDIR/t121_hg_payload.json') as f:
    hg = json.load(f)
assert cb['from_pc'] == 'SENTINEL_PC_9f3e', f'cross_pc_bridge from_pc={cb.get(\"from_pc\")!r}'
assert hg['from_pc'] == 'SENTINEL_PC_9f3e', f'hermes2_deaddrop_guard from_pc={hg.get(\"from_pc\")!r}'
print('T-121: PASS (both callers propagate the overridden _resolve_local_pc sentinel)')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"T-121: PASS"* ]]
}
