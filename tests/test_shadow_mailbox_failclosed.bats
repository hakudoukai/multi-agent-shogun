#!/usr/bin/env bats
# test_shadow_mailbox_failclosed.bats — leg C (subtask_shadow_failclosed_legC_a3_20260805)
#
# 発令書: docs/incident_logs/2026-08-05_order_shadow_mailbox_failclosed.md
# 出所: 委員長殿裁定 → 将軍second 中継 msg_20260805_102826_17770d10 → karo-second
#
# 背景: `ashigaru-second-1〜7` という canon 外の宛名に、影の inbox file が七本存在した。
# 影の watcher が消えた今 (08-05 09:2x〜09:36)、影の名宛に書いても nudge すら出ぬ =
# 完全に無音で届かぬ。現に `ashigaru-second-1.yaml` の from=shogun context 警告が
# read:false のまま17時間滞留していた実物がある。scripts/inbox_write.sh は現在
# TARGET を検証せず、canon 外の宛名でも黙って書き込みを成功させる (本テスト群が
# 検出する欠陥そのもの)。
#
# 本ファイルは leg B (ashigaru2, blocked_by=leg C) が満たすべき契約を
# 「実行可能な失敗する試験」として先に固定する。委員長殿の四形 (a)(b)(c)(d) に対応。
# 実装前ゆえ (a)(c)(d) は赤で正しい。(b) は既存配送を壊していない事の陽性対照で
# 今も緑であるべき。
#
# ── leg B が実装すべき契約 (このテストが定義する仕様) ──
# ★軍師second 監査 FAIL 是正 (2026-08-05・karo-second 中継)★:
#   実 `queue/pane_registry.yaml` は ★top-level `pane_registry:` の下に `panes:` が一段★
#   (`panes[].agent_id` ではなく ★`pane_registry.panes[].agent_id`★)。誤記のまま実装すれば
#   全宛先が非canonと誤判定され fail-closed で配送が全断する。以下 1. を訂正し、
#   SMFC-SCHEMA1/SMFC-SCHEMA2 (末尾) で ★この path/形状そのものを機械固定★ する
#   (記述の訂正だけでは「誤りが露見せぬ事」は閉じぬ、との指摘に対応)。
#   ★但し書き★: `ashigaru1/2/3` は MainPC分・SecondPC分で agent_id が★二重に存在★する。
#   本契約は「canon か否か (集合の帰属)」の判定にのみ registry を用いる —
#   ★名 → 特定 pane への一意対応には使わぬ・使えぬ★ (leg B は一意対応を前提に組んではならぬ)。
#
# 1. canon 宛先集合 = `<SCRIPT_DIR>/queue/pane_registry.yaml` の
#    ★`pane_registry.panes[].agent_id`★ (トップレベルキー `pane_registry:` の下の `panes:`)
#    (env `INBOX_WRITE_CANON_REGISTRY` で上書き可能 — detector-dead 疑似のため)。
# 2. TARGET が canon 外 → exit 非0・`queue/inbox/<TARGET>.yaml` は書かれない (fail-closed)。
#    ★2026-08-05 是正三点目 (将軍second 具申・karo-second 実測裏付け・leg A の実地失敗が
#    契機)★: 「FROM が canon 内」だけでは不十分。実測 (registry 全16名×inbox突合) で
#    ★16名中5名が canon でありながら実質配送不能★と判った (箱 file 不在=honda/sanada、
#    空箱のまま長期停滞=shogun/gunshi/takenaka、書込はあるが長期停滞=karo)。
#    ★∴ 「canon か否か」ではなく「読む者が居るか」を問え★ —— さもなくば返送便自体が
#    影の箱と同じ運命 (無音消失) を辿る (足軽3号の (d)「検出器が死んでいた」の配送側の双子)。
#
#    ★2026-08-05 軍師second 再監査 FAIL (二度目・karo-second 実測裏付け) 是正★:
#    ⑴ ★mtime は代理に成らぬ★ — mtime は write で進み read では進まぬ。かつ fail-closed の
#       返送そのものが mtime を更新し得るため「書かれた事」を「読まれた事」と取り違える
#       循環を開く (本件の主題そのもの)。∴ mtime 判定を撤回し、★resolvable FROM の定義★
#       を「canon ★かつ★ FROM の inbox に read:true の便が★1件以上★あり、その中の
#       最新 timestamp が閾値 (`INBOX_WRITE_STALE_READER_SECONDS`、env 上書き可) 以内」へ
#       差し替える。timestamp は既存 message 書式と同じ naive local (`%Y-%m-%dT%H:%M:%S`)、
#       leg B 側は同じ naive local `datetime.now()` と比較せよ (tz 変換すると噛み合わぬ)。
#       ★read:false の便 (delivery_failed 返送含む) は一切この判定に寄与しない★ —
#       これが循環を断つ核心 (新着の未読がいくら積もっても「読まれた証」にはならぬ)。
#       (file 不在や messages が空の場合は read:true が0件ゆえ自動的に resolvable でない)。
#    ⑵ ★`queue/dead_letter/_unroutable/` 単体は「新たな静かな墓場」になり得る★ —
#       karo-second 実測で当該 dir は本日 5/8 作成の空 dir であり、常時読む者は無い
#       (`scripts/diagnose.sh` は求められた時のみ・他は archive の死んだ v2 script のみ)。
#       ★かつ escalate 先をどこへ変えても同じ問いが入れ子で付きまとう★
#       (file である限り「その file を誰が読むか」は再帰的に問われる)。
#       ★∴ 唯一 墓場に成り得ぬ終端は「呼び手への戻り値」★ —— 呼び手は構造上必ずその瞬間
#       走っているため、非zero exit + stderr は必ず届く。★本契約における「記録して上げる」
#       の主契約(load-bearing)は非zero exit + stderr の明示印 (`UNROUTABLE_ESCALATED`、
#       TARGET と FROM を含む) とする★。`queue/dead_letter/_unroutable/` への書込は
#       ★補助的な法医学的記録として引き続き要求する★が、それ単体が「誰かに読まれる事」を
#       保証するとは主張しない — その保証 (定期的な sweep/監視) は本 leg / inbox_write.sh
#       単体の scope 外であり、別途の運用課題として明示的に積み残す。
#    - FROM が canon 内 ★かつ★ 上記の意味で resolvable → FROM 自身の inbox へ
#      type=delivery_failed の返送便 (内容に「宛先不明」「<TARGET>」
#      「照合できる有効な宛先の一例 (例: ashigaru1)」を含む)。
#    - FROM が canon 外、★または★ canon だが resolvable でない (file 不在/read:trueが
#      無い/stale) → 黙って消さず non-zero exit + stderr に `UNROUTABLE_ESCALATED`
#      (TARGET・FROM 双方を含む) を出し、かつ `queue/dead_letter/_unroutable/` 配下に
#      TARGET/FROM 双方を含む記録を補助的に新規に残す (委員長殿 leg 記述 (c))。
# 3. canon 判定源 (registry) が読めぬ時は fail-closed (allow ではなく reject) し、
#    stderr に検出器不能である旨の印 (例: `DETECTOR_UNAVAILABLE`) を出す。
# 4. canon 内 TARGET を検証OKで通す時も、stderr に「検証を実行しOKだった」事を示す
#    印 (例: `canon_check` と `OK` の両方) を残す — 「0件の成功顔」を「未検査」から
#    区別する為 (委員長殿 (d))。

setup_file() {
    export PROJECT_ROOT
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)"
    export VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"
    export INBOX_WRITE_SCRIPT="$PROJECT_ROOT/scripts/inbox_write.sh"
    export REAL_PANE_REGISTRY="$PROJECT_ROOT/queue/pane_registry.yaml"

    [ -f "$INBOX_WRITE_SCRIPT" ] || return 1
    [ -f "$REAL_PANE_REGISTRY" ] || return 1
    "$VENV_PYTHON" -c "import yaml" 2>/dev/null || return 1
}

setup() {
    export TEST_TMPDIR
    TEST_TMPDIR="$(mktemp -d "$BATS_TMPDIR/shadow_failclosed_test.XXXXXX")"

    # 同一技法 (tests/test_inbox_write.bats): SCRIPT_DIR を sandbox へ retarget した写しを作る。
    # ★実 repo の scripts/inbox_write.sh 自体は 1文字も書き換えぬ★ (read-only 検証)。
    export TEST_SCRIPT_DIR="$TEST_TMPDIR/scripts_root"
    mkdir -p "$TEST_SCRIPT_DIR"
    sed "s|SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")/..*|SCRIPT_DIR=\"$TEST_TMPDIR\"|" \
        "$INBOX_WRITE_SCRIPT" > "$TEST_SCRIPT_DIR/inbox_write.sh"
    chmod +x "$TEST_SCRIPT_DIR/inbox_write.sh"
    ln -sf "$PROJECT_ROOT/.venv" "$TEST_TMPDIR/.venv"

    export TEST_INBOX_WRITE="$TEST_SCRIPT_DIR/inbox_write.sh"
    export TEST_INBOX_DIR="$TEST_TMPDIR/queue/inbox"
    mkdir -p "$TEST_INBOX_DIR"

    # 実 registry の写し (読取専用参照。canon 判定源として使わせる — 実 file は不触)。
    mkdir -p "$TEST_TMPDIR/queue"
    cp "$REAL_PANE_REGISTRY" "$TEST_TMPDIR/queue/pane_registry.yaml"

    # cross-PC bridge を無効化 (本試験は local 配送の是非のみを見る)
    export HOME_ORIG="$HOME"
    export HOME="$TEST_TMPDIR/fake_home"
    mkdir -p "$HOME/.openclaw"
    touch "$HOME/.openclaw/disable_cross_pc_bridge"
}

teardown() {
    export HOME="$HOME_ORIG"
    rm -rf "$TEST_TMPDIR"
}

# =============================================================================
# (b) 正しい宛名へ送る → 届く = ★陽性対照★ (実装前後を通じて常に緑であるべき)
# =============================================================================
@test "SMFC-B: valid canon target (ashigaru1) is delivered unchanged (positive control)" {
    run bash "$TEST_INBOX_WRITE" "ashigaru1" "leg-C positive control message" "notification" "shogun-second"
    [ "$status" -eq 0 ]
    [ -f "$TEST_INBOX_DIR/ashigaru1.yaml" ]

    "$VENV_PYTHON" - << PY
import yaml
with open("$TEST_INBOX_DIR/ashigaru1.yaml") as f:
    data = yaml.safe_load(f)
msgs = data["messages"]
assert any(m["content"] == "leg-C positive control message" for m in msgs), msgs
print("SMFC-B: PASS")
PY
}

# =============================================================================
# (a) 影の宛名へ送る → 受理されず、送り主へ返る (FROM は canon 内)
# =============================================================================
@test "SMFC-A1: shadow target (ashigaru-second-1) is rejected, not silently written" {
    run bash "$TEST_INBOX_WRITE" "ashigaru-second-1" "stale w141 context warning" "notification" "shogun-second"
    [ "$status" -ne 0 ]
    # ★fail-closed の核心★: 影 file が新規に書かれてはならぬ (受理された痕跡ゼロ)。
    [ ! -f "$TEST_INBOX_DIR/ashigaru-second-1.yaml" ]
}

@test "SMFC-A2: shadow target rejection is returned to a resolvable (canon + evidenced-read) FROM's own inbox" {
    # ★軍師second 再監査 FAIL 是正★: 「読む者が居る」の証拠は mtime ではなく
    # ★read:true の便が実在し、その timestamp が新しい事★ (mtime は write でも進むため
    # fail-closed の返送それ自体が偽の生存証を作ってしまう循環に陥る)。
    # 5分前 (閾値内) を read:true で用意する — 見せかけの陽性対照を避ける為、
    # 自動生成に任せず「予め本当に読まれた便」を明示的に用意する。
    RECENT_TS=$(date -d "-5 minutes" "+%Y-%m-%dT%H:%M:%S")
    cat > "$TEST_INBOX_DIR/shogun-second.yaml" << YAML
messages:
- id: msg_preexisting_live
  from: karo-second
  timestamp: "${RECENT_TS}"
  type: status_update
  content: pre-existing read message proving an active reader
  read: true
YAML

    run bash "$TEST_INBOX_WRITE" "ashigaru-second-1" "stale w141 context warning" "notification" "shogun-second"
    [ "$status" -ne 0 ]

    [ -f "$TEST_INBOX_DIR/shogun-second.yaml" ]
    "$VENV_PYTHON" - << PY
import yaml
with open("$TEST_INBOX_DIR/shogun-second.yaml") as f:
    data = yaml.safe_load(f)
msgs = data.get("messages") or []
notice = [m for m in msgs if m.get("type") == "delivery_failed"]
assert notice, f"no delivery_failed return-notice found: {msgs}"
body = notice[-1]["content"]
assert "宛先不明" in body, body
assert "ashigaru-second-1" in body, body
# ★照合できる情報を添えよ★ (発令書 §5) — 有効な宛先が最低一例挙がっている事。
assert "ashigaru1" in body, body
print("SMFC-A2: PASS")
PY
}

# =============================================================================
# (c) 返送先が不明な便 → 黙って捨てず、記録して上げる (FROM も canon 外)
# =============================================================================
@test "SMFC-C: unroutable target AND unresolvable FROM is escalated, not silently dropped" {
    run bash "$TEST_INBOX_WRITE" "ashigaru-second-9" "orphaned message, no valid return path" "notification" "ghost_unknown_sender_zzz"
    [ "$status" -ne 0 ]

    # 影の宛先へ書かれてもおらず
    [ ! -f "$TEST_INBOX_DIR/ashigaru-second-9.yaml" ]
    # 存在せぬ送り主の inbox を勝手に作って押し込んでもいない (それ自体が新たな影 file になる)
    [ ! -f "$TEST_INBOX_DIR/ghost_unknown_sender_zzz.yaml" ]

    # ★軍師second 再監査 是正★: 「記録して上げる」の主契約 (load-bearing) は
    # ★呼び手への戻り値★ (呼び手は構造上その瞬間 必ず走っており、file と違い墓場に
    # 成り得ぬ)。stderr に TARGET/FROM 双方を含む明示印を要求する。
    [[ "$output" =~ UNROUTABLE_ESCALATED ]]
    [[ "$output" =~ "ashigaru-second-9" ]]
    [[ "$output" =~ "ghost_unknown_sender_zzz" ]]

    # dead-letter への記録は ★補助的な法医学的記録★ として引き続き要求する
    # (それ単体が「誰かに読まれる事」を保証するとは主張しない — 上記 stderr が主契約)。
    ESCALATION_DIR="$TEST_TMPDIR/queue/dead_letter/_unroutable"
    [ -d "$ESCALATION_DIR" ]
    MATCH=$(/usr/bin/grep -rl "ashigaru-second-9" "$ESCALATION_DIR" 2>/dev/null | head -1)
    [ -n "$MATCH" ]
    /usr/bin/grep -q "ghost_unknown_sender_zzz" "$MATCH"
}

# =============================================================================
# (c) 拡張 — 2026-08-05 是正三点目 (将軍second 具申・karo-second 実測裏付け):
# 「返送先不明」は ★canon 外★ だけでは尽きぬ。leg A (ashigaru5) の実地失敗
# (元送り主 `shogun` の inbox が実在するが 0通・最終書込 07-02) が示した通り、
# FROM が canon ★であっても★ 読む者が居ぬ箱へ返送便を書けば、影の箱と同じ
# 「無音消失」を再生産する。∴ 「file 不在」「read:true の便が一件も無い/古い (停滞)」
# の両方を (c) の「返送先不明」に含め、escalate せねばならぬ (2026-08-05 再監査是正済:
# 判定は file の mtime ではなく ★message の read:true + その timestamp★ で行う)。
# =============================================================================

@test "SMFC-C2: canon FROM whose inbox file has never been created (no reader ever) is treated as unresolvable, escalated" {
    # `honda`/`sanada` 実測 (karo-second 10:5x) を模す: canon だが inbox file 自体が無い。
    [ ! -f "$TEST_INBOX_DIR/honda.yaml" ]

    run bash "$TEST_INBOX_WRITE" "ashigaru-second-2" "orphaned message, canon FROM but no box ever created" "notification" "honda"
    [ "$status" -ne 0 ]

    # 影の宛先へも書かれず、かつ「初めての箱」を勝手に作って返送便を押し込んでもいない。
    [ ! -f "$TEST_INBOX_DIR/ashigaru-second-2.yaml" ]
    [ ! -f "$TEST_INBOX_DIR/honda.yaml" ]

    [[ "$output" =~ UNROUTABLE_ESCALATED ]]
    [[ "$output" =~ "ashigaru-second-2" ]]
    [[ "$output" =~ "honda" ]]

    ESCALATION_DIR="$TEST_TMPDIR/queue/dead_letter/_unroutable"
    [ -d "$ESCALATION_DIR" ]
    MATCH=$(/usr/bin/grep -rl "ashigaru-second-2" "$ESCALATION_DIR" 2>/dev/null | head -1)
    [ -n "$MATCH" ]
    /usr/bin/grep -q "honda" "$MATCH"
}

@test "SMFC-C3: canon FROM with read:true history but stale (latest read timestamp beyond threshold — 'was active, now stopped') is unresolvable, escalated" {
    # `karo` 実測 (karo-second 10:5x・39/40通既読・最終既読 07-08=約1ヶ月停滞) を模す:
    # 過去には読まれていたが、直近の read:true が無い ∴ 現在「読む者が居る証拠」は無い。
    OLD_TS=$(date -d "-40 days" "+%Y-%m-%dT%H:%M:%S")
    cat > "$TEST_INBOX_DIR/gunshi.yaml" << YAML
messages:
- id: msg_long_ago_read
  from: karo-second
  timestamp: "${OLD_TS}"
  type: status_update
  content: was read once, long ago
  read: true
YAML

    INBOX_WRITE_STALE_READER_SECONDS=86400 \
        run bash "$TEST_INBOX_WRITE" "ashigaru-second-3" "orphaned message, canon FROM but stale reader history" "notification" "gunshi"
    [ "$status" -ne 0 ]

    [ ! -f "$TEST_INBOX_DIR/ashigaru-second-3.yaml" ]
    # 停滞していた箱へ、この試験を理由に新規便が書き込まれてはならぬ (元の1通のみのまま)。
    "$VENV_PYTHON" - << PY
import yaml
with open("$TEST_INBOX_DIR/gunshi.yaml") as f:
    data = yaml.safe_load(f)
msgs = data.get("messages") or []
assert len(msgs) == 1 and msgs[0]["id"] == "msg_long_ago_read", f"stale mailbox must not receive the notice: {msgs}"
print("SMFC-C3 (no-write-to-stale-box): PASS")
PY

    [[ "$output" =~ UNROUTABLE_ESCALATED ]]
    [[ "$output" =~ "ashigaru-second-3" ]]
    [[ "$output" =~ "gunshi" ]]

    ESCALATION_DIR="$TEST_TMPDIR/queue/dead_letter/_unroutable"
    [ -d "$ESCALATION_DIR" ]
    MATCH=$(/usr/bin/grep -rl "ashigaru-second-3" "$ESCALATION_DIR" 2>/dev/null | head -1)
    [ -n "$MATCH" ]
    /usr/bin/grep -q "gunshi" "$MATCH"
}

@test "SMFC-C4: fresh UNREAD traffic in FROM's inbox must NOT count as reader evidence (closes the mtime-style circularity at the message level)" {
    # ★軍師second 再監査 FAIL の核心★: mtime を捨てても「直近の message timestamp
    # (read 状態を問わず)」を見てしまえば同じ循環が message level で再発する。
    # ∴ 直近だが read:false の便★だけ★を持つ FROM (=誰かが書いたが誰も読んでおらぬ)
    # は、read:true が無いのと同じく unresolvable でなければならぬ。
    RECENT_TS=$(date -d "-1 minutes" "+%Y-%m-%dT%H:%M:%S")
    cat > "$TEST_INBOX_DIR/takenaka.yaml" << YAML
messages:
- id: msg_fresh_but_unread_1
  from: karo-second
  timestamp: "${RECENT_TS}"
  type: status_update
  content: freshly written but nobody has read it yet
  read: false
- id: msg_fresh_but_unread_2
  from: shogun-second
  timestamp: "${RECENT_TS}"
  type: notification
  content: another fresh unread message
  read: false
YAML

    run bash "$TEST_INBOX_WRITE" "ashigaru-second-4" "orphaned message, FROM has only fresh unread traffic" "notification" "takenaka"
    [ "$status" -ne 0 ]

    [ ! -f "$TEST_INBOX_DIR/ashigaru-second-4.yaml" ]
    # 既存の2通の read:false は変えられておらず、delivery_failed も追記されていない
    # (=fresh-but-unread を根拠に「resolvable」と誤判定して書き込んでいない証)。
    "$VENV_PYTHON" - << PY
import yaml
with open("$TEST_INBOX_DIR/takenaka.yaml") as f:
    data = yaml.safe_load(f)
msgs = data.get("messages") or []
assert len(msgs) == 2, f"fresh-but-unread mailbox must not receive the notice: {msgs}"
assert all(not m.get("read", False) for m in msgs), msgs
print("SMFC-C4 (fresh-unread-does-not-count): PASS")
PY

    [[ "$output" =~ UNROUTABLE_ESCALATED ]]
    [[ "$output" =~ "ashigaru-second-4" ]]
    [[ "$output" =~ "takenaka" ]]

    ESCALATION_DIR="$TEST_TMPDIR/queue/dead_letter/_unroutable"
    [ -d "$ESCALATION_DIR" ]
    MATCH=$(/usr/bin/grep -rl "ashigaru-second-4" "$ESCALATION_DIR" 2>/dev/null | head -1)
    [ -n "$MATCH" ]
    /usr/bin/grep -q "takenaka" "$MATCH"
}

# =============================================================================
# (d) 何も無い時に何と言うか — ★零件を「成功の顔」で返すな★
#     「該当なし(健全)」と「検査していない」と「検出器が死んでいた」を区別可能にする。
# =============================================================================
@test "SMFC-D1: healthy zero-violation accept leaves an explicit canon-check-ran marker" {
    run bash "$TEST_INBOX_WRITE" "ashigaru1" "healthy accept, canon check should have run" "notification" "shogun-second"
    [ "$status" -eq 0 ]
    # ★「通った」だけでなく「検証した上で通した」事が読み取れねばならぬ★ —
    # そうでなければ「該当なし」と「そもそも検査していない (今の欠陥そのもの)」が
    # 見分けが付かぬ。
    [[ "$output" =~ canon_check ]]
    [[ "$output" =~ OK ]]
}

@test "SMFC-D2: canon registry unreadable → fail-closed reject with a detector-dead marker (not a silent allow)" {
    # canon 判定源そのものを壊す (detector dead を模す) — allow へ倒れてはならぬ。
    INBOX_WRITE_CANON_REGISTRY="$TEST_TMPDIR/queue/does_not_exist.yaml" \
        run bash "$TEST_INBOX_WRITE" "ashigaru1" "registry unreadable at check time" "notification" "shogun-second"
    [ "$status" -ne 0 ]
    [ ! -f "$TEST_INBOX_DIR/ashigaru1.yaml" ]
    [[ "$output" =~ DETECTOR_UNAVAILABLE ]]
}

# =============================================================================
# SCHEMA — 軍師second 監査 FAIL 是正 (2026-08-05): canon 出所の path/形状そのものを
# 機械固定する (記述を直すだけでは「誤りが露見せぬ事」は閉じぬ、との指摘への対応)。
# =============================================================================

# SMFC-SCHEMA1: 実 registry と同じ「トップレベルキーが違う」形 (pane_registry: の
# 一段が無く、panes: がいきなり top-level) を canon 判定源に与えた場合、
# ★正しい path (pane_registry.panes[].agent_id) では見えぬ★ ため、fail-closed で
# 拒否されねばならぬ (「形は近いが違う物」を誤って canon 扱いしない事の証明)。
@test "SMFC-SCHEMA1: wrongly-shaped registry (flat top-level panes:, no pane_registry: wrapper) is NOT accepted as canon source" {
    cat > "$TEST_TMPDIR/queue/wrongshape_registry.yaml" << 'YAML'
panes:
- tmux_target: test:0.0
  agent_id: ashigaru1
YAML
    INBOX_WRITE_CANON_REGISTRY="$TEST_TMPDIR/queue/wrongshape_registry.yaml" \
        run bash "$TEST_INBOX_WRITE" "ashigaru1" "wrong-shape registry must not leak through" "notification" "shogun-second"
    [ "$status" -ne 0 ]
    [ ! -f "$TEST_INBOX_DIR/ashigaru1.yaml" ]
}

# SMFC-SCHEMA2: canon 判定は「真に override された registry の内容」で決まらねばならぬ
# ——(i) real repo には存在せぬ新規名でも、正しい形 (pane_registry.panes[].agent_id) の
# override に載っていれば受理される (= 実際にこの path から読んでいる証)。
# (ii) real repo では有効な `ashigaru1` でも、override にその名が無ければ拒否される
# (= real registry や固定リストへ黙って fallback していない証)。
# 両方が同時に成り立って初めて、path/形状が真に機械固定されたと言える。
@test "SMFC-SCHEMA2: canon set is driven by the actual overridden registry content, not a hardcoded/fallback list" {
    cat > "$TEST_TMPDIR/queue/custom_registry.yaml" << 'YAML'
pane_registry:
  panes:
  - tmux_target: test:0.9
    agent_id: totally_novel_test_agent_xyz
YAML

    # (i) override 内にのみ在る新規名 → 受理されねばならぬ。
    INBOX_WRITE_CANON_REGISTRY="$TEST_TMPDIR/queue/custom_registry.yaml" \
        run bash "$TEST_INBOX_WRITE" "totally_novel_test_agent_xyz" "novel canon name from override" "notification" "shogun-second"
    [ "$status" -eq 0 ]
    [ -f "$TEST_INBOX_DIR/totally_novel_test_agent_xyz.yaml" ]

    # (ii) real repo では有効だが override には無い名 → 拒否されねばならぬ。
    INBOX_WRITE_CANON_REGISTRY="$TEST_TMPDIR/queue/custom_registry.yaml" \
        run bash "$TEST_INBOX_WRITE" "ashigaru1" "must not fall back to real/default registry" "notification" "shogun-second"
    [ "$status" -ne 0 ]
    [ ! -f "$TEST_INBOX_DIR/ashigaru1.yaml" ]
}
