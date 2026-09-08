# v3 本体 と CI #2 の目の差・および on_conflict の材 (讀取のみ・DB 0・fetch 0・走行 0)

as_of 2026-09-08 04:23 JST / 席 ashigaru-third-2 / 令 order71 (家老の順の裁=弾B が先) / 裁 283660 の材
★床 (着手時 再測 差0)★: `9268704f85a4f05a` plan123_ruling_and_window_correction_v1.md 64行 / 前紙 `f7e066394ceecd6e` lineage_end_runlog_reconciliation_v1.md 69行 ―― ★何れも不触★
底本: v3 = blob `0754d9284db2d50c5f3941ad1d3cf786d5279de9` (作業樹 scripts/sync_source_cache.py と ★逐一同値★) / CI #2 = .github/workflows/sync-source-cache.yml / DDL = supabase/migrations/20260403020939_create_source_code_cache.sql
★四条②★ 数には何の数かを添へる。★四条③★ 意味の違ふ数を足し引きせぬ (pattern 本数 と path 本数 と 列数 は別物ゆゑ和を作らぬ)。★四条④★ 見込みは見込みと記す。

## §1 INCLUDE pattern の目の差 (単位=pattern 本数)
| 目 | pattern 本数 (書かれた儘) | pattern 本数 (一意) |
|---|---|---|
| v3 本体 | ★35★ | ★31★ (重複 4 本=`docs/audits/**/*.md` `docs/audits/**/*.txt` `supabase/functions/**/*.ts` `supabase/migrations/*.sql` が各 2 度) |
| CI #2 | ★28★ | ★28★ (重複 0) |
- ★v3 一意 31 − CI 28 = 3 本★ (逐語): `.cache/audit_redo/**/*.md` / `.cache/audit_redo/**/*.txt` / `docs/audits/**/*.log`
- ★CI 28 − v3 一意 31 = 0 本★ ∴ ★CI の目は v3 の目の真部分集合★ (CI ⊂ v3)。
- 逐語の在処: v3 = blob L88 の直前 INCLUDE_PATTERNS ブロック / CI = yml L63〜L92。★3 本は CI の側に一つも書かれて居らぬ★ (grep で 0 件)。

## §2 当席の旧 28 本は誤りではなく ★CI の目★ であつた (単位=pattern 本数)
- order68/69/70 で当席が使つた list を ★本 session の transcript から復元★ (讀取のみ・jsonl 359,893,500 B を stream)。復元された list は 5 種 (35/28/31/27/22 本) で、其の内 ★28 本の list★ が当席の旧い目。
- ★CI の 28 本と 記号差 0・★順序まで同一★★ ∴ 当席の旧 28 本は ★CI #2 の目を写した物★ であり、「3 本が欠けて居た」のではなく ★目が 2 つ在つた★。
- ∴ order70 §3 の「28 pattern 版 5,172 / 31 pattern 版 5,190」は ★CI の目 と v3 の目★ の 2 値であり、何れも誤りではない。増分 0 は両方の目で同じ。

## §3 ★EXCLUDE も違ふ★ ―― 当席が order69 §3 で掛けたは ★CI の目★ であつた (要 開示・単位=pattern 本数)
| 目 | EXCLUDE pattern 本数 | 逐語 |
|---|---|---|
| v3 本体 (blob L88〜) | ★5★ | `**/__pycache__/**` `**/node_modules/**` `**/dist/**` `**/.git/**` `frontend/src/vite-env.d.ts` |
| CI #2 (yml L93〜97) | ★7★ | 上の内 `**/.git/**` を欠き ★`**/*.test.*` `**/*.spec.*` `**/test_*` の 3 本を持つ★ |
- ★v3 は `**/*.test.*` を除かぬ★。order69 §3 で「4 本が EXCLUDE で 2 本に落ちる」と書いた時、当席が掛けたは ★CI の目★ であり v3 の目ではない ―― ★目の名を添へずに書いた★ (四条② 違反)。★前紙は書き換へず 此処に併記する★。
- ★而して結論は反転せず 却つて絞れる★: 若し書き手が v3 なら 4 本が入り DB は 18:58:47 に ★4 行★ を持つ筈だが、総監督殿の SELECT は ★2 行★ (order70 §1)。∴ ★18:58:47 の 2 行を書いた器の目は CI #2 の目と一致し v3 の目とは一致せぬ★。
- 三値: 「2 行の書き手が CI #2 の側である」= ★code と行数から読める★ (実測は DB に書き手の列が無く ★測定不能★・order70 §4)。★目の差は書き手の指紋になり得る★ ―― 之は order72 (先頭 `/` の書き手) にも效く器である。
- EXCLUDE_DIRS も別 (単位=dir 名の本数): v3 ★8★ (`.venv-linux` `venv` `.codex_audit` を持つ) / CI ★6★ (`.pytest_cache` を持つ)。

## §4 on_conflict の逐語 (裁 283660 の材)
| 器 | 逐語 | on_conflict |
|---|---|---|
| v3 本体 | L121 `UPSERT_CONFLICT_KEY = "file_path"` / L202 `url = f"{SUPABASE_URL}/rest/v1/source_code_cache"` / L205 `"Prefer": "return=minimal,resolution=merge-duplicates"` / ★L209 `params={"on_conflict": UPSERT_CONFLICT_KEY}`★ | ★有り★ |
| CI #2 upsert | L60 `"Prefer": "resolution=merge-duplicates"` / L169〜174 `requests.post(f"{SUPABASE_URL}/rest/v1/source_code_cache", headers=HEADERS, json=payload, timeout=30)` | ★無し★ (query も params も 0) |
| CI #2 delete | L186 `f"{SUPABASE_URL}/rest/v1/source_code_cache?file_path=eq.{fp}"` | (delete ゆゑ対象外) |
- ★而して DDL は `file_path TEXT PRIMARY KEY`★ (migration 20260403020939 の 3〜4 行目・逐語)。∴ ★此の表に限り★ 主鍵の列 と v3 が指す列は ★同一★。
- 三値: 「無指定の merge-duplicates が主鍵で解決する」= ★当席には測定不能★ (PostgREST の外部仕様であり code からは讀めぬ・当席は DB を打たぬ)。★裁に要るは此の一点のみ★。
- 併記 (危さの所在): CI 側は ★列の名を書いて居らぬ★ ゆゑ、主鍵が file_path から動いた日に ★CI だけが黙つて別の列で解決する★。v3 は名を書いて居る。∴ 「今 同じか」と「主鍵が動いた後も同じか」は別の問ひである。
- 表の列の数 (単位=列): DDL 7 列 + 後の alter 2 列 (`content_sha256` `last_snapshot_id`) = ★9 列★ ―― order70 §4 が数へた 9 列と ★差 0★。★書き手 (PC・枝・器) の列は 0★。

## §5 CI の目は二段である (単位=pattern 本数・別々に数へる)
- 発火の目 (`on.push.paths`) = ★16 本★ / 収集の目 (INCLUDE) = ★28 本★。枝は `main` と `feature/**` の 2 種。
- 収集の目に在り ★発火の目に覆はれぬ★ = ★2 本★: `supabase/seed/*.sql` `supabase/policies/*.sql` ∴ 此の 2 系のみを触れた push では ★CI は走らぬ★ (走れば拾ふ)。
- CI は `HEAD~1..HEAD` の差分に在る file だけを書く (L126〜141) ―― ★全量ではない★。

## §6 三値のまとめ
| 事 | 三値 |
|---|---|
| CI ⊂ v3 (INCLUDE・差 3 本・逆 0 本) | ★現に在る★ |
| 当席の旧 28 本 = CI の 28 本 (記号差 0・順序同一) | ★現に在る★ |
| v3 が `*.test.*` を除く事 | ★現に無い★ (除くは CI のみ) |
| CI の upsert に on_conflict の指定 | ★現に無い★ |
| 無指定 merge-duplicates の解決先が主鍵である事 | ★測定不能★ (外部仕様・DB 0) |
| 18:58:47 の 2 行の書き手が CI #2 の側である事 | ★測定不能★ (行数と目の一致から読めるのみ) |

## §境界
DB 讀 0・書 0・SQL 実行 0・fetch/pull/clone/push/prune 0・共有 `.git` へ書込動詞 0・走行 0・本番 code 書込 0・secret 0・患者本文 0。
打つた git = `cat-file -p` の 1 種 (讀取)。shell の `>` `>>` `tee` = ★0★ (python の subprocess で捕へた・order70 の床違反 1 を承けて)。
transcript jsonl は ★讀取のみ★ (当 session の物・復元した list は同 dir の o71_transcript_lists.json に置いた)。
前紙 2 本は書き換へず、§3 の食ひ違ひは ★併記★ で開示した。見込みと記した ETA 30 分に対し 実所要は本紙の刻の通り。
