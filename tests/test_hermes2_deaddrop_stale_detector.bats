#!/usr/bin/env bats
# test_hermes2_deaddrop_stale_detector.bats
#
# hermes2 (環境部長) legacy dead-drop YAML の read-only stale 検知器 — TDD テスト
# 起点: 副委員長 work order hermes2-dead-drop-route-guard-work-order-20260721.md item 3
#
# 目的: queue/inbox/hermes2.yaml の未読件数の「新規増加」を検知するが、
# 検知器自身は配送 consumer にはならない (本文再送・既読化・削除は絶対禁止)。
# state は queue/inbox/ の外 (queue/metrics/) に保持し、対象 YAML には
# 一切書き込まない。

setup_file() {
    export PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export DETECTOR_SCRIPT="$PROJECT_ROOT/scripts/hermes2_deaddrop_stale_detector.sh"
    export VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"
    "$VENV_PYTHON" -c "import yaml" 2>/dev/null || return 1
}

setup() {
    export TEST_TMPDIR="$(mktemp -d "$BATS_TMPDIR/h2_stale_test.XXXXXX")"
    export TEST_INBOX_DIR="$TEST_TMPDIR/queue/inbox"
    export TEST_METRICS_DIR="$TEST_TMPDIR/queue/metrics"
    mkdir -p "$TEST_INBOX_DIR" "$TEST_METRICS_DIR"

    export TEST_SCRIPT_DIR="$TEST_TMPDIR/scripts"
    mkdir -p "$TEST_SCRIPT_DIR"
    sed "s|SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")/..*|SCRIPT_DIR=\"$TEST_TMPDIR\"|" \
        "$PROJECT_ROOT/scripts/hermes2_deaddrop_stale_detector.sh" > "$TEST_SCRIPT_DIR/hermes2_deaddrop_stale_detector.sh"
    chmod +x "$TEST_SCRIPT_DIR/hermes2_deaddrop_stale_detector.sh"
    ln -sf "$PROJECT_ROOT/.venv" "$TEST_TMPDIR/.venv"
    export TEST_DETECTOR="$TEST_SCRIPT_DIR/hermes2_deaddrop_stale_detector.sh"

    export HERMES2_INBOX="$TEST_INBOX_DIR/hermes2.yaml"
    export STALE_STATE_FILE="$TEST_METRICS_DIR/hermes2_deaddrop_stale_state.yaml"
}

teardown() {
    [ -n "$TEST_TMPDIR" ] && [ -d "$TEST_TMPDIR" ] && rm -rf "$TEST_TMPDIR"
}

_write_inbox_n_unread() {
    local n="$1"
    local total="${2:-$n}"
    "$VENV_PYTHON" - "$HERMES2_INBOX" "$n" "$total" <<'PYEOF'
import sys, yaml
path, n, total = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
n = min(n, total)
msgs = []
for i in range(total):
    msgs.append({
        "id": f"msg_test_{i}",
        "from": "some_producer",
        "timestamp": "2026-07-21T00:00:00",
        "type": "status_update",
        "content": f"test message {i}",
        "read": i >= n,  # first n are unread, rest are read
    })
with open(path, "w") as f:
    yaml.safe_dump({"messages": msgs}, f, allow_unicode=True)
PYEOF
}

# =============================================================================
# D-001: legacy hermes2.yaml absent → graceful zero-unread baseline, exit 0,
# detector must NOT create/touch queue/inbox/hermes2.yaml itself.
# =============================================================================

@test "D-001: hermes2.yaml absent → baseline established, exit 0, target file NOT created" {
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [ ! -f "$HERMES2_INBOX" ]
    [ -f "$STALE_STATE_FILE" ]
}

# =============================================================================
# D-002: first run with existing unread messages → baseline established
# (not treated as growth, since there is no prior state to compare against).
# =============================================================================

@test "D-002: first run with 7 unread messages → baseline established, exit 0" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"baseline"* ]]
    [ -f "$STALE_STATE_FILE" ]
}

# =============================================================================
# D-003: second run, unread count unchanged → OK, no growth, exit 0
# =============================================================================

@test "D-003: unread count unchanged across two runs → no growth, exit 0" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" != *"GROWTH"* ]]
}

# =============================================================================
# D-004: second run, unread count increased → stale growth detected, exit 1
# =============================================================================

@test "D-004: unread count increases across two runs → GROWTH detected, exit 1" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    _write_inbox_n_unread 9 9
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"GROWTH"* ]]
}

# =============================================================================
# D-005 / D-006: read-only guarantee — detector never mutates the target
# YAML file (no resend, no read-marking, no deletion) across repeated runs.
# =============================================================================

@test "D-005: detector never modifies hermes2.yaml content across multiple runs" {
    _write_inbox_n_unread 7 7
    before_sha="$(sha256sum "$HERMES2_INBOX" | awk '{print $1}')"

    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    after_sha="$(sha256sum "$HERMES2_INBOX" | awk '{print $1}')"
    [ "$before_sha" = "$after_sha" ]
}

@test "D-006: detector never marks messages read=true in hermes2.yaml" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    unread_after=$("$VENV_PYTHON" -c "
import yaml
with open('$HERMES2_INBOX') as f:
    data = yaml.safe_load(f)
print(sum(1 for m in data['messages'] if not m.get('read', False)))
")
    [ "$unread_after" -eq 7 ]
}

# =============================================================================
# D-007: 2 consecutive clean (no-growth) cycles → detector reports the
# 2-cycle confirmation explicitly (work order item 6 evidence requirement).
# =============================================================================

@test "D-007: 2 consecutive no-growth cycles → detector reports 2-cycle confirmation" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"consecutive_clean_cycles=2"* ]] || [[ "$output" == *"2-cycle"* ]]
}

# =============================================================================
# D-008: unread count decreases (e.g. manual triage) → not growth, exit 0
# =============================================================================

@test "D-008: unread count decreases across two runs → not growth, exit 0" {
    _write_inbox_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]

    _write_inbox_n_unread 3 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" != *"GROWTH"* ]]
}

# =============================================================================
# D-009: state file itself lives outside queue/inbox/ (never inside the
# directory the guard is protecting).
# =============================================================================

@test "D-009: state file is stored outside queue/inbox/" {
    _write_inbox_n_unread 1 1
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    case "$STALE_STATE_FILE" in
        "$TEST_INBOX_DIR"/*) false ;;
        *) true ;;
    esac
}

# =============================================================================
# D-010: finding H2-G1-STALE-DETECTOR-COUNT-ALIASING-002 — 未読件数が同数の
# まま「旧未読1件が既読化 (or 消滅)」+「新規未読1件が到着」する同数入替が
# 起きた場合、件数だけの比較では差分ゼロとなり検知漏れする。ID 集合の差分
# 比較であれば、前回未読 ID 集合に存在しなかった新規 ID の出現を検知できる。
# =============================================================================

_write_inbox_with_ids() {
    # $1.. = space-separated "id:read" pairs, e.g. "msg_0:False msg_1:True"
    "$VENV_PYTHON" - "$HERMES2_INBOX" "$@" <<'PYEOF'
import sys, yaml
path = sys.argv[1]
pairs = sys.argv[2:]
msgs = []
for pair in pairs:
    mid, read_flag = pair.split(":")
    msgs.append({
        "id": mid,
        "from": "some_producer",
        "timestamp": "2026-07-21T00:00:00",
        "type": "status_update",
        "content": f"test message {mid}",
        "read": read_flag == "True",
    })
with open(path, "w") as f:
    yaml.safe_dump({"messages": msgs}, f, allow_unicode=True)
PYEOF
}

@test "D-010: unread count stays constant but one unread ID is swapped for a new one → GROWTH detected, exit 1" {
    _write_inbox_with_ids \
        "msg_0:False" "msg_1:False" "msg_2:False" "msg_3:False" \
        "msg_4:False" "msg_5:False" "msg_6:False"
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"baseline"* ]]

    # msg_0 は既読化 (or triage 済) されて消え、代わりに新規 msg_new が
    # 未読で到着 → unread 件数は 7 のまま変わらない (count-neutral swap)。
    _write_inbox_with_ids \
        "msg_0:True" "msg_1:False" "msg_2:False" "msg_3:False" \
        "msg_4:False" "msg_5:False" "msg_6:False" "msg_new:False"
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"GROWTH"* ]]
}

# =============================================================================
# TC2: Codex cycle1 B2 detection test — H2-CODEX-B2-UNREAD-COUNT-GROWTH-001
#
# 背景: unread_ids は `m.get('id')` が真値のメッセージのみを集合化する
# (id フィールド自体を持たないメッセージは常に集合から除外される)。その
# ため D-004/D-010 のように★全メッセージが id を持つ★状況では、たとえ
# count_growth 条件を取り除いても new_ids 差分だけで growth を検知できて
# しまい、B2 (ID を持たない未読メッセージの増加を検知し損なう) の穴を
# 実際には検証していない。
#
# TC2 は id フィールドを一切持たないメッセージ集合のみで unread 件数を
# 増加させ、unread_ids 集合が両 cycle とも空集合のまま変化しない状況を
# 作る → new_ids は常に空集合となるため、growth を検知できるのは
# count_growth (unread > prev_unread) のみ、という B2 の穴を直接塞ぐ。
# =============================================================================

_write_inbox_no_id_n_unread() {
    local n="$1"
    local total="${2:-$n}"
    "$VENV_PYTHON" - "$HERMES2_INBOX" "$n" "$total" <<'PYEOF'
import sys, yaml
path, n, total = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
n = min(n, total)
msgs = []
for i in range(total):
    msgs.append({
        # ★TC2 (Codex cycle1 B2)★: id フィールドを意図的に持たせない。
        # unread_ids は id を持つメッセージのみを収集するため、id なし
        # メッセージの増加は ID 集合差分だけでは検知不能。
        "from": "some_producer",
        "timestamp": "2026-07-21T00:00:00",
        "type": "status_update",
        "content": f"test message no-id {i}",
        "read": i >= n,
    })
with open(path, "w") as f:
    yaml.safe_dump({"messages": msgs}, f, allow_unicode=True)
PYEOF
}

@test "TC2: ID-less unread messages growth (Codex cycle1 B2) → GROWTH detected via count_growth fallback, exit 1" {
    _write_inbox_no_id_n_unread 5 5
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"baseline"* ]]

    # unread_ids は id 無しのため両 cycle とも空集合 (new_ids は常に空) —
    # count_growth (unread 総数比較) だけが唯一の検知経路となる。
    _write_inbox_no_id_n_unread 7 7
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 1 ]
    [[ "$output" == *"GROWTH"* ]]
}

# =============================================================================
# TC3: Codex/gunshi T1 non-negative int contract test — fix-cycle3 追補
# H2-G1-CODEX-T1-NONNEGATIVE-VALIDATION-001
#
# 背景: fix-cycle2 の T1 是正は isinstance(prev_unread_raw, int) のみで型検証
# していたが、Python では bool は int のサブクラスのため True/False を整数と
# して誤って受理してしまう。また負数も弾いていなかった。TC3 は state file を
# 直接破損させ (bool/負数混入)、①bool・負数の prev_unread が「有効な前回値」
# として扱われず baseline (安全側) にフォールバックすること ②bool・負数の
# consecutive_clean_cycles が 0 にリセットされること ③unread_ids が非 list
# または非 string 要素混入でもクラッシュせず安全にフォールバックすること、
# を検証する。
# =============================================================================

_write_state_file() {
    # $1=last_unread_count用Python literal, $2=consecutive_clean_cycles用Python literal,
    # $3=unread_ids用Python literal (省略時 "[]")
    local unread_val="$1"
    local cycles_val="$2"
    local ids_val="${3:-[]}"
    "$VENV_PYTHON" - "$STALE_STATE_FILE" "$unread_val" "$cycles_val" "$ids_val" <<'PYEOF'
import sys, yaml, ast
path, unread_raw, cycles_raw, ids_raw = sys.argv[1:5]
state = {
    'last_checked_at': '2026-07-21T00:00:00',
    'last_total_count': 5,
    'last_unread_count': ast.literal_eval(unread_raw),
    'consecutive_clean_cycles': ast.literal_eval(cycles_raw),
    'unread_ids': ast.literal_eval(ids_raw),
}
with open(path, 'w') as f:
    yaml.safe_dump(state, f, allow_unicode=True)
PYEOF
}

@test "TC3a: corrupted state last_unread_count=bool(True) rejected → baseline fallback, not mis-treated as int 1" {
    _write_inbox_n_unread 3 5
    _write_state_file "True" "2" "[]"
    run bash "$TEST_DETECTOR"
    # 是正前: isinstance(True, int) は True のため prev_unread=1 として受理され、
    # unread(3) > 1 で GROWTH (exit 1) を誤検知してしまう。
    [ "$status" -eq 0 ]
    [[ "$output" == *"baseline"* ]]
}

@test "TC3b: corrupted state last_unread_count=-5 (negative) rejected → baseline fallback" {
    _write_inbox_n_unread 3 5
    _write_state_file "-5" "2" "[]"
    run bash "$TEST_DETECTOR"
    # 是正前: 負数も isinstance(int) を通過して受理され、unread(3) > -5 で
    # GROWTH (exit 1) を誤検知してしまう。
    [ "$status" -eq 0 ]
    [[ "$output" == *"baseline"* ]]
}

@test "TC3c: corrupted state consecutive_clean_cycles=-7 (negative) rejected → reset to 0 before increment" {
    _write_inbox_n_unread 3 5
    _write_state_file "3" "-7" "[\"msg_test_0\", \"msg_test_1\", \"msg_test_2\"]"
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    # 是正前: int(-7) がそのまま受理され、clean 判定時に -7+1=-6 という
    # 意味不明な負のカウントが出力されてしまう。是正後は 0+1=1。
    [[ "$output" == *"consecutive_clean_cycles=1)"* ]]
}

@test "TC3d: corrupted state consecutive_clean_cycles=bool(True) rejected → reset to 0 before increment" {
    _write_inbox_n_unread 3 5
    _write_state_file "3" "True" "[\"msg_test_0\", \"msg_test_1\", \"msg_test_2\"]"
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    # 是正前: int(True)=1 がそのまま受理され、clean 判定時に 1+1=2 になって
    # しまう。是正後は bool 除外により 0+1=1。
    [[ "$output" == *"consecutive_clean_cycles=1)"* ]]
}

@test "TC3e: corrupted state unread_ids is non-list (string, not a list) → safe empty-set fallback, no crash" {
    _write_inbox_n_unread 3 5
    _write_state_file "3" "2" "\"not_a_list\""
    run bash "$TEST_DETECTOR"
    # 非 list は空集合へフォールバック (安全側=既知IDなし扱い) → 今回の
    # unread_ids 全件が「新規」とみなされ GROWTH。クラッシュしないことが本質。
    [ "$status" -eq 1 ]
    [[ "$output" == *"GROWTH"* ]]
}

@test "TC3f: corrupted state unread_ids contains non-string elements → non-string entries filtered, no crash" {
    _write_inbox_n_unread 3 5
    _write_state_file "3" "2" "[1, None, \"msg_test_0\", \"msg_test_1\", \"msg_test_2\"]"
    run bash "$TEST_DETECTOR"
    # 非 string 要素 (1, None) は除去され、残る文字列3件が現在の unread_ids と
    # 完全一致するため growth なし (クラッシュしないことが本質)。
    [ "$status" -eq 0 ]
    [[ "$output" == *"OK: no new stale accumulation"* ]]
}

# =============================================================================
# TC4: Codex/gunshi B3 concurrency regression test — fix-cycle3 追補
# H2-G1-CODEX-B3-CONCURRENCY-TEST-MISSING-002
#
# flock による read-modify-write 排他は静的レビューでは妥当に見えるが、実際に
# 並行起動した際「更新消失 (lost update)」が起きないことを実証する自動試験が
# 無ければ回帰を検知できない。同一 inbox/state を用いて複数プロセスを同時
# 起動し、①全プロセスが exit 0 (静的 inbox のため growth は本来発生しない)
# で終了する ②最終 state YAML が健全に parse できる ③consecutive_clean_cycles
# が「直列実行した場合と厳密に一致する値」になっている (flock が真に排他制御
# し、どの並行呼び出しも他の呼び出しの更新を踏み潰していないことの証明) こと
# を検証する。lock 待ちは無期限 (timeout 無し、詳細は本体スクリプトのコメント
# 参照) のため、本試験はタイムアウト由来の欠測ケースを想定しない。
# =============================================================================

@test "TC4: concurrent detector launches against shared state → all exit 0, state YAML intact, no lost updates (Codex/gunshi B3 concurrency)" {
    _write_inbox_n_unread 3 5

    # baseline を直列に1回確立 (consecutive_clean_cycles=1 から開始)。
    run bash "$TEST_DETECTOR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"baseline"* ]]

    local n=8
    local pids=()
    local i
    for i in $(seq 1 "$n"); do
        bash "$TEST_DETECTOR" >"$TEST_TMPDIR/concurrent_$i.log" 2>&1 &
        pids+=("$!")
    done

    local exit_codes=()
    local pid
    for pid in "${pids[@]}"; do
        wait "$pid"
        exit_codes+=("$?")
    done

    # ①全プロセスが exit 0 (静的 inbox のため growth は起こり得ない)
    local code
    for code in "${exit_codes[@]}"; do
        [ "$code" -eq 0 ]
    done

    # ②state YAML が健全 ③consecutive_clean_cycles が直列実行と厳密一致
    # (baseline の1回 + 並行実行 n 回 = 1+n。flock が真に排他していなければ
    # lost update により 1+n を下回るはず)。
    run "$VENV_PYTHON" -c "
import yaml
with open('$STALE_STATE_FILE') as f:
    d = yaml.safe_load(f)
assert isinstance(d, dict)
for k in ('last_checked_at', 'last_total_count', 'last_unread_count', 'consecutive_clean_cycles', 'unread_ids'):
    assert k in d, k
assert d['last_unread_count'] == 3, d['last_unread_count']
assert d['last_total_count'] == 5, d['last_total_count']
assert d['consecutive_clean_cycles'] == 1 + $n, d['consecutive_clean_cycles']
print('OK')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"OK"* ]]
}
