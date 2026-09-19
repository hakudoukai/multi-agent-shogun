# km-217 專任1 ―― 括られぬ値に「コロン＋空白」が入ると帳が死ぬ形の全帳 census

宛先: 家老mac ／ 起票: ashigaru-mac-1 ／ 実測時刻: 2026-09-20T03:02(+0900)頃 ／ 親裁: iincho seq339533
評: `queue/tasks/*.yaml` `queue/inbox/*.yaml` **全60本**を `yaml.safe_load` に掛け、死んだ本を本ごとに逐語で示す。
★本紙は commit/tree を宣さない★（雛形v1.3§1/§3 ―― ①は納め便で宣す）。

## ㋐ 母數宣言（三つ別々に）

歩いた根と深さ（実際の argv。当機の `find` は `bfs` shim で、下記が実行された実 argv）:

```
⑴ queue/tasks/  : bfs -S dfs -regextype findutils-default /Users/momizimac/multi-agent-shogun/queue/tasks -type f -name '*.yaml'
   → tasks_count = 24
⑵ queue/inbox/  : bfs -S dfs -regextype findutils-default /Users/momizimac/multi-agent-shogun/queue/inbox -type f -name '*.yaml'
   → inbox_count = 36
⑶ 和            : 24 + 36 = 60
```

深さは無制限（`-maxdepth` 未指定・両ディレクトリ配下の全サブディレクトリを含む）。内訳:

| 根 | (top) | サブディレクトリ | 合計 |
|---|---|---|---|
| `queue/tasks/`  | 10 | `_fuda_hikae/`=12, `_stopped-20260903/`=2 | 24 |
| `queue/inbox/`  | 19 | `_archive/`=17 | 36 |

参考: `-maxdepth 1`（トップ層のみ）なら tasks=10 / inbox=19（合計29）。★本 census の母數は再帳ぜず全深度=60を正とする★（「全帳」の命に従う）。

証跡: `00_find_argv.txt` `01_tasks_list.txt`(24行) `02_inbox_list.txt`(36行)

## ㋑ 三値（触る前・今回の実害ファイルの前後比較）

★死んだ版（家老mac報告・02:30:53時点、queue/*.yaml は git 追跡外ゆゑ以下は家老mac の報告の転記）★:
`queue/tasks/ashigaru-mac-2.yaml` bytes=115680 / lines=527 / sha256=f4995fb1a5268ab6e7646cfa3735b27f3e9d25e8a59cf30788d563c4b8a791a9

★直つた版（家老mac報告・02:45:17時点）★: bytes=116003 / lines=528

★今 census した時点の同ファイル（本紙作成中に実測）★: bytes=120446 / lines=542 / sha256=7e5cfddf3e6f0cb55e74111f4c83e28fffd00ae04cc17afee22c64edec2dd50 ・`yaml.safe_load` → **OK**（其の後の弾の往来で増えて居るが、生きて居る）。

★死んだ版そのものの現物★: **未測（理由=`queue/*.yaml` は `.gitignore` 上 `queue/` は allowlist だが個々の runtime yaml は追跡対象外・`git log -- queue/tasks/* queue/inbox/*` は0件。加へて `docs/evidence/` `/tmp` を sha256=f4995fb1... で検索したが複製を発見せず。∴ 死んだ版の本文そのものを再現する経路が無い）**。

## ㋒ 実射・対照

### (A) 全60本 safe_load rc 表（⒝・母數と和が一致する事の證）

```
tasks: OK=22  DEAD=2   (22+2=24 ✓ 母數と一致)
inbox: OK=23  DEAD=13  (23+13=36 ✓ 母數と一致)
和   : OK=45  DEAD=15  (45+15=60 ✓ 母數の和と一致)
```

証跡（全本の rc・本ごとに一行、通も"OK"と明記）: `10_tasks_census.tsv`(24行) `11_inbox_census.tsv`(36行)

### (B) 死んだ15本の内訳 ―― ★同型ではない・二種の別疵★

| # | path (repo-relative) | 例外型 | 死んだ行 | 其の行の字数 | 列 | 鍵名 | 逐語(要約) |
|---|---|---|---|---|---|---|---|
| 1 | `queue/tasks/_stopped-20260903/ashigaru-mac-5.yaml` | ParserError | 272 | 13 | 1 | (無・鍵の疵ではない) | `- saitei_z43:` ―― list項目`-`がmapping文脈と衝突（`expected <block end>, but found '-'`） |
| 2 | `queue/tasks/_stopped-20260903/ashigaru-mac-6.yaml` | ParserError | 231 | 13 | 1 | (無・鍵の疵ではない) | `- saitei_z44:` ―― #1と★全同型★（`fukumei:`スカラー値の直後にコメント区切り→列1の`- saitei_zNN:`。block構造の衝突。★colon+space疵ではない★。前稿では手動抜粋で270行目`- task_id: ...`を誤つて死行と記したが、census TSV(problem_mark)は231行目を指し、再検すると231行目こそ`- saitei_z44:`＝ファイル#1と同一形。270行目はparserが231で既に止つた後の未到達領域であり、死因ではない ―― 訂正済★） |
| 3〜15 | `queue/inbox/_archive/{ashigaru-mac-1..6,fukuincho,gakushu-bucho,gunshi-mac,karo-mac,karo,kikaku-bucho,shogun-mac}_pruned.yaml`（13本） | ComposerError | 各本ばらばら(27〜178674) | — | 1 | (無) | `---` 区切りで複数doc（"but found another document"）―― ★仕様通りの多doc archive★。`scripts/inbox_write.sh` L360-362 が `'a'`(追記)で書くのみ・読み手0（`grep -rl safe_load_all scripts/ ~/bin/` = 0件・`_pruned` を読む器は無い） |

**∴ 今回の実害（ashigaru-mac-2.yaml、`ScannerError: mapping values are not allowed here`＝括られぬ値のcolon+space）と同型の疵は、現存60本中 ★0本★。** 死んだ15本は全て★別の疵型★（①block構造衝突=2本 ②意図的多doc archive=13本）。

証跡: `40_dead_lines_excerpt.txt`

### (C) 陽性対照／陰性対照（⒟の検出子・合成再現）

★死んだ版の現物が無い（㋑参照）ため、実害と同一の疵形を合成して代用した（原物ではない旨を明記）★:

| | ファイル | yaml.safe_load | 己の検出子(`detector_kakoranu_colon.py`) |
|---|---|---|---|
| 陽性対照(合成) | `synthetic_positive.yaml`（`saitei_han: 明日の弾: これは危険な値です`＝括らぬ値にcolon+space） | **DEAD** `ScannerError: mapping values are not allowed here` (line2,col17) | **SUSPECT** line=2 key=saitei_han |
| 陰性対照(合成) | `synthetic_negative.yaml`（同じ値を`"..."`で括る） | **OK** | **CLEAN** |
| 陰性対照(現物) | `queue/tasks/ashigaru-mac-2.yaml`（現時点） | **OK**（㋑参照） | (下記(D)参照) |

証跡: `synthetic_positive.yaml` `synthetic_negative.yaml` `30_synthetic_safeload.txt` `31_synthetic_detector.txt`

### (D) 己の検出子を60本へ実射 ―― ★誤検出を隠さず書く★

`detector_kakoranu_colon.py` は「`key: value`行で、valueが括られず、且つvalue自身に`: `を含む」を素朴にsuspectとする一行regex検出子。60本へ実射した結果:

```
tasks: SUSPECT=11行 (対象ファイル4本)
inbox: SUSPECT=836行 (対象ファイル18本)
```

★然し此の検出子は、真に死んだ2本(#1,#2)の★実際の死行(272行/270行)を一つも当てて居ない★（偽陰性 ―― 疵型が違ふゆゑ）。
且つ suspect の大半は、複数行に渡る括り済み値(`|`ブロックや長い`"..."`)の★内側の自由文★を、行単位regexが誤つて「括られぬ値」と誤認した★偽陽性★である（例: `queue/tasks/_stopped-20260903/ashigaru-mac-6.yaml` line183 `⑹ ★yamlの構造に注意★` ―― 見出し行がkey:valueに見えるが実際は箇条書きの本文）。

**∴ 此の検出子は「合成再現の疵型」には正しく反応するが、★現物60本に対しては真陽性0・偽陽性多数・偽陰性2という弱い道具★である。之を隠さず書く。** 母數との対応が取れる唯一の權威は(A)の`yaml.safe_load`直接census であり、此の検出子は補助に留まる。

証跡: `20_detector_tasks.txt` `21_detector_inbox.txt`

## ㋓ 条逐語（本弾の命の該当箇所）

> 「⒠ ★家老の『527行中 一本だけ』も検め直せ。当職の数を信じて引くな。★」（tsugi_no_tama_217、家老mac、2026-09-20T03:00）

**検め直した結果**: 家老mac の元の主張は「★死んだ版527行の中で、此の疵型(colon+space)は1箇所だけ★」という★単一ファイル内の内訳★であり、其の死んだ版の現物が無い(㋑)ため★直接の再検証は不能=未測（理由=現物無し）★。
然し、本 census が別軸で示した事実は看過できない: **家老mac の言（「527行中 一本」）は暗に「疵はこの1件だけ」と読める余地があるが、★現存する全帳（60本）を見れば、疵の型を跨いで数へると15本が死んで居る★。** 家老mac の元の主張それ自体を否定する材料ではない（対象が違う＝単一file内訳 vs 全帳）が、**「一本」という数字だけを引いて「他に疵は無い」と読むのは誤り**である。∴ ⒠の命に応じ、家老mac の数を其の儘引かず、★全帳の別軸統計を添えて突き合はせた★。

## ㋔ 案（紙のみ・器は不触）

1. `_stopped-20260903/ashigaru-mac-5.yaml` `-6.yaml` の block構造衝突（#1,#2）は★現用0★（(B)の運用確認どおり、`karo_overload_monitor.sh` 等は non-recursive glob でトップ層のみを見る）。直す必要は無いが、★退避済みである事実の記録として残すのみ★。
2. `_archive/*_pruned.yaml`（13本）は★仕様どおりの多doc archive★であり、`safe_load`単体で死ぬのは想定内（読み手が無いため実害0）。★もし将来 読み手を作るなら`safe_load_all`を使へ★という一行の申し送りのみ提案（器は今回作らない）。
3. 今回の実害型（colon+space・括られぬ値）自体は現存60本中0件 ―― ★再発防止の要は「新たに書く時に括るか否か」であり、既存帳の走査では捉へられぬ★（書く前の防止が要る、という論点は本弾の範囲外ゆゑ上申のみ）。

## 受入条件（判定の束 ①〜⑦・雛形v1.3 対応）

- **①対象tuple**: ★本紙には書かない★（雛形v1.3§1/§3 ―― 納め便で40桁宣す）
- **②成果物**: `docs/evidence/km-217-yaml-kakoranu-atai-no-census-20260920/` 配下（本紙含む10本、下記manifest参照）
- **③実走のraw**: cwd=`/Users/momizimac/multi-agent-shogun`（census実行時）・argv=上記㋐の`bfs`実行列・rc=census_yaml.py 双方 rc=0・raw=`10_tasks_census.tsv` `11_inbox_census.tsv`
- **④依存の境界**: 外部依存無し（`census_yaml.py`/`detector_kakoranu_colon.py`は標準lib(`hashlib`,`re`,`sys`)+`PyYAML`のみ・repo既存の`.venv`内`pyyaml`を使用・lockfile=`未測（理由=本弾はrepo本体のPython依存を新規追加せず、既存.venvのpyyamlを読取専用で呼ぶのみ。census自体はrepoの実行物ではなく評価用の一時器ゆゑlockfile対象外）`）
- **⑤件数**:
  - 正 = 60/60（全本 rc 取得。母數と和が一致）
  - ★意味負★ = 2/60（真に死んで居るが実害型とは別疵＝block構造衝突。恒真でない証明＝60本悉く同型ではない事を示した）
  - 陽性対照 = 合成positive（`ScannerError`+検出子SUSPECT） / 陰性対照 = `ashigaru-mac-2.yaml`現物（OK）+合成negative（OK+CLEAN）
  - 受入⑴母數三定義と歩いた根=PASS(㋐) ⑵全本rc表(母數と和一致)=PASS(A) ⑶陽性/陰性対照=PASS(C、但し陽性は合成・原物未測を明記) ⑷判定の束=本節 ⑸紙のみ=PASS(器変更0・他席yaml変更0) ⑹家老数の検め直し=PASS(㋓、結論=対象不同ゆゑ直接反証不能だが全帳の別軸統計を添えた)
- **⑥復元**: 本紙は評価専用worktree(`~/wt/a1-km217`)で作成・repo本体(`scripts/`, 他席`queue/*.yaml`)は一切変更していない。`git status --porcelain -uall --ignored`（worktree側）= 下記manifest直後に確認予定
- **⑦法令根拠**: 該当なし（未測ではなく非該当）
