#!/usr/bin/env bats
# test_codex_residue_negative.bats — 工区1 ⒞ ★負テスト3形★
#
# 出所: 理事長令「通信経路恒久安定化」工区1
#       → Commander msg_20260807_201018_d1d9e5ea
#       → 将軍second msg_20260807_201322_adbe40db
#       → 家老second msg_20260807_201541_b56065bf (足軽4号 差配)
# 設計宣言 (実行前に形を固定した票):
#       docs/incident_logs/2026-08-07_worksite1_c_negative_test_design_a4.md
# 被検対象 (a2 の ⒝① 実装) と interface 契約 C-1〜C-4:
#       docs/incident_logs/2026-08-07_worksite1_ab_codex_residue_a2.md §5
#
# ★本 file は production 関数 `codex_residue_cleanup()` を ★直に呼ぶ★★。
#   test 本体へ if/else を書き写す事は禁 (設計票 §6 の条 — 既存 T-CODEX-003/004 は
#   本体を呼ばず己の写しを測って居り、本体が変わっても緑のままに御座る)。
#
# 狙い = ★掃除が走ってはならぬ場合★ の検め。C-u は composer を無差別に消す ∴
#        誤爆すれば人/agent の本物 draft を破壊する (三形中 最大の損害)。
#
# テスト構成:
#   T-RESID-000: 契約 C-1 — production 関数が source 後に在る事
#   T-RESID-001: ㈠   本物 draft が composer に在る → 掃除せぬ
#   T-RESID-002: ㈠補助 prefix ★と★ 人の続き文が併存 → 掃除せぬ
#   T-RESID-003: ㈡ⓐ 前方に余分 `xinbox2`      → 掃除せぬ
#   T-RESID-004: ㈡ⓑ 後方に余分 `inbox2x`      → 掃除せぬ
#   T-RESID-005: ㈡ⓒ 真部分列 `inbox`          → 掃除せぬ
#   T-RESID-006: ㈡ⓓ 別の未読数 `inbox3`       → 掃除せぬ (別便の残骸を消さぬ)
#   T-RESID-007: ㈡ⓔ 末尾空白 `inbox2␣`        → ★掃除が走る (cleaned)★ = C-4⑸ の契約
#   T-RESID-008: ㈢   着弾成功・composer 空     → 掃除せぬ (全体 grep 実装なら落ちる形)
#   T-RESID-009: ★陽性対照★ 真の残骸           → ★掃除が走る★
#                (之が無ければ ㈠㈡㈢ の「C-u 無し」は ★走って居らぬのか通ったのか★ 判じ得ぬ)
#
# ★live watcher process を要する形は本 file に一つも無い★ (⒠blocker 配下の
#   ㊀㊁㊂ は設計票 §4 の通り ★実行せず blocked★・mock で代走せぬ)。

setup_file() {
    export PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
    # 既定は本物の production script。
    # WATCHER_SCRIPT_OVERRIDE は ★変異検査 (mutation check) 専用★ の口に御座る ――
    # 「述語が本体に噛んで居るか」を、本体を ★一字も触れずに★ 検める為
    # (writable な複製へ既知の欠陥を入れ、本 file が ★落ちる事★ を確かめる)。
    # 常用路では設定せぬ ∴ 既定の挙動は不変。
    export WATCHER_SCRIPT="${WATCHER_SCRIPT_OVERRIDE:-$PROJECT_ROOT/scripts/inbox_watcher.sh}"
    [ -f "$WATCHER_SCRIPT" ] || return 1
}

setup() {
    export TEST_TMPDIR="$(mktemp -d "$BATS_TMPDIR/codex_residue_test.XXXXXX")"

    export MOCK_LOG="$TEST_TMPDIR/tmux_calls.log"
    > "$MOCK_LOG"

    export MOCK_CAPTURE_PANE=""

    # 既存 tests/unit/test_send_wakeup.bats の harness を ★流用★ (新規発明せず)。
    # __INBOX_WATCHER_TESTING__=1 で本物の inbox_watcher.sh を source し、
    # 関数定義のみを読み込む (arg parse / main loop は skip される)。
    export TEST_HARNESS="$TEST_TMPDIR/test_harness.sh"
    cat > "$TEST_HARNESS" << HARNESS
#!/bin/bash
AGENT_ID="test_agent"
PANE_TARGET="test:0.0"
CLI_TYPE="codex"
SCRIPT_DIR="$PROJECT_ROOT"

tmux() {
    echo "tmux \$*" >> "$MOCK_LOG"
    if echo "\$*" | grep -q "capture-pane"; then
        printf '%s\n' "\${MOCK_CAPTURE_PANE:-}"
        return 0
    fi
    return 0
}
timeout() { shift; "\$@"; }
export -f tmux timeout

export __INBOX_WATCHER_TESTING__=1
source "$WATCHER_SCRIPT"
HARNESS
    chmod +x "$TEST_HARNESS"
}

teardown() {
    rm -rf "$TEST_TMPDIR"
}

# 掃除が走ったか否かを ★MOCK_LOG の C-u 送出★ で判ずる (契約 C-3)
assert_no_cu() {
    if grep -q "send-keys.*C-u" "$MOCK_LOG"; then
        echo "FAIL: C-u が送出された (掃除が暴発)"
        cat "$MOCK_LOG"
        return 1
    fi
}

assert_cu_sent() {
    if ! grep -q "send-keys.*C-u" "$MOCK_LOG"; then
        echo "FAIL: C-u が送出されて居らぬ"
        cat "$MOCK_LOG"
        return 1
    fi
}

# --- T-RESID-000: 契約 C-1 の検め ---

@test "T-RESID-000: 契約C-1 codex_residue_cleanup が production 側に在る" {
    run bash -c "source '$TEST_HARNESS' && declare -F codex_residue_cleanup"
    [ "$status" -eq 0 ]
    echo "$output" | grep -q "codex_residue_cleanup"
}

# --- ㈠ 本物 draft が composer に在る時、掃除が走らぬ事 ---

@test "T-RESID-001: ㈠ 本物 draft が composer に在る → 掃除せぬ" {
    # 会話面に inbox2 が ★着弾済★ (= 全体 grep 実装なら一致して掃除が暴発する条件)
    # composer には人の書きかけの文
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
› 副院長殿へ 本日の残件を纏めて"

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=composer_mismatch"
    assert_no_cu
}

@test "T-RESID-002: ㈠補助 prefix と人の続き文が併存 → 掃除せぬ" {
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
› inbox2 と書いた後に続けて人が打った"

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=composer_mismatch"
    assert_no_cu
}

# --- ㈡ prefix 部分一致で走らぬ事 (ⓐ〜ⓓ) ---

@test "T-RESID-003: ㈡ⓐ 前方に余分 xinbox2 → 掃除せぬ" {
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
› xinbox2"

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=composer_mismatch"
    assert_no_cu
}

@test "T-RESID-004: ㈡ⓑ 後方に余分 inbox2x → 掃除せぬ" {
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
› inbox2x"

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=composer_mismatch"
    assert_no_cu
}

@test "T-RESID-005: ㈡ⓒ 真部分列 inbox → 掃除せぬ" {
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
› inbox"

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=composer_mismatch"
    assert_no_cu
}

@test "T-RESID-006: ㈡ⓓ 別の未読数 inbox3 → 掃除せぬ (別便の残骸を消さぬ)" {
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
› inbox3"

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=composer_mismatch"
    assert_no_cu
}

# --- ㈡ⓔ 末尾空白 = ★契約 C-4⑸ により 掃除が走る★ が期待値 ---
# 述語の出所: a2 票 §5「a4 の ㈡ⓔ の期待値 = 掃除が走る (cleaned)」
#   根拠 = tmux capture-pane -p は行末空白を必ず落とす ∴ 本経路では区別し得ぬ。
# ★之は負テストに非ず・契約の検め★ (設計票では「述語未定」と記した形)。

@test "T-RESID-007: ㈡ⓔ 末尾空白 inbox2␣ → 契約通り 掃除が走る (cleaned)" {
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
› inbox2 "

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=0"
    echo "$output" | grep -q "STATE=cleaned"
    assert_cu_sent
}

# --- ㈢ 着弾成功時に掃除が走らぬ事 (★最も肝★) ---

@test "T-RESID-008: ㈢ 着弾成功・composer 空 → 掃除せぬ" {
    # 着弾した nudge は ★会話面にも★ 在る。capture 全体を grep する実装なら
    # 常に一致して掃除が暴発する ∴ 本形は「composer 行のみを見て居るか」の検め。
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
codex: 承知仕った
› "

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=composer_mismatch"
    assert_no_cu
}

# --- ★陽性対照★ (之が無ければ上の「C-u 無し」は空振りと区別し得ぬ) ---

@test "T-RESID-009: 陽性対照 真の残骸 (着弾済+完全一致) → 掃除が走る" {
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
› inbox2"

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=0"
    echo "$output" | grep -q "STATE=cleaned"
    assert_cu_sent
}

# --- ㈣ 着弾せぬ物を掃除せぬ事 (令16 追加分・事前宣言済) ---
#
# ★出自★: 変異検査 M5 (着弾確認から composer 行の除外が落ちる) が
#   当職10形 0/10・a2 13形 0/13 で ★両母集団を素通り★ した = 穴。
#   composer 行自身を「着弾」と誤認する実装は、人が偶々同じ字を打っただけの
#   composer を残骸と看做して消し飛ばし申す。

@test "T-RESID-010: ㈣ 着弾せぬ完全一致 (会話面に無し) → 掃除せぬ (not_landed)" {
    # composer には 'inbox2' が完全一致で在るが、★会話面には一度も着弾しておらぬ★。
    # = nudge は届いておらず、人が偶々同じ字を打った状況に御座る。
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
codex: 承知仕った
› inbox2"

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=not_landed"
    assert_no_cu
}

# --- ㈤ idle 掃除 (令25 で門が及んだ2箇所) に噛む形 (令16 追加課⑴) ---
#
# ★出自★: a2 が process_unread 内の idle 掃除2箇所へ codex_presend_gate を及ぼした
#   (将軍追認済)。当職の㈠〜㈣は codex_residue_cleanup を直に呼ぶのみ ∴
#   ★idle 箇所には一度も噛んでおらぬ★ = 陽性対照不在。本形で埋める。
#
# ★空振り防止★: 「裸 C-u が 0」だけでは ★分岐ごと消えても緑★ に成り申す。
#   ∴ codex 分岐の出現数が 2 である事を同時に検め、「数えた上での 0」とする。

@test "T-RESID-011: ㈤ idle 掃除の codex 分岐に 門を経ぬ裸の C-u が無い (分岐数2を同時に検む)" {
    run awk '
        /elif \[\[ "\$\(get_effective_cli_type\)" == "codex" \]\]; then/ {
            branches++; inbranch=1; gated=0; next
        }
        inbranch && /codex_presend_gate/            { gated=1 }
        inbranch && /send-keys .* C-u/              { if (!gated) naked++; inbranch=0 }
        inbranch && /^[[:space:]]*(else|fi)[[:space:]]*$/ { inbranch=0 }
        END { printf "BRANCHES=%d NAKED=%d\n", branches+0, naked+0 }
    ' "$WATCHER_SCRIPT"

    echo "観測: $output"
    # ★門を経ぬ裸の C-u は 0 箇所★
    echo "$output" | grep -q "NAKED=0"
    # ★其の 0 は「数えた上での 0」★ — 分岐が消えたのではない事の証
    echo "$output" | grep -q "BRANCHES=2"
}

# --- ㈥ 契約 C-3 の残る2値を観測する形 (母集団の穴埋め) ---
#
# ★出自★: 契約 C-3 は STATE の取り得る値を5つと宣す。
#   当職の㈠〜㈤は cleaned / composer_mismatch / not_landed の ★3値しか観測しておらぬ★。
#   残る no_composer / empty_prefix は ★宣言されて居るのに一度も測られておらぬ★ =
#   「其の路が壊れても誰も気付かぬ」状態に御座る。

@test "T-RESID-012: ㈥ⓐ composer marker 不在 → 掃除せぬ (no_composer・安全側)" {
    # marker 行 (❯ / ›) が capture に一つも無い = composer の在処が判らぬ。
    # ★判らぬ時に撃つ★ のが最も危うい ∴ 見送るが正。
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
inbox2
codex: 承知仕った"

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup 'inbox2'; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=no_composer"
    assert_no_cu
}

@test "T-RESID-013: ㈥ⓑ prefix 空 → 掃除せぬ (empty_prefix・空文字で全一致させぬ)" {
    # prefix が空のまま完全一致を問えば ★空 composer が常に一致★ し得る。
    # 引数の空は「掃除する物が無い」の意 ∴ 判定に入る前に弾くが正。
    export MOCK_CAPTURE_PANE="user: 前便を承知仕った
› "

    run bash -c "source '$TEST_HARNESS'; codex_residue_cleanup ''; echo \"RC=\$? STATE=\$CODEX_RESIDUE_STATE\""
    echo "$output" | grep -q "RC=1"
    echo "$output" | grep -q "STATE=empty_prefix"
    assert_no_cu
}
