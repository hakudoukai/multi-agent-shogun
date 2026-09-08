# run.log 逐語 受領 と 系譜の末端 突合 (讀取のみ・DB 0・走行 0・fetch 0・書込 0)

as_of 2026-09-07 21:55 JST / 席 ashigaru-third-2 / 令 order69 / 逐語 出所=総監督殿 hs_7f5a6da5 (21:44 受領・家老third 経由)
★前紙 不触 (着手時 再測 差0 3/3)★: `54fe3eb4b887c12c` option_c_lot_handover_v1.md 84行 / `5befe6fada8fd2b2` unmeasured6_measurement_plans_v1.md 66行 / `e47fbe3cc64eb344` plan4_other900_and_plan6_two_rows_v1.md 50行
数の 1: §1=file 1本 / §2=csv の論理行 1本(=表の行 1本=file_path 1値) / §3=file 1本 / §4=run.log に現れた数 1つ
path 値・content・commit message は一字も写して居らぬ (dir 括りと拡張子の類までとす)

## §1 逐語の物 ―― 実在と sha256 の突合 (当席が sha256sum で測り直した)
| 物 | 便の記載 | 当席の測り | 差 |
|---|---|---|---|
| run.log (`/home/hakudoukai/o61_delete_20260907/`) | sha256 265cde…dd88・6行・275B | 同値・6行・275B | ★差0★ |
| delete.sql (同上) | sha256 a5d428…9a58・30行 | 同値・30行 | ★差0★ |
| o61_candidates_export.csv (backup) | sha256 3af768…7d9a・393,779行 | 同値・wc -l 393,779 | ★差0★ |
| o61_include_set_main_dbf05a029.csv (backup) | sha256 97356a…19a13・4,202行 | 同値・4,202行 (header 1 + 4,201) | ★差0★ |
| backup dir の file 数 | 7 本を列挙 | 実在 7 本 | ★差0★ |
| o61_s4_export.sql / o61_s5_dryrun.sql / option_c_execution_packet_v1.md | sha 記載無し | 当席が新たに測る: `10cbe6ed…`/`4b382fe9…`/`ee9e19ec…` | 新規 |
| backup の写しと third 局所 dir の同一性 | 「写し(sha 同一)」 | candidates csv を両所で測り 同値 | ★差0★ |
- ∴ 逐語で示された 4 本の sha256 は ★4/4 差0★。backup dir は /mnt/c 配下ゆゑ ★讀取のみ・一字も書いて居らぬ★ (45MB の parse は同 sha の局所写しで行つた)。

## §2 export の ★件数★ (行数と別に数へた値) と 1,651 との差
- 器: `csv.field_size_limit(sys.maxsize)` + `csv.reader`・streaming (content 値は捨て、file_path と updated_at のみ見た)。
- ★件数 = 1,649★ (distinct file_path 1,649・重複 0)。★物理行 393,779★ ∴ 1 件あたり 238.8 行 ―― content が複数行ゆゑ ★行数 ≠ 件数★ は現に在る。
- 便の「候補 export(★1,651 件★・DELETE 前)」は ★合はぬ★。★差 2★。
- 根 (delete.sql の逐語で閉ぢる): L7 `loaded` = export を temp へ入れた数 = ★1649★ / L10 `cand_now` = ★実行時に再計した★「main 集合に無い行」の数 = ★1651★。∴ 1,651 は export の件数ではなく ★19:01:14 時点の候補の再計値★。
- 傍証: export の updated_at 最大 = ★2026-09-07 16:43:27★・18:5x 台の行 ★0★ ∴ 18:57 に書かれた行は export に入り得ぬ。

## §3 差 2 の名指し (order68 ⑥ と突き合はせ)
- 総監督殿が cand_now 一覧で名指した 2 行 = #120 `9bbdebdef` 18:57:36 / #121 `8ca8e7ea1` 18:57:47。当席は此の 2 commit を git 讀取で開いた。
- 触れた file: #120=7本 / #121=5本 (order68 と 差0)。其の内 ★status A (新設) = 各 2本・和 4本★。
- 4本に v3/CI の EXCLUDE を掛けると ★`**/*.test.*` に当たる 2本が落ち★、残るは ★各 commit 1本・和 2本★ (悉く `frontend/src/features/**` 直下・INCLUDE に当たり・基準 main 集合 4,201 に無い)。
- ∴ ★差 2 の正体 = 18:57:36 と 18:57:47 に 1本づつ新設された INCLUDE file の行★。試験 file 2本は EXCLUDE ゆゑ表へ入らぬ ―― ★4 が 2 になる理由は EXCLUDE である★。
- 二重の検算: 表の総数 5,806→5,808 = ★+2★ ／ 候補 1,649→1,651 = ★+2★ ―― 増えた 2 行が悉く候補側であり、`main_hit=0` と向きが合ふ。
- order68 の三値 (消した 1,649 への正規行の混入 = ★現に無い★) は動かぬ: 此の 2 行は export に無く (§2 傍証)・deleted=1649 の外に在り・今も表に残つて居る。

## §4 run.log の数 と 引き継ぎ紙 §2 系譜 の 一行づつの突合 (9 項)
| run.log の数 | §2 系譜の対応 | 突合 |
|---|---|---|
| loaded=1649 | 「deleted 1,649」の母 = 候補 export | ★差0★ (当席の csv 件数 1,649 とも 差0) |
| before=5808 | 「DELETE 直前 5,808」 | ★差0★ |
| matched=1649 | 対応語 ★無し★ | loaded と等値 ⇒ export の全行が表に現存 (消えて居た行 0) |
| cand_now=1651 | 対応語 ★無し (§2 未載)★ | loaded との差 ★2★ = §3 の 2 行 |
| main_hit=0 | 「main_hit 0」 | ★差0★ |
| deleted=1649 | 「deleted 1,649」 | ★差0★ |
| after=4159 | 「残 4,159」 | ★差0★ |
| total_now 4159 | 同上 (COMMIT 後の再測) | ★差0★ |
| ok=t / COMMITTED / rc=0 | §2 に無い (可否の印) | delete.sql L17 が `deleted=1649 かつ before-after=1649` を自ら検し真 |
- 和: ★突合 9 項 = 差0 が 7 / §2 に載つて居らぬ数が 2 (matched・cand_now)★。★合はぬ数 = 0★。
- §2 の「packet 時 5,806」は run.log に対応が無いが、5,808−5,806=2 と cand_now−loaded=2 が ★同じ 2★ を指す。
- 引き継ぎ紙 §2 の前段 (20,956 / deleted 15,288 / 残 5,668) は run.log の外 ―― 本紙では突合して居らぬ。

## §5 三値
| 事 | 三値 |
|---|---|
| 逐語 4 本の sha256 一致・backup 7 本の実在 | ★現に在る★ |
| export の件数 1,649 (≠ 行数 393,779・≠ 1,651) | ★現に在る★ |
| 差 2 = 18:57 の 2 commit が 1本づつ新設した INCLUDE file (git 側で一意に定まる) | ★現に在る★ |
| 其の 2 行が表に現存する事・file_path の DB 側 照合 | ★測定不能★ (SELECT 1本を要す・当席は DB を讀まぬ) |
| 「1,649 件だけの別 backup file」 | ★現に無い★ ―― 要らぬ。export 其の物が 1,649 件であつた |
| 消した 1,649 に正規行 (現 main の INCLUDE) が混ざつた事 | ★現に無い★ (order68 の 0/63 と本紙 §3 が同じ向き) |

## §6 総監督殿向け 確認 SELECT 1本 (当席は打たぬ・案文のみ)
`select file_path, commit_hash, updated_at, created_at from public.source_code_cache where created_at > '2026-09-07 16:43:27+09' order by created_at;`
期待列 4・★期待行数 2★ (2 行なら §3 の名指しが DB 側でも閉ぢる。3 行以上なら 19:01 以降の書込が在ると読む)。危険=讀取のみ・権限=総監督殿。

## §境界
DB 讀 0・書 0・DELETE 0・DDL 0・SQL 実行 0・fetch/pull/clone 0・push 0・v3 走行 0・本番 code 書込 0・secret 0・患者本文 0。
打つた git は `show --name-status -m --first-parent --format=` のみ (讀取動詞)。backup dir (/mnt/c 配下) は ★讀取のみ★・sha 測定と ls の外に触れて居らぬ。
§3 の EXCLUDE 判定は当席の fnmatch (出口側の目) ―― 前紙 order68 §2-b の 623 差の併記は本紙でも效く (入口 regex と目が異なる)。
本紙は前紙 3 本を書き換へず併記した新紙。逐語は令 YAML の source 欄に全文在り、便には写して居らぬ。
