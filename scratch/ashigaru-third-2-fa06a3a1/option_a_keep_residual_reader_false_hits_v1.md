# ㋐「残す」―― 残 5,668 行を読み手が file_path だけで当てる形 (讀取のみ・走行0)

前紙・床(悉く不触・着手時に再測し一致): option_b_v4_ddl_apply_rollback_impact_v1.md f675db01059148c3 55行(§3 の読み手8箇所=本紙の起点) / residual_5668_handling_three_options_v1.md ae4210d3fc811b36 59行(§2 ㋐) / option_c_full_stale_scan_predicate_v1.md 34f11cfac4d55b42 58行 / fnmatch_vs_regex_divergence_select_drafts_v1.md e9b562509f5f4928 57行 / after_delete_5668_gap_1483_readonly_v1.md 306816953dc056f5 59行(区分 ㋑㋺㋩ の出所)
as_of 2026-09-07 18:20 / 出所= v3 blob 0754d9284db2d50c5f3941ad1d3cf786d5279de9(709行) ・RPC supabase/migrations/20260516103359*.sql ・CI .github/workflows/sync-source-cache.yml ・表定義 20260403020939:3-11
区分: ㋑=他枝にのみ在る path 1,442 / ㋺=履歴で削除された path(D) 357 / ㋩=CI 外書き(CI 3,301 ⊂ v3 4,185 ゆゑ現に無い) / 差41(226ref 合併 5,627 対 實測 5,668)。㋐ は DDL も DELETE も打たぬ形である。本紙は DB へ1本も打たず v3 も走らせて居らぬ。推しは書かぬ。

## §1 読み手が残行を当てる条件 (行番号・計9)

| # | 行 | 当てる条件 | 枝で分ける手掛かり |
|---|---|---|---|
| R1 | v3 L121 `UPSERT_CONFLICT_KEY="file_path"` → L209 `on_conflict` | file_path のみ | 無し(列が無い) |
| R2 | v3 L490 `params={"file_path": f"in.({paths_csv})"}` | file_path のみ | 無し |
| R3 | v3 L461 `select=file_path`(offset/limit=1000) → L469 set 追加 | 条件無し(全行) | 無し |
| R4 | v3 L331 `order=updated_at.desc, limit=1` → 返り L338 `commit_hash` | 条件無し(全行の中の最新1行) | updated_at の新旧のみ |
| R5 | v3 L510 `ON CONFLICT (file_path)`(dry-run 印字) | file_path のみ | 無し |
| R6 | RPC 20260516103359:4 `SELECT file_path, md5(content), file_size FROM public.source_code_cache` (WHERE 無し) | 条件無し(全行) | 返り列(:2)の content_md5 のみ・枝は無し |
| R7 | CI :186 `DELETE ...?file_path=eq.{fp}` | file_path のみ | 無し |
| R8 | CI :169-174 POST(:60 `Prefer: resolution=merge-duplicates`) | file_path(PK)のみ | 無し |
| R9 | v3 L434 `get_cache_row_count`(`Prefer: count=exact`・row 0件) | 条件無し(全行の数) | 無し |

- ★9 箇所の悉くが枝を問はぬ★。branch/pc の列が表に無い(20260403020939:3-11)ゆゑ、`+branch` で当てる読み手は ★0 箇所★ である。`+sha/md5` を持つのは R6 の返り列のみで、比べるのは讀み手の側である。

## §2 区分 × 読み手 (当/否/不能)

| # | ㋑ 他枝 1,442 | ㋺ 履歴D 357 | ㋩ CI外書き |
|---|---|---|---|
| R1 | 不能(其の path が現作業樹に現れた走行でのみ当たる) | 否(現作業樹に無い・復活すれば当たる) | 不能(母集合が測れぬ) |
| R2 | 当(L656 の (b) へ倒れた走行のみ・(a) では否) | 当(同上) | 不能 |
| R3 | 当 | 当 | 当 |
| R4 | 不能(残行の updated_at が最新の時のみ当たる) | 不能(同上・古い側ゆゑ当たり難い) | 不能 |
| R5 | 否(現作業樹の file のみ印字) | 否 | 否 |
| R6 | 当 | 当 | 当 |
| R7 | 不能(CI の to_delete に入る時のみ) | 否(CI の走査対象外) | 不能 |
| R8 | 不能(其の path が CI 対象に成つた時のみ) | 否 | 不能 |
| R9 | 当 | 当 | 当 |

- 数へた1= 読み手1箇所×区分1つ の枡。当=9・否=8・不能=10(計27)。

## §3 当たつた時に起きる事 と根拠行

| 事 | 起きる読み手 | 根拠行 |
|---|---|---|
| 上書き | R1・R8 | L209 の衝突先が file_path ゆゑ行は増えず content/commit_hash/updated_at が替はる(表定義:4 PRIMARY KEY) |
| 消失 | R2・R7 | L490 の `in.(...)`・CI:186 の `eq.` が枝を問はず消す。L667-668 で走り、失敗は L676-679 で開示される |
| 二重 | R6 | 同じ論点の新旧が並んで返る。RPC に WHERE が無く返り列に枝が無い ∴ 讀み手(MCP 経由)は何れが現行か分けられぬ |
| 無害 | R3・R9 | 数と集合が増えるのみ。但し R3 は L661 へ流れて R2 の母集合に成り、R9 は「残 5,668」の測りそのものである |
| 引金 | R4 | ★残行が (b) を呼ぶ★: L645 が DB を先に讀む ∴ 残行の updated_at が最新なら別枝の commit を掴む → L652 `commit_exists` 偽 → L655 で None → L656 が真 → L660-661 → L667-668 が走る。commit_exists が真の側でも L664 が別枝との差分 D/R を stale に積む ∴ 二筋とも残行が消える側へ回り得る |

- ★令の文言は「三値」だが列挙は 上書き/二重/消失/無害 の4語である。本紙は4語で置き、R4 は其の4語の何れでもない(他を呼ぶ)ゆゑ「引金」を別に立てた。黙つて丸めては居らぬ。

## §4 「残す」で要る注記 (事実のみ・推し無し)

- ㋐ は「打たぬ」だけでは保てぬ。L656 `if full_stale_scan or not prev_commit:` が真に成る道が3つ在る: ①`--full-stale-scan` を渡す(L524) ②L645 の DB 讀みと L650 の state file がともに空 ③L652 で prev_commit が此の樹で解決できぬ。②の state file は L298-299 `repo_root/tmp/<LAST_SYNC_COMMIT_FILE>`(追跡外)ゆゑ tmp の消去で失せる。③へ倒れる引金は §3 R4 の通り★残行自身が持つ★ ∴ ㋐ と ㋒ は排他ではない。
- (b) へ倒れても悉くが消える訳ではない。L661 `compute_stale_paths` は fnmatch であり、order53 §2 の通り A型(`<dir>/**/*.<ext>`)の直下 file は消えぬ側・B/C型の深い行は消える側へ倒れる。R6 で讀み手が現行と古い版を分ける手掛かりは content_md5(RPC:2)と表の commit_hash・updated_at のみである。

## §5 境界

- DB 書込0・DB 讀取0・DDL 0・v3 走行0・`--dry-run` 0・fetch/rebase 0・本番 code 書込0・D 樹不触。
- §2 の「当/否/不能」は blob と CI と RPC の讀取から起こした機序であり、實際に走らせて得た結果ではない。1,442・357・3,301・4,185・5,668 は前紙(306816953dc056f5)の数をそのまま引いた物で、本紙で測り直しては居らぬ。
- 読み手は9箇所だが MCP 側(Claude.ai)が何本の呼出を持つかは当席から測れぬ ∴ 9 は★下限★である(order54 §3 の但書と同じ)。前紙5本は1字も書き換へて居らぬ。
