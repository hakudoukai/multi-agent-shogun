# ㋒ lot 引き継ぎ紙 v1 (order66 產・讀取のみ・★DB 0・走行 0・fetch 0★)

as_of 2026-09-07 19:19 JST / 席 ashigaru-third-2 / 倣つた形 = `sync_v2_lot_handover_v3.md` `1e63177573db1900` (63行・不触)
前紙 (床) = `leading_slash27_writer_path_history_v1.md` `a96fa3b10676202a` 44行 ―― 着手時に再測し ★一致★
★食ひ違ひの開示★: 令は「紙 16 本」と書かれて居るが、台帳の done 便は ★15 本★ (order50〜63・65)。
  ★order64 は 19:04 に置かれ 19:06 に取消 (`msg_20260907_190647_beae5f25`) ゆゑ紙が無い★。∴ 15 + 取消 1 = 16 と読める。本紙は 15 本で置く。
数: 1 = 紙 1 本 / 行 1 本 (= file_path 1 本)。path 値・content・commit_hash の値は一字も写して居らぬ。

## §1 紙 15 本 (sha16 は本手番で各 file から再測・★差 0 が 15/15★)
| 令 | 紙名 (`scratch/ashigaru-third-2-fa06a3a1/` 下) | sha16 | 行 | 的と主数値 |
|---|---|---|---|---|
| 50 | `after_delete_5668_gap_1483_readonly_v1.md` | `306816953dc056f5` | 59 | 残 5,668 対 N 4,185 の差 1,483 を ㋑1,442/㋺357/㋩/㋥/㋭ に分解 |
| 51 | `residual_5668_handling_three_options_v1.md` | `ae4210d3fc811b36` | 59 | 残 5,668 の扱ひ ㋐残す/㋑v4 DDL/㋒消す の 3 案 |
| 52 | `option_c_full_stale_scan_predicate_v1.md` | `34f11cfac4d55b42` | 58 | ㋒ の述語 = `full_stale_scan` の三経路・L661 fnmatch の狭め |
| 53 | `fnmatch_vs_regex_divergence_select_drafts_v1.md` | `e9b562509f5f4928` | 57 | 入口 regex 対 出口 fnmatch の食ひ違ひ・要 SELECT 3 本 |
| 54 | `option_b_v4_ddl_apply_rollback_impact_v1.md` | `f675db01059148c3` | 55 | ㋑ v4 DDL の当て方と戻し方・読み手 8 箇所 |
| 55 | `option_a_keep_residual_reader_false_hits_v1.md` | `a1728b44add87de4` | 60 | ㋐ 残す時の読み手の空振り 9 箇所・4 語 + 引金 R4 |
| 56 | `residual_5668_three_options_comparison_v1.md` | `4cd5df0a785c131f` | 33 | 3 案の比較・併記訂正 2 件を本紙側に置く |
| 57 | `gap41_5627_vs_5668_source_candidates_v1.md` | `e662da0c4d34468a` | 53 | 差 41 の出所 ―― 248 ref で 5,678 ∴ ★+10 過剰★へ置き換はる |
| 58 | `non_ascii_path10_encoding_causality_v1.md` | `725fa322a2478ae2` | 52 | 非 ASCII path 10 本・NFC 一致・URL 分離子 0 |
| 59 | `remote_only_refs_c4_measurable_v1.md` | `dadf9a7993db09e6` | 54 | C4 遠隔のみの ref 17 本 ―― fetch を要する ∴ 当席は測れぬ |
| 60 | `push_dry_audit_bundle_991d4987a_v1.md` | `cdd29923871c8bae` | 29 | 監査束の枝を乾走→push (GO 286399)・force 0 |
| 61 | `option_c_execution_packet_v1.md` | `ee9e19ec2a63b4dd` | 70 | ★㋒ 実行 packet 5 段★ 樹/INCLUDE 4,201/候補 1,649/export/TEMP 乾走 ROLLBACK |
| 62 | `candidates1649_other900_origin_reverse44_v1.md` | `b255e4432b5bc024` | 44 | 其外 900 を ㋥9/㋭335/㋬556 に三分・正規化差 無・逆向き 44 |
| 63 | `never_in_history335_writer_shape_and_556_vs_357_v1.md` | `49c6455cd17e1eb9` | 47 | ㋭335 の書き手の形 (束 34・hash 18 種)・556 対 357 = ★別母数★ |
| 65 | `leading_slash27_writer_path_history_v1.md` | `a96fa3b10676202a` | 44 | 先頭 `/` 27 本 ―― 讀めた 5 器いづれも書き得ぬ・27/27 候補に在り |

## §2 数の系譜 (出典を付す。★総監督殿の値は家老便経由で受けた物であり当席は DB を 1 本も打つて居らぬ★)
| 刻 | 数 | 何を 1 と数へたか | 出所 |
|---|---|---|---|
| v2 lot 前 | 20,956 | 表の行 | seq285143 (総監督) / `sync_v2_lot_handover_v3.md` §2 項7 |
| v2 lot 16:07 COMMIT | deleted 15,288 → 残 ★5,668★ | 表の行 | 同上 |
| ㋒ packet 時 (19:0x 前) | 表 ★5,806★ | 表の行 (S3 で二度測つた) | order61 紙 §S3 |
| 同 | INCLUDE 集合 ★4,201★ / 候補 ★1,649★ / 逆向き ★44★ | 追跡簿の path / 表の行 | order61 紙 §S2-S3 |
| 候補の内訳 | ㋑729 + ㋺24 (重なり 4) + 其外 900 = 1,649 | 表の行 | order61 紙 §S3 |
| 其外 900 の内訳 | ㋥9 (rename 旧側) + ㋭335 (履歴に一度も無し) + ㋬556 | 表の行 | order62 紙 §1 |
| ㋒ DELETE 直前 | 表 ★5,808★ | 表の行 (5,806 + 2) | 総監督便 seq286458 / hs_9d8570a9 (家老便経由) |
| 増えた 2 行 | cand_now 1,651 の内 ★2★ | 表の行 | hs_9d8570a9 ―― #120/#121 merge で main に入つた file を v3 hook が書いた ★正規行★ |
| ㋒ DELETE 19:01 COMMIT | deleted ★1,649★ → 残 ★4,159★ ・main_hit ★0★ | 表の行 | seq286458 (家老便経由) |
- 検算: 5,808 − 1,649 = ★4,159★ (合ふ)。5,806 → 5,808 の 2 行は ★INCLUDE 基準 `dbf05a029` が古いゆゑ候補に見えた正規行★ であり、消した 1,649 には入つて居らぬ。

## §3 GO 鎖と実行者 (★打手は総監督殿・A2 は packet の組立と枝の push のみ★)
| seq | 何の GO | A2 が為した事 | 打手 |
|---|---|---|---|
| 286399 | 監査束の枝 push | 乾走 → push (force 0)・紙 60 | A2 (令の範囲内) |
| 286419 (親 286415) | ㋒ 実行 packet の組立 (DB 讀取 SELECT と TEMP 乾走 ROLLBACK のみ緩和) | 5 段を rc=0 で組み・門を通し ROLLBACK・紙 61 | A2 |
| 286458 | ㋒ DELETE COMMIT | ★A2 は打つて居らぬ★ (令に無く・env の緩和も order61 限り) | ★総監督殿★ |
| hs_9d8570a9 | 非 main 2 行の SELECT と order64 取消 | 取消便を受け order63 に専念 | 総監督殿 / 家老殿 |

## §4 併記訂正の一覧 (★和 5★ ―― いづれも ★元の文を消さず併記★)
1. ㋒「残行を悉く消す」の狭め: order51 §2 → order52 §3 (L661 fnmatch ∴ A型直下は消えぬ側)。併記の場 = order56 冒頭。
2. 三値 → 4 語: order55 の令は「三値」だが列挙は 上書き/二重/消失/無害 の 4 語。家老裁 `msg_20260907_180250_f4191651` で 4 語が正。併記の場 = order56 冒頭。
3. 差 41: order50 §3 の「226 ref 合併 5,627 対 實測 5,668 = 差 41」→ 248 ref で測り直し ★5,678★ ∴ 「41 不足」ではなく ★+10 過剰★ へ置き換はる。併記の場 = order57 §4。
4. order50 ㋩「CI は v3 の外を書かぬ = 現に無い」→ 候補 1,649 の内 ★317 本が CI #2 の集合に当たる★ (其の内 其外900 に属する 147)。母集合が違ふ ∴ 矛盾せぬが「外を書かぬ」と読むには足りぬ。併記の場 = order62 冒頭。
5. 誤測 1: 静的 SQL を `grep -c "E'/"` で測り 1 件と出たが content 側の拾ひ誤り。VALUES 第1要素で測り直し ★0★。併記の場 = order65 §境界。

## §5 未測・測定不能 の一覧
- C4 ★遠隔のみの ref 17 本★ ―― fetch を要する ∴ 当席の禁の内側では測れぬ (order59)。差 17 の裁も未了。
- ㋭335 の ★書き手の器★ ―― csv の 7 列の形までは測つたが器は名指せぬ (order63)。
- 先頭 `/` の ★27 本の器★ ―― 讀めた 5 器はいづれも書き得ぬ ∴ repo 内の道では説明が付かぬ (order65)。hash 長 22/24/29/43 の非 hex を入れる道は符號の中に無い。
- 其外 900 の ★書き手★ 全般 ―― 履歴での三分までで、誰が表へ入れたかは測つて居らぬ (order62)。
- 入口 regex 対 出口 fnmatch の ★両向きの食ひ違ひ★ (入口のみ 623 / 出口のみ 59) の実害 ―― 要 SELECT 計 10 本が未了 (order53/57/58/59)。
- CI #2 が ★現に走つて居るか★ ―― workflow の実行歴を見て居らぬ (order62・order50 ㋩ 併記)。

## §6 証跡の在処
- INCLUDE 集合 csv = `o61_include_set_main_dbf05a029.csv` sha256 `97356a6ce61f323149b1be0019fcf380cd622e14d7ffa3842ec9a4ce94f19a13` (csv 行 4,202 = 見出し 1 + 4,201)
- 候補 export csv = `o61_candidates_export.csv` sha256 `3af768ba96d4b27f2901bc39fb0d7a3173f7f3b26ecd61c1a08133e4c3337d9a` (45,632,972 byte・論理行 1,649・物理行 393,779)
- S4 export script = `o61_s4_export.sql` / S5 乾走 script = `o61_s5_dryrun.sql` (全文は order61 紙 §S5 に写し済)。いづれも上記 dir 下。
- 台帳 = `scratch/ashigaru-third-2-ledger/sent_ids.yaml` (本紙の直前で 5,525 行・便 1 通 = 7 行 か 10 行)
- ★総監督殿側の run.log・backup の path は当席へ届いて居らぬ★ ―― v2 lot では `~/sync_v2_export/20260907/run.log` が便で示されたが、㋒ lot では ★受けて居らぬ★ ∴ 本紙に書けぬ (次担当は総監督殿へ請ふべき所)。

## §7 次担当への注記 (7 項)
1. ★INCLUDE 基準の鮮度★: 候補の判定は「其の時の main の追跡簿」に依る。基準 (`dbf05a029`) が古いと ★新しく merge された正規行が候補に見える★ ―― 現に 2 行が其れであつた。DELETE の直前に S3 を測り直す事。
2. ★fnmatch 対 regex の食ひ違ひは両向き★: 入口のみ 623・出口のみ 59。片方だけ直すと逆向きの取りこぼしが残る。
3. ★㋐ と ㋒ は排他ではない★: ㋐ (残す) を選んでも読み手の空振り 4 語は残り、引金 R4 は其の 4 語の何れでもない (order55)。
4. ★表に branch/pc の列は無い★ (`20260403020939` の 7 列)。∴ 「どの枝が書いたか」は表からは言へぬ ―― commit_hash の形が唯一の手掛かりで、其れも 40 hex とは限らぬ (order65)。
5. ★入る道は枝ごとに在り、出る道は 1 本しか無い★ (order50 §3 根)。pre-push hook は今 `SYNC_SOURCE_CACHE_FORCE != 1` で SKIP する止血が入つて居る (L54-61) ―― 止血を解く時は入口の増え方を先に測る事。
6. ★便は 300 字で拒まれる★ (`inbox_write.sh`)。証跡は紙へ置き、便は path + sha16 + 要旨に留める。`IW_ALLOW_LONG` は本 lot で 0 回。
7. ★数は「何を 1 と数へたか」を必ず併記★。本 lot では 表の行 / 追跡簿の path / csv の論理行 / 紙の本数 が別物として現れ、母数の取り違へが併記訂正 5 件の内 3 件 (項 3・4・§3 の 556 対 357) の因であつた。

## §境界
- 本紙は ★既存 15 本を 1 字も書き換へて居らぬ★ (再測は讀取のみ)。総監督殿の値は ★家老便経由の受け取り★ であり当席の測りではない (§2 の出所欄に明記)。
- DB 讀取 0・書込 0・DELETE 0・DDL 0・fetch/pull/clone 0・v3 走行 0・本番 code 書込 0・force push 0。
- 判定語・推し語・先送り語は置いて居らぬ。次に何を為すべきかは総監督殿・家老殿の裁である。
