# push 991d4987a → refs/heads/dry/reserveimage-77a10783-audit-bundle (order60)
GO: 總監督 seq286399 (條件改め・親 286262/286395)・Y 依頼 seq285592 hs_8c8719a2 / 家老third 經由 msg_20260907_183436_20281b6e
as_of 2026-09-07T18:37:15+09:00 / 席=ashigaru-third-2 / 對象 repo=/mnt/c/DentalBI / remote=origin

## §1 前測 5 點 (悉く令の記述と一致・1 つも違はず)
| # | 測り | 結果 |
|---|---|---|
| P1 | `git cat-file -t 991d4987a…` | **commit** |
| P2 | `git log -1 --format='%H %P %an'` | 親=**ccb39de3d8a6f0d943f051e775bda085a55683be** / author=**reserveimage** |
| P3 | `git ls-remote origin refs/heads/dry/reserveimage-77a10783-audit-bundle` | **出力 0 行 = 新規** |
| P4 | `git ls-remote origin refs/heads/karo-third/a2-14c8ec72-fixed` | **ccb39de3d8a6…** |
| P5 | `git merge-base --is-ancestor ccb39de3d8a6 origin/karo-third/a2-14c8ec72-fixed` | **rc=0** |
- 併記: `diff --stat ccb39de3d..991d4987a` = **4 file・120 insertions・0 deletions**、頭 dir は **reports のみ** (`reports/evidence/77a10783/` の README.md・negative.raw・positive.raw・verify_block1_two_papers.py) ∴ **製品 source 0**。

## §2 push (force 無・此の 1 refspec のみ・timeout 300)
`git push origin 991d4987a584e0f5e32945c867ff327babcecc24:refs/heads/dry/reserveimage-77a10783-audit-bundle` → **rc=0**。返り逐語: `* [new branch]  991d4987a584e0f5e32945c867ff327babcecc24 -> dry/reserveimage-77a10783-audit-bundle`。

## §3 pre-push hook の副作用 (令の求めに依り開示)
- `[dup-check] PASS: 新規path 24件を検査、二重実装0件` ―― 之は **hook が刷つた器の語**であり當席の判定ではない。
- `[pre-push] source_code_cache sync SKIPPED (DB負荷止血 2026-09-07・main は CI が同期・強制は SYNC_SOURCE_CACHE_FORCE=1)` ―― hook L58-61 の既定分岐。**當席は `SYNC_SOURCE_CACHE_FORCE` を設けて居らぬ**(押す前に未設定を確かめた) ∴ **DB への書込 0**。
- ∴ 外部書込は **0 件**。hook が走らせた python は dup-check **1 本**のみ。
## §4 push 後の讀返し
`git ls-remote origin refs/heads/dry/reserveimage-77a10783-audit-bundle` → **991d4987a584e0f5e32945c867ff327babcecc24**・rc=0。
遠隔 ref 總數 (peeled 除く): 押す前 **277** (HEAD1/heads150/pull123/tags3) → 押した後 **280** (HEAD1/heads**151**/pull**125**/tags3)。heads **+1** = 本 push。pull **+2** = **當席の手ではない** (18:32→18:38 の間に他者が立てた物)。main・他 ref へは **0 打**。
## §5 境界
- 押したのは **1 refspec のみ**・**force 無**・**新規枝**ゆゑ上書きした物は無い。取消しの判は總監督殿 (當席は打たぬ)。
- GO は家老third 經由の便で受けた物であり、當席は seq286399 を DB で直に讀んで居らぬ (DB 0 の床)。
- pull **+2** は ls-remote の 2 時點の引き算であり、誰が何を立てたかは測つて居らぬ。
- dup-check は `origin/main...HEAD` を診る作りで、HEAD は當時 `wp-a1-a3-3-20260723` ―― **押した commit とは別**。其の PASS は本 push の中身を診た結果ではない。
