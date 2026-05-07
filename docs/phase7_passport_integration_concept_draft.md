# Phase 7 パスポート連携 — 概念設計 (ekarte 側接続点) cycle1 確定版

| 項目 | 値 |
|------|------|
| タスクID | subtask_phase7_passport_integration_draft_001 |
| 親 cmd | cmd_t13_ekarte_zerobase_001 |
| 担当 | ashigaru2 (さくら) |
| 起草日 | 2026-05-06 |
| 確定版日時 | 2026-05-06 (cycle1: 家康レビュー PASS 反映 + 家老最終裁可) |
| base_commit | 79ac2e74 |
| ステータス | **確定版 (cycle1)** — Phase 7 cmd 発令時の参照資料 |
| 範囲 | ekarte 側の接続点 (実装視点) のみ。UI ビジュアルはデザイン班 (理事長+信長) 専権 |

---

## 1. 結論サマリ (家老向け 30秒読み)

1. **既存資産は十分整備されている**。teriha-passport (DD-126) は frontend/backend/DB が骨格まで存在。新規実装はほぼ不要、**接続のみ**。
2. **接続点は 9 個** 洗い出した。実装視点で「軽 5本 / 中 3本 / 重 1本」に分類。
3. **🚨 重大警告 (CRITICAL)**: backend に **2系統のエンジンが併存** している (teriha_passport_engine vs child_adventure_engine)。CLAUDE.md §9 パターン1+4 該当。**Phase 7 着手は `cmd_passport_engine_consolidation_001` (統廃合 cmd) 完了まで凍結**。並走運用は Anti-Duplication Rule 違反追認となるため非推奨。
4. **推奨実装順**: 軽 → 中 → 重。最小起点は「SOAP finalize 後フック」(C2)。これは既存 `sync_handover_on_soap_finalize_all` と同パターンで増設可能。
5. **C2 は SAGA 併用必須**: visit に `passport_sync_status (pending/done/failed)` カラム導入で状態不整合検出+再試行可視化、fire-and-forget BackgroundTasks との併用。
6. **保護者同意 (15歳未満)** は Phase 7 着手前にデザイン班+法務監査要。Step1 患者選択時に同意取得→C1 enable/disable 制御、未取得時は受付バッジ+親 LINE/メール通知。
7. **RLS 監査** (`cmd_passport_rls_audit_001`) を別 cmd として並走推奨 (他院展開 §17 を見据え)。
8. **Phase 6 統合テスト E2E-12.4/.5/.6** が Phase 7 接続点の baseline として活用可能 (ashigaru1 担当 commit 4037717 にて整備済)。

---

## 2. 既存資産棚卸し

### 2.1 frontend: `frontend/src/features/teriha-passport/`

| 項目 | 内容 |
|------|------|
| エントリ | `TerihaPassportPage.tsx` |
| 主要コンポーネント | `PassportCover.tsx` `AgeModeHome.tsx` `VisaStampGrid.tsx` `MyStatusCard.tsx` `MinigameMenu.tsx` `RewardExchange.tsx` `PreparationQuestPanel.tsx` `ParentDashboard.tsx` `CeremonyOverlay.tsx` |
| API ラッパー | `api.ts` |
| 型定義 | `types.ts` (DD-126 v1.0 準拠) |
| エンジン | `engine/ageTier.ts` (年齢→tier 解決) |
| hooks | `hooks/usePassport.ts` `hooks/useVisaGrid.ts` |
| ストーリー | `story/story-master.md` |
| アセット | `assets/brand/*.svg` (passport-emblem, corner-tl/tr/bl/br) `assets/characters/dino_family.png` `assets/icons/sparkle.svg` |
| テスト | `__tests__/ageTier.test.ts` |

**型定義の主要 enum** (types.ts より抜粋):
- `AgeTier`: egg / chick / adventurer / hero / kingdom_warrior / parent
- `RankCode`: tamago / hiyoko / bokensha / yusha / okoku_senshi
- `StampKind`: reservation_achieved / visit / quest_complete / birthday / special
- `MissionType`: preparation_quest / visit_quest / daily_brush / minigame / birthday / graduation / custom
- `GameCode`: brushing_rhythm / food_quiz / prevention_quiz / cavity_hunt / mouth_exercise / tooth_adventure_rpg

### 2.2 backend (DD-126 系: teriha_passport)

| ファイル | 役割 |
|---------|------|
| `backend/services/teriha_passport_engine.py` | DD-126 正版エンジン。XP/rank/mission/stamp/reward 集約 |
| `backend/routers/teriha_passport.py` | REST API |
| `backend/tests/test_teriha_passport_engine.py` | エンジン単体テスト |
| `backend/tests/test_teriha_passport_webhooks.py` | webhook イベントテスト |

**主要エンドポイント** (`/api/teriha-passport/...`):
- `POST /members/enroll` - 会員登録
- `GET /members/{member_id}/dashboard` - ダッシュボード取得
- `POST /xp/add` - XP 加算
- `POST /missions/assign` `POST /missions/complete` - ミッション
- `POST /stamps/award` - スタンプ付与
- `POST /rewards/redeem` - 景品交換
- `POST /games/record` - ミニゲームスコア記録
- `POST /family/link` - 家族リンク
- `POST /events/on-appointment-created` - 予約作成イベント
- `POST /events/on-visit-checked-in` - 来院チェックインイベント ★ekarte 連携の本命
- `POST /events/on-preparation-reminder` - 準備リマインダー

### 2.3 backend (別系統: child_adventure)

| ファイル | 役割 |
|---------|------|
| `backend/services/child_adventure_engine.py` | 別世代の冒険エンジン |
| `backend/routers/child_passport.py` | `/api/child-passport/*` |
| `backend/tests/test_child_passport_router.py` | テスト |

**主要エンドポイント** (`/api/child-passport/...`):
- `GET /eligibility/{patient_no}` - 14歳以下判定
- `POST /convert-visit` - **visits 行を冒険ログに変換** ★既存の ekarte→passport 接続点 (要統廃合判断)
- `GET /passport/{patient_no}` - パスポート画面データ
- `GET /adventure-log/{patient_no}` - 冒険履歴
- `GET /ranking/{clinic_id}` - 医院内ランキング

### 2.4 Supabase テーブル群

**DD-126 系 (passport_*) — 9 テーブル + 95 mapping + 12 rank + 90 敵**:

| テーブル | 用途 |
|---------|------|
| `passport_members` | 会員 (clinic_id × patient_no × world_theme_id) |
| `passport_xp_log` | XP 履歴 |
| `passport_stamp_log` | スタンプ履歴 |
| `passport_mission_log` | ミッション履歴 |
| `passport_reward_history` | 景品交換履歴 |
| `passport_rank` | ランク定義 (12 rank) |
| `passport_adventure_mapping` | **処置コード → 冒険イベント マッピング (95 件)** ★既に存在 |
| `passport_family_link` | 家族リンク |
| `passport_game_score` | ミニゲームスコア |

**別系統 (child_adventure_*)**:
- `child_adventure_stats` - 集計済み統計
- `child_adventure_logs` - 冒険ログ

### 2.5 ekarte-v6 出力データ

| ステップ | コンポーネント | 主要出力 |
|---------|--------------|---------|
| Step0 | ModeSelect | mode 切替 (input/audit/etc) |
| Step1 | PatientSearch | patient_no, clinic_id, age_at_visit (←ここで is_child 判定可能) |
| Step2 | VisitTypeDecide | visit_type, visit_date |
| Step4 | ToothSelect | tooth_events 候補 (歯式) |
| Step5A | DiseaseMode | 疾病コード |
| Step5B | TreatmentMode | 処置コード ★ passport_adventure_mapping 参照源 |
| Step6 | DetailPanel | treatment_records 詳細 |
| Step7 | PerioChart | 歯周検査値 |
| Step8 | Vitals | バイタル |
| Step9 | Prescription | 処方 (フッ素塗布など preventive 系の検出可能) |

**ekarte 確定エンドポイント**:
- `POST /api/ekarte-v6/visits` (作成)
- `POST /api/ekarte-v6/soap` (SOAP 作成)
- `PUT /api/ekarte-v6/soap/{soap_id}/finalize` (SOAP 確定)
- `PUT /api/ekarte-v6/visits/{visit_id}/finalize-all` ★**全 SOAP 確定 = visit 完結**

**既存 finalize 後フック (本命の参考実装)**:
```python
# backend/api/ekarte_records.py:942
sync_handover_on_soap_finalize_all(db, finalized_records)
```
このパターンに `sync_passport_on_soap_finalize_all(db, finalized_records)` を追記できれば最小侵襲で連携可能。

---

## 3. 接続点候補リスト (実装視点)

各候補に **重さ** (軽/中/重) + **優先度** (高/中/低) + **依存先** を明記。

### 3.1 軽量接続 (5本)

#### C1. 患者検索ヒット時 → パスポートモード誘導 [軽 / 高]

- **発火点**: `Step1_PatientSearch` の患者選択イベント
- **処理**: `passport_members` lookup + `parent_consent_at` 検証を行い、以下分岐:
  - `is_child=true && parent_consent_at IS NOT NULL` → 「パスポートを開く」ボタン enable
  - `is_child=true && parent_consent_at IS NULL` → ボタン disable + 受付バッジ「同意未取得」+ 親 LINE/メール通知トリガ提示
  - `is_child=false` → ボタン非表示
- **新規コード**: `useChildEligibility.ts` (フロント hook 1本) + 受付バッジ表示制御 (デザイン班 UI 確定後組込)
- **既存流用**: 統廃合後の正版 eligibility API
- **副作用**: 受付/施術側の体験向上、XP 直接加算なし
- **§5.3 連携**: 保護者同意 UX フローと一体設計

#### C2. SOAP finalize-all 後 → passport visit イベント発火 [軽 / 高] ★最小起点

- **発火点**: `backend/api/ekarte_records.py:942` の `sync_handover_on_soap_finalize_all` 直後
- **処理** (SAGA パターン併用):
  1. visit テーブルに `passport_sync_status: pending` で UPDATE
  2. BackgroundTasks で fire-and-forget 実行 (ekarte 確定処理は阻害しない)
  3. visit から patient_no/clinic_id 取得
  4. `passport_members` で会員確認 + clinic_id 一致検証 (§5.2 必須)
  5. `POST /events/on-visit-checked-in` 相当の処理 (XP 加算 + visit スタンプ付与)
  6. 成功時: `passport_sync_status: done` で UPDATE
  7. 失敗時 (retry cap 超過): `passport_sync_status: failed` で UPDATE + dead-letter キュー (`passport_event_dlq`) へ移動
- **新規コード**:
  - `backend/services/passport_sync.py` (新規 1 ファイル) — sync_passport_on_soap_finalize_all 実装
  - `visits.passport_sync_status` カラム追加 migration
  - `passport_event_dlq` テーブル新規 (もしくは既存 dead-letter 機構流用)
- **既存流用**: teriha_passport_engine.on_visit_checked_in
- **副作用**: ekarte 確定処理レイテンシは BackgroundTasks 採用により**増加しない**
- **観察可能性**: 構造化ログ + corr_id 伝播 + `ERR-PASSPORT-001` 等のエラーコード採番 (§16 準拠)
- **冪等性**: visit_id を idempotency key として `INSERT ON CONFLICT (visit_id) DO NOTHING` パターンで重複 sync を防止 (SH8)
- **可視性**: `passport_sync_status` を dashboard に集計表示し、failed 件数の閾値監視を行う (§16 自動応答パイプライン連携)

#### C3. 処置選択時 (Step5B) → 「今日の冒険プレビュー」表示 [軽 / 中]

- **発火点**: `Step5B_TreatmentMode` で処置コード選択イベント
- **処理**: `passport_adventure_mapping` を参照し、選択中の処置コードに対応する敵/冒険を read-only でプレビュー表示
- **新規コード**: `useAdventurePreview.ts` (フロント hook) + 軽い lookup API (`GET /api/teriha-passport/adventure-preview?treatment_codes=...`)
- **既存流用**: passport_adventure_mapping (既存 95 件)
- **副作用**: なし (read-only)、UI 領域はデザイン班裁量

#### C4. 予約作成時 → reservation_achieved スタンプ [軽 / 中]

- **発火点**: 予約 API (既存予約モジュール) の作成 hook
- **処理**: 既存 `POST /api/teriha-passport/events/on-appointment-created` を呼出
- **新規コード**: 既存予約モジュール側に薄い hook 1本のみ
- **既存流用**: teriha_passport.on_appointment_created (既存)
- **副作用**: 予約 API のレイテンシ微増 → C2 同様 BackgroundTasks 推奨

#### C5. パスポートカバー画像差替 [軽 / 低]

- **発火点**: ランクアップ時 (passport_xp_log 加算後の rank_for_xp 判定)
- **処理**: 既存 `PassportCover.tsx` が `current_rank_code` を props で受けて画像切替済み (DD-126 Phase E 完了状況は §7 確認事項)
- **新規コード**: 不要 (既存実装の活用のみ)
- **既存流用**: PassportCover.tsx + assets/characters/
- **副作用**: なし

### 3.2 中量接続 (3本)

#### C6. 処方完了 (Step9) → preparation_quest 完了判定 [中 / 中]

- **発火点**: `Step9_Prescription` 確定時 (フッ素塗布/シーラント等の予防系処方検出)
- **処理**: 処方コードに preparation_quest 該当があれば `POST /missions/complete` を発行
- **新規コード**: 処方コード→ミッションコードの薄い対応表 (5-10 件、設定ファイル `config/preparation_quest_mapping.yaml`)
- **既存流用**: teriha_passport.complete_mission
- **副作用**: 処方 API のレイテンシ微増、誤判定時のロールバック設計が必要

#### C7. 兄弟姉妹来院連動 (passport_family_link) [中 / 低]

- **発火点**: visit finalize 後 (C2 の延長)
- **処理**: `passport_family_link` で同一家族を引き、兄弟姉妹に「家族が来院しました」スタンプ通知
- **新規コード**: `passport_family_notify.py` (新規 1 ファイル) + push 通知連携
- **既存流用**: passport_family_link テーブル
- **副作用 / 縮退方針**: push 通知未整備の場合は **in-app バッジ** (TerihaPassportPage の通知センターアイコン+バッジカウント) で代替。`passport_notification_inbox` テーブル (新規) に通知を貯め、患者アプリ起動時に未読表示。Phase 7 cmd 発令時に push 基盤完成度を確認し方式選択 (§7 確認事項参照)。

#### C8. ミニゲームスコア → 来院時 reward 付与 [中 / 低]

- **発火点**: visit finalize 後 (C2 の延長) または ミニゲーム終了時
- **処理**: 過去 N 日の `passport_game_score` 合計 → 閾値超で reward 自動付与
- **新規コード**: 集計クエリ + reward 自動発行ロジック (`backend/services/passport_reward_auto.py` 新規)
- **既存流用**: passport_game_score + passport_reward_history
- **副作用**: reward 在庫管理 (既存 reward モジュールがどう管理しているか確認要)

### 3.3 重量接続 (1本)

#### C9. 月次集計→ランクアップ儀式演出 [重 / 中]

- **発火点 (択一・dedupe 必須)**: 以下のいずれか **一方のみ** に絞ること。両方併用は dedupe 漏れ事故の温床。
  - **方式A (推奨)**: 日次 cron `backend/jobs/passport_rank_check.py` で `passport_xp_log` 集計 → `passport_rank` 閾値判定
  - **方式B (代替)**: `rank_for_xp` 判定タイミング (XP 加算直後) で同期的にチェック
- **dedupe 機構**: いずれの方式でも `passport_members.pending_ceremony_at` (timestamptz) と `passport_members.last_ceremony_displayed_at` (timestamptz) を併用し、同一ランクアップが複数回演出されることを防止。`pending_ceremony_at IS NOT NULL AND last_ceremony_displayed_at < pending_ceremony_at` のときのみ表示候補となる。
- **表示先 (デザイン班合議事項 §7)**: 以下二択を Phase 7 着手前にデザイン班+理事長殿で確定
  - **案A (患者アプリ側)**: 次回 `TerihaPassportPage` 起動時に `CeremonyOverlay.tsx` 表示 — 診療動線中断なし、推奨
  - **案B (ekarte 側)**: 来院時 ekarte が起動した瞬間に医院 PC で演出 — 診療動線中断懸念あり、要 UX 検証
- **新規コード**: 日次 cron (方式A 採用時) + dedupe カラム追加 migration + フロント overlay 起動条件
- **既存流用**: passport_xp_log + passport_rank + CeremonyOverlay.tsx (既存)
- **副作用**: 日次 cron 運用が必要 (§16 自動応答パイプラインに組込検討)

---

## 4. データフロー概念図 (Markdown)

```
[ekarte-v6 フロント]                   [DentalBI backend]                       [Supabase]
                                                                                  
Step1 PatientSearch ────query───▶ /api/teriha-passport/eligibility ────read────▶ patients (birth_date)
       │                          (統廃合後の正版 API)             ────read────▶ passport_members
       │  if is_child && consent_ok                                              (parent_consent_at)
       ▼                                                                                  
   [パスポート開くボタン enable / disable]                                              
   [受付バッジ: 同意未取得時]                                                            
                                                                                          
Step5B TreatmentMode ───query──▶ /api/teriha-passport/adventure-preview ─read─▶ passport_adventure_mapping
       │                                                                                  
       ▼                                                                                  
   [今日の冒険プレビュー]                                                                
                                                                                          
Step9 Prescription ─finalize──▶ PUT /api/ekarte-v6/visits/{id}/finalize-all              
                                       │                                                  
                                       ├─ sync_handover_on_soap_finalize_all (既存)        
                                       │                                                  
                                       ├─ visits.passport_sync_status = 'pending' ───────▶ Supabase
                                       │                                                  
                                       └─ BackgroundTasks: sync_passport_on_soap_finalize_all (新規 C2)
                                              │  fire-and-forget                          
                                              ├─ teriha_passport_engine.on_visit_checked_in
                                              │     │                                    
                                              │     ├─ passport_xp_log INSERT  ─────────▶ Supabase
                                              │     ├─ passport_stamp_log INSERT ───────▶ Supabase
                                              │     └─ passport_mission_log UPDATE ─────▶ Supabase
                                              │                                          
                                              ├─ 成功: visits.passport_sync_status = 'done'
                                              │                                          
                                              ├─ 失敗 (retry超過): visits.passport_sync_status = 'failed'
                                              │                  passport_event_dlq INSERT ─▶ Supabase
                                              │                                          
                                              └─ (将来) passport_family_notify (C7)       
                                                                                          
[患者フロント (恐竜王国)]                                                                
                                                                                          
TerihaPassportPage ◀──read── /api/teriha-passport/members/{id}/dashboard ◀─read── passport_*
       │                                                                                  
       ├─ PassportCover (rank に応じた表紙) ★C5                                          
       ├─ VisaStampGrid (visit/予約 ★C4)                                                 
       ├─ MinigameMenu (★C8 reward 連動)                                                 
       ├─ MyStatusCard (XP/rank)                                                         
       ├─ ParentDashboard (家族 ★C7 in-app バッジ)                                       
       └─ CeremonyOverlay (rank up 時 ★C9 dedupe フラグ参照)                            
```

---

## 5. リスク・前提条件

### 5.1 🚨 最重要リスク: 2系統エンジンの併存 (CRITICAL)

**現状**:
- `teriha_passport_engine` (DD-126 v1.0 正版) — `passport_*` テーブル群を使う
- `child_adventure_engine` (別系統) — `child_adventure_*` テーブルを使う、`child_passport` ルーターから呼出
- frontend `types.ts` のコメントは DD-126 準拠 → 正版は teriha_passport と推測
- しかし child_passport には既に `POST /convert-visit` という ekarte→passport 接続点がある

**根本原因 4 パターン照合 (CLAUDE.md §9)**:
- ✅ パターン1 (旧版と新版の併存) 該当
- ✅ パターン4 (同名・同責務の重複定義) 該当

**確定方針**:
1. **Phase 7 着手は `cmd_passport_engine_consolidation_001` (統廃合 cmd) 完了まで凍結**
2. 統廃合 cmd で:
   - `teriha_passport_engine` を正版として確定
   - `child_adventure_engine` を `_archive` 退避 + 参照クリーンアップ
   - `/api/child-passport/*` エンドポイントを廃止 (両立期間を最小化)
3. **並走運用は実施しない** — Anti-Duplication Rule 違反の追認となるため (本確定版で旧 cycle1 ドラフトのフォールバック案を削除)
4. 本確定版の C1-C9 は teriha_passport 系を前提に記述

### 5.2 RLS 整合性 (clinic_id 別データ分離)

- `passport_members.clinic_id` で分離されているはず (要確認: RLS policy)
- ekarte 側 visit_id → passport_members の lookup 時、**両方の clinic_id 一致検証必須**
- C2 sync 時 mismatch 検出フロー:
  1. `WARN` ログ出力 (構造化ログ + corr_id + `ERR-PASSPORT-RLS-001`)
  2. `passport_event_dlq` (dead-letter) へ移動し処理を停止 — **silent skip は禁止**
  3. dashboard.md に集計表示し、医院展開時の RLS 監査トリガとする
- 香椎照葉 (clinic_id=5) のみが対象だが、他院展開 (§17) を見据え RLS は厳密に
- **別 cmd 推奨**: `cmd_passport_rls_audit_001` で他院展開前に RLS policy 監査 + clinic_id 一致検証ロジックの単体テスト整備

### 5.3 患者同意 (15歳未満保護者同意) — UX フロー一体設計

- §17 法令対応チェックリスト + §3 dashboard 🚨要対応事項 (保護者同意フロー)
- 技術側カラム (DD-126 にあるか要確認、なければ Phase 7 着手前に migration):
  - `passport_members.parent_consent_at: timestamptz` — 同意取得日時
  - `passport_members.parent_consent_method: text` — 取得経路 (LINE / 紙 / 受付対面)

**Step1 ⇄ C1 一体 UX フロー**:

```
Step1_PatientSearch で患者選択
        │
        ▼
GET passport_members (or eligibility API)
        │
        ├─ is_child=false        ─→ パスポートボタン非表示
        │
        ├─ is_child && consent取得済 ─→ パスポートボタン enable
        │                           ↓ クリック
        │                       TerihaPassportPage 表示
        │
        └─ is_child && consent未取得 ─→ パスポートボタン disable
                                    + 受付バッジ「保護者同意未取得」表示
                                    + ボタン: 「親に LINE で同意依頼」
                                              「親に メール で同意依頼」
                                              「対面で受付対応」
                                    ↓
                        各経路で同意取得後 passport_members.parent_consent_at INSERT
                                    ↓
                        Step1 再評価 → C1 ボタン enable
```

- **Phase 7 着手前にデザイン班+法務監査+理事長殿擦り合せ必須**
- 同意未取得時の縮退動作: ekarte 業務は通常通り進行、パスポート機能のみ非表示

### 5.4 性能影響 (ekarte 確定処理レイテンシ)

- C2 (sync_passport_on_soap_finalize_all) は ekarte の finalize-all クリティカルパスに乗る
- **対策**: BackgroundTasks 採用 (fire-and-forget) で実装し、失敗してもekarte 確定は阻害しない設計
- 既存 `sync_handover_on_soap_finalize_all` のレイテンシ実測値が不明 → §7 確認事項
- §16 Error Design Mandate: retry cap (3回) + dead-letter キュー (`passport_event_dlq`) + correlation_id 伝播

### 5.5 §16 Error Design 観点 (ドラフト段階での言及のみ)

- 構造化ログ: 全 passport 連携呼出に `corr_id`, `err_code` (例: `ERR-PASSPORT-SYNC-001`, `ERR-PASSPORT-RLS-001`, `ERR-PASSPORT-CONSENT-001`) 付与
- メール通知: passport 連携失敗は WARN 扱い (ekarte 本体は成功しているため)、24h で集計サマリ
- fallback: passport 連携失敗時はリトライキュー、ユーザ操作はブロックしない
- ヘルスチェック: `/api/teriha-passport/health` (新規)
- §15 自動復旧: SH2 (Exponential Backoff Retry) + SH8 (Idempotent Retry: visit_id を idempotency key)
- 実装は Phase 7 着手時、本確定版では設計言及のみ

### 5.6 §14 Boy Scout Rule 適用範囲

- 概念設計のみのため対象外
- Phase 7 着手時:
  - **primary**: 新規 `passport_sync.py` (8項目全充足)
  - **直接依存**: `ekarte_records.py:finalize_all_soap` (構造化ログ + corr_id + エラーコード追加)
  - **関連**: `teriha_passport_engine.py` (既に存在、最低限 corr_id 伝播)
- **Phase 6 整備 observability コードとの衝突確認**: Phase 6 で構造化ログ・corr_id・エラーコードが整備されているはずなので、Phase 7 で重複設定しないよう Phase 7 着手時に再確認 (家康指摘 6)

---

## 6. 推奨実装順 (難易度・優先度ソート)

| 順 | 接続点 | 重さ | 優先度 | 着手前提 |
|----|--------|------|--------|---------|
| 0 | **`cmd_passport_engine_consolidation_001`** (統廃合 cmd) | - | **必須** | 家老/信長別 cmd 発令、本確定版完了後の最初のステップ |
| 0' | `cmd_passport_rls_audit_001` (RLS 監査 cmd) | - | 並走推奨 | 0 と並走可、他院展開前に完了 |
| 1 | C2: SOAP finalize-all 後フック (SAGA 併用) | 軽 | 高 | 0 完了 |
| 2 | C1: 患者検索ヒット時誘導 (同意 UX 一体) | 軽 | 高 | 1 完了 + 5.3 デザイン班擦り合せ完了 |
| 3 | C5: パスポートカバー差替 | 軽 | 低 | DD-126 Phase E が完了済か確認 (§7) |
| 4 | C4: 予約作成時スタンプ | 軽 | 中 | 予約モジュール改修権限要 |
| 5 | C3: 処置選択時プレビュー | 軽 | 中 | デザイン班 UI 確定後 |
| 6 | C6: 処方完了時 quest 判定 | 中 | 中 | preparation_quest 一覧確定後 |
| 7 | C9: 月次ランクアップ儀式 | 重 | 中 | 5.3 デザイン班 演出+表示先確定後 |
| 8 | C8: ミニゲーム reward 連動 | 中 | 低 | reward 在庫設計確認後 |
| 9 | C7: 家族通知 (push or in-app バッジ) | 中 | 低 | push 通知基盤完成度確認後 |

---

## 6.5 各 C* の E2E テストカバレッジ案 (Phase 6 baseline 連携)

ashigaru1 担当の Phase 6 統合テスト計画書 (commit `4037717`) に組み込まれた E2E-12.4/.5/.6 が、Phase 7 各接続点の **逆向きテスト書換 baseline** として活用可能。Phase 7 cmd 発令時に以下の対応で書換える。

| 接続点 | Phase 6 baseline | Phase 7 で書換え後の意味 |
|--------|-----------------|----------------------|
| C2 (SOAP finalize 後 sync) | E2E-12.6: sync_handover_on_soap_finalize_all 直後の passport 副作用ゼロ | C2 増設後: passport_xp_log/stamp_log への意図した INSERT を検証 (副作用ゼロ → 正しい副作用) |
| C1 (eligibility API) | E2E-12.5: /api/teriha-passport/* + /api/child-passport/* レスポンス同型性 | 統廃合後: 正版 API のみが応答、廃止 API は 404 を返すことを検証 |
| 全般 | E2E-12.4: passport_*_log への不正 INSERT 検出 | C1〜C9 実装後: 意図した INSERT のみが行われ、不正 INSERT がないことを検証 |
| C9 (rank up dedupe) | (Phase 6 では明示なし) | Phase 7 着手時に追加: 同一ランクアップが複数回演出されないことを検証 (`pending_ceremony_at`/`last_ceremony_displayed_at` 整合性) |
| C2 SAGA 状態 | (Phase 6 では明示なし) | Phase 7 着手時に追加: passport_sync_status の pending→done / pending→failed→DLQ 遷移を検証 |
| 5.2 RLS | (Phase 6 では明示なし) | `cmd_passport_rls_audit_001` で整備: clinic_id mismatch 時 WARN+DLQ を検証 |
| 5.3 同意 | (Phase 6 では明示なし) | Phase 7 着手時に追加: parent_consent_at 未取得時の C1 disable 動作を検証 |

ashigaru1 通達 (msg_20260506_115323): §4.3 R6 (Phase 7 前後で smoke 意味反転、scope 切替必須) + §15.1 (未実装期=non-regression / 実装後=逆向きテストの位置付け) が Phase 6 計画書に明記済。Phase 7 cmd 発令時に E2E-12.4/.5/.6 を逆向きテストへ書換える作業を含めること。

---

## 7. Phase 7 着手前に家老/信長へ確認すべき事項

1. **(必須)** `cmd_passport_engine_consolidation_001` 発令と完了 (本確定版の前提)
2. **(必須)** `cmd_passport_rls_audit_001` 発令 (他院展開前)
3. **(必須)** 保護者同意フロー (法令監査の進行状況、技術側 `parent_consent_at` カラム要確認、デザイン班+法務+理事長殿擦り合せ)
4. **(必須)** C9 ランクアップ儀式の **表示先確定** (案A 患者アプリ側 / 案B ekarte 側) — デザイン班合議事項
5. DD-126 Phase E (PassportCover→TerihaPassportPage 組込) の完了状況
6. push 通知基盤の整備計画 (C7 採用方式 push or in-app バッジ の判断材料)
7. reward 在庫管理モジュールの仕様 (C8 連動可否)
8. 予約モジュールの改修権限・スケジュール
9. Phase 6 統合テスト計画 (ashigaru1 commit `4037717`) と Phase 7 接続点の逆向きテスト書換段取り
10. ekarte 確定時のレイテンシ実測値 (現状の sync_handover_on_soap_finalize_all)
11. C9 月次儀式の発火方式確定 (方式A 日次cron / 方式B 同期チェック の二択)

---

## 8. 参考: 範囲外と判断した事項

| 項目 | 範囲外理由 |
|------|----------|
| パスポート世界観 (恐竜王国の物語性) | デザイン班 (理事長+信長) 専権 |
| ミニゲーム本体実装 | DD-126 Phase F 別タスク、本確定版はフック点のみ言及 |
| 敵 90 体ビジュアル | デザイン班 |
| push 通知 SDK 選定 | 別 cmd で計画的整備 |
| アプリストア配信 | 別フェーズ |
| 課金 (subscription_status) | 経営判断、別 cmd |
| AI チャット連携 (T13 機能5) | 優先度 C、先送り |

---

## 9. 改訂履歴

| 版 | 日時 | 変更内容 | 起草者 |
|----|------|---------|-------|
| draft-001 | 2026-05-06 | 初稿 | ashigaru2 |
| **cycle1 確定版 (draft-002)** | **2026-05-06** | **家康レビュー PASS 反映 + 家老最終裁可。改訂5項目: (1) C2 に SAGA パターン (passport_sync_status) 追記 (2) C9 dedupe 機構明記 (pending_ceremony_at/last_ceremony_displayed_at) + 表示先デザイン班合議事項化 (3) §5.1 並走フォールバック削除 + cmd_passport_engine_consolidation_001 統廃合 cmd 完了まで凍結方針 (4) §5.2 clinic_id 一致検証 + WARN+DLQ + cmd_passport_rls_audit_001 言及 (5) §5.3 Step1↔C1 同意 UX 一体フロー追記。さらに家康(4)(7) 反映: §3.2 C7 in-app バッジ縮退方針、§6.5 各 C* の E2E カバレッジ案 (Phase 6 baseline E2E-12.4/.5/.6 連携)。ashigaru1 通達 (msg_20260506_115323) 反映済。** | **ashigaru2** |

---

**注**: 本確定版は概念設計のみ。実装着手は `cmd_passport_engine_consolidation_001` (統廃合 cmd) 完了後に Phase 7 cmd を別途発令して頂く必要があり、本確定版は Phase 7 cmd 発令時の参照資料です。デザイン班の UI 案 (特に §5.3 同意 UX フロー / C9 表示先) と接続点の擦り合わせも実装前に必須でござる。
