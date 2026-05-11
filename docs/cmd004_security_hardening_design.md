# cmd_004 Security Hardening Infra 設計書 (= secret + dep audit + SAST + rate limit、根本治療原則整合構造改善)

- task_id: subtask_cmd004_security_hardening_infra
- parent_cmd: cmd_004
- bloom_level: L4
- 文書種別: **設計書 + 運用 runbook**
- author: ashigaru3 (= 滝川一益、Phase 6 自然進化)
- preflight: /mnt/c/Projects/hakudokai-dev/ + multi-agent SC WSL access 確認済
- 前提 (= 既設計 / 既実装):
  - `scripts/validate_report_privacy.py` — secret/PII pattern 検出 (cmd_013、Phase 5 で runtime filter にも転用)
  - `backend/services/observability/pii_filter.py` (Phase 5) — runtime secret redact
  - `backend/services/web_reservation/rate_limiter.py` — slowapi 既稼働 (web_reservation のみ)
  - `backend/requirements.txt` — slowapi 既存
  - `queue/reports/ashigaru7_cmd004_clinic_id_hardcode_eradication_design_final.yaml` — pre-commit framework 設計 (実装未着手)
  - `docs/cmd004_notification_facade_design.md` (Phase 4) — alert dispatch
  - `docs/cmd004_observability_design.md` (Phase 5) — alert routing 統合点
- 本書 deliverable:
  - `/mnt/c/Projects/hakudokai-dev/.pre-commit-config.yaml` (= 新規、ashigaru7 設計 hook を placeholder 予約 + secret hook 実装)
  - `/home/hakudokai/projects/multi-agent-shogun-newbuild/.pre-commit-config.yaml` (= 新規、multi-agent 側 secret hook)
  - `scripts/lint/check_secrets.sh` (= staged file に validate_report_privacy.py を適用する pre-commit wrapper)
  - `scripts/lint/dependency_audit.sh` (= pip-audit + npm audit を runnable、CI gate drafted)
  - `backend/.bandit` (= SAST 設定)
  - `backend/services/security/rate_limiter.py` (= 集約 limiter、PII 経路用)
  - `backend/services/security/__init__.py`
  - `backend/tests/test_security_hardening.py`
- updated: 2026-05-11

---

## 0. 範囲・非範囲

### 0-1. 含む

- secret 管理規範 + pre-commit hook (= staged file の secret detection)
- dependency audit (pip-audit + npm audit) の runnable script + CI gate 設計
- SAST 設定 (bandit + eslint-plugin-security 推奨)
- rate limiting (slowapi) を PII 経路に統合適用
- ashigaru7 pre-commit framework との duplicate 回避 (= 同 config に共存)
- secret 漏洩 negative test + dependency audit dry-run + rate limit 検証

### 0-2. 含まない

- secret vault / KMS 統合 (= AWS Secrets Manager 等、provider 統合は OD-SEC-1)
- SBOM 生成 / SLSA (= ops 後段、OD-SEC-2)
- WAF / DDoS 防御 (= infrastructure 層、OD-SEC-3)
- 認証 (= OIDC / SAML) refactor (= cmd_002 + ashigaru4 領域)
- ESLint plugin 実装 (= ashigaru7 framework 担当)

---

## 1. 根本治療原則整合 self-check

| 規範 | 否認パターン | 本書採用 |
|------|------------|---------|
| 規範1 (短期 hack 厳禁) | secret は .env で「気をつける」のみ | pre-commit hook で staged file 機械検査 |
| 規範2 (局所修正禁、構造改善優先) | 個別 endpoint に rate limit decorator 散在 | 集約 `backend/services/security/rate_limiter.py` で limit policy を 1 か所定義 |
| 規範3 (将来運用安定優先) | dep audit は本番事故時に手動 | runnable script + CI gate draft + weekly schedule 設計 |
| 規範4 (仕組み追加 vs 改修区別) | bandit / pip-audit を必須化 | optional install + script の中で `command -v` で graceful skip、requirements.txt 表明のみ |
| 規範5 (代替提示 + 永続追記) | scope 外要求は黙殺 | OD-SEC-* で後続申し送り |
| 評価基準 | unit test だけ | secret 漏洩 negative + rate limit hit/miss + dep audit dry-run + pre-commit integration test |

---

## 2. AC1 — secret 管理 inventory + pre-commit hook

### 2-1. 既 secret 一覧 (= 集約規範)

| secret | 配置 | 規範 |
|--------|------|------|
| `ANTHROPIC_API_KEY` | `/home/hakudokai/.config/codex/.env` (個別 PC)、commit 含めず | env_only |
| `VAPID_PRIVATE_V{N}` | Supabase Secrets (= `vapid_key_versions.secret_name` 参照) | secrets_manager_only |
| HMAC secret (QR token) | env / secrets | env_only |
| Supabase service role key | env | env_only |
| ntfy auth (Bearer / Basic) | `config/ntfy_auth.env`、`.gitignore` 済 | env_only |

**集約規範**: 全 secret は env_only または secrets_manager_only、commit 含めず。`.gitignore` で `.env*` を block、追加で **pre-commit hook で staged file の secret pattern を機械検査**。

### 2-2. pre-commit hook 構造 (= ashigaru7 framework 共存)

両 repo に `.pre-commit-config.yaml` を起案。ashigaru7 clinic_id hook (= 設計済、実装未着手) のための **placeholder** を共存 slot として予約。

`/mnt/c/Projects/hakudokai-dev/.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: secret-detect-staged
        name: secret/PII detection on staged files (cmd_004 Phase 6)
        entry: bash scripts/lint/check_secrets.sh
        language: system
        pass_filenames: true
        stages: [pre-commit, pre-push]

      # ─── ashigaru7 framework placeholder (= clinic_id eradication design_final 由来) ───
      # ashigaru7 phase 3 batch 1 で uncomment + scripts/lint/check_clinic_id_hardcode.sh 実装後 有効化。
      # 本 task で先行実装すると責任越境のため slot 予約のみ。
      # - id: clinic-id-backend-grep
      #   ...
      # - id: clinic-id-frontend-eslint
      #   ...
```

`/home/hakudokai/projects/multi-agent-shogun-newbuild/.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: secret-detect-staged
        name: secret/PII detection on staged files (cmd_004 Phase 6)
        entry: bash scripts/lint/check_secrets.sh
        language: system
        pass_filenames: true
        stages: [pre-commit, pre-push]
```

### 2-3. check_secrets.sh — staged file scan

`scripts/lint/check_secrets.sh`:
- 引数 = pre-commit が渡す staged file path 列
- 各 file を `scripts/validate_report_privacy.py` の HIGH pattern (= subset) で scan
- HIGH 検出時 exit 1 → commit reject
- file が .env / .gitignore-d な場合 skip

これにより既 validate_report_privacy.py を **CI gate 層** と **pre-commit 層** の 2 段で使用、Phase 5 の runtime filter と 3 層構造 (= pre-commit / CI / runtime)。

---

## 3. AC2 — dependency audit

### 3-1. tool

| layer | tool | 用途 |
|-------|------|------|
| backend (Python) | `pip-audit` | requirements.txt の CVE スキャン |
| backend (Python) 代替 | `safety` | pyup.io DB ベース、補完 |
| frontend (Node) | `npm audit` | package-lock.json の CVE |
| weekly | GitHub Actions schedule (= 別 ops task) | OD-SEC-4 |

### 3-2. script

`scripts/lint/dependency_audit.sh`:
```
1. command -v pip-audit → 存在時のみ実行 (= optional install、規範4 整合)
2. pip-audit -r backend/requirements.txt --strict / 非ゼロ exit を上位 capture
3. cd frontend && npm audit --audit-level=high / 非ゼロ exit を上位 capture
4. 両方の summary を stdout、CI で fail
```

未 install 環境では skip、警告のみ。

### 3-3. CI gate (= ドラフト、本書 scope 内は script、GitHub Actions yaml は OD-SEC-4)

```
on: [pull_request, push]
jobs:
  audit:
    steps:
      - run: pip install pip-audit
      - run: bash scripts/lint/dependency_audit.sh
```

---

## 4. AC3 — SAST

### 4-1. backend bandit

`backend/.bandit`:
```
[bandit]
exclude_dirs = ["tests", ".venv"]
skips = ["B101"]  # assert_used (test 内 assert は許可)
```

実行: `bandit -r backend -c backend/.bandit`、CI gate 化は OD-SEC-5。

### 4-2. frontend eslint-plugin-security

設計のみ — `eslint.config.js` に `eslint-plugin-security` を追加する手順を docs §4-3 に記載。実装は ashigaru7 framework と統合 (= ESLint config 改修は ashigaru7 領域)。

### 4-3. 推奨 ESLint config 追加

```javascript
import security from 'eslint-plugin-security';
export default [
  // ... 既設定 ...
  security.configs.recommended,
];
```

---

## 5. AC4 — rate limiting + 認証 hardening

### 5-1. 集約 limiter

`backend/services/security/rate_limiter.py`:
- 既 `backend/services/web_reservation/rate_limiter.py` の slowapi Limiter を **2 つ目** として import、共通 Limiter を**集約再エクスポート** (= API 経路重複させず)
- PII 経路用の 専用 policy 定数を定義:
  - `PATIENT_QR_LIMIT = "20/minute"` (= patient_checkin/qr)
  - `PATIENT_EXPORT_LIMIT = "5/hour"` (= /me/export 等 ashigaru4 portability)
  - `CONSENT_VIEW_LIMIT = "60/minute"`
  - `PUSH_SUBSCRIBE_LIMIT = "10/minute"`

### 5-2. 適用 endpoint

| endpoint | policy | 理由 |
|----------|--------|------|
| `POST /api/patient-checkin/qr` | `PATIENT_QR_LIMIT` | brute-force 抑止 (= ashigaru1 QR token 設計連動) |
| `POST /api/push-notifications` | `PUSH_SUBSCRIBE_LIMIT` | subscribe 過剰防止 |
| `GET /api/patient_consents/*` | `CONSENT_VIEW_LIMIT` | scan 抑止 |
| `/me/export` 等 (= 後段 ashigaru4 portability) | `PATIENT_EXPORT_LIMIT` | data egress 制限 |

### 5-3. 認証 hardening

本 task は rate limit に絞り、認証 (= OIDC / 多要素) は別 task。ただし以下を「規範」として明記:
- 失敗 N 回で IP 一時 block (= 既 slowapi 拡張)
- patient_checkin/qr では token signature 検証 → 失敗時 metric `auth_failure_total{endpoint}` (= Phase 5 observability 連動)

---

## 6. AC5 — テスト方針

### 6-1. secret 漏洩 negative test

- `check_secrets.sh` に AKIA / sk-ant- / Bearer / 5-10 桁 digit を含む temp file を渡す → exit 1
- safe file (= sample yaml without secret) → exit 0
- `--dry-run` mode で list-only

### 6-2. dependency audit dry-run

- `dependency_audit.sh` を bare 環境で起動 → tool unavailable 時 graceful skip + warning
- mock pip-audit return code で fail propagation

### 6-3. rate limit 検証

- TestClient で `POST /api/patient-checkin/qr` を `PATIENT_QR_LIMIT` 超過呼出 → 429
- 制限内 → 200 / 201
- 既 patient_checkin の routes と統合した integration test

### 6-4. SKIP=0

全 test `.skip()` 不使用。bandit / pip-audit / npm audit の実行は CI 側、本 task の test は **script の logic** を unit test。

---

## 7. 実装手順

```
✓ Phase A: inventory — 完了
✓ Phase B: 設計書 — 完了
→ Phase C: 実装
   1. scripts/lint/check_secrets.sh
   2. scripts/lint/dependency_audit.sh
   3. multi-agent + hakudokai-dev の .pre-commit-config.yaml
   4. backend/.bandit
   5. backend/services/security/__init__.py + rate_limiter.py
   6. patient_checkin / push_notifications に rate limit 適用
→ Phase D: pytest
→ Phase E: report
```

---

## 8. Open Items

| OD | 項目 | 申し送り先 |
|----|------|----------|
| OD-SEC-1 | secret vault / KMS 統合 (AWS Secrets Manager / Supabase Vault) | karo (= ops) |
| OD-SEC-2 | SBOM 生成 + SLSA | karo (= ops) |
| OD-SEC-3 | WAF / DDoS 防御 | karo (= ops) |
| OD-SEC-4 | GitHub Actions weekly dep scan workflow | karo (= ops) |
| OD-SEC-5 | bandit / eslint CI gate yaml 起案 | karo (= ops) |
| OD-SEC-6 | ashigaru7 phase 3 batch 1 完遂後の `.pre-commit-config.yaml` clinic_id hook uncomment | ashigaru7 (= 統合) |
| OD-SEC-7 | 認証 failure → observability metric 連動 (= `auth_failure_total{endpoint}`) | karo (= 統合 wiring) |
| OD-SEC-8 | rate limit を `clinic_id_mismatch_detected_total` alert と統合 | karo (= 統合 wiring) |

---

## 9. 結論

本書は cmd_004 security hardening を **構造的根本解決設計** として起案する。secret/dep/SAST/rate limit を ad-hoc でなく規範化、ashigaru7 framework に共存、Phase 5 observability に統合可能 — 実稼働後の retrofit risk を抑止し、根本品質で security layer を確立する。

**ashigaru3 (滝川一益) 設計確認**: 根本治療原則 5 規範 + 評価基準 (test + 法令 + UX 完備) 全整合、構造的根本解決設計。
