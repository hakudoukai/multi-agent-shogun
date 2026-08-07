#!/usr/bin/env bats
#
# 令25 ⑴ 送信前 C-u 根治 — ★負テスト★ (足軽2号 / 工区1)
#
# ★出自★: 令①の範囲外 (送信前 C-u) を ★将軍second 裁で工区1へ拡張★ した分。
#
# ★a4 殿の ⒞ とは 別票・別形式に御座る★ (令 ㈡ 「別形式として宣言し、
#   a4 が ⒞ の票を組み直さずに済む様にせよ」):
#     a4 ⒞ = ★送信 後★ の残骸掃除 (codex_residue_cleanup) の負テスト。
#     本票  = ★送信 前★ の門       (codex_presend_gate)   の負テスト。
#   両者は正規化 (C-4 ⑴〜⑸) を ★同一関数 composer_line_normalized で共有★ する。
#   ∴ a4 の ⒞ に手を入れる要は無し。両票は同じ物差しを別の刻で測るのみ。
#
# ★境界★: 本テストは ★実 tmux を一度も呼ばぬ★。tmux は stub 関数に置換し、
#   send-keys は「撃った事の記録」だけを取る。∴ 令の境界
#   「send-keys 0 / watcher 生殺 0 / hermes pane は capture のみ」を犯さぬ。
#
# ★負テストの読み★ (「PASS と書くな」の形):
#   各 case の見出しに ★何が起きたら PASS と書いてはならぬか★ を記す。
#   期待は「通る事」ではなく「★通してはならぬ物が通らぬ事★」に御座る。

setup() {
    REPO="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    # 既定は正本。★変異テスト (mutation) の為に差替可★ —
    # 「門を壊したら本当に赤に成るか」を確かめねば、此の緑は空の緑に御座る。
    WATCHER="${PRESEND_GATE_WATCHER:-$REPO/scripts/inbox_watcher.sh}"
    [ -f "$WATCHER" ] || { echo "watcher not found: $WATCHER"; return 1; }

    # ★実装本体から関数を抜き出して評価する (写経禁)★
    #   test に実装を書き写せば 実装が変わっても test は緑のまま = 嘘の緑に成り申す。
    eval "$(sed -n '/^composer_line_normalized() {/,/^}/p' "$WATCHER")"
    eval "$(sed -n '/^codex_presend_gate() {/,/^}/p' "$WATCHER")"
    eval "$(sed -n '/^codex_residue_cleanup() {/,/^}/p' "$WATCHER")"

    type composer_line_normalized >/dev/null || { echo "抽出失敗: composer_line_normalized"; return 1; }
    type codex_presend_gate       >/dev/null || { echo "抽出失敗: codex_presend_gate"; return 1; }

    PANE_TARGET="stub:0.0"
    AGENT_ID="testagent"
    SENT_LOG="$BATS_TEST_TMPDIR/sent_keys"
    : > "$SENT_LOG"
    FAKE_CAPTURE=""
}

# ─── stub 群 (実 tmux / 実 sleep を呼ばぬ) ───
tmux() {
    case "$1" in
        capture-pane) printf '%s\n' "$FAKE_CAPTURE" ;;
        send-keys)    shift; printf '%s\n' "$*" >> "$SENT_LOG" ;;
        *)            : ;;
    esac
}
timeout() { shift; "$@"; }
sleep()   { :; }
date()    { printf 'STUBDATE'; }

cu_count() { grep -c -- 'C-u' "$SENT_LOG" 2>/dev/null || true; }
sent_count() { wc -l < "$SENT_LOG" | tr -d ' '; }

# composer marker は U+276F (❯)。実測 (hermes-honbucho:0.0 / hermes-gunshi-second:0.0) と同形。
CMP=$'❯'

# ══════════════════════════════════════════════════════════════════
# N1 ★最重要★ 他者の本物 draft
#    → C-u が 1 度でも飛んだら PASS と書くな
#    → 門が「注入して良し」を返したら PASS と書くな
#    (起票時 hermes-honbucho:0.0 に現に載って居た実文を そのまま使う)
# ══════════════════════════════════════════════════════════════════
@test "N1: 他者の draft を抱えた composer へ C-u も注入も為さぬ" {
    FAKE_CAPTURE=" ${CMP} [本部長 downlink] pc_handshake seq=155925"
    run_gate() { codex_presend_gate "inbox3" "stub:0.0"; }
    if run_gate; then
        echo "FAIL: dirty composer なのに門が通した (state=$CODEX_PRESEND_STATE)"; return 1
    fi
    [ "$CODEX_PRESEND_STATE" = "dirty" ] || { echo "FAIL: state=$CODEX_PRESEND_STATE (期待 dirty)"; return 1; }
    [ "$(cu_count)" = "0" ] || { echo "FAIL: C-u が $(cu_count) 回飛んだ — draft 破壊"; return 1; }
    [ "$(sent_count)" = "0" ] || { echo "FAIL: keystroke が $(sent_count) 件飛んだ"; return 1; }
}

# ══════════════════════════════════════════════════════════════════
# N2 己の注入 prefix と完全一致
#    → C-u が飛ばねば PASS と書くな (残骸が残り 次便と繋がって混合便に成る)
# ══════════════════════════════════════════════════════════════════
@test "N2: composer が己の nudge と完全一致なら掃除して通す" {
    FAKE_CAPTURE=" ${CMP} inbox3"
    codex_presend_gate "inbox3" "stub:0.0" || { echo "FAIL: 己の物なのに通さぬ (state=$CODEX_PRESEND_STATE)"; return 1; }
    [ "$CODEX_PRESEND_STATE" = "cleaned_own" ] || { echo "FAIL: state=$CODEX_PRESEND_STATE"; return 1; }
    [ "$(cu_count)" = "1" ] || { echo "FAIL: C-u が $(cu_count) 回 (期待 1)"; return 1; }
}

# ══════════════════════════════════════════════════════════════════
# N3 空 composer
#    → 門が見送ったら PASS と書くな (nudge が永久に届かず飢える)
#    → 不要な C-u が飛んだら PASS と書くな (無用の keystroke は撃たぬ)
# ══════════════════════════════════════════════════════════════════
@test "N3: 空 composer は通し、無用の C-u を撃たぬ" {
    FAKE_CAPTURE=" ${CMP}"
    codex_presend_gate "inbox3" "stub:0.0" || { echo "FAIL: 空なのに見送った (state=$CODEX_PRESEND_STATE)"; return 1; }
    [ "$CODEX_PRESEND_STATE" = "empty" ] || { echo "FAIL: state=$CODEX_PRESEND_STATE"; return 1; }
    [ "$(cu_count)" = "0" ] || { echo "FAIL: 空なのに C-u が $(cu_count) 回"; return 1; }
}

# ══════════════════════════════════════════════════════════════════
# N4 marker 不在 (capture 失敗 / 画面遷移中)
#    → 「見えぬから空だろう」と注入したら PASS と書くな
#    ※飢餓の代償は実装 docstring に明記済 (毎回 log へ出す)
# ══════════════════════════════════════════════════════════════════
@test "N4: composer marker 不在なら安全側に見送る" {
    FAKE_CAPTURE="Welcome to Codex
loading..."
    if codex_presend_gate "inbox3" "stub:0.0"; then
        echo "FAIL: marker 不在なのに通した (state=$CODEX_PRESEND_STATE)"; return 1
    fi
    [ "$CODEX_PRESEND_STATE" = "no_composer" ] || { echo "FAIL: state=$CODEX_PRESEND_STATE"; return 1; }
    [ "$(sent_count)" = "0" ] || { echo "FAIL: keystroke が飛んだ"; return 1; }
}

# ══════════════════════════════════════════════════════════════════
# N5 正規化 C-4 ⑴〜⑸ (NBSP / 前後空白)
#    → 空白差だけで「他者の draft」と誤判定して見送ったら PASS と書くな
#    (`capture-pane -p` は行末空白を必ず落とす ∴ 末尾差は測れぬ、の含意)
# ══════════════════════════════════════════════════════════════════
@test "N5: NBSP・前後空白の差は己の物と看做す" {
    FAKE_CAPTURE=$'   ❯  inbox3   '
    codex_presend_gate "inbox3" "stub:0.0" || { echo "FAIL: 空白差で誤って見送った (state=$CODEX_PRESEND_STATE)"; return 1; }
    [ "$CODEX_PRESEND_STATE" = "cleaned_own" ] || { echo "FAIL: state=$CODEX_PRESEND_STATE"; return 1; }
}

# ══════════════════════════════════════════════════════════════════
# N6 ★部分一致で消すな★
#    composer = "inbox3 と書きかけの続き" (己の prefix を ★含む★ が一致せぬ)
#    → 掃除したら PASS と書くな (「含む」で消すのは draft 破壊の別経路)
# ══════════════════════════════════════════════════════════════════
@test "N6: 己の prefix を含むだけの draft は掃除せぬ" {
    FAKE_CAPTURE=" ${CMP} inbox3 の件だが、これは人が書きかけの文に御座る"
    if codex_presend_gate "inbox3" "stub:0.0"; then
        echo "FAIL: 部分一致で通した (state=$CODEX_PRESEND_STATE)"; return 1
    fi
    [ "$CODEX_PRESEND_STATE" = "dirty" ] || { echo "FAIL: state=$CODEX_PRESEND_STATE"; return 1; }
    [ "$(cu_count)" = "0" ] || { echo "FAIL: 部分一致なのに C-u が飛んだ"; return 1; }
}

# ══════════════════════════════════════════════════════════════════
# N7 履歴中の古い marker 行
#    → 上方の古い marker を composer と誤読したら PASS と書くな
# ══════════════════════════════════════════════════════════════════
@test "N7: composer は最下段の marker 行のみを見る" {
    FAKE_CAPTURE=" ${CMP} 前に人が送った古い命令
  └─ ● done
 ─ ready │ gpt 5.6 sol
 ${CMP}"
    codex_presend_gate "inbox3" "stub:0.0" || { echo "FAIL: 最下段は空なのに見送った (state=$CODEX_PRESEND_STATE)"; return 1; }
    [ "$CODEX_PRESEND_STATE" = "empty" ] || { echo "FAIL: state=$CODEX_PRESEND_STATE (古い marker を拾った疑い)"; return 1; }
}

# ══════════════════════════════════════════════════════════════════
# N8 own_prefix が空 (/new・startup prompt の路)
#    → 書きかけが在るのに通したら PASS と書くな
#    (/new は会話を捨てる不可逆の令 ∴ 尚更 draft を跨いで撃たぬ)
# ══════════════════════════════════════════════════════════════════
@test "N8: own_prefix 空の路は 空 composer のみ通す" {
    FAKE_CAPTURE=" ${CMP} 書きかけの文"
    if codex_presend_gate "" "stub:0.0"; then
        echo "FAIL: prefix 空の路で dirty を通した"; return 1
    fi
    [ "$CODEX_PRESEND_STATE" = "dirty" ] || { echo "FAIL: state=$CODEX_PRESEND_STATE"; return 1; }
    [ "$(cu_count)" = "0" ] || { echo "FAIL: C-u が飛んだ"; return 1; }

    : > "$SENT_LOG"
    FAKE_CAPTURE=" ${CMP}"
    codex_presend_gate "" "stub:0.0" || { echo "FAIL: 空 composer を見送った"; return 1; }
    [ "$CODEX_PRESEND_STATE" = "empty" ] || { echo "FAIL: state=$CODEX_PRESEND_STATE"; return 1; }
}

# ══════════════════════════════════════════════════════════════════
# N9 ★門と掃除が同じ物差しで測る事★ (二重実装の検出)
#    → 同じ composer に対し 二者の正規化結果が食い違ったら PASS と書くな
# ══════════════════════════════════════════════════════════════════
@test "N9: 送信前門と送信後掃除は同一の正規化を共有する" {
    FAKE_CAPTURE=$'   ❯ inbox7   '
    composer_line_normalized "stub:0.0" || { echo "FAIL: 正規化が composer を得られず"; return 1; }
    local a="$COMPOSER_CONTENT"
    [ "$a" = "inbox7" ] || { echo "FAIL: 正規化結果='$a' (期待 'inbox7')"; return 1; }

    # 掃除側も同じ関数を通る事 = 「己の物」判定が一致する
    FAKE_CAPTURE=$'inbox7 landed\n   ❯ inbox7   '
    codex_residue_cleanup "inbox7" "stub:0.0" || { echo "FAIL: 掃除側が己の物と看做さず (state=$CODEX_RESIDUE_STATE)"; return 1; }
    [ "$CODEX_RESIDUE_STATE" = "cleaned" ] || { echo "FAIL: residue state=$CODEX_RESIDUE_STATE"; return 1; }
}

# ══════════════════════════════════════════════════════════════════
# N10 ★set -euo pipefail の下で marker 不在が daemon を殺さぬ事★
#    → grep 不一致が watcher を落としたら PASS と書くな
# ══════════════════════════════════════════════════════════════════
@test "N10: marker 不在でも set -euo pipefail 下で落ちぬ" {
    set -euo pipefail
    FAKE_CAPTURE="no marker here"
    composer_line_normalized "stub:0.0" && rc=0 || rc=$?
    [ "$rc" = "1" ] || { echo "FAIL: 返値=$rc (期待 1)"; return 1; }
    echo "生存確認: 此処へ到達した事が ★落ちなかった証★"
}

# ══════════════════════════════════════════════════════════════════
# N11 ★配線の静的検証★ — 門が "x" より ★前★ に在る事
#    → "x" が門より先に在ったら PASS と書くな
#    (関数単体の緑は「門が正しく判ずる」証にすぎず、
#     「門が正しい場所に置かれた」証には成らぬ)
# ══════════════════════════════════════════════════════════════════
@test "N11: 全ての \"x\" 送出点の直前に門が在る" {
    local w="$WATCHER"
    local bad=0
    while read -r xline; do
        # 当該 "x" 行より前 30 行以内に codex_presend_gate 呼出が在るか
        local from=$(( xline > 30 ? xline - 30 : 1 ))
        if ! sed -n "${from},$((xline-1))p" "$w" | grep -q 'codex_presend_gate'; then
            echo "FAIL: L${xline} の \"x\" 送出に先立つ門が無い"
            bad=1
        fi
    done < <(grep -n 'send-keys -t "\$PANE_TARGET" "x"' "$w" | cut -d: -f1)
    [ "$bad" = "0" ] || return 1
}

# ══════════════════════════════════════════════════════════════════
# N12 ★C-u 送出点の棚卸し固定★ (tripwire)
#    → 無門の C-u が新たに増えても緑のままなら PASS と書くな
#    棚卸し (本改修後): 実 C-u 送出行は ★13 箇所★。内訳:
#      ⑴ 門/掃除の実装の中 ………… 2 (codex_presend_gate / codex_residue_cleanup)
#      ⑵ 門を通した後の C-u ……… 6 (/new路 / startup / context-reset /
#                                    nudge前掃除 / idle掃除×2 — 孰れも codex)
#      ⑶ claude 専用の枝 ………… 5 (send_keys_verified / retry / verify再送 / idle×2)
#         ★⑶ は本改修で ★一字も変えて居らぬ★ = 稼働中 9本の watcher を壊さぬ為。
#           ∴ claude 路は ★直っておらぬ既知の穴★ に御座る (票 §3-4)。
#    数が動いたら ★人が棚卸しを見直す★ 事。自動で通してはならぬ。
#    (本 tripwire は現に働き申した: 12→13 の増を検出し 実装者に棚卸しを改めさせた)
# ══════════════════════════════════════════════════════════════════
@test "N12: C-u 送出点の数が棚卸しから動いて居らぬ" {
    local n
    n=$(grep -c 'timeout [0-9]* tmux send-keys -t "\$\(PANE_TARGET\|pane\)" C-u' "$WATCHER" || true)
    [ "$n" = "13" ] || {
        echo "FAIL: C-u 送出点=$n (棚卸し 13)。増減したなら 各点が門を通るか人が検めよ"
        grep -n 'timeout [0-9]* tmux send-keys -t "\$\(PANE_TARGET\|pane\)" C-u' "$WATCHER"
        return 1
    }
}

# ══════════════════════════════════════════════════════════════════
# N13 ★send_cli_command 階層での門の実効★ (TC-FR-009 mock 緩和の対価)
#    tests/agent_selfwatch.bats TC-FR-009 の mock へ「空 composer を持つ pane」を
#    与えた (= 門を通す) 事の★対価★として、其の一つ上の階層で
#    「書きかけ在らば /new は撃たれぬ」を此処に固定する。
#    → 之が無ければ「mock を緩めて緑にした」だけに成り申す。
#    何が起きたら PASS と書いてはならぬか:
#      ・書きかけ在るに rc=0 で返る
#      ・書きかけ在るに "/new" か "x" が 1 つでも送出される
# ══════════════════════════════════════════════════════════════════
@test "N13: 書きかけ在る pane へ send_cli_command /clear は /new も x も撃たぬ" {
    local harness="$BATS_TEST_TMPDIR/h13.sh"
    cat > "$harness" <<EOF
AGENT_ID="t"; PANE_TARGET="test:0.0"; CLI_TYPE="codex"
INBOX="\$BATS_TEST_TMPDIR/in.yaml"; LOCKFILE="\$INBOX.lock"
SCRIPT_DIR="$REPO"; IDLE_FLAG_DIR="\$BATS_TEST_TMPDIR"
tmux() {
    echo "tmux \$*" >> "\$SENT13"
    if echo "\$*" | grep -q capture-pane; then printf '%s\n' " ❯ [本部長 downlink] pc_handshake seq=155925"; return 0; fi
    return 0
}
timeout() { shift; "\$@"; }
sleep() { :; }
pgrep() { return 1; }
export -f tmux timeout sleep pgrep
export __INBOX_WATCHER_TESTING__=1
source "$WATCHER"
EOF
    export SENT13="$BATS_TEST_TMPDIR/sent13.log"; : > "$SENT13"
    echo 'messages: []' > "$BATS_TEST_TMPDIR/in.yaml"

    run bash -c "source '$harness'; send_cli_command /clear"
    [ "$status" -ne 0 ] || { echo "FAIL: 書きかけ在るに rc=0 (=撃った)"; return 1; }

    if grep -q 'send-keys -t test:0.0 /new' "$SENT13"; then
        echo "FAIL: 書きかけ在るに /new を撃った"; cat "$SENT13"; return 1
    fi
    if grep -q 'send-keys -t test:0.0 x' "$SENT13"; then
        echo "FAIL: 書きかけ在るに \"x\" を撃った (之も composer を汚す)"; cat "$SENT13"; return 1
    fi
    if grep -q 'C-u' "$SENT13"; then
        echo "FAIL: 書きかけ在るに C-u を撃った (draft 消滅)"; cat "$SENT13"; return 1
    fi
}
