門 rc=0 ／ 母數=★本席の割当 枝 14 本★・★臺帳 46 行★ ／ 條①=一致 46(相違 0・実体無 0・讀めぬ行 0・manifest_verify.py rc=0) ―― 出す前門を `KM_GATE_MANIFEST_BASE=.` 付きで★束の中から★通した(裁 seq322699)。★最終巡=本行を焼いた後★の出目(`_gate/05_gate.*`)。

# km-102 ―― 枝四十五の着地仕分け(家老mac の枝・後半 14 本)

- 席 = ashigaru-mac-3(專任3) / bloom L5 / 的 = ★「此の枝を着地させるか、捨てるか」一件のみ★
- task_id = `km-102-eda-yonjuugo-no-chakuchi-shiwake-karo-kou-20260917`(札 sha256頭16=`83f0383f919915cf` 64行 5323B)
- 親 = 委員長裁 seq325884(親 325872) ―― 枝削除は★不可逆削除＝理事長専管★ゆゑ★消さない★
- ★此の弾で枝を一本も消して居らぬ★。checkout / merge / rebase / cherry-pick / push / fetch / refs 書換 ―― 悉く行つて居らぬ。git は ★読取のみ★(`cat-file` `diff` `rev-list` `ls-tree` `show` `ls-remote --heads`)。PR は起票して居らぬ。他席の pane は覗いて居らぬ。

## 一言 ―― 14 本 悉く ★甲(着地させる)★。乙=0・丙=0

★之は「14 本を悉く PR せよ」の意では★ない★★。
下の五つの拠り所(丙①丙②乙①乙②乙③)は ★「捨ててよい」と言へる形★ を五通り並べた物であり、14 本は其の何れにも当たらなかつた ―― 即ち ★「捨ててよい證が一つも立たなかつた」★ である。「着地させるべし」の積極的な證ではない。是非の判定は軍師mac の職(裁 325884)。

## ㋐ 母數 ―― 14 本・物は悉く手許に在る

- 割当 = 14 本(札 `eda_warimochi` 逐語)。`raw/11_bogen.tsv` に full sha40 を逐語で列べた。
- `git cat-file -e <sha>^{commit}` rc=0 が ★14/14★・object_type=commit が 14/14・sha40 と `rev-parse` の一致 14/14。
- ★家老の臺帳を鵜呑みにせず己で数へた★: `git ls-remote --heads origin`(★fetch ではない・読取★)で mac の枝を数へ、家老臺帳 `karo-mac-eda-fuyou-20260917/raw/20_mac_eda.tsv` と突き合はせた ―― ★60/60 一致★(`raw/21_roster.tsv` 突合欄=一致 60 本)。

## ㋑ 二つの差分 ―― ★混ぜて居らぬ★

`raw/31_sokutei.tsv` が生の數。★⑴と⑵は別の問である。★

### ⑴ 対 origin/main

`git diff --name-only 4be3ee19e1c5...<sha>` の行数。★此の數が意味せぬ事(数の規律3)★:

- ★「此の枝が変へた file 数」では★ない★★。`A...B` は git の定義上 ★merge-base(A,B) から B まで★ の片側であり、★origin/main が此の系譜に対して何 file 遅れて居るか★ を言ふ。
- 出目 = ★6〜1167★(中央値辺り 524)。之は「各枝が 524 file 触つた」ではなく ★分岐点から枝の tip までに積まれた file の総数★ である ―― 同じ系譜に乗る枝は同じ古さを何度も数へ直す。
- ★枝同士の大小比較に使ふな。★ 現に最小 6(lot48235904)と最大 1167(km-88)の隔たりは「仕事量が 194 倍」ではなく ★乗つて居る系譜が違ふ★ 事を映して居るに過ぎぬ(lot48 の基点のみ `manifest-verify-20260909`・他 13 本は `km-gate-kou-otsu-20260917`)。

### ⑵ ★自前★の差分

60 本の tip の内 ★其の枝の真の祖先★ である物を悉く挙げ、`git rev-list --count B..X` が最小の B を基点として `git diff --name-only B..X` を数へた(`raw/31_sokutei.tsv` の`(2)kiten_eda` が其の B)。★測れた = 14/14・測れぬ = 0★。

- 13 本は基点が `karo-mac/km-gate-kou-otsu-20260917`、lot48235904 のみ`karo-mac/manifest-verify-20260909`。祖先 tip は各 9 本(lot48 は 5 本)在り、★最小を選ぶに当たつて同点(tie)は 0 件★ ―― 基点は一意に決まつた(`tie_kazu`欄)。
- path の数へは ★`-z`(NUL 区切)★ で取つた。git は非 ASCII path を引用符で括る ∴行数で数へると括られた行を取り零す虞が在る。札の言ふ「行数」も併せて刷り、★両者の食ひ違ひ 0 件★ を `raw/32_chuu.txt` に記した。
- ★⑵ が意味せぬ事★: 「此の枝が正しい」ではない。「此の枝しか触つて居らぬ」でもない(同じ file を触る他枝は ㋕ に列べた)。★基点から先に在る file の数★ ―― 其れだけである。

### ㋑補 ―― ★乖離は両側に在る★(⑴ は片側しか言はぬ)

⑴ は片側ゆゑ ★main が己の向きへ何 file 進んだか★ を一切言はぬ。測らねば「main は遅れて居るだけ」と誤読する ∴ 測つた(`driver/35_ryoumuki.py` /`raw/36_ryoumuki_main.txt` / `raw/37_ryoumuki.tsv`)。

- ★14 本の分岐点は悉く一点★ = `6e9d40600a80`(2026-09-08)。
- 其処から ★main は 21 commit・14 file 進んで居る★ ―― 即ち ★此の 14 本は悉く main より 21 commit 遅れて居る★(⑴ が言ふ「main が遅れて居る」の★裏側★)。
- ★然らば衝突するか★: 各枝の ⑵(自前 path)と main 側 14 file の交はりを数へた ――★交はる枝は 2 本のみ★。
  - `km-82-hata-ni-wa-hata-no-bannin-wo-20260917` ―― 1 件: `scripts/inbox_watcher.sh`
  - `lot48235904-provenance-20260916` ―― 1 件: `scripts/checks/karo_mac_manifest_verify.py`
- 残り 12 本は ★main が動かした file を一つも触つて居らぬ★ ∴ ★main 側との衝突は無い★(後は下の ㋕ の枝同士の重なりのみ)。
- ★此の數が意味せぬ事★: 交はり 0 は ★「そのまま merge できる」ではない★。同じ file を触らずとも意味の上で食ひ違ふ事は在る(例: 一方が器を動かし他方が其の器を呼ぶ紙を書く)。★path の交はりだけを言ふ。★

## ㋒ commit 数と領域

`raw/31_sokutei.tsv` の `(1)commit_main` `(1)ryouiki` `(2)ryouiki`。

| 枝 | ⑴ | ⑵ | commit(対main) | ⑵の領域 |
|---|---|---|---|---|
| `km-80-utsuwa-ga-uketa-na-wo-bannin-hyou-he-noseru-mae-ni-hakare-20260917` | 539 | 75 | 17 | docs |
| `km-81-hook-no-jigen-wo-onaji-enzanshi-de-kenme-20260917` | 486 | 22 | 17 | docs scripts |
| `km-81b-bannin-zero-no-ratelimit-check-20260917` | 542 | 78 | 17 | docs |
| `km-82-hata-ni-wa-hata-no-bannin-wo-20260917` | 500 | 36 | 18 | docs scripts |
| `km-83-shikii-de-wa-mamorenu-tane-wo-mitsuke-yo-20260917` | 846 | 382 | 17 | docs |
| `km-84-hata-no-tane-wo-repo-zentai-de-kazoe-yo-20260917` | 547 | 83 | 17 | docs |
| `km-88-a3-20260917` | 1167 | 703 | 17 | docs |
| `km-89-a2-20260917` | 904 | 440 | 17 | docs |
| `km-90-a1-20260917` | 524 | 60 | 17 | docs |
| `km-91-a3-20260917` | 504 | 40 | 17 | docs |
| `km-hook-no-sotai-path-ga-mon-wo-hiraku-20260917` | 476 | 12 | 17 | docs |
| `km-kansa-daikou-20260913-wo-ref-he-todokeru-20260917` | 484 | 20 | 17 | queue |
| `lot48235904-provenance-20260916` | 6 | 4 | 7 | docs scripts |
| `settings-hook-abs-20260917` | 467 | 3 | 18 | .claude scripts |

- 対 main の commit: 7 commit=1本 / 17 commit=11本 / 18 commit=2本。
- ⑴ の領域は ★三通り★(★14 本悉く同じ、ではない★):
  - `(根).gitignore docs queue scripts` ―― 12 本
  - `(根).gitignore docs scripts` ―― 1 本
  - `.claude (根).gitignore docs queue scripts` ―― 1 本
- ★之も「各枝が触つた領域」ではなく「分岐点から tip までに触られた領域」である。★lot48235904 だけ `queue` を欠くのは、其の枝が別系譜(基点 `manifest-verify-20260909`)に乗つて居るからであり、「queue を触らぬ枝」だからではない。
- ⑵ の領域こそが ★其の枝が齎す物★: 紙のみ 10 本 / 器を含む 4 本。

## ㋓ 仕分け ―― ★拠り所を先に宣してから当てた★

拠り所は `driver/80_shiwake.py` の docstring に ★測る前に★ 書いた(出目を見てから足したり曲げたりして居らぬ)。順に当て ★先に当たつた一つ★ で決める。

| # | 拠り所 | 判ずる欄 | 当たつた本数 |
|---|---|---|---|
| 丙① | 物が手許に無い | `11_bogen` cat_file_e rc≠0 | 0 |
| 丙② | ⑵ が測れぬ(真の祖先 tip 無し) | `31_sokutei` (2)kiten_eda=測れぬ | 0 |
| 乙① | ★末端が運ぶ★(60本中に子孫 tip 在り) | `42_shison` 子孫tip数≧1 | 0 |
| 乙② | 齎す物が無い(⑵=0) | `31_sokutei` (2)file_gyou=0 | 0 |
| 乙③ | 既に main に在る(自前 path 悉く同一 blob) | `51_shitsu` ★mainへ齎す★=0 | 0 |
| 甲 | 上の五つに悉く当たらぬ | ― | ★14★ |

∴ ★甲=14 / 乙=0 / 丙=0★。丙が 0 ゆゑ「何を測れば判ずるか」を書く先は無い。

甲の中の副札は ★着地の順序★ を付ける物であつて甲乙の別ではない ―― 甲-器-要調停 3 / 甲-器 1 / 甲-紙 10。

| 枝 | 札 | 理由(一行) |
|---|---|---|
| `km-80-utsuwa-ga-uketa-na-wo-bannin-hyou-he-noseru-mae-ni-hakare-20260917` | 甲-紙 | 子孫0・⑵=75・mainへ齎す=75 ∴着地要。紙/箱のみ(docs)・衝突0 ∴記録として単独で出せる |
| `km-81-hook-no-jigen-wo-onaji-enzanshi-de-kenme-20260917` | 甲-器-要調停 | 子孫0・⑵=22・mainへ齎す=22 ∴着地要。器(scripts)を触り、同じ file を2本が触る ∴版の先後を糺してから出せ |
| `km-81b-bannin-zero-no-ratelimit-check-20260917` | 甲-紙 | 子孫0・⑵=78・mainへ齎す=78 ∴着地要。紙/箱のみ(docs)・衝突0 ∴記録として単独で出せる |
| `km-82-hata-ni-wa-hata-no-bannin-wo-20260917` | 甲-器-要調停 | 子孫0・⑵=36・mainへ齎す=36 ∴着地要。器(scripts)を触り、同じ file を3本が触る ∴版の先後を糺してから出せ |
| `km-83-shikii-de-wa-mamorenu-tane-wo-mitsuke-yo-20260917` | 甲-紙 | 子孫0・⑵=382・mainへ齎す=382 ∴着地要。紙/箱のみ(docs)・衝突0 ∴記録として単独で出せる |
| `km-84-hata-no-tane-wo-repo-zentai-de-kazoe-yo-20260917` | 甲-紙 | 子孫0・⑵=83・mainへ齎す=83 ∴着地要。紙/箱のみ(docs)・衝突0 ∴記録として単独で出せる |
| `km-88-a3-20260917` | 甲-紙 | 子孫0・⑵=703・mainへ齎す=703 ∴着地要。紙/箱のみ(docs)・衝突0 ∴記録として単独で出せる |
| `km-89-a2-20260917` | 甲-紙 | 子孫0・⑵=440・mainへ齎す=440 ∴着地要。紙/箱のみ(docs)・衝突0 ∴記録として単独で出せる |
| `km-90-a1-20260917` | 甲-紙 | 子孫0・⑵=60・mainへ齎す=60 ∴着地要。紙/箱のみ(docs)・衝突0 ∴記録として単独で出せる |
| `km-91-a3-20260917` | 甲-紙 | 子孫0・⑵=40・mainへ齎す=40 ∴着地要。紙/箱のみ(docs)・衝突0 ∴記録として単独で出せる |
| `km-hook-no-sotai-path-ga-mon-wo-hiraku-20260917` | 甲-紙 | 子孫0・⑵=12・mainへ齎す=12 ∴着地要。紙/箱のみ(docs)・衝突0 ∴記録として単独で出せる |
| `km-kansa-daikou-20260913-wo-ref-he-todokeru-20260917` | 甲-紙 | 子孫0・⑵=20・mainへ齎す=20 ∴着地要。紙/箱のみ(queue)・衝突0 ∴記録として単独で出せる |
| `lot48235904-provenance-20260916` | 甲-器-要調停 | 子孫0・⑵=4・mainへ齎す=3 ∴着地要。器(scripts)を触り、同じ file を8本が触る ∴版の先後を糺してから出せ |
| `settings-hook-abs-20260917` | 甲-器 | 子孫0・⑵=3・mainへ齎す=3 ∴着地要。器(scripts/.claude)を据ゑ、同 file を触る他枝0 ∴単独で出せる |

### ★此の仕分けが答へて居らぬ事★

- 「中身が正しいか」 ―― 拠り所は悉く ★在る/無い・同一/相違★ の話であり是非を問うて居らぬ。
- 「PR に通るか」 ―― ㋔ の受入条件を ★実際に通すまで★ 判らぬ(下記「門 rc は宣し得ぬ」)。
- 「捨てる枝が 0 本」ではない ―― ★此の 14 本には捨ててよい證が立たなかつた★ だけである。

## ㋔ 受入条件 ―― 甲 14 本が PR として通る為に満たすべき条

`raw/91_ukeire.tsv` / `raw/92_taba.tsv`。★checkout せず枝の木を `git show` / `ls-tree` で引いて測つた★(工作樹は汚して居らぬ)。

| 条 | 何を見たか | 出目 |
|---|---|---|
| 甲 束 | ⑵ path が当たる `docs/evidence/<束>/` | 12/14 本が束 1 つ、2 本は束 0(器・箱のみ) |
| 乙 臺帳 | 其の束に `MANIFEST.txt` が枝の木に在るか | 在り 10 / ★無し 2★ |
| 丙 臺帳の根 | 束内相対か根相対か(裁 seq322699) | ★束内相対 10/10・根相対 0★ |
| 丁 門の器 | `scripts/checks/karo_mac_dasumae_gate.sh` が枝の木に在るか | 在り ★14/14★ |
| 戊 臺帳の器 | `scripts/checks/karo_mac_manifest_append.py` が枝の木に在るか | ★在り 0/14★ |
| 己 対照 | 束の file 名 or README に「対照」の字 | 8/12 束 |
| 庚 衝突 | 自前差分で同じ file を触る他枝(`61_kasanari`) | 衝突有り ★3★ 本 |

### ★受入条件(枝毎)★

下の五条は ★悉く満たされて初めて★ PR として出せる。★『満たして居る』と『満たせる』は別である。★

1. **門 rc=0** ―― `KM_GATE_MANIFEST_BASE=.` を付けて束の中から出す前門を通す事。★此の紙では rc=0 と宣し得ない★: 門を通すには其の枝の木が要り、checkout は禁ぜられて居る。∴ ★測れぬ★ と書く ―― 起票する席(監督 lot)が枝毎に通して初めて判る。
2. **臺帳が束内相対** ―― 測れた 10 束は ★悉く束内相対★ で既に満つ。★臺帳を持たぬ 2 束(km-88 / lot48235904)は、出す前に臺帳を立てねばならぬ。★
3. **対照が在る** ―― 「対照」の字が在る束 8 / 無い束 4。★字の在否であつて、対照が★効いて居る★事の證ではない(数の規律3)。★字が無い束は、対照が無いのか名が違ふのか ―― ★其の束を開いて確かめよ★。
4. **main 側との衝突** ―― 分岐点から main は 14 file 動いて居る。其れを触る枝は ★2 本のみ★(km-82=`scripts/inbox_watcher.sh` / lot48235904=`scripts/checks/karo_mac_manifest_verify.py`)。★此の 2 本は main の新しい版の上へ載せ直す事★ が条。残り 12 本は main 側と path が交はらぬ。
5. **枝同士の衝突の始末** ―― 下の ㋕ に列べた通り。

### ★門の器と臺帳の器が main に無い(全席に及ぶ)★

`driver/70_utsuwa_ban.py` で 60 本 + main + disk を一枚に並べた(`raw/71_utsuwa_ban.tsv`)。

- `scripts/checks/karo_mac_dasumae_gate.sh` ―― ★main に無し★。枝に 4 版在る(9cd550fc2cf9=46本 / 54e133c85832=6本 / b0bf5b05eded=2本 / 054c442eaee3=1本)。★disk の版は `karo-mac/km-79-futatsu-no-mon-he-otsu-wo-ateru-20260917` と同一★ ――即ち ★未commit ではない★。
- `scripts/checks/karo_mac_manifest_append.py`(臺帳へ行を足す唯一の器・裁 seq321856) ――★main にも 60 本の枝にも無く、disk のみに在る(未commit)★。∴ 皆が「臺帳は之で建てよ」と命ぜられて居る器が、★何處の ref にも載つて居らぬ★。
- ★`.claude/settings.json` の disk の版も ★何れの枝にも無い(未commit)★★ ――`karo-mac/settings-hook-abs-20260917` を着地させても、disk の今の姿には成らぬ。
- ∴ ★此の 14 本を悉く着地させても、出す前門は main で走らぬ★。門の器を運ぶ枝は★此の組の外★(km-79 等)に在る ―― ★仕分けの順序は、器を運ぶ枝が先である。★

## ㋕ 重なり ―― ★組の中に鎖は一本も無い★

`raw/41_kusari.tsv`(組内の祖先対) / `raw/42_shison.tsv`(60本に対する子孫) /`raw/61_kasanari.tsv`(自前差分の file が重なる対)。

- ★組 14 本の中で tip が他の tip の祖先に成つて居る対 = ★0 対★★。∴ 鎖は描けぬ(`raw/41_kusari.tsv` は 0 行)。
- 更に ★60 本に広げても子孫 tip は 0★ ―― 14/14 本が ★鎖の末端(leaf)★ である。
- ∴ ㋕ の問「★鎖の末端のみ着地させれば足りるか★」の答: ★足りぬ。此の組では一本も畳めない。★ 末端のみ着地させる策は 「A の tip が B に含まれる」時に B だけ出せば A も運ばれる、という理屈で効く。此の 14 本は互ひに祖先関係に無く、各々が基点から独立に 1〜3 commit 生えて居る(兄弟であつて親子ではない) ∴ ★どの一本を落としても其の中身は何處からも運ばれぬ。★

### 但し ★file の重なりは在る★(祖先関係とは別の問)

| 己の枝 | 相手の枝 | 共有 path 数 |
|---|---|---|
| `km-81-hook-no-jigen-wo-onaji-enzanshi-de-kenme-20260917` | `km-91-bannin-no-hikaku-ki-ga-fu-wo-toosu-ana-wo-hakare-20260917` | 1 |
| `km-81-hook-no-jigen-wo-onaji-enzanshi-de-kenme-20260917` | `gate-hook-fix-20260916` | 1 |
| `km-82-hata-ni-wa-hata-no-bannin-wo-20260917` | `km-73-otsu-dash-ichido-no-kane-20260917` | 1 |
| `km-82-hata-ni-wa-hata-no-bannin-wo-20260917` | `km-74-otsu-wo-kyouyuuki-yonhon-he-sueru-20260917` | 1 |
| `km-82-hata-ni-wa-hata-no-bannin-wo-20260917` | `km-shikii-yokotenkai-20260917` | 1 |
| `lot48235904-provenance-20260916` | `a1-r56` | 2 |
| `lot48235904-provenance-20260916` | `daiko-teishutsu-20260916` | 2 |
| `lot48235904-provenance-20260916` | `gate-hook-fix-20260916` | 2 |
| `lot48235904-provenance-20260916` | `hantei-saiteishutsu-20260917` | 3 |
| `lot48235904-provenance-20260916` | `km-79-futatsu-no-mon-he-otsu-wo-ateru-20260917` | 1 |
| `lot48235904-provenance-20260916` | `km-dead-inbox-gate-20260917` | 4 |
| `lot48235904-provenance-20260916` | `km-gate-kou-otsu-20260917` | 1 |
| `lot48235904-provenance-20260916` | `manifest-verify-20260909` | 1 |

- 重なる相手は ★悉く己の組の外★(13 対・内訳欄 己の組=0)。
- ∴ ★此の 14 本は互ひに衝突せぬ ―― 14 本同士は順不同で出せる。★
- 但し組の外とは衝突する: km-81 が `scripts/stop_hook_inbox.sh` で 2 本、km-82 が `scripts/inbox_watcher.sh` で 3 本、lot48235904 が門の器と臺帳照合器で ★8 本★。
- ★lot48235904 は特に手当が要る★: 其の `karo_mac_dasumae_gate.sh` は 6 本が持つ版(`54e133c85832`)であり、★disk の版(`054c442eaee3`)でも、兄弟 13 本の基点が持つ版(`9cd550fc2cf9`・46 本)でもない★。∴ 其の儘着地させると ★門の器が古い版へ戻る虞★ が在る。―― 但し lot48 の齎す物は紙 2 枚(provenance)と器 2 本であり、★紙 2 枚は disk と同一(`51_shitsu` disk同一=2/4)★ ゆゑ、★器を除いて紙のみ着地させる道★ が在る。其の判は軍師mac の職。

## 中身は disk に在るか ―― ★捨てて失ふのは「記録」であつて「bytes」ではない★

`raw/51_shitsu.tsv`。⑵ の path 一本づつを ★枝の blob と disk の中身★ で比べた(disk は純 python で `sha1(b"blob %d\0" + bytes)` を組んで照合 ―― git の index を触らぬ為)。

- ★disk と 100% 同一が 12/14 本★。残り 2 本 = lot48235904(50%)・settings-hook-abs(67%)。
- ∴ ★12 本は「捨てても中身は disk に在る」★。失ふのは ★誰が・何時・何故 其れを書いたか★ ――即ち ★記録★ である。
- ★此の數が意味せぬ事★: 「disk に在る ∴ 捨てて良い」では★ない★。disk は ★一台の Mac の一つの作業樹★ に過ぎず、ref に無い物は ★他の PC へは届かぬ★。上の『臺帳の器が何處の ref にも無い』が其の実例である。

## 門

- 出す前門 `scripts/checks/karo_mac_dasumae_gate.sh` を ★`KM_GATE_MANIFEST_BASE=.` 付き★ で★束の中から★ 通した(裁 seq322699 ―― 臺帳は束内相対)。出目 = `_gate/`。
- 臺帳は ★`cd 束` してから★ `scripts/checks/karo_mac_manifest_append.py` を呼んで建てた。
- 一行目の rc・母數・條① は ★最終巡(一行目を焼いた後)★ の出目である。

## 此の弾で ★己の器を★ 倒した所(隠さず書く)

1. **`ls-tree` は cwd の prefix で絞る** ―― 束の中から `git ls-tree -r -z <rev>` を呼び、rc=0 で ★0 件★ が返つた。束の path は其の木に無いからである。∴ 51 の初版は「disk同一=0・main無=全件」と刷つた。★0% の一致は在り得ぬ★と踏んで検め、`--full-tree` を足し、陽性対照(main の木が 2 件未満 or `CLAUDE.md` を欠けば ★一行も書かず rc=5 で止まる★)を据ゑた。
2. **基点の枝名を rev として使つた** ―― origin の枝は local ref に非ず(手許は 7 本のみ)ゆゑ`fatal: ambiguous argument`。`rev-parse` の rc を捨てて居た ∴ 空の base で diff を取り掛けた。★臺帳(`21_roster.tsv`)から sha を引き、引けねば止まる★ 形へ直した。
3. **内側の loop が外側の loop 変数 `t`(束の名)を潰した** ―― 以後の「対照の字」照合が★臺帳最終行の path★ を束名と見做し、対照欄が 12 本悉く反転した。名を `fld` へ分けた。
4. **臺帳の根の判別を白表(`driver/`|`raw/`…)で書いた** ―― km-83 の臺帳は `10_kuchi/…``40_doku/…` で束内相対なのに白表に漏れ、10 束中 1 束を「別方言」と誤つた。裁 seq322699 が問ふのは ★根から書かれて居るか否か★ の一点ゆゑ ★否定で判ずる★ 形へ直した。
5. **臺帳の列名を `枝` と書いた(実は `相手の枝`)** ―― `KeyError` で器が倒れたが、★倒れた後に awk が前巡の出目を刷つた★ ∴ 画面には正しげな表が出た。`rm` して引き直し、★出目が在るか★ を併せて刷る形にした。
6. **書き器が dict を黙つて呑んだ** ―― `kaku_tsv` の行は list を要するのに dict を渡し、`for x in r` が ★鍵★ を回して ★見出しを 14 回複製した表★ を rc=0 で書いた。★出目が在る事は正しさの證ではない。★ 器へ「list/tuple でなければ撥ねる」門を据ゑ、★dict を渡して止まる事を確かめてから★ 引き直した。
7. **「測れぬ」と書く前に測つた** ―― lot48 の門の器が古いか否かを「己の割当の外ゆゑ丙」と書き掛けたが、60 本の木を引けば ★何處に何版在るか★ は判る。引いた結果 disk の版は km-79 の枝に在り ★未commit ではない★ と判つた ∴ 丙にはせぬ。

## 数が意味せぬ事(纏め・数の規律3)

- ⑴ = ★分岐点から枝の tip までに積まれた file 数(★片側★)★。枝の仕事量ではない。枝同士で比べるな。★main が己の向きへ進んだ分は一切入つて居らぬ(其れは ㋑補 の 14 file)。★
- ⑵ = ★基点から先に在る file 数★。正しさでも、独占でもない。
- 甲=14 = ★捨ててよい證が一つも立たなかつた本数★。「悉く PR せよ」ではない。
- 子孫 tip=0 = ★此の組では鎖を畳めぬ★。「他所に鎖が無い」ではない(組の外の重なりは 13 対在る)。
- disk同一 12/14 = ★bytes は手許に在る★。「ref に要らぬ」ではない。
- 門 rc(一行目) = ★此の束★ が出す前門を通つた事。★14 本の枝が通る事ではない。★

## 納め便 ―― ★字数は器で測つた★

- 宛 = 家老mac(`karo-mac`)。★軍師mac は死箱★ ∴ 監査は家老mac の代送を乞ふ。
- 字数 = ★280 字★(條 300 字 ―― `python3` の `len` で測つた。胴 = `raw/96_fumi.txt`・測りの出目 = `raw/96_fumi_ji.txt`)。
- 器 `driver/97_fumi.py` は ★300 字を超えたら一字も本便を書かず rc=7 で止まる★。現に初版は 350 字で止まり、其の下書が `raw/96_fumi_shitagaki.txt` に残る―― ★門が効いた證★ である。
- ★此の字数が意味せぬ事★: 便が★届いた★事ではない。`inbox_write.sh` の rc と、家老mac の箱の尾で別に確かめる。

## 出目の在り処

- `raw/11_bogen.tsv` ―― ㋐ 母數・物の在否
- `raw/21_roster.tsv` ―― ㋐ 己の ls-remote と家老臺帳の突合(60/60)
- `raw/22_lsremote.txt` ―― ㋐ ls-remote の生
- `raw/31_sokutei.tsv` ―― ★㋑⑴⑵の生の數★
- `raw/32_chuu.txt` ―― ㋑ NUL と行数の食ひ違ひ(0件)
- `raw/36_ryoumuki_main.txt` ―― ★㋑補 分岐点と main 側の 14 file★
- `raw/37_ryoumuki.tsv` ―― ★㋑補 両向き・自前と main 側の交はり★
- `raw/41_kusari.tsv` ―― ㋕ 組内の祖先対(0行)
- `raw/42_shison.tsv` ―― ㋕ 60本に対する子孫(悉く0)
- `raw/51_shitsu.tsv` ―― 中身 対 main / 対 disk
- `raw/52_path.tsv` ―― 同 path 毎
- `raw/61_kasanari.tsv` ―― ㋕ file の重なり 対
- `raw/62_kasanari_matome.tsv` ―― 同 纏め
- `raw/71_utsuwa_ban.tsv` ―― 器の版が 60本+main+disk の何處に在るか
- `raw/81_shiwake.tsv` ―― ★㋓ 仕分け(枝・sha・⑴・⑵・commit・領域・甲乙丙・理由)★
- `raw/82_shiwake_riyuu.tsv` ―― ㋓ 拠り所の当たり方
- `raw/91_ukeire.tsv` ―― ㋔ 受入条件
- `raw/92_taba.tsv` ―― ㋔ 束毎の臺帳・根・対照
- `raw/96_fumi.txt` ―― ★納め便の胴(280字)★
- `raw/96_fumi_ji.txt` ―― 同 字数の測り
- `raw/96_fumi_shitagaki.txt` ―― 同 350字で止められた下書(門の證)
