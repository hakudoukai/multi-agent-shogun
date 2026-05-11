# cmd_004 患者 engagement analytics dashboard — 設計書

## 1. 目的と原則

cmd_004 小児恐竜王国 (= 照葉歯科) 患者 engagement の集計 metric を
スタッフ向け dashboard で時系列可視化する。

| 原則 | 内容 |
|---|---|
| **根本治療** | 患者 PII を一切出力しない aggregate-only 設計。後工程で安易に「patient_id を加える」拡張を禁ずる物理的構造 (= service 層・router 層・schema の三段で patient identifier を持ち回らない)。 |
| **clinic_id RLS** | 全 query で `clinic_id` 必須・ハードコード禁。`ClinicIdContext` (frontend) → `clinic_id` query param (API) → Supabase RLS の三段で境界制御。 |
| **opt-out 即反映** | `patient_consents.erase_requested_at IS NOT NULL` の患者は member 単位で aggregate から除外。`is_active=false` (撤回) も同様に除外。 |
| **拡張性 chain** | 将来 `consent_type='analytics_aggregate'` を導入する余地を schema 設計に内包 (= consent_gate feature_key `analytics_aggregate` を予約)。 |

## 2. 集計対象 metric

| metric | 由来 table | 集計関数 | 出力 |
|---|---|---|---|
| `xp_sum` | `passport_xp_log.delta_xp` (positive only) | SUM by day | daily series + period total |
| `xp_active_members` | `passport_xp_log.member_id` distinct | COUNT DISTINCT by day | daily series |
| `tier_up_count` | `passport_tier_up_celebrations.created_at` | COUNT by day | daily series + period total |
| `checkin_count` | `patient_checkin_logs.checked_in_at` | COUNT by day | daily series + period total |
| `handover_count` | `handover_notes` (or `handover_archives`) | COUNT by day | daily series + period total |

- 全 metric は **クリニック単位の総量**。患者個別 detail は永遠に出さない。
- `period_days` は 7〜180 の閉区間。default 30。
- 各 daily series 要素は `{date: 'YYYY-MM-DD', value: int}` のみ。

## 3. PII 保護 — 三段防衛

### Layer 1: query 時除外 (= service 層)

```python
def _excluded_member_ids(sb, clinic_id) -> set[str]:
    """erase_requested or is_active=false な patient を passport_members 経由で member_id 化"""
```

`patient_consents` を `patient_id` で join し、`erase_requested_at IS NOT NULL` または
`is_active=false` の patient に紐づく `passport_members.member_id` を弾く。

### Layer 2: response schema (= router 層)

- Pydantic response model に `patient_id` / `member_id` / `patient_no` 列を**型レベルで禁止**。
- `metadata: dict` を返さない (= source_event_ref に patient 識別子が混入する経路を遮断)。

### Layer 3: 出力 scan (= test 層)

backend pytest で `validate_report_privacy.py` の `scan_text` を response body に適用し、
HIGH パターン (absolute path / token / API key) 検出時に test 失敗。

## 4. API 仕様

### GET `/api/analytics/patient-engagement`

```
query:
  clinic_id    : int (required, RLS 越境禁)
  period_days  : int (default 30, range [7, 180])
  end_date     : date (default = today JST)
```

response 200:
```json
{
  "clinic_id": 5,
  "period": {"from": "2026-04-12", "to": "2026-05-11", "days": 30},
  "totals": {
    "xp_sum": 12500,
    "tier_up_count": 18,
    "checkin_count": 234,
    "handover_count": 89,
    "active_members": 47
  },
  "daily_series": {
    "xp_sum":         [{"date": "2026-04-12", "value": 450}, ...],
    "tier_up_count":  [{"date": "2026-04-12", "value": 1},   ...],
    "checkin_count":  [{"date": "2026-04-12", "value": 8},   ...],
    "handover_count": [{"date": "2026-04-12", "value": 3},   ...]
  },
  "privacy": {
    "aggregate_only": true,
    "excluded_members": 2,
    "consent_feature_key": "analytics_aggregate",
    "consent_gate_applied": false
  }
}
```

error:
- 422 — `clinic_id` 不正・`period_days` 範囲外
- 500 — supabase 取得失敗

### RLS 戦略

- `clinic_id` は staff の所属 clinic に限る (= 既 `staff.clinic_id` policy)。
- staff role 以外の auth は 401 (router 側で `auth_middleware` 経由)。
- service-role bypass は禁 (= テスト時のみ mock 経由)。

## 5. Frontend dashboard

### path
`/staff/analytics/patient-engagement` (= 既 admin/staff view 配下、将来 sidebar から導線)

### コンポーネント構成

```
EngagementDashboard (page)
├── ControlBar (period_days selector, end_date picker)
├── KpiCards (totals — xp_sum, tier_up_count, checkin_count, handover_count, active_members)
└── ChartGrid (recharts)
    ├── XpTrendChart       (LineChart, xp_sum daily)
    ├── TierUpBarChart     (BarChart, tier_up_count daily)
    ├── CheckinBarChart    (BarChart, checkin_count daily)
    └── HandoverBarChart   (BarChart, handover_count daily)
```

- `useClinicId()` で `clinic_id` 取得 → API call。
- recharts を採用 (= 既 `AnalyticsDashboard.tsx` と整合、bundle 増加無し)。
- 個別 patient 行列は描画しない。tooltip 表示は date + value のみ。

## 6. 拡張性 chain

| 将来拡張 | 設計上の予約 |
|---|---|
| `analytics_aggregate` consent_type 導入 | `privacy.consent_feature_key` を response に明記 → 将来 gate を有効化しても破壊変更 (= response schema 変更) にならない。 |
| metric 追加 (例: rewards_redeemed) | `daily_series` を dict 形式とし、key 追加だけで frontend が無破壊で受け取れる。 |
| 期間粒度切替 (= week/month rollup) | router 側で `granularity` query を後付け可能。daily series は最小粒度。 |
| 院横断 view (= shogun KPI) | `clinic_id=0` で全院集計、ただし RLS で staff 多院兼務時のみ許可。本 phase は対象外。 |

## 7. test 戦略

### backend pytest

| test name | 検証 |
|---|---|
| `test_happy_path_returns_aggregate_only` | response に patient_id 等 PII 列が皆無 |
| `test_excluded_erase_requested_patients` | erase_requested_at>0 の patient の xp/checkin/handover が一切混入しない |
| `test_clinic_id_required` | clinic_id 欠落で 422 |
| `test_period_days_out_of_range` | period_days=0 / 365 で 422 |
| `test_validate_report_privacy_scan` | response 全文を `scan_text` に通し HIGH 件数 0 |
| `test_daily_series_zero_fill` | 該当日に event 無くても date が daily_series に出現 (= time-series gap 回避) |

### frontend vitest

| test name | 検証 |
|---|---|
| `EngagementDashboard renders KPI cards` | totals 4 種 + active_members 描画 |
| `EngagementDashboard renders 4 charts` | recharts 4 種が描画 |
| `EngagementDashboard handles period change` | period_days セレクタ操作で API 再 fetch |
| `EngagementDashboard does not leak PII` | snapshot に patient_id 文字列が出現しない |

## 8. ファイル配置

```
backend/services/engagement_analytics_service.py  # 集計 pure functions
backend/routers/engagement_analytics.py           # FastAPI router
backend/tests/test_engagement_analytics.py        # pytest
frontend/src/services/engagementAnalyticsApi.ts   # API client
frontend/src/pages/EngagementAnalyticsDashboard.tsx
frontend/src/__tests__/engagement_analytics/EngagementAnalyticsDashboard.test.tsx
```

migration は不要 (= 既 table のみ利用)。

## 9. 非目標

- 個別患者の engagement 詳細 (= patient timeline)
- 商用利用・第三者提供 (= 根本治療原則「analytics は患者 engagement 改善のみ」遵守)
- 認証層の改修 (= 既 auth_middleware を踏襲)
- 多 clinic 横断比較 (= 本 phase 対象外、§6 拡張性 chain に記載)
