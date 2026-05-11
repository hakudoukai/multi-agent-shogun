# cmd_004 観測性 infra 設計書 (= logs + metrics + traces + alerts、根本治療原則整合構造改善)

- task_id: subtask_cmd004_observability_infra
- parent_cmd: cmd_004
- bloom_level: L4
- 文書種別: **設計書 + 運用 runbook** (= 構造的根本解決設計、実稼働後 retrofit 不可な観測性 layer を初版で完備)
- author: ashigaru3 (= 滝川一益、SC WSL hakudoukai@gmail.com、Phase 5)
- preflight: /mnt/c/Projects/hakudokai-dev/ + multi-agent SC WSL access 確認済
- 前提 (= 既設計 / 既実装):
  - `docs/cmd004_notification_facade_design.md` (Phase 4) — NotificationFacade、AlertRouter 配信経路
  - `scripts/validate_report_privacy.py` — PII / secret pattern 検出器 (cmd_013 由来)
  - `scripts/ntfy.sh` + `scripts/auto_git_sync.sh` — 既 log 出力 source
  - `backend/main.py` — FastAPI app、`logging.getLogger(__name__)` ベースの flat log
  - `frontend/src/patient-app/hooks/useOfflineQueue.ts` (Phase 3) — Web Push delivery のクライアント可観測点
- 本書 deliverable:
  - `backend/services/observability/__init__.py` (= 新規) — 公開 API export
  - `backend/services/observability/logging_config.py` (= 新規) — 構造化 JSON logger + PII filter
  - `backend/services/observability/pii_filter.py` (= 新規) — logging.Filter (= validate_report_privacy.py の pattern を実行時 redact)
  - `backend/services/observability/metrics.py` (= 新規) — Prometheus registry + custom metric 定義 + optional import fallback
  - `backend/services/observability/middleware.py` (= 新規) — FastAPI HTTP 計測 middleware
  - `backend/services/observability/alert_router.py` (= 新規) — AlertRouter (= NotificationFacade 経由 admin alert)
  - `backend/tests/test_observability.py` (= 新規) — pytest
  - `requirements.txt` (= 改修) — prometheus_client optional 追加 (= 仕組み追加点、明示)
- updated: 2026-05-11

---

## 0. 範囲・非範囲

### 0-1. 本書の範囲

| 項目 | 含む |
|------|------|
| 観測性 3 pillar (= logs / metrics / traces) inventory | ○ |
| 構造化 JSON log 規約 + PII filter (= validate_report_privacy.py 適用) | ○ |
| Prometheus metric 設計 + optional import fallback | ○ |
| FastAPI middleware (= HTTP request 計測) | ○ |
| custom metric (= consent_version 利用率 / clinic_id mismatch / notification 配信成功率) | ○ |
| AlertRouter (= NotificationFacade 連動 admin alert) | ○ |
| PII 漏洩 negative test 方針 | ○ |
| 既 ntfy.sh / auto_git_sync.sh / supabase log との sink chain | ○ |

### 0-2. 本書の非範囲

| 項目 | 非範囲理由 |
|------|-----------|
| distributed tracing (= OpenTelemetry 全面導入) | 仕組み追加 task、本書では interface のみ stub |
| log aggregation 外部 sink (= Loki / ELK / Vector) | provider 統合、後段 ops task |
| Grafana dashboard | UI 領域、別 task |
| ashigaru4 patient delete audit | 連動点のみ明記、実装は別 task |
| SLO / SLI 経営目標 | 別 layer、本書は infra 層に絞る |

---

## 1. 根本治療原則整合 self-check

### 1-1. 「とりあえず動く」回避

陛下御差配 msg_20260511_164625 で「個別 ad-hoc log 禁、3 pillar 構造化 + sink + alert routing」と通達。本書は以下で整合:

| 規範 | 安易な実装 (= 否認) | 本書採用 (= 根本治療) |
|------|-------------------|--------------------|
| 規範1 (短期 hack 厳禁) | `print()` / `logger.info()` 散在、JSON 化 ad-hoc | 統一 JSON formatter + PII filter handler、全 logger に attach |
| 規範2 (局所修正禁、構造改善優先) | 個別 endpoint に metric 計測 inline | middleware で横断計測 + custom metric は collector に集約 |
| 規範3 (将来運用安定優先) | metric は後付け | initial 段階で 5 種 standard + 3 種 custom を確定、prometheus 形式で永続化 |
| 規範4 (仕組み追加 vs 改修区別) | prometheus を必須化、import 失敗で起動不能 | **optional import**、不在時は no-op stub registry、requirements.txt は dependency 表明のみ |
| 規範5 (代替提示 + 永続追記) | scope 外要求は黙殺 | OD-OBS-* で後続申し送り (= Loki sink / OpenTelemetry / Grafana 等) |
| 評価基準 (test + 法令 + UX 完備) | metric だけ test | PII 漏洩 negative test + alert trigger e2e + 既 facade regression |

### 1-2. PII 保護 chain

3 pillar の全 path で `validate_report_privacy.py` の HIGH/WARN pattern を適用:

```
Application code
  ↓ logger.info(...)
PII Filter (= logging.Filter)
  ↓ pattern detected → redact (例: "AKIA*****")
JSON Formatter
  ↓ structured record
Sink (= stdout / file / loki ※ OD-OBS-1)
```

metric は label に PII を含めない設計 (= 例: `notification_delivery_total{channel="webpush", status="sent"}` のみ、`patient_id` は label にしない)。

---

## 2. AC1 — 観測性 3 pillar inventory

### 2-1. logs

| Source | 現状 | 改修方針 |
|--------|------|---------|
| `backend/main.py` + 各 router | `logging.getLogger(__name__)`、flat text | JSON formatter + PII filter を root logger に attach |
| `scripts/ntfy.sh` | stdout/stderr のみ | 改修不要 (= 内部 admin、PII 流入無し) |
| `scripts/auto_git_sync.sh` | `queue/reports/auto_sync_log.yaml` | 既 yaml、本書 scope 外 |
| `scripts/ntfy_listener.sh` | tmux + stdout | 改修不要 |
| frontend console.error | shim 既存 (= test/setup.ts) | OD-OBS-3 で sink 化検討 |
| supabase logs | hosted | OD-OBS-1 で aggregate sink 連動 |

### 2-2. metrics

| 区分 | source | 採用 |
|------|--------|------|
| HTTP request | FastAPI middleware (= 新規 ObservabilityMiddleware) | `http_requests_total` / `http_request_duration_seconds` |
| Notification | facade audit_log callback | `notification_delivery_total{channel,status}` |
| Consent | patient_consents (= Phase 4 と連動) | `consent_versioning_active_total{version}` |
| Cross-clinic 漏洩 | SW + backend cache check | `clinic_id_mismatch_detected_total{layer}` |
| Web vitals (frontend) | 後段、`OD-OBS-2` | (本書 scope 外) |

### 2-3. traces

本書 scope 外、interface のみ用意:
- `traceparent` header 受領した場合に log の `corr_id` に転写
- OpenTelemetry の本格導入は OD-OBS-4

---

## 3. AC2 — 構造化 JSON log + PII filter

### 3-1. JSON formatter 設計

```python
{
  "ts": "2026-05-11T17:30:00Z",
  "level": "INFO",
  "logger": "backend.routers.push_notifications",
  "msg": "push_subscription_created",
  "clinic_id": 5,
  "corr_id": "...",
  "extra": { ... 任意の key=value ... }
}
```

- `ts` は UTC ISO 8601 (= timezone-aware)
- `extra` は record `extra={...}` 経由でのみ、record の record-level attributes が JSON 化
- `msg` は機械処理可能な event 名 (= snake_case 推奨)、自然言語パラメタは extra へ

### 3-2. PII filter 実装方針

`logging.Filter` を root logger に attach、validate_report_privacy.py の `HIGH_PATTERNS` を再利用し、record の `msg`/`args`/`extra` に対して redact。redact pattern は `**REDACTED:{pattern_name}**` で痕跡を残し、検出回数 metric (= `pii_filter_redactions_total{pattern}`) を増分。

### 3-3. 検証 (= negative test)

- `logger.info("AKIA1234567890ABCDEF emitted")` を発火、フォーマット後 record に `AKIA...` 文字列が含まれていないことを検証
- 同じく `Bearer aXXXX...`、`/home/hakudokai/...`、5-10 桁の連続 digit を redact 確認

---

## 4. AC3 — Prometheus metric (optional import)

### 4-1. optional import pattern

```python
try:
    from prometheus_client import Counter, Histogram, CollectorRegistry, REGISTRY
    _PROMETHEUS_AVAILABLE = True
except ImportError:
    _PROMETHEUS_AVAILABLE = False
    # stub: 同じ API surface を持つ no-op classes
    class _NoOp:
        def labels(self, **_): return self
        def inc(self, *_): pass
        def observe(self, *_): pass
    Counter = Histogram = lambda *_a, **_kw: _NoOp()
    CollectorRegistry = REGISTRY = None
```

これにより:
- prometheus_client install 済 → 実 metric 動作
- 未 install → no-op stub、app は起動失敗しない (= 規範4 整合)
- requirements.txt には依存表明あり、本番では install 推奨

### 4-2. standard metric set

| metric | type | labels | 用途 |
|--------|------|--------|------|
| `http_requests_total` | Counter | `method, path, status` | HTTP request 計数 |
| `http_request_duration_seconds` | Histogram | `method, path` | latency |
| `notification_delivery_total` | Counter | `channel, status` | facade dispatch 結果 |
| `consent_versioning_active_total` | Counter | `version` | consent_version 利用率 |
| `clinic_id_mismatch_detected_total` | Counter | `layer` | cross-clinic 漏洩検知 |
| `pii_filter_redactions_total` | Counter | `pattern` | PII filter 検出回数 |

### 4-3. middleware

`ObservabilityMiddleware` (= BaseHTTPMiddleware) で:
1. request 受信時に timer start
2. response 確定後 `http_requests_total{method,path,status}.inc()`
3. duration を `http_request_duration_seconds{method,path}.observe()`
4. path は `request.url.path` の dynamic id (例: `/api/patients/{id}`) を generic 化 (= path template 抽出)

---

## 5. AC4 — Alert routing (= NotificationFacade 経由)

### 5-1. AlertRouter

```python
class AlertRouter:
    def __init__(self, facade: NotificationFacade, clinic_id: int): ...
    def fire(self, rule: AlertRule) -> None: ...
```

`rule` は dataclass:

```python
@dataclass
class AlertRule:
    name: str                # 'error_rate_spike' / 'consent_violation' / 'clinic_id_leakage'
    severity: Severity       # NORMAL/HIGH/EMERGENCY
    title: str
    body: str
    metric_snapshot: dict[str, Any] = field(default_factory=dict)
```

`fire()` 内で:
1. `Recipient(type=ADMIN, clinic_id=...)` を組み立て
2. `NotificationContext(trigger_id=f'alert:{rule.name}', severity=...)` を渡す
3. `facade.notify(...)` を await
4. 結果を `alert_router_fired_total{rule,delivered}` で計測

### 5-2. 標準 rule

| rule.name | trigger | severity |
|-----------|---------|---------|
| `error_rate_spike` | `http_requests_total{status=~"5.."}` 増分閾値超 | HIGH |
| `consent_violation` | facade dispatch で `consent_missing` を 1 回でも観測 | EMERGENCY |
| `clinic_id_leakage` | `clinic_id_mismatch_detected_total` 増分 ≥1 | EMERGENCY |
| `patient_delete_request` | ashigaru4 連動 hook | HIGH |

本書では `fire()` の dispatch 経路 + 上記 4 rule の `AlertRule` 定数を提供。閾値検知 cron は OD-OBS-5。

---

## 6. AC5 — テスト方針

### 6-1. PII 漏洩 negative test

- AKIA / sk-ant- / sk- / Bearer / `/home/`-path / 5-10 桁 digit を logger に流し、formatter 出力に **含まれない** ことを assert
- `pii_filter_redactions_total` インクリメントを確認

### 6-2. metric test

- `MetricsRegistry` (= stub 経路含む) で `http_requests_total` の labels と inc が想定通り
- middleware が path-template を抽出 (= `/api/patients/abc` → `/api/patients/{id}`)
- optional import 不在環境でも no-op、app 起動継続

### 6-3. alert trigger test

- AlertRouter.fire(rule=consent_violation) → facade.notify 呼出が 1 度
- recipient.type == ADMIN
- delivered_via 検証 (= stub adapter 使用)

### 6-4. SKIP=0

全 test `.skip()` 不使用。stub 経路で全 case 実行可能。

---

## 7. 実装手順

```
✓ Phase A: inventory — 完了
✓ Phase B: 設計書 — 完了
→ Phase C: 実装
   1. pii_filter.py
   2. logging_config.py (= JSON formatter + filter attach)
   3. metrics.py (= optional import + standard set)
   4. middleware.py (= HTTP 計測)
   5. alert_router.py (= NotificationFacade 連動)
   6. __init__.py (= public API)
   7. requirements.txt 更新
→ Phase D: pytest
→ Phase E: report + karo
```

---

## 8. Open Items

| OD | 項目 | 申し送り先 |
|----|------|----------|
| OD-OBS-1 | 外部 log sink 統合 (= Loki / Vector / ELK) | karo (= ops、provider 統合) |
| OD-OBS-2 | frontend web-vitals + RUM | ashigaru? (= UI subtask) |
| OD-OBS-3 | frontend console.error → sink ship | karo (= 後続) |
| OD-OBS-4 | OpenTelemetry tracing 全面導入 | karo (= 仕組み追加 task) |
| OD-OBS-5 | metric 閾値 cron + 動的 rule 設定 UI | karo (= ops) |
| OD-OBS-6 | Grafana dashboard provisioning | karo (= ops) |
| OD-OBS-7 | supabase log と app log の corr_id 突合 | karo (= ops) |

---

## 9. 結論

本書は cmd_004 観測性 infra を **構造的根本解決設計** として起案する。logs/metrics/traces 3 pillar を初版で確定、PII filter で個情法 + 機密保護を入口で gating、AlertRouter で Phase 4 NotificationFacade に統合 — 実稼働後の retrofit 不可な観測性 layer を完備品質で構築する。

**ashigaru3 (滝川一益) 設計確認**: 根本治療原則 5 規範 + 評価基準 (test + 法令 + UX 完備) 全整合、構造的根本解決設計。
