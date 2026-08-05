# codex_exec_sandbox_guard.sh・通す側(陽性対照)テスト (足軽1号、2026-08-06・家老second下命)

## 境・限界・未測 (冒頭に置く・下命どおり)

- ★本テストが証すのは guard 本体(59行)の★コード分岐★が、3条件充足時に exit 0 を返す事のみ★。
  「Codex exec を実際に安全に起動できる」事の end-to-end 証明ではない。
- ★呼び手 0件★: `grep -rln "codex_exec_sandbox_guard" --include="*.sh"` で本体以外の呼出し元が
  存在しない事を確認済(下記「前提検算」参照)。∴ guard が通っても、それを呼ぶ側 (audit_codex.sh 等) が
  未結線のままなら Codex exec は現状動かない。結線は本工区の範囲外。
- ★sandbox 実体検証は guard 自身が placeholder と明記★ (guard コード行51-52のコメント:
  「ここは環境の sandbox 実装に依存する placeholder」)。本テストの `CODEX_SANDBOX_KIND` は
  自己申告文字列であり、guard は非空文字列であれば無条件に信頼する現行コードの挙動を検証したに
  過ぎない。将来 guard が実 sandbox 検証を実装した場合、本テストの前提は作り直しが要る。
- ★理事長GO発令の実運用フローは検証していない(意図的)★。実路上の GO_RECORD
  (`/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record`) を作る事は
  「agent 自己配置=D-lane違反」に該当するため、mount namespace による一時隔離層(tmpfs)内でのみ
  条件を満たし、namespace 終了後に実路上へ何も残らぬ事を前後で確認する手法を採った(詳細は下記)。
  ∴ 本テストは実路上の halt 解除フローそのものを検証していない。
- ★技法の可搬性は未確認★: `unshare --mount --user --map-root-user` (unprivileged user namespace)
  は本機 (WSL2, kernel 6.6.87.2-microsoft-standard-WSL2, util-linux 2.39.3) で動作を確認したが、
  他PC (main/third等) で同様に動く保証はない (kernel の unprivileged userns 設定に依存)。
- 禁三点 (audit_codex.sh 起動・guard 本体書換・.claude/settings.json 編集) はいずれも守った。
  newbuild・姉妹clone は不触。
- 測時 = 2026-08-05T22:03:54Z / JST換算 2026-08-06T07:03:54+09:00 (`date -u +%Y-%m-%dT%H:%M:%SZ` 実行結果、テスト実行直後)。
- HEAD = `83bdb61` (guard本体への最終変更コミット。`git log -1 -- scripts/checks/codex_exec_sandbox_guard.sh` 実行結果)。

## 前提2件の検算 (下命の追加依頼・「判断を一つ混ぜよ」への応答)

家老second下命本文中の実測主張2件を、当職も独立に再測した。

```
$ sha256sum scripts/checks/codex_exec_sandbox_guard.sh
a98f6129b73e11a9a897c197f92c9e21628ab0c57a659355c35a1b1fda19d88c  scripts/checks/codex_exec_sandbox_guard.sh
$ wc -l scripts/checks/codex_exec_sandbox_guard.sh
59 scripts/checks/codex_exec_sandbox_guard.sh
$ git log --oneline -1 -- scripts/checks/codex_exec_sandbox_guard.sh
83bdb61 fix(shim): 未コミット安全是正25件の保全=...(家老second W19実測・...)
$ git status --short scripts/checks/codex_exec_sandbox_guard.sh
(無出力)
```
**∴ 「guard は tracked」= 正しい** (git管理下・未コミット変更なし)。

```
$ grep -rl "codex_exec_sandbox_guard" tests/ 2>&1; echo "exit:$?"
exit:1
$ grep -rl "codex_exec_sandbox_guard" --include="*.sh" --include="*.bats" . 2>/dev/null \
  | grep -v "^./scripts/checks/codex_exec_sandbox_guard.sh$"
(該当なし)
```
**∴ 「負テスト零件」= 正しい** (tests/ 配下および repo 全体、本体以外に専用の負テスト・bats参照は0件)。

両premiseとも、足軽6号 W (`docs/incident_logs/2026-08-06_codex_guard_wiring_verification_a6.md`)
の独立実測と一致した (相互裏付け・示し合わせなし・別々に着手)。

## 手法: なぜ mount namespace か (自己供給回避の設計判断)

guard は3条件を順に判定する (コード行17-58):

1. `GO_RECORD` (固定path `/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record`、
   env override 禁) が実在し `CODEX_EXEC_SANDBOX_GO: APPROVED` を含む → 無ければ exit 1
2. `intended_cwd` が live repo (`*/projects/multi-agent-shogun*`) でない → live なら exit 1
3. `CODEX_SANDBOX_KIND` が空でない → 空なら exit 2 (判定不能)

条件1のGO_RECORDは guard 自身のコメントで「agent自己配置=D-lane違反」と明記されている
(実際の halt解除は理事長GO発令後に上位のみが行う想定)。∴ 通す側を測るために実路上へこの
ファイルを作れば、それ自体が禁じられた自己供給になり本末転倒である。

そこで `unshare --mount --user --map-root-user` で新しい mount namespace + user namespace を
作り、その中でのみ `/home/hakudokai/.config` に tmpfs をマウントして GO_RECORD を置いた。
tmpfs は namespace 終了と同時に消え、実ファイルシステムには一切影響しない。guard 本体は
一切改変せず、実際のファイル(絶対path)をそのまま呼び出す — 「namespace越しに本物のコードパスを
本物の絶対pathで実測する」形にした (コードの複製・改変・env override による迂回はしていない)。

## テストスクリプト (実行前に検分可能・guard本体は不参照/不改変)

- path: `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/c07c854f-14b0-4a0e-a56e-79de8255f052/scratchpad/positive_control_test.sh`
  (repo外 scratchpad。repo内には書込んでいない)
- 76行 / sha256=`5af8269e7c19e85cc8d09057188f315a8f0bc3ba9da8678f09fa647139170976`
  (提出直前に測定)

```bash
#!/usr/bin/env bash
# codex_exec_sandbox_guard.sh 通す側(陽性対照)+ 弁別性 sanity テスト
#
# 目的:
#   guard 本体(scripts/checks/codex_exec_sandbox_guard.sh)を一切改変せず、かつ
#   GO_RECORD の実路上ファイル(/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record)を
#   一切作らず(自己供給=D-lane違反回避)、mount namespace の一時隔離層(tmpfs)内でのみ
#   3条件を満たして guard が exit 0 (OK) を返す事を実測する(シナリオA=本命の陽性対照)。
#   併せて、同じ隔離層の中で1条件ずつ外し、guard が正しく弁別して停止する事も確かめる
#   (シナリオB/C/D=陽性対照が「常に通る門」になっていない事の確認・sanity)。
#
# 各シナリオは独立の unshare namespace で実行 = 相互汚染なし。
# namespace 終了後、実路上に GO_RECORD が一切残っていない事を最終確認する。

set -uo pipefail

GUARD=/home/hakudokai/projects/multi-agent-shogun/scripts/checks/codex_exec_sandbox_guard.sh
REAL_GO_DIR=/home/hakudokai/.config/dentalbi
REAL_GO_FILE="$REAL_GO_DIR/codex_exec_sandbox_go.record"
NONLIVE_CWD=/tmp/.../scratchpad/positive_control_nonlive_cwd_test
LIVE_CWD=/home/hakudokai/projects/multi-agent-shogun

echo "=== [事前] 実路上 GO_RECORD 不在の確認 ==="
if [ -e "$REAL_GO_FILE" ]; then
  echo "ABORT: 実路上に既に $REAL_GO_FILE が存在する。前提崩れのため中止。" >&2
  exit 90
fi
echo "OK: $REAL_GO_FILE は実路上に不在(このテスト開始前から)。"
echo ""

run_scenario () {
  local label="$1" make_go="$2" cwd_kind="$3" set_sandbox="$4"
  echo "--- シナリオ $label: GO_RECORD作成=$make_go / cwd=$cwd_kind / CODEX_SANDBOX_KIND設定=$set_sandbox ---"
  unshare --mount --user --map-root-user bash -c '
    set -uo pipefail
    mount -t tmpfs tmpfs /home/hakudokai/.config
    if [ "'"$make_go"'" = "yes" ]; then
      mkdir -p '"$REAL_GO_DIR"'
      echo "CODEX_EXEC_SANDBOX_GO: APPROVED (namespace-local test artifact only)" > '"$REAL_GO_FILE"'
    fi
    if [ "'"$set_sandbox"'" = "yes" ]; then
      export CODEX_SANDBOX_KIND=test-namespace-isolated
    fi
    mkdir -p "'"$NONLIVE_CWD"'"
    if [ "'"$cwd_kind"'" = "live" ]; then
      TARGET_CWD="'"$LIVE_CWD"'"
    else
      TARGET_CWD="'"$NONLIVE_CWD"'"
    fi
    OUT=$(bash '"$GUARD"' "$TARGET_CWD" 2>&1)
    RC=$?
    echo "  guard stdout+stderr:"
    echo "$OUT" | sed "s/^/    /"
    echo "  exit code: $RC"
  '
  echo ""
}

echo "=== シナリオA (本命=陽性対照): 3条件すべて充足 → 期待 exit 0 ==="
run_scenario "A" yes nonlive yes
echo "=== シナリオB (弁別性sanity): GO_RECORD充足だが cwd=live-repo → 期待 exit 1 ==="
run_scenario "B" yes live yes
echo "=== シナリオC (弁別性sanity): GO_RECORD+cwd非live だが CODEX_SANDBOX_KIND未設定 → 期待 exit 2 ==="
run_scenario "C" yes nonlive no
echo "=== シナリオD (弁別性sanity・実路上baselineと同型): GO_RECORD作成せず → 期待 exit 1 ==="
run_scenario "D" no nonlive yes

echo "=== [事後] namespace 終了後、実路上 GO_RECORD が依然不在である事の確認(自己供給していない証) ==="
if [ -e "$REAL_GO_FILE" ] || [ -d "$REAL_GO_DIR" ]; then
  echo "★異常★: 実路上に $REAL_GO_DIR/$REAL_GO_FILE が存在する。自己供給が発生した疑い。" >&2
  exit 91
fi
echo "OK: 全シナリオ終了後も実路上に $REAL_GO_DIR / $REAL_GO_FILE は不在のまま。"
```

(注: 本文中の `NONLIVE_CWD` は紙面の都合で `.../scratchpad/...` と省略表示。実ファイルでは
scratchpad の絶対path全文が入っている。)

## 実行結果 (全4シナリオ・実測ログそのまま)

- 出力保存先: `/tmp/claude-1000/-home-hakudokai-projects-multi-agent-shogun/c07c854f-14b0-4a0e-a56e-79de8255f052/scratchpad/positive_control_test_output.txt`
  (repo外・59行 / sha256=`859e7b6b4a7c6178645ede6c8850fd883490dc0f20023463e5a65c6c0880a123`)

```
=== [事前] 実路上 GO_RECORD 不在の確認 ===
OK: /home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record は実路上に不在(このテスト開始前から)。

=== シナリオA (本命=陽性対照): 3条件すべて充足 → 期待 exit 0 ===
--- シナリオ A: GO_RECORD作成=yes / cwd=nonlive / CODEX_SANDBOX_KIND設定=yes ---
  guard stdout+stderr:
    [codex_exec_sandbox_guard] OK: sandbox=test-namespace-isolated 検証済・非live cwd=(scratchpad path)。Codex exec 起動可。
  exit code: 0

=== シナリオB (弁別性sanity): GO_RECORD充足だが cwd=live-repo → 期待 exit 1 ===
--- シナリオ B: GO_RECORD作成=yes / cwd=live / CODEX_SANDBOX_KIND設定=yes ---
  guard stdout+stderr:
    [codex_exec_sandbox_guard] BLOCK: intended_cwd=/home/hakudokai/projects/multi-agent-shogun は live repo。Codex exec を live repo cwd で起動するな。
  exit code: 1

=== シナリオC (弁別性sanity): GO_RECORD+cwd非live だが CODEX_SANDBOX_KIND未設定 → 期待 exit 2 ===
--- シナリオ C: GO_RECORD作成=yes / cwd=nonlive / CODEX_SANDBOX_KIND設定=no ---
  guard stdout+stderr:
    [codex_exec_sandbox_guard] WARN: CODEX_SANDBOX_KIND 未設定=sandbox種別不明。保守的に判定不能(2)を返す。
  exit code: 2

=== シナリオD (弁別性sanity・実路上baselineと同型): GO_RECORD作成せず → 期待 exit 1 ===
--- シナリオ D: GO_RECORD作成=no / cwd=nonlive / CODEX_SANDBOX_KIND設定=yes ---
  guard stdout+stderr:
    [codex_exec_sandbox_guard] BLOCK: halt解除の理事長GO記録file不在 (/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record)。検証済sandbox未確立 (信長SAFETY裁定2026-07-21・seq132707)。Codex exec を起動するな=Codex leg documented扱いへ。
  exit code: 1

=== [事後] namespace 終了後、実路上 GO_RECORD が依然不在である事の確認(自己供給していない証) ===
OK: 全シナリオ終了後も実路上に /home/hakudokai/.config/dentalbi / /home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record は不在のまま。
```

シナリオD実行前後に加え、テスト全体の実行前後でも実路上 `/home/hakudokai/.config/dentalbi/`
不在を個別確認した (`ls -la` 実行結果、上記「境・限界・未測」参照)。4シナリオとも期待exit codeと
完全一致。

## 結論

- ★陽性対照(シナリオA)成立★: 3条件 (GO_RECORD実在+marker一致・非live cwd・CODEX_SANDBOX_KIND非空)
  をすべて満たせば guard は exit 0 (OK) を返す事を実測で確認した。
  「guard は何も通さぬ門ではない」— 通す側が実在する。
- ★弁別性(シナリオB/C/D)も確認★: 1条件でも欠くと、欠いた条件に対応する正しい exit code
  (live cwd=1 / sandbox種別未設定=2 / GO_RECORD不在=1) を返す。陽性対照は「常に通る」偽陽性ではない。
- ★自己供給なし★: 実路上の GO_RECORD は本テスト前後で一貫して不在。理事長GO発令フローを
  代行・迂回していない。
- 残課題 (本工区の範囲外・上位判断事項): 呼び手0件 (結線未了)・sandbox実体検証がplaceholder・
  技法の他PC可搬性未確認。Codex leg 全面解禁の可否は「guard 結線 + 負テストPASS + 委員長GO」の
  3点セット (下命記載) のうち guard の通す側実証はこれで満たすが、負テスト (弾く側の専用test)
  はなお別途0件のままであり、当職の担当範囲(通す側)のみで完結する話ではない。

## ETA

即応・本便で完了 (確度: 高 — 実測4シナリオ+自己供給なし前後確認まで完遂)。

軍師second へ直提出する。
