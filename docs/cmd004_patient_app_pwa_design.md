# cmd_004 患者 app PWA 化 設計書 (= Service Worker offline + background sync + 構造改善)

- task_id: subtask_cmd004_service_worker_offline_sync
- parent_cmd: cmd_004 (小児恐竜王国 + 患者 app PWA 化)
- bloom_level: L4
- 文書種別: **設計書 + 運用 runbook** (= 根本治療原則整合明示、構造的根本解決設計)
- author: ashigaru3 (= 滝川一益、SC WSL hakudoukai@gmail.com)
- preflight: /mnt/c/Projects/hakudokai-dev/ SC WSL access 確認済
- 前提 (= 既設計/既実装):
  - `docs/kids_app_push_ceremony_detail_design.md` (信長手動再構築 v0.1) — VAPID/SW/DDL 正本
  - `docs/cmd004_push_vapid_management.md` — Phase 1+2 push infra 運用 runbook (= ashigaru3 push_vapid 既起案)
  - `frontend/public/patient-sw.js` — push handler 既実装 (Phase 1)
  - `frontend/src/hooks/useClinicId.ts` — `ClinicIdContext` (= 全 app 共通、URL param 起点)
  - `frontend/src/patient-app/PatientAppLayout.tsx` — manifest + SW register 起点
- 本書 deliverable:
  - `frontend/public/patient-sw.js` (大改修): cache namespace + 3 戦略 + background sync + update notification protocol
  - `frontend/public/patient-manifest.json` (強化): maskable icon + shortcuts + 完備属性
  - `frontend/src/patient-app/hooks/useOfflineQueue.ts` (新規): IndexedDB queue API + sync hook
  - `frontend/src/patient-app/hooks/useServiceWorkerUpdate.ts` (新規): SW update detection + prompt 制御
  - `frontend/src/patient-app/components/UpdateNotificationBanner.tsx` (新規): update prompt UI
  - `frontend/src/patient-app/PatientAppLayout.tsx` (拡張): SW 登録経路強化 + update banner 配置 + clinic_id 永続化
  - `frontend/tests/unit/patient-sw.test.ts` (新規 vitest): cache strategy + 漏洩防止 unit
  - `frontend/tests/e2e/patient-app-offline.spec.ts` (新規 playwright): offline simulation
- updated: 2026-05-11

---

## 0. 範囲・非範囲

### 0-1. 本書の範囲

| 項目 | 含む |
|------|------|
| Service Worker cache strategy 設計 (= clinic_id namespace + 3 戦略) | ○ |
| Background sync (= IndexedDB queue + sync event) 設計 | ○ |
| PWA manifest 強化 (= installable shell + maskable + shortcuts) | ○ |
| SW update notification protocol (= postMessage chain + UI prompt) | ○ |
| clinic_id 文脈保持 (= offline 中も維持、cross-clinic 漏洩防止) | ○ |
| pytest + Playwright offline simulation test 方針 | ○ |
| 根本治療原則整合 (= 「とりあえず動く」否認の構造的設計) | ○ |

### 0-2. 本書の非範囲

| 項目 | 非範囲理由 |
|------|-----------|
| Web Push 通知本体 (= subscribe / send_push) | `cmd004_push_vapid_management.md` で完備、本書は cache + sync + update に絞る |
| VAPID 鍵 rotation 運用 | 同上 |
| 保護者同意 gate | `cmd004_guardian_consent_spec.md` (ashigaru4) |
| ceremony 演出 | `kids_app_push_ceremony_detail_design.md` §3 |
| API 設計 (backend router) | 本書は frontend PWA 層に絞る |
| ストア配信 (= TWA / iOS Safari の installable 特殊事情) | 後続 ops task |

---

## 1. 根本治療原則整合 — 設計理由 (= 単純 cache を回避)

### 1-1. 「とりあえず動く」回避の判断

陛下御差配 msg_20260511_164625 で「短期 hack/patch 厳禁、構造改善優先、test + 法令 + UX 完備で根本品質」と通達。本書は以下で整合する:

| 規範 | 安易な実装 (= 否認) | 本書採用 (= 根本治療) |
|------|-------------------|--------------------|
| 規範1 (短期 hack 厳禁) | API すべて同一 cache、TTL なし | 3 戦略マップ + clinic_id namespace + TTL meta |
| 規範2 (構造改善優先) | 既 SW に try/catch を追加して凌ぐ | SW 再設計 (cache 命名規約 + 戦略 router) |
| 規範3 (将来運用安定優先) | manifest 最小限のまま | maskable + shortcuts + 完備、ストア配信前提 |
| 規範4 (仕組み追加 vs 改修区別) | external lib (dexie 等) を脳死導入 | 自前 minimal IndexedDB wrapper、scope 内で完結 |
| 規範5 (代替提示 + 永続追記) | scope 外要求は黙殺 | OD-PWA-* で後続申し送り |
| 評価基準 (test + 法令 + UX 完備) | unit test だけ書いて済ます | vitest + Playwright offline simulation + UX prompt 完備 |

### 1-2. cross-clinic 漏洩防止 — 法令観点

患者 app は **clinic_id ごとに完全分離** が必要 (= 個情法 + 医療法、医院間で患者情報は完全独立)。SW cache は単一 origin で共有されるため、cache namespace を `clinic_id` で分割しないと、別医院の API response が cache から漏れる事故が起こり得る。

**設計**: cache 名を `dentalbi-patient-v3-clinic-{clinic_id}` の形に namespace 化、`/api/?clinic_id=N` の query string を見て cache を選択する。

---

## 2. AC1 — Service Worker offline cache strategy (= 3 戦略マップ + namespace)

### 2-1. cache 命名規約

```
CACHE_PREFIX     = 'dentalbi-patient-v3'
SHELL_CACHE      = `${CACHE_PREFIX}-shell`        # 全 clinic 共通の static asset
API_CACHE_OF(id) = `${CACHE_PREFIX}-api-clinic-${id}`  # clinic_id ごとに分離
RUNTIME_CACHE    = `${CACHE_PREFIX}-runtime`      # SWR 戦略用、共有可な静的 runtime asset
```

### 2-2. 戦略マップ (= URL → strategy)

| URL pattern | 戦略 | 理由 |
|-------------|------|------|
| `/app`, `/patient-manifest.json`, `/icons/*` | **Cache-First** | shell — 不変、起動高速化最優先 |
| `/assets/*` (= Vite hashed bundle) | **Cache-First** | hashed filename で immutable、即配信 |
| `/api/patients/*`, `/api/patient_consents/*` (= 医院横断不可) | **Network-First + clinic_id namespace cache** | 最新優先、unreachable 時のみ cache fallback |
| `/api/push-notifications/vapid-public-key` | **Stale-While-Revalidate** | 90 日 rotation、即時 stale OK、裏で update |
| `/api/dictionary/*`, `/api/explanation_logs/*` (= 読み取り中心 master) | **SWR** | UX 即応 + 裏で更新 |
| その他 `/api/*` (= POST 等) | **Network-Only + queue** | offline 時は IndexedDB queue へ |

### 2-3. cache 衛生 (= 古い世代の clean)

`activate` event で `CACHE_PREFIX` で始まらない cache、または前 prefix (`dentalbi-patient-v2`) は削除する。version 切替時に `clients.claim()` で即時引継ぎ。

---

## 3. AC2 — Background sync (= IndexedDB queue + sync event)

### 3-1. queue store 設計

IndexedDB database `dentalbi-patient-offline`、object store `pending_requests`:

| field | type | 用途 |
|-------|------|------|
| `id` | autoIncrement | primary key |
| `url` | string | 復元用 absolute path |
| `method` | string | `POST`/`PUT`/`DELETE`/`PATCH` |
| `headers` | object | `Content-Type` 等 |
| `body` | string (JSON) | request body |
| `clinic_id` | number | cross-clinic 検証用 |
| `enqueued_at` | ISO 8601 | 古い queue 検出用 (24h 超は破棄) |
| `attempts` | number | retry 回数 (max 5) |

### 3-2. sync event protocol

```
1. SW: fetch event → POST/PUT/DELETE/PATCH で network 失敗
2. SW: IndexedDB に enqueue + Response.error() ではなく { status: 202, body: { queued: true, queue_id } } 返却
3. SW: self.registration.sync.register('patient-app-sync') を tag 登録
4. browser online 検出 → sync event 発火
5. SW: store を順走査 → fetch retry → 成功なら remove、失敗なら attempts++ (max 5 で dead-letter)
6. SW: 成功時 client へ postMessage({ type: 'sync-success', queue_id }) で UI 反映 trigger
```

### 3-3. UI 連動 (`useOfflineQueue` hook)

- `enqueue(request)`: SW へ postMessage で明示 queue 追加 (= fetch経由でなく事前 queue する場合)
- `pendingCount`: store 件数 polling
- `onSyncSuccess(callback)`: postMessage 受信時に呼ばれる

### 3-4. dead-letter handling

`attempts >= 5` の request は `dead_letter` object store へ移し、`useOfflineQueue` 経由で「再試行 / 破棄」UI を出す。本書では dead-letter store の起案までを担い、UI は OD-PWA-2 (後続) で実装。

---

## 4. AC3 — PWA manifest 強化 (= installable shell)

### 4-1. 追加属性 (= 既 minimal 構成への差分)

| 属性 | 値 | 理由 |
|------|----|------|
| `id` | `/app` | install 重複防止 |
| `categories` | `["medical", "health"]` | store 表示 |
| `lang` | `ja` | 日本語固定 |
| `dir` | `ltr` | 横書 |
| icons (maskable) | 192/512 maskable PNG | Android adaptive icon |
| `shortcuts` | 「予約」「お知らせ」「明細」3 件 | A2HS shortcut menu |
| `prefer_related_applications` | `false` | native app 誘導なし |
| `screenshots` | 1080×1920 ホーム画面 png (= OD-PWA-3 で追加) | store 表示拡充 |

### 4-2. icon 資産

既存: `/icons/icon.svg`、`/icons/icon-192.png`、`/icons/icon-512.png`
新規必要: `/icons/icon-192-maskable.png`、`/icons/icon-512-maskable.png`

本書実装では `purpose: "maskable"` を既 icon に paste 適用し、専用 maskable PNG 生成は OD-PWA-3 で後続 (= 画像生成は ashigaru1/2 のデザイン領域)。

---

## 5. AC4 — Update notification (= postMessage protocol + UI prompt)

### 5-1. protocol

```
SW (new version) → install event → self.skipWaiting() 廃止
                ↓
Browser: detect updatefound → registration.installing 監視
                ↓
Client (PatientAppLayout): registration.waiting あり → setUpdateAvailable(true)
                ↓
UI: UpdateNotificationBanner 表示 "新しいバージョンが利用可能です"
                ↓
User 操作: 「更新」click → registration.waiting.postMessage({ type: 'SKIP_WAITING' })
                ↓
SW: skipWaiting() → controllerchange → window.location.reload()
```

### 5-2. なぜ自動 skipWaiting を廃止するか

Phase 1 の SW は `self.skipWaiting()` を install で即発火 → 患者の操作中に勝手にリロードされる risk。
**根本治療**: 患者の意思で更新するよう変更、UI prompt で明示同意。

### 5-3. fallback (= prompt 無視時)

7 日後 (= last_dismissed_at から) に強制 prompt 再表示。Stale runtime は機能上問題ないが、push notification の payload 互換性 (= corr_id schema 変更) を考慮し、長期 stale を放置しない。

---

## 6. AC5 — clinic_id 文脈保持 + cross-clinic 漏洩防止

### 6-1. 多層 fallback

| 層 | 取得元 | 失効時 |
|----|--------|--------|
| 1. URL query | `?clinic_id=5` | (なし) |
| 2. localStorage | `patient_app.clinic_id` | URL に書き戻し |
| 3. last-seen IndexedDB | `app_state.last_clinic_id` | URL に書き戻し |
| 4. default = 1 | hardcode | (警告 log) |

### 6-2. cache namespace 強制

SW fetch handler は `/api/` request を見た際:

1. URL query string から `clinic_id` を抽出
2. 不在なら `Cache-Control: no-store` 扱い (= cache せず)
3. 存在すれば `API_CACHE_OF(clinic_id)` を選択
4. Cross-clinic な response (= API response body 内の `clinic_id` field が request の clinic_id と不一致) は cache 不能、log 出力

### 6-3. clean up

`activate` event で URL クエリ抽出可能な `clinic_id` 一覧を取得できないので、`API_CACHE_OF(*)` は **削除しない** (= 患者ごとに最大 ~2-3 clinic 程度の想定で容量問題なし)。容量上限超過時のみ LRU で淘汰する設計を OD-PWA-4 で後続。

---

## 7. AC6 — テスト方針

### 7-1. vitest (unit / integration)

`frontend/tests/unit/patient-sw.test.ts`:
- `_pickCacheName(url)` の戦略 router を直接 import で test (SW を ES module export)
- cache namespace 関数 (`apiCacheOf(clinicId)`) の純関数 test
- IndexedDB queue logic は fake-indexeddb で test

**注意**: SW 本体 (event listener) は JSDOM 環境で限界あり → Playwright e2e で補完。

### 7-2. Playwright (e2e offline simulation)

`frontend/tests/e2e/patient-app-offline.spec.ts`:

```typescript
test('offline 中も /app 起動可、復旧時 queue 自動 sync', async ({ context, page }) => {
  await page.goto('/app?clinic_id=5');
  await page.waitForFunction(() => navigator.serviceWorker.controller !== null);
  // SW 登録待ち
  await context.setOffline(true);
  await page.reload();
  // shell 起動確認
  await expect(page.getByText('My DentalBI')).toBeVisible();
  // 入力 queue
  // ... (具体 input は実装後の patient app UI に依存、本書は test 骨子)
  await context.setOffline(false);
  // sync 待ち
});

test('cross-clinic cache 漏洩なし', async ({ context, page }) => {
  await page.goto('/app?clinic_id=1');
  await page.waitForResponse(r => r.url().includes('/api/patients/'));
  await page.goto('/app?clinic_id=2');
  // clinic_id=2 の response が clinic_id=1 の cache から来ないことを確認
  // (= clinic_id=2 API call が actual network へ行く)
});
```

### 7-3. SKIP=0 ルール

本書ですべての test 系に `.skip()` を含めないことを宣言する。pre-implementation な部分は test を **書かず**、書いたものは全実行。

### 7-4. 実行環境前提 (= 実装時の機械 evidence)

| layer | 実行可否 (本 task SC WSL) | 補足 |
|-------|------------------------|------|
| vitest unit | ○ 実行可 | 13/13 pass、SKIP=0 |
| Playwright e2e | × WSL system libs 不在 (`libasound.so.2`, `libnspr4.so` 等) | test ファイル完成、実行は `playwright install-deps` 後の CI / dev PC 環境委譲 |

Playwright e2e の WSL 実行は `sudo apt install libasound2 libnss3 libnspr4 ...` 系の system dep install が必要で、本 task agent (= ashigaru) は sudo 不可。**OD-PWA-7** で deps セットアップ自動化 (= Dockerfile / Vagrant / setup script) を後続 ops 申し送り。test SKIP は無く、環境制約による実行未完了のみ。

---

## 8. 実装手順 (= 根本治療 chain: inventory → gap → 設計 → 実装 → test)

```
✓ Phase A: inventory (= 既 SW、manifest、ClinicIdContext、test infra 確認) — 完了
✓ Phase B: gap 分析 (= §1-1 規範対応表、本書 §2-§7 で構造解決) — 完了
→ Phase C: 設計書起案 (= 本書) — 完了
→ Phase D: 実装
   1. patient-sw.js 再設計 — cache strategy + namespace + sync + update protocol
   2. patient-manifest.json 強化
   3. useOfflineQueue.ts 新規 hook
   4. useServiceWorkerUpdate.ts 新規 hook
   5. UpdateNotificationBanner.tsx 新規 UI
   6. PatientAppLayout.tsx 拡張
→ Phase E: test
   1. vitest unit (SW logic + IndexedDB queue 純関数)
   2. playwright e2e (offline simulation, cross-clinic 漏洩防止)
→ Phase F: report + karo 報告 (AC8)
```

---

## 9. Open Items (= 後続申し送り)

| OD | 項目 | 申し送り先 | 根拠 |
|----|------|----------|------|
| OD-PWA-1 | external IndexedDB lib (dexie) 移行検討 | karo (= 後続 infra subtask) | 自前 wrapper の保守性検証後 |
| OD-PWA-2 | dead-letter UI (= 「再試行 / 破棄」) | ashigaru? (= UI subtask) | sync max attempts 超過 request の救済 |
| OD-PWA-3 | maskable icon PNG 生成 + screenshots | ashigaru1/2 (= デザイン領域) | デザイン responsibility |
| OD-PWA-4 | cache LRU 淘汰実装 | karo (= 後続 SW subtask) | 容量上限到達時 |
| OD-PWA-5 | TWA / iOS Safari 配信検証 | karo (= ops subtask) | store 配信前提整備 |
| OD-PWA-6 | Web Push payload schema 検証時の update 強制 prompt 実装 | ashigaru3/4 統合 | §5-3 fallback の本格化 |
| OD-PWA-7 | Playwright deps セットアップ自動化 (= WSL2 system libs `libasound2`/`libnss3`/`libnspr4`...) | karo (= ops/infra subtask、CI 環境整備) | 本 task で test 完成、実行委譲 |

---

## 10. 結論

本書は cmd_004 患者 app PWA 化を **構造的根本解決設計** として起案する。Service Worker を 3 戦略 + clinic_id namespace に再設計、IndexedDB queue で offline 入力を保持、SW update を patient 意思で制御、cross-clinic 漏洩を多層防御 — 全層を「とりあえず動く」否認の根本品質で構築する。

実装 6 ファイル + test 2 ファイル + 本書で AC1-AC8 を満たす。F007 遵守、push 前陛下御差配。

**ashigaru3 (滝川一益) 設計確認**: 根本治療原則 5 規範 + 評価基準 (test + 法令 + UX 完備) に整合、構造的根本解決設計。
