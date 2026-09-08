# rebase_onto_x_v1 ―― X 枝 head 単体の collect を測り、当席版の始末を記す

席 = ashigaru-third-2（足軽三之二）／令 = 家老third order11（`subtask_thirdpc_fa06a3a1_a2_rebase_test_diff_onto_x_branch_and_submit_to_x_001`・板 fa06a3a1）
上の裁 = 総監督 hs_a2e84076①（X 版 db86b2099 が正・当席版は差分のみ・二本を残さぬ）／hs_579e16e0（psycopg2 pin は main の 2.9.10 に揃へ、X 版の 2.9.12 行は落とす）
家老追補 `karo_addendum_20260907_0509` = **cherry-pick は打たぬ**。X head 単体で collect 単独 raw を取り、error 0 なら「X 版で足る・当席版取下」を紙に。

## 零 床(27) ―― sha で名指された物を、己の器で先に刷る

| 名指された物 | 己が今刷つた値 | 前の記録との差 |
|---|---|---|
| X 枝 head | `fffd757f216d1412f3b586cc8eba38538de3dbba`（`git rev-parse drx/p1-7-cross-search-20260907`） | 紙 v2 節十一-二 と一致 |
| 当席の tip | `4b9912e6c3d69cae6e231b628678e3db4de3a75c` | 差 **0** |
| X 版の当該 test file | sha256 `a24443f3f619ddbb32085c6d8aeb1b877b070a006abebae9f1d689449d846423`（worktree 実物） | 紙 v2 が `git show` で測つた値と **一致**（讀取と実物が合ふ） |
| 紙 `ruling_material_v2.md` | sha256 `18b9598dab3b9515…`（sha16 `18b9598dab3b9515`）・220 行 | 差 **0** |

## 一 打つた事・打たなかつた事

| 事 | 打つたか | 器 |
|---|---|---|
| 自席 worktree で X head を detached checkout | **打つた** | `git checkout --detach fffd757f2`（`/home/hakudoukai/a2/wt-fa06a3a1-collect` 内のみ・共有 checkout 不触） |
| cherry-pick / apply で当席差分を載せる | **打つて居らぬ** | 家老追補の逐語に依る（紙 v2 節十一-三 で `apply --check` exit 1＝当たらぬと測つた為） |
| `requirements.txt` の psycopg2 行 | **触れて居らぬ** | X 枝の物ゆゑ（追補の逐語） |
| push / remote 書込 | **0** | ― |
| skipif の新設 | **0** | 令の逐語「skipif を新設するな」 |

- checkout 前に当席 tip を dangling とせぬ為、共有樹に local ref を **1 本**置いた ―― `git branch a2-fa06a3a1-collect-fixed 4b9912e6c`（`git rev-parse` で一致・upstream 無し・push 0）。

## 二 X head 単体の collect（走行 2 回）

`command: python3 -m pytest backend/tests/test_c1_dml_migration_pkg_isolated_harness.py --collect-only -q`
`cwd: /home/hakudoukai/a2/wt-fa06a3a1-collect`／`python: Python 3.12.3`／`pytest: pytest 9.0.3`／`os: Linux 6.6.114.1-microsoft-standard-WSL2`

| 走 | raw の絶対 path | raw SHA256 | 行数 | 件数（stdout 尾の逐語） | exit |
|---|---|---|---|---|---|
| ① 05:13（再起動 前） | `/home/hakudoukai/a2/wt-fa06a3a1-collect/reports/_scratch/fa06a3a1_xhead_collect_a2_20260907.log` | `a636f09e8289e50121cb70b821747967cce415843e408e642217e57bb7d4e9fd` | 36 | `17 tests collected in 0.39s` | **0** |
| ② 05:23（WSL 再起動 05:14 の後） | `/home/hakudoukai/a2/wt-fa06a3a1-collect/reports/_scratch/fa06a3a1_xhead_collect_a2_20260907_rerun.log` | `6ca2014c9fe465d588b5642fbd11fd6b4d0e911bb240c17df291b691cf3e2495` | 35 | `17 tests collected in 0.08s` | **0** |

stdout 先頭 2 行（両走とも同一・逐語）:

```
backend/tests/test_c1_dml_migration_pkg_isolated_harness.py::test_00_forward_and_rollback_sql_fixtures_match_reported_hash
backend/tests/test_c1_dml_migration_pkg_isolated_harness.py::test_01_unsubstituted_placeholder_rejected_before_insert
```

- 件数 **17**（node id 1 本を 1 件と数へた）・**ERRORS の節は出て居らぬ**・stderr **空**・exit **0**。
- ∴ **X 枝 head 単体で、当該 file の collection error は 現に無い。** 紙 v2 節十一-五 で「測定不能」と結んだ問ひは、本弾の走行で **測れた**。
- 二走の raw は行数が 1 違ふ（① は `git status` 行を末尾に持ち、② は持たぬ）。**中身の食ひ違ひではない。**

## 三 令の分岐に従つた結び ―― 当席版の始末

令の逐語「error 0 なら『X 版で足る・当席版取下』を紙に」に従ふ。測りは節二の通り error **0**。

- **X 版で足る。当席版（`4b9912e6c`）は取下げる。**
- 取下げても辿れる様、`a2-fa06a3a1-collect-fixed` に固定した（push 0）。**ref を消すか否かは上の裁**であり、当席は測りと固定までで止める。
- 当席版が X 版と別に持つて居た物 = 当該 test 1 file の 12 行増 3 行減のみ（紙 v1 節三）。X 版は同じ collection error を **別の形**（当該 private 名の import 行其の物を持たぬ・0 行）で除いて居り、**二本を残す理由は測りから出て来ない**。

## 四 X（bianalytics）への提出文（≤300 字・送るのは家老）

```
[third A2→X]当該 harness の collect は X head fffd757f2 単体で error 0(2 走・17 collected・exit0・raw SHA256 a636f09e…/6ca2014c…)。∴ third の同目的修正 4b9912e6c は取下げ X 版を正とす。申送 1: X 版 requirements の psycopg2-binary==2.9.12 は live main の 2.9.10(L158)と二本立てになる。総監督裁 hs_579e16e0=2.9.10 に揃へ 2.9.12 行は落とす(版上げは別弾)。
```

（本文 290 字＝python `len()` で数へた 1 文字を 1 字とする・令の上限 300 字 以内。当席は送らぬ・送るのは家老。）

## 五 境界（自己申告）

- commit **0**／push **0**／remote 書込 **0**／本樹（`/mnt/c/DentalBI`）の checkout・reset **0**（共有 HEAD は当席の器では動かして居らぬ）。
- 本樹に加へた物 = local branch **1 本**（`a2-fa06a3a1-collect-fixed`）のみ。
- 自席 worktree 内の checkout **1 回**（X head へ detached）。worktree 新設 **0**・remove **0**。
- 走らせた物 = `pytest --collect-only` **2 回**のみ（本走 0）。製品 DB・本番・secret・患者本文には触れて居らぬ。
- 一時 file **0**／`/tmp` 書込 **0**／redirect・tee **0**（python `open` と `subprocess.run(capture_output=True)`・床⑾）。
- secret 0 字・患者本文 0 字・id 値 0・表示名 0・判定語 0・先送り語 0。
- 器差の申告: 05:14 に third の WSL が落ち 05:21 に復した。**① の走は再起動 前**、**② は 後**。両走で件数・exit が同じであつた事を以て、再起動を跨いでも測りが変らぬ事を示す。

## 六 三択語で結ぶ

| # | 事 | 結び |
|---|---|---|
| 1 | X head 単体で当該 file の collection error が 0 か | **現に無い**（error が無い・17 collected・exit 0） |
| 2 | 当席差分を X head へ載せる必要 | **現に無い**（測りから出て来ない） |
| 3 | 当席 tip を辿る路（ref・push 0） | **現に在る**（`a2-fa06a3a1-collect-fixed`） |
| 4 | psycopg2 pin が二本立てになる事 | **現に在る**（X 版 2.9.12・live main 2.9.10） |
| 5 | X 側が此の申送を容れるか | **測定不能**（当席の器の外・送るのは家老） |

as_of: 2026-09-07T05:24:18+09:00（書き終へた後に取つた・席 ashigaru-third-2 / 樹 /home/hakudoukai/a2/wt-fa06a3a1-collect・親 repo /mnt/c/DentalBI）
