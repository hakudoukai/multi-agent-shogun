# 軍師second票「判定語の書式」全件census（読取のみ）— 足軽2号

- timestamp: 2026-08-06T22:35:02+09:00
- executor: ashigaru2
- task_id: current_order_8_20260806_2222_VERDICT_FORMAT_CENSUS（queue/tasks/ashigaru2.yaml）
- order_from: karo-second（msg_20260806_222350_371baf26）
- method: `queue/reports/gunshi_second_*.md` を対象に、file単位でgrep（正規表現は各節に明記）。**判定の当否は問わぬ・書式のみ**。
- 禁の順守: 監査の当否を裁かず／票の本文・patient・secretは引かず（構造欄の値語のみ引用）／票を書き換えず／新規scriptは作らず（本票のcommandは全て対話実行の使い捨て、fileには残さず）。

---

## ⒜ 母集団（★本日のみ★と★全期間★は別行・合算せず）

| scope | 対象 | 拡張子 | prefix | 件数 |
|---|---|---|---|---|
| 本日のみ | `queue/reports/` 直下、日付サフィックス `20260806` | `.md` | `gunshi_second_` | **103** |
| 全期間 | `queue/reports/` 直下、日付制限なし（実測範囲＝現存ファイルのみ、最古20260706〜最新20260806） | `.md` | `gunshi_second_` | **423** |

★令④ 実行の刻の数え直し★: 本日分＝103。★将軍second 殿実測（22:18）の 103 と一致★（母集団は食い違わず）。
※`.sha256` 付随ファイル1件（全期間側）は対象外（拡張子不一致・票本体でない）。

---

## ⒝ 判定語の書式を型で分類（件数＋代表file名。本文は引かず）

分類は file 単位・優先順位固定（上から順に最初にmatchした型へ分類、重複計上なし）:
1. **型A**=`- 判定: `PASS`` 形（行頭「判定:」＋backtick）
2. **型B**=`- verdict: PASS` 形（行頭「verdict:」英語欄・backtick/`**`装飾の有無は問わぬ）
3. **型C**=型A/型Bどちらの構造欄も持たぬが、本文中に `**PASS`/`**FAIL`/`★PASS`/`★FAIL` 等の強調記法で判定語が現れる（narrative型）
4. **型D**=上記いずれも持たぬ（構造欄なし・強調記法での判定語も検出せず）

### 本日のみ（20260806、n=103）

| 型 | 件数 | 代表file名 |
|---|---|---|
| A（判定: \`PASS\`） | 36 | `gunshi_second_26834_count_to_events_material_audit_20260806.md` |
| B（verdict: 英語欄） | 67 | `gunshi_second_00e_whitelist_application_audit_20260805.md` 系（同prefix参照可） / 本日代表＝`gunshi_second_codex_guard_wiring_design_v2_reaudit_20260806.md` |
| C（narrative強調） | 0 | （該当なし） |
| D（判定語未検出） | 0 | （該当なし） |
| 計 | 103 | — |

★将軍second 殿の「同書式を持たぬ票＝67」は★型Bを指す★と読める（型Aのみを「書式あり」とカウントした場合の残余と一致）。
★重要な訂正点★＝型Bの67件も★構造化された判定欄を持つ（`- verdict: X`）★——「書式を持たぬ」のではなく「★型Aと異なる書式★を持つ」が正確（⒞で詳述）。

### 全期間（n=423）

| 型 | 件数 | 代表file名 |
|---|---|---|
| A（判定: \`PASS\`） | 36 | `gunshi_second_26834_count_to_events_material_audit_20260806.md`（★全36件とも20260806のみ・他日付ゼロ★） |
| B（verdict: 英語欄） | 328 | `gunshi_second_verdict_go1_codex_cycle2_20260710.md` |
| C（narrative強調） | 34 | `gunshi_second_accounting_cycle3_20260707.md`（★PASS形） / `gunshi_second_audit_fki_lane_a_prep_20260721.md`（**FAIL形） |
| D（判定語未検出） | 25 | 内訳は⒟参照 |
| 計 | 423 | — |

---

## ⒞ 否の語（FAIL・CONDITIONAL・REDO等）— 件数と書式

### 本日のみ（20260806）

| 語 | 件数 | 現れた書式 | file |
|---|---|---|---|
| FAIL | **1** | 型B（`- verdict: FAIL（二者制 (Codex leg 停止中)）`） | `gunshi_second_codex_guard_wiring_design_v2_reaudit_20260806.md` |
| CONDITIONAL | 0 | — | — |
| REDO | 0 | — | — |
| PENDING/UNKNOWN | 0 | — | — |

★将軍second 殿実測「FAIL＝0」との差分★＝型A（`判定:`)欄限定でのFAIL探索なら0件で一致し得るが、★型B（`verdict:`)欄まで含めるとFAIL＝1件現存★。
※単語「FAIL」が本文中（判定欄以外・他票への言及等）に出現するfileは別途11件あるが、それらは★当該票自身の判定語ではない★ため上表には計上せず（型分類は判定欄／強調記法に限定）。

型B内訳（本日、67件の`verdict:`値・先頭token）: PASS（装飾なし）=43／PASS（二者制…付記）=23／FAIL（二者制…付記）=1。

### 全期間

| 語 | 型A | 型B | 型C | 計 |
|---|---|---|---|---|
| PASS(系) | 36 | 289 | 16（★PASS×2, **PASS×14） | 341 |
| FAIL(系) | 0 | 35 | 18（★FAIL×3, **FAIL×15） | 53 |
| REDO | 0 | 1（`gunshi_second_w70_4_bytes_route_premise_existence_audit_20260804.md`） | 0 | 1 |
| OTHER/判別不能 | 0 | 3（下記） | 0 | 3 |

型B「OTHER」3件（`verdict:`欄はあるが値がPASS/FAIL/REDOの定型token外）＝
`gunshi_second_verdict_a2_staffauth_t15_rls_20260712.md` / `gunshi_second_verdict_dentalbi_A_7commit_20260711.md` / `gunshi_second_verdict_dentalbi_BC_env_tsbatch_20260711.md`
——★値そのものは未確認（本文を引かぬ禁を優先し欄の有無のみ記録）★。

CONDITIONAL／PENDING／UNKNOWN の語は、全期間・本日いずれの判定欄・強調記法内にも検出せず＝0件。

---

## ⒟ 判らぬは判らぬまま（第四値）

- **型D 25件（全期間）の内訳**（判定欄なし・強調記法での判定語も未検出）:
  - うち16件は★本文中に無装飾のPASS/FAIL単語が存在★（代表＝`gunshi_second_verdict_t9_b2_universal_editor_20260709.md`）——判定語の有無は「判らぬ」ではなく「有るが書式が型A/B/Cのいずれとも異なる」＝★型E相当が未定義のまま残る★。
  - 残り9件は★PASS/FAIL単語が本文のどこにも見当たらず★（代表＝`gunshi_second_readgate_plan_v1.1_20260706.md`）。この9件は`gunshi_second_`prefixだが★監査票（audit verdict）ではなく別genre★（読了note・診断報告・待機キュー・restart手順等）と見受けられ申す。★これが「監査票」か否かの裁定は当職の権限外ゆえ判ぜず★。
- 型B「OTHER」3件の実値（全期間）＝未確認（上記）。
- 母集団の日付範囲は★現存fileのみの実測★——`_archive`等への退避・削除済fileの有無は本工区の射程外ゆえ判ぜず。
- 型分類の優先順位（A→B→C→D）により、複数書式を併せ持つfile（例：判定欄と強調記法の両方を持つ）は★先にmatchした型のみに計上★＝二重計上防止だが、逆に「両方持つfile が何件あるか」は本票では数えておらず判らぬ。

---

## 前工区の穴（消さず引継ぎ・current_order_6 由来）

canon命令path全件×実在判定票にて当職が自ら開けた穴 三つ（proposal 81件 未逐語／docs_other 16-17件 未個別／origin/main 断面の最新性）＝★引き続き未解消のまま残す★。
