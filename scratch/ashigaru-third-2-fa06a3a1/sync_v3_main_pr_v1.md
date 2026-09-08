# sync_v3 main 起点 PR 切り直し (order44) as_of 2026-09-07 / 席=ashigaru-third-2 / 樹=/mnt/c/DentalBI
## §1 始める前の再測 (fetch 0)
`rev-parse refs/remotes/origin/main` = `0973f8e584d7210ec46fbc125202957772c80abe`・`ls-remote origin refs/heads/main` = `0973f8e584d7210ec46fbc125202957772c80abe` ∴ **一致した**(不一致なら止まる所であつた)。
`rev-parse 3155e8dc0:scripts/sync_source_cache.py` = `0754d9284db2d50c5f3941ad1d3cf786d5279de9`・`rev-parse 3155e8dc0:tests/test_sync_source_cache.py` = `f27523f66ca36a2ba365d6b550f062c96e5578f0` ―― 令の 2 blob と全桁一致。
## §2 自席 worktree と新枝 (共有樹 checkout 0)
`worktree add -b a2-fa06a3a1-sync-rewrite-v3-main /home/hakudoukai/a2/wt-v3-main 0973f8e58…0abe` → `HEAD is now at 0973f8e58 進行管理板を再生成(機械・停止ワースト10つき)`。在中 worktree は a2 配下 **2 本**(本樹 と wt-964a06d0-d3adf65b・上限内)。
## §3 2 file の当て (自席樹内のみ)
`git checkout 3155e8dc0 -- scripts/sync_source_cache.py tests/test_sync_source_cache.py` rc=0。当てる前の main 側 blob = `76a1e2a91b422a1b71583f24a8573c67d88a78a8` / `dc14b700f2b306e5b26d73b443b81ea2efed4fd0`(2 file は main に既に在る)。
当てた後 `git hash-object` = `0754d9284db2d50c5f3941ad1d3cf786d5279de9` / `f27523f66ca36a2ba365d6b550f062c96e5578f0` ＝ §1 と全桁一致。`status --porcelain` は `M` 2 行のみ ―― **他 file 変更 0**。
## §4 隔離 pytest (1 走・DB 接続 0・raw = order44_pytest_raw.txt sha16 f8dd0d0c4202e837 7 行)
```
$ python3 -m pytest tests/test_sync_source_cache.py -p no:cacheprovider --basetemp=<自席> -rsxX -q
...........................                                              [100%]
27 passed in 0.80s      rc=0
```
27 ＝ 試験関数 1 本を 1 と数へた総数。`-rsxX` は skip/xfail が在れば 1 行づつ出す指定・出て居らぬ ∴ **skip 0・fail 0・error 0**。走らせたのは此の 1 file のみ(suite 全体は走らせて居らぬ)。raw は其の 1 走を写した物であり、2 度目は走らせて居らぬ。
## §5 commit と push
題 1 行目 = `sync_source_cache v3 最終形(2 file のみ): git 追跡簿基準 + EXCLUDE 帯`(本文に出所 3155e8dc0・2 blob 全桁・総監督 seq284974 を明記)。
- **tip = `b7323535bba89b59fad8fb2c6e6e7632be43a211`** / 親 = `0973f8e584d7210ec46fbc125202957772c80abe`
- `diff --stat main..tip` = `scripts/sync_source_cache.py | 287` `tests/test_sync_source_cache.py | 290` `2 files changed, 556 insertions(+), 21 deletions(-)` ＝ **2 file のみ**
- pre-commit hook が `Supabase secret scan PASS: no tracked secret values detected.` と刷つた。**hook の語であり当席の判定ではない**。
- `push origin a2-fa06a3a1-sync-rewrite-v3-main:a2-fa06a3a1-sync-rewrite-v3-main` rc=0(名指し 1 refspec・**force 無し**)→ 遠方の返り `* [new branch]`。`ls-remote` 再刷 = `b7323535bba89b59fad8fb2c6e6e7632be43a211` ＝ 手元 tip と同一(測つた)。upstream は rc=1 = 設定して居らぬ。
## §6 PR
- 新 PR **#114** `https://github.com/hakudoukai/hakudokai-dev/pull/114`・base `main`・headRefOid `b7323535bba89b59fad8fb2c6e6e7632be43a211`・state `OPEN`・`changedFiles` **2**
- `gh pr view --json` 逐語: `"mergeable":"MERGEABLE"` / `"mergeStateStatus":"UNSTABLE"`。`gh pr checks 114` = `secret-scan pending`×2 / `Vercel Preview Comments pass` / `Vercel pass (Canceled by Ignored Build Step)`(rc=8)。**CI は走り切つて居らぬ**(当席の判定ではなく gh の語)。
- 本文 = `pr_body_order44.md` 38 行 1,526 字(起点/head/出所/2 blob 全桁/試験 raw/#112 を継ぐ因/軍師の裁 284801 は未読の註/merge は総監督・secret 0 字)。
- `gh pr close 112 --comment` rc=0 → `gh pr view 112` = `"state":"CLOSED"`。comment に #114 と両 sha を書いた。merge/approve/label 0。
## §7 後片付と開示
`worktree remove /home/hakudoukai/a2/wt-v3-main` rc=0(remove 前 status 0 行) → a2 配下は **1 本**(wt-964a06d0-d3adf65b・不触)。
枝 `a2-fa06a3a1-sync-rewrite-v3`(`3155e8dc0`・#112 の物)は **消して居らぬ**・遠方の同名も残つて居る。fetch/merge/rebase/DELETE/DB 0・force 0。
開示: ⑴ `mergeStateStatus` は `UNSTABLE` であり、因は `secret-scan` が `pending` の儘である事(当席は CI を待つて居らぬ・裁は上)。⑵ 軍師の裁 seq284801・総監督 seq284974 は家老便に依る引用であり、当席は其の便を読んで居らぬ(未測)。
