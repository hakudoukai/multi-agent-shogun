# sync v2 lot 引き継ぎ紙 v1 (order38 產・讀取のみ・★実行 0・DB 接続 0★)

as_of 2026-09-07 15:1x JST / 席=ashigaru-third-2 / 令=karo-third order38。
用=次の総監督殿(別アカウント)が本紙 1 枚から GO 判断へ辿れる様にする事。sha16 は ★本手番で再測つた★。
path は multi-agent-shogun repo からの相対。枝と commit は ★/mnt/c/DentalBI repo★ の物 (讀取のみ)。
三択語=測つた/測つて居らぬ/測れぬ。1 = file 1 本、行 = 行 1 本。

## §1 產物表 (7 件・sha16 再測 2026-09-07)
| 產物 | path | sha16 | 行 | 役 |
|---|---|---|---|---|
| v3 patch | scratch/ashigaru-third-2-fa06a3a1/0003-sync_source_cache-v3-tracked-index-plus-exclude-belt.patch | c05138103db14f7b | 678 | 直しの本体 (2 file・新規 0) |
| v3 紙 | 同 dir/sync_source_cache_rewrite_v3.md | a319a31c27960150 | 91 | v3 の設計と測り |
| export 紙 | 同 dir/venv_rows_export_v1.md | 120f4fe5968c98cf | 78 | 消す前に控へる手順 |
| rollback 紙 | 同 dir/venv_rows_rollback_v1.md | 6a45761bdb87da5d | 71 | 戻す手順 + ★GO 8 項 §7★ |
| order35 手順紙 | 同 dir/venv_rows_export_rollback_go_plan_v1.md | 83842dd17d680485 | 119 | 全体の元紙 (★DELETE 文は §6 に在る★) |
| order33 SELECT 案 | 同 dir/rows_15271_select_plan_v1.md | ea20e81d75e95ade | 80 | 数を数へる案 (15,271 側) |
| 総監督 SELECT 結果 | ―― (便 0032ec458) | ★測れぬ★ (当席に file 0) | ―― | 15,288 の出所 |
補: 試験の生 = 同 dir/order36_pytest_raw.txt (3e9058da3dc9efaf・8 行・`27 passed`)。

## §2 順序 6 段と現況 (順序の裁 = 総監督 seq284563)
| 段 | 何をする | 打手 | 現況 (as_of 15:1x) |
|---|---|---|---|
| 1 | v3 を作る | A2 | 產物 = 上表。枝 a2-fa06a3a1-sync-rewrite-v3 = ★3155e8dc0★ (再測)。樹は畳んだ |
| 2 | 軍師 third-2 の検分 | 軍師 | ★待ち★ (家老が seq284637 で提出・v2 の判定を v3 で置換の願ひ付) |
| 3 | export (控へを採る) | 総監督 | 紙 完・★実行 0★ |
| 4 | rollback 手順を備へる | A2 | 紙 完 (乾走の手順まで書いた)・★実行 0★ |
| 5 | GO | 総監督 | ★未★ |
| 6 | DELETE | 総監督 | ★未★ (家老も A2 も打たぬ定め) |
枝の土台 = 1fbd0aa0f。★共有 HEAD も今 1fbd0aa0f で土台と同じ★ (再測)。
patch の当りは土台にて `git apply --check` rc=0 を測つた (order36 時)。段が進めば再測が要る。

## §3 未だ詰まつて居らぬ事 (★3 件・GO の前に人が見るべき所★)
1. ★15,288 と 15,271 の差 17★ ―― 15,288 = 総監督 SELECT 実測 (backend/.venv 12,527 + .venv-linux 2,761)、
   15,271 = order33 の引き算。総監督紙は「同じ日の他 prefix と相殺の範囲」と記す。当席は ★詰めて居らぬ★。
   export 紙・rollback 紙は 15,288 を期待値に採つた。ずれたら止まる形にしてある (rollback 紙 §6)。
2. ★#2 CI の upsert に on_conflict が無い件★ ―― 裁 283660 ★待ち★。本 lot の外だが、
   同じ表 (source_code_cache) を触る道ゆゑ、GO の前に併せて見られたい。
3. ★v2 の判定の置換★ ―― 軍師 third-2 へ出して在るのは v2。家老が v3 での置換を願つて居る (seq284637)。
   置換が済まぬ内に段 3 へ進むと、検分を受けて居らぬ物で消す事に成る。

## §4 GO の前に人が確かめる 8 項
★rollback 紙 (6a45761bdb87da5d) の §7★ を見られたい。★本紙へは転記して居らぬ★ (令の定め・二重管理を避ける為)。
要点のみ = 数の一致・控への sha256 と別媒体・乾走・v3 の検分結果・v3 が経路へ入つたか・WHERE 2 条件・打手の控へ。

## §5 当席が打つて居らぬ物 (境界)
DB へ SQL 0 本・export 0・DELETE 0・push 0・commit は自席枝のみ (共有枝 0)・本樹の作業樹への書込 0。
`/home/hakudoukai/a2/wt-964a06d0-d3adf65b` (D 樹) は ★軍師の判定待ちゆゑ触れて居らぬ★ (worktree list で在を再測)。
