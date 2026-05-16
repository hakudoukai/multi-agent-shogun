# 申し送りエンジン 収束設計 v0.2 (= v2/v3/v5 + iPad横向きセット入力案 統合・最終収束)

- 指令: command_queue 544e244f-75f0-48ef-9a1c-2fe793abb706 / 前段 94355af3 (operation_id: handoff-board)
- mission: 「申し送り v2/v3/v5 と iPad横向きセット入力案を整理し、最終設計へ収束させる」
- author: 直政 (naomasa / SC・git=ashigaru2)
- 起案: 2026-05-16
- bloom: L2 設計収束のみ (実装commitは Stage2/3 別task、push前は陛下御差配)
- 報告経路: PowerShell worker 不全 (operation_order未対応 + WSL interop死) のため Supabase MCP 直結 fallback
- base 正本: 製品 DentalBI (`/mnt/c/Projects/hakudokai-dev/`) を一次正本、multi-agent側 moushi_engine_ui_design_v0.1 を UX入力

---

## 0. 結論 (収束決定)

**handover_sheets API を構造化 SoT に採用し、handover_notes(v3 schema) を下書き/カンバン連携層とする。**
理由: handover_sheets は treatments サブリソースを持ち構造化度が高く、「申し送り＝A4印刷書類」要件 (申し送りA4用紙設計 §1 絶対ルール) に整合。新規テーブル並立を回避 (Anti-Duplication)。

---

## 1. バージョン系譜の整理 (= v2/v3/v5)

| 版 | 実体 | 証拠 |
|----|------|------|
| 骨格 (StepO) | handover_notes/archives/lines 3テーブル + `/api/handover` CRUD + サイドバー登録 | `StepO_申し送りフォーム骨格_指示文_20260212.md` |
| **v3** | handover_notes に「カンバン列(workflow_status/is_writing/remote_request)」「自費カード種別(card_type/self_pay_info_json)」「難易度(difficulty)」追加 | `backend/db/sqlite_init.py` L258-269 / StepO L58-73 (実装確認済) |
| 変更履歴の正 | 引継ぎログ系列 `handover_v29..v42` (最新 v42_20260324) | `docs/DentalBI/handover/` |
| A4印刷版 | カンバン(6列WF)と申し送り(A4書類)を完全分離 (route/component/state) | `申し送りA4用紙設計_20260215_1700.md §1` |

> 注: 「v2/v5」は単独doc命名でなく handover_notes schema 進化 + 引継ぎ版列の通番。設計版の SoT は v3 schema (= 現行 live)。

## 2. iPad横向きセット入力案 (= handover_v34 §6 最優先方針を採用)

`handover_v34_20260321.md §6 UI改善方針(★次回最優先)` を最終UI規範として採用:

| 項目 | 採用方針 |
|------|----------|
| モード切替 | `/settings` マスタ設定画面へ集約、通常モード画面にタブを置かない |
| 病名パネル | 通常モードでは非表示、全幅を症状入力に充てる |
| レイアウト順 | 部位選択 → Step1 → Step2 → Step3 → 確定 → よく使うパターン(最下部) |
| ボタン | コンパクト化 (iPad横向きでスペース効率向上) |

SOAP確定定義 (`handover_v35 §4-1`):
- S欄: 主訴 = 音声入力 + テキスト自由記述
- O欄: 検査所見 = カテゴリ別5段階ボタン (マスタ管理)
- A欄: カルテ病名 = S+O+Xray所見から AI推定 → Dr確定
- P欄: A欄と一体化、**病名タップ → 処置セット候補展開**

→ 画面構成: **iPad横向き2ペイン** — 左ペイン=症状入力ステップ(部位→Step1-3→確定)、右ペイン=A4プレビュー。
既存 `HandoverSelectPage`→`HandoverHomePage` (App.tsx L222-223 route登録済) を本レイアウトへ拡張。

## 3. 小西化 / SPT等の簡単セット方針 (= 処置セットプリセット)

「簡単セット」= 病名タップで処置セット(プリセット)をワンタップ展開する機構。

- 駆動データ: `backend/db/migrations/014_seed_billing_rules.sql` の billing_rules
  (`spt_transition` / `p_exam_2nd` / `srp_after_sc` / `sealant` / `fluoride` / `denture_adjust` 実在確認済)
- 統一原則 (`handover_v39 §107`): 処置セット / カルテ / 書類 / AI清書 は同じルールから導出する
- 実装: P欄の病名タップ → billing_rules由来候補を `treatment_blocks_json` へ投入
- 「小西化」= 院別(小西歯科系)プリセットの匿名化/標準化方針と推定 (※逐語定義は未確証、§6 未完了)

## 4. 採用構成 (収束)

```
[患者選択 HandoverSelectPage]
    ↓ /handover-sheet/:patientId
[HandoverHomePage — iPad横向き2ペイン]
  左: 部位 → S(音声+自由) → O(5段階) → A(AI推定→Dr確定) → P(病名タップ→処置セット展開) → 確定
  右: A4プレビュー (印刷=申し送り書類、カンバンとは別機能)
    ↓
[handover_sheets API (構造化SoT)] ⇄ [handover_notes v3 (下書き/カンバン連携)]
```

- backend: `handover.py`(15295B) / `handover_sheets.py`(15916B) 実装済を流用、新規テーブル禁
- clinic_id ハードコード禁 (ClinicIdContext注入規範、karo review C1 踏襲)

## 5. 変更ファイル

- 本指令スコープ = L2設計収束。**コード変更なし**。
- 本書 `docs/moushi_engine_converged_design_v0.2.md` を成果物として起草 (artifact)。
- 実装(Stage2/3)で変更予定: `frontend/src/pages/HandoverHomePage.tsx`、処置セット展開hook、A4プレビュー。

## 6. 未完了リスト (Open Items)

| # | 項目 | 対応 |
|---|------|------|
| OM-1 | 「小西化」の逐語定義 (院別プリセット匿名化方針の確証) | handover_v30-42 精読で確定要 |
| OM-2 | handover vs handover_sheets endpoint差分の確定 | Stage2着手前に精査 |
| OM-3 | OM7: iPad/Android tablet device仕様 未確定 | 信長round2裁可待ち |
| INFRA-1 | WSL2↔Windows interop全面停止 (UtilAcceptVsock accept4 failed 110、全.exe不能) | 足軽範囲外、大将軍→理事長上申要 |
| INFRA-2 | Start-Daishogun.ps1 worker が command_type=operation_order 未対応 (全PC failed) | dispatch worker 改修要、大将軍上申 |

## 7. 次アクション

1. Stage2 task起案: HandoverHomePage iPad横向き2ペイン化 + 病名タップ処置セット展開
2. 大将軍→理事長: INFRA-1/INFRA-2 上申 (指揮系統厳守、直接差配要求せず)
3. 本書を gunshi 品質チェック → karo 報告 (push前 陛下御差配)

---

*収束設計 v0.2 起案: 直政、2026-05-16 (command 544e244f / 94355af3, operation handoff-board)*
