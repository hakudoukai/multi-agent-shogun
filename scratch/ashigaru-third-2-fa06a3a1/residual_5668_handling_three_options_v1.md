# 残 5,668 行の扱ひ 三案 (讀取のみ・DDL は案文・適用 0)

- as_of: 2026-09-07 16:40 JST / 席: ashigaru-third-2 / 令: order51 / 材料: order50 紙 306816953dc056f5 §3/§4・v3 main blob 0754d9284・migrations 3 本 (いづれも讀取のみ)
- ★当席の推しは書かず、判定材料のみ置く★。案は 3・和 3。打つ手を選ぶは総監督殿。

## §1 讀取で測れた前提 (行番号は v3 blob 0754d9284)

- 表: supabase/migrations/20260403020939_create_source_code_cache.sql:4 `file_path TEXT PRIMARY KEY`
  ∴ 同 path は 1 行のみ・枝/PC を区別する列は無い。索引 = idx_source_code_cache_updated(updated_at DESC)。
- 書く: L121/L209 `on_conflict=file_path`・L205 `resolution=merge-duplicates`・row は L604-609。
- 消す: L476-490 `delete_stale` = `file_path=in.(…)`。其の母集合は 2 経路 ——
  (a) L667 `stale_paths_from_git` = 前回 sync commit 以降の D/R のみ (現行の常道)
  (b) L659-661 `get_cached_paths` + `compute_stale_paths` = ★表に在り作業樹に無い INCLUDE path を悉く★
  (b) が走るのは `--full-stale-scan` (L524) 明示時、または prev_commit を引けぬ時 (L650-656)。
- 讀む側: RPC public.get_source_code_manifest() (20260516103359:2 `RETURNS TABLE(file_path, …)`)、CI .github/workflows/sync-source-cache.yml:170 (POST) / :186 (DELETE `file_path=eq.`)、MCP 経由の Claude.ai。
- L249-252 の註: `--changed-only` の縮小母集合を (b) へ渡すと現存 file が誤つて消される (2,113 件の例が記されて居る)。

## §2 三案の表

| 観点 | ㋐ 残す (現状) | ㋑ 鍵に枝/PC 列を加へ v4 | ㋒ DELETE 条件を拡げ他枝 path を消す |
|---|---|---|---|
| 何を変へる | 変へぬ | 表の主鍵と列・v3 の書込 row | 走らせ方 (既存経路)・恒常化する時のみ CI |
| DDL 案文 | 無し | 下記 D1・D2 (戻しは D3) | 無し |
| code 差分行 | 無し | L121 (鍵) / L209 (on_conflict) / L604-609 (row) / L508 (SQL 生成) / L490 (DELETE 条件) | ★新規 0★ —— L524 `--full-stale-scan` を付け main の作業樹で走らす。恒常化する場合のみ yml:170 近傍へ引数追加 |
| 危険 | 他枝 path が積み続ける。manifest/MCP に main に無い path が混じる | file_path の一意が失せるゆゑ RPC・MCP・CI:186 の `file_path=eq.` が複数行を指す。DEFAULT で埋めた既存 5,668 行は皆同じ枝値になり、真の枝は後から復元できぬ | 母集合が (b) ゆゑ ★main の作業樹に無い INCLUDE path を悉く消す★。他枝にのみ在る 1,442 が対象に入る。L249-252 の縮小母集合と併せると更に広がる |
| 戻し方 | —— | D3。但し重複行が入つた後は一意へ戻せぬゆゑ、重複を先に消さねば D3 は拒まれる | 消した行は表からは戻せぬ。各枝を checkout して再走、または 2026-09-07 の export csv 15,288 行から復元 |

- D1 (㋑ 列追加・案文): `ALTER TABLE public.source_code_cache ADD COLUMN branch text NOT NULL DEFAULT 'main', ADD COLUMN pc text NOT NULL DEFAULT 'unknown';`
- D2 (㋑ 主鍵付替・案文): `ALTER TABLE public.source_code_cache DROP CONSTRAINT source_code_cache_pkey; ALTER TABLE public.source_code_cache ADD PRIMARY KEY (file_path, branch, pc);`
- D3 (㋑ 戻し・案文): `ALTER TABLE public.source_code_cache DROP CONSTRAINT source_code_cache_pkey; ALTER TABLE public.source_code_cache ADD PRIMARY KEY (file_path); ALTER TABLE public.source_code_cache DROP COLUMN branch, DROP COLUMN pc;`
- ★D1/D2/D3 は案文であり、当席は 1 本も打つて居らぬ (適用 0・DB 書込 0・讀取 0)★。

## §3 各案で消える行・残る行の見積 (order50 の数を用ゐる)

| 案 | 消える行 | 残る行 |
|---|---|---|
| ㋐ | 0 | 5,668 (以後 他枝の走行ごとに増える。増分は 測つて居らぬ) |
| ㋑ | 0 (分けるだけで消さぬ) | 5,668 + 以後の枝別行 (増分は 測つて居らぬ) |
| ㋒ | 上限 1,483 (= 5,668 − main N 4,185)。内訳の候補は ㋑ 他枝のみ 1,442・㋺ 履歴 D 357 | 4,185 に近い形 (厳密な数は DB を讀まねば 測定不能) |

- ★1,442 + 357 = 1,799 は上限 1,483 を超える★ ∴ ㋑ と ㋺ は重なつて居る。重なりの数は 測つて居らぬ。
- 226 局所 ref 合併 5,627 対 實測 5,668 の ★差 41★ は未だ詰めて居らぬゆゑ、上の見積も 41 の幅を持つ。

## §4 SELECT 2 本 (order50 §4) の結果 X → 案 Y の判定表

- S1 = 先頭 2 階層別 count / S2 = commit_hash 別 count + max(updated_at)。

| 結果 X | 読み | 案 Y の材料 |
|---|---|---|
| S1 の超過が frontend/.claude/docs に集中 | 他枝 path (㋑) が主部 | ㋒ が 1 走で当たる形。㋑ は以後の混在を分ける形 |
| S1 の超過が広く薄い | 履歴 D (㋺) が混じる | ㋒ の対象に入る。㋐ では減らぬ |
| S2 の commit_hash が 1〜2 種に集中 | 単一走行が書いた形 | ㋐ でも積み増しは起きぬ読み |
| S2 が多種 + max(updated_at) が 16:07 より後 | 別経路が今も書いて居る | ㋐/㋒ とも再び積む形ゆゑ、書き手 (CI・second PC) の特定が先 |
| S2 に commit_hash NULL の塊 | 静的 batch SQL 由来の疑 | ㋒ で行は減るが入口は残る |

## §5 境界

- DB 書込 0・讀取 0・走行 0・fetch 0・DDL 適用 0・本番 code 書込 0。前紙 3 本は不触。数は order50 の 226 局所 ref 合併に拠り、遠隔にのみ在る枝・削られた枝は 測つて居らぬ。
- ㋒ の「消える行」は INCLUDE に当たる分のみで當日の作業樹次第で動く。當席は 1 走も走らせて居らぬ。
