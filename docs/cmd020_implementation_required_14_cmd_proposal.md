# cmd_020 implementation_required 14 件 新 cmd 上申準備提案 v0.1

起案: 平岩親吉 (= ashigaru6、SC 六番槍)、2026-05-13T15:00+09:00
task_ref: subtask_cmd020_implementation_required_14_cmd_proposal
parent_cmd: cmd_020
design_doc 正本:
- queue/reports/naomasa_sc_audit_phase2_status_green_path_20260512.yaml (= 14 candidate canonical source)
- docs/shogun_orchestration_charter_v0.1.md §15 (= 1 Issue = 1 Branch = 1 PR)
- queue/reports/unverified_inventory_20260512.yaml (= 14 candidate evidence)
直政 pre_audit: msg_20260513_134905、pass_with_concerns、findings medium 2 件 acknowledge 済

---

## 0. 本提案の性質と境界

本書は **docs/report ONLY の上申提案**であり、以下を厳禁とする (= 直政 pre_audit finding medium 1 整合):

- queue/tasks/ 配下の新 task YAML 起案
- Supabase development_progress / design_tasks の status edit
- queue/inbox/ 配下への task_assigned 発信
- ashigaru 配分の runtime 反映 (= 上申案として記載のみ)

**out-of-scope 境界** (= 直政 pre_audit finding medium 2 整合):

- **C-15-B7** (= W9 batch7 alert residual 14 item): 別 green path (= manifest publication + impl + audit)、本書で混入禁
- **C-V29-W11DDA** + **C-V30-W11DDB** (= W11 in_progress): monitor 経路、impl task 不要

本書 14 件は **C-V21/V22/V31/V33/V34/V35/V36/V37/V38/V39/V41/V42/V43/V44** のみを扱う。

実配信は家康殿経由本多殿御差配 + 直政 post_audit chain で実施。

---

## 1. 統合分類と推奨上申単位

14 件を **Charter v0.1 §15.4 (= 1 Issue = 1 Branch = 1 PR)** 基本単位整合下、以下の cmd 単位で上申推奨:

| 推奨 cmd | 包含 candidate | 上申単位の理由 | 着手優先度 |
|---|---|---|---|
| **cmd_021** W9 算定エンジン完遂 | C-V21, C-V22 | 蜘蛛の糸 169 件 manifest 配下、batch 単位で 5-7 ashigaru 並列実施想定。最大規模、独立 cmd 化必須 | A (= 早期着手) |
| **cmd_022** W11 朝礼フル版 | C-V31 | Phase1-4 独立、UI/AI/録画 stack 複合、単独 cmd 妥当 | B |
| **cmd_023** W12 臨床ナレッジ UI | C-V33 | DB schema + UI + AI 連携、単独 cmd 妥当 | B |
| **cmd_024** W13 訪問業務完遂 | C-V34, C-V35 | Phase4-7 + 経路最適化、訪問業務一体上申 | B |
| **cmd_025** W14 外部接続 batch | C-V36, C-V37, C-V38 | ペイライト + CTI + LINE/Web 予約、外部 API 接続群、PCI DSS + 電気通信事業法令整合で同期上申 | A |
| **cmd_026** W14 書式 Lv3 + 唾液検査 | C-V39 | 書式 + 検査 + 通知、単独 cmd 妥当 (= dental_form_inventory 既存統合) | C |
| **cmd_027** W15 deploy 準備 | C-V41, C-V42 | runbook + manual + Tailscale + 実データテスト、deploy 一体上申 | A (= go-live 前提) |
| **cmd_028** W16 材料管理 | C-V43 | QR + OCR + CV + 数理消費量、QR kanban spec 既存統合 | C |
| **cmd_029** W17 人事 + 全院展開 | C-V44 | 最終 phase、人事 + DTF + rollout 統合、最大規模 | C (= 後段) |

**合計 9 cmd 上申、14 candidate を完全 cover、out-of-scope (= C-15-B7 / V29 / V30) 混入なし。**

---

## 2. 各 cmd 提案 (= acceptance_criteria + target_file + test plan + ashigaru 配分案 + bloom level)

### 2.1 cmd_021 W9 算定エンジン完遂 (= C-V21-W9TENSU + C-V22-W9SPIDCHK)

#### (a) acceptance_criteria

- AC0: 既実装 inventory yaml (= queue/manifests/w9_design_tasks_169.yaml 168 件 status + 既存 backend/services/teriha_passport_engine.py 等の現状調査)
- AC1: design_tasks 169 件 batch1-7 全 ID coverage matrix 起案
- AC2: 算定 engine 多層構造実装 (= prerequisite_rules / 病名 ↔ 処置 / セット算定 / 50% 増し / 通則 / 加算 chain)
- AC3: R8 (= 2026 改定保険) 施行前検算 logic (= C-V21) 実装
- AC4: 蜘蛛の糸 算定チェック + バリデーション (= C-V22) 実装
- AC5: unit test 全件 PASS (= 169 design_task 各々に対応 test、SKIP=0)
- AC6: integration test (= 副院長判定の三点照合 cc20258b session_minutes 完全再現)
- AC7: 黒田監査 + 直政監査 pass + 兄上監査 chain 完遂
- AC8: 5-10 年運用想定下の改定対応 path 文書化 (= R9 / R10 改定向け extension point)

#### (b) target_file + spec doc reference

- target: `backend/services/teriha_passport_engine.py` (拡張) + 新規 `backend/services/billing_calculation_engine.py`
- spec doc: `docs/cmd021_w9_billing_engine_full_design.md` (新規起案)
- source-of-truth: `queue/manifests/w9_design_tasks_169.yaml` + session_minutes cc20258b

#### (c) test plan

- unit: `backend/tests/test_billing_calculation_engine.py` (= 169 design_task 各々の prerequisite + 処置/病名 + セット + 50% 増し + 通則 + 加算 each test)
- integration: `tests/integration/test_w9_three_point_match.py` (= 副院長判定再現)
- regression: 既存 `tests/test_regenerate_dashboard.py` Stage A baseline retain
- SKIP=0 必須

#### (d) ashigaru 配分案

- batch1 (算定チェック 42 件): ashigaru1 + ashigaru2
- batch2 (validation 30 件): ashigaru3
- batch3 (R8 改定 31 件): ashigaru4
- batch4 (加算 28 件): ashigaru5
- batch5 (病名 chain 18 件): ashigaru6
- batch6 (通則 20 件): ashigaru7
- batch7 alert residual 14 件: **本 cmd 範囲外 (= C-15-B7、別 cmd で扱う)**
- 直政 (gunshi) audit / 黒田 mainpc audit + 信長兄上監査 chain

#### (e) bloom level

- **L5** (= 169 design_task 並列 impl、最大規模、複数 ashigaru chain、5-10 年運用 R8/R9/R10 改定対応 extension)

---

### 2.2 cmd_022 W11 朝礼フル版 Phase1-4 (= C-V31-W11CHOREI)

#### (a) acceptance_criteria

- AC0: 既存 W11 phase_a/b inventory + 朝礼関連既存 artifact 調査
- AC1: Phase1 (= 出席記録) impl + test
- AC2: Phase2 (= 議事 progress 共有) impl + test
- AC3: Phase3 (= WebRTC 録画) impl + test (= 法令: 電気通信事業 / 個人情報 / 録音同意)
- AC4: Phase4 (= AI 議事録 + アクション抽出) impl + test
- AC5: UI/UX 統合 (= staff scheduling + 通知)
- AC6: privacy + security test (= 録画 access control)
- AC7: 黒田監査 + 直政監査 + 兄上監査 pass
- AC8: 5-10 年運用下の WebRTC provider 切替 path 文書化

#### (b) target_file + spec doc reference

- target: 新規 `backend/routers/morning_meeting.py` + `frontend/src/features/morning-meeting/`
- spec doc: `docs/cmd022_w11_morning_meeting_full_design.md` (新規起案)
- 法令 reference: `docs/cmd004_gdpr_art32_security_compliance.md` (整合)

#### (c) test plan

- unit: backend router + service 各々
- integration: WebRTC stub test + AI 議事録 生成 test (= LLM mock)
- e2e: 家老担当 (= 全エージェント操作権限要)
- privacy: 録画 access control + 削除 path test
- SKIP=0 必須

#### (d) ashigaru 配分案

- Phase1: ashigaru2 (= 既 ceremony_event experience)
- Phase2: ashigaru4 (= 既 morning sync experience)
- Phase3: ashigaru5 (= WebRTC / 録画 stack 新規)
- Phase4: ashigaru6 (= AI 議事録 LLM 連携)
- 直政 (gunshi) audit + 家老 e2e

#### (e) bloom level

- **L4** (= 4 phase 連続、UI/AI/録画/法令 4 軸複合)

---

### 2.3 cmd_023 W12 臨床ナレッジ UI (= C-V33-W12CLNUI)

#### (a) acceptance_criteria

- AC0: 既存 ナレッジ artifact (= grep 結果 0 件) + 関連 cmd_004 spec doc 棚卸
- AC1: ナレッジ DB schema 設計 (= category + tagging + version + access)
- AC2: 編集 UI impl + WYSIWYG + 画像/動画 attach
- AC3: 検索 UI impl + 全文検索 (= meilisearch / typesense 等)
- AC4: AI 要約 + tagging 自動 (= LLM 連携)
- AC5: access control (= 院長 / 副院長 / 衛生士 / 受付 等の role)
- AC6: privacy + audit log (= 編集履歴 retain)
- AC7: 黒田監査 + 直政監査 + 兄上監査 pass
- AC8: 5-10 年運用下の DB migration + 検索 engine 切替 path 文書化

#### (b) target_file + spec doc reference

- target: 新規 `backend/routers/clinical_knowledge.py` + `frontend/src/features/clinical-knowledge/`
- spec doc: `docs/cmd023_w12_clinical_knowledge_ui_design.md` (新規起案)

#### (c) test plan

- unit: schema + router + service
- integration: 検索 engine test + LLM 要約 mock test
- privacy: access control role 別 test
- SKIP=0 必須

#### (d) ashigaru 配分案

- schema + backend: ashigaru1
- 編集 UI: ashigaru2
- 検索 UI: ashigaru3
- AI 要約: ashigaru6
- access control: ashigaru7
- 直政 (gunshi) audit

#### (e) bloom level

- **L4** (= schema + UI + AI + access、4 軸複合)

---

### 2.4 cmd_024 W13 訪問業務完遂 (= C-V34-W13VISIT + C-V35-W13RTE)

#### (a) acceptance_criteria

- AC0: 既存 訪問関連 artifact 棚卸 + Phase1-3 状態確認
- AC1: Phase4 (= 訪問記録) impl + test
- AC2: Phase5 (= 訪問計画) impl + test
- AC3: Phase6 (= 帳票) impl + test (= 介護保険 / 訪問診療 法令)
- AC4: Phase7 (= 報告 / 集計) impl + test
- AC5: 訪問ルート最適化 (= C-V35) impl + test (= TSP/VRP + 実時間 traffic)
- AC6: map provider 選定 + 患者宅 geocoding + privacy (= 住所 PII)
- AC7: 黒田監査 + 直政監査 + 兄上監査 pass
- AC8: 5-10 年運用下の map provider 切替 + 法令改正対応 path 文書化

#### (b) target_file + spec doc reference

- target: 新規 `backend/routers/visit.py` + `backend/services/visit_route_optimizer.py` + `frontend/src/features/visit/`
- spec doc: `docs/cmd024_w13_visit_full_design.md` (新規起案)
- 法令 reference: 介護保険法 + 訪問診療 算定要件

#### (c) test plan

- unit: backend service + 経路最適化 algorithm 単体 test (= 既知ベンチマーク TSP)
- integration: map provider mock test + 訪問記録 e2e
- privacy: 住所 PII access control
- SKIP=0 必須

#### (d) ashigaru 配分案

- Phase4-5: ashigaru2 + ashigaru3
- Phase6-7: ashigaru4 + ashigaru5
- 経路最適化: ashigaru6 (= 数理最適化 + 外部 API)
- map provider 統合: ashigaru1
- 直政 (gunshi) audit

#### (e) bloom level

- **L4** (= 4 phase + 数理最適化 + 外部 API + 法令、5 軸複合)

---

### 2.5 cmd_025 W14 外部接続 batch (= C-V36-W14PAY + C-V37-W14CTI + C-V38-W14LINE)

#### (a) acceptance_criteria

- AC0: 既存 決済 / CTI / LINE / Web 予約 artifact 棚卸
- AC1: ペイライト 実 API 接続 (= C-V36) impl + PCI DSS 整合 + tokenization + webhook + reconciliation
- AC2: VALTEC MOT/TEL CTI 接続 (= C-V37) impl + 発信者番号 + 患者紐付け + 録音 + 法令 (= 電気通信事業)
- AC3: LINE 通知 + Web 予約 (= C-V38) impl + Messaging API + 改正電気通信事業法整合
- AC4: 外部 API 統合 facade 化 (= 共通 retry / circuit-breaker / observability)
- AC5: secret 管理 + rotation (= 既 cmd004_secret_rotation chain 整合)
- AC6: privacy + security test (= 全外部接続 endpoint)
- AC7: 黒田監査 + 直政監査 + 兄上監査 pass + security review skill 経由
- AC8: 5-10 年運用下の provider 切替 + 法令改正対応 path 文書化

#### (b) target_file + spec doc reference

- target: 新規 `backend/integrations/paylight/` + `backend/integrations/cti_valtec/` + `backend/integrations/line/`
- spec doc: `docs/cmd025_w14_external_integration_batch_design.md` (新規起案)
- 法令 reference: PCI DSS + 電気通信事業法 + 改正電気通信事業法

#### (c) test plan

- unit: 各 integration adapter
- integration: provider sandbox test (= ペイライト / VALTEC / LINE 各々)
- security: secret rotation + token scope test
- privacy: PII flow test
- SKIP=0 必須

#### (d) ashigaru 配分案

- ペイライト: ashigaru1 (= 既 qr_token / secret_rotation experience)
- CTI: ashigaru4 (= 既 SC inbox routing experience)
- LINE/Web 予約: ashigaru2 (= 既 ceremony_event API experience)
- facade 化: ashigaru7
- security review: 黒田 + 直政 + 信長兄上

#### (e) bloom level

- **L4** (= 3 外部 API + 法令 PCI DSS + 電気通信事業 + facade、5 軸複合)

---

### 2.6 cmd_026 W14 書式 Lv3 + 唾液検査 (= C-V39-W14YOSHI3)

#### (a) acceptance_criteria

- AC0: dental_form_inventory 既存 inventory + 唾液検査 artifact 棚卸
- AC1: 書式 Lv3 (= 既 inventory 整合) impl + test
- AC2: 唾液検査 spec 起案 + impl
- AC3: 検査機器 import path (= CSV / API)
- AC4: 結果 通知 (= 患者 + dr) chain
- AC5: privacy + 検査結果 PII
- AC6: 黒田監査 + 直政監査 + 兄上監査 pass
- AC7: 5-10 年運用下の検査機器 provider 切替 path

#### (b) target_file + spec doc reference

- target: 既存 dental_form_inventory 統合 + 新規 `backend/services/saliva_inspection.py`
- spec doc: `docs/cmd026_w14_form_lv3_saliva_inspection_design.md` (新規起案)

#### (c) test plan

- unit: 書式 + 検査結果 import
- integration: 機器 mock test
- privacy: 結果 access control
- SKIP=0 必須

#### (d) ashigaru 配分案

- 書式 Lv3: ashigaru3 (= 既 form_inventory experience)
- 唾液検査 spec: ashigaru6
- impl: ashigaru4
- 直政 (gunshi) audit

#### (e) bloom level

- **L4** (= 書式 + 検査 + 通知、3 軸複合)

---

### 2.7 cmd_027 W15 deploy 準備 (= C-V41-W15DEP + C-V42-W15MAN)

#### (a) acceptance_criteria

- AC0: 既存 deploy artifact + Tailscale + manual 関連棚卸
- AC1: deploy runbook 起案 (= production / staging / dr 環境)
- AC2: 実データテスト (= GDPR + 改正個人情報保護法 整合) plan
- AC3: Tailscale VPN 構成 + ACL + audit log
- AC4: 操作マニュアル (= スタッフ役職別 + 業務別 + 緊急時) 起案
- AC5: 画面 capture + 動画 chain
- AC6: 黒田監査 + 直政監査 + 兄上監査 pass
- AC7: 5-10 年運用下の マニュアル更新 cadence + version 管理

#### (b) target_file + spec doc reference

- target: 新規 `docs/deploy_runbook.md` + `docs/operation_manual/` (= 役職別 + 業務別) + `infrastructure/tailscale/`
- spec doc: `docs/cmd027_w15_deploy_preparation_design.md` (新規起案)

#### (c) test plan

- runbook scenario test (= staging で deploy 全段実行)
- 実データテスト privacy compliance check
- Tailscale ACL test
- マニュアル comprehension test (= スタッフ役職別 sample read)
- SKIP=0 必須

#### (d) ashigaru 配分案

- runbook: ashigaru1
- 実データテスト: 家老 (= e2e 担当)
- Tailscale: ashigaru4 (= infra)
- マニュアル: ashigaru5 + ashigaru6 + ashigaru7 (= 役職別 分担)
- 直政 (gunshi) audit + 家老 e2e

#### (e) bloom level

- **L3** (= 文書 + scenario + infra、文書中心)

---

### 2.8 cmd_028 W16 材料管理 (= C-V43-W16MAT)

#### (a) acceptance_criteria

- AC0: QR kanban spec 既存 (= docs/cmd004_qr_kanban_spec.md) + 材料管理 artifact 棚卸
- AC1: QR スキャン (= QR kanban 既存統合) + 在庫 reflect
- AC2: 納品 OCR (= 発注書 / 納品書 OCR) impl
- AC3: 棚 AI (= 棚 image → 在庫推定 computer vision) impl
- AC4: 理論消費量 (= treatment-set 連動 = cmd_021 整合) impl
- AC5: 発注自動化 + 承認 flow
- AC6: 黒田監査 + 直政監査 + 兄上監査 pass
- AC7: 5-10 年運用下の OCR / CV model 切替 path

#### (b) target_file + spec doc reference

- target: 既存 QR kanban 拡張 + 新規 `backend/services/materials_management.py` + `backend/services/inventory_cv.py`
- spec doc: `docs/cmd028_w16_materials_management_design.md` (新規起案)

#### (c) test plan

- unit: QR + OCR + CV + 数理消費量 各々
- integration: 発注 → 納品 → 在庫 reflect e2e
- accuracy baseline: OCR / CV 精度測定 (= cmd_004_kartetto_pdf_v0_2 規範整合)
- SKIP=0 必須

#### (d) ashigaru 配分案

- QR 統合: ashigaru1 (= 既 QR experience)
- OCR: ashigaru6 (= 既 cmd_004 PDF v0.2 parser experience)
- CV: ashigaru4 (= 新規 CV 実装)
- 数理消費量: ashigaru3 (= cmd_021 連動)
- 発注 flow: ashigaru2
- 直政 (gunshi) audit

#### (e) bloom level

- **L4** (= QR + OCR + CV + 数理、4 軸複合)

---

### 2.9 cmd_029 W17 人事 + 全院展開 (= C-V44-W17JINJI)

#### (a) acceptance_criteria

- AC0: 既存 人事 / 勤怠 / 給与 artifact 棚卸 + DTF adapter 仕様調査
- AC1: 勤怠管理 impl + test
- AC2: 給与計算 impl + test (= 労務法令)
- AC3: 評価 + 1on1 + キャリア impl
- AC4: DTF adapter (= Dental Treatment Form? 仕様確認後 impl)
- AC5: 全院展開 (= 多院 multi-tenant + 院別 customization)
- AC6: privacy + 給与情報 access control + audit log
- AC7: 黒田監査 + 直政監査 + 兄上監査 pass + security review
- AC8: 5-10 年運用下の 労務法令改正 + 院数拡大 path 文書化

#### (b) target_file + spec doc reference

- target: 新規 `backend/routers/hr.py` + `backend/services/payroll.py` + `backend/integrations/dtf/`
- spec doc: `docs/cmd029_w17_hr_dtf_rollout_design.md` (新規起案)
- 法令 reference: 労働基準法 + 社会保険 + 個人情報保護

#### (c) test plan

- unit: 勤怠 + 給与 計算 各々
- integration: DTF adapter mock test
- multi-tenant: 院別 customization isolation test
- privacy: 給与 access control role 別 test
- SKIP=0 必須

#### (d) ashigaru 配分案

- 勤怠: ashigaru2
- 給与: ashigaru3 (= 数理 + 法令)
- 評価 + 1on1: ashigaru5
- DTF adapter: ashigaru4
- multi-tenant: ashigaru1 + ashigaru7
- security review: 黒田 + 直政 + 信長兄上

#### (e) bloom level

- **L5** (= 人事 stack + 法令 + 多院 multi-tenant + DTF、最大規模 cmd)

---

## 3. 全体配分 summary (= 提案上申案)

| ashigaru | 主担当 cmd | 副担当 cmd |
|---|---|---|
| ashigaru1 | cmd_023 schema, cmd_025 ペイライト, cmd_027 runbook | cmd_021 batch1, cmd_028 QR, cmd_029 multi-tenant |
| ashigaru2 | cmd_022 Phase1, cmd_025 LINE, cmd_028 発注 | cmd_021 batch1, cmd_023 編集 UI, cmd_024 Phase4-5, cmd_029 勤怠 |
| ashigaru3 | cmd_023 検索 UI, cmd_026 書式 Lv3, cmd_028 数理消費量 | cmd_021 batch2, cmd_024 Phase4-5, cmd_029 給与 |
| ashigaru4 | cmd_022 Phase2, cmd_025 CTI, cmd_028 CV, cmd_029 DTF | cmd_021 batch3, cmd_024 Phase6-7, cmd_026 impl, cmd_027 Tailscale |
| ashigaru5 | cmd_022 Phase3 (= WebRTC) | cmd_021 batch4, cmd_024 Phase6-7, cmd_027 マニュアル, cmd_029 評価 |
| ashigaru6 | cmd_021 batch5 (= 病名), cmd_022 Phase4 (= AI 議事録), cmd_023 AI 要約, cmd_024 経路最適化, cmd_026 唾液, cmd_028 OCR | cmd_027 マニュアル |
| ashigaru7 | cmd_021 batch6 (= 通則), cmd_023 access control, cmd_025 facade | cmd_027 マニュアル, cmd_029 multi-tenant |
| gunshi (直政) | 全 cmd post_audit | - |
| karo (本多忠勝) | 全 cmd dispatch + 結果集約 | - |
| shogun (信長殿) | 全 cmd 最終監査 | - |

**負荷観察**: ashigaru6 主担当 6 件 (= 既 cmd_004 PDF v0.2 parser + 既 cmd_020 Layer F 経験から AI / OCR / 数理 stack 寄せ)、ashigaru1/4 主担当 3 件、他 2-3 件。post_audit 段で本多殿による再配分余地あり。

---

## 4. 着手 sequence 推奨 (= dependency 整合下)

```
phase_1 (= 早期着手):
  - cmd_021 (= 算定 engine、go-live 前提)
  - cmd_025 (= 外部接続、PCI DSS + 電気通信事業)
  - cmd_027 (= deploy 準備、go-live 前提)

phase_2 (= phase_1 後):
  - cmd_022 (= 朝礼)
  - cmd_023 (= 臨床ナレッジ)
  - cmd_024 (= 訪問業務)

phase_3 (= phase_2 後):
  - cmd_026 (= 書式 + 唾液)
  - cmd_028 (= 材料管理、cmd_021 数理消費量連動)
  - cmd_029 (= 人事 + 全院展開、最終 phase)
```

各 phase 内は並走可能、phase 間は dependency (= cmd_021 数理消費量 → cmd_028 / cmd_027 go-live → cmd_026/028/029) 整合下で sequential。

---

## 5. 既知の限界 + 後段対応

- **本書は上申提案のみ**: queue/tasks/ 新規 task YAML 起案は本書範囲外、家康殿経由本多殿御差配 + 直政 post_audit 後に発番
- **Supabase status は不変**: 本書実装後も development_progress / design_tasks 全 14 row の status は本 task で edit せず、各 cmd 完遂時 (= karo + naomasa post_audit chain) で更新
- **C-15-B7 boundary 厳守**: 本書 14 件と W9 batch7 alert residual 14 item は別 cmd (= 既 manifest chain 整合) で扱う
- **W11 monitor 経路尊重**: C-V29-W11DDA / C-V30-W11DDB は本書範囲外、naomasa monitor_proposal 経路で完遂 trigger 後 post_audit
- **bloom level estimate**: 各 cmd の bloom_level は本書時点 estimate、各 cmd AC0 inventory 段で final 化想定
- **5-10 年運用想定**: 各 cmd AC8 (= 法令改正 + provider 切替 + 院数拡大 path 文書化) で根本治療原則整合

---

## 6. 起案完了基準 (= 本書自己評価)

- ✅ 14 candidate 全件 cover (= C-V21〜V22 + V31 + V33〜V39 + V41〜V44 計 14 件)
- ✅ out-of-scope boundary 明示 (= C-15-B7 / V29 / V30 別経路明記)
- ✅ docs/report ONLY 性質明示 (= queue mutation / Supabase edit / inbox 発信 全件禁)
- ✅ 9 cmd 単位 (= Charter v0.1 §15.4 1 Issue = 1 Branch = 1 PR 整合)
- ✅ 各 cmd に (a) acceptance_criteria (b) target_file + spec doc reference (c) test plan (d) ashigaru 配分案 (e) bloom level 全件記載
- ✅ 着手 sequence + dependency 整合
- ✅ 全体配分 summary (= 上申後 home 配分提案)

直政 pre_audit findings medium 2 件全件 acknowledge 済、各 §で明示記載。

---

*v0.1 起案: 平岩親吉 (= ashigaru6、SC 六番槍)、2026-05-13T15:00+09:00、朝駆け 直政 pre_audit pass 配信下、家康 13:42 加速 query 整合、新規範下 Sonnet → Codex 監査 path*
