# 申し送り 確定UI v0.3 — 3層分離 最終1案 (handoff-ui-finalization)

- 指令: command_queue `bb0e7ed8-54db-484e-961f-f105f5a0eb3c`「第2次: 申し送りUI確定」/ operation_id: handoff-ui-finalization
- 前段: `docs/moushi_engine_converged_design_v0.2.md`（SCローカル・**未commit/未push**・sha256:8857c587…・100行・6232B = 大将軍が未確認だった理由）
- author: 直政 (naomasa / SC・git=ashigaru2) / bloom: L2（UI確定、実装は別task / push前 陛下御差配）
- 報告経路: `python3 -m daishogun.commander`（WSL interop非依存・正常稼働）

---

## 0. 確定方針（1案に確定）

大将軍推奨の **3層分離** を採用確定。各層は独立route/component/stateで疎結合（申し送りA4設計§1「カンバンと申し送りは別機能」絶対ルールを全層に拡張）。

| 層 | 役割 | 実体（実装済を流用） |
|----|------|----------------------|
| **L1 患者CRM「温かい記憶」** | 患者の人となり・思い出・気配りを蓄積 | `frontend/src/pages/PatientCrm/PatientCrmPage.tsx` + `components/CrmTimeline.tsx` + `hooks/useCrmData.ts` + `crmTheme.ts` + `features/crm/useCrmSpeechInput.ts`。docs: CRM-1(自由記入+音声→Claude構造化), E-4a(患者総合情報ボード, `patient_note_stamps`/`disease_episodes`既存) |
| **L2 申し送りカンバン「実務管理」** | 来院フロー6列ワークフロー管理 | `handover_notes` v3 `workflow_status`/`is_writing`/`remote_request`、`/kanban` KanbanPage、Sidebar申し送り・カンバン |
| **L3 iPad横向きクイックセット入力** | 高速セット入力（記録の本体） | `HandoverSelectPage`→`HandoverHomePage`(App.tsx L222-223) + `handover_sheets` API |

## 1. v2/v3/v5 差分（確定）

| 版 | 差分 | 証拠 |
|----|------|------|
| 骨格(StepO base) | handover_notes/handover_archives/daily_report_lines 3テーブル + `/api/handover` CRUD + Sidebar登録 | StepO L1-16, L670 |
| **v3** | handover_notes へ **カンバン列**(workflow_status/is_writing/remote_request)・**自費カード種別**(card_type/self_pay_info_json)・**難易度**(difficulty) を追加 | StepO L61/69/73 = `backend/db/sqlite_init.py` L258-269（実装一致確認済） |
| v4〜v5系 | 引継ぎ通番(`DentalBI_引き継ぎ_*_v4..v27` / `handover_v29..v42`)でUI改善を反映: v34=iPad横向き最優先, v35=SOAP/P欄処置セット, v39=統一原則 | `docs/DentalBI/handover/` |

→ 確定: **v3 schema を DB SoT**、v34/v35 を UI規範、v0.2収束(handover_sheets=構造化SoT)を L3 に継承。

## 2. 画面構成（ワイヤー）

```
┌─ サイドバー: [患者CRM] [申し送り] [カンバン] ────────────────────────┐
│                                                                      │
│  L3 申し送り画面  /handover-sheet/:patientId  (iPad 横向き 2ペイン)   │
│  ┌───────────────── 左: クイックセット入力 ──┬── 右: A4プレビュー ──┐ │
│  │ 部位選択                                  │  [印刷レイアウト]    │ │
│  │  → S欄(音声+自由記述)                     │   申し送り書類       │ │
│  │  → O欄(カテゴリ別5段階ボタン)             │   そのまま印刷可     │ │
│  │  → A欄(AI推定病名→Dr確定)                 │                     │ │
│  │  → P欄: 病名タップ→処置セット候補展開 ★   │                     │ │
│  │  → 確定                                   │                     │ │
│  │  よく使うパターン (最下部)                │                     │ │
│  └───────────────────────────────────────────┴─────────────────────┘ │
│  ※モード切替は /settings へ集約・通常画面にタブ無し（v34 §6）        │
│                                                                      │
│  L2 /kanban : 6列ワークフロー(到着→…→会計) カード=handover_notes      │
│  L1 /patient-crm : CrmTimeline 温かい記憶（音声走り書き→Claude構造化） │
└──────────────────────────────────────────────────────────────────────┘
```
- ボタンはiPad横向きスペース効率でコンパクト化、病名パネルは通常非表示。

## 3. 主要操作フロー

1. **L3 記録**: 患者選択(HandoverSelectPage)→HandoverHomePage→部位→S(音声)→O(5段階)→A(AI→Dr確定)→P(病名タップ=処置セット ワンタップ展開, billing_rules由来)→確定→`handover_sheets` 保存→右ペインA4即時反映。
2. **L2 管理**: 確定 handover_notes が `workflow_status` でカンバン6列を遷移（到着/記入中/リモート依頼/変更あり等）。
3. **L1 記憶**: スタッフが走り書き/音声でCRM入力→Claude API巡回(CRM-2)で構造化→CrmTimelineに「温かい記憶」として蓄積、次回来院時に参照。

## 4. DB / API 接続

| 層 | API | テーブル |
|----|-----|----------|
| L3 | `backend/api/handover_sheets.py`(構造化SoT, treatmentsサブ) ＋ `handover.py`(下書きCRUD) | `handover_notes`(v3) / `handover_archives` |
| L3セット | billing_rules 駆動 → `treatment_blocks_json` | `backend/db/migrations/014_seed_billing_rules.sql`(spt_transition/p_exam_2nd/srp_after_sc/sealant/fluoride/denture_adjust) |
| L2 | `/api/handover` LIST + workflow status PATCH | `handover_notes.workflow_status` |
| L1 | CRM-1/CRM-2 (音声→Claude構造化) | `patient_note_stamps`(既存10件) / `disease_episodes` |

- 新規テーブル禁（Anti-Duplication / E-4a §0-B 5禁止準拠）、clinic_id ハードコード禁（ClinicIdContext注入）。

## 5. 未実装リスト

| # | 項目 | 状態 |
|---|------|------|
| U-1 | HandoverHomePage の iPad横向き2ペイン化（右A4プレビュー同時表示） | 未（L3画面/API/型は実在、2ペインレイアウト未） |
| U-2 | P欄 病名タップ→処置セット展開UI（billing_rules結線） | 未実装 |
| U-3 | L1↔L3 連携（CRM記憶を申し送り入力時にサジェスト） | 未設計 |
| U-4 | handover vs handover_sheets endpoint差分の正式統合判定 | 未決（推奨: sheets=SoT） |
| U-5 | 「小西化」逐語定義（院別プリセット匿名化方針） | 未確証（handover_v30-42精読要） |
| U-6 | tablet device仕様(iPad/Android)確定 | 未決（信長round2裁可待ち） |

## 6. 次の実装タスク（Stage2提案）

1. **T1**: `HandoverHomePage.tsx` を iPad横向き2ペイン化（左ステップ/右A4プレビュー）+ ボタンコンパクト化・病名パネル非表示・レイアウト順(v34§6)。
2. **T2**: P欄に `<TreatmentSetPicker>` 追加、`014_seed_billing_rules.sql` 由来候補を病名タップで展開→`treatment_blocks_json`。
3. **T3**: L1 CRM サジェスト連携（useCrmData→申し送り入力補助）。
4. **T4**: handover/handover_sheets endpoint差分監査→統合（U-4）。
- 各T: ashigaru 1名/0.5-1日、bloom L3、push前 陛下御差配。

## 7. 未決事項（大将軍へ・指揮系統厳守）

- U-4(API統合) 推奨案=**handover_sheets を SoT**（理由: treatmentsサブリソース保有・A4書類要件整合）。低リスクのため本案で進行、覆す場合のみ大将軍指示要。
- U-5/U-6 は調査・設計継続中（停止せず）。INFRA: PowerShell系は不全だが python commander 経路で回避済（WSL interop自体は要復旧、足軽範囲外→大将軍上申済）。

---

*確定UI v0.3 起案: 直政、2026-05-17 (command bb0e7ed8 / operation handoff-ui-finalization)*
