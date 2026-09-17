# km-107 ★讀み手の破れは何本の臺帳に及ぶか★ ―― 專任1(ashigaru-mac-1) 初段

札=km-107-yomite-no-han-wo-kazoeru-20260917 ／ 據=軍師mac REVISE PR#22(seq326657/326674)⑵ ／ 家老が因を割つた後の「害の広さ」の測り
着手 刻=raw/00_chaku_toki.txt(2026-09-17T16:42:18+0900) ／ 宣ETA=18:15 ／ 讀取のみ(checkout・refs・.gitignore・verify.py・commit・push 悉く不觸)

## 一 結語(先に)

| 欄 | disk(作業樹・歩き根=repo根) | git HEAD の樹 | git 全 93 ref の和(重複無き blob) |
|---|---|---|---|
| 母數 定義A(名に manifest) | **4869** 本 | 15 blob | 157 blob |
| 母數 定義C(path行 1 以上=讀み手が讀む行を持つ) | **1681** 本 | 13 | 100 |
| ★甲(括つた空白名)★ | **40 行 / 20 紙** | 10 行 / 3 blob | 23 行 / 10 blob |
| ★乙(括らぬ空白名)★ | **1221 行 / 105 紙** | **0** | **0** |

- ★乙 1221 の内、名に空白が在ると讀める行は 4 行(三の三)。他 1217 は 讀み手の出力の写し(1025)・markdown 表の桁(126)・散文形の舊臺帳(66) である ―― 檢出子の定義(seg 全体を名と見る)が拾つた物で、★空白名の害は 4 行★。
- ★甲 40 行は 直つた讀み手なら悉く正(40/40)・旧では悉く誤(0/40)★。乙 1221 は ★二版とも 0/1221★(raw/32)。
- ★樹の乙は三欄悉く 0★ ―― 然し之は「壊れて居らぬ」の意ではない(五)。素の空白名は今も両版が切り落す(對照の二行目、raw/32)。
- 讀み手の版(93 ref・raw/29): 旧 b19ec9ea=★67★ / 直 ebfc4c0e=★1★(refs/heads/karo-mac/hantei-saiteishutsu-20260917) / 無 25。disk の作業樹は 直。家老の「68 本中 旧 67 / 直 1」と ★一致★(ref 總は 69→93 に増えて居るが、有る本數は同じ 68)。

## 二 ㋐ 母數 ―― 集め方の逐語

**disk**(driver/10_bosuu_disk.sh・raw/10_*):
> 歩き根 `/Users/momizimac/multi-agent-shogun`。根直下の `.git` のみ剪定(`-path "$REPO/.git" -prune`)。
> 定義A = `-type f`(regular・symlink 含まず) ∧ `-iname '*manifest*'`(basename が大小文字を區別せず manifest を含む)。
> `-print`(改行區切)と `-print0`(NUL區切)の二器で出す。本數は grep -c '' / NUL 數 / wc -l の三つで別々に數へた。

| 器 | 本數 | rc |
|---|---|---|
| grep -c '' raw/10_disk_A.lst | 4869 | 0 |
| tr -dc '\0' < raw/10_disk_A.nul \| wc -c | 4869 | 0 |
| wc -l | 4869 | - |
| find 自身の rc | - | **1**(raw/10_find.err 1 行=權限拒否 `…km-sakai…/sakai/nanmon/n13_noaccess_dir` ―― 他席の fixture。★歩けなんだ dir が一つ在る★ ∴ 4869 は「歩けた範圍」の數) |

find は `bfs`(raw/10_env.txt)。刻=16:46:37。★16:44 の下見では 4865 であつた★ ―― 二分で 4 本増えた(箱は測る間に育つ)。
定義B(A ∧ `.txt`)=1351 ／ 定義C(A ∧ path行≥1)=1681 ／ 非正規(FIFO 等・open せず)=0 ／ 己の束に當たつた本數=0(對照の紙は名に manifest を含めぬ・臺帳は歩きの後に建つ)。
上位 dir 別(raw/22): queue 4598(C 1546・甲 17・乙 1220) / docs 196(C 115・甲 23・乙 1) / reports 34 / .claude(worktree) 33 / scripts 6 / .venv 1 / android 1。
★歩き根の外★: `/private/tmp/gunshi-km49.*` と `/private/tmp/km_wt_pr22_*` の二 worktree は根の外ゆゑ歩いて居らぬ(git worktree list)。

**git の樹**(driver/25_gai_tree.py・raw/26):
> (i) HEAD(75aa92f・枝 ashigaru-mac-3/km-51-…)の `git ls-tree -r -z HEAD` の blob ∧ basename に manifest(大小無視)。
> (ii) `git for-each-ref` の 93 ref に (i) と同じ濾し。★重複無き blob★ で數へる(同じ blob は一度・ref 數は raw/28 の欄)。ls-tree rc≠0 の ref=0。
> 中身は `git cat-file --batch`。disk の紙は一枚も讀まぬ。

| | blob | B(.txt) | C | 行總 | path行 | 讀めぬ |
|---|---|---|---|---|---|---|
| HEAD | 15 | 13 | 13 | 1035 | 835 | 148 |
| 全 ref 和 | 157 | 97 | 100 | 16726 | 10234 | 5829 |

## 三 ㋑ 害の行 ―― 檢出子の宣(driver/gai.py 冒頭の逐語)と數

行 = `b"\n"` で切る(splitlines は使はぬ・U+2028 を行末と見做す爲)。註=`#` 始まり/空行。path行=sha256=<64hex> を含む註でない行。讀めぬ=含まぬ行。
seg = `path=` の直後から最初の ` sha256=`/` bytes=`/` lines=` の手前(無ければ `sha256=` の手前、`label = p` 形は最後の ` = ` の右)。両端の空白は剥ぐ。
括り = 両端が同じ `"` か `'`。空白 = inner に `' '` か `'\t'`(書き手 append.py の KUUHAKU と同じ二字)。
**甲=括り∧空白 ／ 乙=¬括り∧空白** ／ 丙=括り∧¬空白(旧形) ／ 平=本形 ／ 丁=其の他の unicode 空白(U+3000 等)。

### 三の一 disk(raw/22・raw/21・raw/23)

| 種 | 行 | 紙 |
|---|---|---|
| 甲 | 40 | 20 |
| 乙 | 1221 | 105 |
| 丙 | 11737 | - |
| 平 | 31969 | - |
| 丁 | 12 | 2(km-46・km-47 の fixture 臺帳) |
| 讀めぬ | 47397 | - |

行數の二器: python `b"\n"` 實測 と `grep -c ''`(/usr/bin/grep) を 4869 紙 全てに當て ★食ひ違ひ 0 紙★(raw/20 の 食違 欄)。

### 三の二 層(driver/23・raw/23_disk_sou.txt ―― 宣は同 file 冒頭)

| 層 | 行 | 紙 | 何か |
|---|---|---|---|
| 甲-現物 | 20 | 9 | 他席の臺帳が己の fixture(空白名)を括つて載せた行(km-45/46/47/83・km-hiku-sahou/sakai/18tai16・karo-mac_shiketsu) |
| 甲-對照 | 20 | 11 | taishou/fixture/_gate/saiken 下の作り物・門控 |
| 乙-表 | 126 | 9 | `\| path \| sha256=… \|` の markdown 表。空白は表の記法 |
| 乙-写 | 1025 | 72 | 讀み手の出力 `★読めぬ行★ ep=S3-EP1 sha256=…` の写し(.out 68 紙・.txt 4) |
| 乙-殘 | 70 | 26 | 全行を raw/23 に刷つた。目で分けると下の通り |

乙-殘 70 の内訳(目視・raw/23 の全行):
- ★名に空白が在る行 = 4★: km-46(專任2) `…/shiryou/a b.txt`(行107) ／ km-onaji-utsuwa `…/fixtures/が の 紙.txt`(行305) ／ km-41(專任3) `…/hougen/ne/na ni kuuhaku.txt`(行29) ／ km-105 `_fixture/s_A/MANIFEST.txt` `c d.txt`(行2)。四つとも ★fixture の名★ であり、素で書かれて居る ∴ ★二版とも切り落す(raw/31_disk_yomite.tsv)★。
- 散文形 66: 番号付き一覧 `1. x.patch`(k60/k61/k63/k64/k65/k67/k68/k70=26 行)・`- N1 d0ec3ebf:`(k62=11)・括弧註 `x.py (実枝, commit …)`(B12_10/10r/B7_17/k21=15)・`@fda05c76c` 付(B4_20/07d=3)・其の他(`親 manifest`・`README(commit 後の實測)`・`[訂正・append-only] …` 等 11)。空白は名でなく散文の空白。★之等は 2026-09-06〜08 の舊臺帳で、讀み手は空白とは別の理由で讀めぬ★。

### 三の三 樹(raw/26・raw/24_refs_sou.txt)

| | 甲 行/blob | 乙 | 甲-現物 | 甲-對照 |
|---|---|---|---|---|
| HEAD | 10 / 3 | 0 | - | - |
| 全 ref 和 | 23 / 10 | 0 | 7 行/3 blob(km-46 4・km-47 1・km-83 MANIFEST.txt 2) | 16 行/7 blob |

★樹には乙が一行も無い★(HEAD も 93 ref の和も)。甲 23 行は悉く直つた讀み手で正(raw/32)。

## 四 ㋒ 對照(driver/30・raw/32_taishou_totals.txt・raw/taishou/)

| 紙 | 甲 | 乙 | 期待 | 判 | 行[python] | 行[grep -c] | splitlines() | 刻 |
|---|---|---|---|---|---|---|---|---|
| yousei_kou.txt(括つた空白名) | 1 | 0 | (1,0) | 通 | 3 | 3 | 3 | 16:48:49 |
| yousei_otsu.txt(素の空白名) | 0 | 1 | (0,1) | 通 | 2 | 2 | 2 | 16:48:49 |
| insei.txt(空白無・三方言) | 0 | 0 | (0,0) | 通 | 4 | 4 | 4 | 16:48:49 |
| u2028.txt(名に U+2028) | 0 | 0 | (0,0) | 通 | 1 | 1 | **2** | 16:48:49 |

對照 rc=0(raw/30_run.rc)。對照の紙は名に manifest を含めぬ(己の母數へ入らぬ爲)。u2028 は「splitlines なら +1」の疵が ★此の檢出子には無い★ 證(python 1 = grep 1 ≠ splitlines 2)。
二版の讀み手を同じ行に當てる(raw/32): `path="a b/c.txt"` → 旧 `"a`(誤)・直 `a b/c.txt`(正) ／ `path=a b/c.txt` → 旧 `a`・直 `a`(★両誤★) ／ `path=a/b.txt` → 両正。
★現に在る害行に當てる★(raw/31_*): disk 甲 40 → 旧 誤40/直 正40 ／ disk 乙 1221 → 旧 誤1221/直 誤1221 ／ refs 甲 23 → 旧 誤23/直 正23。

## 五 ㋓ 數が意味せぬ事

1. **乙 1221 は「空白名 1221」ではない。** 檢出子は seg 全体を名と見る故、讀み手の出力の写し(1025)・表の桁(126)・散文(66)を拾つた。名に空白が在ると讀めるのは 4 行、四つとも fixture。
2. **樹の乙 0 は「讀み手が直つた」の意ではない。** 素の空白名は今も両版が `a` に切り落す(四の對照二行目)。0 は「誰も素の空白名を commit して居らぬ」だけ。器は今も壊れて居る。
3. **甲 40/23 が直つた版で讀める事は「安全」の意ではない。** 直つた讀み手を持つ ref は 93 の内 1 のみ。旧を持つ 67 ref のどれで門を通しても甲は「実体無」に落ちる。
4. **母數 4869 は名の一致であつて臺帳の一致ではない。** 讀める行を持つ物は 1681。3188 本(.py/.rc/.err/.out 等の器と控)は名に manifest を持つだけ。
5. **數は刻の函数。** 16:44 4865 → 16:46 4869。權限拒否で歩けぬ dir が一つ在り(find rc=1)、其の下は母數の外。
6. **甲-現物/甲-對照・乙-殘 の内訳は path の字面(taishou/fixture/_gate 等)と目視で分けた物**であり、檢出子の出目ではない(raw/23 冒頭に宣)。

## 六 ㋔ 門・臺帳・禁

- 臺帳=`manifest.txt`(束内相對・`cd <束>` → `scripts/checks/karo_mac_manifest_append.py` のみで建てた)。門=`KM_GATE_MANIFEST_BASE=. bash scripts/checks/karo_mac_dasumae_gate.sh manifest.txt <臺帳の path 列>`。控=`mon_<HHMMSS>.log/.err/.rc`(走每に別名・臺帳へ入れぬ)。門の出目(rc・條① の四つの數)は ★控を見よ★ ―― 紙は己を含む臺帳の數を書けぬ(自己言及の境)。
- ★臺帳から除いた紙★: `raw/10_disk_A.nul`(末尾 NUL・二進ゆゑ條④に鳴る)。sha256/bytes/NUL數 は raw/33_nul_sha.txt に留めた。同じ内容の改行區切 `raw/10_disk_A.lst` は臺帳に在る(bytes 同一 888203)。
- 0 byte の stderr 控 4 本(20/23/25/30_run.err)は條④の爲 一行「(stderr 空…)」にした。`*_run.stdout` は totals の写しゆゑ K.seikei で EOF 空行を一つに整へた。對照の紙 raw/taishou/* は意圖 byte の儘(K.kaku を通さぬ)。
- 禁: 枝の削除/checkout/refs 書換・.gitignore・verify.py・git add/commit/push・/tmp ―― ★一つも行つて居らぬ★。讀んだ git 操作 = ls-tree/cat-file/for-each-ref/rev-parse/hash-object のみ。
- 軍師mac は死箱(rc=68)ゆゑ監査提出は家老mac 代送。
