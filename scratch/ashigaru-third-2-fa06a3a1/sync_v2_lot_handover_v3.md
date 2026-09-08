# sync v2 lot 引き継ぎ紙 v3 (order49 產・讀取のみ・★DB 0・走行 0・fetch 0★)

as_of 2026-09-07 16:3x JST / 席=ashigaru-third-2 / 令=karo-third order49。
★前紙 v2 = `sync_v2_lot_handover_v2.md` sha16 `4faa28c3133801ff` 70 行 (本手番で再測)・v1 `63cfeac1b5787c70` ―― 何れも 1 字も書き換へて居らぬ★。
★v2 → v3 の差分要旨 (3 つ)★:
 (a) GO 鎖 8 項に ★実績値★ が入つた (総監督殿 seq285143・lot 完遂: export/乾走/DELETE COMMIT)。v2 では 1〜5・7・8 が「未」であつた。
 (b) 紙の疵 2 点 (`\copy` の列リスト・行数の数へ方) を ★併記で取消し★ 正した文を置いた (§3)。
 (c) main tip の as_of を打ち直した (v2 の `1d8e1ede…` → 本手番の局所 ref `620df477e…`)。
三択語=測つた/測つて居らぬ/測れぬ。1 = file 1 本、commit = commit 1 本、行 = ★csv の論理行 (レコード) 1 本★ (§3 疵2)。
path は multi-agent-shogun repo からの相対。枝と commit は /mnt/c/DentalBI repo の物 (讀取のみ)。

## §1 現況 (本手番で再測・局所 ref のみ)
| 事 | 値 | 註 |
|---|---|---|
| main tip | `620df477e3558783b26665bab332134b2cb84d0b` | ★局所 `refs/remotes/origin/main` を讀んだ写し★。fetch 0 ゆゑ遠隔の現在と一致するかは ★測つて居らぬ★ |
| tip の 2 blob | `scripts/sync_source_cache.py` = `0754d9284db2d50c5f3941ad1d3cf786d5279de9` / `tests/test_sync_source_cache.py` = `f27523f66ca36a2ba365d6b550f062c96e5578f0` | v2 と同値 ∴ ★v3 の blob が main に在る★ |
| PR #114 | `MERGED` / mergeCommit `abb57b40665b64f418e27d171f19218398640185` / base `main` / head `b7323535bba89b59fad8fb2c6e6e7632be43a211` / 2 file | ★v2 からの写し★ (本手番で gh を打つて居らぬ) |
| abb と tip の関係 | `merge-base --is-ancestor abb 620df477e` rc=0・`rev-list --count abb..620df477e` = ★12★ | v2 の時は 4 であつた。時が進んだ事による |
| PR #112 | `CLOSED` / mergedAt null / head `3155e8dc0893f3ff40eb809d9fcae0c08f97875c` / 16 file | ★v2 からの写し★ |
| evidence push | 遠方 `refs/heads/karo-third/a2-14c8ec72-fixed` = `ccb39de3d8a6f0d943f051e775bda085a55683be` (早送り・force 0) | 紙 `A_evidence_push_v1.md` d1adcffae95db085 |

## §2 GO 鎖 8 項 ―― 実績 (打手は全て総監督殿。値は seq285143 を家老便経由で受けた物であり ★当席は DB を 1 本も打つて居らぬ★)
| 項 | 要旨 | 実績 | 出所 |
|---|---|---|---|
| 1 | export 紙 §6 の照合 3 式 | export ★15,288 行★ (行 = csv 論理行)。行数式は §3 疵2 の読み替へを当てる | seq285143 |
| 2 | `both_rows` が 15,288 か | ★15,288★ と ★対応する★ | seq285143 |
| 3 | export の sha256 を別媒体へ 1 本 | sha256 頭 `7d4ed5dde22bd547` | seq285143 |
| 4 | 乾走 (TEMP → count → ROLLBACK) | TEMP 乾走 `loaded` = ★15,288★ | seq285143 |
| 5 | v3 の軍師検分 | ★当席は原本を讀んで居らぬ (測つて居らぬ)★ ―― 家老便の引用のみ | 家老便 |
| 6 | v3 が同期経路へ入つて居るか | main tip の blob = `0754d9284…` ∴ ★追跡簿上は入つた★。実走行は ★測つて居らぬ★ | §1 |
| 7 | DELETE の WHERE が prefix 2 本 + 生れた日か | DELETE COMMIT ★16:07★ ―― before 20,956 / deleted ★15,288★ / after ★5,668★ / 残 0。WHERE の文言そのものは ★当席は讀んで居らぬ★ | seq285143 |
| 8 | 打つ器・人・時刻を控へたか | 証跡 = `~/sync_v2_export/20260907/run.log` ★path のみ記す・当席は開かぬ★ (令の禁)・時刻 16:07 | seq285143 |
★DELETE の文そのものは本紙へ転記して居らぬ★ (二重管理を避ける・元紙 = order35 手順紙 `83842dd17d680485` §6)。

## §3 紙の疵 2 点 ―― ★元の文は消さず、併記して取消す★
### 疵1 `\copy` に列リストが無い (元紙 = `venv_rows_rollback_v1.md` `6a45761bdb87da5d` §3 L22)
- ★元の文 (取消)★: `\copy venv_restore FROM 'venv_rows_20260907.csv' WITH (FORMAT csv, HEADER true)`
- ★正した文★: `\copy venv_restore (file_path, content, file_size, line_count, commit_hash, updated_at, created_at) FROM 'venv_rows_20260907.csv' WITH (FORMAT csv, HEADER true)`
- 何故: TEMP 表は `CREATE TEMP TABLE venv_restore (LIKE public.source_code_cache INCLUDING DEFAULTS)` (同 §3 L21) で作るゆゑ ★表の列順★ を継ぐ。csv は 7 列でありその順は表の列順と同じとは限らぬ ∴ ★列リストを必須とする★。以後 `\copy` は列リスト無しで書かぬ。

### 疵2 行数の数へ方 (元紙 = 同 `venv_rows_rollback_v1.md` §2 L14)
- ★元の文 (取消)★: `wc -l venv_rows_20260907.csv` = 15,289 (= 15,288 + header 1)
- ★正した文★: 行数は ★csv の論理行 (レコード) で数へる★ (dev_qa#867)。`content` 列に改行が入るゆゑ ★物理行 (`wc -l`) は論理行より多くなる★。数へ方は csv parser を通す (例: TEMP 表へ載せた後の `count(*)`)。
- ∴ 照合式は「`wc -l` = 15,289」ではなく「★`loaded` (= TEMP 表の `count(*)`) = 15,288★」を採る。§2 項1・項4 は此の読み替へで書いた。
- ★本紙で「行」と書いた時は csv 論理行の事である★ (冒頭の数へ方に明記)。

## §4 未だ詰まつて居らぬ事 (GO の外・人が見るべき所)
1. ★15,288 と 15,271 の差 17★ ―― 15,288 = 総監督 SELECT 実測、15,271 = order33 の引き算。当席は ★詰めて居らぬ★。lot は 15,288 を採つて完遂した。
2. ★#2 CI の upsert に on_conflict が無い件★ ―― 裁 283660 ★待ち★。同じ表 (source_code_cache) を触る道。
3. ★DELETE 後の 5,668 と v3 の母集合 4,185 の差 1,483★ ―― 4,185 = 当席が origin/main の追跡簿で数へた N (order48 紙 `648f7f12079e7d55` §3)。5,668 は総監督実測。差の中身は ★測つて居らぬ★ (v3 の対象外 prefix・古い path・生れた日違ひ の何れか)。order48 紙 §5 の SELECT 案② が此の内訳を採る形になつて居る。
4. ★v3 の軍師検分の原本★ ―― 当席は讀んで居らぬ (§2 項5)。
5. `/home/hakudoukai/a2/wt-964a06d0-d3adf65b` (D 樹) ―― ★軍師の判定待ちゆゑ触れて居らぬ★。

## §5 次の総監督殿の初手 (5 行)
1. 本紙 §1 の main tip (`620df477e…`) と 2 blob を己の器で再測する ―― 当席は fetch を打つて居らぬゆゑ、遠隔が先へ進んで居る事は在り得る。
2. §2 の実績値 (15,288 / 7d4ed5dd / 16:07 / 5,668) を run.log と DB で己の目で突き合はせる ―― 当席は run.log を開いて居らぬ。
3. §3 の疵 2 点を rollback 紙本体へ入れるか、本紙の併記で足りるかを裁く (当席は前紙を書き換へぬ定めゆゑ本紙に置いた)。
4. §4-3 の差 1,483 を order48 紙 §5 の SELECT 案② で採る。
5. §4-2 の裁 283660 を併せ見る ―― 同じ表を触る道ゆゑ。

## §6 当席が打つて居らぬ物 (境界)
DB へ SQL 0 本・export 0・DELETE 0・merge 0・force 0・fetch 0・rebase 0・push 0・本番 code 書込 0・script 走行 0。
`~/sync_v2_export/20260907/run.log` は ★開いて居らぬ★ (path のみ記した・令の禁)。前紙 v1/v2 と rollback 紙・export 紙は ★1 字も書き換へて居らぬ★ (疵は本紙で併記取消)。
