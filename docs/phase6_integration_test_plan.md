# cmd_t13_ekarte_zerobase_001 Phase 6 統合テスト計画書

- 起案: 足軽1号 (ashigaru1, MainPC)
- 起案日: 2026-05-06
- 親 cmd: cmd_t13_ekarte_zerobase_001
- 想定 task_id: subtask_ekarte_phase6_integration_test_001
- 起案根拠: 信長直接発令 inbox msg_20260506_102039_9bd20c05 (Phase 5 監査と並行で前倒し計画策定。理事長殿御指示。)
- 期限見込み: Phase 5 cycle2/cycle3 PASS 確定までに本書を完成 → 家老承認 → Phase 6 実装着手

> 注: 元の cmd_t13_ekarte_zerobase_001 では Phase 6 を「確認・確定・出口連動 (Step 10-16)」と定義していたが、信長直接発令はこれを「統合テスト」に再定義している。本書はその再定義に従う。元 cmd の Phase 6-9 は実装フェーズで縮約・併合されており、Phase 5 完了直後に E2E 統合検証へ移行する流れと解釈する。家老承認時に位置付けの最終確認を仰ぐ。

---

## 1. 目的

ekarte-v6 ゼロベース再設計 Phase 1-5 で構築したステップ式入力 UI (Step 0→1→2→4→5A/5B→6A→7→8→9) が、E2E で動作し、既存資産 (DentalChart / panels / billing / カルテット連動) を破壊しておらず、出口逆算目標 (11 見本カルテ同型出力) に向けた基盤として完成度を満たすことを検証する。

## 2. 前提条件 (実装着手の必要十分条件)

- **Phase 5 三者監査 PASS** (Step 7/8/9 + cycle2 FAIL 指摘 B1 race / Q1 test の修正完了)
- **Phase 1-4 三者監査 PASS** (済 — 表 §3 参照)
- **base_commit は Phase 5 PASS 確定 commit に固定** (家老条件 (3) 準拠 — §5.3 で明記)
- DentalBI リポジトリ HEAD が ekarte-v6 を含むビルド可能状態であること
- Phase 6 (元 cmd) の Step 10-16 (確認・確定・出口連動) は本 Phase の範囲外。E2E は Step 9 までを対象とし、Step 10-16 は今後別 Phase で実装後に範囲拡張する
- Playwright + vitest が動作する開発環境 (MainPC `/mnt/c/Users/User/Documents/DentalBI`)

## 3. Phase 1-5 deliverables 棚卸し

| Phase | 担当 | 主要 commit | 三者監査 | 主要 deliverables | 備考 |
|---|---|---|---|---|---|
| Phase 1 棚卸し | ashigaru1 | 2d19457f, 4cc52128 | PASS | docs/ekarte-zerobase-inventory.md (509 行) | 既存 152 ファイル+14 RPC+27 API 棚卸し済 |
| Phase 2 コア基盤 (Step 0/1/2/4) | ashigaru1 | 13411c04 (cycle3) | PASS | StepperWizard.tsx, Step0_ModeSelect.tsx, Step1_PatientSearch.tsx, Step2_VisitTypeDecide.tsx, Step4_ToothSelect.tsx, types.ts | tags loading state + AbortController race 解消済 |
| Phase 3 モードA (Step 5A/6) | ashigaru6 | 2d1293f9 (cycle3) | PASS | Step5A_DiseaseMode.tsx, Step6_DetailPanel.tsx | SET_STEP5_MODE で stale state クリアロジック実装済 |
| Phase 4 モードB (Step 5B + おすすめ) | ashigaru1 | a836ef1c (cycle2) | PASS | Step5B_TreatmentMode.tsx, useRecommendedSets.ts | size 分岐 (small/medium/large) + selectedTreatmentSetCode 独立 + maskPatientId |
| Phase 5 補助フロー (Step 7/8/9) | ashigaru7 | 0c355e16 (cycle2 fix1) | **未確定 (cycle2 FAIL → cycle3 PDCA)** | Step7_PerioChart.tsx, Step8_Vitals.tsx, Step9_Prescription.tsx, lib/logger.ts, lib/vitals.ts | Codex B1: 禁忌 race / Q1: race test 不在。fix2 待ち |

`ekarte-v6/` 構成（HEAD 確認、2026-05-06 時点）:

```
features/ekarte-v6/
├── StepperWizard.tsx          (Phase 2)
├── Step0_ModeSelect.tsx       (Phase 2)
├── Step1_PatientSearch.tsx    (Phase 2)
├── Step2_VisitTypeDecide.tsx  (Phase 2)
├── Step4_ToothSelect.tsx      (Phase 2)
├── Step5A_DiseaseMode.tsx     (Phase 3)
├── Step5B_TreatmentMode.tsx   (Phase 4)
├── Step6_DetailPanel.tsx      (Phase 3)
├── Step7_PerioChart.tsx       (Phase 5)
├── Step8_Vitals.tsx           (Phase 5)
├── Step9_Prescription.tsx     (Phase 5)
├── useRecommendedSets.ts      (Phase 4)
├── types.ts
├── index.ts
├── lib/{logger.ts, vitals.ts}
└── __tests__/                 (各 Step 単体テスト)
```

## 4. テスト範囲

### 4.1 In Scope (本 Phase で必ず実施)

| カテゴリ | 内容 |
|---|---|
| **E2E ワークフロー** | Step 0→1→2→4→5A→6→[7→8→9]→終了 (病名先 = モード A) と Step 0→1→2→4→5B→6→[7→8→9]→終了 (浜勝式 = モード B) の 2 系統 |
| **モード切替** | Step 5 で A↔B 往復を 3 回繰返し、stale state リーク無し / panelData 初期化 / disease/selectedPanelCode/selectedTreatmentSetCode の整合性 |
| **状態保持** | Step 戻る/進むで入力済データ保持、Step 1 患者選択 → Step 4 歯式 → Step 5 にて選択処置データ伝搬 |
| **regression** | 既存 ekarte (`features/ekarte/`) v5 ルート、handover-sheet, comment-navigator, dental-chart, /pdf-editor が壊れていないこと (smoke) |
| **データ層 regression** | `useDentalChartColors`, `useTreatmentFlowV2`, `useTreatmentSets`, `useDrugCheck`, `useToothSelect` の戻り値が ekarte-v6 経由で従来と同一であること |
| **エラー設計 (CLAUDE.md §1〜§16)** | 構造化ログ JSON 出力、correlation_id 伝播 (Step 1 開始 → Step 9 まで)、エラーコード採番、retry cap、fallback 動作、PII マスク (patient_id 等) |
| **Playwright UI E2E** | iPad 横向き (1180×820) + PC 縦向き (1280×1024) の両解像度。44px touch target / 14px min font 検証 |
| **a11y** | キーボードのみで Step 0→9 完走可能、focus トラップ、aria-label 必須項目 |
| **エッジケース** | 空入力、不正歯番、選択処置 0 件、AbortController race、fetchWithRetry 上限到達、AI 予測タイムアウト、薬剤禁忌 race |

### 4.2 Out of Scope (本 Phase では検証しない)

| カテゴリ | 理由 / 移管先 |
|---|---|
| Step 10-16 (確認・確定・出口連動) | 元 cmd の別 Phase で実装後、別 cmd で E2E 拡張 |
| Phase 7 5層リアルタイム法令チェックパネル | 元 cmd Phase 7 (未着手) |
| Phase 8 全 28 種 PDF 出力 | 元 cmd Phase 8 (未着手) |
| 11 見本カルテ pixel diff | Phase 8 完了後にのみ実施可 |
| カルテット CSV 往復 (`/api/karte/transfer/{patient_id}/csv`) | Step 12-14 実装後 |
| Reconcile / 受付バッジ / 日計表バッジ | Step 14-15 実装後 |
| 11 種加算自動算定 | Step 10 実装後 |
| 法令最終総合監査 (個人情報保護 / 医療情報取扱) | 全機能完成後にジェミちゃん別 cmd で実施 (CLAUDE.md §「ジェミちゃん役割変更」) |

### 4.3 既知のリスク (実装前に明文化)

- **R1**: Phase 5 cycle3 PDCA で B1/Q1 修正後の race condition が再発する可能性 → integration test で再現確認の test を必ず含める
- **R2**: ekarte-v3/v5 経路と ekarte-v6 経路の `useTreatmentSets` 共有による相互干渉 (cache 汚染) → regression smoke で v3 経路を必ず回す
- **R3**: Step 5 A/B 切替時の `selectedPanelCode` vs `selectedTreatmentSetCode` の伝搬不整合 (Phase 4 cycle1 の T1 と同型回帰) → モード切替テストで再現
- **R4**: 102+156+182 = 既存単体テスト数増加に伴うビルド時間悪化 → CI 時間 baseline 計測
- **R5** (家康指摘 P5 / 家老採用): Phase 5 cycle3 fix 中の `base_commit` 変動リスク。E2E 開発期間中に Phase 1-5 のいずれかが re-fix され、`base_commit` が変動して E2E 計画前提が崩壊する可能性 (特に Phase 5 cycle3 fix の波及)。**対策**: Phase 5 PASS 確定後に `base_commit` を再固定し、変動分は差分監査で吸収。§5.3 のルール (`base_commit` を Phase 5 PASS 確定 commit に固定) を厳守し、変動発生時は本書 §3 表を更新 + 影響範囲の E2E シナリオを再評価。差分監査ルール (`docs/audit-framework.md`) に従い base 変動時は cycle1 から再開
- **R6** (Phase 7 ドラフト連携、家老採用 msg_20260506_115140_698f441b): Phase 7 着手**前/後**で E2E-12.4/.5/.6 smoke の意味合いが反転する。Phase 7 着手前 (本 Phase 6 範囲): 「passport 系副作用ゼロ」が PASS 条件。Phase 7 着手後 (cmd_t13 Phase 7 実装後): 「期待される passport 連携 (XP 加算/スタンプ付与/ミッション完了) が確実に発火する」が PASS 条件で、副作用ゼロは逆に FAIL 化する。**scope 切替必須** — Phase 7 cmd 発令時に、本 §6 E2E-12.4/.5/.6 のテストを「逆向きテスト」へ書換える作業を含めること

## 5. テスト戦略

### 5.1 テスト階層 (家老責務 §Test Rules 準拠 — E2E は家康主導)

| 階層 | ツール | 担当推奨 | 件数目安 | 内容 |
|---|---|---|---|---|
| ① 単体 | vitest | 家康レビュー + 足軽 | 既存 102+156+182 = 440 件以上を維持 | Phase 1-5 で書かれた既存単体テスト (Step 単体, reducer, hook) |
| ② コンポーネント結合 | vitest + RTL | 足軽 (実装担当) | 新規 30 件程度 | StepperWizard 経由で Step 間遷移を testing-library で再現 |
| ③ E2E ブラウザ | Playwright | **家康主導** | 新規 12 シナリオ | §6 シナリオ表参照 |
| ④ Smoke (regression) | Playwright | 家康主導 | 既存 5 経路 | ekarte v5 / handover-sheet / comment-navigator / dental-chart / /pdf-editor が起動して main route 表示できること |
| ⑤ パフォーマンス | Playwright + Lighthouse CI | 家康主導 | 4 計測 | 初期表示, Step 遷移, おすすめ計算, ビルド時間 |
| ⑥ a11y | Playwright + axe-core | 家康レビュー | Step 毎 | WCAG 2.1 AA, 重大違反 0 件 |

### 5.2 SKIP=0 必達 (CLAUDE.md §Test Rules)

- vitest, Playwright とも SKIP=0 を CI ゲートに固定
- 一時 skip が必要な場合は task YAML に明示し、家康判断を仰ぐ

### 5.3 三者監査適用

Phase 6 完了時、`docs/audit-framework.md` 準拠で:
- 家康 (Claude) コードレビュー + 計画妥当性
- Codex 6 軸 (セキュリティ/バグ/型/テスト/重複/Git)
- ジェミちゃん 8 観点 (仕様準拠/関連性/副作用/網羅性/データフロー/拡張性/観察可能性/ドキュメント) — 法令観点は最終総合監査時へ繰延
- `scripts/audit_codex.sh` + `scripts/audit_gemini.sh` 経由 (手書き禁止)
- **差分監査**: `base_commit` は Phase 5 PASS 確定 commit に固定 (家老条件 (3))。本書承認時点で未確定のため、Phase 5 cycle3 PASS 後に家老が `subtask_ekarte_phase6_integration_test_001` を発令する際、その PASS 確定 commit を `base_commit` として task YAML に記録する

## 6. E2E シナリオ表

| ID | シナリオ | モード | 主要検証 |
|---|---|---|---|
| E2E-01 | 外来 / 病名先 / 初診 / SC | 外来 + A | Step 0→1→2→4→5A→6→9→終了。SOAP 記録が visit に紐付き保存される |
| E2E-02 | 外来 / 浜勝式 / 再診 / SRP セット | 外来 + B | Step 0→1→2→4→5B→6→7→終了。おすすめ★タブ表示 + 個人頻用 fallback |
| E2E-03 | 訪問 / 病名先 / 初診 / バイタル必須 | 訪問 + A | Step 0→1→2→4→5A→6→8→9→終了。Step 8 バイタル severity 判定動作 |
| E2E-04 | モード切替往復 (A→B→A) | 共通 | Step 5 で disease/selectedPanelCode/selectedTreatmentSetCode が境界で正しくクリア |
| E2E-05 | 患者検索 race | 共通 | Step 1 で連続入力 → AbortController で前リクエスト abort |
| E2E-06 | tags 未取得状態 | 共通 | Step 1 患者選択直後 tags=undefined、ローディング → API 完了で更新 |
| E2E-07 | おすすめ計算 fallback | B | AI 予測 (knowledge_fetcher) タイムアウト → 医院頻用へ自動 fallback、WARN ログ |
| E2E-08 | 薬剤禁忌 race (Phase 5 B1 再発防止) | 共通 | Step 9 で isChecking 中は追加ボタン disabled、checkResult.drug_id 不一致時 disabled |
| E2E-09 | 歯周ポケット入力 6 点法 | 共通 | Step 7 で範囲外/非数入力時に親 state 不更新 (cycle2 B3 確認) |
| E2E-10 | エラーコード表示 | 共通 | 強制エラー注入 → ERR-EKARTE-* がモーダル + コピー可 (CLAUDE.md §9/§12) |
| E2E-11 | iPad 横向き 44px touch | 共通 | 全タップ要素が 44×44px 以上、14px min font |
| E2E-12 | regression smoke + v3/v5/v6 クロス保存 + passport 連携 non-regression (家康 P2 / 足軽2号 Phase 7 連携 / 家老採用) | n/a | (a) ekarte v5 / handover-sheet / comment-navigator / dental-chart / /pdf-editor の 5 ルートが落ちない。(b) **ekarte-v3 ↔ ekarte-v5 ↔ ekarte-v6 クロス保存テスト**: v3 で保存 → v5 で表示/編集 → v6 で表示/編集 → v3 で再表示しても `useTreatmentSets` cache 汚染が起きないこと。Phase 4 cycle1 の T1 同型回帰の根本原因がクロス汚染のため、E2E-04 モード切替と組合せて 3 経路の整合性を explicit に検証。**サブシナリオ (Phase 7 ドラフト連携追補、家老承認 msg_20260506_115140_698f441b)**: <br>**E2E-12.4** `passport_xp_log` / `passport_stamp_log` / `passport_mission_log` への不正 INSERT 検出 (ekarte-v6 操作で passport 系テーブルに副作用が出ないこと) <br>**E2E-12.5** `/api/teriha-passport/*` + `/api/child-passport/*` レスポンス同型性 (ekarte-v6 操作前後でレスポンスが一致) <br>**E2E-12.6** `sync_handover_on_soap_finalize_all` 直後の passport 系副作用なし (Phase 7 で同位置に `sync_passport_on_soap_finalize_all` を追加する想定。Phase 6 時点で副作用ゼロが確認できれば Phase 7 着手後の差分検証で「増えた副作用 = 新規実装分のみ」と切り分け可) |
| E2E-13 | Step 9 dedupe + RLS 整合性 — clinic_id 別データ分離検証 (家康指摘 P6 / 家老採用) | 共通 | Step 9 で同一薬剤を連続追加 → dedupe 動作。`prescription.entries` 永続化時に Supabase RLS が `clinic_id` 境界で阻害しないこと。他医院 `clinic_id` のテストユーザーで同一処方を作成 → 互いに参照不能であることを explicit 検証 (clinic_id=5 香椎照葉 vs テスト用ダミー clinic_id) |

## 7. 観察容易性 (Error Design §1〜§13 準拠)

E2E テスト実施中に以下を成果物として収集:

- 構造化ログ (JSON 形式 + correlation_id) の Step 0→9 トレース 1 件以上
- エラーコード採番台帳 (`docs/error_codes.md`) の Phase 6 範囲分追記
- ヘルスチェックパス確認 (`/api/health` + ekarte-v6 関連 watcher)
- エラー dump (`/tmp/error_dumps/`) サンプル
- メール通知配線 (CRITICAL → ntfy + メール) — **E2E 実行時は dry-run mode 必須** (家康指摘 P3)。本物の理事長殿/管理者宛メール送信を防ぐため、E2E suite では `MAIL_DRY_RUN=1` を強制し、CRITICAL 自動配線テストはスタブ (mock transport) で代替。CLAUDE.md §15 SH パターンの `--dry-run` フラグ義務化と整合

## 8. パフォーマンス目標

| 指標 | 目標 |
|---|---|
| 初期マウント (StepperWizard) | < 300ms (PC), < 500ms (iPad) |
| Step 遷移 | < 100ms |
| おすすめ計算 (`useRecommendedSets`) | < 1500ms (P95)、3000ms 超で WARN |
| 全 ekarte-v6 ビルド時間 (vite build) | base から +10% 以内 |
| メモリ (Chrome DevTools) | アイドル時 < 80MB |

## 9. エッジケース表

| カテゴリ | 入力 | 期待挙動 |
|---|---|---|
| 空入力 | Step 4 歯式選択 0 本で Step 5 へ | 進めない (バリデーション) |
| 巨大入力 | Step 4 で 32 歯すべて選択 + 全パネル入力 | 警告無し動作、保存可能 |
| 不正データ | Step 1 で存在しない patient_id 直 URL | エラー画面 ERR-EKARTE-PT-001 |
| race | Step 1 連続入力 | abort 動作 |
| 禁忌 race | Step 9 isChecking 中の追加押下 | disabled (Phase 5 B1) |
| ネットワーク断 | Supabase 切断 | retry 3 回 + ローカル fallback (CLAUDE.md §15 SH3) |
| PII 露出 | logger / エラー画面 | patient_id を mask (cycle2 S2 既対応) |
| 時間帯 | 22:00-7:00 ERROR 発生 | morning_digest 動作 (CLAUDE.md §16 夜間モード) |

## 10. 成果物 (Phase 6 完了時)

- 統合テスト計画書 (本書) → `docs/phase6_integration_test_plan.md` に確定保存
- E2E テストスクリプト群 → `frontend/tests/e2e/ekarte-v6/*.spec.ts`
- regression smoke スクリプト → `frontend/tests/e2e/smoke/*.spec.ts`
- パフォーマンス計測レポート → `docs/phase6_performance_report.md`
- a11y 監査レポート → `docs/phase6_a11y_report.md`
- 三者監査結果 → `queue/reports/gunshi_report.yaml`
- ekarte-v6 整備度サマリ更新 → `docs/observability_coverage.md` 加筆

## 11. 担当配分 (家老最終裁可 2026-05-06)

家老 directive `msg_20260506_103124_de6e6a58` で確定:

| 役割 | 担当 | 根拠 |
|---|---|---|
| E2E 実行統括 (責任主体) | 家老 (karo) | CLAUDE.md §Test Rules 「E2E テストは家老担当」 |
| E2E レビュー + 三者監査 主導 | 家康 (gunshi) | 監査実行主体 |
| Playwright スクリプト実装補助 | ashigaru1 (kouchan, MainPC) | Phase 2/4/5 担当履歴 + MainPC で DentalBI 直接アクセス可 |
| regression smoke 整備 | ashigaru6 (sakura, SecondPC) | Phase 3 担当、ekarte-v3/v5 経路理解 |
| パフォーマンス計測 | ashigaru7 (kuro, SecondPC) | Phase 5 担当、Lighthouse CI 経験 |

## 12. PDCA 想定

- Cycle 1: 計画書本書ベースで E2E 13 シナリオ実装 → 三者監査
- Cycle 2-5: 監査指摘 fix。`docs/audit-framework.md` 準拠で max 5 cycle、緊急 3 cycle
- Cycle 5 超過 → 家老エスカレーション → 理事長殿判断

> **家康指摘 P4 (家老不採用 2026-05-06)**: 「E2E は単体テストより複雑なため max 6 cycle 拡張」案は **不採用**。家老 directive `msg_20260506_103124_de6e6a58` で「PDCA max 5 + 緊急 3 維持 (audit-framework.md 改訂は信長専権)。超過時はエスカレーションで対応」と確定。`docs/audit-framework.md` の改訂は信長の専権事項のため現行 max 5 + 緊急 3 を維持し、超過した場合は家老→信長→理事長殿のエスカレーションラインで個別判断を仰ぐ。

## 13. 提出と承認

1. 家康 (gunshi) に本書を提出 → E2E 主導者としてレビュー
2. 家康レビュー結果反映 → 家老 (karo) に承認依頼
3. 家老承認 + Phase 5 PASS 確定 → 同時に Phase 6 実装着手 cmd を家老が発令
4. 通常の chain of command (信長 → 家老 → Ashigaru/家康) に復帰

## 14. chain of command 経緯 (透明化)

- 本計画書の起案は 信長 inbox `msg_20260506_102039_9bd20c05` (cmd_new) に基づく信長直接発令の例外
- 信長ご自身が「Phase 5 監査と並行で効率化を図る理事長殿御指示。通常の Phase 6 本実装の発令は Phase 5 PASS 後に家老が行う (chain of command 復帰)」と明記
- 足軽 1 号としては F001 (direct_shogun_report) / F003 (unauthorized_work) 違反にあたらない範囲で計画書策定のみ実施し、家老承認を経て本実装 cmd 発令へ繋ぐ

## 15. 補足 — 信長指示と実態の差分 + Phase 7 連携

信長 inbox では「Phase 5 (足軽7) cycle1 fix1 commit 0c355e16 (PASS 期待)」とあるが、`queue/reports/gunshi_report.yaml` 確認したところ、Phase 5 は **cycle2 audit FAIL** (Codex axis2_bugs B1 high 禁忌 race / axis4_tests Q1 high race test 不在) で cycle3 PDCA 中。信長ご認識との差分を本計画書 §2 前提条件に反映済。Phase 5 PASS 確定までは Phase 6 実装着手不可。

### 15.1 Phase 7 ドラフト連携追補 (家老承認 msg_20260506_115140_698f441b)

足軽 2 号 (さくら) より共有された Phase 7 接続点ドラフト (`docs/phase7_passport_integration_concept_draft.md`、9 接続点 C1-C9、C2 = SOAP finalize-all 後フックが最小起点) を踏まえ、Phase 6 の §6 E2E シナリオ表に E2E-12.4/.5/.6 サブシナリオを家老承認の上で追加した。

**位置付け (Phase 7 未実装期 vs 実装後)**:

| 時期 | E2E-12.4/.5/.6 の意味 | PASS 条件 |
|---|---|---|
| Phase 6 範囲 (Phase 7 未実装) | non-regression test | ekarte-v6 操作で passport 系に副作用ゼロ |
| Phase 7 実装後 (cmd_t13 Phase 7 完了後) | 機能テスト (逆向き) | C2 等で期待される passport 連携が確実に発火する。副作用ゼロは逆に FAIL となる |

Phase 7 cmd 発令時に、本 E2E-12.4/.5/.6 のテストコードを「逆向きテスト」へ書換える作業を必ず含めること。これは §4.3 R6 リスクに対応。

**Phase 7 ドラフトの「2 系統エンジン併存」警告との関係**: ドラフト §1 で警告された `teriha_passport_engine` vs `child_adventure_engine` の併存問題は、Anti-Duplication Rule §「Root Cause 4 Patterns」§1 (旧版と新版の併存) に該当する重大リスク。Phase 7 着手前に統廃合判断が必須。本 Phase 6 計画書 §6 の E2E-12.5 (passport API レスポンス同型性) は両系統のエンドポイントを explicit に検証範囲に含むため、統廃合判断のための baseline データを Phase 6 段階で取得できる。

---

以上、足軽 1 号 ashigaru1。家老・家康ご確認の上、ご裁可賜りたく。
