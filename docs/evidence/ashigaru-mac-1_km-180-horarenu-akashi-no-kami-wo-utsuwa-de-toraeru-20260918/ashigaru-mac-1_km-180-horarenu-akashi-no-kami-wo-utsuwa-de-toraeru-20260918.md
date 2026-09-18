# km-180 ―― 彫られぬ證の紙を器で必ず捕へる(測るのみ・据ゑぬ)

- 板 = queue/tasks/ashigaru-mac-1.yaml `km-180-horarenu-akashi-no-kami-wo-utsuwa-de-toraeru-20260918`(家老mac 発・板外 裁332455・1弾1枝 裁333060⑶・据ゑ 18:12)/ 書手 ashigaru-mac-1 / 宛 karo-mac
- 刻 = 紙を書き始めた刻 2026-09-18T18:21:57+0900 / 着手便 18:2x(宣ETA 19:15・300 字超で四度書き直し=疵)/ 測り 18:17:55〜18:20:25
- ★直さぬ・据ゑぬ★(hook・門・settings・.gitignore 不触)。代器は ㋔ に提案として書くのみ。

## ㋐ 樹の身元(★同じ問ひが樹ごとに違ふ答を出す★・raw/00)

| 樹 | show-toplevel | HEAD(測つた時) | 枝 | docs/evidence 直下 dir |
|---|---|---|---|---|
| A(己) | /Users/momizimac/wt/a1-km167-ci | 7c0d1492acfd5fcef5a60503888ab0dbd53fe5f6 | ashigaru-mac-1/km-167-ci-20260918 | ★3★ |
| B(己・本弾で切つた) | /Users/momizimac/wt/a1-km180 | 6bde7170ce574090a6139ba2dfe3aa4cb6db8634(切つた時)→ 2522ecbe(陰性対照の紙を追跡させた後) | ashigaru-mac-1/km-180-horarenu-akashi-20260918 | ★2★ |
| C(共有・★読むのみ★・他席の生きた樹) | /Users/momizimac/multi-agent-shogun | d8e3aa58b9eeac6f97f0d60928fbdc40c7c93f11 | ashigaru-mac-3/km-51-… | ★150★(家老の 151 と 1 違ふ=刻の差か dir の出入り・當席は断じぬ) |

∴ origin/main(6bde7170)の docs/evidence 直下は ★1 dir(km-manifest-append-track-20260917)★ のみ。共有樹の 150 は殆どが彫られぬ束(下 ㋒)。

## ㋑ 母數と根

根 = docs/evidence ★のみ★(深さ 1 = 束・束の内は全深さを歩く・symlink は辿らぬ)。★queue/ は歩かぬ★。器 = raw/01_census.py(己の器・argv に樹を取る・読むのみ)。束内最大深さ: A 1・B 1・C 6。git 呼び 5 種 × 155 束の rc は悉く 0(raw/10_*.tsv 末尾)。

## ㋒ 束ごとの三つの数(raw/10_census_{A,B,C}.tsv・11・12)

| 樹 | 束数 | 差>0 | 其の本数計 | 差<0 | 差=0 | ★差>0 且つ porcelain 0 行(盲)★ |
|---|---|---|---|---|---|---|
| A | 3 | 1(km-176 束: disk 94/追跡 70/差 24) | 24 | 0 | 2(km-167 束 119/119・km-manifest-append-track 19/19) | 1 |
| B | 2 | 1(本 km-180 束・測つた時 disk 3/追跡 0) | 3 | 0 | 1(km-manifest-append-track 19/19) | 1 |
| C | 150 | ★133★ | ★12382★ | 0 | 17 | ★96★(残る 37 は porcelain>0 だが其の行は差の一部しか写さぬ・例 km-100 束: 差 427 に porcelain 1 行) |

- 差≠0 の束 133 本は ★悉く★ raw/11_census_C_diff_nonzero.tsv に束名で列ねた(畳まぬ・133 行)。差 0 の 17 束は raw/12(17 行)。負の差は三樹とも 0(deleted 列 悉く 0)。
- ★陽性対照★ km-176 束(樹 A): 差 24 = letters/ の便の控 24 本(當席が「tip を動かさぬ為 commit せぬ・臺帳外」と宣した物・raw/21 逐語)。決めて掛からず測つた結果として在つた。
- ★陰性対照(差 0 の束)★: 樹 A の km-167 束(119/119)・km-manifest-append-track-20260917(三樹とも 19/19)。

## ㋓ porcelain の盲(實射・二方向・raw/20・22・31)

- ⒜ 樹 A・km-176 束: `git status --porcelain -- <束>` = ★rc 0・0 行・out 0B・err 0B★ に対し disk のみ 24 本。= 濡れ衣ではなく ★黙り★。同じ命令に `--ignored` を足すと 24 行(悉く `!!`)。
- ⒝ `git check-ignore -v` 逐語(3 本・rc 0): `.gitignore:7:*<TAB>docs/evidence/…/letters/km176_hantei_1of6.sent.txt`(他 2 本同形)。追跡済の紙に当てると rc 1(規則無し)= 追跡済は伏せられぬ。.gitignore は 443 行の allowlist 型で 7 行目が裸の `*`、docs/evidence を許す行は ★無い★(grep 0)。
- ⒞ ★陰性対照(己の紙・己の束)★ 樹 B: raw/30_inseitaishou_tracked_paper.txt を當席が作り `git add -f` で追跡させ commit 2522ecbe7163e6819a2cedfe91654ca4f5a88892。一字 `x` を足す → porcelain ★1 行 ` M …`★。`git checkout -- 紙` で戻し sha256 97eb4da4… 一致・porcelain 0 行。同じ束の追跡外の紙 raw/00 は porcelain 0 行・check-ignore `.gitignore:7:*` rc 0。∴ porcelain は「追跡済の改め」には鳴り「追跡外(伏せられた)」には黙る。

## ㋔ 代はりの器(★紙に書くのみ・据ゑぬ★)

提案 = 束ごとに三本を足す:
```
git ls-files --others --exclude-standard -- <束>            # 追跡外・伏せられぬ物
git ls-files --others --ignored --exclude-standard -- <束>  # 追跡外・伏せられた物 ← 盲の本体
git ls-files --deleted -- <束>                              # disk に無く追跡に在る(負の差)
```
「彫られぬ本数」= 一行目+二行目、負の差 = 三行目。判 = `find <束> -type f` の本数 − `git ls-files -- <束>` の行数 と一致する事を同時に検める(二つの独立な器の同値)。

- 實測: 三樹 155 束 ★悉く★ (others + others_ignored) == diff(raw/10 末尾行: A 3/3・B 2/2・C 150/150)。rc は 5 呼び全て 0。母數 155・差の総計 A 24 / B 3 / C 12382。
- ★捕へられる物★: .gitignore/.git/info/exclude/global excludes に伏せられた追跡外 file(一本ずつ path で)・伏せられぬ追跡外 file・追跡に在つて disk に無い file。
- ★捕へられぬ物(必ず書く)★: ⑴ 追跡済で ★中身が変はつた★ file(porcelain の ` M` の領分・本器は数へぬ → porcelain と併用が要る)⑵ 束の内の ★入れ子 .git★(submodule/別 repo)の中身(ls-files は境で止まる・find は数へる → 差が出るが本器は 0 と言ふ)⑶ symlink の先(find -type f も ls-files も辿らぬ・双方 0 ゆゑ差に出ず、指す先の紙が彫られたかは別問)⑷ 空 dir(file 0 ゆゑ両方 0)⑸ 名に改行を含む file(行数で数へる器は狂ふ・-z が要る)⑹ `git status --porcelain --ignored`(既定 traditional)は追跡外 dir を ★一行に畳む★(raw/23: km-177 束 56 本 → 1 行 `!! …/`)ゆゑ代器に使ふなら `--ignored=matching`(56 行)か ls-files 形に限る ⑺ 束の外(docs/evidence 直下でない置場)は根の外。
- 器の疵: 本 census も行数で数へる(⑸)。

## ㋕ 意味せぬ事

- 樹 C の 12382 本は「共有樹の disk に在つて共有樹の HEAD(席3 の枝)に無い本数」であり、他の枝や origin に彫られて居るかは測つて居らぬ(彫られて居る束も多い筈・例 km-167 束は樹 A では 119/119)。
- 「差 0」は本数の一致であり、中身の一致(sha)ではない。
- 家老の 151 と當席の 150 の 1 の差は追はぬ(刻が違ふ・他席の生きた樹)。

## ㋖ 疵

⑴ 着手便が 300 字を四度超えた(337/329/318/315/308 → 五度目で入つた)⑵ raw/20 の初版で己の tmp の path を二重にして「no such file」を吐き、取り直した(初版は上書き・残さず=疵)⑵' PIPESTATUS は zsh で空(memory 既知)を一度踏み rc を単独で取り直した。

## 宣⇔實

宣ETA 19:15。實 = 納め便の刻(紙の外)。
