# DentalBI 25 Form Inventory v1.0 (= 二重実装絶対防止 SoT)

- 取得日: 2026-05-09 22:47
- 取得経路: backend `/api/pdf/templates` + `/api/documents/field-map`
- 総 form 数: **25**
- 総 field 数: **1690**
- 元 JSON: `docs/dental_form_inventory/all_forms_field_map_v1.json` (1.4MB)

## 重要原則 (= 陛下御差配)
- **新規 form 作成 = 完全禁止**
- 既存 25 form の schema を SoT、抽出・連携・拡張のみ
- 監査時 1 form でも所在不明・新規重複 → FAIL
- 18b285d0 二重実装事故簿 教訓厳守

## 25 form 一覧 + field 数

| # | formType | label | fields | size |
|---|----------|-------|--------|------|
|  1 | `form1_initial` | 歯管（初回） | 65 | 210.0x297.0mm |
|  2 | `form1_continuous` | 歯管（継続） | 60 | 210.0x297.0mm |
|  3 | `form2_prosthesis` | 補管 | 13 | 210.0x297.0mm |
|  4 | `form3_hygiene` | 口腔衛生管理 | 60 | 210.0x297.0mm |
|  5 | `form4_home_care` | 在宅管理 | 109 | 210.0x297.0mm |
|  6 | `form5_visit_hygiene` | 訪衛指 | 49 | 210.0x297.0mm |
|  7 | `referral_shared` | 情共 | 27 | 210.0x297.0mm |
|  8 | `oral_func_checklist_pre` | 発不(前) | 29 | 210.0x297.0mm |
|  9 | `oral_func_checklist_post` | 発不(後) | 43 | 210.0x297.0mm |
| 10 | `oral_func_plan` | 発不計画 | 45 | 210.0x297.0mm |
| 11 | `oral_hypo_exam` | 低下症検査 | 29 | 210.0x297.0mm |
| 12 | `oral_hypo_plan` | 低下計画 | 67 | 210.0x297.0mm |
| 13 | `oral_hypo_record` | 低下記録 | 63 | 210.0x297.0mm |
| 14 | `child_oral_questionnaire` | 小児問診 | 23 | 210.0x297.0mm |
| 15 | `lab_order_crown_bridge` | 技工CB | 15 | 210.0x297.0mm |
| 16 | `lab_order_denture` | 技工義歯 | 31 | 210.0x297.0mm |
| 17 | `consent_extraction` | 抜歯同意書 | 38 | 210.0x297.0mm |
| 18 | `oral_transition_plan` | 経口移行（oral_transition_plan） | 122 | 210.0x297.0mm |
| 19 | `oral_hygiene_mgmt` | 口衛管理加算（oral_hygiene_mgmt） | 148 | 210.0x297.0mm |
| 20 | `meal_assessment` | 食事指導（meal_assessment） | 54 | 210.0x297.0mm |
| 21 | `home_care_info_dentist` | DR居宅 | 63 | 210.0x297.0mm |
| 22 | `dh_home_eval_plan` | DH居宅 | 138 | 210.0x297.0mm |
| 23 | `ichigo_sheet` | 1号用紙 | 133 | 210.0x297.0mm |
| 24 | `nigo_sheet` | 2号用紙 | 152 | 210.0x297.0mm |
| 25 | `meisai_receipt` | 明細領収 | 114 | 210.0x297.0mm |

## カテゴリ別分類 (= 推察)

### 歯科疾患管理系 (5)
- form1_initial / form1_continuous (= 歯管 初回/継続)
- form2_prosthesis (= 補管)
- form4_home_care (= 在宅管理)
- referral_shared (= 情共)

### 口腔衛生・指導系 (4)
- form3_hygiene (= 口腔衛生管理)
- form5_visit_hygiene (= 訪衛指)
- oral_hygiene_mgmt (= 口衛管理加算)
- meal_assessment (= 食事指導)

### 口腔機能発達不全症系 (3)
- oral_func_checklist_pre / post / plan (= 発不 前/後/計画)

### 口腔機能低下症系 (3)
- oral_hypo_exam / plan / record (= 低下症 検査/計画/記録)

### 在宅・移行系 (3)
- home_care_info_dentist (= DR居宅)
- dh_home_eval_plan (= DH居宅)
- oral_transition_plan (= 経口移行)

### 小児系 (1)
- child_oral_questionnaire (= 小児問診)

### 技工指示系 (2)
- lab_order_crown_bridge (= 技工CB)
- lab_order_denture (= 技工義歯)

### 同意書系 (1)
- consent_extraction (= 抜歯同意書)

### 保険医療様式 (3)
- ichigo_sheet (= 1号用紙)
- nigo_sheet (= 2号用紙)
- **meisai_receipt (= 明細領収)** ← cmd_006 a6 堀 cycle2 対象

## 主要 form の field 構造例

### meisai_receipt (= 114 fields、cmd_006 a6 堀 担当)

| field name | x_mm | y_mm | w x h |
|------------|------|------|-------|
| `patient_no` | 7 | 16 | 14.9x5mm |
| `patient_name` | 24.9 | 14.2 | 38x6mm |
| `visit_date` | 75.6 | 14.8 | 53x5mm |
| `department` | 3.1 | 29.4 | 16x4mm |
| `receipt_no` | 20.5 | 29.2 | 20.2x4mm |
| `issue_date` | 42.3 | 29.2 | 24x4mm |
| `expense_category` | 68.2 | 29.3 | 16x4mm |
| `copay_ratio` | 85.2 | 29.4 | 16x4mm |
| `honnin_kazoku` | 102.4 | 29.5 | 16x4mm |
| `insurance_kubun` | 120.1 | 29.5 | 16.1x4mm |
| `detail_00_kubun` | 16 | 41.5 | 24x4.4mm |
| `detail_00_treatment` | 42 | 41.5 | 58x4.4mm |
| `detail_00_points` | 102 | 41.5 | 16x4.4mm |
| `detail_00_count` | 120 | 41.5 | 16x4.4mm |
| `detail_01_kubun` | 16 | 45.9 | 24x4.4mm |
| `detail_01_treatment` | 42 | 45.9 | 58x4.4mm |
| `detail_01_points` | 102 | 45.9 | 16x4.4mm |
| `detail_01_count` | 120 | 45.9 | 16x4.4mm |
| `detail_02_kubun` | 16 | 50.3 | 24x4.4mm |
| `detail_02_treatment` | 42 | 50.3 | 58x4.4mm |
| `detail_02_points` | 102 | 50.3 | 16x4.4mm |
| `detail_02_count` | 120 | 50.3 | 16x4.4mm |
| `detail_03_kubun` | 16 | 54.7 | 24x4.4mm |
| `detail_03_treatment` | 42 | 54.7 | 58x4.4mm |
| `detail_03_points` | 102 | 54.7 | 16x4.4mm |
| ... | ... | ... | (+89 more = detail_NN_kubun/treatment/points/count) |

## 連携先 (= cmd_006 第二波 関連)

| ashigaru | 担当 form | field 数 |
|----------|-----------|---------|
| MainPC a6 堀秀政 | meisai_receipt | 114 |
| MainPC a1 柴田勝家 (PDF抽出) | 全 25 form 横断 | 1690 |
| MainPC a5 蒲生氏郷 (機能⑦同意) | consent_extraction | 38 |
| SecondPC a3 服部半蔵 (法令監査) | 25 form 全件の医療法準拠検証 | 1690 |
| SecondPC a4 大久保忠世 (DD-044切替) | 25 form の TSV化検討 | 1690 |

## 既存資産との関係

- backend `TEMPLATE_SPECS` (= /usr/lib/.../dentalbi/backend/api/) が単一権威源
- frontend `/pdf-editor?form=<formType>` で各 form の座標エディタ
- `/api/documents/field-map?form_type=<formType>` で field 座標取得
- `/api/coordinates/{form_type}/fields` で個別 field 取得
- `/api/documents/field-coordinates/batch` で一括取得/更新

## 拙者所見

- 25 form / 1690 field の構造完備、新規作成は無用
- 機能② カルテッド PDF抽出 = この 25 form の field schema を逆引き
- DD-044 TSV化 = この 25 form を TSV column と mapping
- 法令監査 = 25 form 全件の COPPA/医療法/個情法準拠評価
