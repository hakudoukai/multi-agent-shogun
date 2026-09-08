# sync_source_cache v3 の DB 負荷 讀取見積 (order47 產・★讀取のみ・実行 0・DB 接続 0★)

as_of 2026-09-07 16:2x JST / 席=ashigaru-third-2 / 令=karo-third order47 (総監督 hs_9e6cb6a5 08:48)。
見た物 = main の blob `0754d9284db2d50c5f3941ad1d3cf786d5279de9` (`scripts/sync_source_cache.py`・709 行) と
比較の為の v2 blob `76a1e2a91b422a1b71583f24a8573c67d88a78a8`。何れも `git show` で讀んだのみ。
三択語 = 測つた / 測つて居らぬ / 測れぬ。1 = 呼出 1 本・file 1 本・statement 1 本。
★本紙の数は「静かに讀んで数へた見積」であり、走らせて測つた物ではない★。

## §1 N の実測 (追跡簿 × INCLUDE × EXCLUDE を当席が写して数へた)
`git ls-files -z` の追跡簿 = **13,956 file**。v3 の `collect_files` と同じ順で篩に掛けると:
作業樹に無し 0 / `EXCLUDE_DIRS` で落ち **0** / `INCLUDE_PATTERNS` に当たらず 9,842 / `EXCLUDE_PATTERNS` で落ち 1。
∴ **N = 4,113 file**(同期対象)。`BATCH_SIZE = 50` ゆゑ **batch = ceil(N/50) = 83 本**。
本文の総 byte = **179,684,795**(作業樹 `st_size` の合計・平均 43,687 byte・1MB 超が 36 file)。
∴ 1 batch あたりの本文 ≒ **2.16 MB**(平均。中身の偏りは大きい)。★HTTP 本文はこれに JSON の被せが乗る★。
註: 此の N は ★今の main の追跡簿★ で数へた物。v2 期の N は別 (下記 §4)。

## §2 v3 の DB 呼出 (関数別・1 走行あたり)
| 関数 | 文の種類 (PostgREST 経由) | 単位 | 回数の式 f(N,R) | 今の値 |
|---|---|---|---|---|
| `upsert_batch` (← `upsert_with_isolation` ← `main`) | `INSERT … ON CONFLICT (file_path) DO UPDATE` (`on_conflict=file_path`・`resolution=merge-duplicates`) | 50 行/本 | `ceil(N/50)` | **83** |
| 同 (batch 失敗時の隔離) | 同上・1 行/本 | 1 行 | 失敗 batch 1 本につき `+50` | 0 (失敗が無ければ) |
| 同 (`upsert_batch_with_retry`) | 同上の再送 | ― | transient のみ 最大 `×3` (1s→2s) | ― |
| `get_last_sync_commit_from_db` | `SELECT commit_hash … ORDER BY updated_at DESC LIMIT 1` | 1 行 | **1**(定数) | 1 |
| `stale_paths_from_git` | ★DB を触らぬ★ (`git diff --name-status --diff-filter=DR`) | ― | **0** | 0 |
| `get_cached_paths` (★fallback のみ★) | `SELECT file_path … LIMIT 1000 OFFSET k` | 1,000 行/本 | `ceil(R/1000)` (R%1000=0 なら +1) | 走らぬ限り 0 |
| `delete_stale` | `DELETE … WHERE file_path IN (…)` | 全 stale を 1 本 | `0 または 1` | ― |
| `get_cache_row_count` | `SELECT file_path` + `Prefer: count=exact`・`Range: 0-0` | 0 行 + 総数 | **1**(定数) | 1 |
∴ ★定常の 1 走行★ = `INSERT` **83** + `SELECT` **2** + `DELETE` **0〜1** = **85〜86 往復**。
★fallback (前回 commit が無い/解決できぬ/`--full-stale-scan`)★ = 上に `ceil(R/1000)` 本の頁繰りが加はる。
fallback へ落ちる条件は 3 つ = ⑴ DB の最新行が無い ⑵ state file も無い ⑶ 前回 commit が此の樹で解決できぬ(shallow clone・別枝)。何れも stderr へ `STALE_FALLBACK_FULL_SCAN` を刷る。

## §3 総監督材料との突合 (三択語)
材料 = 07:55 crash recovery 直後の `pg_stat_statements`: **INSERT 106 回 19s** / **LIMIT/OFFSET 12 回 1.5s**。
| 材料 | v3 の何処か | 三択 | 註 |
|---|---|---|---|
| INSERT 106 回 | `upsert_batch` の POST ―― ★v3 で `INSERT` を出す口は此の 1 本のみ★(dry-run の `generate_upsert_sql` は print であり DB へ行かぬ) | **対応する** | 但し 106 と §2 の 83 が同じ走行の物かは ★測つて居らぬ★。106 は隔離の 1 行 POST や複数走行を含み得る |
| 19s / 106 ≒ 0.179s/本 | 1 本 = 50 行・平均 2.16MB の本文 | **対応する** | 時間の内訳(網・書込・索引)は ★測れぬ★(当席に DB 讀取が無い) |
| LIMIT/OFFSET 12 回 | v2 の `get_cached_paths`(1,000 行頁繰り)・v3 では ★fallback 時のみ★。定常の v3 で `LIMIT` を伴ふのは `get_last_sync_commit_from_db`(LIMIT 1) と `get_cache_row_count`(Range 0-0) の **2 本** | **対応する箇所は在るが数は測つて居らぬ** | 12 回 ≒ 12,000 行分の頁繰りに見えるが、其の走行が v2 か v3 か・OFFSET の有無の内訳は ★測つて居らぬ★ |
| 1.5s / 12 ≒ 0.125s/本 | 頁 1 枚 = 1,000 行の `file_path` のみ | **対応する** | ― |
∴ 材料の時間を其の儘当てると、v3 の定常 1 走行の DB 時間 ≒ `83×0.179 + 2×0.125` ≒ **15.1s**。
★之は「材料の 1 本あたり時間が同じなら」の見積であり、測つた値ではない★。

## §4 v2 → v3 で減つた往復・増えた往復
| 事 | v2 | v3 (定常) | 差 |
|---|---|---|---|
| stale の母集合 | 全表を `LIMIT 1000 OFFSET k` で頁繰り = `ceil(R/1000)` 本 | `git diff` = **0 本** | ★−`ceil(R/1000)`★ |
| 最終カウント | `get_cached_paths()` を ★2 度目★ = 更に `ceil(R/1000)` 本 | `count=exact` **1 本** | ★−(`ceil(R/1000)`−1)★ |
| 前回 commit の讀み | 無し | `LIMIT 1` **1 本** | +1 |
| upsert | `ceil(N_v2/50)` 本 | `ceil(4113/50)` = 83 本 | 下段 |
| DELETE | 0〜1 | 0〜1 | ±0 |
R = cache の行数。R ≒ 15,000 と置けば読取往復は **32 本 → 2 本**(★−30★)。R は当席に ★測れぬ★(DB 讀取 0)。
upsert 側: v2 の母集合は ★作業樹 glob★ ゆゑ `backend/.venv%` 等 15,288 行が混じつた(材料の数)。
N_v2 ≒ 4,113 + 15,288 = 19,401 と置けば `ceil/50` は **389 本 → 83 本**(★−306★)。
★N_v2 は当席が数へた物ではない★(15,288 は総監督 SELECT の実測を借りた)。∴ 此の行は ★見積★ と読まれたい。
増えた物 = `SELECT LIMIT 1` 1 本のみ。減つた物 = 頁繰り 2 系統と、追跡外 file の upsert。

## §5 総監督殿への SELECT 案 (★3 本・当席は 1 本も打つて居らぬ★)
1. `pg_stat_statements` を `query ILIKE '%source_code_cache%'` で絞り、`calls`・`total_exec_time`・`mean_exec_time` を文別に見る ―― 106/19s と 12/1.5s が今どう動いたかを同じ物差で再度採る為。
2. `source_code_cache` の総行数と、`file_path` の先頭 1 階層別の内訳 ―― `backend/.venv%`・`.venv-linux%` が今も残つて居るか(§4 の N_v2 の裏)。
3. `updated_at` の最新 1 行の `commit_hash` ―― v3 の一次 state が入つて居るか(入つて居らねば毎走 fallback の頁繰りに落ちる)。
★何れも讀取のみ・書込を含まぬ★。文面は総監督殿の器で組まれたい(当席は接続を持たぬ)。

## §6 境界と開示
DB へ 0 本・実行 0・本番 code 不触・push 0・commit 0・merge 0・fetch 0。v3 の本体は `git show` で讀んだのみで、輸入(import)も走らせて居らぬ。
§1 の篩は ★当席が v3 の pattern 表を写して書いた別の script★ で数へた(本番 code を輸入せぬ為)。∴ v3 本体との一致は「同じ pattern・同じ順」を目で合はせた迄で、★実行での突合は測つて居らぬ★。
中間 file 1 本(`/home/hakudoukai/a2/.tmp_lsfiles_z`・己が作つた物)は数へ終へて消した。他者の物は 1 本も触れて居らぬ。
`.venv` 等の帯は §1 で ★0 件★ を数へた ―― 今の追跡簿には仮想環境の file が 1 本も無い(帯が働いたのではなく、元から追跡されて居らぬ)。
