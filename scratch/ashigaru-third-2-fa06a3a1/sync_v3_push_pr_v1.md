# sync_v3 push と PR 起票 (order41) as_of 2026-09-07 / 席=ashigaru-third-2

## §1 push 前の再測 (樹 = /mnt/c/DentalBI・共有樹は触れて居らぬ)
- tip  `3155e8dc0893f3ff40eb809d9fcae0c08f97875c` (rev-parse で測つた)
- 親   `ce3b08dbeb0f9d42bec9ed79ac45d5f6da8c9020` (同上)
- 遠方 `ls-remote refs/heads/a2-fa06a3a1-sync-rewrite-v3` → 行数 0 = 遠方に無かつた
- 遠方 main `0973f8e584d7210ec46fbc125202957772c80abe`
- 共有樹 HEAD は `wp-a1-a3-3-20260723` の `ecb571234` に動いて居た(他席の物・不触)

## §2 push (打つた形)
`git push origin a2-fa06a3a1-sync-rewrite-v3:a2-fa06a3a1-sync-rewrite-v3`
名指し 1 refspec のみ / force 無し / 他枝 0 / 共有樹の checkout・branch 切替 0。rc=0。
遠方の返り逐語 = ` * [new branch]          a2-fa06a3a1-sync-rewrite-v3 -> a2-fa06a3a1-sync-rewrite-v3`
pre-push hook が 2 行刷つた。**hook の語であり当席の判定ではない**:
- `[dup-check] PASS: 新規path 3件を検査、二重実装0件`
- `[pre-push] source_code_cache sync SKIPPED (DB負荷止血 2026-09-07・main は CI が同期・強制は SYNC_SOURCE_CACHE_FORCE=1)`

## §3 push 後の再刷
`ls-remote` → `3155e8dc0893f3ff40eb809d9fcae0c08f97875c refs/heads/a2-fa06a3a1-sync-rewrite-v3`
∴ 遠方 tip と手元 tip は同一の 40 字であつた(測つた)。

## §4 PR
- 番号 **112** / URL `https://github.com/hakudoukai/hakudokai-dev/pull/112`
- base `main` / head `a2-fa06a3a1-sync-rewrite-v3` / headRefOid `3155e8dc0893f3ff40eb809d9fcae0c08f97875c`
- state `OPEN` (gh pr view --json の値・逐語)
- 題 `sync_source_cache v3(git 追跡簿基準+EXCLUDE 帯)`
- 本文 = `scratch/ashigaru-third-2-fa06a3a1/pr_body_order41.md` (31 行・1,239 字)。
  載せた値 = fixed sha / 0004 sha16 `7e13a766854ced5b` / 軍師の裁 seq284801 / 紙 2 本の sha16
  (`bc7554d022008b25` `63cfeac1b5787c70`) / 「merge は総監督・DELETE 0」。secret は 0 字。
- merge 0 / approve 0 / label 0 / review 依頼 0 ―― 打つて居らぬ。

## §5 開示 (令の欠・食ひ違ひ)
1. 軍師の裁 seq284801 と総監督 GO seq284835 は **家老便に依る引用であり、当席は其の便を読んで居らぬ(未測)**。
   PR 本文にも同じ註を付けた。
2. 共有樹 HEAD は order38/order40 の刻の `1fbd0aa0f` から `ecb571234` へ動いて居る。
   §1 の `apply --check` rc=0 は **`1fbd0aa0f` の樹で採つた値**であり、今の HEAD で採り直しては居らぬ。
3. 本枝は base `1fbd0aa0f` から起こして居り、遠方 main `0973f8e5` との間は当席は測つて居らぬ。
