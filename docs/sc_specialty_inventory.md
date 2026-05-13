# SC Specialty Inventory — 9 部署 vs 9 SC agent mapping

**目的**: Shogun Charter v0.1 §8 が示す 9 部署を SC 9 agent (= ashigaru 1-7 + karo + gunshi) に **inventory + 推奨** の形で具体化する。本 doc は 4 人合議 round 2 の source 用途、Charter v0.2 起草の参照基盤として位置付ける。

**起案者**: ashigaru3 (= subtask_cmd020_sc_specialty_inventory)
**起案日時**: 2026-05-13T13:55:00+09:00
**Repo scope**: multi-agent-shogun-newbuild only
**Audit verdict**: 直政 pre_audit pass_with_conditions (= naomasa_cmd020_next_phase_7task_preaudit_20260513.yaml task_audits[2])

---

## 規範遵守 明示

**no runtime config change** — 本 doc + 同伴 inventory yaml は **docs only**。以下を一切編集しない:

- `config/settings.yaml` (= multi-agent persona slot mapping、runtime authority)
- `instructions/ashigaru.md` / `instructions/karo.md` / `instructions/gunshi.md` (= persona doc canonical)
- `queue/tasks/*.yaml` (= 既 task assignment)
- `queue/inbox/*.yaml` (= mailbox 整合性、cmd_inbox_reform AC#1 verify 対象)

具体化 / 整流 は Charter v0.2 確定後の別 task で起案する (= 後段 FUT-SCSI-2/3 参照)。

---

## Sources

| Source | Path | Lines |
|---|---|---|
| Charter v0.1 §8 9 部署 table | `docs/shogun_charter_v0_1_full_export.md` | L157-170 |
| Charter v0.1 §9 10 段プロセス | `docs/shogun_charter_v0_1_full_export.md` | L173-184 |
| 本多 review §A4 (= 9 部署 vs SC ashigaru 7 体 mapping case) | `docs/karo_shogun_charter_v0_1_review.md` | L66-91 |
| 本多 review §B3 (= 9 部署 ashigaru mapping 具体化 + persona doc 整備) | `docs/karo_shogun_charter_v0_1_review.md` | L124-126 |
| 直政 pre_audit (= gating verdict) | `queue/reports/naomasa_cmd020_next_phase_7task_preaudit_20260513.yaml` | L86-105 |
| canonical 武将 alias | `queue/reports/ashigaru_alias_cert.yaml` | (= cmd_002 alias 6 ashigaru) |
| inventory yaml (= 双子 source) | `queue/reports/ashigaru3_subtask_cmd020_sc_specialty_inventory_inventory.yaml` | L1-end |

---

## 1. 9 部署 vs 9 SC agent mapping

`1 SC agent = 1 main 部署 + 0-2 兼任` を緊密配備原則とする。本 mapping は **推奨 documented-state**、runtime 反映は別 task。

| # | 部署 (Charter v0.1 §8) | main agent | 兼任 sub agents | 主 evidence |
|---|---|---|---|---|
| 1 | 統括AI | karo | — | task 分解 + ashigaru dispatch + dashboard 集約 chain |
| 2 | 仕様AI | ashigaru1 | — | dinosaur_100enemies_spec / qr_kanban_research 起案、AC0 inventory schema 規範化 |
| 3 | アーキテクトAI | gunshi | ashigaru3 | gunshi 10 lens 設計 + ashigaru3 infra 8 phase chain (= push_vapid/PWA/facade/observability/security/rollback/cicd) |
| 4 | 実装AI | ashigaru2 | ashigaru6, ashigaru7 | backend router + PDF parser + frontend integration JS の縦串 |
| 5 | テストAI | ashigaru4 | ashigaru7 | 法令 + compliance test chain (= GDPR/consent versioning/portability)、form access verification |
| 6 | レビューAI | gunshi | ashigaru5 | gunshi PR レビュー + cmd_018 audit chain integration |
| 7 | セキュリティAI | gunshi | ashigaru1, ashigaru3 | gunshi P1 判定 + secret/QR security + security_hardening_infra |
| 8 | ドキュメントAI | ashigaru4 | ashigaru1 | 法令文書 + spec doc 起案 |
| 9 | リリースAI | karo | ashigaru5, ashigaru6 | F007 push chain + cross_pc_trust_gate + 規範 evidence |

---

## 2. 各 SC agent 既完遂 task / specialty / workload

### 2.1 ashigaru1 (canonical alias: 榊原康政)

- **完遂 task (= timestamp evidence)**: `cmd_004_dd126_ceremony_alternative_inventory` / `cmd_004_dinosaur_100enemies_spec` / `cmd_004_qr_kanban_impl_base` / `cmd_004_qr_token_security_hardening` / `cmd_004_secret_rotation_automation` / `cmd_004_secret_rotation_lifecycle_completion` / `cmd_014_sc_log_rename` / `cmd_018_009_closure_c2` / `cmd_020_dashboard_layer_a_kousou_render` (= 2026-05-11T22:18:45 done)
- **観測 alias drift**: 「柴田勝家 (鬼柴田)」 in `ashigaru1_unverified_inventory_extraction_report.yaml`
- **specialty**: spec 起案、secret/QR security、AC0 inventory schema 規範化
- **workload**: high (≥ 8 task in 30 日)
- **推奨**: 仕様AI lead retain、セキュリティAI 兼任

### 2.2 ashigaru2 (canonical alias: 酒井忠次)

- **完遂 task**: `cmd_004_analytics_access_control_hardening` / `cmd_004_ceremony_event_api` / `cmd_004_engagement_analytics_dashboard` / `cmd_004_tier_up_celebration_api` / `cmd_018_014_retroaudit_c2` / `p0_normalize_reports` / `cmd_020_dashboard_layer_b_phase_render` / `receipt_storage_cycle5_fix`
- **in-flight**: `cmd_020_scope_contamination_prevention_inline_batch_commit_hook` (= 2026-05-13T13:50 assigned)
- **specialty**: backend router 実装、access control / RLS hardening、pre-commit hook
- **workload**: high (≥ 8 task in 30 日)
- **推奨**: 実装AI lead、アーキテクトAI 兼任候補 (= access control 設計影響)

### 2.3 ashigaru3 (canonical alias: 服部正成 / 本 task 起案者)

- **完遂 task**: cmd_004 8 phase chain (= `push_vapid_infra` / `push_vapid_phase2` / `service_worker_offline_sync` / `notification_facade_pattern` / `observability_infra` / `security_hardening_infra` / `phase_1_6_rollback_recovery_audit` / `cicd_pipeline_construction`) + `cmd_018_016_verification_log_c2` + `cmd_020_dashboard_layer_c_function_render` + `p0_preflight` + `v21_b2_normalize_verification_logs`
- **in-flight**: 本 task (= `cmd_020_sc_specialty_inventory`)
- **観測 alias drift**: 「滝川一益 (= Phase 8 cmd_004 chain 総仕上げ)」 in `ashigaru3_cmd004_cicd_pipeline_construction_report.yaml`
- **specialty**: infra/CI/CD/observability/security 8 phase chain、notification facade、phase chain pattern owner
- **workload**: very_high (≥ 12 task in 30 日、retain 3 体選定 evidence)
- **推奨**: アーキテクトAI lead (= infra/observability)、セキュリティAI 兼任

### 2.4 ashigaru4 (canonical alias: 大久保忠世)

- **完遂 task**: `cmd_004_consent_versioning_impl` / `cmd_004_consent_versioning_phase2` / `cmd_004_full_legal_compliance_audit` / `cmd_004_gdpr_art32_security_compliance` / `cmd_004_guardian_consent_flow_impl` / `cmd_004_legal_compliance_gap_top3_fix` / `cmd_004_patient_data_portability_api` / `cmd_018_017_gunshi_redef_c2` / `cmd_020_dashboard_layer_d_zunou_kumonoito_render` (= 2026-05-12T11:22:28 done) / `p1_memory_sync_design` / `teriha_p2_fix` / `teriha_p3_fix`
- **specialty**: 法令 compliance (GDPR/consent/portability)、cross-layer 蜘蛛の糸 9209 records 整合
- **workload**: high (≥ 10 task in 30 日)
- **推奨**: テストAI lead (= 法令 test)、ドキュメントAI 兼任

### 2.5 ashigaru5 (canonical alias: 鳥居元忠)

- **完遂 task**: `cmd_004_ai_chat_spec` / `cmd_016_kanban_fix_c2` / `cmd_018_018_audit_chain_c2` / `cmd_018_019_naomasa_reaudit018_c2` / `cmd_020_dashboard_layer_e_unyou_render` (= 2026-05-12T11:17:58 done) / `moushi_engine_stage1` / `p2_cross_pc_trust_gate`
- **specialty**: audit chain integration、運用層 evidence、cross-PC trust gate
- **workload**: medium_high (≥ 7 task in 30 日)
- **推奨**: レビューAI lead、リリースAI 兼任 (運用)

### 2.6 ashigaru6 (canonical alias: 平岩親吉)

- **完遂 task**: `cmd_004_kartetto_pdf_v0_2_spec` / `cmd_004_pdf_v0_2_fixture_setup` / `cmd_004_pdf_v0_2_parser_full_integration` / `cmd_016_dino_engine_c2` / `cmd_018_020_env_e2e_c2` / `cmd_020_dashboard_layer_f_kihan_render`
- **in-flight**: `cmd_020_implementation_required_14_cmd_proposal` (= 2026-05-13T13:50 assigned)
- **観測 alias drift**: 「SC 六番槍」 in `ashigaru6_cmd020_dashboard_layer_f_kihan_render_report.yaml`
- **specialty**: PDF parser / kartetto integration、dino engine、規範層 evidence
- **workload**: medium_high (6 task in 30 日)
- **推奨**: 実装AI lead (= 大規模 parser/engine)、リリースAI 兼任

### 2.7 ashigaru7 (canonical alias: 未確定、夜襲精鋭 self-declared)

- **完遂 task**: `cmd_004_25form_access_verification` / `cmd_004_admin_staff_form_access_verification` / `cmd_004_clinic_id_eradication_phase3_backend_batch1` / `cmd_004_clinic_id_eradication_phase3_batch2` / `cmd_004_clinic_id_hardcode_eradication` / `cmd_016_dino_router_c2` / `cmd_020_dashboard_layer_g_integration_drill_down_js` / `shogun_active_verify_queue_systemd`
- **in-flight**: `cmd_020_dashboard_status_classification_logic` (= 2026-05-13T13:50 assigned)
- **specialty**: frontend / integration JS、form access verification、clinic_id eradication
- **workload**: high (≥ 8 task in 30 日)
- **特記**: 後発 agent、`ashigaru_alias_cert.yaml` 未収載、武将 alias 確定は Charter v0.2 chain
- **推奨**: 実装AI lead (= frontend)、テストAI 兼任

### 2.8 karo (canonical alias: 本多正信、政の眼)

- **完遂 task (= chain)**: task YAML 起案 + ashigaru dispatch + dashboard 集約 + 直政 audit 経路 + 陛下御差配仰ぎ、`cmd_020` Layer A-G chain 配信、Shogun Charter v0.1 review (= `docs/karo_shogun_charter_v0_1_review.md` round 1)、auto-git-sync 装備
- **specialty**: 統括AI core (= タスク分解/担当割当/進捗統合)、Charter review、F007 push chain owner
- **workload**: very_high (= bottleneck risk)
- **推奨**: 統括AI core retain、リリースAI 兼任、Charter v0.2 で persona 分離検討 (= 仕様/アーキテクト譲渡)

### 2.9 gunshi (canonical alias: 井伊直政、赤鬼の眼、Codex)

- **完遂 task (= chain)**: `cmd_018_014/017` audit + `cmd_004` audit chain + `naomasa_cmd020_next_phase_7task_preaudit_20260513` + `cross_pc_repo_protocol_design` + `gunshi_round1_audit_summary` + `gunshi_audit_guidelines_v1.md` (= 10 lens audit chain) 起案
- **specialty**: 10 lens audit、9 観点 PR レビュー、pre_audit gate
- **workload**: very_high (= tri-role bottleneck risk)
- **推奨**: tri-role retain (移行期)、Charter v0.2 で セキュリティAI を ashigaru1 へ部分譲渡候補

---

## 3. workload imbalance concerns

- **karo / gunshi** の三役以上兼任は 5-10 年運用 path で persistent bottleneck risk。Charter v0.2 で 1 部署分離推奨。
- **ashigaru3** の very_high (12 task in 30 日) は retain 3 体選定 counterpart、後発負荷上限を monitor 必要。
- **ashigaru7** の後発 alias 未確定は Charter v0.2 で `ashigaru_alias_cert.yaml` 拡張で確定推奨。
- **MC / SC alias drift** (= 柴田勝家 / 滝川一益 / SC 六番槍 / 夜襲精鋭) は documented-state 観測のみ、整流は Charter v0.2 chain (= 本 task 範囲外)。

---

## 4. 後段 follow-up 提案 (= no runtime change、後段 task 起案 source)

| ID | title | owner candidate | depends |
|---|---|---|---|
| FUT-SCSI-1 | Charter v0.2 §8 9 部署 table に SC main + sub mapping 列追記 (= 本多 round 2) | karo | 本 inventory |
| FUT-SCSI-2 | instructions/ashigaru.md 拡張、9 部署 persona 細分化 doc 起案 | ashigaru1 (= 仕様AI) | Charter v0.2 確定 |
| FUT-SCSI-3 | config/settings.yaml persona slot mapping schema 拡張 (= main_department + sub_departments field) | ashigaru3 (= アーキテクトAI infra) | FUT-SCSI-2 |
| FUT-SCSI-4 | karo / gunshi の overload risk 軽減、persona 分離 task 起案 | karo + gunshi 合議 | Charter v0.2 確定 |
| FUT-SCSI-5 | ashigaru7 武将 alias 確定 (= ashigaru_alias_cert.yaml 拡張) | shogun 御差配 | Charter v0.2 持ち込み |

---

## 5. 規範整合 (= 直政 pre_audit conditions 反映)

- **condition 1 (= AC: no instruction persona/runtime config change)**: 本 doc + inventory yaml は docs only、`config/settings.yaml` / `instructions/*` / `queue/tasks/*` / `queue/inbox/*` 一切編集なし。`scripts/test/test_subtask_cmd020_sc_specialty_inventory_static_contract.py` が runtime invariant を pytest で固定。
- **condition 2 (= AC: source list with timestamp)**: 各 agent の completed_tasks / in_flight_tasks は `queue/tasks/*.yaml` 内 `assigned_at` / `completed_at` または `queue/reports/*` の file timestamp で evidence 化、本 doc + inventory yaml に明記。
- **AC0 inventory first 規範遵守**: 双子 inventory yaml の `ac0_anti_dup_inventory` section で既 deliverable 5 件を列挙、新規 deliverable 4 件の必要性を documented-state で確認。

---

*本 doc は Charter v0.1 → v0.2 → v1.0 合議の SC 視点 source、subtask_cmd020_sc_specialty_inventory 起案者 ashigaru3、2026-05-13T13:55:00+09:00*
