# `grep` shell関数(ugrep --ignore-files)と真の /usr/bin/grep の乖離 — 条件を特定

下命=家老second msg_20260806_110045_51c3fc11 (②の問い) → msg_20260806_111718_f0e2ad7a (③条件を絞れ・着地急げ)。
起草=足軽3号。走らせず・DBに触れず・hakudokai-dev/newbuildへ一字も書かず、当repo内での読取+使い捨てprobeファイル
(生成後 即削除・全て `git status --porcelain` で残留なきこと確認済) のみで検めた。

## 冒頭・結論を先に

1. **①の問い（②「repo全体」の検索方法）への回答**: 当職が2026-08-06_reserveimage_cycle2_f2_design_adversarial_review_a3.md
   §発見3で用いた `grep -rn "_create_all_appointment_tables" --include=*.py .` は **command化されていない `grep`**
   であり、下記②で確定した通り **shell関数経由 (ugrep --ignore-files)** を通っていた。
   ∴ **手法そのものは万全ではなかった**(自己申告)。
   然れど本便末尾の「再検証」で、**tracked分＋全615 .pyファイル(disk上の存在するもの全て)を真の `/usr/bin/grep`
   (`command grep`) で再走査し、同結果(0件)を確認した**。∴ **主張「repo全体で未定義」の結論自体は生き残る**が、
   これは事後の再検証によるものであり、当初の一回きりの `grep` 呼び出しだけでは確証たり得なかった。

2. **③の問い（除外はどの条件で起き、どの条件で起き申さぬか）**: **確定**。
   → **`.gitignore` に対象dirを丸ごと再許可する `!dirname/` 形式(個別globなし)の裸のwhitelist行が在るか否か**が分岐点。
   在れば ugrep は再帰的に "全許可" と解釈し除外を行わぬ。無ければ (個別file/glob単位のwhitelistのみ、
   または一切whitelistなし) ugrep は当該fileを除外する。
   **かつ この ugrep の解釈は git 自身の解釈と食い違う** — `!dirname/` は git 的には「ディレクトリ探索の許可」のみで、
   中身の個別fileは別途whitelistされねば `git add` すら拒まれる(下記②-cで実証)。∴ **ugrepはgitより甘い側に間違える**。

## ② 為した実測（逐語コマンド・件数）

### ②-a 当初の「一致した」再現 (将軍second の queue/ 例・当職も再現)

```
$ grep -rl "read: false" queue/     → 48件
$ command grep -rl "read: false" queue/  → 48件   (一致・除外なし)
```

### ②-b 決定的差分テスト①: 既存 gitignored .py file (scripts/design-pipeline/extract_prototype.py) へ使い捨てneedle追記

対象は足軽2号既報の「git不可視10件」の一つ (`.gitignore:7:*` に捕捉・`git ls-files --error-unmatch` rc=1で untracked確認済)。

```
$ echo "# UNIQUE_NEEDLE_A3_GITIGNORE_TEST_20260806" >> scripts/design-pipeline/extract_prototype.py
$ grep -rln "UNIQUE_NEEDLE..." --include=*.py .          → (無出力) exit=1  ★除外された★
$ command grep -rln "UNIQUE_NEEDLE..." --include=*.py .  → ./scripts/design-pipeline/extract_prototype.py  exit=0
$ grep -rln "UNIQUE_NEEDLE..." .                          → (無出力) exit=1  ★--include有無に依らず除外★
$ command grep -rln "UNIQUE_NEEDLE..." .                  → ./scripts/design-pipeline/extract_prototype.py  exit=0
```
(直後に原状復元・`diff` で復元確認・`git status --porcelain` で当該pathの残留差分なきこと確認済)

### ②-c 「tracked/untracked」仮説を反証 — 両path共 untracked、結果は分かれる

```
$ git ls-files --error-unmatch queue/inbox/ashigaru3.yaml                       → error (untracked) rc=1
$ git ls-files --error-unmatch scripts/design-pipeline/extract_prototype.py     → error (untracked) rc=1
```
両方ともgit未追跡。∴ tracked/untrackedの差ではない(仮説棄却)。

### ②-d 決定的差分テスト②: dir⇔extensionの入替 (どちらが効くかを分離)

新規probe file (即削除) を作成し4象限で確認:

```
queue/_a3_probe.py           (.py  in queue/)              → wrapped grep: 除外(exit=1) / command grep: 発見(exit=0)
scripts/design-pipeline/_a3_probe.yaml (.yaml in scripts/design-pipeline/) → wrapped grep: 除外(exit=1) / command grep: 発見(exit=0)
queue/_a3_gitignore_probe_test.yaml    (.yaml in queue/)    → wrapped grep: 発見(exit=0) / command grep: 発見(exit=0)  ★除外されぬ★
```
∴ **拡張子(.py/.yaml)ではなく、対象dirがqueue/か否かで分かれた**。

### ②-e queue/だけが除外されぬ理由 — `.gitignore` の裸directory-whitelist行を特定

```
$ command grep -n "queue" .gitignore
244:!queue/
245:!queue/pane_registry.yaml
```
`!queue/` (244行目) は **個別file/globを伴わぬ裸のdirectory再許可行**。一方 `scripts/design-pipeline/` には
whitelist行が **0件** (`command grep -n "design-pipeline" .gitignore` → 無出力)。

### ②-f ★核心発見★ ugrepはgit自身より甘く解釈する (証拠)

```
$ echo x > queue/_a3_probe.py
$ git check-ignore -v queue/_a3_probe.py
  .gitignore:7:*    queue/_a3_probe.py         ← git は「除外されている」と判定 (rc=0)
$ git add --dry-run queue/_a3_probe_check.py
  fatal: pathspec ... ignored by one of your .gitignore files    ← git add も拒否
$ grep -rl "^x$" queue/_a3_probe.py             → 発見 (exit=0)   ← ugrep(wrapped)は「除外されていない」と判定
```
**git本体は`queue/_a3_probe.py`を「無視対象」と一貫して判定する(check-ignore・add両方)。
然れどugrep(--ignore-files)はこれを無視せず発見する。** ∴ `!queue/`のような裸dir-whitelist行を、
ugrepは「配下を再帰的に全許可」と解釈し、gitの「dir traversalのみ許可・file単位は別途要whitelist」という
本来の意味論より甘い側に踏み外している。

## ③ 影響範囲 — `!queue/` は孤例ではない

`.gitignore`全429行中、個別glob narrowingを伴わぬ裸の `!dirname/` 行を機械的に列挙したところ **70件**
(`command grep -nE '^![^*]+/$' .gitignore`)。内訳の主要例——`.claude/` `instructions/` `lib/` `config/`
`shim/` `backend/` `templates/` `context/` `scripts/` `scripts/lib/` `scripts/checks/` `saytask/` `memory/`
`docs/` `queue/` `images/` `skills/` `tests/` `android/` 等。

**未測**: 上記70件全てが `!queue/` と同じ「ugrep側は再帰全許可」の挙動を示すかは、本便の期限内では
1件ずつ個別実証しておらぬ。∴ ★推して「70件とも同じ」と断ずるな★——`queue/`と同型の
「配下に個別globが一切続かぬ純粋な裸dir行」という条件が同じ効果を及ぼす**可能性**を示すに留める
(構造的類似のみ・個別実証は未測)。

## ④ 実害の射程 — 当職の元claimへの適用

`_create_all_appointment_tables` 探索の対象は `.py` file。`.py` fileがugrep側で
「dir丸ごと再許可」扱いを受けている場所(queue/等)は、通常 `.py` を含まぬ運用dir。∴ **今回の個別claimは
実害を免れたが、それは偶然(対象文字列が該当し得るdirの性質と、除外を免れるdirの性質が重ならなかった)であり、
方法論として安全であったからではない**。

## ⑤ 新たに開ける穴

- 本findingの「再検証(command grep で615 .py file全数)」自体も、**手動で1回叩いただけ**であり、以後
  当職や他の足軽が再び `grep`(裸)を使えば同じ穴に落ちる。恒久策(alias/wrapper是正・CLAUDE.mdへの明記)は
  当職の権限外。
- 70件の`!dirname/`行の個別実証を行っておらぬため、「除外が起きぬ場所」の全量は**未確定**。
  ここを「安全」と誤読すれば、当職が本便で示した誤読と同型の誤りを別の探索対象で再演し得る。
- probe fileの生成・削除は本人(当職)による手動確認のみ。第三者による`git status`再確認は未実施。

## 判じ難き・未測

- ugrepの正式仕様書(`--ignore-files`の`.gitignore`解釈アルゴリズム)は未参照(オフライン不可・当職はソース読取のみで挙動から逆算した)。
  ∴ ★「なぜそう実装されているか」は未測、「現にそう振る舞う」は実証済み★という区別で書いている。
- 70件のうち何件が実際に同型挙動を示すかは未測。

## 禁則遵守の確認

一本も破壊的操作なし。probe fileは全て生成直後に削除・`git status --porcelain`で残留無きこと逐次確認。
既存file(extract_prototype.py)への追記は同一シェルセッション内で即時復元し`diff`で一致確認。
hakudokai-dev/newbuildへは一字も書いていない。rcはpipeに通していない(各コマンド単発実行・`$?`直読)。
`/usr/bin/grep -r`相当は`command grep`で明示。

---
断面: 2026-08-06T11:23:30+0900 (機械) ／ HEAD=`3f932aa69873507536d1b5085476186d6a7ee5fc` ／
参照=queue/inbox/ashigaru3.yaml sha256=`904a51b1426fcc7bb9d54f07ea75dea75a5fd5fb7fc6185c03417f868a5a63ea`、
.gitignore sha256=`c46f5b5dd50ce02644a589c4685bce10491cdb67054d46ebb06f6bbd711642a4`、
元claimの元file=2026-08-06_reserveimage_cycle2_f2_design_adversarial_review_a3.md
sha256=`aa49d0785043d0f02a0e0d89cdcba219ab6363d93f905e845c3cfb7357501084`。
提出先: 家老second + 軍師second。
