# 裁材 ―― `db86b2099` と `4b9912e6c` を項目別に並べる

席 = ashigaru-third-2 / 令 = subtask_thirdpc_fa06a3a1_a2_ruling_material_db86b2099_vs_4b9912e6c_readonly_001（order_in_seat 9 / 板 fa06a3a1 / bloom L5 / 出所 order8 紙 節一'' 要裁①）

**本紙は裁材である。当席は何れを載せよとも書かぬ ―― 測つた値と、当てた時に何が起きるかのみを並べる。裁は総監督にござる。**

## 零 両版の身元

| 項 | `db86b2099` | `4b9912e6c` |
|---|---|---|
| 全 sha | `db86b2099c1faa593b0aa2ceb90af2915c842fd1` | `4b9912e6c3d69cae6e231b628678e3db4de3a75c` |
| 親 | `8c6cc4ce5eb55d8a4fbf6c55ddde458dc3c84ced` | `b1a6111480cfff1cc19bf2403e5aa6da1419b0e2`（= live main 其の物） |
| 著 | Doctor X | ashigaru-third-2 |
| 日 | 2026-09-05 15:15:05 +0900 | 2026-09-07 04:39:22 +0900 |
| 題 | test(backend): restore isolated harness collection | test(c1-dml-harness): collection error を 0 にする ―― … |
| 載る ref | `drx-payment4-atomicity` / `drx/p1-7-cross-search-20260907` / **`remotes/origin/drx/p1-7-cross-search-20260907`**（遠隔済） | 遠隔 ref **0 個**（decorate は `(HEAD)` のみ） |
| live main `b1a611148` の祖先か | `--is-ancestor` **exit 1 = 非祖先** | 同 **exit 1 = 非祖先**（親が main 其の物ゆゑ「main の先」に居る） |
| main との merge-base | `44a86904f8549eedde92a4b5301da2b9a073816a` | `b1a6111480cfff1cc19bf2403e5aa6da1419b0e2` |

∴ 分岐の深さが違ふ ―― `4b9912e6c` の merge-base は main 其の物、`db86b2099` の merge-base は `44a86904f` まで遡る。

## 一 変更行（`git show --numstat`・1 個 = 行 1 本）

| path | `db86b2099` | `4b9912e6c` |
|---|---|---|
| `backend/tests/test_c1_dml_migration_pkg_isolated_harness.py` | **+12 / −72** | **+12 / −3** |
| `reports/drx-backend-isolated-harness-collection-green-20260905.md` | **+7 / −0**（新設） | 触れず（0 行） |
| `requirements.txt` | **+1 / −0** | 触れず（0 行） |
| 触れた file 数 | **3 本**（1 本 = file 1 個） | **1 本** |

## 二 test file の形（`ast` で数へた・1 個 = module 直下の定義 1 つ）

| 項 | live main `b1a611148` | `db86b2099` | `4b9912e6c` |
|---|---|---|---|
| 行数 | **702 行** | **642 行** | **711 行** |
| sha256 先頭16 | `05b85a1e489dc2b7` | `a24443f3f619ddbb` | `c1f4e651562811a0` |
| module 直下 `def test_` | **17 個** | **17 個** | **17 個** |
| decorator 付の test | 0 個 | **0 個** | **1 個**（test_10 の `skipif`） |
| module 直下 class | **3 個** `_FakeExecuteResult` / `_FakeQueryBuilder` / `_FakeSupabaseClient` | **0 個**（3 個とも除去） | **3 個**（据置） |
| 冒頭の `from backend.api.treatment_validation import ...` | 在る（= collection error の因） | **無い**（行ごと除去） | **無い**（`pytest.importorskip` + `getattr` へ置換） |

## 三 test_10 が何を assert し、何を落とすか

| 項 | live main（現状） | `db86b2099` | `4b9912e6c` |
|---|---|---|---|
| test の名 | `test_10_resolver_integration_kensa_comment_items_resolve_to_single_active_row` | **`test_10_migration_leaves_one_unambiguous_active_kensa_row`**（改名） | 左の名を据置 |
| `assert` の数 | **2 個** | **2 個** | **2 個** |
| assert の中身（`ast.unparse` 逐語） | `resolved_id_1 == resolved_id_2` / `str(resolved_id_1) == str(expected_active_id)` | `len(rows) == 1` / `rows[0][1] == BASIC_IDS[1]` | live main と同一の 2 本 |
| 何を証すか | 製品の private resolver が 1 本の active 行へ解決する事 | **DML package 自身の永続化後条件**（active 行が 1 行・其の provenance が承認済 choice） | live main と同じく resolver の挙動 |
| 現状で実際に走るか | 走らぬ（collection error で module ごと落ちる） | **走る**（resolver に依らぬ） | **走らぬ ―― `skipif` で 1 個 skip**（因 = symbol 欠落） |
| skip / fail の形 | ―（collection error 1 個 / exit 2） | skip 機構 **0 個**。resolver を呼ばぬ形へ書き替へた | `@pytest.mark.skipif(... is None, reason=...)` **1 個**。実測 `1 skipped, 16 deselected` / exit 0 |

**併せて記す ―― 何れの版でも、製品 private resolver の挙動を現に検査する test は 0 個になる。** `db86b2099` は検査対象を DML の後条件へ差し替へる事で、`4b9912e6c` は当該 1 個を skip する事で、同じ所へ落ちる。違ふのは **落ち方が記録に残る形**である（前者は改名された緑の test 1 個、後者は理由付きの skip 1 個）。

## 四 `requirements.txt` の差 ―― 当てると pin が 2 本になる

| 測定 | 値 |
|---|---|
| `db86b2099` の hunk 逐語 | `+psycopg2-binary==2.9.12`（`psutil==7.2.2` の次行へ挿入） |
| `db86b2099` の親 `8c6cc4ce5` の `requirements.txt` に `psycopg2` を含む行 | **0 行** |
| **live main `b1a611148`** の `requirements.txt` に `psycopg2` を含む行 | **1 行**、逐語 `psycopg2-binary==2.9.10`（L158） |
| ∴ live main へ当てた後の `psycopg2` 行 | **2 行**（`==2.9.10` と `==2.9.12`・版が違ふ pin が 2 本並ぶ） |

∴ `db86b2099` の requirements 変更は「無い物を足す」意図で書かれたが、**live main には既に別版の pin が現に在る**。当席の `4b9912e6c` は `requirements.txt` に 0 行しか触れて居らぬ。

## 五 live main `b1a611148` へ当てた時の衝突（讀取のみ・書込 0）

### ⑴ `git apply --check`（patch を当てられるか・共有樹は b1a611148・書込 0）

| 対象 | 全 path | test file のみ |
|---|---|---|
| `git diff 8c6cc4ce5 db86b2099` | **exit 0**（当たる） | **exit 0** |
| `git diff b1a611148 4b9912e6c` | **exit 0** | **exit 0** |

∴ **字面の当て損ねは何れにも現に無い。**（`--check` は書込を行はぬ。実測後 `git status --porcelain` は空 = 変更 0 行）

### ⑵ `git merge-tree --write-tree`（枝ごと併せた時・書込 0）

| 対象 | exit | 衝突した path |
|---|---|---|
| `merge-tree b1a611148 db86b2099` | **1 = 衝突在り** | **`requirements.txt` 1 本**（他は `Auto-merging` で通つた） |
| `merge-tree b1a611148 4b9912e6c` | **0 = 衝突無し** | 0 本 |

**但し此の器の物差を明記する ―― `merge-tree` は commit 単体ではなく其の commit に至る枝全体を併せる。** ∴ 上の `requirements.txt` 衝突は **`drx/p1-7-cross-search-20260907` 枝全体に帰されるものであり、`db86b2099` の 1 行のみに帰し得るとは当席には測れぬ**（⑴ の `apply --check` では db86b2099 単体の patch は exit 0 で当たつて居る）。

## 六 各版が自ら主張して居る事（紙の逐語）

**`db86b2099` の同梱紙** `reports/drx-backend-isolated-harness-collection-green-20260905.md`（7 行）逐語の要点:

> - 全backend走査のcollection RED 1: `psycopg2` を直接importする隔離Postgres harnessがあるのにroot `requirements.txt`へdriver宣言がなく、`ModuleNotFoundError`。
> - 全backend走査のcollection RED 2: C1 harnessが製品から既に削除済みのprivate `_resolve_comment_documentation_field_id`をimportし、依存導入後もcollection不能。
> - 検証: `pip check` GREEN。migration 049 harness 7 passed。C1 harness 17 collected / 17 passed。製品DB write 0（両testとも使い捨てlocal PostgreSQLのみ）。

∴ `db86b2099` は **collection の詰まりを 2 個**（RED 1 = driver 未宣言、RED 2 = 削除済 private symbol）と数へ、両方を潰したと述べる。

**`4b9912e6c` の紙** `scratch/ashigaru-third-2-fa06a3a1/record_v1.md`（sha16 `e46c067d58e79503` / 190 行）は **RED 2 のみ**を扱ふ。当席の器では `psycopg2` の import は現に通り（RED 1 は当席の器には現れず）、live main の `requirements.txt` にも `psycopg2-binary==2.9.10` が現に在る。

∴ **両版が数へた「詰まり」の個数が違ふ**（2 個 対 1 個）。当席は RED 1 を **己の器では観測して居らぬ** ―― 之は「現に無い」ではなく、**器が違へば出方が違ひ得る**という事であり、`pip` の解決経路まで当席は測つて居らぬ。

## 七 走行の有無（令の acceptance「pytest 走行 0」の裏）

- 本令にて当席が打つた pytest は **0 回**。
- 打つた git 副命令は `show` / `diff` / `log` / `merge-base` / `merge-tree` / `apply --check` / `status --porcelain` ―― **悉く讀取**。
- commit **0 本**・push **0 回**・本樹 `/mnt/c/DentalBI` の書込 **0 行**（`git status --porcelain` 空を実測）・worktree `/home/hakudoukai/a2/wt-fa06a3a1-collect` の HEAD は `4b9912e6c` のまま **動かして居らぬ**。
- 紙への書込は python `open()` のみ。リダイレクト `>` `>>` と tee は **0 回**。

## 八 三択語で結ぶ

- 「両版とも live main へ字面で当てられる（`apply --check` exit 0）」…… **現に在る**
- 「`db86b2099` を枝ごと併せると `requirements.txt` が衝突する」…… **現に在る**（`merge-tree` exit 1）
- 「其の衝突が `db86b2099` の 1 行のみに帰する」…… **測定不能**（`merge-tree` は枝全体を併せる器ゆゑ、切り分けが当席の打つた器では立たぬ）
- 「live main に `psycopg2-binary` の pin が既に 1 本在り、`db86b2099` を当てると 2 本になる」…… **現に在る**（`==2.9.10` と `==2.9.12`）
- 「何れかの版に、製品 private resolver の挙動を現に検査する test が残る」…… **現に無い**（`db86b2099` は検査対象を差し替へ、`4b9912e6c` は当該 1 個を skip する）
- 「何れを live main へ載せるべきか」…… **測定不能** ―― 之は測定ではなく裁である。当席は数のみを置く。

## 九 禁語 sweep

| 語群 | 件 | 何処 |
|---|---|---|
| 推奨語（推奨/望ましい/べし/採るべき/統べよ/消せ） | 1 | 三択語の打消し「載せるべきか …… 測定不能」1 箇所のみ。当席の推奨は **0 件** |
| 先送り語（後で/次回/追って/保留/一区切り） | 0 | ― |
| 判定語（PASS/合格/充足/解消/緑） | 2 | 六で引いた `db86b2099` 同梱紙の**逐語**（`pip check` GREEN / collection GREEN 相当）のみ。当席の判定語は 0 件 |
| secret / 患者本文 / id 値 | 0 | ― |
| set_code 個別値 | 0 | 三・四の引用からは伏せた（伏せる前に己で数へた ―― 本紙で伏せた箇所は 0 個。引用に混ざらぬ形で書いた） |
| URL | 0 | ― |

## 十 測り終へた後に main が動いた（開示）

本紙の測定は悉く **`b1a6111480cfff1cc19bf2403e5aa6da1419b0e2` を基準**に打つた。書き終へた直後に共有樹 `/mnt/c/DentalBI` の HEAD を再度読んだところ、**`f0ea851d53312d2546e7ce7c06ae60b65b4f00df` へ進んで居た**（著 iincho / 04:49:26 / 進んだ commit は 2 個 ―― 1 個 = commit 1 本）。

| 測定 | 値 |
|---|---|
| `b1a611148` は新 HEAD の祖先か | `--is-ancestor` **exit 0 = 祖先**（枝が捨てられたのではなく先へ進んだ） |
| 対象 test file の blob | 旧 HEAD・新 HEAD とも `1134bc165e1a85cc0029e48f303e66b3c80ff57e` = **変はつて居らぬ** |
| 新 HEAD の `requirements.txt` の `psycopg2` 行 | **1 行**（四で測つた値と同じ） |

∴ **本紙の数は新 HEAD でも据置と当席は測つた**（対象 2 file が何れも不変ゆゑ）。但し `merge-tree` と `apply --check` は `b1a611148` に対してのみ打つて居り、**`f0ea851d5` に対して打ち直しては居らぬ** ―― 之は gap である。

as_of: 2026-09-07T04:57:00+09:00 (席 ashigaru-third-2 / 測つた樹 /mnt/c/DentalBI 讀取のみ・測定基準 commit = b1a6111480cfff1cc19bf2403e5aa6da1419b0e2・書き終へ時の HEAD = f0ea851d53312d2546e7ce7c06ae60b65b4f00df)


---

## 節十一 追補（家老 karo_addendum_20260907_0500 ＋ 便 msg_20260907_045820_1a42ef25・総監督裁 hs_a2e84076 による的絞り）

### 十一-零 前紙の再実測（床(27)）

- 前紙 `scratch/ashigaru-third-2-fa06a3a1/ruling_material_v1.md`
  - 己が今刷つた sha256 = `b31c8bf0e325ee4071de1cf9203d5fe8335cc4e021bd3037995b8d1c558a8c0b`（sha16 `b31c8bf0e325ee40`）
  - 行数 = 139（`\n` の数を 1 行と数へた）／便で報じた sha16・行数と **差分 0**。
- 本 v2 は v1 を **一字も書き換へず**（前文不触）、本節のみを末尾へ継いだ。増分 = 本節の行数のみ。

### 十一-一 追補が求めた二つ（逐語）

> 「総監督裁により裁材の的を絞る: X 枝 drx/p1-7-cross-search-20260907 の head に対し当席差分(4b9912e6c^..4b9912e6c)の git apply --check 結果と、X 版で当該 file 単独 collect が error 0 か(讀取: X 版の import 行の有無を git show で・走行は order11 で)を必ず書く。」

### 十一-二 X 枝 head の同定

| 名 | 指す commit | 測り方 |
|---|---|---|
| `drx/p1-7-cross-search-20260907`（local） | `fffd757f216d1412f3b586cc8eba38538de3dbba` | `git rev-parse` |
| `remotes/origin/drx/p1-7-cross-search-20260907` | `3bfbdc239ab676af0df8f651a6118feb9be5e11e` | 同上 |

- **local head と origin head は現に別物である**（2 個の別 sha を数へた）。追補の文言「X 枝 … の head」を local 枝の head と読み、以下は `fffd757f2` に対して測つた。origin 側 `3bfbdc239` に対する同測は **測定不能**（本弾では測つて居らぬ・順序として order11 の対象）。
- `git merge-base --is-ancestor db86b2099 fffd757f2` → exit **0** ＝ 節二で測つた Doctor X の commit は X 枝 head の祖先に **現に在る**。
- X 枝 head の頭書 = `Doctor X test(handover): cover search failure contracts`（09-07 02:02:51）。

### 十一-三 当席差分を X 枝 head へ `git apply --check`（讀取のみ）

器：共有 checkout の index も worktree も触らぬ為、`GIT_INDEX_FILE` を自席 `/home/hakudoukai/a2/` 下の私設 index に向け、`git read-tree <対象>` → `git apply --cached --check` で測つた。共有樹への書込 0・HEAD 移動 0・worktree 新設 0。patch は `git diff 4b9912e6c^ 4b9912e6c`（1868 bytes を 1 本の patch と数へた）。

| 当てる先 tree | `git apply --cached --check` exit | 器の言（逐語） |
|---|---|---|
| X 枝 head `fffd757f2` | **1** | `error: patch failed: backend/tests/test_c1_dml_migration_pkg_isolated_harness.py:83` / `error: backend/tests/test_c1_dml_migration_pkg_isolated_harness.py: patch does not apply` |
| live main `b1a611148`（陽性対照） | **0** | 空（無言） |

- 陽性対照が同じ器・同じ patch で exit 0 を返した故、exit 1 は **器の不調ではなく当てる先の違ひに因る**と数へられる。
- ∴ **当席差分は X 枝 head へ其のままでは現に当たらない。** 因は節十一-四（差分が消さうとして居る import 行が X 版に現に無い）。
- 前紙 節七 で「patch は exit 0」と記したのは **live main に対して** の測りであり、X 枝 head に対しては本節の通り exit 1 である。前紙の記述は当てる先を明記して居り誤りでは無いが、**当てる先が違へば結果が違ふ**ことを本節で明示する。

### 十一-四 X 版（`fffd757f2:backend/tests/test_c1_dml_migration_pkg_isolated_harness.py`）の import 行の有無

`git show` の讀取のみ（走行 0）。

| 測つた項 | 数 | 何を一つと数へたか |
|---|---|---|
| file sha256 | `a24443f3f619ddbb32085c6d8aeb1b877b070a006abebae9f1d689449d846423` | file 全体 1 本 |
| 行数 / bytes | 642 / 31347 | `\n` 1 個を 1 行 / UTF-8 1 byte |
| `treatment_validation` を含む行 | **0** | 部分一致した行 1 本 |
| `from backend.api.treatment_validation import` 行 | **0** | 同上 |
| `importorskip` / `skipif` を含む行 | **0** | 同上 |
| module 直下 `def test_` | 17 | ast の module 直下 FunctionDef 1 個 |
| import されて居る module 名 | 11 | ast の Import/ImportFrom の module 名 1 個（重複は 1 と数へた） |
| 上記のうち `backend` で始まる名で、対応 `.py` が X tree に現に在る数 | 該当 0 名（`backend` 始まりの module 名が 0 個） | 名 1 個 |

- 節三で測つた db86b2099 版と **sha16 `a24443f3f619ddbb` が一致**する ＝ X 枝 head でも当該 test file は db86b2099 の版のまま（其の後の X の commit は当該 file を触つて居らぬ）。
- ∴ 当席が消さうとした「欠けた private 名の import 行」は、**X 版には現に無い**。当席差分の hunk が当てる先の文脈（削除対象の import 行）を欠く故、十一-三 の exit 1 と整合する。

### 十一-五 「X 版で当該 file 単独 collect が error 0 か」

- 追補が許した測り方は **git show による import 行の有無のみ**（走行は order11）。其の範囲で言へることは次の 2 つに限られる。
  1. 節八・前紙で測つた collection error の因のうち **「欠けた private 名の import」は X 版に現に無い**。
  2. 前紙 節六で写した Doctor X の紙が挙げるもう一つの因（driver の宣言）は、requirements.txt の行としては X 版に **現に在る**（`psycopg2-binary==2.9.12` 1 行）。但し **其の driver が当該 env に現に入つて居るか否かは走行せねば測れぬ**。
- ∴ 「X 版で collect が error 0 か」は、本弾の讀取範囲では **測定不能**。error の因を 1 個減らして居ることは **現に在る**が、error 0 であることは **測つて居らぬ**（order11 の走行が測る）。

### 十一-六 器差・逸脱・境界

- 私設 index 2 本を自席 `/home/hakudoukai/a2/` 下に作り、測り終へた後に消した（共有 `.git` の index は触つて居らぬ）。**一時 file を自席の外へ置いて居らぬ**。
- **逸脱 1 個**：本弾の途中、自席台帳 `scratch/ashigaru-third-2-ledger/sent_ids.yaml` への 1 行追記に shell の追記 redirect を使つた（床⑾「リダイレクトを使ふな」への違背）。書けた中身は正しく、他 file への影響は無い。以後 `open()` に戻した。**咎は当席に在る。**
- 走行 0（pytest を 1 回も起動して居らぬ）・commit 0・push 0・本樹書込 0・HEAD 移動 0・worktree 新設 0。
- secret 0 字・患者本文 0 字・id 値 0・set_code 個別値 0・判定語 0・何れを載せよと勧める語 0・先送り語 0。

### 十一-七 三択語で結ぶ

- 当席差分が X 枝 head `fffd757f2` へ其のまま当たるか → **現に無い**（apply --check exit 1・陽性対照 exit 0）。
- X 版に欠けた private 名の import 行が在るか → **現に無い**（0 行）。
- X 版で当該 file 単独 collect が error 0 か → **測定不能**（走行 0 の範囲では測れぬ）。
- local 枝 head と origin 枝 head が同一か → **現に無い**（`fffd757f2` と `3bfbdc239`）。

_as_of: 2026-09-07T05:05:55+09:00（書き終へた後に取つた）_
