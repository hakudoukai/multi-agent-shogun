# km-221 ── 走る器の .bak 除外が -bak- 形を見ぬ疵を閉ぢる

task_id: km-221-hashiru-ki-no-bak-jogai-ga-hasami-bak-wo-minu-kizu-wo-tojiru-20260920
担当: ashigaru-mac-1 ／ 命: karo-mac (msg_20260920_050554_50b2ff3b)

★①(ref/commit/tree)は本紙に書かず、納め便(karo-mac 宛 inbox_write)へのみ記す(雛形v1.3 §1)★

## 0. 母數の函数(歩き根・深さ・刻を先に宣す)

karo-mac の落度⑶(歩き根を宣さぬ数は読手が検められぬ)を承け、両走とも以下を固定して走らせた:

- 歩き根 = `.` (cwd = `/Users/momizimac/multi-agent-shogun` ―― 両走とも同一cwd、raw=`10_old_run.cwd.txt`/`11_new_run.cwd.txt`)
- 深さ = 無制限(`os.walk` 全深・`SKIPDIR` で枝刈りされた部分のみ除く。§4 参照)
- 刻(旧器) = 2026-09-20T05:09:05+0900 (raw=`10_old_run.timestamp.txt`)
- 刻(新器) = 2026-09-20T05:09:10+0900 (raw=`11_new_run.timestamp.txt`)
- argv(旧器) = `python3 <OLD_PATH> .` (raw=`10_old_run.argv.txt`)
- argv(新器) = `python3 <NEW_PATH> .` (raw=`11_new_run.argv.txt`)

## 1. 旧器の固定(fail-closed sha256 pin)

karo-mac の落度⑴の通り、旧器の束
`docs/evidence/karo-mac_agent-status-maehou-ichi-wo-haisu-20260919/` は
HEAD (`a02391d8deca9b176644ea0a1f188a91dd09e38c`) で `git ls-tree -r HEAD -- <束>` = **0件**、
すなわち ★git の何處にも無い(悉く追跡外)★。∴ commit による固定は不可能、sha256 で固定した。

當職が自らの器で取り直した値:

| 項目 | 家老mac declared | 當職が取り直した値 | 一致 |
|---|---|---|---|
| sha256 | `956c4669d99ba1b60bd707252f7d36ac726e5c1e3d8e05024d779f94cbf9a6a2` | 同左 | ✅ |
| 行 | 67 | 67 | ✅ |
| bytes | 3504 | 3504 | ✅ |

★一致を得たので走らせた(fail-closedの手前を通過)★。旧器の本体は一切編輯していない
(kinshi⑵順守)。

## 2. 旧器を其の儘走らせた値(⑴)

raw: `10_old_run.{cwd,argv,timestamp,stdout,stderr,rc}.txt`

```
rc(歩行)  = 0
全file    = 35293
器(実行bit or 拡張子, .bak除) = 2436
読めた    = 2436
器でない  = 32857
```

疵の実体(karo-mac 指摘・當職が逐語で再確認): `kiki/km_tmux_census2.py:38`
```
if '.bak' in p or p.endswith('~'): skipped_ext+=1; continue
```
対象 `./shutsujin_departure.sh.karo-mac-bak-20260820T000340` は文字列 `.bak` を含まぬ
(`.karo-mac-bak-` であり `.bak` という4文字の連続部分列を持たぬ)。∴ 旧器の除外に掛からず、
★走る器の母数(器=2436)へ入る★。

## 3. 新器を作り三形へ拡げた値(⑵)

旧器は編輯せず(kinshi⑵順守)、新器 `kiki/km_tmux_census2_bakfix.py` を
本束の中に新規に作つた(sha256=`c447a028548951384994569427415ffb0d2008b93c90b79501cbf99e84c959dd`、
123行/6048bytes)。旧器の甲/乙/丙/丁 census 本体は不変、変更点は行38相当の除外条件を
三形へ拡げた一点のみ(+三形の hit 計測を追加)。

除外三形: `.bak` (form1・旧器と同じ) / `.bak-` (form2) / `-bak-` (form3・今回追加)。

raw: `11_new_run.{cwd,argv,timestamp,stdout,stderr,rc}.txt`

```
rc(歩行)  = 0
全file    = 35293
器(実行bit or 拡張子, bak三形除) = 2435
読めた    = 2435
器でない  = 32858
```

### 3.1 三形の排他性(★排他でない事を数で示す★・karo-mac 落度⑵型の再発防止)

```
form1(literal '.bak')  hit件数=21 実本数=21
form2(literal '.bak-') hit件数=21 実本数=21
form3(literal '-bak-') hit件数=1  実本数=1
和集合(いずれか1つ以上を含む) 実本数=22
排他性: form1∩form2=21本 / form1∩form3=0本 / form2∩form3=0本 / 三形全交差=0本
```

★∴ 三形は排他でない★ ―― form1(`.bak`)に当たる21本は悉く form2(`.bak-`)にも当たる
(form1⊆form2、この母数では完全重複)。form3(`-bak-`)は独立に1本のみ当たり、
form1/form2 のいずれとも重ならない。単純に `21+21+1=43` と数へるのは誤りであり、
実本数(和集合)は `22` である。重なる21本の逐語は `11_new_run.stdout.txt:165-185`
(`form1=True form2=True form3=False` の各行)に有る。

## 4. 差の逐語(⑶)

旧器の母数(器=2436)に入り、新器(器=2435)で抜けた file を名指しで全部列挙する:

```
./shutsujin_departure.sh.karo-mac-bak-20260820T000340  form1=False form2=False form3=True
```

**1本のみ**。二つの独立な方法で交差検算した:

- 方法A(直接列挙): `newly_excluded` リストの長さ = 1 (`11_new_run.stdout.txt` 末尾セクション)
- 方法B(集計算術): 旧器の n_ki(器) `2436` − 新器の n_ki(器) `2435` = `1`
  (対応して 器でない側も `32858 − 32857 = 1` で符合)

両者一致(A=B=1)。karo-mac の落度⑵(hit件数と本数を混同した誤り)を承け、
本紙では「本数」と「hit件数」を常に別欄で書いた(上の逐語行にも form ごとの
hit真偽を併記)。

## 5. .git 配下を歩くか歩かぬかの実測(⑷)

旧器・新器とも `SKIPDIR = {".git", ...}` により `os.walk` の `dns` から
`.git` という basename のディレクトリを毎階層で除く実装(旧器母束の
`km_tmux_census2.py` および當職の新器で共通)。これを推論だけでなく
実測(陽性・陰性対照)で確かめた:

```
cand_all中 '.git/' を含む path の本数 = 0
陽性対照 .git/logs/refs/heads/ashigaru-mac-1/km-181-mitsu-no-naoshi-kagyaku-bak-futekisuto-20260918 が cand_all(全歩行file)に在るか = False
陰性対照 CLAUDE.md が cand_all(全歩行file)に在るか = True
cand_all 総数 = 35399
```

陽性対照(`.git/logs/...bak-futekisuto-20260918`、karo-mac が name-order で示した既知の
`.git` 内 bak 系ファイル)は母数(`cand_all`)に **不在**(False)。
陰性対照(當職が自ら選んだ `CLAUDE.md`、repo 直下の在る file)は母数に **在る**(True)。
∴ `.git` 配下は歩かれない ―― 実測で確認、推論のみに拠らなかった。

(`cand_all` = 全歩行file 35399 は、器判定(拡張子/実行bit/bak除外)前の
歩行結果そのもの。器判定後の `全file` 表示 35293 とは異なる母数である ――
`35399` は `os.walk` が返した全candidate、`35293` は `os.path.isfile` かつ
非symlinkのみに絞つた後の数。この差 106 はディレクトリエントリ・symlink・
非通常ファイルの除外による。)

---

## ② 成果物(repo-relative path / sha256 / bytes / lines)

| 種別 | path | sha256(64桁) | bytes | lines |
|---|---|---|---|---|
| 新器 | `docs/evidence/ashigaru-mac-1_km-221-bak-jogai-no-kizu-20260920/kiki/km_tmux_census2_bakfix.py` | `c447a028548951384994569427415ffb0d2008b93c90b79501cbf99e84c959dd` | 6048 | 123 |
| 紙(本紙) | `docs/evidence/ashigaru-mac-1_km-221-bak-jogai-no-kizu-20260920/km-221-hashiru-ki-no-bak-jogai-no-kizu-20260920.md` | ★本紙自身の sha256 は納め便へ記す(v1.3追補3・自己言及不可)★ | ― | ― |
| 臺帳 | `docs/evidence/ashigaru-mac-1_km-221-bak-jogai-no-kizu-20260920/km-221-manifest.txt` | (manifest 作成後、納め便へ記す) | ― | ― |

## ③ 実走の raw

| 走 | cwd | argv | rc | raw stdout(path/sha256) |
|---|---|---|---|---|
| 旧器 | `/Users/momizimac/multi-agent-shogun` | `python3 docs/evidence/karo-mac_agent-status-maehou-ichi-wo-haisu-20260919/kiki/km_tmux_census2.py .` | 0 | `10_old_run.stdout.txt` / `36dd2baa49480be0a3673914c565b4c4ab829f1fa109e81c18e318d2cce682ae` |
| 新器 | `/Users/momizimac/multi-agent-shogun` | `python3 docs/evidence/ashigaru-mac-1_km-221-bak-jogai-no-kizu-20260920/kiki/km_tmux_census2_bakfix.py .` | 0 | `11_new_run.stdout.txt` / `39a74388a8d7d4f71542b2e5db979ee51585d82e586e082b44c719fa370da5fa` |

stderr は両走とも空(sha256=`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`、
これは SHA-256 の空文字列の既知値と一致 ―― 空で正しい)。

## ④ 依存境界

lockfile = N/A(理由: 本弾は素の Python3 標準ライブラリ(`os`/`sys`/`re`/`io`/`stat`)のみを
使ふ単一script、外部パッケージ依存無し)。外部 node_modules 参照 = 無し。外部 symlink 参照 = 無し
(新器・旧器とも symlink は `os.path.islink` で明示的に skip、`os.walk` 自体は
`followlinks=False` が既定でありディレクトリsymlinkも辿らない)。

## ⑤ 件数

- 正(N/N) = 差分1本の検出 ―― 方法A(直接列挙)=1 / 方法B(集計算術)=1、両者一致 `1/1`
- ★意味負★(M/K、非自明な否定) = 三形の非排他性 ―― `form1∩form2=21` は「重ならない」という
  自明でない仮説を反証する非自明な負(21本が実在して重なる、ゼロではない)。
  `21/22`(和集合22本中、form1とform2が重なる21本)。
- 陽性対照 = `.git/logs/refs/heads/ashigaru-mac-1/km-181-...-bak-futekisuto-20260918` が
  母数に不在(False) ―― 期待通り(`.git`はSKIPDIRで刈られる)。
- 陰性対照 = `CLAUDE.md` が母数に在(True) ―― 期待通り(repo直下の通常fileは歩かれる)。

## ⑥ 復元性

新器を新規に作つた故、復元検査が必要。下記コマンドで検査する(結果は納め便で報告、
gate 実走後に本項へ追記):

- 復元後 sha256 一致(新器を再度読み込み、上記②の値と一致するか)
- `git status --porcelain -uall --ignored` の行数(★-uallと--ignoredの両方、片方のみでは
  この repo の `.gitignore` 行7=裸の `*` により偽clean になる★)
- 再正 N/N(gate再走で同じrcが得られるか)

## ⑦ 法令根拠

N/A(理由: 本弾は repo 内の開発支援ツールの疵検出・修正であり、法令・規制の適用対象では
ない。患者情報・医療記録は一切不触)。

---

## 禁止事項の順守

- `scripts/` 配下・他席の器は読取のみ、一指も触れず。
- 旧器 `km_tmux_census2.py` は編輯せず(證の紙として不変のまま)。
- push / PR / gh / merge / git reset は一切実行せず。commit は自枝へ `git add -f` で
  名指し、`git commit --only` で行ふ(本紙の後、gate通過後に実施)。
- 他席の yaml・箱・枝・HEAD・index には触れず(読取のみ)。
- 證の紙は `/tmp` に置かず(全て本束 `docs/evidence/.../` 内に直接生成)。
- 破壊的操作(Tier 1 D001-D008)は実行していない。
