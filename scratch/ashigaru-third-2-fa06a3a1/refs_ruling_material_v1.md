# 当席 local ref 2 本の裁材(讀取のみ・事実のみ) v1

令: subtask_thirdpc_fa06a3a1_a2_two_fixed_refs_keep_or_drop_ruling_material_readonly_001
親裁: 総監督裁 seq281003(作業後 remove)・A2 紙 rebase_onto_x_v1 節三「ref を消すか否かは上の裁」
席: ashigaru-third-2 / 樹: /mnt/c/DentalBI(讀取のみ・branch -d/-D 0・worktree 0・checkout 0・push 0・走行 0)
動詞: git rev-parse / show -s / merge-base / rev-list --count / diff --stat / diff --name-only / cherry / for-each-ref --contains

## 節一 ref A = `a2-14c8ec72-fixed`
- tip = `80814278bbbeb0d260b5939ed4f5b7b824d2bade` / date 2026-09-07 04:18:28 +0900
  件名: `14c8ec72: reject identity query on handover main template detail route before DB read`
- merge-base(main d83839730) = `4729753591cde87b20617dad2a29d8c05259e74b` / base..tip の commit 数 = **37**
- merge-base(X fffd757f2) = `44a86904f8549eedde92a4b5301da2b9a073816a` / base..tip の commit 数 = **348**
- base(main 側)→tip の `diff --stat` = **129 files changed, 10848 insertions(+), 147 deletions(-)**
  (1 と数へたもの=git が列挙した file 一件。本文写しは行つて居らぬ)
- touched file の頭(名のみ・5 本): backend/api/handover_sheets.py /
  backend/tests/test_handover_main_template_read_api.py / frontend/playwright.9decb71a.config.ts /
  frontend/src/App.tsx / frontend/src/features/ekarte-ab-input/annotations/AnnotationOverlay.tsx

## 節二 ref B = `a2-fa06a3a1-collect-fixed`
- tip = `4b9912e6c3d69cae6e231b628678e3db4de3a75c` / date 2026-09-07 04:39:22 +0900
  件名: `test(c1-dml-harness): collection error を 0 にする ―― 廃止済 private resolver の import を importorskip+getattr 護りへ替へ、当該 1 test のみ skipif`
- merge-base(main d83839730) = `b1a6111480cfff1cc19bf2403e5aa6da1419b0e2`(= tip の親) / base..tip = **1**
- merge-base(X fffd757f2) = `44a86904f…` / base..tip = **338**
- base(main 側)→tip の `diff --stat` = **1 file changed, 12 insertions(+), 3 deletions(-)**
  touched = backend/tests/test_c1_dml_migration_pkg_isolated_harness.py の 1 本のみ

## 節三 同等が現に在るか(file 内容の blob 一致で数へた)
`git rev-parse <rev>:<path>` の blob sha を突合。1 と数へたもの=touched file 一件。
| ref | touched | main と内容一致 | main と相違 | main に file 無し |
|---|---|---|---|---|
| A a2-14c8ec72-fixed | 129 | 0 | 10 | 119 |
| B a2-fa06a3a1-collect-fixed | 1 | 0 | 1 | 0 |

| ref | touched | X と内容一致 | X と相違 | X に file 無し |
|---|---|---|---|---|
| A | 129 | 10 | 20 | 99 |
| B | 1 | 0 | 1 | 0 |

- `git cherry d83839730 <ref> <main 側 base>`: A = `+` **37** / `-` 0、B = `+` **1** / `-` 0
  (`+`=upstream に同等が無い、`-`=同等在り、と git が判じた数)
- 依て測つた事: 何れの ref も、main には同等が **現に無い**。
- 測つて居らぬ事: X 側の cherry は base が 44a86904f と遠く、mainline の commit を多数含む為
  (A=346・B=336)、「同等の有無」の材としては用ゐて居らぬ(数のみ記す)。

## 節四 他の ref が同じ commit を持つて居るか(失はれる範囲の材)
`git for-each-ref --contains <sha>` を base..tip の全 commit に当てて数へた。
- ref A の 37 commit:
  | 含む ref | 該当 commit 数 |
  |---|---|
  | refs/heads/a2-14c8ec72-fixed | 37 |
  | refs/heads/a1-handover-fe-e9aa24a8 | 36 |
  | refs/remotes/origin/a1-handover-fe-e9aa24a8 | 18 |
  - **当 ref のみが持つ commit = 1 本**(`80814278b`)。残り 36 本は A1 席の local ref が持ち、内 18 本は origin にも在る。
  - `80814278b` 単体の `--stat` = **2 files changed, 16 insertions(+)**
    (backend/api/handover_sheets.py 5+ / backend/tests/test_handover_main_template_read_api.py 11+)
  - 其の親 `87fa5683a` を含む ref = a1-handover-fe-e9aa24a8 と 当 ref の 2 本(origin には無い)。
- ref B の 1 commit:
  - tip `4b9912e6c` を含む ref = **refs/heads/a2-fa06a3a1-collect-fixed の 1 本のみ**(remote ref 0 本)。
  - 単体の `--stat` = **1 file changed, 12 insertions(+), 3 deletions(-)**。

## 節五 消した場合に失はれる物(退避済か否か)
- ref A: git 上で当 ref のみが持つのは `80814278b`(2 file・16 行)。
  紙・raw での退避 = `scratch/ashigaru-third-2-y77a10783/` に在る。
  | file | sha16 | 行 |
  |---|---|---|
  | A_record_v1.md | 8b7691a9942be892 | 170 |
  | A_record_v2.md | 9d62f73f072b28b2 | 184 |
  | A_worktree_remove_v1.md | 398e58910772d085 | 86 |
  | raw_14c8ec72/…_a2_20260907.log | 0a2c4d6f9aa64466 | 41 |
  | raw_14c8ec72/…_v2.log | 31025eb4146afdcf | 114 |
  | raw_14c8ec72/…_v3.log | 9d8306c1c4e99843 | 129 |
  - 但し **patch/diff 形の退避 = 0 件**(当席 dir 内 `*.patch`/`*.diff` を数へて 0)。
    即ち紙と raw は「何を測つたか」を残すが、**変更本文そのものは git の object にしか無い**。
- ref B: 当 ref のみが持つのは `4b9912e6c`(harness 1 file・12+/3-)。
  紙 = `scratch/ashigaru-third-2-fa06a3a1/` の worktree_remove_v1(163b60504e014221 70 行)・
  worktree_remove_v2(2005ecf6735646b0 129 行)・xhead_run_v1(018e34070505ee6e 78 行)・
  missing_symbol_history_v1(7e72643c1518018e 86 行)が sha と件名を記す。
  raw = raw_fa06a3a1/ に 5 本(collect d240c833…・xhead_collect a636f09e…・同 rerun 6ca2014c…・
  run1 d4f1f9d5…・run2 2477efea…)。**patch 形の退避 = 0 件**。
- 測つて居らぬ事: reflog・gc の挙動、及び object が何時まで残るか。

## 節六 本紙が書いて居らぬ事
- 残す/消すの何れを採るかは書いて居らぬ(本席は測つた事のみを記す)。
- 走行 0・branch -d/-D 0・worktree 0・checkout 0・push 0。

as_of: 2026-09-07T06:02:59+09:00
