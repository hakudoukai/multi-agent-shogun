# ㋑ v4(枝・PC 列) D1-D3 の適用順・戻し・途中失敗・読み手影響 (讀取のみ・適用0)

前紙: residual_5668_handling_three_options_v1.md ae4210d3fc811b36 59行 (§2 ㋑・D1-D3 の出所)
床(不触・再測一致): option_c_full_stale_scan_predicate_v1.md 34f11cfac4d55b42 58行 / fnmatch_vs_regex_divergence_select_drafts_v1.md e9b562509f5f4928 57行 / after_delete_5668_gap_1483_readonly_v1.md 306816953dc056f5 59行
as_of 2026-09-07 18:05 / 出所= v3 blob 0754d9284db2d50c5f3941ad1d3cf786d5279de9(709行) ・表定義 supabase/migrations/20260403020939_create_source_code_cache.sql:3-11 ・RPC supabase/migrations/20260516103359*.sql:1-7 ・CI .github/workflows/sync-source-cache.yml
本紙は DDL を1文も適用して居らぬ。DB へ SELECT も打つて居らぬ。v3 script も走らせて居らぬ。以下は blob と migration の讀取から起こした案文と機序である。推しは書かぬ。

## §1 適用順と各段の戻し案文 (案文のみ・適用0)

| 段 | 案文 | 戻し案文 | 戻せる条件 |
|---|---|---|---|
| D1 | `ALTER TABLE public.source_code_cache ADD COLUMN branch text NOT NULL DEFAULT 'main', ADD COLUMN pc text NOT NULL DEFAULT 'unknown';` | `ALTER TABLE public.source_code_cache DROP COLUMN branch, DROP COLUMN pc;` | 何時でも(入つた値は失せる) |
| D2 | `ALTER TABLE public.source_code_cache DROP CONSTRAINT source_code_cache_pkey;` と `ALTER TABLE public.source_code_cache ADD PRIMARY KEY (file_path, branch, pc);` の2文 | 同じく2文: `DROP CONSTRAINT source_code_cache_pkey;` → `ADD PRIMARY KEY (file_path);` | file_path が重複せぬ間のみ |
| D3 | (戻し一括) D2 の戻し → D1 の戻し の順 | — | 同上 |

- D2 は★2文★である。別々に打てば其の間 ★PK の無い窓★ が開く(§2 c)。1 transaction に包む形も在る(打つ/打たぬは総監督殿)。v3 blob 全文に `BEGIN`/`COMMIT;`/`ROLLBACK` は0件ゆゑ、包む器は script の側には無い。
- D3 は order51 §2 に既記の通り、別枝/別PC の行が1行でも入つた後は `ADD PRIMARY KEY (file_path)` が重複で拒まれる。∴ 戻せる窓は「D2 の後・別枝の行が入る前」だけである。

## §2 途中失敗時の table 状態と読み手

- a) ★D1 のみ(D2 未着手)★: 列が2本増え、既存 5,668 行は悉く ('main','unknown') を持つ。PK は file_path のまま。∴ §3 の8箇所は1つも振舞ひが変はらぬ。戻しは D1 の戻しのみで足る。
- b) ★D1+D2 完了★: 一意が (file_path,branch,pc) へ移る。§3 R1・R5 が 42P10(ON CONFLICT に合ふ一意制約が無い)で止まる。R2・R6・R7 は行が複数に成る側へ倒れる。
- c) ★D2 の1文目のみ(DROP は通り ADD PRIMARY KEY が失敗)★: ★PK の無い表★が残る。ON CONFLICT の指す先が失せ、v3 の upsert も CI の POST も衝突先を持たぬ。行の重複を防ぐ物が此の窓には何も無い。
- d) いづれの段でも既存行の content/commit_hash/updated_at は書き換はらぬ(DDL は列と制約にのみ触る)。5,668 行の数自体も D1-D3 では増減せぬ。

## §3 一意が失せた後に複数行を指す/振舞ひが変はる読み手 (数へた1= 呼出箇所1つ・計8)

| # | 出所と行 | 何を指すか | D1+D2 後 |
|---|---|---|---|
| R1 | v3 L121 `UPSERT_CONFLICT_KEY="file_path"` → L209 `params={"on_conflict": ...}` | upsert の衝突先 | 42P10。L219 raise → L275 で非一過性 → L281「BATCH FAILED」→ L284 1件づつ隔離 → L294 で全件が「POISON FILE isolated」と印字 |
| R2 | v3 L490 `params={"file_path": f"in.({paths_csv})"}` | stale の削除先 | 1 path の指定で 枝数×PC数 行を消す |
| R3 | v3 L461 select file_path(offset/limit=1000) → L469 `all_paths.add` | 残 path の一覧 | 同 path が複数行で返る。L469 の set が畳むゆゑ返り値の数は path 数のまま。頁繰は★行数★で回る ∴ 要求回数が増え、「残 5,668」は行数であつて path 数ではなくなる |
| R4 | v3 L331 `order=updated_at.desc, limit=1` | 前回 sync commit | 全枝・全PC の中の最新1行。別枝の commit を掴めば L341 `commit_exists` が偽 → L657 の (b) 全走査へ倒れる |
| R5 | v3 L510 `ON CONFLICT (file_path) DO UPDATE` | dry-run 印字用 SQL | 其の案文が 42P10。※本紙は `--dry-run` も打たぬ |
| R6 | RPC 20260516103359:4 `SELECT file_path, md5(content), file_size FROM public.source_code_cache` | MCP 経由の讀み手が見る一覧 | 同 path が 枝数×PC数 行で返る。返り列(:2)に branch/pc は無い ∴ 讀み手は何れの行か分けられぬ |
| R7 | CI :186 `DELETE ...?file_path=eq.{fp}` | CI の削除先 | R2 と同じく 枝数×PC数 行を消す |
| R8 | CI :169-174 POST(:60 `Prefer: resolution=merge-duplicates`・on_conflict の指定無し) | CI の書き先 | 衝突先を明示せぬ作りゆゑ PK に依る。D1 の既定が入り書き先は1行に定まる。返る行は変はらぬ |

- 内訳: 42P10 で止まる=2(R1・R5) / 枝を跨いで消す=2(R2・R7) / 複数行が返る=2(R3・R6) / 別枝の値を掴む=1(R4) / 変はらぬ=1(R8)。
- ★件数の但書★: 8 は「blob と CI と RPC の3出所を讀んで見付けた呼出箇所」の数であり、MCP 側の讀み手(Claude.ai)が何本の呼出を持つかは当席から測れぬ ∴ 8 は★下限★である。

## §4 既存 5,668 行の新列の埋め方 三案 (打つは総監督殿・適用0)

| 案 | 案文/やり方 | 危険 |
|---|---|---|
| F1 既定値で埋める | D1 の `NOT NULL DEFAULT` がそのまま既存行に入る(追加文以外は要らぬ) | 5,668 行が悉く ('main','unknown') に潰れる。元が何れの枝・何れの PC の行であつたかは表に残つて居らぬ ∴ 後から分けられぬ。且つ D2 の後も file_path の重複は0のまま ∴ order50 の差 1,483 は此の案では分解されぬ |
| F2 NULL 許容で足し後から埋める | `ADD COLUMN branch text, ADD COLUMN pc text;` → `UPDATE ... SET branch=..., pc=...` → `ALTER COLUMN ... SET NOT NULL` → D2 | PK 列は NOT NULL を要する ∴ 埋め切る前に D2 を打てば拒まれる。且つ埋める間に走る同期が NULL の行を作り、其の後の SET NOT NULL が止まる |
| F3 commit_hash から逆算 | 外で git から commit→枝 の対応表を作り持ち込み `UPDATE ... SET branch = <対応>` | 表に枝の列が無く commit_hash は40字の値のみ ∴ DB 内では引けぬ。同 commit が複数枝に在る/既に消えた commit/CI 書きと手走りの commit が混じる場合は一意に定まらぬ。★pc は commit_hash から引く術が無い★(記録が表にも blob にも無い) ∴ F3 は branch にしか効かず pc は F1 か F2 に依る |

## §5 境界

- DDL 適用0・DB 書込0・DB 讀取0・v3 走行0・`--dry-run` 0・fetch/rebase 0・本番 code 書込0・D 樹不触。§1/§4 の SQL は悉く★案文★であり、打つ/打たぬは総監督殿の裁。
- §2 の「42P10」は PostgreSQL が ON CONFLICT に合ふ一意制約を持たぬ時に返す符号として書いた物であり、当席が実際に打つて得た返りではない。
- §3 R3 の「頁繰が行数で回る」は L458-472 の作り(limit=1000・L470-471 の break が `len(data)<limit`)から起こした機序であり、實測ではない。
- 前紙4本は1字も書き換へて居らぬ(冒頭の sha16 は本作業の着手時に再測して一致を見た値)。
