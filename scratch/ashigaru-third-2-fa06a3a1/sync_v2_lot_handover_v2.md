# sync v2 lot 引き継ぎ紙 v2 (order46 產・讀取のみ・★実行 0・DB 接続 0★・v1 63cfeac1b5787c70 は不触)

as_of 2026-09-07 16:0x JST / 席=ashigaru-third-2 / 令=karo-third order46。
用=次の総監督殿(別アカウント)が本紙 1 枚から GO 判断へ辿れる様にする事。sha16・commit は ★本手番で再測つた★。
path は multi-agent-shogun repo からの相対。枝と commit は ★/mnt/c/DentalBI repo★ の物 (讀取のみ)。
三択語=測つた/測つて居らぬ/測れぬ。1 = file 1 本、行 = 行 1 本、commit = commit 1 本。

## §0 ★現況 (v2 で新たに足した節・merge 後)★
| 事 | 値 (本手番で再測) | 註 |
|---|---|---|
| PR #114 | `state=MERGED` / `mergedAt=2026-09-07T06:56:43Z` / `mergeCommit=abb57b40665b64f418e27d171f19218398640185` / base `main` / head `b7323535bba89b59fad8fb2c6e6e7632be43a211` / `changedFiles` 2 | `gh pr view --json` の語 |
| merge commit | `abb57b40665b64f418e27d171f19218398640185`・親 2 本 = `0973f8e584d7210ec46fbc125202957772c80abe`(旧 main) と `b7323535bba89b59fad8fb2c6e6e7632be43a211`(A2 の枝) | `log -1` |
| ★main の今の tip★ | `1d8e1edea7ef21f9654c72d5f30a85fec4a5ad67` (`ls-remote origin refs/heads/main` = 手元 `refs/remotes/origin/main` と同値) | ★家老便の `abb57b406` から ★4 commit 進んで居る★(`rev-list --count abb..1d8e` = 4)。`merge-base --is-ancestor abb 1d8e` rc=0 ゆゑ ★abb は今の main に含まれて居る★ |
| main tip の 2 blob | `scripts/sync_source_cache.py` = `0754d9284db2d50c5f3941ad1d3cf786d5279de9` / `tests/test_sync_source_cache.py` = `f27523f66ca36a2ba365d6b550f062c96e5578f0` | `abb57b406` 時点でも同値・家老再測とも同値 ∴ ★v3 の blob が main に在る★ |
| PR #112 | `state=CLOSED` / `mergedAt=null` / `mergeCommit=null` / head `3155e8dc0893f3ff40eb809d9fcae0c08f97875c` / `changedFiles` 16 | 合流させずに閉ぢた。#114 が継いだ |
| evidence push | 遠方 `refs/heads/karo-third/a2-14c8ec72-fixed` = `ccb39de3d8a6f0d943f051e775bda085a55683be`(早送り・force 0)。中身 = `reports/evidence/A_record_v2.md` + `A_worktree_remove_v1.md` の 2 紙 270 挿入 | 紙 `A_evidence_push_v1.md` d1adcffae95db085 |
| 残つて居る枝 | `a2-fa06a3a1-sync-rewrite-v3` = `3155e8dc0…`(#112 の物) / `a2-14c8ec72-fixed` = `8aff82bf4fbf32d70a092b31498eb5f402552c4d`(旧 ref) ―― 何れも ★消して居らぬ★ | `show-ref --verify` |

## §1 產物表 (7 件・sha16 は v1 の値・本手番で再測して居らぬ物は其の旨)
| 產物 | path | sha16 | 行 | 役 |
|---|---|---|---|---|
| v3 patch | scratch/ashigaru-third-2-fa06a3a1/0003-sync_source_cache-v3-tracked-index-plus-exclude-belt.patch | c05138103db14f7b | 678 | 直しの本体 (2 file・新規 0) |
| v3 紙 | 同 dir/sync_source_cache_rewrite_v3.md | a319a31c27960150 | 91 | v3 の設計と測り |
| export 紙 | 同 dir/venv_rows_export_v1.md | 120f4fe5968c98cf | 78 | 消す前に控へる手順 |
| rollback 紙 | 同 dir/venv_rows_rollback_v1.md | 6a45761bdb87da5d | 71 | 戻す手順 + ★GO 8 項 §7★ |
| order35 手順紙 | 同 dir/venv_rows_export_rollback_go_plan_v1.md | 83842dd17d680485 | 119 | 全体の元紙 (★DELETE 文は §6 に在る★) |
| order33 SELECT 案 | 同 dir/rows_15271_select_plan_v1.md | ea20e81d75e95ade | 80 | 数を数へる案 (15,271 側) |
| 総監督 SELECT 結果 | ―― (便 0032ec458) | ★測れぬ★ (当席に file 0) | ―― | 15,288 の出所 |
補: 試験の生 = 同 dir/order36_pytest_raw.txt (3e9058da3dc9efaf・8 行・`27 passed`)。★上表の sha16 は v1 の写しであり、本手番で再測して居らぬ★。 ★v2 lot の道中の紙 (本手番で測つた)★: order41 `sync_v3_push_pr_v1.md` ef7fd33a928877f3 37 行 / order43 `A_evidence_successor_v2.md` f3831b77efa5e554 40 行 / order45 `A_evidence_push_v1.md` d1adcffae95db085 18 行 / order44 `sync_v3_main_pr_v1.md` 0e938a3e8b7007e0 31 行。

## §2 順序 6 段と現況 (順序の裁 = 総監督 seq284563)
| 段 | 何をする | 打手 | 現況 (as_of 16:0x) |
|---|---|---|---|
| 1 | v3 を作る | A2 | ★済★。#114 として main へ入つた (`abb57b406`・blob 2 本 上表) |
| 2 | 軍師 third-2 の検分 | 軍師 | 家老便は「軍師 PASS seq284801」と伝へる(★`PASS` は其の便の語であり当席の判定ではない★)。★当席は其の便を讀んで居らぬ (測つて居らぬ)★ |
| 3 | export (控へを採る) | 総監督 | 紙 完・★実行 0★ |
| 4 | rollback 手順を備へる | A2 | 紙 完 (乾走の手順まで書いた)・★実行 0★ |
| 5 | GO | 総監督 | ★未★ |
| 6 | DELETE | 総監督 | ★未★ (家老も A2 も打たぬ定め) |
∴ 段 1 は v1 の時の「枝 3155e8dc0・樹を畳んだ」から ★main 合流済★ へ進んだ。段 2〜6 は v1 と変はつて居らぬ。

## §3 GO 鎖 8 項の済/未 (項目の本文は rollback 紙 6a45761bdb87da5d §7・★打手は全て総監督★)
| 項 | 要旨 | 済/未 | 誰が |
|---|---|---|---|
| 1 | export 紙 §6 の照合 3 式が揃つたか | ★未★ (export 実行 0) | 総監督 |
| 2 | `both_rows` が 15,288 か | ★未★ (当席 DB 讀取 0) | 総監督 |
| 3 | export の sha256 を別媒体へ 1 本 | ★未★ | 総監督 |
| 4 | 乾走 (TEMP 表 → count → ROLLBACK) | ★未★ | 総監督 |
| 5 | v3 の軍師検分が着いて居るか | ★当席は測つて居らぬ★ (家老便に依る引用のみ) | 軍師→総監督 |
| 6 | v3 が同期経路へ入つて居るか | ★main の追跡簿上は入つた★ (main tip の blob = `0754d9284…`)。実走行は ★測つて居らぬ★ | 総監督 |
| 7 | DELETE の WHERE が prefix 2 本 + 生れた日か | ★未★ (DELETE 0) | 総監督 |
| 8 | 打つ器・人・時刻を控へたか | ★未★ | 総監督 |
★DELETE の文そのものは本紙へ転記して居らぬ★ (二重管理を避ける・元紙 = order35 手順紙 §6)。

## §4 未だ詰まつて居らぬ事 (★3 件・GO の前に人が見るべき所★)
1. ★15,288 と 15,271 の差 17★ ―― 15,288 = 総監督 SELECT 実測 (backend/.venv 12,527 + .venv-linux 2,761)、15,271 = order33 の引き算。総監督紙は「同じ日の他 prefix と相殺の範囲」と記す。当席は ★詰めて居らぬ★。export 紙・rollback 紙は 15,288 を期待値に採り、ずれたら止まる形にしてある (rollback 紙 §6)。
2. ★#2 CI の upsert に on_conflict が無い件★ ―― 裁 283660 ★待ち★。本 lot の外だが同じ表 (source_code_cache) を触る道ゆゑ、GO の前に併せて見られたい。
3. ★v3 の検分の着荷★ ―― v1 では「v2 の判定を v3 で置換の願ひ (seq284637)」であつた。今は家老便が其の語を伝へるが、当席は原本を ★讀んで居らぬ★。段 3 へ進む前に総監督殿の目で 1 度 確かめられたい。

## §5 ★次の総監督殿の初手 (5 行)★
1. 本紙 §0 で main tip (`1d8e1ede…`) と 2 blob (`0754d9284…`/`f27523f66…`) を己の器で再測する ―― 合はねば GO へ進まぬ。
2. 本紙 §3 の 5 (軍師の検分の原本 seq284801) を直に讀む ―― 引用ではなく原本で。
3. rollback 紙 6a45761bdb87da5d §7 の 8 項を上から押す。1〜4 が済むまで DELETE の紙 (order35 §6) を開かぬ。
4. §4-1 の差 17 を詰める (もしくは「詰めずに進む」と明記して控へる)。
5. §4-2 の裁 283660 を併せ見る ―― 同じ表を触る道ゆゑ。

## §6 当席が打つて居らぬ物 (境界)
DB へ SQL 0 本・export 0・DELETE 0・merge 0・force 0・fetch 0・本樹の作業樹への書込 0。push は名指し 1 refspec を 2 度のみ (`a2-fa06a3a1-sync-rewrite-v3-main` と `karo-third/a2-14c8ec72-fixed`)。
`/home/hakudoukai/a2/wt-964a06d0-d3adf65b` (D 樹) は ★軍師の判定待ちゆゑ触れて居らぬ★ (`worktree list` で在を再測)。
★開示★: 家老便は merge 後の main を `abb57b406` と伝へたが、本手番の `ls-remote` は `1d8e1ede…` であつた。誤りではなく ★時が進んだ★ 事による (abb は 1d8e の祖先・間に 4 commit)。v1 紙は 1 字も書き換へて居らぬ。
