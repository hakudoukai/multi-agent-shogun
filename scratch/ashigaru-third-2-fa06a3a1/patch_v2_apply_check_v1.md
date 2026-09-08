# patch v2 は現 共有 HEAD に当たるか (order34 產・讀取と --check のみ・適用 0)

as_of 2026-09-07 14:20 JST / 席=ashigaru-third-2 / 令=karo-third order34。測り方=git 讀取と `git apply
--check` のみ。適用0・pytest 走行0・DB0・push0・commit0・共有 checkout 操作0・D 樹 wt-964a06d0 不触。
三択語=測つた/測つて居らぬ/測れぬ。註 `Checking patch` `Applied patch ... cleanly` は git の逐語で当席の
判定語ではない。raw=order34_applycheck_raw.txt sha16=4d4a5202ed1e4d98 32 行。

## §1 共有 HEAD (測つた・1 = commit 1 個)
| 物 | 値 |
|---|---|
| 現 共有 HEAD | `59ef7ecd087e51788a04d6d1a6dda29233b05dc0` (short `59ef7ecd0`) |
| 家老 14:05 実測 | `254dd9cfb0c5c4500bbf52b295b79b823545f05b` |
| 関係 | `merge-base --is-ancestor 254dd9cfb HEAD` rc=0 = ★祖先★・間の commit ★1 個★ |
| patch v2 の base | `8daf47adb2ec31cb3ffc2591276cc3c20082c904` / base..HEAD = ★17 個★ |
∴ 家老の値から 1 commit 進んで居る。本紙は現 HEAD `59ef7ecd0` を対象にした。

## §2 対象 2 file に触れた commit (8daf47ad..HEAD)
`git log --oneline 8daf47ad..HEAD -- scripts/sync_source_cache.py tests/test_sync_source_cache.py`
→ ★出力 0 行・rc=0★ ⇒ 17 commit の内 対象 2 file を触つた commit は ★0 個★ (測つた)。
patch v2 の対象は `diff --git` ★2 行★ = 右の 2 file のみ (patch 讀取)。再測 sha16=b99e75d8d356ec46 554 行。

## §3 自席 detached 樹での --check (適用 0)
樹 `/home/hakudoukai/a2/wt-o34-applycheck` を `worktree add --detach 59ef7ecd0…` で 1 本 (枝 0・D 樹と
合はせ同時 ★2 本★・床 281003 の内)。逐語:
```
$ git apply --check -v <patch v2>
Checking patch scripts/sync_source_cache.py...
Checking patch tests/test_sync_source_cache.py...
rc=0
```
`git apply --stat` 逐語 `2 files changed, 440 insertions(+), 10 deletions(-)`
(`scripts/sync_source_cache.py | 223` / `tests/test_sync_source_cache.py | 227`)。
∴ 現 HEAD に対し ★rc=0 で当たる★。衝突 hunk ★0 個★ ゆゑ名指す箇所は無く、直す作業も行つて居らぬ。

## §4 適用 0 の裏 (測つた)
--check の後、樹の `git status --porcelain`=★0 行★ / `git diff --stat`=0 行 / `--cached --stat`=0 行 /
対象 2 file は HEAD の儘 (464 行・245 行) / 樹の `rev-parse HEAD`=`59ef7ecd087e5178…` 不動。

## §5 樹の始末 (測つた)
`git worktree remove …/wt-o34-applycheck` rc=0・prune ★0 回★・後の `worktree list` ★6 行★ で o34 無し・
dir も `ls` で無し。detached ゆゑ ref 不要 (枝を作つて居らぬ)。D 樹 wt-964a06d0 は list に現存=不触。

## §6 ★開示★
1. `--check --3way` も参考に打ち逐語 `Applied patch to '…' cleanly.` が出た。git の語であり当席の判定では
   ない。--3way でも index/作業樹は動いて居らぬ (§4 で測つた)。
2. 本紙は「当たるか」のみ。当てた後に試験が通るかは order31 の樹 (已に remove) での 24 本が最後であり、
   現 HEAD 上では ★測つて居らぬ★ (pytest 走行 0 の令)。order33 の SELECT も依然 打たれて居らぬ。
## §7 先の紙の sha 再測 (床(27)・as_of 14:20)
b99e75d8d356ec46 554 行 patch v2 / ea20e81d75e95ade 80 行 rows_15271_select_plan_v1.md(o33) /
eb60655c1f9d8822 37 行 order32_tree_and_candidates_v1.md(o32)
