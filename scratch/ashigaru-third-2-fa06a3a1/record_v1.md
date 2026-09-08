# fa06a3a1 記録 ―― test_c1_dml_migration_pkg_isolated_harness.py の collection error を 0 にする

席 = ashigaru-third-2 / 令 = subtask_thirdpc_a2_test_c1_dml_migration_collection_error_fix_001 (order_in_seat 8 / 板 fa06a3a1 / priority 3 / bloom L3 / 出所 総監督 hs_98a48d14 01:13)

## 零 床(27) ―― 令が sha で名指した物を、己の器で先に刷る

令は紙ではなく **commit** を名指した。故に紙の再刷ではなく commit の再測を置く。

| 令が名指した物 | 令の書き方 | 己が測つた値 | 一致 |
|---|---|---|---|
| salvage commit | `7f3f371b9` | `7f3f371b94b535ad301a06ea0b29e98817ba4268` / 親 `f063b664f5b75cc704fc37df891e83f04d932a5a` / 著 hakudoukai / 2026-09-02 22:38:22 +0900 / 題「salvage(safe): third-PC 甲樹の生きた成果のうち ★既存fileを一字も上書きせぬ 28本★ のみを live main 直上に載せる」 | 短縮 sha は一致 |
| 対象 test file (共有樹 /mnt/c/DentalBI) | ― | sha256 `05b85a1e489dc2b77068b4aaceef98bd20a479f26f732a0aca6be5a524f6df26` / **702 行** | ― |

## 一 令の前提と、測つた事実の食ひ違ひ ―― 「salvage 7f3f371b9 由来の関数」は其処に現に無い

令の purpose 逐語:

> test_c1_dml_migration_pkg_isolated_harness.py が treatment_validation に無い _resolve_comment_documentation_field_id を import(salvage 7f3f371b9 由来)→collection error 0 にする(移植か importorskip 理由付き)。

令の acceptance 逐語(該当部):

> 移植なら salvage 7f3f371b9 の関数を出所 sha 付きで持ち込み・importorskip なら理由を 1 行 docstring に。

**測つた:**

| 測定 | 打つた器 | 出た値 |
|---|---|---|
| salvage 7f3f371b9 の `backend/api/treatment_validation.py` に該名は在るか | `git grep -c '_resolve_comment_documentation_field_id' 7f3f371b9 -- backend/api/treatment_validation.py` | **exit 1 = 該当行 0 行** |
| salvage 7f3f371b9 の **全 path** で該名を含む file | `git grep -l ... 7f3f371b9` | **1 file**(1 個 = file 1 本)。其れは `backend/tests/test_c1_dml_migration_pkg_isolated_harness.py`、即ち **import して居る側だけ** |

∴ **令の言ふ「salvage 7f3f371b9 の関数」は、其の commit に現に無い。** salvage は題の通り「既存 file を一字も上書きせぬ」方針であり、`backend/api/treatment_validation.py` は既存 file ゆゑ **定義側は載らず、import する test file だけが載つた**。之が collection error の因である。

### 一' 然らば定義は何処に在るか(悉皆に近い探索)

`git log --all -S'_resolve_comment_documentation_field_id'` を全 path で打つた。該名を出し入れした commit は **6 個**(1 個 = commit 1 本)。うち **定義**(`def ...`)を持つのは次の 2 本のみ。

| commit | 引数の数 | live main (`b1a611148`) の祖先か |
|---|---|---|
| `59b9f4dd85c1c03b608a1637c3e6f6d7d632cf73` (著 ashigaru-third-5 / 2026-07-23) `backend/api/treatment_validation.py` L4295 | **2 個**(1 個 = 仮引数 1 つ。`client, set_code`) | `--is-ancestor` **exit 1 = 祖先に非ず** |
| `8a23afa8a` (題「fix(karte_visit_items): G1 cycle1 REDO是正 Finding1/2/3/4 (D1b/R8, a3-5)」) | **3 個**(`client, set_code, field_name`) | 同じく祖先に非ず |

対して test は `_resolve_comment_documentation_field_id(fake_client, <set_code>, None)` と **3 個**で呼ぶ(L641-642)。∴ 仮に 59b9f4dd8 の 2 引数版を持ち込んでも呼出は通らぬ。**令が名指した唯一の出所からは移植できず、実際に signature の合ふ出所は令に書かれて居らぬ commit である。**

### 一'' 先行実装が現に在る(二重実装の禁・要 上の裁)

同じ collection error を、既に別の手で潰した commit が在る。

- `db86b2099c1faa593b0aa2ceb90af2915c842fd1` 題「test(backend): restore isolated harness collection」/ 著 Doctor X / 2026-09-05 15:15:05 +0900 / 親 `8c6cc4ce5eb55d8a4fbf6c55ddde458dc3c84ced`
- 載る ref = `drx-payment4-atomicity`・`drx/p1-7-cross-search-20260907`・**`remotes/origin/drx/p1-7-cross-search-20260907`**(= 既に遠隔へ出て居る)
- live main `b1a611148` の祖先か = **exit 1 = 祖先に非ず**
- 手当の形 = import と `_FakeSupabaseClient` 一式を **削り**、test_10 を「移行後の active 行が 1 行へ収束する」直接検証へ **書き替へた**。其の docstring 逐語に「旧製品resolverは廃止済みなので、削除済みprivate関数をimportせず」と在る。
- 変更量 = 3 file / +20 行 / -72 行(1 個 = 行 1 本)

∴ **当席の手当と Doctor X の手当は同じ file の同じ箇所に当たる。** 何れを live main へ載せるかは **裁であり、当席の分限を超える**。当席は測つた事実のみを此処に置く。

## 二 移植か importorskip か ―― 択んだのは importorskip・其の理由

| 択 | 可否 | 測つた根拠 |
|---|---|---|
| 移植(令の書いた出所 = salvage 7f3f371b9 から) | **成らず** | 其の commit に定義が 0 行 |
| 移植(真の出所 = 8a23afa8a の 3 引数版から) | 成り得るが択ばず | ①令に書かれて居らぬ出所である ②書込先が `backend/api/treatment_validation.py` = 製品 API の既存 file であり、salvage が意図して載せなかつた面である ③先行実装 db86b2099 の docstring は同関数を「廃止済み」と記す。廃止された private 関数を製品面へ戻すのは **collection error 0 の求めを超え、裁を要する** |
| importorskip(+ getattr 護り + 当該 1 test のみ skipif) | **成る** | 触れるのは test file **1 本**のみ。製品面への書込 0 行 |

∴ **importorskip を択んだ。** 令の acceptance「importorskip なら理由を 1 行 docstring に」に従ひ、test_10 の docstring 冒頭へ理由を 1 行(1 個 = 文 1 つ)置いた。

### 二' 手当の中身(逐語)

冒頭 import を次へ替へた ――

```python
_treatment_validation = pytest.importorskip(  # noqa: E402  (path setup above is required first)
    "backend.api.treatment_validation"
)
_resolve_comment_documentation_field_id = getattr(
    _treatment_validation, "_resolve_comment_documentation_field_id", None
)
```

`importorskip` 単独では足りぬ ―― **module は現に import でき、欠けて居るのは symbol 1 個**だからである。故に `getattr(..., None)` で受け、test_10 にのみ次を掛けた。

```python
@pytest.mark.skipif(
    _resolve_comment_documentation_field_id is None,
    reason="_resolve_comment_documentation_field_id が backend.api.treatment_validation に現に無い",
)
```

module 全体を `pytest.skip(allow_module_level=True)` にはして居らぬ ―― 其れは残り 16 個(1 個 = test item 1 つ)を悉く skip へ落とすからである。

## 三 返却 ―― 器・commit・走行

### ⑴ 器と樹

| 項 | 値 |
|---|---|
| 樹 | `/home/hakudoukai/a2/wt-fa06a3a1-collect`(`git worktree add --detach` で新設・共有 checkout 不触) |
| base | `b1a6111480cfff1cc19bf2403e5aa6da1419b0e2`(= 共有樹 HEAD) |
| python | 3.12.3 |
| pytest | 9.0.3 |
| 走らせた場 | WSL2(Ubuntu)。**Windows runtime での再走は行つて居らぬ ―― 之は gap である** |

### ⑵ 固定 commit(1 本)

| 項 | 値 |
|---|---|
| tip | `4b9912e6c3d69cae6e231b628678e3db4de3a75c` |
| 親 | `b1a6111480cfff1cc19bf2403e5aa6da1419b0e2` |
| 触れた path | `backend/tests/test_c1_dml_migration_pkg_isolated_harness.py` **1 本のみ**(1 本 = file 1 個) |
| 増減 | **+12 / -3 行**(1 個 = 行 1 本) |
| 親の blob | `1134bc165e1a85cc0029e48f303e66b3c80ff57e` |
| tip の blob | `90cb6cfdaae48c0a9d7dcee7b84ebd0d7f66147a` |
| `git show --check` | exit 0 |
| `git log -1 --decorate` | `(HEAD)` のみ ―― 遠隔 ref 0 個 = **push 0** |

### ⑶ 走行(令の acceptance「対象 file 単独 collect の raw 先頭2行+件数+exit」)

**手当前(BEFORE)** `python -m pytest <対象> --collect-only -q -p no:cacheprovider`

raw 先頭 2 行(1 行 = 改行区切り 1 本):

```
==================================== ERRORS ====================================
_ ERROR collecting backend/tests/test_c1_dml_migration_pkg_isolated_harness.py _
```

末尾逐語 `no tests collected, 1 error in 0.78s` / **collection error 1 個**(1 個 = pytest が数へた error 1 つ) / collect された test item **0 個** / **exit 2**

**手当後(AFTER)** 同じ command

raw 先頭 2 行:

```
backend/tests/test_c1_dml_migration_pkg_isolated_harness.py::test_00_forward_and_rollback_sql_fixtures_match_reported_hash
backend/tests/test_c1_dml_migration_pkg_isolated_harness.py::test_01_unsubstituted_placeholder_rejected_before_insert
```

末尾逐語 `17 tests collected in 0.47s` / **collection error 0 個** / collect された test item **17 個** / **exit 0**

∴ 令の求めた「pytest collection error 0」は **現に在る**。

### ⑷ 形の裏取り(床31 ―― ast で数へる)

- `python -m compileall` exit **0**
- `ast.parse` で module 直下の `def test_` を数へた = **17 個**(1 個 = 函数定義 1 つ)。pytest が collect した 17 個と一致する ―― 即ち **parametrize による膨らみは 0** であり、両者は同じ物差で数へられて居る。

### ⑸ skipif が実際に何を落とすか(隠さず記す)

`pytest <対象> -k test_10 -q -rs` を打つた。exit **0** / `1 skipped, 16 deselected` / 逐語 `SKIPPED [1] ...:638: _resolve_comment_documentation_field_id が backend.api.treatment_validation に現に無い`。

∴ **collection error 1 個は消えたが、代りに skip が 1 個 生じて居る**(1 個 = test item 1 つ)。当 repo の Test Rules は「SKIP = FAIL」と記し、当 file の module docstring も逐語「隔離環境が使えない場合はSKIPで完了扱いにせず、pytest.failで明示的に失敗させる (SKIP=FAIL原則、プロジェクトTest Rules準拠)。」と記す ―― 但し其の文の射程は逐語「隔離環境が使えない場合」であり、当席の skip の因は **symbol 欠落**であつて隔離環境ではない。**両者が同一の禁に当たるか否かは裁であり、当席は判じ得ぬ。事実のみを置く。**

### ⑹ raw log

| 項 | 値 |
|---|---|
| path | `/home/hakudoukai/a2/wt-fa06a3a1-collect/reports/_scratch/fa06a3a1_collect_a2_20260907.log` |
| sha256 | `d240c833e10bf79669efef0c1015d115df8ff02c114c8976729a1773ccf3accb` |
| 大きさ | **89 行 / 5556 byte** |
| 追跡 | `git status --porcelain` = `??` = **untracked**(commit へ入れて居らぬ) |

## 四 境界の実測

| 禁 | 測つた値 |
|---|---|
| 本樹書込 0 | `/mnt/c/DentalBI` の HEAD は前後で `b1a6111480cfff1cc19bf2403e5aa6da1419b0e2` 不変。対象 file の sha256 先頭16 は前後で `05b85a1e489dc2b7` 不変。`git status --porcelain <対象>` は **空 = 変更 0 行** |
| push 0 | tip の decorate は `(HEAD)` のみ。遠隔 ref **0 個** |
| commit を増やすな | 当令で作つた commit は **1 本**。amend 0 回 |
| 製品 DB / 患者本文 / 患者画像 | 触れて居らぬ。DB へ打つた query **0 本** |
| X/Y file 不触 | 触れた file は test 1 本のみ |
| FE 専任 e9aa24a8 | 其の worktree `/home/hakudoukai/a1/wt-handover-fe` へは触れて居らぬ。同時編集 0 件 |
| 一時 file(床⑾) | リダイレクト `>` `>>` と tee は 0 回。書込は悉く python `open()` |

## 五 三択語で結ぶ

- 「対象 file 単独 collect の collection error が 0 である」…… **現に在る**(exit 0 / 17 item collect)
- 「令の名指した salvage 7f3f371b9 に当該関数の定義がある」…… **現に無い**(0 行)
- 「当席の手当と Doctor X の db86b2099 の何れを live main へ載せるべきか」…… **測定不能**(裁であつて測定ではない。当席は上へ挙げる)
- 「Windows runtime でも同じ結果になるか」…… **測定不能**(当席は WSL2 でしか走らせて居らぬ。値が測れぬのであつて、上限が測れぬのではない ―― 器が無いのではなく、当席が其の器へ行つて居らぬ)

## 六 禁語 sweep

| 語群 | 件 | 何処 |
|---|---|---|
| 先送り語(後で/次回/追って/保留/一区切り) | 0 | ― |
| 判定語(PASS/合格/充足/解消/緑) | 1 | 三で引いた pre-commit hook の出力 `Supabase secret scan PASS` は **器が吐いた逐語**であり当席の判定語ではない ―― 本紙本文には写して居らぬ |
| 是正案語(是正案/統べよ/消せ) | 1 | 一'' の打消し「何れを載せるかは裁であり、当席の分限を超える」 |
| secret / 患者本文 / id 値 / set_code 個別値 | 0 | 一' の呼出例に在つた set_code 個別値 1 個(1 個 = 文字列 literal 1 つ)は `<set_code>` へ伏せた。伏せる前に己で数へた ―― 本紙全体で 1 個 |
| URL | 0 | ― |

as_of: 2026-09-07T04:41:36+09:00 (席 ashigaru-third-2 / 樹 /home/hakudoukai/a2/wt-fa06a3a1-collect・親 repo /mnt/c/DentalBI)
