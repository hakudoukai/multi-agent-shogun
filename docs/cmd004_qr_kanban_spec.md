# cmd_004 機能① QR + カンバン 統合設計 spec (= 既実装 spec 化 + 構造的根本治療 gap 分析)

- task_id: subtask_cmd004_qr_kanban_impl_base
- parent_cmd: cmd_004「会計待ち時間ゼロ」機能① QR スキャン入口 → kanban カード遷移
- bloom_level: L3
- author: ashigaru1 (榊原康政 persona、MainPC)
- 起案日: 2026-05-11
- 範囲: **既実装の spec 化 + gap 分析 + test 拡充計画**。新規 endpoint 実装は本 task 範囲外 (= 二重実装回避、karo 御差配 msg_164541 Option α)
- 上位指針: 陛下御差配【根本治療原則】(msg_164625) — 短期 hack 厳禁、構造改善 + test/法令/UX 完備で根本品質
- 連動 spec:
  - `docs/cmd004_payment_flow_spec.md` (ashigaru4 起案予定、会計フロー)
  - `docs/cmd004_dinosaur_100enemies_spec.md` (ashigaru1 既起案、passport 連動先)

---

## 0. 要約 (= spec の存在意義)

cmd_004 機能①「会計待ち時間ゼロ 接続①」は、ashigaru1 inventory (msg_164436) により **既に 95%+ 実装完了** と判明。本 spec は (a) 既実装の正規 documentation 化、(b) 構造的根本治療観点での真の gap 列挙、(c) test 拡充計画 を担う。前置の調査 spec (`subtask_cmd004_qr_kanban_research`) は ashigaru3 pivot で未起案、本 spec が **後追い正本** として確定する。

---

## 1. AC0: 既実装 inventory (file:line 機械 evidence)

調査 base: `/mnt/c/Projects/hakudokai-dev/` HEAD (2026-05-11 16:50 時点 SC WSL access)。

### 1-1. flow 全景

```
[ 受付窓口側 ] CheckinQRDisplay.tsx (token 表示、30 分自動更新)
       ↓
[ 患者端末 ] PatientCheckin.tsx (camera + BarcodeDetector + manual fallback)
       ↓
       POST /api/patient-checkin/qr  { clinic_id, patient_no, qr_token }
       ↓
[ Backend ] patient_checkin.py:53-126 qr_checkin
       ├─ _validate_qr_token  (= SHA256("dentalbi-checkin-{clinic_id}-{YYYY-MM-DD}")[:16] 一致)
       ├─ patient_id 正規化   (= _normalize_patient_id → "XX_YYYYYY")
       ├─ 重複チェック       (= patient_checkin_logs 当日 SELECT)
       ├─ Supabase insert    (= patient_checkin_logs + patient_app_notifications)
       ├─ _safe_register_kanban → register_arrived_card  (= kanban arrived レーン)
       └─ _safe_register_passport_xp → TerihaPassportEngine.add_xp(reason=qr_checkin)
       ↓
[ Frontend 結果 ] success / already / error UI + kanban_status/passport_status warning 表示
```

### 1-2. Backend 層

| layer | symbol | file:line | 役割 |
|------|--------|-----------|------|
| API router 登録 | `app.include_router(patient_checkin_router)` | `backend/main.py:380` | `/api/patient-checkin/*` 配信 |
| API router 登録 | `app.include_router(kanban_router)` | `backend/main.py:273` | `/api/kanban/*` 配信 |
| Endpoint A | `POST /api/patient-checkin/qr` | `backend/routers/patient_checkin.py:53-126` | QR チェックイン本体 (token 検証 + DB insert + kanban/passport 連動) |
| Endpoint B | `GET /api/patient-checkin/qr-token/{clinic_id}` | `backend/routers/patient_checkin.py:196-205` | 窓口側 token 生成 (30 分自動更新前提) |
| Endpoint C | `GET /api/patient-checkin/today/{clinic_id}` | `backend/routers/patient_checkin.py:208-222` | 当日チェックイン一覧 |
| Endpoint D | `PUT /api/patient-checkin/{id}/status` | `backend/routers/patient_checkin.py:225-242` | waiting/called/in_treatment/completed 遷移 |
| Token logic | `_generate_qr_token` | `backend/routers/patient_checkin.py:40-44` | `sha256("dentalbi-checkin-{clinic_id}-{today_jst}")[:16]` |
| Token validation | `_validate_qr_token` | `backend/routers/patient_checkin.py:47-50` | 期待値と完全一致比較 |
| 正規化 | `_normalize_patient_id` | `backend/utils/patient_format.py:21-31` | `^\d{2}_.+` 一致なら維持、それ以外は `{clinic_id:02d}_{patient_no}` 付与 |
| Kanban 連動 | `register_arrived_card` | `backend/api/kanban.py:1246-1338` | 部分 UNIQUE 索引 + INSERT OR IGNORE で同日同患者 1 枚保証 (QB2 cycle1 fix) |
| Passport 連動 | `_safe_register_passport_xp` | `backend/routers/patient_checkin.py:153-193` | 会員照合 → `add_xp(delta=10, reason=qr_checkin)`、例外時 status=warning |
| TZ helper | `today_jst` / `now_jst` | `backend/utils/timezone.py` (= QL3 fix) | Asia/Tokyo 明示 |
| PII mask | `_mask_patient_no` | `backend/utils/patient_format.py:34-41` | 末尾 4 桁以外マスク (KGL1 fix 整合) |

### 1-3. Frontend 層

| layer | file | 役割 |
|------|------|------|
| 受付側 QR 表示 | `frontend/src/pages/reception/CheckinQRDisplay.tsx` (75+ 行) | タブレット窓口設置、30 分自動更新 |
| 患者側 QR スキャン | `frontend/src/patient-app/pages/PatientCheckin.tsx` (319 行) | camera + BarcodeDetector + manual fallback |
| API client | `frontend/src/services/patientAppApi.ts:155-165` | `qrCheckin(clinicId, patientNo, qrToken)` |
| API client | `frontend/src/services/patientAppApi.ts:163-168` | `getQrToken` / `getTodayCheckins` |
| Routing | `frontend/src/patient-app/routes.tsx` | `/patient-app/checkin?patient_id&clinic_id` |

### 1-4. Test 層 (= 27 既 test、ファイル `backend/tests/test_patient_checkin.py` 774 行)

| クラス | test 数 | 主観点 |
|------|------|--------|
| TestQrToken | 3 | 生成 / 同日決定性 / clinic 別異 |
| TestQrCheckin | 7 | success / invalid token / 既受付 / kanban 例外 isolation / passport 例外 isolation / 正規化 / prefix 維持 |
| TestTodayCheckins | 1 | 当日一覧 |
| TestStatusUpdate | 2 | 正常 / 不正 status |
| TestRegisterArrivedCard | 6 | create / dedup / 別患者 / 別日 / archived 後再来院 / 並列 race (QTS1) |
| TestRegisterPaymentCompleted | 8 | done/inputting→billing / idempotent / not_found / archived ignore / clinic isolation / KQ1 race guard / KB2 done_entered_at |
| TestTriggerKanbanBillingMove | 5 | DB 例外 swallow / KS1 sanitize / KGL1 PII mask |

### 1-5. DB schema (= SQLite handover_notes、現行)

| column | type | 用途 |
|------|------|------|
| `note_id` | TEXT PK (UUID) | カード ID |
| `patient_id` | TEXT | "XX_YYYYYY" 正規化形式 |
| `clinic_id` | INTEGER | clinic 分離 key |
| `visit_date` | TEXT | YYYY-MM-DD (JST 基準) |
| `workflow_status` | TEXT | arrived/input_waiting/inputting/review/done/billing/archived |
| `card_type` | TEXT | insurance/self_pay |
| `visit_type` | TEXT | outpatient |
| `checkin_time` / `checkout_time` / `done_entered_at` | TEXT | ISO timestamp |
| `is_writing` / `has_changes` | INTEGER | 排他制御 + 自動戻し制御 |
| `registered_by` | TEXT | "qr_checkin" 固定 (QR 経由識別) |
| INDEX `idx_handover_active_per_day` | UNIQUE PARTIAL | `(patient_id, clinic_id, visit_date) WHERE workflow_status != 'archived'` |

Supabase 側 `patient_checkin_logs` / `patient_app_notifications` は別系統 (= 監査ログ + 通知配信)、SQLite と二重持ち。

---

## 2. AC1: 構造的根本治療観点 gap 分析 (= 単なる edge case ではない真の gap)

陛下根本治療原則 (msg_164625) を満たすため、**短期 hack ではなく構造改善** で解決可能な gap を優先列挙する。

### 2-1. Gap table

| # | gap | 観点 | 現状 (file:line) | severity | 根本治療提案 (短期 hack 否定) |
|---|-----|------|------|----------|---------|
| G-S1 | Token に secret 不含、任意者が clinic_id だけで token 生成可能 | security | `_generate_qr_token` patient_checkin.py:40-44 が **公開された SHA256 計算** | **High** | clinic 毎の per-clinic secret (= env var or DB) を追加し HMAC 化。**設計変更**、hack ではない |
| G-S2 | Token 有効期間 = 当日全日 (1 日中流用可)、リプレイ攻撃に脆弱 | security | 日付 + clinic_id のみで生成、時刻成分なし | Mid | 短時間 window (e.g. 30 分 rolling、HOTP/TOTP 様) で expire、frontend 側 30 分自動更新と既整合 |
| G-S3 | Rate limit なし、QR endpoint への brute force / DoS 余地 | security/法令 | router 直結、middleware 無し | Mid | FastAPI dependency で IP 単位 token bucket、shared limiter (= redis 等)。**仕組み追加** |
| G-L1 | `patient_checkin_logs` の保存期間規定無し | 法令 (医療情報セキュリティガイドライン 6.0、最低 5 年) | DB schema にライフサイクル定義なし | High | 監査ログ retention policy + 暗号化 at-rest、別 spec で TTL 明文化 |
| G-L2 | `patient_no` log 漏れ防止は手動 `_mask_patient_no` 依存、強制機構なし | 法令 (個人情報保護法 22 条) | KGL1 fix で個別対応、global formatter なし | Mid | logging filter で `^\d{2}_\d{4,}$` を自動 mask、**構造改善** |
| G-U1 | BarcodeDetector 非対応ブラウザ (Safari iOS < 17 等) の fallback 動線 test 無し | UX | PatientCheckin.tsx:93-98 が `idle` に戻すのみ、test_patient_checkin.py に E2E 検証なし | Mid | jest test で `BarcodeDetector` 不在時 fallback UI 表示 verify、別 frontend test 追加 |
| G-U2 | カメラ permission 拒否時の再申請動線無し (1 度拒否 → 完了不能) | UX | PatientCheckin.tsx:99-102 で alert only | Low | 拒否時の help text + 設定画面誘導 link、UI 設計改修 |
| G-U3 | 高齢者向け 大文字 token 手動入力時の入力補助無し (空白/小文字許容、混同字対策無し) | UX | PatientCheckin.tsx:283-313 plain text input | Mid | 入力前 normalize (= upper + strip)、`O/0`, `I/1` 視覚混同警告。**構造改善** |
| G-T1 | clinic_id mismatch (= token は clinic 1 用、POST は clinic 2 で送る) の挙動 test なし | test | `_validate_qr_token` が clinic_id 違いを暗黙拒否するが、明示 test 無し | Low | 既 test に追加 (= AC2 範囲) |
| G-T2 | TZ 境界 (= 23:59:59 → 00:00:01 JST 跨ぎ) の token 拒否 test なし | test | QL3 で JST 明示済だが境界 test なし | Low | 既 test に追加 (= AC2 範囲) |
| G-T3 | `qr_token` 異常入力 (空文字 / 半角空白 / 超過長) の挙動 test なし | test | 現状は invalid_token で 400、但し空文字 test なし | Low | 既 test に追加 (= AC2 範囲) |
| G-T4 | `patient_no` 異常入力 (空 / 全角数字 / 半角記号混入) の挙動 test なし | test | `_normalize_patient_id` が `strip()` のみ | Low | 既 test に追加 (= AC2 範囲) |
| G-D1 | SQLite (= 本系) と Supabase (= 監査ログ) の二重持ちで整合保証無し | data integrity | kanban.py は SQLite、patient_checkin_logs は Supabase | Mid | 本 spec 範囲外、cmd_004 payment_flow_spec と統合的に DB 戦略 spec 化要 |
| G-A1 | 既受付時の補完登録 ("既 checkin あるが kanban カード無し") の代替シナリオ未文書化 | architecture | qr_checkin L73-87 で補完するが理由が口承 | Low | spec.md (= 本 doc) で恒久化 |

**severity 内訳**: High=2 (security/法令)、Mid=6、Low=6。

### 2-2. 根本治療優先順位

1. **G-S1 / G-S2 / G-L1**: cmd_004「会計待ち時間ゼロ」より広く、患者アプリ全体 security backbone なので **別 task 切出推奨** (= cmd_004 secret_management 等)。
2. **G-U1 / G-U3**: UX backbone、PatientCheckin.tsx 改修範囲広く、frontend 別 task 切出推奨。
3. **G-T1 ~ G-T4**: 本 task AC2 範囲、test 拡充で解消。

---

## 3. AC2: test 拡充計画 (= 本 task 内で実装)

下記 4 件を `backend/tests/test_patient_checkin.py` に追加。**全 test pytest 既動作 + SKIP=0 / FAIL=0** を維持。

| test name | 対象 gap | 検証内容 |
|-----------|--------|----------|
| `test_checkin_rejects_clinic_id_mismatch_token` | G-T1 | clinic_id=1 用 token を clinic_id=2 で POST → 400 |
| `test_checkin_rejects_empty_or_whitespace_token` | G-T3 | qr_token="" / "   " で POST → 400、kanban 連動非呼出 |
| `test_checkin_rejects_oversized_token` | G-T3 | qr_token に 1024 文字 garbage → 400 |
| `test_normalize_patient_id_strips_whitespace_only` | G-T4 | patient_no="  001234  " → "01_001234" (空白 strip 確認) |

`TestQrCheckin` / `TestRegisterArrivedCard` クラスに追加、既 fixture を流用。

TZ 境界 test (G-T2) は既 `_generate_qr_token` の monkey patch が必要で副作用大、別 task で実施 (= 本 task scope out、report に記録)。

---

## 4. AC3: pytest 実行計画

- 実行 cmd: `cd /mnt/c/Projects/hakudokai-dev && python -m pytest backend/tests/test_patient_checkin.py -v`
- 目標: SKIP=0 / FAIL=0、既 27 test + 新規 4 test = 31 test PASS
- F007 遵守: commit 後 push 前に陛下御差配仰ぎ

---

## 5. β option: 真の残機能候補列挙 (= 別 task 候補)

karo msg_164541 通り、本 task report 内で列挙、別 task 化判断は karo 後段:

| # | 残機能 | 規模感 | 動機 |
|---|--------|--------|------|
| β1 | clinic 毎 secret + HMAC 化 (= G-S1 治療) | L3 backend | security backbone |
| β2 | Token 短期 expire (= G-S2 治療、TOTP 様) | L3 backend + frontend | リプレイ攻撃対策 |
| β3 | Rate limit middleware (= G-S3 治療) | L2 infra | DoS 対策 |
| β4 | 検診カード対応 (= 健診目的来院の card_type 拡張) | L3 backend + spec 起案 | 自費/健診患者対応 |
| β5 | 子供用 QR モード (= 患者保護者親 QR で子複数受付) | L4 backend + frontend + 法令 | 小児歯科の親同伴 UX |
| β6 | 家族同時 QR (= 1 QR で 2-4 名同時受付、家族グループ id) | L4 backend + frontend | 同伴家族短縮 |
| β7 | NFC bridge (= 診察券 NFC + QR 両対応) | L4 hardware + frontend | 高齢者向け非カメラ動線 |
| β8 | TZ 境界完全 test (= G-T2 治療) | L2 test | 12 月末 / 1 月始の運用安全 |
| β9 | BarcodeDetector 非対応 fallback E2E test (= G-U1 治療) | L2 frontend test | Safari iOS 旧版対応 |
| β10 | 高齢者向け入力補助 + 混同字対策 (= G-U3 治療) | L2 frontend | UX backbone |
| β11 | patient_no 自動 mask logging filter (= G-L2 治療) | L2 backend infra | 法令準拠強制 |
| β12 | DB 戦略 spec (= G-D1 治療、SQLite/Supabase 整合) | L3 spec | データ整合 backbone |
| β13 | 監査ログ retention policy + 暗号化 (= G-L1 治療) | L3 backend + spec | 医療情報ガイドライン 6.0 準拠 |

---

## 6. 構造的根本治療評価 (= 陛下原則 self-check)

| 原則 | 本 spec の遵守 |
|---|---|
| (1) 短期 hack/patch 厳禁 | 本 spec は既実装の正本化 + 根本 gap 列挙のみ。hack 提案無し |
| (2) 局所修正禁、構造改善 | gap 治療は全て **構造変更 or 仕組み追加** として β 候補化、局所 patch 無し |
| (3) 工数最小化より将来運用安定 | secret/法令/UX gap を High/Mid 評価、本 task 内では test 拡充のみ実施、本格治療は β 別 task |
| (4) 仕組み追加 vs 改修区別 | gap table 各行で「仕組み追加」or「改修」を提案区別 |
| (5) 根本不可時の代替 + 永続追記 | G-T2 を本 task scope out として report に永続記録 |

---

## 7. 関連 commit history (= 実装 evidence)

- `1302d5b3` (= cmd_004 kanban cycle3 fix、ashigaru1 担当) — billing 終端化 + VALID_MOVES 統一
- `d3f0b59a` + `54ad600` (= cmd_004 dinosaur 100 enemies spec、ashigaru1 直前 task)
- QB1 / QB2 / QL1 / QL2 / QL3 / QTS1 / QTS2 / KQ1 / KB2 / KGL1 / KS1 = cycle1-3 fix marker (= 既コード内コメント参照)

以上。
