# source_code_cache 同期 1 回の DB 負荷（讀取のみ・order27）
席=ashigaru-third-2 / 令=order27 (msg_20260907_085035_3223df6f)
対象=/mnt/c/DentalBI/scripts/sync_source_cache.py sha16=1bb2eb405e0781cc 464 行
repo HEAD=d33f265138151400（作業中 25e417fe4a2b8d5b→d33f2651 と動いたゆゑ全數を本 HEAD で再測）
禁の遵守: DB 書込 0・DB 讀取 0・`--dry-run` 以外の走行 0・共有樹書込 0・push 0・install 0・worktree 新設 0・secret 値 0(env 名のみ)・/tmp 不使用(產は全て scratch 自席 dir)

## 1. 母数表（1 = file 1 本 / byte = 実 file の byte）
collect_files を模した讀取。module は import せず ast で INCLUDE/EXCLUDE 定数のみ取り出した（`.env` は開いて居らぬ）。INCLUDE 35 本(重複除き 31)・EXCLUDE 5・EXCLUDE_DIRS 4・BATCH_SIZE 50。
| dir | file 数 | byte |
|---|---|---|
| docs | 384 | 150,511,962 |
| frontend | 1320 | 10,423,451 |
| backend | 743 | 9,511,950 |
| scripts | 539 | 3,015,379 |
| supabase | 789 | 2,552,442 |
| tests | 193 | 2,028,163 |
| .claude | 139 | 1,310,755 |
| tools | 25 | 221,499 |
| infra | 15 | 92,740 |
| 直下 CLAUDE.md | 1 | 113,591 |
| **和** | **4148** | **179,781,932** |
中央値 4,504B・最大 12,717,930B・1MB 超 36 本。git ls-files 13949 本の内 母数に入るは 4101 本、残り 47 本は untracked（母数は git 管理の有無を見ず glob で採る）。

## 2. dry-run 集計表（1 = INSERT 文 1 本 / row 1 = upsert される row 1 本）
`python3 scripts/sync_source_cache.py --dry-run`。main L343-357 で印字後 return し REST 呼出に至らぬことを讀んで確かめた。stdout 181,427,289 byte・rc 0・43.3s。
| 項 | 數 | 何を 1 と數へたか |
|---|---|---|
| 母数 file | 4148 | glob で採れた file 1 本 |
| dry-run が印字した INSERT 文 | 4125 | 文頭 `INSERT INTO source_code_cache (…` 1 本 |
| 実行時に row 化される件数 | 4128 | batch に積まれる dict 1 本 |
| 実行時 payload（content の utf-8 byte 和） | 178,062,459 | NUL 除去後の byte |
| batch50 の POST 回数 | 83 | ceil(4128/50) |
| dry-run 出力 byte | 181,427,289 | stdout の byte（SQL 骨と `''` 逃がしを含む） |
差の内訳（自席で全 4148 本を開いて數へた）: not_found 0・空(content.strip() が空) 20・utf-8 で復号できぬ 3・NUL 混入 5。dry-run は復号できぬ 3 本を印字せず(`continue`)、実行時は置換して同期する(L373-379)。∴ 文数 4125 = 4148−20−3、実行時 row 4128 = 4148−20。**dry-run は実行時より 3 本少ない。**

## 3. REST / SQL 形表
| 呼出 | REST | SQL 相当 | 回数 |
|---|---|---|---|
| upsert_batch L143-157 | POST ?on_conflict=file_path, Prefer: return=minimal,resolution=merge-duplicates, timeout 60 | INSERT … ON CONFLICT (file_path) DO UPDATE SET … | ceil(row/50) |
| get_cached_paths L241-263 | GET ?select=file_path&offset=K&limit=1000, timeout 30 | SELECT file_path FROM source_code_cache LIMIT 1000 OFFSET K（**WHERE 無・ORDER BY 無**） | floor(N/1000)+1 |
| delete_stale L266-284 | DELETE ?file_path=in.("a","b",…), timeout 30 | DELETE FROM source_code_cache WHERE file_path IN (…) | stale>0 なら 1（件数に依らず 1 req・URL 長は件数に比例） |
N = cache の現行 row 数。当席は SELECT を打つて居らぬゆゑ N は**測つて居らぬ**。stale 検査は `--changed-only` でも縮めず全 collect_files を母集合に渡す(L422 註記)。∴ **GET の回数は full と changed-only で変はらぬ。**

## 4. 突き合はせ表（総監督実測 hs_18460a32 と当席算）
| 項 | 総監督実測 | 当席算 | 一致/不一致 |
|---|---|---|---|
| INSERT 回数 | 106 回 / 19s | 83 回 (4128 row ÷ 50) | **不一致**（差 23 回） |
| 106 回が含意する row 数 | — | 5251〜5300 (ceil(n/50)=106) | 当席 4128 と**不一致** |
| LIMIT/OFFSET 回数 | 12 回 / 1.5s | floor(N/1000)+1 | 12 なら N=11000〜11999、6 回×2 走行なら各 5000〜5999 |
| 1 回あたり秒 | INSERT 0.179s / GET 0.125s | 総監督の數の割算 | 当席は打つて居らぬゆゑ**測つて居らぬ** |
不一致の候補因（いづれも当席では**測つて居らぬ**、DB 讀取が禁ゆゑ）:
(a) 走者が別 —— CI (.github/workflows/sync-source-cache.yml sha16=f2a94fa4e67faa65・199 行) は **script を呼ばず inline python** で 1 file = 1 POST（batch 無し）、GET の頁繰りは皆無。∴ 106 回/12 回の形は CI からは出ぬ（file を讀んで確かめた構造の事実）。
(b) cache に残つた古い row —— order26 で塞いだ経路（stale 掃除の失敗を握り潰し 0 で終へる）が働いて居た間、消え損ねた row は誰にも報せず溜まる。row が母数より多ければ GET 頁も INSERT も増える。
(c) 走行が重なつた / 別枝・別樹で走つた。

## 5. 見積表（script が走つた 1 回あたり）
| | full | --changed-only (現 HEAD) |
|---|---|---|
| 対象 row | 4128 | 6 |
| payload byte | 178,062,459 | 51,236 |
| POST 回数 | 83 | 1 |
| GET 回数 | floor(N/1000)+1（N 未測） | 同左（**縮まぬ**） |
| DELETE 回数 | stale>0 なら 1 | 同左 |
| 秒（総監督の単価で割算） | POST ≒ 14.9s ＋ GET | POST ≒ 0.2s ＋ GET |
changed-only の差分 18 本の内 母数に入るは 6 本（残り 12 本は INCLUDE 外）。

## 6. 令の前提と実測の食ひ違ひ（開示）
令は「同期 1 回(=1 push)」と置くが、**現在の pre-push は既定で同期を走らせぬ**。/mnt/c/DentalBI/.git/hooks/pre-push sha16=e4a47593600691e3・70 行・L58-61 逐語:
```
if [ "${SYNC_SOURCE_CACHE_FORCE:-0}" != "1" ]; then
  echo "[pre-push] source_code_cache sync SKIPPED (DB負荷止血 2026-09-07・main は CI が同期・強制は SYNC_SOURCE_CACHE_FORCE=1)"
  exit 0
fi
```
∴ 現時点で push 1 回 = script 由来の DB 呼出 0 回（`SYNC_SOURCE_CACHE_FORCE=1` の時のみ L64 の `--changed-only` が走る）。本紙の見積は「script が走つた 1 回」の數であり push 1 回の數ではない。止血がいつ・誰の手で入つたかは**測つて居らぬ**（本樹で git log を追つて居らぬ）。

## 7. SELECT 提案（打たず・DB 讀取 0 を保つ）
1. `SELECT count(*) FROM source_code_cache;` → §4 の含意(5251〜5300 / 11000〜11999)と突き合はせる。
2. `SELECT count(DISTINCT file_path) FROM source_code_cache;` → ORDER BY 無し OFFSET 走査の取りこぼしを見る。
3. `SELECT file_path, file_size FROM source_code_cache ORDER BY file_size DESC LIMIT 20;` → §1 の 1MB 超 36 本と突き合はせる。
4. `SELECT commit_hash, count(*) FROM source_code_cache GROUP BY 1 ORDER BY 2 DESC LIMIT 10;` → 走者と走行回数の切り分け(§4 a/c)。
5. `SELECT count(*) FROM source_code_cache WHERE updated_at < now() - interval '7 days';` → 消え損ねた row の量(§4 b)。
6. `SELECT pg_size_pretty(pg_total_relation_size('source_code_cache'));` → §2 の 178,062,459 byte と突き合はせる。

## 8. raw（產と數の出所・同 dir scratch/ashigaru-third-2-fa06a3a1/）
| file | sha16 | 中身 |
|---|---|---|
| order27_scope.json | ccc4ac3d24e5b98e | 母数 4148 本の list と byte |
| order27_dryrun_agg.json | 7e1428146eef4ee2 | 1 巡目集計(stdout 181,427,289 / 43.3s / rc 0) |
| order27_dryrun_agg2.json | eca9aad324b68ad3 | 2 巡目集計(区切り 4124・scope 外 0・62.4s) |
| order27_dryrun_head.txt | deb99e293ff54ca3 | dry-run 出力の先頭 400 byte |
| order27_rowcount.json | e0a72087af527c2d | 空 20 / 非復号 3 / NUL 5 / row 4128 |
| order27_changed_only.json | de941dcc92ce86ba | changed-only 6 本・51,236 byte |
| order27_dryrun_collect.py / collect2.py | fc797f3c65ffadf4 / a0319df8bc920ba4 | 讀取用の集計 script（当席作） |
dry-run 出力の先頭 2 行（逐語）: `INSERT INTO source_code_cache (file_path, content, line_count, file_size, commit_hash, updated_at)` / `VALUES ('.claude/agents/audit-verify.md', '---`
stderr 逐語 2 行: `-- Full sync mode: 4148 files detected` / `-- Dry-run complete: 4148 files`

## 9. 數の限界と過ちの開示
- 1 巡目は文頭句の出現を數へて 4185 を得たが、**同じ句が同期対象 file の中身にも現れる**（本 script 自身を含む）。2 巡目は `\n\nINSERT …\nVALUES ('` を区切りに割り、scope 内・単調増加のみ採つて 4124 を得た。先頭 1 文は前に `\n\n` が無く区切りに掛からぬゆゑ 印字文数 = 4124+1 = 4125（§2 の内訳と合ふ）。
- payload byte は当席が file を開いて數へた値であり、**DB が受け取つた byte ではない**（JSON 化・圧縮・網の実量は測つて居らぬ）。
- 秒は全て総監督の實測値の割算であり、当席は 1 度も REST を打つて居らぬ。
- order26 の作業中、当席は一度 `/tmp/a2_dst_sync_source_cache.py` を置いた（後に scratch へ移した）。「/tmp 不使用」の床は order27 で着いたゆゑ order26 の時点では未着だが、事実として記す。
- 語の註: 上に現れる `SKIPPED` / `SKIP` / `FORCE` は hook と script の逐語であり、当席の判定語ではない。
三択語: 測つた=§1〜3・5・8 の全數と §6 の hook 逐語。測つて居らぬ=cache の row 数 N・106/12 の走者・止血の入つた時刻・DB 側の受信 byte。測れぬ=無し。
as_of: 2026-09-07 09:10 JST
