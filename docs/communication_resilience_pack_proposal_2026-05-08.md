# cmd_communication_resilience_pack_001 — 報連相崩壊 構造的解決提案

> **Status**: 信長提案、理事長殿明示直命 2026-05-08 16:00「これらの原因と解決方法をシステムを提案して」
> **Drafted by**: 信長 (織田信長) 2026-05-08 16:05 JST
> **背景**: 本朝の報連相崩壊 8 件問題に対する統合解決提案、家康並行 audit (= docs/ieyasu_communication_breakdown_audit_2026-05-08.md) 結果と統合予定

## 0. 結論
報連相崩壊 8 件の問題は既起案 cmd 群 + 新規 4 cmd で構造的解決可能。3 段階で実装、本日 Stage 1 + 5/9-10 Stage 2 + 火曜 cycle2 Stage 3。

## 1. 8 問題 × 解決マッピング
(本 turn 信長報告参照)

## 2. 既起案 cmd への mapping
- 本多 Reform A (cmd_control_plane_reset_admission_001) → #5
- 本多 Reform B (cmd_registry_transport_integrity_001) → #1
- 大なた Phase B (SecondPC watchdog) → #3
- 真田 cmd_secondpc_state_reconciliation_001 (進行中) → #2

## 3. 新規 4 cmd 候補
- cmd_yaml_schema_validation_001 → #4 (maeda_report 破損防止)
- cmd_inbox_write_contract_test_001 → #6 (content vs field 乖離)
- cmd_codex_send_keys_safety_001 → #7 (信長 send-keys 連発禁止)
- cmd_alert_dedup_escalation_001 → #8 (activity_monitor dedup)

## 4. 実装段階
### Stage 1 (= 本日中)
- #1 修復済 (commit 2f4b960)
- #2 真田進行中
- #7 信長 memory 永続化 (= 本 turn 即実装)
- #8 alert dedup 簡易 patch (= 後続)

### Stage 2 (= 5/9-10)
- #3 大なた Phase B (ashigaru7)
- #4 + #6 ashigaru2 cycle3+ 候補

### Stage 3 (= 火曜 cycle2)
- #5 本多 Reform A (真田 dispatch)
- #1 本多 Reform B 完成 (cycle2 で全 hardcode 排除)

## 5. 期限 + PDCA
- max cycle 5
- 全件火曜 01:00 (= cycle2 期限) までに完遂目標

## 6. 三者監査
家康 + 服部半蔵 (Phase 5 後) + 黒田 (議長、Phase 5 後)、移行期は家康 + 本多 retrospective

## 7. 関連
- docs/honda_recommendations_2026-05-08.md (= 本多諮問)
- docs/honda_phase16_3_retrospective_audit_2026-05-08.md
- docs/honda_initial_proposals_2026-05-08.md
- docs/honda_audit_lane_status_design_2026-05-08.md
- docs/honda_secondpc_inefficiency_retrospective_2026-05-08.md
- docs/honda_validation_implementation_flow_2026-05-08.md
- docs/cmd_root_resolution_001_draft.md (= 大なた)
- docs/ieyasu_communication_breakdown_audit_2026-05-08.md (= 家康調査、別途起案中)

---
*提案完: 信長 (織田信長) — 2026-05-08 16:05 JST、家康調査結果統合後 v2 起案予定*
