# 裁 ①②③ の適用 と 窓の併記訂正 (讀取のみ・DB 0・fetch 0・書込 0)

as_of 2026-09-08 04:10 JST / 席 ashigaru-third-2 / 令 order70 / 裁=総監督殿 hs_270498bb(22:12)・SELECT 結果 hs_f9bca39e(22:09)
★前紙 不触 (着手時 再測 差0)★: `f7e066394ceecd6e` lineage_end_runlog_reconciliation_v1.md 69行 / `dadf9a7993db09e6` remote_only_refs_c4_measurable_v1.md 38行 / `54fe3eb4b887c12c` option_c_lot_handover_v1.md 84行
数の 1: §1〜§2=表の行 1本(file_path 1値) / §3=ref 1本・path 1本 / §4=列 1つ
path 値は写さぬ (§1 の 2 本の file 名は総監督殿の便に既出ゆゑ其の儘 引く)

## §1 窓の併記訂正 ―― 前紙 order69 §6 は書き換へず 此処に併記す
- 前紙 §6 の文言: `… where created_at > '2026-09-07 16:43:27+09' order by created_at;` ・★「期待行数 2」★。実際は ★6 行★。
- ★誤つて居たは窓の取り方であり、其の窓を書いたは ★当席★ である★ (家老殿は「期待行数を検めずに上げた」と己の誤りとされたが、文言は当席の紙 §6 に在る)。誤りは 2 つ:
  1. ★列の取り違へ★ ―― 起点 16:43:27 は export の ★updated_at の最大★ である。之を ★created_at★ の窓に当てた。両者は別の列ゆゑ窓が広がる。
  2. ★候補 filter の脱落★ ―― 本来の候補は「main 集合(4,201)に無い行」だが、o61_main は delete.sql の temp table ゆゑ外から引けず、当席は ★NOT EXISTS を落として★ 窓を書いた。∴ 候補でない行まで入る。
| 6 行の刻 | 本数 | 何者か | 差 2 との関はり |
|---|---|---|---|
| 16:47:25 | 2 | 総監督殿の一覧で #118/#119 | ★候補ではない★ (§2-c で数により示す) |
| 16:59:02〜03 | 2 | 同上 | ★候補ではない★ (同上) |
| ★18:58:47★ | ★2★ | commit_hash `8ca8e7e` / `9bbdebd` | ★差 2 の当人★ |
| 19:01:14 以降 | ★0★ | ― | DELETE 後に候補域へ入つた行は無い |

## §2 差 2 の結びが立つ理由 (四つの独立な数へが同じ 2 を指す)
- (a) run.log: `cand_now` 1,651 − `loaded` 1,649 = ★2★。
- (b) 表の総数: packet 時 5,806 → DELETE 直前 5,808 = ★+2★。(a) と同値。
- (c) 16:47/16:59 の 4 行が候補で ★在り得ぬ★ 事: `updated_at ≥ created_at` ゆゑ 16:43:27 より後に生れた行は export(最大 updated_at 16:43:27)に入らぬ。若し此の 4 行が候補なら cand_now は 1,649+4+2=★1,655★ となり 実測 1,651 と合はぬ。∴ 4 行の file_path は main 集合の側に在る (=候補でない)。
- (d) 名前の一致: 18:58:47 の 2 行の commit_hash は 18:57:36 `9bbdebdef` と 18:57:47 `8ca8e7ea1`。前紙 §3 で当席が git から採つた「A(新設) ∧ INCLUDE ∧ ¬EXCLUDE ∧ ¬main 集合」は ★各 commit 1 本づつ★ であり、其の file 名 (DefenseWarningPanel.tsx / kakeiAUnevaluableMeter.ts) が SELECT の 2 行と ★一致★。
- 刻の整合: commit 18:57:36/47 → 行 18:58:47 = 60〜71 秒後 ∴ 書込は commit の後に走つて居る。
- ∴ ★窓は誤つて居たが、差 2 の結びは (a)(b)(c)(d) の何れからも立つ★。前紙 §3・§5 の三値は動かぬ。

## §3 裁 ① 遠隔 ref ―― 総監督殿の fetch 済を ★讀取のみ★ で当たる (当席の fetch 0)
| 測り | 値 |
|---|---|
| 遠隔 ref (peeled 除く) | ★310★ (order59 時 277) |
| 局所 ref | ★278★ (order59 時 248)・一意 tip ★232★ |
| 遠隔 tip の内 局所 object store に ★在る★ | ★295★ |
| 同 ★無い★ | ★15★ = `refs/pull/*` 14 + `refs/heads/mac/dino-story-engine`(遠隔 tip `53b2936ec`) |
| 局所 278 ref の合併 INCLUDE (v3 31 pattern) | ★5,190★ |
| 之に 遠隔 tip 295 本を悉く足した合併 | ★5,190★ ―― ★増分 0★ |
- order59 の「17 本」の今:
  - 遠隔のみ枝 ★2 本★ (`karo-main/…lot35b-…` `karo-main/…lot39-r7-…`) は ★今 局所に在る★ (tip `158d01d31` `d1b44f24c`・遠隔と同値)。単独 INCLUDE 3,619 / 3,612 だが ★他の ref に無い path = 0 / 0★ ∴ 合併を 1 本も増やさぬ。
  - tip 差 ★2 本★ (order59 は名を記さず) → 現在の tip 差は ★1 本★ `mac/dino-story-engine` のみで、其の ★遠隔 tip の tree は今も讀めぬ★。同一物かは ★測定不能★。
  - 遠隔のみ pull の讀めぬ分 ★13 → 14★ (遠隔 pull が 123→140 に増えた為)。同一性は ★測定不能★・本数のみ。
- ★目の併記★: 本紙の合併 5,190 は ★v3 の 31 pattern を fnmatch で当てた★ 値。order59 §3 の 5,678 とは ★目が違ふ★ (差 488) ゆゑ ★直に引き算するな★。当席の 28 pattern 版では 5,172 ―― ★増分 0 は 28/31 の何れの目でも同じ★。

## §4 裁 ③ ―― ②(㋭335 の書き手)・③(先頭 `/` 27 本の書き手) は ★DB では判定不能★
- 理由 1: 現 DB の列は file_path/content/file_size/line_count/commit_hash/updated_at/created_at/content_sha256/last_snapshot_id の 9 つで、★書き手(PC・枝・器)を示す列は 1 つも無い★ (後 2 列は全 NULL)。
- 理由 2: 鍵は file_path 1 列ゆゑ、誰が書いても行は 1 本に畳まれる (前紙 order50 §1)。
- 理由 3: 先頭 `/` の 27 本は ★現 DB に 0 行★ ―― ㋒ で消えた側に在り、今は export csv の中にしか無い。
- ★唯一の路 (器・一行・実行 0)★: `grep -n -E '(23 種の短 sha を | で繋ぐ)' <各 PC の pre-push hook log> <CI #2 の run log>` ―― commit_hash × created_at を log 側の刻と突き合はせる。CI 側の器は前紙 order67 §7 の `gh run list --json status,conclusion,createdAt,headBranch`。★当席は打たぬ★。
- 之でも当たらぬ場合 (log が既に無い・PC が 4 台の外) は ★測定不能のまま★ と書く外に無い。

## §5 三値
| 事 | 三値 |
|---|---|
| SELECT が 6 行を返した事・窓の誤り 2 つ | ★現に在る★ |
| 差 2 の結び (18:58:47 の 2 行) | ★現に在る★ (四つの数へが同じ 2) |
| 16:47/16:59 の 4 行が候補である事 | ★現に無い★ (§2-c の算術) |
| 遠隔 tip 295 本を足した合併の増分 | ★現に無い★ (0 本) |
| 讀めぬ 15 本 (pull 14・mac 遠隔 tip 1) の中身 | ★測定不能★ (fetch を要す・当席は打たぬ) |
| ②③ の書き手を DB から当てる事 | ★測定不能★ (§4 の理由 3 つ) |

## §境界
DB 讀 0・書 0・SQL 実行 0・fetch/pull/clone 0・push 0・prune 0・共有 `.git` への書込動詞 0・本番 code 書込 0・secret 0・患者本文 0。
打つた git = `for-each-ref` `ls-remote` `ls-tree -r --name-only -z` `cat-file -e/-p` の 4 種 (悉く讀取)。★開示 1★: `ls-remote` は網を讀む動詞ゆゑ「局所のみ」ではない (order59 と同じ扱ひ・object は持つて來ぬ)。
★開示 2★: 04:0x の疎通確認で `> /dev/null` を ★1 度★ 打つた ―― 当席の床「shell `>` 禁」に反する。file は生れて居らぬ (device 宛) が、迂回せず記す。以後は python の subprocess で捕る。
本紙は前紙 3 本を書き換へず併記した新紙。中間 json 3 本 (`o70_refs.json` `o70_union.json` `o70_union31.json`) は同 dir に置いた。
