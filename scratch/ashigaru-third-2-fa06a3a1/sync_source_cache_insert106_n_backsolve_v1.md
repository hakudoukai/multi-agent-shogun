# INSERT106 の N 逆算と SELECT 3 本の期待形 (讀取のみ・DB 読書 0・走行 0)

as_of 2026-09-07 16:2x JST / 席 ashigaru-third-2 / 令 order48 / 前紙 3fddc938ffde158b 不触
底本 repo=/mnt/c/DentalBI・v3 blob `0754d9284db2d50c5f3941ad1d3cf786d5279de9` (709 行)
材料 07:55 crash recovery 直後の `pg_stat_statements` (総監督殿の實測・当席は DB を 1 本も打つて居らぬ)

## §1 batch 式 (blob 行番号・逐語)
- L107 `BATCH_SIZE = 50` / L612 `if len(batch) >= BATCH_SIZE:`→L613 (満 50 で吐く) / L620 `if batch:`→L621 (端数 1 度)
- L200 `upsert_batch` = POST 1 本 = INSERT 1 発行。L220 `MAX_UPSERT_TRIES = 3` ゆゑ transient は同一文が最大 3 回 (L235)。L265 `upsert_with_isolation` は非 transient 失敗で L284 `for row in batch:` = +len(batch) 単発 (最大 50)、transient 継続は L280 で止まり fan-out せぬ。
- 母集合 M = N − skipped (L579 not found・L593 empty)。∴ 束の数 = ceil(M/50)。

## §2 逆算 (INSERT 発行数 = 106 と置く)
- 束のみ (retry 0・隔離 0): ceil(M/50)=106 ⇔ ★M ∈ [5251, 5300]★ (端数 1〜50)。
- 一般形: 106 = ceil(M/50) + 隔離 k + retry r。∴ 隔離/retry/複数走行の和なら M の下限は下がり ★式は 1 つに定まらぬ★。

## §3 時点別 N (讀取のみ・fetch 0・当席が数へた 22 時点)
数へ方: 各 commit の `git ls-tree -r --name-only` を母集合に、其の commit 自身の INCLUDE/EXCLUDE/EXCLUDE_DIRS を当てた
(matcher は blob L377 glob→regex と L124 fnmatch を写した)。1 と数へたのは「其の tree に在る path 1 本」。

| 時点 | 日付 | N | ceil(N/50) |
|---|---|---|---|
| origin/main 620df477e | 09-07 | 4185 | 84 |
| 9daaafde1 局所枝先端 | 09-07 | 4103 | 83 |
| 7f3f371b9 | 09-02 | 3959 | 80 |
| eaa254472 | 07-21 | 2599 | 52 |
| 36e5b4a47 INCLUDE 拡張 | 05-03 | 2107 | 43 |
| 3e6d34d2a | 04-07 | 1031 | 21 |

(全 22 行は `order48_n_by_commit.py` の出力。上表は極値と INCLUDE 改訂点の抜粋。04-06 以前は INCLUDE 表が無く N=0)
- 106 batch に当たる時点 (N ∈ [5251,5300]) は ★現に無い★ ── 追跡簿基準の最大が 4185。
- v2 以前の入口は ★作業樹 glob★ (L157 docstring 逐語「v2 まで: repo_root.glob」) ゆゑ、当時の實母集合は追跡外 (.venv 等) を含み tree からは ★測れぬ★。
- 4103 対 order47 の 4113 の差 10 は「commit tree を数へた」対「作業樹 index を数へた」の違ひ。どちらが正かは ★測つて居らぬ★。

## §4 106 を作り得る他の道 (upsert 以外・併記)
1. `--changed-only` (L523/L533) の小走行 (1 走 ≒ ceil(変更数/50) ≒ 1 本) の ★和★。
2. 隔離 (L284) の単発・retry (L235) の再発行。pg_stat_statements は文を正規化するゆゑ 50 行束と 1 行単発が ★同一 entry に合算される可能性★ (当席は DB を讀まぬゆゑ 測れぬ)。
3. 統計の起点。crash recovery で統計が捨てられて居れば 106 は 07:55 以降の累計。起点は 測つて居らぬ。
4. 当 script 以外の経路が同表へ INSERT する場合 ── 有無を 測つて居らぬ。

## §5 SELECT 3 本の期待形と判定表 (総監督殿の実行材料・当席は 0 本)
★① pg_stat_statements を `query ILIKE '%source_code_cache%'` で絞る★
期待列 queryid / left(query,80) / calls / rows / total_exec_time / mean_exec_time / stats_since ・期待行数 3〜8
- rows ≒ 50×calls → 束のみ ⇒ M ≒ 5300 ⇒ §3 に当たる時点は無く、作業樹 glob 期か走行の和と読む
- rows ≒ calls (≒106) → 単発の集まり (隔離 or --changed-only)、中間 → 混在と読む / calls=83 or 84 の entry が別に在る → v3 定常 1 走 (§3 の 4103/4185) に対応する
- stats_since が 07:55 より後 → 106 は 07:55 以降の累計と読む

★② `source_code_cache` の総行数と file_path 先頭 1 階層別の内訳★
期待列 prefix / cnt (+総計 1 行)・期待行数 8〜12 (backend/frontend/scripts/docs/supabase/infra/tests/tools/.claude/CLAUDE.md)
- 総行数 ≒ 4185 ± 変更分 → v3 の母集合 (origin/main) と対応する
- `.venv`/`.venv-linux` の行 = 0 → 総監督 seq285143 の DELETE (16:07・15288 行) と対応する
- 総行数 ≒ 19,4xx → .venv 帯が残る状態 (16:07 より前の観測) と読む / < 4,000 → 母集合の一部のみ表に在ると読む

★③ `updated_at` 最新 1 行の commit_hash (v3 の一次 state・L322/L331 `order=updated_at.desc&limit=1`)★
期待列 commit_hash / updated_at・期待行数 1
- 620df477e の短縮と一致 → v3 の一次 state が入つて居ると読む (`get_commit_hash` は `rev-parse --short HEAD`)
- 09-07 16:0x より古い → v3 merge 後の走行が表に届いて居らぬと読む / 0 行 → fallback 条件① に当たり `STALE_FALLBACK_FULL_SCAN` へ落ちる

## §6 境界と開示
DB 読 0・書 0・走行 0 (--dry-run も無し)・fetch/rebase/merge 0・本番 code 書込 0・push 0。局所 ref のみ讀んだ (fetch 0 ゆゑ遠隔の先端が此れより先に在るかは 測つて居らぬ)。
§3 の N は ★当席が pattern 表を写した別 script★ の値で、v3 本体を走らせての突合は 測つて居らぬ。§2 の M の skipped は 測れぬ。
