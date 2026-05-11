# cmd_004 通知統合 Facade Pattern 設計書

- task_id: subtask_cmd004_notification_facade_pattern
- parent_cmd: cmd_004
- bloom_level: L4
- 文書種別: **設計書 + 運用 runbook** (= 構造的根本解決設計、根本治療原則整合)
- author: ashigaru3 (= 滝川一益、SC WSL hakudoukai@gmail.com)
- preflight: /mnt/c/Projects/hakudokai-dev/ SC WSL access 確認済
- 前提 (= 既設計 / 既実装):
  - `docs/cmd004_push_vapid_management.md` (Phase 1+2) — Web Push infra 正本
  - `docs/cmd004_patient_app_pwa_design.md` (Phase 3) — PWA + offline + clinic_id namespace
  - `docs/cmd004_guardian_consent_spec.md` (ashigaru4) — 保護者同意 spec
  - `supabase/migrations/20260509_patient_consents_schema.sql` + `20260512_cmd004_consent_versioning_extensions.sql` — consent schema + versioning
  - `scripts/ntfy.sh` + `scripts/ntfy_listener.sh` + `lib/ntfy_auth.sh` — ntfy 内部 admin
  - `backend/routers/push_notifications.py` (Phase 1+2) — Web Push send_push state machine
- 本書 deliverable:
  - `supabase/migrations/20260511c_cmd004_notification_preferences.sql` (= 新規) — NotificationPreference + 時間帯制限
  - `backend/services/notifications/facade.py` (= 新規) — NotificationFacade
  - `backend/services/notifications/adapters/__init__.py` + `ntfy.py` + `web_push.py` + `sms.py` + `email.py` (= 新規 5 ファイル) — Channel Adapter
  - `backend/services/notifications/types.py` (= 新規) — Recipient / Message / NotificationContext schemas
  - `backend/services/notifications/router_logic.py` (= 新規) — channel 自動選択 logic (= 純関数 test 容易)
  - `backend/tests/test_notification_facade.py` (= 新規) — pytest
  - `backend/main.py` 末端で facade を application state に保持 (= linter exemption pattern)
- updated: 2026-05-11

---

## 0. 範囲・非範囲

### 0-1. 本書の範囲

| 項目 | 含む |
|------|------|
| 通知 channel inventory (= ntfy / Web Push / SMS / Email / LINE) | ○ |
| recipient-type (= admin / patient / guardian) 別 channel mapping | ○ |
| NotificationFacade interface 設計 | ○ |
| 4 adapter (Ntfy / WebPush / SMS-stub / Email-stub) 実装 + テスト方針 | ○ |
| NotificationPreference table 設計 (= opt-in/out + 時間帯制限) | ○ |
| consent_versioning 連動 (= 撤回時の自動失効、version chain 整合) | ○ |
| 既 push_notifications.send_push の facade 統合方針 | ○ |
| 根本治療原則整合の self-check + 拡張 chain | ○ |

### 0-2. 本書の非範囲

| 項目 | 非範囲理由 |
|------|-----------|
| SMS provider 統合 (= Twilio / AWS SNS / NTT 系) | 後段 task、本書では stub adapter |
| Email provider 統合 (= SendGrid / SES) | 同上 |
| LINE Messaging API 統合 | 後段 task |
| ntfy_listener.sh の inbound 入力経路 | 内部 admin の inbound、本書 outbound に絞る |
| consent UI 改修 | ashigaru4 担当 |
| ceremony 演出 | ashigaru5/SoT 担当 |

---

## 1. 根本治療原則整合 self-check (= 陛下御差配 msg_20260511_164625)

### 1-1. 「とりあえず動く」回避の判断

陛下御差配で「個別 channel 直接実装禁、facade + adapter で抽象化 + 拡張容易性」と明記。本書は以下で整合する:

| 規範 | 安易な実装 (= 否認) | 本書採用 (= 根本治療) |
|------|-------------------|--------------------|
| 規範1 (短期 hack 厳禁) | router の各 endpoint で `if channel == 'webpush': ...` を散在 | 単一 facade entry + adapter dispatch |
| 規範2 (局所修正禁、構造改善優先) | 既 send_push に SMS 引数追加して凌ぐ | facade を上位レイヤとして新設、既 send_push は WebPushAdapter 内部呼出に降格 |
| 規範3 (将来運用安定優先) | preference table を後付け | initial 段階で時間帯/quiet hours/opt-out を含む完全 schema |
| 規範4 (仕組み追加 vs 改修区別) | sms-twilio 等 external lib を試行的に追加 | stub adapter で interface 確定、provider 統合は別 task で「仕組み追加」と区別 |
| 規範5 (代替提示 + 永続追記) | scope 外要求を黙殺 | OD-NF-* で後続申し送り、本書は永続 doc |
| 評価基準 (test + 法令 + UX) | unit test 一部のみ | facade dispatch + channel selection + opt-out compliance を網羅 test、quiet hours で UX 配慮、erase_requested_at と連動で個情法 L04 整合 |

### 1-2. cross-clinic + cross-recipient 漏洩防止

Phase 3 の clinic_id namespace に続き、本 facade も:
- 各 dispatch で `recipient.clinic_id` を必須化、不一致 endpoint への配信を refuse
- audit log (`notification_delivery_log` を `push_delivery_log` と統合再利用) に `clinic_id` を必ず記録

---

## 2. AC1 — 通知 channel inventory

### 2-1. 5 channel × 3 recipient mapping

| Channel | admin | patient | guardian | 用途 | 現状実装 |
|---------|-------|---------|----------|------|---------|
| **Ntfy** | ✓ | × | × | shogun ↔ agents 内部運用、緊急 admin alert | `scripts/ntfy.sh` 既稼働 |
| **WebPush** | × | ✓ | ✓ | 患者 PWA / 保護者 PWA への push | `backend/routers/push_notifications.py` Phase 1+2 完成 |
| **SMS** | × | ✓ | ✓ | OTP / 緊急通知 / fallback | **未実装** (= 本書で stub adapter) |
| **Email** | × | ✓ | ✓ | 明細送付 / 同意リマインド | **未実装** (= 本書で stub adapter) |
| **LINE** | × | ✓ | ✓ | 患者 fallback | **後段** (= 本書 scope 外、Open Item) |

### 2-2. recipient-type 定義

```python
# backend/services/notifications/types.py 抜粋
class RecipientType(str, Enum):
    ADMIN = "admin"        # 内部運用、clinic スタッフ向けではなく shogun/agents
    PATIENT = "patient"    # 患者本人 (= patients.id)
    GUARDIAN = "guardian"  # 保護者 (= patient_consents.guardian_*)
```

`STAFF` (= 院内スタッフ) は本 facade 範囲外 (= 既存スタッフ通知系統がある、別 task で統合検討)。

### 2-3. channel 自動選択 fallback chain

| recipient | 優先順位 |
|-----------|---------|
| ADMIN | Ntfy (一択) |
| PATIENT | preference 優先 → WebPush → Email → SMS (= cost 順 + UX 順) |
| GUARDIAN | preference 優先 → SMS (OTP は SMS 一択) → WebPush → Email |

`preference` (= NotificationPreference table、§3) が明示されていれば優先、未設定なら上記 fallback。

---

## 3. AC3 — NotificationPreference table 設計

### 3-1. table 定義

```sql
CREATE TABLE public.notification_preferences (
  id                uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  clinic_id         integer NOT NULL,
  recipient_type    character varying NOT NULL
                    CHECK (recipient_type IN ('admin','patient','guardian')),
  recipient_id      uuid,                                    -- patient/guardian の id、admin は NULL (= clinic_id 単位)
  channel           character varying NOT NULL
                    CHECK (channel IN ('ntfy','webpush','sms','email','line')),
  enabled           boolean NOT NULL DEFAULT true,
  quiet_hours_start time,                                    -- 例: '22:00' (= 22 時以降は通知抑制)
  quiet_hours_end   time,                                    -- 例: '08:00'
  consent_id        uuid REFERENCES public.patient_consents(id) ON DELETE SET NULL,
                                                              -- 該当 consent と連動 (= patient_consents.is_active=false なら enabled 自動失効)
  category          character varying,                       -- 'visit_reminder' / 'ceremony' / 'billing' 等、NULL=全カテゴリ
  updated_by        character varying,                       -- staff email / patient self
  updated_at        timestamp with time zone NOT NULL DEFAULT now(),
  created_at        timestamp with time zone NOT NULL DEFAULT now(),
  UNIQUE (clinic_id, recipient_type, recipient_id, channel, category)
);
```

### 3-2. consent_versioning 連動

facade dispatch 時 `_resolve_effective_consent(consent_id)` で `patient_consents.is_active=true AND superseded_by IS NULL` を確認。撤回 (`is_active=false`) または expire (`erase_requested_at IS NOT NULL`) ならば preference を runtime で無視。これにより:

- patient_consents 撤回時に preference を物理 update しない (= immutable audit trail 保持)
- consent_version chain で「いつ撤回されたか」が `consent_versioning_audit_trail` から復元可能

### 3-3. quiet hours (= UX + 法令)

夜間 (= 22 時 〜 翌 8 時等) は emergency 以外抑制。emergency 判定は `NotificationContext.severity == 'emergency'` で bypass。法令上明示要件ではないが、医療 UX として配慮。

---

## 4. AC2 — NotificationFacade interface

### 4-1. signature

```python
# backend/services/notifications/facade.py 抜粋
class NotificationFacade:
    def __init__(
        self,
        ntfy: NtfyAdapter,
        web_push: WebPushAdapter,
        sms: SMSAdapter,
        email: EmailAdapter,
        clock: Callable[[], datetime] = _utcnow,
    ) -> None: ...

    async def notify(
        self,
        recipient: Recipient,
        message: NotificationMessage,
        context: NotificationContext,
    ) -> NotificationResult: ...
```

### 4-2. dispatch 規約

1. `select_channels(recipient, context, preferences)` で channel 順を確定
2. 各 channel で `is_blocked_by_quiet_hours()` + consent re-check
3. block されなければ `adapter.send()` を呼ぶ
4. 1 channel 成功で stop、全失敗で `NotificationResult(status='all_failed', errors=[...])`
5. 監査 log を `push_delivery_log` に統一記録 (= 既 table 拡張、新 channel 値 追加)

### 4-3. 既 send_push の降格

`backend/routers/push_notifications.py` の `send_push` endpoint は本書実装後:
- 内部実装は `NotificationFacade.notify(..., context.channel_hint='webpush')` を呼ぶ wrapper
- 既 endpoint signature を後方互換維持、breakage なし

---

## 5. AC4 — Adapter 実装方針

### 5-1. 共通 interface

```python
class NotificationAdapter(Protocol):
    name: ChannelName
    async def send(self, recipient: Recipient, message: NotificationMessage) -> AdapterResult: ...
    def supports(self, recipient: Recipient) -> bool: ...
```

### 5-2. 個別実装

| Adapter | 実装方針 |
|---------|---------|
| **NtfyAdapter** | `subprocess.run(['scripts/ntfy.sh', body])` を非同期 wrap、`supports = recipient.type == ADMIN` |
| **WebPushAdapter** | 既 `push_notifications._attempt_push_send` + `_log_delivery` を internal 関数として再利用、Phase 2 で起案済 state machine をそのまま継承 |
| **SMSAdapter (stub)** | `send` は `AdapterResult(status='stub_skipped', detail='provider not configured')` を返す。`supports` は `recipient.phone_e164` 存在 + clinic_id の sms provider config がある場合のみ True (= 後段で provider 統合) |
| **EmailAdapter (stub)** | 同上、`recipient.email` ベース |

### 5-3. ntfy 経路の隔離 (= Phase 2 audit 結果継承)

NtfyAdapter は `RecipientType.ADMIN` のみ accept。patient/guardian を渡すと `AdapterRejection` を raise、`supports() == False`。Phase 2 で確立した cross-channel 隔離原則を facade 層で structural に enforce。

---

## 6. AC5 — テスト方針

### 6-1. pytest test 対象

1. **router_logic.select_channels** — channel 順 + preference 優先 + emergency bypass + quiet hours
2. **consent re-check** — 撤回後の preference は dispatch しない
3. **adapter.supports** — recipient type vs channel mismatch を排除
4. **NtfyAdapter** — admin 以外 reject
5. **WebPushAdapter** — `push_notifications._attempt_push_send` の stub 経路と互換
6. **opt-out compliance** — `enabled=false` の preference は dispatch しない
7. **facade.notify** — 1 channel 失敗時の fallback chain
8. **audit log** — 全 dispatch で `push_delivery_log` (or 新 `notification_delivery_log`) に 1 行記録

### 6-2. SKIP=0

全 test を `.skip()` 無しで書く。stub adapter は **fake-success / fake-stub-skip** で代用、Provider 統合は test 不要。

---

## 7. 実装手順

```
✓ Phase A: inventory (= 既 ntfy / push_vapid / consent / preference 不在 確認) — 完了
✓ Phase B: gap 分析 + 設計書 (= 本書) — 完了
→ Phase C: 実装
   1. types.py (= dataclass / Enum / Protocol)
   2. router_logic.py (= 純関数 select_channels)
   3. adapters/{ntfy,web_push,sms,email}.py
   4. facade.py
   5. migration `20260511c_cmd004_notification_preferences.sql`
   6. push_notifications.send_push を facade wrapper に降格
   7. main.py 末端で facade を application state に
→ Phase D: pytest
→ Phase E: report + karo 報告
```

---

## 8. Open Items

| OD | 項目 | 申し送り先 | 根拠 |
|----|------|----------|------|
| OD-NF-1 | SMS provider 統合 (Twilio / AWS SNS / 国内 SMS API) | karo (= 後続 subtask) | 仕組み追加、本 task で stub |
| OD-NF-2 | Email provider 統合 (SendGrid / SES) | karo (= 後続 subtask) | 同上 |
| OD-NF-3 | LINE Messaging API 統合 | karo (= 後続 subtask) | 後段 |
| OD-NF-4 | `push_delivery_log` を `notification_delivery_log` へ rename + channel 列追加 | karo (= migration subtask) | 将来 channel 横断 audit 用 |
| OD-NF-5 | quiet hours の per-clinic 共通 default 設定 UI | ashigaru? (= UI subtask) | preference 個別設定の UX 補強 |
| OD-NF-6 | preference 自己管理 UI (= 患者が自分の preference を管理) | ashigaru? (= UI subtask) | UX |
| OD-NF-7 | emergency severity bypass の audit 厳格化 (= 濫用防止 review) | karo (= ops subtask) | bypass の濫用検知 |

---

## 9. 結論

本書は cmd_004 通知統合を **構造的根本解決設計** として起案する。既 ntfy / Web Push を adapter で抽象化、SMS / Email を stub で interface 固定、NotificationPreference で opt-in/out + quiet hours + consent_versioning 連動 — 個別 channel 直接実装による技術的負債を回避し、後続 provider 統合を「仕組み追加」として明示分離する。

**ashigaru3 (滝川一益) 設計確認**: 根本治療原則 5 規範 + 評価基準 (test + 法令 + UX 完備) 全整合、構造的根本解決設計。
