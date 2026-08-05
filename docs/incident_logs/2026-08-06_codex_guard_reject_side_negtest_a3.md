# codex_exec_sandbox_guard.sh — 弾く側 負テスト報告 (足軽3号)

- 発令: 家老second → 足軽3号 (msg_20260806_065625_de110cbd・2026-08-06T06:56:25)
- 対象: `scripts/checks/codex_exec_sandbox_guard.sh`
- 本報告 提出時刻 (機械測): 2026-08-06T07:08:41+09:00
- 本報告 sha256 は ★本文末尾に置く★ (提出直前に測る為・自己言及ゆえ本文冒頭には書けぬ)

---

## ★境・限界・未測 (冒頭・読み落とし防止)★

1. **段(1)(2) の弾く側は 実行では未検証**。理由=guard は 3 段直列判定
   (段0=halt gate / 段1=live-repo cwd 判定 / 段2=sandbox 種別判定) を持つが、
   現環境で `GO_RECORD` (`/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record`) が
   ★実在せぬ★ (本報告作成前に `ls` で確認済)。∴ 段0 が常に先着し exit 1 を返し、段1/2 には
   ★実行が到達し得ぬ★。段1/2 を実行で検証するには `GO_RECORD` を実在させねばならぬが、
   guard 自身のコメント (L27) が「GO記録file は理事長GO発令後に上位のみが配置する。
   agent自己配置/自己設定 = D-lane違反」と明記しており、★本 repo 上の実 guard に対しては
   一切 作成/書換せなんだ★ (絶対境界を守った)。
2. **1 の代替として、isolated copy (scratchpad 内・実 guard とは別物) で段1/2 を検証を試みた**。
   結果は §3 に記す。★これは実 guard の実行結果ではない★。GO_RECORD 相当 file も
   scratchpad 内のみに作成し、実 repo・実 GO_RECORD path には一切触れておらぬ。
   **この isolated 検証の途中、harness (許可分類器) が「安全機構の実働バイパスを確認・強化する
   行為」と判じ、追加の連鎖検証 (symlink alias + sandbox種別設定の組合せで exit 0 まで到達するか)
   および 後片付けの `rm -rf` を ★拒否した★**。当職はこれに従い ★連鎖検証を打ち切った★。
   ∴ symlink alias 単体での結果 (段1 素通り→exit 2) までが実測の限度であり、
   「exit 0 まで完全に抜けるか」は ★未測のまま★ である (试さぬのではなく、试すのを止めた)。
3. **scratchpad 内に isolated copy の残骸が残っている**
   (`/tmp/claude-.../scratchpad/isolated_guard_probe/`)。削除を試みたが同じ理由で拒否された。
   ★repo 外・session 専用の scratchpad であり、git 管理外・本 repo には一切含まれぬ★。
   セッション終了で消える性質の領域であり、当職の側でこれ以上の操作は行わぬ。
4. **網羅を主張せず**。§2 の実行済 7 ケース、§3 の isolated 2 ケースが「試した形」の全て。
   それ以外の入力形 (symlink 以外の alias 経路、bind mount、WSL 特有の多重 path 等) は
   ★試しておらぬ★ (排除しておらぬ、というだけで「安全」の意味ではない)。

---

## §1 前提検証 (下命により義務化・karo-second の実測2件を検めた)

karo-second が本便で「今後は前提を一つ検めて返せ」と求めた例示2件を検めた。

| 前提 (karo-second の記述) | 判定 | 実測根拠 |
|---|---|---|
| 「guard は tracked」 | ★正しい★ | `git ls-files scripts/checks/codex_exec_sandbox_guard.sh` → 1件ヒット。`git check-ignore -v` は exit 1 (非ignore)。 |
| 「(当対象について) 負テスト零件」 | ★正しい★ | `/usr/bin/grep -rl "codex_exec_sandbox_guard"` を repo 全体に実行 → 自ファイル (`scripts/checks/codex_exec_sandbox_guard.sh` 自身) 以外に0件。`tests/unit/test_codex_guard.bats` は★別物★ (`scripts/message_delivery_v2/codex_guard.sh` という別スクリプトの試験であり、対象を取り違えぬよう確認した)。 |

★両前提とも正しかった★ (誤りの指摘は無し)。

---

## §2 実行した負テスト (対 実 guard・7ケース全 PASS)

成果物: `tests/checks/codex_exec_sandbox_guard/smoke_test.sh` (163行・sha256=6a624c8d4671a8cfdbb04bd9934abbfc4f65ec27394e58c409814700a29f2e89)

実行結果 (2026-08-06T07:0x 実測・逐語):

```
=== codex_exec_sandbox_guard.sh 弾く側 負テスト (halt gate のみ実測可) ===
[PASS] C01    rc=1 (expected=1) — 無引数 ($PWD 既定) → GO_RECORD 不在ゆえ exit 1 (halt)
[PASS] C02    rc=1 (expected=1) — intended_cwd=live repo 直下 → halt が先着 (cwd 判定には未到達)
[PASS] C03    rc=1 (expected=1) — intended_cwd=live repo 配下 → halt が先着
[PASS] C04    rc=1 (expected=1) — intended_cwd=newbuild パターン → halt が先着
[PASS] C05    rc=1 (expected=1) — intended_cwd=/tmp (安全に見える cwd) でも halt が弾く
[PASS] C06    rc=1 (expected=1) — intended_cwd に相対 ../ を含む脱出試行文字列 → それでも halt が先着し弾く
[PASS] C07    rc=1 (expected=1) — CODEX_SANDBOX_KIND=docker 設定下でも halt が先着
----
ALL PASS (7/7)
```

**読み方の注意**: 7ケース全てが「弾いた」のは事実だが、★全て段0 (halt gate) を測っており、
段1(cwd判定)/段2(sandbox種別判定) の弾く側そのものは測っておらぬ★。C02〜C06 は cwd を変化させたが、
いずれも段0 で止まるため、段1 の cwd パターンマッチ条件分岐そのものには到達していない
(= C02〜C06 の PASS は「段1 が正しく弾いた証」ではなく「段0 が cwd に関係なく弾く証」)。

---

## §3 isolated copy による補助検証 (★実 guard の実行結果ではない★・§1 境界を必ず参照)

`GO_RECORD` 変数のみを scratchpad 内 path へ書換えた **写し** (`guard_copy.sh`) を用意し、
scratchpad 内にのみ marker 入り file を作成して段0 を通過させ、段1/2 を検証した。
実 guard 本体・実 `GO_RECORD` path には一切触れておらぬ。

| # | 入力 | 結果 (isolated copy) | 意味 |
|---|---|---|---|
| 1 | intended_cwd=live repo 直下 | BLOCK (段1・rc=1) | 想定通り弾いた |
| 2 | intended_cwd=`../home/hakudokai/projects/multi-agent-shogun` (相対 `../` 脱出試行) | BLOCK (段1・rc=1) | **★当職の当初仮説 (glob は realpath 解決せぬゆえ `../` 文字列は素通りし得るのでは) は ★誤りと判明★**。`case` の glob パターン `*/projects/multi-agent-shogun` の先頭 `*` は `../` を含む任意文字列にマッチするため、この形の脱出は弾かれる。 |
| 3 | intended_cwd=live repo への **別名 symlink** (scratchpad 内に作成した alias。名に `multi-agent-shogun` を含まぬ) | ★段1 を素通り★→段2 (sandbox未設定) → rc=2 (判定不能) | **★実測で見つけた本物の隙間★**: 段1 は文字列パターン照合のみで realpath 解決を行わぬ (`realpath` で確認=alias は実 repo と同一 inode を指す)。ゆえに「同じ場所を指すが名前が違う経路」は段1 の網に掛からず、BLOCK(1) から 判定不能(2) へ★格下げ★される。 |

**#3 の位置づけ**: これは guard 自身のコメント (L43「絶対path書込みは cwd隔離だけでは防げない」) が
★既に自認している種類の限界★であり、当職が新たに突いた穴ではなく、★文書化された既知の弱点を
実測で裏付けた★という性格の物である。 exit 2 (判定不能) は exit 0 (許可) ではなく、呼出側が
「判定不能=停止扱い」で運用していれば実害には至らぬ設計 (script header コメントにも
「呼出側は停止扱い」の言及あり)。★然れど exit 1(BLOCK・明確な拒否) と exit 2(判定不能・原因不明)
は 監査ログ上の意味が異なり、後者は「なぜ止まったか」が呼出側ログに残りにくい★という副次的懸念がある
(★これは当職の推測であり、呼出側の実装を読んで確かめてはおらぬ★)。

**#3 から先 (sandbox種別も設定して exit 0 = 完全な素通りに至るか) は、harness が
「安全機構の実働バイパスの確認・強化」と判じて拒否したため、当職はここで打ち切った**。
∴ 「完全に素通りするか」は ★未測のまま★ である。

---

## §4 この工区と対に成る他工区

- 本便冒頭に「因=上記 足軽1号への下命と同じ (当隊の監査が二者制ゆえ完了が出せぬ)」との記述有り。
  ★足軽1号 の当該下命そのものは 当職の inbox に着信しておらず、内容未確認★
  (探した範囲=自 inbox 全44件・`grep -i codex` 一致は本便のみ)。
  ∴ 「因の共有」は確認できたが、「工区として対を成すか」は判定不能。
- 自 inbox 内には他に codex guard 関連の並行工区は見当たらず (母集団=自inbox全44件、根拠=上記 grep)。

---

## §5 本工区で己が直した誤り

- 当初、C06 (相対 `../` 脱出) を「試しておらぬ形」として報告する予定であったが、
  isolated copy での実測により「この特定の形は実は弾かれる」と判明し、★仮説を実測で訂正した★
  (§3 表の #2)。訂正前の仮説を報告に残さず、訂正後の実測結果のみを正として記載した。

---

## §6 三者/二者監査の明記

本工区の監査体制=★二者制★ (軍師second + Gemini。Codex leg は信長SAFETY裁定 seq132707 により停止中)。

---

**軍師second へ直提出。ETA=即時 (提出時点で完了)。確度=高 (§2 は実測7/7・§1 前提検証も実測2/2一致)。
§3 の isolated 検証は「実 guard ではない」という限定付きで確度中。**

---

sha256sum (本ファイル自身・提出直前実測・本行追記前の断面): `a2c912d7960e40a657a9798f4ac9976fcd76dec6bfc6b775d1a30beda599f777` (132行時点)。
★本行追記により sha は変わる。最終値は提出メッセージ本文に別途記す★ (133行時点=73a2bd920a01c37ac996a2a4a8498e527e164f2c7335e26bad7da669c2dd9df0)。

---

## §7 追補 (提出後に気付いた点・2026-08-06T07:1x)

**成果物1 (`tests/checks/codex_exec_sandbox_guard/smoke_test.sh`) は git から不可視 (ignore 判定)。**

`git check-ignore -v tests/checks/codex_exec_sandbox_guard/smoke_test.sh` → `.gitignore:7:*` にマッチし
exit 0 (ignore 確定)。`git ls-files` / `git status --short` いずれにも現れぬ (untracked の `??` すら出ぬ)。

原因: `tests/checks/` 配下は兄弟ディレクトリ (`dd169_kill_term_guard` / `pretooluse_stdin_json` /
`enter_restart_footer_immune` / `audit_gemini_harness`) それぞれに個別の
`!tests/checks/<dir>/` + `!tests/checks/<dir>/*.sh` whitelist 行が要る方式 (`.gitignore` 実測)。
当職の新規ディレクトリにはその行が無く、disk上には実在するが git には一切見えぬ。

**当職は `.gitignore` を自分では編まなんだ** (karo-second 先便 msg_20260806_030806_4c18e3d2「.gitignore本体不触・適用は理事長/委員長の裁可待ち」を踏まえた)。
karo-second・軍師second 双方へ inbox で追補報告済 (2026-08-06T07:1x)。commit 判断はお二方に委ねる。

---

## §8 保全写し (家老second msg_20260806_071944_7223cff5「軍師second 再裁=FAIL(着地の形)」への応)

**★本節は 保全写しであって 正本に非ず★**。
**正本 = `tests/checks/codex_exec_sandbox_guard/smoke_test.sh` (163行・sha256=6a624c8d4671a8cfdbb04bd9934abbfc4f65ec27394e58c409814700a29f2e89)**、
**★`.gitignore:7` の `*` に捕捉され git 不可視★** (`git check-ignore -q` exit=0=ignore・
`git ls-files`/`git status --short` いずれにも現れぬ、2026-08-06T07:21:27 再確認済)。

**再裁の理 (軍師second・家老second中継)**: 中身ではなく ★landing form★。smoke_test.sh が git 不可視ゆえ、
報告書が見えても試験本体が commit 根拠として未着地。∴ repo 可視形 (.md) へ試験本体を全文で着地させれば
再監査の余地あり、との事。

**写した直前の断面 (実測・秒単位)**:
- 正本 path: `tests/checks/codex_exec_sandbox_guard/smoke_test.sh`
- 正本 行数: 163
- 正本 sha256: `6a624c8d4671a8cfdbb04bd9934abbfc4f65ec27394e58c409814700a29f2e89`
- 測定時刻: 2026-08-06T07:21:27+09:00
- HEAD hash (測定時点): `d76b025c0c5346b7c938305dbeca2fbb29cd139f`
- 正本の git 可視性: `git check-ignore -q` exit=0 (ignore・不可視)。`-v` は末尾注記 (§1類似の落とし穴)
  ゆえ用いず、家老second 御指摘通り `-q` の終了コードで判じた。

**7ケース実測 (2026-08-06T07:21:33 再実行・§2 と同一結果)**: `ALL PASS (7/7)`。
★段1(cwd判定)/段2(sandbox種別判定) の弾く側は本テストでは未到達★ (§2/§冒頭境と同じ限界、以下の全文にも
同内容がコメントとして埋め込まれている)。

**破棄条件**: `.gitignore` の裁 (理事長殿/委員長殿) が下り、本 whitelist gap が是正され
正本が `git ls-files` で可視となった時点で、★本 §8 は破棄し、以後は正本 (tracked) のみを参照する★。

**全文 (改変なし・一字も違えず・163行)**:

```bash
#!/usr/bin/env bash
#
# codex_exec_sandbox_guard.sh — 弾く側 (rejection side) 負テスト
#
# 発令: 家老second → 足軽3号 (msg_20260806_065625_de110cbd)
# 対象: scripts/checks/codex_exec_sandbox_guard.sh (59行・3719 bytes・git 追跡済)
#
# ★境・限界 (冒頭に記す・末尾に置けば読み手が読み落とすゆえ)★
#
#   本ガード は 3 段の直列判定を持つ:
#     (0) halt gate  — GO_RECORD file (/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record)
#         の実在 + marker 内容を検証。無ければ即 exit 1 (BLOCK)。
#     (1) live-repo cwd 判定  — INTENDED_CWD が repo/newbuild パターンに glob マッチすれば exit 1。
#     (2) sandbox 種別判定    — CODEX_SANDBOX_KIND 未設定なら exit 2 (判定不能)。
#
#   ★現環境で GO_RECORD は実在せぬ (本テスト実行前に ls で確認済・当スクリプトも re-confirm する)★。
#   ∴ (0) が常に先着で exit 1 を返し、(1)(2) には ★到達し得ぬ★。
#
#   ★(1)(2) を実行で検証するには GO_RECORD を実在させる必要が在るが、
#   guard 本体のコメント (L27) が明記する通り
#   「GO記録file は理事長GO発令後に上位のみが配置する。agent自己配置/自己設定 = D-lane違反」
#   ゆえ、★本テストは GO_RECORD を一切 作成/書換せぬ★ (絶対境界・本工区の禁則を守る為)。
#
#   ∴ 本テストが実測できるのは ★halt gate (段0) の弾く側のみ★。
#   段(1)(2) の弾く側 (live-repo cwd 拒否・絶対path・相対path ../ 脱出・sandbox種別判定) は
#   ★試しておらぬ★ (試せぬ、ではなく「試すには禁則に触れるゆえ 試しておらぬ」)。
#
#   ★試した形★ = halt gate 拒否 (GO_RECORD 不在) を、intended_cwd の 6 変化
#                 (無引数/live repo 直下/live repo 配下/newbuild/安全な cwd/相対 ../ 脱出) +
#                 CODEX_SANDBOX_KIND 設定有無 の組合せで確認。
#                 ★いずれも段0 で止まる事を示すのみで、段1/2 の条件分岐そのものは検証せぬ★。
#
#   ★未測 (design-level observation・実行未確認)★ = guard コメント L43 が自ら認める通り、
#   段(1) の cwd 判定は文字列 glob マッチであり realpath 解決を行わぬ。
#   ゆえに「相対 path の ../ が文字列上 repo パターンに一致せぬ形」で live repo へ実際には
#   入り込む入力が在れば、段(1) は理論上 素通りし得る (guard 自身のコメントに拠る認識であり、
#   ★当職が実行して確かめた事実ではない★。段0 に阻まれ 実行では到達不能ゆえ)。
#
#   ★網羅を主張せず★。上記以外の未試形が在り得る事を排除せぬ。
#
# 実行: bash tests/checks/codex_exec_sandbox_guard/smoke_test.sh
# 期待: 全ケース PASS、最終行 "ALL PASS (N/N)"
#

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
GUARD="$REPO_ROOT/scripts/checks/codex_exec_sandbox_guard.sh"
GO_RECORD="/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record"

if [ ! -f "$GUARD" ]; then
    echo "ERROR: guard not found: $GUARD" >&2
    exit 1
fi

# --- 前提の再確認 (本テスト自体が GO_RECORD を作らぬ事の保証・実行毎に検める) ---
if [ -e "$GO_RECORD" ]; then
    echo "ERROR: GO_RECORD が実在する ($GO_RECORD)。本テストは『GO_RECORD 不在』を前提に段0の弾く側のみを検証する設計ゆえ、実在する環境では前提が崩れ結果が無意味になる。中断する。" >&2
    exit 2
fi

PASS=0
FAIL=0
FAILED_CASES=()

run_case() {
    local case_id="$1"
    local description="$2"
    local expected_rc="$3"
    local expected_stderr_grep="$4"
    shift 4
    # 残余引数 = guard へ渡す引数 (0 個 or 1 個の intended_cwd)

    local actual_rc actual_stderr
    actual_stderr=$(bash "$GUARD" "$@" 2>&1 1>/dev/null)
    actual_rc=$?

    local ok=1
    if [ "$actual_rc" != "$expected_rc" ]; then
        ok=0
    fi
    if [ -n "$expected_stderr_grep" ] && ! printf '%s' "$actual_stderr" | grep -qi "$expected_stderr_grep"; then
        ok=0
    fi

    if [ "$ok" = 1 ]; then
        printf '[PASS] %-6s rc=%s (expected=%s) — %s\n' "$case_id" "$actual_rc" "$expected_rc" "$description"
        PASS=$((PASS + 1))
    else
        printf '[FAIL] %-6s rc=%s (expected=%s) stderr_grep=%q — %s\n' "$case_id" "$actual_rc" "$expected_rc" "$expected_stderr_grep" "$description" >&2
        printf '       stderr=%s\n' "$actual_stderr" >&2
        FAIL=$((FAIL + 1))
        FAILED_CASES+=("$case_id")
    fi
}

echo "=== codex_exec_sandbox_guard.sh 弾く側 負テスト (halt gate のみ実測可) ==="
echo "guard: $GUARD"
echo "GO_RECORD (不在を前提): $GO_RECORD"
echo "----"

# C01: 無引数 (= $PWD 既定・repo 内で実行しても) → halt で弾かれる
run_case "C01" \
    "無引数 (\$PWD 既定) → GO_RECORD 不在ゆえ exit 1 (halt)" \
    1 "GO記録file不在"

# C02: intended_cwd = live repo root
run_case "C02" \
    "intended_cwd=live repo 直下 → halt が先着 (cwd 判定には未到達)" \
    1 "GO記録file不在" \
    "$REPO_ROOT"

# C03: intended_cwd = live repo 配下 (サブpath)
run_case "C03" \
    "intended_cwd=live repo 配下 → halt が先着" \
    1 "GO記録file不在" \
    "$REPO_ROOT/scripts/checks"

# C04: intended_cwd = newbuild パターン
run_case "C04" \
    "intended_cwd=newbuild パターン → halt が先着" \
    1 "GO記録file不在" \
    "/home/hakudokai/projects/multi-agent-shogun-newbuild-test"

# C05: intended_cwd = 明らかに安全な cwd (repo 外・/tmp) → それでも弾かれる
run_case "C05" \
    "intended_cwd=/tmp (安全に見える cwd) でも halt が弾く (cwd の安全性は無関係)" \
    1 "GO記録file不在" \
    "/tmp/codex_exec_sandbox_guard_test_safe_dir"

# C06: intended_cwd = 相対 path による ../ 脱出試行 (文字列上は live repo パターンに非一致)
run_case "C06" \
    "intended_cwd に相対 ../ を含む脱出試行文字列 → それでも halt が先着し弾く" \
    1 "GO記録file不在" \
    "../../../home/hakudokai/projects/multi-agent-shogun"

# C07: CODEX_SANDBOX_KIND を設定しても halt には無関係 (halt が最優先)
#      run_case は env var 注入に非対応ゆえ、本ケースのみ手で組む (run_case 呼出は行わぬ)。
CODEX_SANDBOX_KIND=docker
export CODEX_SANDBOX_KIND
actual_stderr=$(bash "$GUARD" "/tmp/codex_exec_sandbox_guard_test_safe_dir_2" 2>&1 1>/dev/null)
actual_rc=$?
unset CODEX_SANDBOX_KIND
if [ "$actual_rc" = "1" ] && printf '%s' "$actual_stderr" | grep -qi "GO記録file不在"; then
    printf '[PASS] %-6s rc=%s (expected=1) — CODEX_SANDBOX_KIND=docker 設定下でも halt が先着 (sandbox種別設定はhaltを迂回せぬ)\n' "C07" "$actual_rc"
    PASS=$((PASS + 1))
else
    printf '[FAIL] %-6s rc=%s (expected=1) — CODEX_SANDBOX_KIND=docker 設定下でも halt が先着\n' "C07" "$actual_rc" >&2
    printf '       stderr=%s\n' "$actual_stderr" >&2
    FAIL=$((FAIL + 1))
    FAILED_CASES+=("C07")
fi

echo "----"
TOTAL=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
    echo "ALL PASS ($PASS/$TOTAL)"
    echo "★注記★: 全ケースは段0 (halt gate) の弾く側のみを実測。段1(cwd判定)/段2(sandbox種別判定) の弾く側は本テストでは未測 (理由=冒頭参照)。"
    exit 0
else
    echo "FAILED ($FAIL/$TOTAL): ${FAILED_CASES[*]}" >&2
    exit 1
fi
```

**§8 末尾 断面 (本節追記完了直後・別途測定)**: 下記は本 .md ファイル全体の測定であり、
提出メッセージ本文に確定値として記す (このファイル自身への自己言及ゆえ、確定値は本文中には書けぬ・
§前例と同じ理由)。
