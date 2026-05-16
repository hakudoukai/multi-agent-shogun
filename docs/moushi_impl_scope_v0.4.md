# 申し送り 実装範囲確定 v0.4 (handoff-implementation-scope / command 2bd64f20)

- author: 直政 (naomasa / SC・git=ashigaru2) / 2026-05-17 / bloom: L2→L3着手準備
- 前提: 3層構成確定 (L1患者CRM温かい記憶 / L2カンバン実務管理 / L3 iPad横向きクイックセット入力)
- 報告経路: `python3 -m daishogun.commander`

## 0. 監査由来の重要修正（自己申告の懐疑的再検証）

v0.3 は「HandoverHomePage を iPad横向き2ペイン化（新規）」と記したが、独立検証で**2ペイン構造は既に実装済**と判明:
`frontend/src/features/handover-sheet/` に **`SheetLeftPanel.tsx` / `SheetRightPanel.tsx`** + `SheetView.tsx` `SheetHeader.tsx` `TreatmentBlockCard.tsx` `DocumentLinkBar.tsx` `print.css` `__tests__/` が既存。
→ **実装増分は「2ペイン新規構築」ではなく「(a) iPad横向きレスポンシブ最適化 + (b) P欄 処置セットPicker追加」に縮小**。これが本範囲確定の核心訂正。

## 1. 実装範囲表

| 範囲 | 内容 | リスク | 着手順 |
|------|------|--------|--------|
| **S-1 最初に実装** | P欄 処置セットPicker（病名タップ→billing_rules候補→treatment_blocks_json）。新規 additive component `<TreatmentSetPicker>`、既存に非破壊で差込 | 低（追加のみ） | 第1 |
| **S-2** | SheetLeftPanel/RightPanel の iPad横向きレスポンシブCSS最適化（print.css/レイアウト幅）。既存DOM構造維持、style調整のみ | 低〜中 | 第2 |
| **S-3** | v34 §6 UI規範反映（ボタンコンパクト化・病名パネル通常非表示・レイアウト順） | 中（既存UX変更） | 第3（要モック承認） |
| **触らない** | handover_notes/handover_sheets schema、`/api/handover*` 既存endpoint、L1患者CRM、L2カンバン workflow_status、SheetView の保存ロジック、ClinicIdContext | — | 不変 |
| **v2/v3/v5 から残す部品** | `SheetLeftPanel/SheetRightPanel/SheetView/TreatmentBlockCard/DocumentLinkBar`(handover-sheet)、`TreatmentPlanV2Tab`、`CounselingTab`、`PerioChartModal`、handover_notes v3列(workflow_status/card_type/difficulty) | — | 全て再利用・改変最小 |

## 2. 対象ファイル

| 操作 | ファイル |
|------|----------|
| 新規(additive) | `frontend/src/features/handover-sheet/TreatmentSetPicker.tsx`（S-1、未配線スタブから） |
| 新規 | `frontend/src/features/handover-sheet/__tests__/TreatmentSetPicker.test.tsx`（S-1テスト） |
| 改変(style限定) | `frontend/src/features/handover-sheet/SheetLeftPanel.tsx` / `SheetRightPanel.tsx` / `print.css`（S-2） |
| 参照のみ | `backend/db/migrations/014_seed_billing_rules.sql`（Picker候補源）, `backend/api/handover_sheets.py`（保存先） |
| 不変 | `backend/db/sqlite_init.py`, `frontend/src/App.tsx`, L1 PatientCrm/* |

## 3. 既存機能との接続方針

- Picker は `handover_sheets` の treatments サブリソース API へ既存経路で結線（新規endpoint作らない）。
- 候補データ: `014_seed_billing_rules.sql`（spt_transition/p_exam_2nd/srp_after_sc/sealant/fluoride/denture_adjust）を読取専用参照。
- clinic_id は `useClinicId()`（HandoverHomePage既使用）から注入、ハードコード禁。
- L2カンバンとは workflow_status を介してのみ疎結合（Picker は status を変更しない）。

## 4. テスト設計

| ID | 種別 | 対象 | 既存資産 |
|----|------|------|----------|
| T-U1 | frontend unit | `TreatmentSetPicker` 病名タップ→候補表示→選択→onChange | 新規 `handover-sheet/__tests__/` に追加（既存__tests__に並置） |
| T-U2 | frontend unit | レスポンシブ: 横向き幅で左右ペイン分割維持 | SheetView既存testを拡張 |
| T-B1 | backend pytest | treatment_blocks_json への保存整合 | `backend/tests/test_soap_handover_sync.py` を拡張 |
| T-I1 | integration | Picker→handover_sheets保存→再取得一致 | `cn11-handover-integration.test.tsx` 流用 |
| 規範 | SKIP=0 必須（Test Rules 1）。preflight: 製品repo `master` 3e1ca969、frontend/backend test基盤稼働確認後に実行 | | |

## 5. 未決事項

- M-1: S-3（既存UX変更）はモックアップ承認ゲート要 → 推奨: S-1/S-2 先行、S-3はモック後。理由: 既存運用画面の破壊回避（低リスク優先指示に整合）。
- M-2: 小西化(U-5) 逐語定義 未確証（handover_v30-42精読要、本範囲外で並行調査継続）。
- M-3: tablet device仕様(iPad/Android)未決（S-2のbreakpoint値に影響、暫定 iPad 1024×768 横向き基準で進行）。

## 6. 次30分作業

1. 設計doc群(v0.2/v0.3/v0.4 + 監査報告)を SC multi-agent repo に **local commit**（監査C-1解消、F007=push のみ制限・commit可、push せず）。
2. `TreatmentSetPicker.tsx` 未配線スタブ + テスト雛形を additive 作成（既存画面非破壊）。
3. gunshi 品質チェック依頼 → karo 報告（push は陛下御差配）。

---

*実装範囲確定 v0.4: 直政、2026-05-17 (command 2bd64f20 / operation handoff-implementation-scope)*
