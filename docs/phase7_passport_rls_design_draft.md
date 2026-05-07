# Phase 7 patient_id 連携 RLS 設計 — 概念設計ドラフト

| 項目 | 値 |
|------|------|
| タスクID | subtask_phase7_patient_rls_design_draft_001 |
| 親 cmd | cmd_full_activation_2026_05_07 |
| 担当 | ashigaru2 (さくら) |
| 起草日 | 2026-05-07 |
| base_commit | 79ac2e74 |
| ステータス | **draft-001 (概念設計のみ、実装着手禁止)** |
| 範囲 | passport 系 RLS policy / clinic_id 検証ロジック / WARN+DLQ 防御パターン / pgTAP テスト戦略 — 設計のみ |
| 前提ドキュメント | `docs/phase7_passport_integration_concept_draft.md` (cycle1 確定版, commit ca69709) §5.2 を実装視点に具体化 |

---

## 1. 結論サマリ (家老向け 30秒読み)

1. **DentalBI 既存 RLS は実質「ザル」**: `USING (true)` 永続化されており、テナント分離は **アプリ層の `WHERE clinic_id = ?` に依存**。RLS は形式有効化のみ。香椎照葉単院運用ではこれで成立しているが、**§17 他院展開時の前提を満たさない**。
2. **passport_* テーブルは local migration 不在**: DentalBI repo 内に passport_* DDL/RLS の SQL ファイルが存在しない。Supabase 上で直接適用された可能性が高く、**現状 RLS 設定は要 Supabase 直接確認**。Phase 7 着手前の事実確認必須。
3. **engine 層に clinic_id 再検証ロジックなし (CRITICAL)**: `teriha_passport_engine.add_xp / award_stamp / complete_mission` は `member_id` 単独で動作し、呼出元の clinic_id と member の clinic_id を照合していない。多院展開時に member_id 推測 or 取り違えで他院の XP に書込む恐れ。
4. **C2 sync 経路の検証ポイントは 3 箇所**: (a) visit.clinic_id, (b) passport_members.clinic_id, (c) caller (request) の clinic_id — 3 つが完全一致しない場合は **WARN+DLQ で停止**、silent skip 禁止。
5. **エラーコード ERR-PASSPORT-RLS-001〜010 を採番**: 各 mismatch パターンに 1:1 対応、`docs/error_codes.md` に登録予定 (本ドラフト承認後の別タスク)。
6. **§17 提案ロール (hq_shogun_ai / clinic_shogun_ai / director_emergency) は未実装**: CLAUDE.md §17.8 に DDL 例があるのみ、Supabase に存在しない。Phase 7 着手前に `cmd_passport_rls_audit_001` で整備推奨。
7. **法令最終総合監査との関係**: 本ドラフトはあくまで「Phase 7 機能実装上の RLS 整合性」を扱う。**保護者同意 / 個人情報保護法 / 医療情報安全管理ガイドライン §6.10 準拠** は全機能完成後の法令最終総合監査 (CLAUDE.md Third-Party Audit Rule) で別 cmd として扱う。境界を §7 に明記。
8. **本ドラフトは概念設計のみ、DDL 雛形は §6 に参考掲載するも実装/migration 作成は禁止**。

---

## 2. 既存 RLS policy 棚卸し

### 2.1 DentalBI 既存 RLS パターン (永続化されたアーキテクチャ判断)

local migration を全件確認した結果、RLS が `ENABLE` されているテーブルとそのポリシー形態は以下:

| 群 | migration | RLS 形態 | テナント分離 |
|----|-----------|---------|------------|
| daily_kpi / daily_kpi_fields / clinic_kpi_settings / clinics | `008_rls_daily_kpi.sql` | `USING (true)` (anon key 許容) | アプリ層 `WHERE clinic_id` |
| handover_notes_anon / note_acknowledgments_anon / treatment_plans_anon / handover_archives / daily_report_lines | `013_handover_tables.sql` | `ENABLE` のみ (policy 未定義 → service-role 限定) | アプリ層 |
| dropout_alerts / dropout_settings | `010/011` | 同上 | アプリ層 |
| sales_daily | `012` | 同上 | アプリ層 |
| questionnaire | `015_questionnaire_rls.sql` | `service_all USING (true)` | アプリ層 |
| clinic_settings | `016` | 同上 | アプリ層 |
| child_oral_questionnaires / oral_function_checks / comment_navigator | `018-020` | `ENABLE` (policy 不在) | アプリ層 |
| facility_standards / treatment_plan_navi 等 (supabase/migrations 系) | `20260412/20260502_*` | `ENABLE` (policy 不在 or 同パターン) | アプリ層 |

**観察**:
- **RLS は「形式有効化」されているのみ**。Postgres は policy 未定義 + RLS ENABLE で **service-role 以外のアクセスを全拒否**するため、現状はアプリが service-role 鍵を使って全件読み書きする運用。
- アプリ層 (`backend/api/*.py`) で `clinic_id = ?` を WHERE に必ず付与することでテナント分離を確保。
- **anon key からの直接アクセスは一部許容 (USING(true))** — daily_kpi 等で発生、これは将来 multi-clinic 化の最大の地雷。

**この既存パターンの評価**:
- ✅ 単院 (clinic_id=5 香椎照葉) 運用ではアプリ層が完全に閉じているため事故なし
- ❌ §17 他院展開時の **多テナント分離保証なし** — アプリ層バグ 1 つで他院データ漏洩
- ❌ §17.8 で提案された **hq_shogun_ai / clinic_shogun_ai / director_emergency** ロール分離が機能しない (RLS が判定できない)

### 2.2 passport_* テーブル現状 (要 Supabase 直接確認)

local repo 全件 grep の結果、以下が確認された:

| 探索対象 | 結果 |
|---------|------|
| `supabase/migrations/**/passport_*` | **存在しない** |
| `backend/db/migrations/**/passport_*` | **存在しない** |
| `backend/migrations/**/passport_*` | **存在しない** |
| Python コード内の参照 | `backend/services/teriha_passport_engine.py` / `backend/routers/teriha_passport.py` / `backend/tests/test_teriha_passport_*` のみ |

**結論**: passport_* テーブル群 (DD-126 v1.0) の **DDL / RLS 設定は local repo に存在しない**。Supabase 上で直接 (dashboard or 別経路) 適用された可能性が高い。

**Phase 7 着手前に必須の確認 (本ドラフト範囲外、別 cmd で実施)**:
- `passport_members` の RLS ENABLE 状態 + policy 一覧
- `passport_xp_log` / `passport_stamp_log` / `passport_mission_log` / `passport_reward_history` / `passport_family_link` / `passport_game_score` / `passport_adventure_mapping` / `passport_rank` の同上
- 各テーブルの `clinic_id` カラム有無 (engine コードからは少なくとも `passport_members.clinic_id` の存在は確認済)
- `child_adventure_*` テーブル (別系統エンジン) の RLS — 統廃合 cmd の対象なので参考確認

> ⚠️ **本ドラフトは「passport_* に RLS が定義されている前提で書いてはならない」**。`§3 / §4 / §6` では「現状不明 → 推奨設定」の二段で記述する。

### 2.3 visits / patients / handover_sheets / patients_anon との整合性

**ekarte-v6 関連テーブル** (Phase 7 C2 接続点で参照する):

| テーブル | clinic_id | RLS 状態 (local 確認分) | アプリ層 WHERE | 備考 |
|---------|-----------|-------------------|--------------|------|
| `patients_anon` | ✅ | `001_create_tables.sql` で定義、RLS 設定は別 migration or Supabase 側 (要確認) | 全 API で `WHERE clinic_id` | patient_hash が PK、HMAC-SHA256 ハッシュで匿名化 |
| `visits` (ekarte-v6) | ✅ (推定) | `backend/api/ekarte_records.py` 参照、migration 単一ファイル化されていない | `WHERE clinic_id` 必須運用 | C2 接続の起点 |
| `handover_notes_anon` / `handover_archives` | ✅ | `013_handover_tables.sql` で RLS ENABLE、policy 未定義 | アプリ層 | `sync_handover_on_soap_finalize_all` の保管先 |
| `daily_report_lines` | ✅ | 同上 | アプリ層 | 14 区分点数の集計 |

**Phase 7 連携時の整合性論点**:

1. **patient_hash (匿名化) vs patient_no (passport 系)** — DentalBI は patient_hash で匿名化、passport_members は patient_no で生表現。**両者の橋渡し点で clinic_id 一致が崩れる窓**を作る恐れ。 → §3.1 で詳説。
2. **visits (ekarte-v6) の clinic_id** が patient_no を経由して passport_members.clinic_id と一致するか、C2 sync で **必ず照合**。 → §3.1 で詳説。
3. **handover (sync_handover_*)** は既存で RLS-permissive ながら事故なし。これは clinic_id=5 単院運用の恩恵。Phase 7 多院展開を見据えた追加策が `cmd_passport_rls_audit_001` で必要。

### 2.4 §17 RLS ロール (hq_shogun_ai / clinic_shogun_ai / director_emergency) との関係

CLAUDE.md §17.8 に SQL 例として記載されている:

```sql
CREATE ROLE hq_shogun_ai;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO hq_shogun_ai;
GRANT INSERT, UPDATE ON error_log, remote_audit_log TO hq_shogun_ai;
CREATE ROLE clinic_shogun_ai;
GRANT SELECT, INSERT, UPDATE, DELETE ON patients TO clinic_shogun_ai;
CREATE ROLE director_emergency WITH NOINHERIT;
```

**現状 (2026-05-07)**:
- 上記ロールは **概念のみ、Supabase に未作成**。
- 既存 RLS は `USING (true)` パターンのため、ロール分離が機能しない (誰でも素通り)。
- Phase 7 で passport_* に書込む主体は backend の service-role 1 種類のみ。

**Phase 7 着手時点での方針** (本ドラフト推奨):

| ロール | Phase 7 開発期間中の扱い | §17 多院展開時の扱い |
|-------|----------------------|--------------------|
| `service_role` (Supabase 既存) | 全 passport_* 書込権限を維持 | 同左 (但し session ベースで clinic_id を `request.jwt.claim.clinic_id` で固定) |
| `clinic_shogun_ai` | **未使用** (ロール作成は別 cmd) | 自院 (`clinic_id`) のみアクセス可能、RLS で `clinic_id = current_setting('app.clinic_id')::int` 強制 |
| `hq_shogun_ai` | **未使用** | 全院 read 可、書込は `error_log` / `remote_audit_log` のみ — passport_* 書込権限なし |
| `director_emergency` | **未使用** | NOINHERIT、緊急時のみ手動付与 |
| `anon` | passport_* 直接アクセス禁止 (現状) | 同左、必ず backend API 経由 |

**結論**: §17.8 のロール体系は Phase 7 本実装の **必要条件ではないが推奨条件**。Phase 7 単独では service-role + アプリ層 WHERE で動作するが、`cmd_passport_rls_audit_001` で多院展開前にロール体系を実装する段取りが妥当。

---

## 3. patient_id 連携経路の RLS 検証ポイント

Phase 7 ドラフト確定版 §3 で挙げた C1〜C9 のうち、**clinic_id 一致を検証すべき経路** は以下。Phase 7 ドラフト §5.2 を実装視点に具体化したもの。

### 3.1 C2: sync_passport_on_soap_finalize_all (CRITICAL)

**経路図**:

```
[ekarte-v6 finalize-all 完了]
        │
        ├─ caller_clinic_id  ← request.jwt.claim or session
        ↓
[finalized_records (visit_id × N)]
        │
        │  for each visit_id:
        ↓
[1] visits 取得
        │  fields: visit_id, clinic_id (visit_clinic_id), patient_no, ...
        ↓
[2] passport_members lookup
        │  WHERE clinic_id = visit_clinic_id AND patient_no = visit.patient_no
        ↓
[3] member_id 取得 → engine.on_visit_checked_in(member_id, ...)
        │
        ↓
[4] passport_xp_log INSERT, passport_stamp_log INSERT
```

**検証ポイント (3 段階)**:

| # | 検証 | 失敗時の動作 | エラーコード |
|---|------|------------|------------|
| V1 | `caller_clinic_id == visit.clinic_id` | WARN + DLQ + 処理停止 | ERR-PASSPORT-RLS-001 |
| V2 | `visit.clinic_id == passport_members.clinic_id` (passport_members 取得時の WHERE 一致確認) | WARN + DLQ + 処理停止 | ERR-PASSPORT-RLS-002 |
| V3 | `passport_members not found` (lookup 結果 0 件、enroll 未済) | INFO + skip (異常ではない、enroll は別経路) | ERR-PASSPORT-RLS-003 |

**追加検証 (engine 内 member_id 単独操作の脆弱性対策)**:

| # | 検証 | 必要性 | エラーコード |
|---|------|------|------------|
| V4 | engine.add_xp 等で受け取った `member_id` から member を取得し、`member.clinic_id == caller_clinic_id` を確認 | **高 (CRITICAL)** | ERR-PASSPORT-RLS-004 |
| V5 | engine 内部で adventure_mapping 参照時、mapping にも `clinic_id` が存在する場合は一致確認 (現状 mapping 共通テーブルなら不要) | 設計確認後 | ERR-PASSPORT-RLS-005 |

**実装指針 (Phase 7 本実装時の擬似コード — 本ドラフトは概念のみ)**:

```python
# backend/services/passport_sync.py (Phase 7 着手時に新規作成、本ドラフトでは作成しない)
async def sync_passport_on_soap_finalize_all(
    db: SupabaseClient,
    finalized_records: list[VisitRecord],
    *,
    caller_clinic_id: int,  # request scope
    corr_id: str,            # §16 correlation_id
):
    for visit in finalized_records:
        # V1
        if visit.clinic_id != caller_clinic_id:
            log_warn("ERR-PASSPORT-RLS-001", corr_id=corr_id, visit_id=visit.visit_id,
                     caller_clinic_id=caller_clinic_id, visit_clinic_id=visit.clinic_id)
            await dlq_insert("passport_event_dlq", ...)
            continue

        # V2 (lookup 自体に WHERE clinic_id 含む)
        member = db.table("passport_members") \
            .select("*") \
            .eq("clinic_id", visit.clinic_id) \
            .eq("patient_no", visit.patient_no) \
            .execute()
        if not member.data:
            log_info("ERR-PASSPORT-RLS-003", corr_id=corr_id, visit_id=visit.visit_id)
            continue  # enroll 未済は異常ではない

        # V4 (engine 呼出前)
        engine.on_visit_checked_in(
            member_id=member.data[0]["member_id"],
            caller_clinic_id=caller_clinic_id,  # engine 内で再検証
            corr_id=corr_id,
        )
```

### 3.2 C1: 患者検索ヒット時 → パスポートモード誘導

**経路図**:

```
[Step1_PatientSearch]
        │  clinic_id (caller), patient_no (selected)
        ↓
[GET /api/teriha-passport/eligibility/{patient_no}?clinic_id=...]
        │
        ↓
[passport_members lookup]
        │  WHERE clinic_id = caller_clinic_id AND patient_no = patient_no
        ↓
[is_child + parent_consent_at] → ボタン enable/disable
```

**検証ポイント**:

| # | 検証 | 失敗時の動作 | エラーコード |
|---|------|------------|------------|
| V6 | `caller_clinic_id == passport_members.clinic_id` (lookup 自体で確保) | WARN + 404 応答 | ERR-PASSPORT-RLS-006 |
| V7 | URL の patient_no が caller の clinic_id 配下に存在するか (ekarte 側 patients_anon で `patient_hash → patient_no` 整合性、必要なら) | 設計確認後 | (未採番) |

**実装指針**:
- eligibility API は **クエリパラメータ or path** で `clinic_id` を必須化、Body 信頼を避ける。
- 単院 (clinic_id=5) では Field default で動くが、多院展開時は session の jwt claim から取得する設計に切替える前提。

### 3.3 clinic_id mismatch 検出パス (集約)

**全経路の mismatch パターンと対応**:

| パターン | 発火点 | 対応 | エラーコード |
|---------|-------|------|------------|
| caller != visit.clinic_id | C2 | WARN + DLQ + 停止 | ERR-PASSPORT-RLS-001 |
| visit.clinic_id != passport_members.clinic_id (lookup 0 件かつ別 clinic_id で hit) | C2 (※`patient_no` がグローバル一意でない場合のみ顕在化、現状は安全) | WARN + DLQ + 停止 | ERR-PASSPORT-RLS-002 |
| passport_members not found | C2 | INFO + skip | ERR-PASSPORT-RLS-003 |
| caller != member.clinic_id (engine で member_id 単独受領時) | engine.add_xp/award_stamp/complete_mission | WARN + DLQ + 停止 | ERR-PASSPORT-RLS-004 |
| eligibility API で caller != passport_members.clinic_id | C1 | WARN + 404 応答 | ERR-PASSPORT-RLS-006 |
| family_link で family の他メンバーが別 clinic_id | C7 (将来) | WARN + DLQ + 停止 | ERR-PASSPORT-RLS-007 |
| game_score 記録時の member_id mismatch | C8 (将来) | WARN + DLQ + 停止 | ERR-PASSPORT-RLS-008 |
| reward redeem 時の member_id mismatch | engine.redeem_reward | WARN + 拒否 | ERR-PASSPORT-RLS-009 |
| RLS policy 違反検知 (DB 側で) | 全経路 | CRITICAL + ntfy | ERR-PASSPORT-RLS-010 |

### 3.4 application-layer の現状脆弱性 (CRITICAL)

`backend/services/teriha_passport_engine.py` を確認した結果、以下の **member_id 単独操作** が存在し、いずれも呼出元 clinic_id 検証なし:

```python
# 現状 (脆弱性あり)
engine.add_xp(member_id=..., delta_xp=..., reason_code=...)
engine.award_stamp(member_id=..., stamp_kind=...)
engine.complete_mission(mission_log_id=...)
engine.redeem_reward(member_id=..., reward_asset_key=..., reward_tier=...)
engine.record_game_score(member_id=..., game_code=..., score=...)
```

**Phase 7 本実装時の必須対策** (本ドラフトは設計のみ、実装は Phase 7 cmd):

1. **engine の全 member_id 受領メソッドに `caller_clinic_id` 引数を追加** (V4 を強制)
2. engine 内部で member 取得 → clinic_id 比較 → mismatch なら raise PassportRlsError(ERR-PASSPORT-RLS-004)
3. router 層は `request.jwt.claim.clinic_id` (or session) から caller_clinic_id を取得し engine に渡す
4. 単院 (clinic_id=5) 運用中は default=TERIHA_CLINIC_ID で動作可、ただし jwt claim と整合性チェック必須

**この対策は Phase 7 着手の最重要前提**。本ドラフト承認後、Phase 7 cmd 発令時にタスク YAML に明記すること。

---

## 4. 防御パターン設計

### 4.1 WARN ログ + dead-letter (passport_event_dlq)

**設計方針** (CLAUDE.md §16 / Watcher Design Principles 準拠):

- silent skip 禁止 — clinic_id mismatch は必ず WARN ログ + DLQ 永続化
- DLQ 専用テーブル `passport_event_dlq` を新設 (Phase 7 本実装時、本ドラフトは DDL 雛形 §6 に掲載のみ)
- DLQ エントリは **手動 ack 必須** (人間 or HQ Shogun runbook)
- 5 件/小時を超えたら ntfy CRITICAL (§16 自動応答パイプライン連携)

**DLQ レコード構造 (推奨)**:

| カラム | 型 | 説明 |
|-------|---|------|
| dlq_id | UUID PK | 自動採番 |
| err_code | TEXT | ERR-PASSPORT-RLS-001 等 |
| corr_id | TEXT | §16 correlation_id |
| caller_clinic_id | INT | 検出時の caller |
| visit_id | UUID NULL | C2 経路の場合 |
| member_id | UUID NULL | engine 経路の場合 |
| patient_no | TEXT NULL | C1/C2 経路の場合 |
| event_payload | JSONB | 元イベントペイロード (debug 用) |
| created_at | TIMESTAMPTZ | 検出時刻 |
| acknowledged_at | TIMESTAMPTZ NULL | 手動 ack 時刻 |
| acknowledged_by | TEXT NULL | system / 人間 ID |
| close_reason | TEXT NULL | retry_exceeded / manual / etc |

**重複検知**: `(err_code, corr_id, visit_id or member_id)` を UNIQUE 制約で idempotent 化 (SH8 準拠)。

### 4.2 retry cap + idempotent operations

**retry policy** (Watcher Design Principles 準拠):

- C2 sync: retry cap = **3 回**、exponential backoff (1s → 2s → 4s)
- 3 回失敗で DLQ 移動
- visit_id を idempotency key として `passport_xp_log (visit_id, member_id)` 等に UNIQUE 追加検討 → **重複 INSERT を DB 側で阻止**
- `passport_event_dlq.UNIQUE(err_code, corr_id)` で同一 corr_id の重複 DLQ 阻止

**idempotency key の選定**:

| 操作 | idempotency key |
|------|---------------|
| C2 visit→XP 加算 | `passport_xp_log.source_event_ref = visit_id` で既存 hit なら skip |
| C2 visit→stamp 付与 | `passport_stamp_log.source_event_ref = visit_id` で既存 hit なら skip |
| C2 visit→mission 完了 | `passport_mission_log.related_appointment_id` 系統で判定 |
| C4 予約→stamp 付与 | `passport_stamp_log.source_event_ref = appointment_id` で既存 hit なら skip |

DB 層で `UNIQUE` を効かせるため、上記カラムが既存テーブルに含まれているか **§7 確認事項** とする (engine コードからは少なくとも `source_event_ref` カラムの存在は確認可能だが UNIQUE 設定は不明)。

### 4.3 エラーコード採番 (ERR-PASSPORT-RLS-001 〜 010)

§3.3 で列挙したコードを `docs/error_codes.md` に登録予定 (本ドラフト承認後の別タスク)。台帳エントリ雛形:

```markdown
## ERR-PASSPORT-RLS-001
- **発生条件**: C2 sync 時、caller_clinic_id != visit.clinic_id
- **重要度**: WARN (DLQ 移動 + 集計閾値超過時 CRITICAL 昇格)
- **メール通知**: 1 時間集計サマリ
- **ユーザー表示文言**: なし (内部処理エラー、ekarte 確定処理は成功している)
- **対処法**:
  1. dashboard "ERR-PASSPORT-RLS-001 last 24h" で発生件数確認
  2. caller_clinic_id と visit.clinic_id の差分 → 認証経路か finalize-all 呼出元のバグ調査
  3. DLQ から手動再投入 (clinic_id 修正後)
- **発生時 dump 取得項目**: visit_id, caller_clinic_id, visit_clinic_id, finalized_records 件数, request headers
- **関連 corr_id 検索**: error_log + passport_event_dlq の corr_id JOIN
```

ERR-PASSPORT-RLS-002〜010 も同様の形式で別タスクで整備。

### 4.4 多層防御モデル (4 層)

**Phase 7 で目指す防御深度** (Defense in Depth):

| 層 | 機構 | Phase 7 本実装の対象 | §17 多院展開時の追加 |
|----|------|-------------------|--------------------|
| L1 アプリ層 | router/engine の `clinic_id` 検証 + WHERE 必須化 | ✅ **必須実装** | 同左、jwt claim 化 |
| L2 idempotency | UNIQUE 制約 + retry cap | ✅ **必須実装** | 同左 |
| L3 観察可能性 | 構造化ログ + corr_id + ERR-PASSPORT-RLS-* | ✅ **必須実装** (§16 準拠) | 同左、HQ ダッシュボード集約 |
| L4 DB-RLS | `clinic_id = current_setting('app.clinic_id')::int` policy | ⚠️ 推奨だが Phase 7 単独では必須でない | ✅ **必須**、`cmd_passport_rls_audit_001` で整備 |
| L5 ロール分離 | hq_shogun_ai / clinic_shogun_ai / director_emergency | ❌ Phase 7 範囲外 | ✅ **必須**、別 cmd |

**Phase 7 本実装の最低ライン**: L1 + L2 + L3。L4/L5 は他院展開直前に別 cmd で整備。

---

## 5. Supabase RLS テスト戦略

### 5.1 pgTAP vs 手動 SQL の選択

**結論**: Phase 7 本実装段階では **pgTAP 採用推奨だが、最初は手動 SQL シナリオから始め段階的移行**。

| 手法 | 利点 | 欠点 | Phase 7 段階 |
|------|------|------|------------|
| pgTAP | DB 内で完結、CI 組込容易、policy 単体テスト可 | 学習コスト + Supabase 拡張で `pgtap` 有効化が必要 | Phase 7 後半 (推奨) |
| 手動 SQL シナリオ (psql script) | 即着手可、結果が読みやすい | CI 化が手間 | Phase 7 前半 (現実解) |
| Python 経由 (pytest + supabase-py) | 既存テスト基盤に乗せられる、E2E 寄り | RLS policy 単体検証としては間接的 | 補助 (回帰テスト) |

**推奨段取り**:
1. Phase 7 cycle1: 手動 SQL シナリオ 5〜10 本で V1〜V10 を検証
2. Phase 7 cycle2 以降: pgTAP に書換え、CI 組込
3. `cmd_passport_rls_audit_001` (他院展開前): pgTAP 全件 PASS を必須ゲートに

### 5.2 越境アクセス検出シナリオ (推奨 10 本)

**Phase 7 本実装時に整備する pgTAP / 手動 SQL シナリオ**:

| # | シナリオ | 期待結果 | 検証コード |
|---|---------|---------|----------|
| RT01 | clinic_A の service-role が clinic_B の passport_members を SELECT | RLS で 0 件返却 (L4 実装後) | ERR-PASSPORT-RLS-CHECK-01 |
| RT02 | clinic_A の caller が visit_id (clinic_B) で C2 sync を呼出 | V1 検出 → DLQ 移動 | ERR-PASSPORT-RLS-001 |
| RT03 | clinic_A の caller が member_id (clinic_B) で engine.add_xp を呼出 | V4 検出 → エラー応答 | ERR-PASSPORT-RLS-004 |
| RT04 | passport_members に存在しない patient_no で C2 呼出 | V3 INFO + skip | ERR-PASSPORT-RLS-003 |
| RT05 | 同一 visit_id で 2 回 C2 を呼出 (重複) | idempotency で 1 回のみ XP 加算 | (idempotency 検証) |
| RT06 | DLQ への重複 INSERT (同 corr_id) | UNIQUE 制約で阻止 | (idempotency 検証) |
| RT07 | C1 eligibility API で他院 patient_no を query | V6 検出 → 404 | ERR-PASSPORT-RLS-006 |
| RT08 | hq_shogun_ai ロールから passport_members を SELECT (§17.8 実装後) | 全院 read 可 | (§17 検証) |
| RT09 | clinic_shogun_ai ロールから他院 passport_members を SELECT (§17.8 実装後) | 0 件返却 | (§17 検証) |
| RT10 | anon ロールから passport_xp_log を直接 INSERT (バイパス試行) | RLS で拒否 | ERR-PASSPORT-RLS-010 |

### 5.3 CI 組込指針

- Phase 7 本実装の三者監査でデコポン Axis 4 (テスト) で必ずチェック
- pgTAP 全件 PASS が `cmd_passport_rls_audit_001` の完了条件
- Phase 6 統合テスト計画書 (commit 4037717) E2E-12.4 (passport_*_log への不正 INSERT 検出) と統合

---

## 6. 推奨 RLS policy 雛形 (DDL 例 — 実装ではない、参考のみ)

⚠️ **本セクションは概念設計の DDL 例。Phase 7 cmd 発令前に実装 / migration 作成禁止 (Anti-Duplication Rule + 本タスク規律)**。

### 6.1 passport_event_dlq テーブル雛形

```sql
-- Phase 7 本実装時に新規作成、本ドラフトでは作成しない
-- migration: 0XX_passport_event_dlq.sql
CREATE TABLE IF NOT EXISTS passport_event_dlq (
    dlq_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    err_code          TEXT NOT NULL,
    corr_id           TEXT NOT NULL,
    caller_clinic_id  INTEGER,
    visit_id          UUID,
    member_id         UUID,
    patient_no        TEXT,
    event_payload     JSONB,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at   TIMESTAMPTZ,
    acknowledged_by   TEXT,
    close_reason      TEXT,
    UNIQUE (err_code, corr_id, COALESCE(visit_id::text, ''), COALESCE(member_id::text, ''))
);
CREATE INDEX idx_dlq_err_code ON passport_event_dlq(err_code);
CREATE INDEX idx_dlq_created_at ON passport_event_dlq(created_at);
ALTER TABLE passport_event_dlq ENABLE ROW LEVEL SECURITY;
-- 既存パターン踏襲: service-role のみアクセス
```

### 6.2 passport_members に対する将来 RLS policy 雛形 (L4 多層防御)

⚠️ **§17 多院展開直前 (`cmd_passport_rls_audit_001`) で適用予定、Phase 7 単独では非適用**。

```sql
-- 将来適用、本ドラフトでは実装しない
ALTER TABLE passport_members ENABLE ROW LEVEL SECURITY;

-- service_role: バイパス (Supabase デフォルト)

-- clinic_shogun_ai: 自院のみアクセス可
CREATE POLICY "passport_members_clinic_isolation"
    ON passport_members
    FOR ALL
    TO clinic_shogun_ai
    USING (clinic_id = current_setting('app.clinic_id', true)::int)
    WITH CHECK (clinic_id = current_setting('app.clinic_id', true)::int);

-- hq_shogun_ai: 全院 read 可、書込不可
CREATE POLICY "passport_members_hq_read"
    ON passport_members
    FOR SELECT
    TO hq_shogun_ai
    USING (true);

-- anon: 全拒否 (policy 未定義 = service-role/上記ロールのみ)
```

passport_xp_log / passport_stamp_log / passport_mission_log / passport_reward_history / passport_family_link / passport_game_score も同様のパターンで `member_id` 経由で `passport_members.clinic_id` に JOIN して判定する policy を雛形化 (本ドラフト範囲外、別 cmd で具体化)。

### 6.3 既存 visits / patients_anon / handover_* に対する追加方針

- 既存 RLS パターン (`USING (true)` or policy 未定義) を **passport_* で踏襲してはならない**。
- 既存テーブルの RLS 強化は本ドラフト範囲外、`cmd_passport_rls_audit_001` で対応。
- Phase 7 本実装では既存テーブル設定を変更しない (Anti-Duplication / 副作用防止)。

---

## 7. 法令最終総合監査との関係

### 7.1 Phase 7 着手前 (本ドラフトの範囲)

**含まれるもの**:

- ✅ システム整合性 (clinic_id 一致検証、テナント分離)
- ✅ 機能仕様準拠 (Phase 7 ドラフト確定版 §3.1/§3.2/§5.2)
- ✅ Watcher Design Principles 準拠 (retry cap / DLQ / idempotency / dedupe)
- ✅ §16 Error Design 観点 (corr_id / err_code / 構造化ログ)
- ✅ 副作用検知 (Phase 6 E2E-12.4 連携)

**含まれないもの (法令最終総合監査の範囲)**:

- ❌ 個人情報保護法 第 28 条 (委託先の監督) 準拠監査
- ❌ 医療情報安全管理ガイドライン §6.10 (保守事業者要件) 準拠監査
- ❌ 保護者同意 (15 歳未満) の法的有効性監査 — 経路設計 (§5.3 確定版) は含むが法的最終判断は範囲外
- ❌ 5 年保存要件 (医療法施行規則) の DLQ ログ保存期間検証
- ❌ 改竄防止 WORM ストレージ要件
- ❌ §17 リモート保守 SSH ログ取扱い
- ❌ アクセス権限合意書 / 守秘義務誓約書

### 7.2 全機能完成後 (法令最終総合監査の範囲)

CLAUDE.md Third-Party Audit Rule §法令最終総合監査 + ジェミちゃん監査観点に従い、Phase 7 完成後 (および Phase 6/7/8 全完成時点) に **別 cmd** で実施:

```
cmd_legal_final_audit_passport_001 (仮称、全機能完成後発令)
    ↓
ジェミちゃん主導 (理事長殿御指示 2026-05-05)
    - 法令準拠 (個人情報保護法 / 医療情報安全管理ガイドライン)
    - 医療情報取扱い
    - 個人情報保護
    - 保護者同意 (法的有効性)
    - 5 年保存 / 改竄防止
    - 多院展開時の §17 規約
```

### 7.3 境界の明確化

| 監査 | 主担当 | タイミング | 本ドラフトとの関係 |
|------|------|----------|------------------|
| Phase 7 cycle 内 三者監査 | 軍師 + デコポン + ジェミちゃん (システム整合性) | Phase 7 cycle 毎 | 本ドラフトを参照資料として使う |
| `cmd_passport_rls_audit_001` (推奨別 cmd) | 軍師主導、Codex/Gemini 並走 | 他院展開前 | 本ドラフト §2.4 / §6.2 を発展 |
| 法令最終総合監査 | ジェミちゃん主導 | 全機能完成後 | 本ドラフト §7.2 範囲、別 cmd |

---

## 8. Phase 7 本実装着手前のチェックリスト

Phase 7 cmd 発令時に家老が必ず確認する項目 (本ドラフト承認後の運用):

- [ ] **`cmd_passport_engine_consolidation_001` 完了** (Phase 7 ドラフト確定版 §5.1)
- [ ] **passport_* テーブルの実 Supabase RLS 状態確認** — `list_tables` + `get_advisors` で現状取得 (本ドラフト §2.2 の不明箇所を確定)
- [ ] **passport_xp_log / passport_stamp_log / passport_mission_log の `source_event_ref` カラム + UNIQUE 設定確認** (idempotency 設計の前提、本ドラフト §4.2)
- [ ] **passport_members に `parent_consent_at` / `parent_consent_method` カラム存在確認**、なければ Phase 7 着手前に migration (Phase 7 ドラフト §5.3)
- [ ] **engine の全 member_id 受領メソッドに `caller_clinic_id` 引数追加プラン**を Phase 7 タスク YAML に明記 (本ドラフト §3.4 CRITICAL)
- [ ] **passport_event_dlq テーブル新規作成 migration** を Phase 7 cycle1 範囲に含める (本ドラフト §4.1 / §6.1)
- [ ] **エラーコード ERR-PASSPORT-RLS-001〜010 を `docs/error_codes.md` に登録**する別タスク (本ドラフト §4.3)
- [ ] **pgTAP / 手動 SQL シナリオ RT01〜RT10 のテストファイル作成段取り** (本ドラフト §5.2)
- [ ] **§17.8 ロール体系 (`hq_shogun_ai` 等) は Phase 7 単独では未実装、`cmd_passport_rls_audit_001` で別 cmd 化** を家老が認識
- [ ] **既存 `USING (true)` パターンを passport_* で踏襲しない** こと、足軽実装者へ明示 (本ドラフト §6.3)
- [ ] **法令最終総合監査の境界**を Phase 7 範囲に含めない、別 cmd で対応 (本ドラフト §7.3)
- [ ] **Phase 6 統合テスト計画書 (commit 4037717) E2E-12.4 との整合**確認

---

## 9. Phase 7 ドラフト確定版 §5.2 との対応関係

本ドラフトは Phase 7 ドラフト確定版 (commit ca69709) §5.2 を実装視点に具体化したもの。対応関係は以下:

| Phase 7 ドラフト §5.2 記述 | 本ドラフト具体化箇所 |
|------------------------|------------------|
| `passport_members.clinic_id` で分離されているはず | §2.2 (要 Supabase 直接確認、現状未確定) |
| visit_id → passport_members lookup 時、両方の clinic_id 一致検証必須 | §3.1 V1〜V3 + §3.4 V4 |
| C2 sync 時 mismatch 検出フロー: WARN ログ + `passport_event_dlq` 移動 + dashboard 集計 | §4.1 (DLQ 設計) + §6.1 (DDL 雛形) |
| `cmd_passport_rls_audit_001` 別 cmd 推奨 | §2.4 + §6.2 (将来 RLS policy 雛形) + §8 (別 cmd 化チェック) |

---

## 10. 改訂履歴

| 版 | 日時 | 変更内容 | 起草者 |
|----|------|---------|-------|
| draft-001 | 2026-05-07 | 初稿。Phase 7 ドラフト確定版 §5.2 を実装視点に具体化。RLS 棚卸し / 検証ポイント / DLQ 設計 / pgTAP 戦略 / 法令最終監査境界を整備 | ashigaru2 |

---

**注**: 本ドラフトは概念設計のみ。実装着手は Phase 7 cmd 発令後、家老の指示によること。本ドラフトは Phase 7 cmd 発令時の参照資料。`cmd_passport_engine_consolidation_001` (統廃合) 完了 + 本ドラフト軍師レビュー PASS が Phase 7 本実装着手の前提条件でござる。
