#!/usr/bin/env bats
# test_karo_second_send_iincho.bats — karo_second_send_iincho.sh ユニットテスト
#
# 実行主体: `make test` (bats tests/*.bats) および .github/workflows/test.yml
# (push to main/feature/**・PR毎に自動実行、ROOT_TESTS=$(ls tests/*.bats ...) が本fileを含む)。
# 新規常駐processは追加しない — 既存 test 経路にそのまま乗る設計。
#
# T-201: 正常dry-run → 封筒4点固定値が出力に含まれる
# T-202: 誤 target-agent/topic を渡しても正規化され、固定値のみが実封筒へ反映される(拒否)
# T-203: priority は常に high(渡す手段自体が存在しない=固定を再確認)
# T-204: content未指定 → exit 1 Usage
# T-205: sb_auth.sh 不在時 hard fail(exit 1・stderr+永続log双方に届く・2>/dev/null等で握り潰さない)
# T-206: dry-run出力にsecret値(SUPABASE_SERVICE_ROLE_KEY)が含まれない
# T-207: --live失敗時、curlの実stderrがfatalメッセージ/ログへ届く(2>/dev/nullで捨てない)
# T-208: --liveは$HOME/.hakudokai/envへfallbackしない(process env限定)
# T-209: --live成功時、pc_handshakeの行idがstdoutへ届く(return=representation、旧return=minimalの是正)
# T-210: requires_responseは既定false・--requires-response指定でtrue

setup_file() {
    export PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export HELPER_SCRIPT="$PROJECT_ROOT/scripts/karo_second_send_iincho.sh"
    [ -f "$HELPER_SCRIPT" ] || return 1
}

setup() {
    export TEST_TMPDIR="$(mktemp -d "$BATS_TMPDIR/karo_second_send_iincho_test.XXXXXX")"
    export TEST_FAIL_LOG="$TEST_TMPDIR/faillog.log"
}

teardown() {
    [ -n "$TEST_TMPDIR" ] && [ -d "$TEST_TMPDIR" ] && rm -rf "$TEST_TMPDIR"
}

# =============================================================================
# T-201: 正常dry-run → 封筒4点固定値が出力に含まれる
# =============================================================================

@test "T-201: normal dry-run → fixed envelope 4 points present in output" {
    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" bash "$HELPER_SCRIPT" -- "T-201 content"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "DRY-RUN" ]]
    [[ "$output" =~ '"from_pc": "second_pc"' ]]
    [[ "$output" =~ '"to_pc": "iincho"' ]]
    [[ "$output" =~ '"topic": "cross_pc_inbox_iincho"' ]]
    [[ "$output" =~ '"target_agent": "iincho"' ]]
    [[ "$output" =~ '"sender_agent": "karo-second"' ]]
    [[ "$output" =~ '"priority": "high"' ]]
}

# =============================================================================
# T-202: 誤 target-agent/topic 拒否 — 呼出側の指定は反映されず、正規化通知+固定値のみ出力される
# =============================================================================

@test "T-202: wrong --target-agent/--topic rejected → normalized to canonical, NORMALIZED note shown" {
    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" bash "$HELPER_SCRIPT" \
        --target-agent shogun --topic cross_pc_inbox_wrong -- "T-202 content"
    [ "$status" -eq 0 ]

    # 正規化されたことが呼出側(標準出力)に明示される
    [[ "$output" =~ "NORMALIZED" ]]
    [[ "$output" =~ "target_agent" ]]
    [[ "$output" =~ "shogun" ]]

    # 誤った値が実封筒へ反映されていないこと(拒否の実体確認)
    [[ ! "$output" =~ '"target_agent": "shogun"' ]]
    [[ ! "$output" =~ '"topic": "cross_pc_inbox_wrong"' ]]

    # 固定値のみが実封筒へ用いられていること
    [[ "$output" =~ '"target_agent": "iincho"' ]]
    [[ "$output" =~ '"topic": "cross_pc_inbox_iincho"' ]]
}

# =============================================================================
# T-203: priority は常に high — 上書き手段自体が存在しないことの再確認
# =============================================================================

@test "T-203: priority is always high, never medium (pc-handshake-priority-constraint)" {
    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" bash "$HELPER_SCRIPT" -- "T-203 content"
    [ "$status" -eq 0 ]
    [[ "$output" =~ '"priority": "high"' ]]
    [[ ! "$output" =~ '"priority": "medium"' ]]
}

# =============================================================================
# T-204: content未指定 → exit 1 Usage
# =============================================================================

@test "T-204: missing content → exit 1 with Usage message" {
    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" bash "$HELPER_SCRIPT"
    [ "$status" -eq 1 ]
    [[ "$output" =~ "Usage" ]]
}

# =============================================================================
# T-205: sb_auth.sh 不在時 hard fail
# =============================================================================

@test "T-205: sb_auth.sh missing → hard fail exit 1, FATAL to stderr AND persisted to log" {
    mkdir -p "$TEST_TMPDIR/scripts"
    cp "$HELPER_SCRIPT" "$TEST_TMPDIR/scripts/karo_second_send_iincho.sh"
    # $TEST_TMPDIR/shim/hakudokai/lib/sb_auth.sh は意図的に作らない(不在を再現)

    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" \
        bash "$TEST_TMPDIR/scripts/karo_second_send_iincho.sh" -- "T-205 content"

    [ "$status" -eq 1 ]
    [[ "$output" =~ "FATAL" ]]
    [[ "$output" =~ "sb_auth.sh" ]]

    # 永続ログにも同一FATALが記録されていること(stderrのみで終わらせない=沈黙投棄防止)
    [ -f "$TEST_FAIL_LOG" ]
    grep -q "sb_auth.sh not found/readable" "$TEST_FAIL_LOG"
}

# =============================================================================
# T-206: dry-run出力にsecret値が含まれない
# =============================================================================

@test "T-206: dry-run output never contains the SUPABASE_SERVICE_ROLE_KEY value" {
    # サンプル値を明示的に注入し、出力にその値が漏れていないことを確認する
    # (実キーは使わない — 固定サンプル値で argv/出力への混入経路自体を検証する)
    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" \
        SUPABASE_SERVICE_ROLE_KEY="dummy-secret-value-should-not-leak-9f8e7d" \
        bash "$HELPER_SCRIPT" -- "T-206 content"
    [ "$status" -eq 0 ]
    [[ ! "$output" =~ "dummy-secret-value-should-not-leak-9f8e7d" ]]
}

# =============================================================================
# T-207: --live 失敗時、curl の実stderrがfatalメッセージ/ログへ届く(2>/dev/nullで捨てない)
# =============================================================================

@test "T-207: --live POST failure surfaces curl stderr in FATAL (not swallowed by 2>/dev/null)" {
    # 到達不能な127.0.0.1:1(listenerが無い前提)へ向けることで、DNS待ちなしで
    # 即座に接続拒否させ、curlの実エラー理由がfatal本文へ届くかを検証する。
    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" \
        SUPABASE_URL="http://127.0.0.1:1" \
        SUPABASE_SERVICE_ROLE_KEY="dummy-test-key-not-real" \
        timeout 10 bash "$HELPER_SCRIPT" --live -- "T-207 content"

    [ "$status" -eq 1 ]
    [[ "$output" =~ "FATAL" ]]
    [[ "$output" =~ "LIVE POST failed" ]]
    # curlの実stderr(接続失敗理由)がfatal本文に含まれ、空文字で握り潰されていないこと
    [[ ! "$output" =~ "curl_stderr=<empty>" ]]
    [[ "$output" =~ "curl_stderr=" ]]

    # 永続logにも同一内容が届いていること
    [ -f "$TEST_FAIL_LOG" ]
    grep -q "LIVE POST failed" "$TEST_FAIL_LOG"
}

# =============================================================================
# T-208: $HOME/.hakudokai/env のfallbackを持たない — process env不在なら
#         その file に値があっても拾わずhard failすること(失効鍵の恒久化防止)
# =============================================================================

@test "T-208: --live never falls back to \$HOME/.hakudokai/env (process env only)" {
    mkdir -p "$TEST_TMPDIR/fakehome/.hakudokai"
    cat > "$TEST_TMPDIR/fakehome/.hakudokai/env" <<'EOF'
SUPABASE_URL=https://example-should-not-be-read.invalid
SUPABASE_SERVICE_ROLE_KEY=should-not-be-read-either
EOF

    run env -u SUPABASE_URL -u SUPABASE_SERVICE_ROLE_KEY \
        HOME="$TEST_TMPDIR/fakehome" \
        KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" \
        bash "$HELPER_SCRIPT" --live -- "T-208 content"

    [ "$status" -eq 1 ]
    [[ "$output" =~ "FATAL" ]]
    [[ "$output" =~ "unset in process env" ]]
    # fallback file の値が出力に混入していないこと(拾っていない証拠)
    [[ ! "$output" =~ "example-should-not-be-read.invalid" ]]
}

# =============================================================================
# T-209: --live成功時、pc_handshakeの行idがstdoutへ届く
#        (return=representation。旧return=minimalではidが返らず沈黙成功であった)
# =============================================================================

@test "T-209: --live success surfaces the pc_handshake row id in stdout (return=representation, not minimal)" {
    # ローカルmockサーバ: PostgRESTのreturn=representation相当(201+挿入行JSON配列)を返す。
    MOCK_PORT="$(python3 -c 'import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()')"

    cat > "$TEST_TMPDIR/mock_server.py" <<'PYEOF'
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        self.rfile.read(length)
        body = b'[{"id": "mock-row-id-12345"}]'
        self.send_response(201)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass

HTTPServer(('127.0.0.1', int(sys.argv[1])), Handler).serve_forever()
PYEOF

    python3 "$TEST_TMPDIR/mock_server.py" "$MOCK_PORT" &
    MOCK_PID=$!

    # サーバ起動待ち(listenされるまで最大2秒ポーリング。bats自体がfd3を内部利用するため
    # /dev/tcp直接リダイレクトは避け、python3のsocket接続試行で判定する)
    for _ in $(seq 1 20); do
        python3 -c "import socket,sys
s = socket.socket()
s.settimeout(0.2)
try:
    s.connect(('127.0.0.1', int(sys.argv[1])))
    s.close()
    sys.exit(0)
except OSError:
    sys.exit(1)" "$MOCK_PORT" && break
        sleep 0.1
    done

    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" \
        SUPABASE_URL="http://127.0.0.1:${MOCK_PORT}" \
        SUPABASE_SERVICE_ROLE_KEY="dummy-test-key-not-real" \
        timeout 10 bash "$HELPER_SCRIPT" --live -- "T-209 content"

    kill "$MOCK_PID" 2>/dev/null || true
    wait "$MOCK_PID" 2>/dev/null || true

    [ "$status" -eq 0 ]
    [[ "$output" =~ "LIVE POST OK" ]]
    [[ "$output" =~ "id=mock-row-id-12345" ]]
}

# =============================================================================
# T-210: requires_responseは既定false・--requires-response指定でtrue
# =============================================================================

@test "T-210: requires_response defaults to false, --requires-response sets it true" {
    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" bash "$HELPER_SCRIPT" -- "T-210a content"
    [ "$status" -eq 0 ]
    [[ "$output" =~ '"requires_response": false' ]]

    run env KARO_SECOND_SEND_IINCHO_LOG="$TEST_FAIL_LOG" bash "$HELPER_SCRIPT" \
        --requires-response -- "T-210b content"
    [ "$status" -eq 0 ]
    [[ "$output" =~ '"requires_response": true' ]]
}
