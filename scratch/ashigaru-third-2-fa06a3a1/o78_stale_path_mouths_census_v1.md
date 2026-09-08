# order78 甲: stale 経路を呼ぶ口の悉皆 (讀取のみ・DB 0・書換 0)

as_of 2026-09-08 06:0x JST / 席 ashigaru-third-2 / 令 order78 (家老 msg_20260908_053548_ed49c6d5)
★底本 = origin/main `cc3eaee5d`★ (CI が現に走る枝)。v3 = 766 行・抽出 sha256_16 `16e2db65f8cb48fa`。
1 = 口 1 箇所 / path 1 本。網の形は §1。前紙 `499b845d768a5c03`(order76)・`64e58a29ba32995d`(order77) 不触。

## §0 ★己の取り違へを先に開示する★
本弾の初手、当席は `/mnt/c/DentalBI` の ★作業樹★ を底本として讀んだ。作業樹の枝は `wp-a1-a3-3-20260723`
(HEAD `4a7e1891e`) であり、其処の CI yml は ★199 行の内蔵 heredoc★・v3 は 709 行で `--no-stale` を持たぬ。
∴ 一度は「CI は v3 を呼ばぬ」と讀んだ。之は ★誤り★ である。origin/main では order73 の符 `ce83b5c0d` が
在り (`git merge-base --is-ancestor` = 在る)、CI は 63 行に畳まれ v3 を呼ぶ。
- 前紙 o76 §L37「現行 CI は `--changed-only --no-stale`」は ★origin/main に対しては正しい★。書き換へず此処に併記する。
- blob の異同 (實測): CI yml `HEAD 332007bfae75` / `origin/main 3d2dbae7ae84` = 差 ・ v3 `0754d9284db2` / `3bcd289d18ad` = 差 ・
  `scripts/git-hooks/pre-push` = ★同 `911cbab96061`★。
- ★教訓★: 作業樹の枝は main では無い。CI の話をする時は `git show origin/main:` で取れ。

## §1 網の形 (どう数へたか)
- 口の悉皆 = `git grep -n -F 'sync_source_cache'` を ★実行され得る族★ (`*.yml *.yaml *.sh *.py scripts/git-hooks/*`) に限り、
  `docs/` `reports/` (監査 log・報告 raw) を落とした。落とした族に在るのは ★言及であつて実行の口では無い★。
- 実装済 hook = `/mnt/c/DentalBI/.git/hooks/` を直に讀んだ (worktree は hooks を共有樹と共有する)。
- proxy 孤児 = 局所 ref 236 本 (heads+remotes) の合併 20,482 path から 現樹の INCLUDE 集合を引いた 16,369 本。
  ★DB の行では無い★ (DB 讀 0)。規 = `scratch/ashigaru-third-2-fa06a3a1/o78_stale_path_census.py` 52 行。

## §2 呼ぶ口の悉皆 (族・file:行・逐語・判定)
| # | 族 | file:行 | 判断の逐語 | 判定 |
|---|---|---|---|---|
| 1 | CI yml | `.github/workflows/sync-source-cache.yml:63` | `run: python3 scripts/sync_source_cache.py --changed-only --no-stale` | ★走らぬ★ |
| 1' | 同 の門 | `scripts/sync_source_cache.py:693-694` | `if no_stale:` / `print("-- STALE_SKIPPED: reason=--no-stale", file=sys.stderr)` | 門が閉ぢる |
| 1'' | 同 の発火 | `.github/workflows/sync-source-cache.yml:3-6` | `on:` `push:` `branches:` `- main` / `- 'feature/**'` | 自動で走るは此の口のみ |
| 2 | hook (実装済) | `scripts/git-hooks/pre-push:58-60` | `if [ "${SYNC_SOURCE_CACHE_FORCE:-0}" != "1" ]; then` … `exit 0` | ★条件付き★ |
| 2' | 同 の本体 | `scripts/git-hooks/pre-push:64` | `if "$PY" "$SYNC_SCRIPT" --changed-only; then` (★`--no-stale` 無し★) | env=1 なら stale 走る |
| 2'' | 同 の実体 | `.git/hooks/pre-push` (70 行・disk sha256_16 `e4a47593600691e3`) | 追跡簿の型と ★同一★ (git blob `911cbab96061`) | 同上 |
| 3 | hook (退避) | `.git/hooks/pre-push.bak-loadshed-20260907:55` (61 行・`6284d288f4f4e21d`) | `"$PY" "$SYNC_SCRIPT" --changed-only` (★門無し★) | ★走らぬ★ (名が `pre-push` で無い) |
| 4 | hook (別) | `.git/hooks/pre-commit` | `sync_source_cache` の出現 ★0 件★ | ★走らぬ★ |
| 5 | script | `scripts/sync_source_cache_secondpc.py` (219 行) | `stale`/`delete`/`DELETE` の出現 ★0 件★ | ★走らぬ★ |
| 6 | 試験 | `tests/test_sync_source_cache.py:154,184,224` | `monkeypatch.setattr(m, "delete_stale", lambda stale: 0)` | 模擬 (DB へ行かぬ) |
| 7 | 手打ち | `CLAUDE.md:528` (共有樹の冠正本) | ``手動で全件同期したい場合: `python scripts/sync_source_cache.py` `` | ★走る★ (旗無し) |
| 8 | 手打ち | `docs/setup_secondpc.md:90` | `SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_ROLE_KEY" python scripts/sync_source_cache.py` | ★走る★ |
| 9 | 手打ち | `docs/setup_secondpc.md:108` | ``- [ ] `python scripts/sync_source_cache.py` が `Errors: 0` で完走`` | ★走る★ |
| 10 | 手打ち | `scripts/git-hooks/pre-push:67` | `run 'python scripts/sync_source_cache.py' manually` | ★走る★ |
| 11 | 旗 | `scripts/sync_source_cache.py:607,621` | `if dry_run:` … `return` | `--dry-run` は stale へ ★届かぬ★ |

## §3 結び ―― 走る道は何本か
- ★人手も env も要らず 自動で stale が走る道 = 0 本★。
  (自動の口は CI ただ 1 つで、其れは `--no-stale` を明示して門を閉ぢて居る = `:693-694`)
- 条件付き = ★1 本★ (hook・`SYNC_SOURCE_CACHE_FORCE=1` を人が置いた時のみ)。
- 人が一行打てば走る口 = ★4 箇所★ (file 3 本: 冠正本 CLAUDE.md・setup_secondpc.md×2・hook の失敗文言)。
- ∴ 「今は自動では誰も踏まぬ道」であるが「★人が一行打てば踏む道★」である。全き死道では無い。

## §4 (別節) 其の道は 1,442 本を消し得るか
- 手打ちの plain run が入る枝は二つ。`:713` `if full_stale_scan or not prev_commit:` が分ける。
  - prev_commit が DB か state file で解ける時 → `:721` `stale_paths_from_git` = 母集合は ★prev..HEAD の D/R 差分★ ∴ 孤児には ★届かぬ★。
  - 解けぬ時 (`STALE_FALLBACK_FULL_SCAN: reason=no_prev_commit`) → `:718` `compute_stale_paths(cached_paths, all_local_paths)`
    = ★全表 cached の内 現樹に無く INCLUDE(fnmatch) に当たる行を悉く消す★。`--full-stale-scan` を明示すれば無条件で此の枝。
- ★∴ 消し得る★。proxy で測つた本数 (實測・§1 の網):
  | 目 | proxy 孤児の内 消す側 | 
  |---|---|
  | fnmatch (現行 `compute_stale_paths`) | ★1,722★ |
  | regex (order76 の案文を当てた後) | ★1,724★ |
  | 差 | fnmatch のみ ★74★ / regex のみ ★76★ |
- ★数の断り (四条③)★: 此の 1,722 は ★局所 ref 236 本の合併 − 現樹★ であり、総監督殿の 1,483 / 1,442 は ★DB の行★。
  元素が別ゆゑ ★足すな・比べるな★。DB は讀んで居らぬ ∴ 現に何本消えるかは ★確かめて居らぬ★ (六条)。
- ★order76 の案文への効き★: 総数は 1,722 → 1,724 と殆ど動かず、動くのは ★顔ぶれ 74/76 本の入替へ★。
  即ち案文の値打ちは「消える本数を減らす」事では無く「入口と出口の目を揃へる」事に在る。

## §5 危険と境界
- 危険①: hook の退避版 `.bak-loadshed-20260907` は ★門を持たぬ★ (§2 #3)。名を `pre-push` へ戻すと push 毎に stale が走る。
- 危険②: 冠正本 `CLAUDE.md:528` は旗無しの plain run を人に指図して居る ∴ 清くない樹で打てば §4 の全表枝へ落ち得る。
- 危険③: CI は shallow clone ゆゑ prev_commit を解けぬ = `--no-stale` を外した瞬間に §4 の全表枝へ落ちる (CI 自身が `:53-55` で其の理由を書いて居る)。
- 境界: 讀取のみ。DB 讀 0・書 0・SQL 0・fetch/pull/prune 0・push 0・製品 file の書換 0。走らせたは census 規のみ
  (v3 を import して matcher を呼ぶ・`main()` は走らせぬ)。★他 PC (main/second/mac) の実装済 hook は手が届かぬ ∴ 確かめて居らぬ★。
