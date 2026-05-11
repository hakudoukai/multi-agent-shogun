# cmd_004 小児恐竜王国 VAPID key 管理 / push infra 運用 runbook

- task_id: subtask_cmd004_push_vapid_infra
- parent_cmd: cmd_004 (小児恐竜王国)
- bloom_level: L4
- 文書種別: **運用 runbook** (= 設計は別文書、本書は実装/運用手順)
- author: ashigaru3 (= 滝川一益、SC WSL hakudoukai@gmail.com)
- preflight: /mnt/c/Projects/hakudokai-dev/ SC WSL access 確認済
- base 既存資産 (= 改変禁、本書はこの設計を実装する側):
  - `docs/kids_app_push_ceremony_detail_design.md` §1 / §2 / §8 (信長手動再構築 v0.1) — **VAPID/SW/DDL の正本**
  - `docs/cmd004_guardian_consent_spec.md` (= ashigaru4 並行起案、保護者同意 gate の正本)
  - `supabase/migrations/20260509_patient_consents_schema.sql` (= consent_type='push_notification' を保持)
- 本書実装 deliverable:
  - `supabase/migrations/20260511_cmd004_push_subscriptions_schema.sql` (= 新規)
  - `backend/routers/push_notifications.py` (= 新規) + `backend/main.py` 登録 1 行
  - `frontend/public/patient-sw.js` (= push/notificationclick handler 追加)
  - `frontend/src/services/patientAppApi.ts` (= subscribePush / getVapidPublicKey / revokePushSubscription 追加)
  - `frontend/src/patient-app/hooks/usePushSubscription.ts` (= 新規)
  - `backend/tests/test_push_notifications_router.py` (= 新規)
- updated: 2026-05-11

---

## 0. 範囲・非範囲

### 0-1. 本書の範囲

| 項目 | 含む |
|------|------|
| VAPID 鍵 90 日 rotation runbook (実コマンド付) | ○ |
| 緊急 revoke (漏洩検知時) 手順 | ○ |
| Supabase Secrets 配置と参照経路 | ○ |
| 多層保管 (Production / Dev / fallback) と禁止事項 | ○ |
| 監査ログ (vapid_key_access_log) 検査 query | ○ |
| 保護者同意 gate との結合点 (= subscribe 時の re-check) | ○ |
| 既 ntfy.sh 系列との分離 (= 患者向け Web Push vs 内部 admin 通知) | ○ |
| 法令准拠 audit trail (5 年保管) の現状と未対応点 | ○ |

### 0-2. 本書の非範囲

| 項目 | 非範囲理由 |
|------|-----------|
| ceremony 演出 (CeremonyOverlay 5 種) | `kids_app_push_ceremony_detail_design.md` §3 / ashigaru5 ゲーム詳細設計 |
| 保護者同意 UI フロー詳細 | `cmd004_guardian_consent_spec.md` (= ashigaru4 担当) |
| send_push 実装 (= 配信側の retry / rate limit) | 後続 task。本書は subscribe 側のみ |
| LINE Bot / メール fallback | `kids_app_push_ceremony_detail_design.md` §5、後続 |
| WORM mirror による 5 年保管自動化 | 後続 task。本書では migration + log table を起案するのみ |

---

## 1. 既 push 通知系統 inventory (= AC1)

### 1-1. 多経路の分離原則

| 経路 | 用途 | 実装 | 認証 |
|------|------|------|------|
| `scripts/ntfy.sh` (multi-agent shogun infra) | **内部 admin 通知** (shogun ↔ agents、ntfy.sh 経由でスマホ) | `scripts/ntfy.sh` + `scripts/ntfy_listener.sh` + `lib/ntfy_auth.sh` | Bearer / Basic auth、topic 単位 |
| Web Push (cmd_004 本書対象) | **患者向け Push** (= dinosaur_kingdom 通知、ceremony 起動、PWA notification) | `backend/routers/push_notifications.py` + `frontend/public/patient-sw.js` | VAPID (= P-256 ECDSA 鍵ペア) |

**完全分離**: ntfy.sh は外部サービス (ntfy.sh) 経由の本能寺向け軽量通知、Web Push は患者 PWA への WebPush 標準 (RFC 8030)。**互いに依存しない**。

### 1-2. 既存資産 (= 改変禁の上で活用)

| 区分 | path | 状態 |
|------|------|------|
| Service Worker | `frontend/public/patient-sw.js` | 既存 cache 戦略保持 + 本実装で push/notificationclick handler **追記** (Path A、最小改変) |
| PWA manifest | `frontend/public/patient-manifest.json` | 改変なし |
| 同意 schema | `supabase/migrations/20260509_patient_consents_schema.sql` | `consent_type='push_notification'` 既登録、本実装で `is_active=true` を gate に使用 |
| 同意 router | `backend/routers/patient_consents.py` | 既存 endpoint そのまま、本実装は `_has_push_consent()` で参照のみ |
| 同意 UI | `frontend/src/patient-app/pages/ConsentForm.tsx` | 既存 `CONSENT_ITEMS` に `push_notification` 登録済、本実装の前提を満たす |
| Patient identity | `patients` table | 本実装の `push_subscriptions.patient_id` 外部キー先 |

### 1-3. 新規追加 (= 本実装で起案)

| 区分 | path | 内容 |
|------|------|------|
| supabase migration | `supabase/migrations/20260511_cmd004_push_subscriptions_schema.sql` | `vapid_key_versions` / `vapid_key_access_log` / `push_subscriptions` / `push_delivery_log` |
| backend router | `backend/routers/push_notifications.py` | 4 endpoint (vapid-public-key / subscribe / list / revoke) |
| backend main 登録 | `backend/main.py` L135 + L383 | 1 行ずつ追加 |
| frontend SW patch | `frontend/public/patient-sw.js` | push + notificationclick 追記、`CACHE_NAME = 'dentalbi-patient-v2'` 改版 |
| frontend API client | `frontend/src/services/patientAppApi.ts` | getVapidPublicKey / subscribePush / revokePushSubscription |
| frontend hook | `frontend/src/patient-app/hooks/usePushSubscription.ts` | permission / subscribe / unsubscribe / state |
| test | `backend/tests/test_push_notifications_router.py` | 7 ケース (vapid 取得 / consent gate / 新規登録 / 重複 / revoke 成功 / 二重 revoke 409 / 503) |

---

## 2. VAPID 鍵管理 (= SoT 設計 §1 の運用具現)

### 2-1. 鍵生成

P-256 ECDSA (= `web-push` 互換)。openssl 1 行で生成可:

```bash
# 秘密鍵 (DER) → Base64URL 
openssl ecparam -name prime256v1 -genkey -noout -out vapid_v2_priv.pem
openssl ec -in vapid_v2_priv.pem -outform DER 2>/dev/null \
  | tail -c +8 | head -c 32 \
  | base64 | tr -d '=' | tr '/+' '_-'

# 公開鍵 (uncompressed 65 bytes) → Base64URL
openssl ec -in vapid_v2_priv.pem -pubout -outform DER 2>/dev/null \
  | tail -c 65 \
  | base64 | tr -d '=' | tr '/+' '_-'
```

または node の `web-push` CLI:

```bash
npx web-push generate-vapid-keys --json
```

### 2-2. Supabase Secrets 配置

```bash
# Production
supabase secrets set VAPID_PRIVATE_V2='<base64url private>' --project-ref pxvnhkiqyxkejzivspde
supabase secrets set VAPID_PUBLIC_V2='<base64url public>' --project-ref pxvnhkiqyxkejzivspde

# vapid_key_versions に登録 (psql or studio)
INSERT INTO vapid_key_versions (version, status, public_key, secret_name, rotated_by)
VALUES (2, 'active', '<base64url public>', 'VAPID_PRIVATE_V2', 'hakudoukai@gmail.com');

UPDATE vapid_key_versions SET status='deprecated', deprecated_at=NOW() WHERE version=1;
```

### 2-3. 90 日 rotation runbook

```
[Day 0]   新鍵 V_new 生成・Secrets 投入・version INSERT (status=active)
          旧鍵 V_old は status='deprecated' (= 過渡期 14 日)
[Day 0-14] 両鍵で送信可。新規 subscribe は V_new、既存 V_old subscription も配信継続
[Day 14]  V_old を status='revoked' に、Secret 削除:
          supabase secrets unset VAPID_PRIVATE_V_old
          UPDATE vapid_key_versions SET status='revoked', revoked_at=NOW() WHERE version=V_old;
[Day 14-90] V_new 単独運用
[Day 90]  次世代 V_next で繰返
```

### 2-4. 緊急 revoke (漏洩検知時)

```bash
# 1. 即座に Secrets を削除 (= 配信不能化)
supabase secrets unset VAPID_PRIVATE_V<n>

# 2. DB で status を 'revoked' に
UPDATE vapid_key_versions SET status='revoked', revoked_at=NOW() WHERE version=<n>;

# 3. 全 subscription を該当 vapid_version で失効
UPDATE push_subscriptions SET revoked_at=NOW() WHERE vapid_version=<n> AND revoked_at IS NULL;

# 4. 監査ログを strong 記録
INSERT INTO vapid_key_access_log (key_version, action, actor, details)
VALUES (<n>, 'revoke', 'hakudoukai@gmail.com', '{"reason": "leak_detected", "incident_id": "..."}'::jsonb);
```

緊急 revoke は ntfy で理事長殿に即時通知 (= multi-agent infra の `scripts/ntfy.sh` を活用してよい、ただし**患者向け Web Push とは別経路**である点を厳守)。

### 2-5. 多層保管モデルと禁止事項

| 環境 | 一次保管 | 二次保管 (fallback) | 平文 file 化 |
|------|---------|--------------------|-------------|
| Production | Supabase Secrets (= AES-256-GCM、service_role からのみ復号) | なし (= fallback なし、Single Source) | **禁止** |
| Dev | Supabase Secrets (Dev project) | `~/.openclaw/vapid_dev.key` (= 600 perm、本番投入禁止フラグ付) | dev only 可、commit 禁止 |

**絶対禁止**:
- VAPID private key を git に commit (= F007 + 本書の禁則)
- `.env` ファイルに `VAPID_PRIVATE_*=...` を平文記載して push (= dev 環境の `~/.openclaw/` 限定運用)
- `*.log` / `*.md` / Slack / Issue / PR description に private key を貼付

---

## 3. 保護者同意 gate との結合 (= 法令准拠)

### 3-1. 結合点

`push_notifications.py:_has_push_consent()` は subscribe 時に以下を検査:

```python
patient_consents
  .clinic_id = req.clinic_id
  .patient_id = req.patient_id
  .consent_type = 'push_notification'
  .is_active = true
```

1 件以上 hit すれば 200/201、なければ **403 + 日本語メッセージ** (= 「保護者同意フローを先に完了してください (個情法 28 条準拠)」)。

### 3-2. send_push 段階での re-check (= 後続実装)

subscribe 時の同意が後日撤回された場合、`push_subscriptions` は残るが `patient_consents.is_active=false`。**配信前に同じ `_has_push_consent()` で re-check すること**を後続 send_push 実装に申し送る。撤回後の subscription は `revoked_at` ではなく consent_missing 状態として `push_delivery_log.status='consent_missing'` に記録する。

### 3-3. 同意撤回 → subscription 連動 (= 後続実装)

`patient_consents.is_active=false` 化時に該当 patient の `push_subscriptions.revoked_at=NOW()` を一括設定する trigger 起案を後続に申し送る (= 本書範囲外、ashigaru4 同意 spec の §5.5 機能 unlock 解除 cascade と連動)。

---

## 4. 監査ログ運用 (vapid_key_access_log)

### 4-1. 記録対象 action

| action | 発生タイミング | actor 例 |
|--------|--------------|---------|
| `read` | send_push で private key 復号時 (= 後続実装) | `service_role` / push_dispatcher worker |
| `rotate` | §2-2 / §2-3 のローテ実行時 | `hakudoukai@gmail.com` |
| `revoke` | §2-4 緊急 revoke / 14 日経過の自動 revoke | `hakudoukai@gmail.com` / cron `vapid_rotation_v1` |
| `failed_decrypt` | 復号失敗 (= 鍵不整合 / 漏洩疑い) | `service_role` |

### 4-2. 定期検査 query

```sql
-- 直近 30 日の rotate / revoke 全件
SELECT key_version, action, actor, occurred_at
FROM vapid_key_access_log
WHERE action IN ('rotate', 'revoke')
  AND occurred_at > NOW() - INTERVAL '30 days'
ORDER BY occurred_at DESC;

-- 直近 24h の failed_decrypt (= 漏洩疑い early warning)
SELECT key_version, actor, ip_address, details, occurred_at
FROM vapid_key_access_log
WHERE action = 'failed_decrypt'
  AND occurred_at > NOW() - INTERVAL '24 hours'
ORDER BY occurred_at DESC;
```

### 4-3. 保管期間

- 即時保管: vapid_key_access_log (= Supabase RLS で service_role 限定)
- 5 年保管要件: 医療法施行規則第 22 条 (= 診療録 5 年) の準用 (要法務確認)
- WORM mirror: 後続 task で `scripts/log_worm_export.py` の対象に本テーブルを追加すること

---

## 5. 既 ntfy.sh 系列との分離設計

### 5-1. 役割分担

| 系列 | 受信者 | 内容例 | 認証 | 配信成功率要件 |
|------|--------|--------|------|---------------|
| ntfy.sh (内部 admin) | 信長殿 / 蔵屋敷 ops | shogun 待機通知、agent 異常、auto_git_sync HALT | Bearer / Basic | 99% (= ntfy.sh SLA) |
| Web Push (患者向け) | 患者・保護者 | 来院リマインド、ceremony (恐竜進化)、明細 PDF 配信 | VAPID + 保護者同意 | 95% + 7 日内再送 (= 設計 §5) |

### 5-2. 共有しないもの

- 認証経路 (= ntfy auth と VAPID は完全別管理)
- 配信履歴 (= `ntfy_inbox.yaml` と `push_delivery_log` は独立)
- rate limit (= ntfy.sh は外部、Web Push は内製 §5 設計)
- 失敗時 fallback (= ntfy.sh failure → 信長 inbox direct write、Web Push failure → LINE/メール後続)

### 5-3. 共有してよいもの

- 緊急 alert の連鎖通知 (= 例: VAPID 漏洩検知時、ntfy.sh で信長殿に即時通知、これは内部 admin 系列の正当な利用)

---

## 6. テスト / preflight

### 6-1. 単体テスト

```bash
cd /mnt/c/Projects/hakudokai-dev
pytest backend/tests/test_push_notifications_router.py -v
```

7 ケース全 pass を本 task 完遂条件とする (= AC5)。

### 6-2. migration apply 前 preflight

```bash
# Dry-run: migration を staging に適用、本番反映前に必ず動作確認
supabase db push --linked --dry-run
```

### 6-3. frontend 動作確認 (= 後続 manual)

- Chrome DevTools → Application → Service Workers で `patient-sw.js` 登録確認
- Application → Manifest → "Push" で test push 受信 (= dev mode の `web-push` CLI)
- 同意未取得状態で subscribe 試行 → 403 を確認 (= consent gate)

---

## 7. 規律遵守 chesckklist

| 項目 | 状態 |
|------|------|
| F007 (commit/push は陛下御差配仰ぐ) | 本実装は commit までで停止、push は陛下御差配 |
| VAPID private key の commit 含めない | secret_name 列のみで private key 値は DB 不在、Secrets 専用 |
| 既存 detail_design を SoT として尊重 | §1/§2/§8 を本実装で参照、独自設計起こさず |
| 保護者同意 gate の law evidence 引用 | 個情法 28 条 を本書 §3 + router error message に明記 |
| Anti-Duplication | `kids_app_push_ceremony_detail_design.md` 既存 → 本書は **運用 runbook + 実装** に特化 |

---

## 8. Open Items (= 後続 task 申し送り)

| OD | 項目 | 申し送り先 |
|----|------|----------|
| OD-PVI-1 | passport_members との FK 連携 (= 現状 patients.id ベース、後続で member_id 拡張) | 軍師 → karo |
| OD-PVI-2 | send_push 実装 (retry / rate limit / fallback) | 後続 subtask、ashigaru 配分要 |
| OD-PVI-3 | WORM mirror 5 年保管自動化 (= push_delivery_log + vapid_key_access_log) | 後続 subtask |
| OD-PVI-4 | 同意撤回 → push_subscriptions cascade revoke trigger | ashigaru4 同意 spec §5.5 と統合 |
| OD-PVI-5 | LINE Bot / メール fallback (= 配信失敗時 multi-channel) | 後続 subtask |
| OD-PVI-6 | 14 日過渡期の自動 revoke cron 起案 | 後続 ops task |

---

## 9. 結論

本書は cmd_004 小児恐竜王国の Web Push infra を **既設計 SoT (= kids_app_push_ceremony_detail_design.md) に忠実に**実装する scaffold を提供する。設計の再起案は行わず、運用 runbook + 実コード として埋める。残課題 6 件は §8 で後続申し送り。

**ashigaru3 (滝川一益) 確認**: 本書 + 実装 6 ファイル + test 7 ケースで本 task の AC1-AC6 を満たす。F007 遵守、push 前陛下御差配。
