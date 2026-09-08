## 何を変へたか

同じ表 `source_code_cache` へ書く器が **2 つ**在り、目 (INCLUDE/EXCLUDE) が食ひ違つて居た。
総監督 裁 288068 に従ひ **v3 (`scripts/sync_source_cache.py`) を正**として CI を其の器へ一本化する。

| | v3 | CI (旧) |
|---|---|---|
| INCLUDE (一意) | **31 本** | 28 本 (CI ⊂ v3・逆向きの差 0 本) |
| EXCLUDE | 5 本 | 7 本 (記号の差 4 = CI にのみ 3・v3 にのみ 1) |
| EXCLUDE_DIRS | 8 語 | 6 語 |
| upsert の衝突鍵 | `on_conflict=file_path` を明示 | **持たず** PostgREST の既定解決に委ねて居た |

数の断り: 1 = pattern 1 本 / path 1 本 (git の追跡簿 `git ls-files` の 1 行)。

## 触れた file は 3 本

1. `.github/workflows/sync-source-cache.yml` — 独自 POST/DELETE の heredoc python **151 行**を廃し
   `python3 scripts/sync_source_cache.py --changed-only --no-stale` の 1 行へ。
   依存を `httpx` `python-dotenv` へ、秘は**名のみ** v3 が讀む `SUPABASE_SERVICE_KEY` へ移す
   (中身は同じ `secrets.SUPABASE_SERVICE_ROLE_KEY`)。
2. `scripts/sync_source_cache.py` — `--no-stale` を足す (**既定は従前どほり**) + 目と EXCLUDE の差の理由を註で残す。
3. `tests/test_sync_source_cache.py` — 旗の有無で全表走査と DELETE が消える/残る事を各 1 本。**29 passed / 0 skipped**。

## なぜ `--no-stale` が要るか (最重の危険)

CI は `actions/checkout` の `fetch-depth: 2` = shallow ゆゑ、v3 の stale 検査は
前回 sync commit を解けず (`commit_exists` 偽) **`STALE_FALLBACK_FULL_SCAN` へ落ちる**。
落ちると `get_cached_paths()` で全表を頁繰りし、**runner の作業樹に無い INCLUDE path を悉く `delete_stale`** する。
表には他の枝でしか存在せぬ path が積つて居り (別途の讀取調査で **1,442 本 (見込み)**)、
`feature/**` の push ごとに其れが消え得る。深く clone しても、表の最新 `commit_hash` は
`live_20260608_f9139ee1` の如き **label 形**で git に解けぬゆゑ同じ穴に落ちる。
∴ **CI は書くだけ・消さぬ**。掃除は手打ちの `--full-stale-scan` で人の目の下でのみ行ふ。

## 他に見えて居る差 (見込み)

目を v3 へ揃へると、CI にのみ在つた除外 (`**/*.test.*` `**/*.spec.*` `**/test_*`) で落ちて居た
**637 本 (見込み・frontend 333 / backend 242 / scripts 49 / tests 12 / supabase 1)** が新たに書かれ得る。
此の数は当席が `fnmatch` で数へた見込みであり、v3 本体は別の照合 (`_glob_pattern_to_regex`) を使ふゆゑ実数は走らせねば測れぬ。

## 戻し方

- 此の commit を **revert すれば元の heredoc へ戻る** (触れた file は 3 本のみ)。
- 但し **消えた行は revert では戻らぬ**。ゆゑに本 PR は最初から**消さぬ形**にして居る。
- 枝は `a2/sync-cache-unify-ci-20260908` の 1 本のみ・force 無し・main 直 push 無し。

**merge の可否は総監督殿の裁を仰ぐ** (当席 = ashigaru-third-2 は owner として案と実装まで)。
