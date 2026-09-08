# ㋒ 実行 packet ―― clean main 樹 → 候補 SELECT → export → TEMP 乾走(ROLLBACK)
as_of 2026-09-07T18:52:47+09:00 / GO 総監督 hs_e2209945 seq286419(親 286415)・家老third 便 msg_20260907_184315_c47d321a
前紙 sha: order56 4cd5df0a785c131f・order52 34f11cfac4d55b42・order53 e9b562509f5f4928・order50 306816953dc056f5・v2 引継 sync_v2_lot_handover_v3.md 1e63177573db1900
數へ方: 1 = path 1 本。★行 = csv の論理行(レコード)★(v2 疵2 の読み替へ)・物理行は別に併記。

## S1 樹 (rc=0・30.9 秒)
- 動詞 `git worktree add --detach /home/hakudoukai/a2/wt-o61-main-dbf05a029 dbf05a029…` ★fetch 0・pull 0・clone 0★
- HEAD `dbf05a0294faeef9a7adc337ce34ff53ec049c10` = 局所 `origin/main`(2026-09-07 17:08:58 +0900)・`git status --porcelain` 0 行
- 自席 worktree 本数 前 1 → 後 2 → remove 後 1 (★同時 ≤2★)。`git worktree remove --force` rc=0・dir 不在を確かめた
- ★D 樹 `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` 不触★(軍師判定待ち)。共有 `/mnt/c/DentalBI` の枝は動かして居らぬ

## S2 候補集合 = 入口 regex (rc=0・0.5 秒)
- 出所(樹内 `scripts/sync_source_cache.py`): INCLUDE **L48-85**(項 35・重複除き 31)・EXCLUDE_PATTERNS **L88-94**(5)・EXCLUDE_DIRS **L101-104**(8)・`_glob_pattern_to_regex` **L375-404**・`matches_include_patterns` **L409-414**・`collect_files` **L157-178**
- ★v3 は import も走行もして居らぬ★: `ast.literal_eval` で literal のみ取り、判定は当席が同文で写した
- 母集合 `git ls-files -z` **14,738**(作業樹に無い 0・EXCLUDE_DIRS 落ち 0) → `should_exclude` 1 落ち → **14,737**
- ★INCLUDE 集合(入口 regex) = 4,201★・csv `scratch/ashigaru-third-2-fa06a3a1/o61_include_set_main_dbf05a029.csv`・sha256 `97356a6ce61f323149b1be0019fcf380cd622e14d7ffa3842ec9a4ce94f19a13`・csv 行 4,202(header 1 + データ 4,201)
- 出口 fnmatch 版との差(同じ 14,737 に両者を掛けた): 出口 3,637／両方 3,578／★入口のみ 623★／★出口のみ 59★ ∴ order53 の食ひ違ひは本樹でも現に在る

## S3 候補 SELECT (讀取のみ・rc=0)
```
CREATE TEMP TABLE o61_main (file_path text PRIMARY KEY);
\copy o61_main (file_path) FROM '<S2 csv>' WITH (FORMAT csv, HEADER true)
SELECT count(*) FROM public.source_code_cache s
  WHERE NOT EXISTS (SELECT 1 FROM o61_main m WHERE m.file_path = s.file_path);
```
- 表の現行 行数 **5,806**(REST `Content-Range 0-0/5806` と psql `count(*)` の二器で一致)・S2 を TEMP へ `COPY 4201`
- ★候補 = 表に在り S2 に無い = 1,649★／逆向き(S2 に在り表に無い) 44
- 区分(order50・当席が局所で照合): ㋑ 局所 249 ref 合併 INCLUDE(5,678) に在り main tip に無い = **729**／㋺ 履歴 D で消え現 tree に無い INCLUDE(母数 402) = **24**(㋑ と重なり 4)／㋑∪㋺ = 749／★其の外 = 900★(内 CI #2 の集合に当たる 147)
- 候補 1,649 の頭 dir(件数のみ・path 値は csv にのみ): frontend 708・docs 339・backend 155・`.agents` 150・`hakudokai-shogun-r1` 45・頭が空 27・scripts 25・outputs 25
- ★`.agents`(150)・`hakudokai-shogun-r1`(45)・`outputs`(25)・頭が空(27=先頭 `/` の絶対 path 様)は現 main の追跡簿にも局所 249 ref 合併にも無い★ ―― 出所は測つて居らぬ
- ㋩ は order50 で「現に無い」と測つたが、本測では候補 1,649 の内 317 本が CI #2 の集合に当たる(其の外 900 の内は 147)。CI が現に走つて居るかは測つて居らぬ

## S4 export (rc=0)
- 列リスト(明示) `file_path, content, file_size, line_count, commit_hash, updated_at, created_at`(表定義 `supabase/migrations/20260403020939_create_source_code_cache.sql` の列順と同一)
- `\copy (SELECT <上記 7 列> FROM public.source_code_cache s WHERE NOT EXISTS (…) ORDER BY file_path) TO '<csv>' WITH (FORMAT csv, HEADER true)` → `COPY 1649`
- csv `scratch/ashigaru-third-2-fa06a3a1/o61_candidates_export.csv`・sha256 `3af768ba96d4b27f2901bc39fb0d7a3173f7f3b26ecd61c1a08133e4c3337d9a`・45,632,972 byte
- ★行数の別★ 論理行(データ) **1,649**・物理行 393,779(`content` 中の改行ゆゑ)・header 1 ∴ v2 疵1(列リスト)・疵2(論理行)を踏んで居らぬ

## S5 TEMP 乾走 (rc=0)・script 全文 `o61_s5_dryrun.sql`
```
\set ON_ERROR_STOP on
\set expected 1649
BEGIN;
CREATE TEMP TABLE o61_restore (LIKE public.source_code_cache INCLUDING DEFAULTS);
\copy o61_restore (file_path, content, file_size, line_count, commit_hash, updated_at, created_at) FROM '<csv>' WITH (FORMAT csv, HEADER true)
SELECT count(*) AS loaded FROM o61_restore \gset
\echo 'loaded=' :loaded ' expected=' :expected
SELECT (:loaded = :expected) AS gate_ok \gset
\if :gate_ok
\echo 'GATE: loaded = expected'
SELECT count(*) AS would_match_in_table FROM public.source_code_cache s WHERE EXISTS (SELECT 1 FROM o61_restore r WHERE r.file_path = s.file_path);
\else
\echo 'GATE: loaded <> expected'
\endif
ROLLBACK;
SELECT count(*) AS after_rollback_total FROM public.source_code_cache;
SELECT to_regclass('pg_temp.o61_restore') IS NULL AS temp_gone;
```
- 出力(逐語) `COPY 1649` / `loaded= 1649  expected= 1649` / `GATE: loaded = expected` / `would_match_in_table = 1649` / `ROLLBACK` / `after_rollback_total = 5806` / `temp_gone = t`
- ∴ 表に当たる行は 1,649 で csv と一致し、門は通り、tx は ROLLBACK で閉ぢた

## 触れて居らぬ事
★DB 書込 0(COMMIT 0・TEMP は 2 tx 内のみで何れも ROLLBACK)・DELETE 0・UPDATE/INSERT 0・DDL 0(本番 table へ 0・TEMP のみ)・本番 table 行数 5,806 は前後で不変(S4 後・S5 後の二度測つた)★。v3 走行 0・`--dry-run` 0・fetch/pull/clone 0・push 0・本番 code 書込 0・shell `>`/`>>`/tee 0(csv は `\copy`、其の外は python `open()`)。
credential: 自席 env に既に在る `SUPABASE_URL`/`SUPABASE_SERVICE_KEY`/`DATABASE_URL` のみ用ゐた。secret file の探索 0・値は本紙に一字も無い。

## 境界
- 候補 1,649 は ★本 packet を作つた時點の表(5,806)★ に対する物。前紙の 5,668 とは ★138 の開き★ が在り、其の間に誰が書いたかは測つて居らぬ ∴ DELETE を打つ前に S3 を測り直さねば件数は保証されぬ
- ㋑ の母集合は局所 249 ref の合併であり遠隔のみの枝(order59 の 17 本)を含まぬ ∴ ㋑ は ★下限★
- 「其の外 900」の出所は測つて居らぬ。CI #2 が現に走つて居るかも測つて居らぬ
- DELETE の打手は総監督殿。当席は打たぬ。csv・sql は局所 scratch(reports の外)に在る
