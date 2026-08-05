# codex_exec_sandbox_guard 結線設計 反証 (足軽1号、2026-08-06・家老second下命 msg_20260806_084649_7e7fffb3)

**任**=足軽6号 結線設計 (軍師PASS済) の穴を探す事。★同意を探さず反証を探した★。read-only・書込/commit一切せず。

## 境・限界・未測 (冒頭)

設計・.claude/settings.json・.gitignoreいずれも編んでおらぬ。`audit_codex.sh` を含め ★一切のscriptを実行しておらぬ★
(grep/read/wc/sha256sum/git log/git status/git rev-parse/date のみ使用)。GO_RECORD は作成・参照とも行わず (作成=D-lane違反ゆえ絶対境界)。
hakudokai-dev系worktreeへは一字も書いておらぬ。rcはpipeに通さず (`cmd >/dev/null 2>&1; echo $?` 形も本件は未使用・全て静的読解)。
grepは全て `/usr/bin/grep -r` を使用。

測時=2026-08-06T08:52:13+0900 (`date -Iseconds` 実行結果)。HEAD=`f386a8b972ebabaf8fadaa4da83556dd6e346864` (`git rev-parse HEAD` 実行結果)。

## 母集団宣言

対象4件 (設計doc・guard本体・負テスト・settings.json) は★全文読了★ (行数=下記表参照)。
加えて `scripts/audit_codex.sh` (136行) 全文・`shim/hakudokai/hakudokai_audit_scheduler.sh` (193行) 全文・
`scripts/audit_meta_codex.sh` (349行のうち冒頭40行+呼出周辺40行の限定読解・全文ではない)・
`docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md` (60行・全文)・
`docs/audit-framework.md` §15-16 (約140行・限定読解) を反証の裏取りに読んだ。
`npx @openai/codex exec` の呼出site探索は repo 全域 `/usr/bin/grep -rn` で実施 (`.git/` 除外)。

## (1) 対象 (path・行数・sha256、同じ行)

| # | path | 行数 | sha256 |
|---|---|---|---|
| 設計 | docs/incident_logs/2026-08-06_codex_guard_wiring_design_a6.md | 104行 | dc755359f0969b13b196284e5b9234cacc5d29cc93d4a9c72f3f473998543420 |
| 守本体 | scripts/checks/codex_exec_sandbox_guard.sh | 59行 | a98f6129b73e11a9a897c197f92c9e21628ab0c57a659355c35a1b1fda19d88c |
| 負テスト | tests/checks/codex_exec_sandbox_guard/smoke_test.sh | 163行 | 6a624c8d4671a8cfdbb04bd9934abbfc4f65ec27394e58c409814700a29f2e89 |
| 門正本 | .claude/settings.json | 1088行 | 844c63c0d4870f48e23838e777b96b107d5820750644d8d8aab83dc1b8c90c77 |
| 結線先 | scripts/audit_codex.sh | 136行 | b23888c3ea8525636d5a56d448d245926eff77ebbe0d10872b14ae2a7fae8fab |
| 未結線① | shim/hakudokai/hakudokai_audit_scheduler.sh | 193行 | 70b7ab9ba07b3685d92f35908c4c4983219f83c9e9f54614b9e2dda88ca1fa50 |
| 未結線② | scripts/audit_meta_codex.sh | 349行 | 7fb2fc322e05d16cd690279207f23b2e397918fefb50353e8fe7c29cd5ca7b3d |
| 事故原記録 | docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md | 60行 | a4d687d85947c69f957266ae6dfc3b945b6b730112dd8b24f4b403b8ad5d5fd0 |

## (2) 反証 五点

### ⒜ 結線後、この守は何を通してしまうか (塞ぐ物でなく抜ける物)

**★最重要所見★=「呼び手」は `audit_codex.sh` 一本のみではない。repo全域を実測した所、`npx @openai/codex exec` の
呼出siteは★現に4箇所★在り、設計が塞ぐのは★そのうち1箇所のみ★である。**

```
$ /usr/bin/grep -rn "npx @openai/codex exec" --include="*.sh" . 2>/dev/null | /usr/bin/grep -v "\.git/"
./shim/hakudokai/hakudokai_audit_scheduler.sh:125  (run_weekly 内)
./shim/hakudokai/hakudokai_audit_scheduler.sh:176  (run_on_commit 内)
./scripts/audit_codex.sh:93                        (★本設計が結線する唯一の箇所★)
./scripts/audit_meta_codex.sh:263
```

残り3箇所 (`hakudokai_audit_scheduler.sh` 2箇所・`audit_meta_codex.sh` 1箇所) は本設計の範囲外であり、
結線が実装されても★無防備のまま★残る。3箇所とも呼出直前に `cd` を伴わず (`/usr/bin/grep -n "^\s*cd "` で
`hakudokai_audit_scheduler.sh`/`audit_meta_codex.sh` 双方とも0件・`hakudokai_audit_scheduler.sh` の
2件の `cd` はいずれも `$(cd "$SCRIPT_DIR" && git ...)` 形のsubshellでgit操作専用、npx呼出行の実行時cwdには影響せぬ)、
すなわち★invokerのcwdをそのまま継承する構造は`audit_codex.sh`と同型★。

∴ 「結線した」事実が「Codex execが安全になった」という誤った安心を生む危険がある。
本設計doc・関連の陽性対照(a1)・拒否側負テスト(a3)いずれも4箇所目・5箇所目の存在に言及しておらぬ
(★当職の検索範囲では言及0件★)。★零に理由=これら3箇所は「audit_codex.sh」という語で検索する限り
視界に入らぬ。呼び手を「audit_codex.shの呼び手」でなく「npx @openai/codex execそのものの呼び手」で
問い直して初めて見える★。

### ⒝ この修正が新たに開ける穴は何か

新たな穴というより★既存の穴の見え方を変える穴★を1件挙げる。

`scripts/audit_codex.sh` の`INTENDED_CWD`として設計が選んだ値は`$REPO_PATH`(第5引数・既定値
`/mnt/c/Users/User/Documents/DentalBI`)である。しかし2026-07-21事故の確定root causeは
以下の通りである (`docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md` L19-20 逐語):

> `(3) なぜ live repo に到達したか → audit_codex.sh L93 の codex exec が ★invoker の cwd
> (= live repo /home/hakudokai/projects/multi-agent-shogun) で実行★される (git diff だけが cd $REPO_PATH)。`

**すなわち事故当日、危険だったのは「REPO_PATHの値」ではなく「invokerの実際の$PWD」であった。
`git diff`だけが`$REPO_PATH`へcdするsubshellで実行され、`npx @openai/codex exec`自体は
そのsubshellの外・invokerの$PWDのまま実行される、という構造は現行`audit_codex.sh`でも不変
(当職`cat -n`全文読解・L33の`git diff`のみ`cd "$REPO_PATH"`のsubshell内、L93の`npx`呼出は
subshell外・script全体を通じ非subshellの`cd`は0件)。**

設計doc自身の守り (`引数(intended_cwd)の取得元`節) は「guard自身が[intended_cwd]を唯一の引数として
設計されており…既存の$REPO_PATHをそのまま渡すのが最小差分」とだけ理由づけており、
★$REPO_PATHが「invokerの実cwd」を正しく代表するかは検討されていない★。

一方guard本体は`INTENDED_CWD="${1:-$PWD}"` (L17) であり、★引数を渡さねば$PWD (=まさに事故当日
危険だったinvoker実cwd) を既定で見る設計★になっている。設計案は明示的に`"$REPO_PATH"`を渡す事で、
この既定の(より事故の実態に合った)挙動を★意図せず潰している★。

∴ `$REPO_PATH`が呼出時のinvoker実cwdと一致する保証は本設計に無い。`docs/audit-framework.md`内でも
運用が割れている(§15.4「家康の標準フロー」`厳守`指定の例はcd無しで`$REPO`変数を渡すのみ・
§16.1「ドライラン」の例は明示的に`cd /mnt/c/Users/User/Documents/DentalBI`後に`$(pwd)`を渡す形、
と★同一文書内でinvoker cwdと$REPO_PATHを揃える手順と揃えぬ手順が併存★)。
2026-07-21事故は「揃わぬ」運用で起きた事故そのものであり、本設計が採る`$REPO_PATH`渡しは
★事故当日の危険なcwdを検知できたとは限らない★(REPO_PATHが事故当日どの値だったかは
`docs/incident_logs/2026-07-21_codex-audit-live-repo-write.md`に明記が無く★未測★)。

### ⒞ 負テストは何を試しており、何を試しておらぬか

負テスト(`tests/checks/codex_exec_sandbox_guard/smoke_test.sh`)自身の冒頭コメント(L8-39)が
自ら明記する通り、GO_RECORD不在の現環境では★段0(halt gate)の弾く側のみ★が実測可能であり
(C01-C07、いずれもGO_RECORD不在によるexit 1のみを確認)、
★段1(live-repo cwd判定)・段2(sandbox種別判定)の弾く側は実行で検証されておらぬ★(GO_RECORD自己配置=
D-lane違反ゆえ試せぬ、と明記=試さなんだのではなく試せぬ)。当職はこの自己申告を実コードと
突き合わせ、`run_case`呼出7件(C01-C07)全てが期待stderr文字列`"GO記録file不在"`を要求している事
(L102-152実測)を確認し、★自己申告は正確★と判定する(過大主張なし)。

加えて、陽性対照(`2026-08-06_codex_guard_positive_control_a1.md`)は3条件(GO_RECORD実在+marker一致・
非live cwd・CODEX_SANDBOX_KIND非空)を満たす合成環境での★通す側★を実測しているが、これは
guard単体への直接呼出であり、★`audit_codex.sh`経由で`$REPO_PATH`を渡した場合の統合経路は
陽性対照・負テストいずれにも含まれておらぬ★(設計doc自身「陽性対照が結線後も生きるか」節が
「実装後に別途書かれるべき」と認めている通り)。∴ ⒝で述べた`$REPO_PATH`渡しの妥当性は
★どの既存テストでも検証されておらぬ★(零・理由=結線が未実装ゆえ統合テストの対象が存在しない)。

### ⒟ caller零のまま結線する事の前提――何処に挿すのが正か、が設計に一意に書かれておるか

設計doc「呼ぶ位置」節は`audit_codex.sh` L92直前(retry loop突入前・1回のみ)を案として明記しており、
★挿入行の位置自体は一意★(理由付きで不採用案2件も併記・§14-b「仮説に合う例のみ列挙」には
該当せぬ、不採用理由も具体的)。★但し★、挿入位置は一意でも、⒝で述べた通り★渡す引数の値
($REPO_PATHか$PWDか)は一意に正当化されておらぬ★——「一意に書かれているか」を位置と引数値の
両面で問うと、位置は一意・引数値は不十分、という★分離した答★になる。

### ⒠ 門は誤って発火し得るか (偽陽性)。発火したら誰がどう通すのか

**段0 (halt gate)** は偽陽性を原理的に起こし得ぬ設計 (fail-closed・GO_RECORD不在なら常にexit 1、
これは意図通り)。通す手順はguard本体コメントL27・L39-40に明記 (理事長GO発令後に上位のみが
GO_RECORDを配置・agent自己配置はD-lane違反)。★通す手順は書かれている★。

**段1 (cwd判定)** は偽陽性を起こし得る。⒝で述べた通り`$REPO_PATH`の値が「文字列上
`*/projects/multi-agent-shogun*`または`*newbuild*`に一致するが実際は安全な監査対象」
(例=正当な理由でrepo名に`multi-agent-shogun`を含むclone/backup pathをREPO_PATHとして渡す場合)
であれば誤ってblockされ得る。★この場合の解除手順は設計doc・guard本体いずれにも記載が無い★
(零・理由=段1の偽陽性そのものが本設計・a1陽性対照・a3負テストいずれの検討範囲にも入っていない)。
実害は小さい(誤ってblock=安全側に倒れるのみ)が、「発火したら誰がどう通すのか」という問いへの
★答は無い★という事実は記録しておく。

## 【本工区で己が直した誤り】

初稿で⒜の呼出site探索を`scripts/`配下限定のgrepで済ませかけたが、`shim/`配下は探索範囲に
含めていなかった事に気付き、repo全域(`.`起点・`.git/`除外)へ広げ直した。結果、`shim/hakudokai/`
配下の2箇所が新たに見つかった(範囲を絞った初稿のままでは3箇所目のaudit_meta_codex.shしか
拾えていなかった)。

## ★母集団漏れの自己申告★

1. `scripts/audit_meta_codex.sh`は349行中、冒頭40行+L230-270の呼出周辺のみを読んだ(全文は未読)。
   `cd`の有無はgrep(`/usr/bin/grep -n "^\s*cd "`)で全文相手に確認済だが、他の危険な挙動
   (絶対path書込等)の有無は本工区の範囲(呼出site census+引数妥当性)を超えるため確認しておらぬ。
2. `npx @openai/codex exec`以外の呼び方(例=`codex`単体コマンド・別のCLI別名)でCodexが
   起動される経路が在るかは、"npx @openai/codex exec"という文字列一致でのみ探索したため、
   ★未測★(0件と断じてはおらぬ)。
3. `.claude/settings.json`のPreToolUse hook一覧を全文読んだが、本件guardが将来PreToolUse hookとして
   登録される可能性(設計doc・関連の`2026-08-06_orphan_checks_design_intent_a6.md`ではscript直呼び案
   のみが検討されている)は別の結線経路であり、本反証は「script直呼び案」のみを対象とした。
4. ⒠段1偽陽性の実害度合い(「REPO_PATHに`multi-agent-shogun`という文字列を含む正当な監査対象が
   実在するか」)は当職の読解範囲(scripts/・shim/・docs/incident_logs/)では具体例を発見できておらぬ
   (∴ 理論上の懸念であり、現に踏まれた実例は0件)。

## 総括

反証結果=★通す(PASS)★としては渡せぬ。理由=⒜(呼び手4箇所中1箇所のみ結線)と⒝(結線先1箇所内でも
渡す引数値$REPO_PATHが2026-07-21事故当日の危険条件=invoker実cwdを代表する保証が無い)の2点が、
「結線すればCodex execは安全になる」という設計doc全体の前提(冒頭「案」の位置づけ通り、本設計は
実装済ではなく提案段階)に対する★具体的な反証★であるため。裁定は当職の任ではない(下命「裁定するな」
に従い、事実の指摘に留める)。

## 監査体制

暫定二者制 (軍師second + Gemini)。Codex leg停止中 (2026-07-21事案)。

以上、足軽6号 結線設計への反証応答。実装・commit・裁定はいずれも行っていない。
