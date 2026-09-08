# order193 ―― 現に隠して居る 24 単位 / 試験 31 本 を顕在化した記

## §零 頭 ―― 家老が「紙の頭に書け」と命じた一句

> ★『飛んで居た』のでなく ★飛ぶ先が無かつた★★

**飾りが言ふ的 18 の内、★現に無い 16★・★現に在る 2★**（`SheetHeader.tsx` ／ `backend/services/teriha_passport_engine.py`）。
かつ **phase5 の 11 本は ★body=Pass★**（試験の中身が現に無い）。
∴ 之等の飾りの多くは「動く試験を隠して居た」のではなく、**当てる先の物が現に無い所に立つて居た**。
但し ★現に在る 2★ が在るゆゑ「悉く飛ぶ先が無かつた」とは書かぬ。

## §一 何時・何を・幾つ讀んだか（作法 七条目）

- 便 3 通（`msg_20260908_184307_4dc17f78` 令／`…184842…` 走の許し／`…185118…` 一発目受理）。悉く既読へ倒した。
- 的の樹 `/home/hakudoukai/a3/wt-bundle-fix4` の .py **1,484 枚**（除外＝node_modules / .git / .venv / venv / __pycache__ / .pytest\*）。
- 内、飾りを持つ **24 単位**を全て開き、その飾りが言ふ的 **18 path** の在否を己の目で測つた。
- 直した file **6 枚**、走 **2 発**（`--collect-only` のみ）。

## §二 樹と HEAD / tree

- 樹 = `/home/hakudoukai/a3/wt-bundle-fix4`（己の席の樹）。**git を一度も打たぬ**（床の急報 = /mnt/c I/O error・共有 .git を触らぬ）。
- ∴ **HEAD / tree は測定不能**。以下の印は悉く **作業樹の実 file の sha256 頭16**（釘83）。

## §三 直す前の実測（器 = 己の規）

| 箱 | 単位 | 覆ふ試験 |
|---|---|---|
| B 無条件 skip（飾り・pytestmark） | 23 | 31 |
| H collect_ignore | 1 | 0 |
| **計** | **24** | **31** |

的の在否 = 18 中 **現に無い 16 / 現に在る 2**。phase5 11 本は body が `Pass` のみ。

## §四 振り分け ―― 24 単位を三箱へ（一つも余さず）

| 箱 | 単位 | 試験 |
|---|---|---|
| ㋺ 本物の移植（条件を器に測らせる形へ） | 12 | 20 |
| ㋩ 出来ぬ（理由を一本づつ §六） | 12 | 11 |
| ㋑ 理由付き importorskip | 0 | 0 |
| **計** | **24** | **31** |

㋑ が 0 で在る理由 ―― 24 単位の何れも「取込が出来ぬ」形ではなかつた（欠けて居るのは **module ではなく .tsx / .py の実体、又は試験本体**）。∴ `importorskip` は当たる先を持たぬ。

## §五 ㋺ 移植の中身（12 単位 / 20 本）

飾りの**文言は一字も削らず**、其の後ろに条件を足した形へ移した。人が書いた註を **器が毎度測る式**に替へたゆゑ、的が戻れば試験も自ら起きる。

| # | file:行 | 覆ふ本数 | 移した後の条件 |
|---|---|---|---|
| 1 | tests/test_step_r_ui.py:282 | 1 | `EmptyState.tsx` の在否 |
| 2 | tests/test_step_a4_handover_sheet.py:377 | 1 | `useSheetPagination.ts` の在否 |
| 3 | tests/test_step_q.py:461 | 1 | `useBillingRules.ts` の在否 |
| 4 | tests/test_step_s3.py:664 | 1 | `CheckoutModal.tsx` の在否 |
| 5 | tests/test_step_s3.py:678 | 1 | `ComplaintForm.tsx` の在否 |
| 6 | tests/test_step_s3.py:692 | 1 | 同上 |
| 7 | tests/test_step_s3.py:703 | 1 | `ProductivitySection.tsx` の在否 |
| 8 | tests/test_step_s3.py:715 | 1 | 同上 |
| 9 | tests/test_step_s3.py:726 | 1 | 同上 |
| 10 | tests/test_step_s4.py:742→753 | 2 | **`SheetHeader.tsx` の中に `assignedDr` が在るか**（file は現に在る） |
| 11 | tests/test_step_s4.py:758→769 | 2 | `SheetPrintView.tsx` の在否 |
| 12 | backend/tests/test_cmd004_cross_cutting_integration.py:24 | 7 | **未作成 2 file**（`services/consent_gate.py` ／ `services/notifications/facade.py`）が揃つたか |

★#10 は他と形が違ふ★ ―― `SheetHeader.tsx` は **現に在る**。飾りの言ふ事は「file が無い」ではなく「担当Dr/DH の入力が右ペインへ移つた」であつた。∴ file の在否で測れば試験は起きて落ちる。己で中を測ると `assignedDr` **現に無い**・`assignedDh` **現に無い**・`status` **現に在る**。ゆゑに条件を **`assignedDr` の在否**に置いた（読取専用 helper `_has_text` を 1 個挿した。file が無ければ False を返し、収集時に例外を投げぬ）。

★#12 の的 7 の内 `teriha_passport_engine.py` は現に在る★。ゆゑに「試験ごとに其の的で測る」形にはせず、飾りの文言が名指す **未作成 2 file** で module 全体を測る形に留めた（試験ごとに割れば、的の在る 1 本のみが起きて中身の照合に掛かる ―― 之は走 0 では測れぬ）。

## §六 ㋩ 出来ぬ ―― 一本づつの理由

**共通の三つ**（悉くに掛かる）: ㋐ body が `Pass` のみ ∴ 移すべき中身が現に無い（顕在化ではなく **新たに書く**事に成る） ㋑ 書けば `pg_cursor` 経由の DB 接触が要る＝総監督 GO 288377 ⑴（本番 DB / 本番 API 不触・書込 0）に触れる ㋒ 走 0 で確かめられぬ。

| # | file:行 | 試験の名 | 飾りが言ふ数（**写した数・己では確かめて居らぬ**） | 之に足りぬ物 |
|---|---|---|---|---|
| 1 | phase5/test_5a_immutable.py:33 | …table_update_blocked | 残28件（各表 UPDATE+DELETE=14×2） | 14 表への UPDATE 阻止の実行と確認 |
| 2 | phase5/test_5a_immutable.py:40 | …table_delete_blocked | 残14件 | 14 表への DELETE 阻止の実行と確認 |
| 3 | phase5/test_5b_column.py:46 | …partial_immutable_combinations | 残18件（4本×5−上記2件） | 列単位の可否の組合せ |
| 4 | phase5/test_5c_archive_delete.py:24 | …archive_delete_all_52_tables_blocked | 残51件 | 52 表の archive 削除阻止 |
| 5 | phase5/test_5d_pii_gated_view.py:19 | …pii_archive_all_31_combinations | 残61件（31本×2−1） | PII 経路の 31 組 |
| 6 | phase5/test_5e_violation_log.py:28 | …violation_log_update_truncate_blocked | 残2件 | 記録表の自己防護 2 形 |
| 7 | phase5/test_5f_override.py:30 | …override_begin_end_full_lifecycle | 残8件 | 開始/終了/二重/冪等の 8 形 |
| 8 | phase5/test_5g_schema_guard.py:19 | …event_trigger_combinations | 残4件 | CREATE/DROP/非保護 ALTER の 4 形 |
| 9 | phase5/test_phase_a_continuity.py:10 | …continuity_clinic_scope | 全9件 | 越境阻止の 9 形 |
| 10 | phase5/test_v21d_self_patch.py:22 | …memory_sync_ack_update_works | 残2件 | ack 更新の 2 形 |
| 11 | phase5/test_v21d_self_patch.py:28 | …full_generated_column_inventory | （数の言及なし） | 対象表の GENERATED 列の棚卸し |

飾りの言ふ数の和 = **197 件（10 行ぶん）**。★之は写した数であり、己では確かめて居らぬ★。器が数へた **11 本**とは母数が違ふゆゑ **足し引きせぬ**。

**十二単位目（試験 0 本）**: `tests/conftest.py:1` `collect_ignore_glob = ["fixtures/*"]`。的の `tests/fixtures/` は .py 2 枚・`def test` **0** ∴ 之が現に落として居る試験は **現に無い**。振る先を持たぬゆゑ出来ぬ箱に置いた（「隠して居る量が零」であつて「隠す力が無い」の意ではない ―― 後で試験が置かれれば落ち得る）。

## §七 走 2 発の raw

| 発 | 何時 | 器 | rc | 収集 | 収集 error |
|---|---|---|---|---|---|
| 一 | 直す前 | `python3 -m pytest --collect-only -q -p no:cacheprovider <6 file>` | 0 | **216** | **0** |
| 二 | 直した後 | 同（一字も変へず・條 o174） | 0 | **216** | **0** |

床 = `PYTHONDONTWRITEBYTECODE=1`・`-p no:cacheprovider` ∴ 樹への書込 0。DB / 本番 API / 8001 / 5174 に触れて居らぬ。body は一つも走らせて居らぬ。
★境★ ―― `--collect-only` は飾りを外さぬ。**216 は総数であり、隠れて居る本数ではない**。之が前後で動かぬ事が「収集の形が変はつて居らぬ」の証であり、試験の当落を言ふ数ではない。

## §八 新旧併記（同じ器・一字も変へず二度測つた・條 百九十七）

| 数 | 直す前 | 直した後 | 差 |
|---|---|---|---|
| 現に隠して居る 単位 | 24 | **12** | **−12** |
| 現に隠して居る 試験本数 | 31 | **11** | **−20** |
| 飾りが言ふ的 18 の在否 | 在 2 / 無 16 | 在 2 / 無 16 | 0（触れて居らぬ） |
| 収集本数 | 216 | 216 | 0 |
| 収集 error | 0 | 0 | 0 |

**残る 11 本は悉く phase5**（body=Pass）であり、§六 に一本づつ理由を書いた。

## §九 触れた file（作業樹の実 file・sha256 頭16）

| file | sha16（直した後） | wc | split | byte |
|---|---|---|---|---|
| tests/test_step_r_ui.py | 75d1ef72622d3a24 | 314 | 315 | 12,471 |
| tests/test_step_a4_handover_sheet.py | a5a0716d943b72aa | 563 | 564 | 21,354 |
| tests/test_step_q.py | 140b46d474f8e42e | 494 | 495 | 18,452 |
| tests/test_step_s3.py | 9c38c4dc0e218dd0 | 752 | 753 | 26,788 |
| tests/test_step_s4.py | 669ee12d62868e6a | 1,459 | 1,460 | 60,735 |
| backend/tests/test_cmd004_cross_cutting_integration.py | 15a602e4ddd0836b | 116 | 117 | 5,146 |

★直す前の sha を取つて居らぬ★ ∴ **前後の印の併記は測定不能**（自訴・§十二）。製品 code には一字も書いて居らぬ（触れたは試験 file 6 枚のみ）。

## §十 隠し得る 107 行（手を触れて居らぬ）

order192 で数へた **A / C / D / G 計 107 行 / file 56** には ★一字も触れて居らぬ★。
之等は条件が床（env・依存の在否・実行時の分岐）で決まる ∴ **走 0 では測定不能**である。
★「隠して居らぬ」とは書かぬ★。言へるは下限のみ。

## §十一 見込みと外れ（作法 四条目㋓）

1. 見込み「的は悉く現に無い筈」→ **外れ**（2 は現に在る）。向き = 過小に見積る側。
2. 見込み「skipif 化で収集本数は動かぬ」→ **当たり**（216 → 216）。但し之は `--collect-only` の定めから導ける ∴ **器の証としては弱い**。
3. 見込み「phase5 は中身が在る筈」→ **外れ**（11 本悉く body=Pass）。向き = 中身を多く見積る側。

★二つが同じ向き（己は「在る」側へ寄せて見積る）★ ―― 條(o179-a) に照らせば **一度の運ではなく偏り**として数へる。

## §十二 自訴

1. 直す前の file の sha を取らずに直した ∴ §九 の前後併記が測定不能に成つた。次に紙を直す弾が在れば、先に印を取る。
2. `_has_text` helper を 1 個 **挿した**（s4）。之は「置換のみ」の定めの外である ∴ 挿入器を置換器と **別の script** に分けて当てた（床(28)）。
3. #10 の条件を `assignedDr` 一語に置いた。之は己が選んだ一語であり、書き手が「担当Dr/DH」と書いた二語の内の片方である。`assignedDh` でも `status` でもよい所を一語に決めた ―― **選んだのは己**である。
4. §六 の「足りぬ物」の欄は、飾りの文言から読み取つた **己の言ひ換へ**であり、DD-128 の正本に当たつて確かめては居らぬ。

## §十三 繰越

1. #12 を試験ごとの条件へ割る（的の在る `teriha_passport_engine.py` 1 本のみが起きる ―― 走が要る）。
2. #10 の条件語を `assignedDr` から「右ペインに移つた事」を測る形へ寄せる（`SheetRightPanel.tsx` の中を測る）。
3. phase5 11 本を「試験の姿をした予定表」として別の帳へ移すか否か ―― 之は席の裁を超える。
4. 隠し得る 107 行の内、C 20 行の条件が何の床を見て居るかを形で分ける（order192 §十一 の繰越）。
5. 飾りの言ふ 197 件を己の手で数へ直す。

## §十四 /tmp の置き物（本手番の産に非ず・消して居らぬ）

| 名 | 刻 | 大きさ | sha16 |
|---|---|---|---|
| /tmp/a3-tree.txt | 09:46:12 | 3,183 B | 103ae1650945d18f |
| /tmp/a31_respawn_cmd.txt | 前日 21:15:02 | 318 B | 425e5b00bde28e4b |

## §十五 器（規）

| 器 | sha16 | wc | 註 |
|---|---|---|---|
| order193_escape_surface_fix_v1.rule.py（数を出す前・第一段） | 48fd97f32915db1d | 49 | 定めのみ |
| order193_apply_v1.py（置換器・11 単位） | 20a25ba4f77efdd8 | 31 | 置換のみ |

**判定は軍師third に仰ぐ**（己では判定語を書かぬ）。三択語で結ぶ ―― 現に隠して居る単位は **24 から 12 へ**、覆はれた試験は **31 本から 11 本へ**。残る 11 本は **出来ぬ**（理由は §六 に一本づつ）。107 行は **測定不能**。

as_of: 2026-09-08T18:54:31+09:00
