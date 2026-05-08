# 小児アプリ push通知 + 儀式（level up 演出）詳細設計

- task_id: subtask_kids_app_push_phase7_detail_design_001
- parent_cmd: cmd_kids_app_push_phase7_design_detail_001
- 文書種別: 詳細設計（Phase 7 パスポート連携の詳細展開、Phase 7 cmd 発令前提）
- 範囲: 設計のみ。実装コード・UI ビジュアル要素は含まない（デザイン班専権）
- base_commit: 79ac2e74
- author: ashigaru6（SecondPC, hakudoukai@gmail.com）
- 連動文書:
  - `docs/kids_app_push_ceremony_design.md`（本書の概念設計起点、ashigaru6 5/7 19:21）
  - `docs/kids_game_detail_design.md`（ashigaru5 ゲーム詳細設計、§5 が本書 §7 SoT を採用）
- updated: 2026-05-08（v0.1 信長手動再構築版、ashigaru6 復帰時に最終確定）
- recovery_note: 本書は **2026-05-08 22:55 ローカル消失事故** ののち、両アカウント Claude 履歴と既存 git 内資産から信長 (= shogun) が手動再構築した v0.1 版である。**ashigaru6 復帰時に必ず本人が監修・確定すること**。再現 source は §13 を参照。

---

## 0. 前提・正本参照と未参照事項（Anti-Duplication）

### 0-1. 参照済み正本

| # | 正本 | 所在 | 利用方法 |
|---|------|------|----------|
| A | DD-126 関連実装 | `frontend/src/features/teriha-passport/` (DentalBI) | 既存コンポーネント群（参照のみ、改変禁止） |
| B | 既存 CeremonyOverlay | `frontend/src/features/teriha-passport/components/CeremonyOverlay.tsx` | Props=`{kind, message, onDismiss}`（3 引数）。kind は `'birthday' \| 'tier_up' \| 'graduation'` の 3 値 |
| C | 既存 sw.js（PWA） | `frontend/public/sw.js`（**実在は OD2 で要確認**） | 既存 cache 戦略との衝突回避、本書 §2 で拡張ポイントのみ規定 |
| D | passport_xp_log / passport_rank_for_xp / passport_members | 既存 DB（DD-126 マイグレーション済） | XP→Rank 算出は既存ロジックを流用、変更禁止 |
| E | ashigaru5 detail_design.md | `docs/kids_game_detail_design.md` | §5 が本書 §7 を SoT として採用、双方向整合 |
| F | CLAUDE.md §15 SH パターン群 | (本リポジトリ) | SH1+SH2+SH3+SH8 を採用、D1-D6 適用なし |
| G | CLAUDE.md §16 トラブル自動応答 | (本リポジトリ) | エラーコード採番・夜間モード保護を本書 §5/§9 で踏襲 |
| H | CLAUDE.md §17 他院展開 | (本リポジトリ) | LINE Bot / メール fallback の経路を本書 §5 で連携 |

### 0-2. 本書で確定できなかった既存仕様（Open Items 高優先 6 件、§10 参照）

| ID | 項目 | 影響範囲 | 対処 |
|----|------|----------|------|
| OD1 | task YAML 未更新（subtask_kids_app_push_phase7_detail_design_001 への切替が SoT に反映されぬ） | scope 確定 | inbox メッセージ抽出版で進行、家老の事後整合監査を要求 |
| OD2 | 既存 `frontend/public/sw.js` の実在確認 | §2 拡張ポイント | Phase 7-α 着手時、ashigaru6 が現物確認のうえ Path A/B を最終選定 |
| OD3 | 既存 ConsentForm 系コンポーネントの有無 | §4 UI 設計 | 既存があれば流用、なければ本書 §4 wireframe を起点に新規設計（ただしデザイン班専権） |
| OD4 | `passport_members.pending_ceremony_at` / `last_ceremony_displayed_at` カラム実在 | §3 dedupe | 不在なら Phase 7-α migration で追加、ashigaru2 RLS 連動 |
| OD5 | `family_link` 相当テーブル（保護者⇔小児の対応関係）有無 | §4 配信先解決 | 不在なら Phase 7-α で新規 DD 起案 |
| OD13 | ashigaru5 detail_design.md の起草遅延（本書執筆時点では未存在） | §7 統合 API 整合 | 双方独立起草後 §7 SoT を ashigaru5 §5-10 で照合する流れで吸収（事後検証で双方整合を確認） |

### 0-3. Anti-Duplication 厳守チェック

| 項目 | 状態 |
|------|------|
| 既存 CeremonyOverlay の Props（kind/message/onDismiss）を変えない | 維持（§3） |
| 既存 kind を増設しない | 維持（§3） |
| 既存 sw.js を全面書換しない（拡張のみ） | 維持（§2） |
| 既存 award_xp / engine API を破壊しない | 維持（§7） |
| 新規ファイルは本詳細設計書 1 本のみ | 維持（5/8 v0.1 再構築版でも同一） |
| `passport_*_log` 既存テーブルを流用 | 維持（§8） |
| 新規テーブルは parent_consent 系のみ提案、Phase 7-α migration | 維持（§4 / §8） |

### 0-4. ashigaru5 連動 API 整合性宣言

ashigaru5 detail_design.md §5 は本書 §7 を SoT として採用済。本書はゲーム勝利→ XP 加算→ rank 昇格→ ceremony_event 採番→ CeremonyOverlay 起動→ dedupe API までの **API 表面契約** を定義し、ゲーム班 (ashigaru5) はその契約に Props を渡すだけで連携が成立する。

---

## 1. VAPID 鍵管理（Supabase Secret Manager）

### 1-1. 設計方針

PWA Web Push の VAPID 鍵は **長期固定でなくローテーション運用** とし、漏洩・端末紛失・鍵流出リスクを最小化する。

| 項目 | 採用 |
|------|------|
| 公開鍵 / 秘密鍵生成方式 | `web-push` 互換 P-256 ECDSA 鍵ペア |
| 保管先（一次） | **Supabase Secrets Manager**（プロジェクト `pxvnhkiqyxkejzivspde`） |
| 保管先（二次・運用 fallback） | `~/.openclaw/vapid_<env>.key`（dev only、本番禁止） |
| ローテーション周期 | **90 日**（短期化、過渡期両鍵並走で push 失効ゼロ） |
| 過渡期長 | 14 日（旧鍵→新鍵切替期、双方の subscription を平行受理） |
| 監査ログ | `vapid_key_access_log` テーブル（読出し / ローテ / revocation 全記録） |

> **[履歴より]** 概念設計では「180日推奨、有効期限通知」との記述があったが、詳細設計化にあたり **90日へ短縮** とした。ローテ短縮による失効リスクは「過渡期両鍵並走」で吸収する（後述 §1-3）。

### 1-2. 多層保管モデル

```
[Production]
  Supabase Secrets (一次) ── service_role からのみ読出可
       │
       ├─ private_key: 暗号化保管（AES-256-GCM、Supabase 管理）
       └─ public_key: 暗号化保管（任意、frontend には別経路で配信）

[Frontend 配信経路]
  service_role が起動時に GET /api/teriha-passport/vapid-public-key を提供
  → Service Worker が subscribe() 時に取得、平文でブラウザ Push Service へ送出
  → public_key は機密性低、ただしレート制限と CORS で配信元を絞る

[Development]
  ~/.openclaw/vapid_dev.key（暗号化なし、本番投入禁止フラグつき）
```

### 1-3. 90 日ローテ + 過渡期両鍵並走

```
Day 0   ：新鍵 (V2) 生成、Supabase Secrets に追加（旧鍵 V1 と並存）
Day 0-14：両鍵で subscription を受理。新規 subscribe は V2、既存 V1 端末は継続有効
Day 14  ：旧鍵 V1 を revoke、push 配信は V2 のみ
Day 14-90：V2 単独運用
Day 90  ：V3 生成、サイクル繰返
```

過渡期判定は `vapid_key_versions` テーブル（version, status, generated_at, revoked_at）で実現。バックエンド配信時は subscription レコードの `vapid_version` カラムで送出鍵を選択する。

### 1-4. 監査ログ（vapid_key_access_log）

| カラム | 型 | 意味 |
|--------|----|------|
| id | uuid | PK |
| key_version | int | V1/V2/V3... |
| action | enum | `read` / `rotate` / `revoke` / `failed_decrypt` |
| actor | text | service role 名・admin email |
| corr_id | uuid | 一連リクエスト追跡（CLAUDE.md §1 構造化ログ） |
| ip | inet | アクセス元 |
| occurred_at | timestamptz | 発生時刻 |

**RLS**: 理事長殿のみ全件参照可、各医院は自医院 clinic_id にひも付くアクセスのみ参照（§17.8 マルチテナント原則）。

### 1-5. ローテ実行 runbook（docs/runbooks/ERR-PUSH-001.md として別途整備）

```bash
# Day 0
1. supabase secrets set VAPID_PRIVATE_V2=$(openssl ecparam -name prime256v1 -genkey -noout | base64)
2. supabase secrets set VAPID_PUBLIC_V2=...
3. INSERT INTO vapid_key_versions (version=V2, status='active', generated_at=NOW())
4. UPDATE vapid_key_versions SET status='deprecated' WHERE version=V1

# Day 14
5. UPDATE vapid_key_versions SET status='revoked', revoked_at=NOW() WHERE version=V1
6. supabase secrets unset VAPID_PRIVATE_V1
```

ローテ自動化は SH パターン D6（migration の自動 rollback）に該当するため **Layer 3 承認必須**（§17.4.1）。理事長殿のワンタップ承認後にスクリプト実行。

### 1-6. アクセス権限と Layer 分類

| 操作 | Layer | 承認 |
|------|-------|------|
| public_key 配信（read） | Layer 1 | 不要 |
| 過渡期両鍵運用（read both） | Layer 1 | 不要 |
| 90 日ローテ実行（rotate） | Layer 3 | 理事長殿承認必須 |
| 緊急 revoke（漏洩検知時） | Layer 2 | ntfy 通知＋自動実行可 |

---

## 2. PWA Service Worker 詳細実装

### 2-1. 設計起点と Path 選択

既存 `frontend/public/sw.js` の実在を Phase 7-α で確認したうえ、以下のいずれかを採用する。

| Path | 内容 | 採否条件 |
|------|------|---------|
| **Path A: 既存 sw.js を拡張** | 既存 cache 戦略を維持、本書の push handler のみ追加 | 既存 sw.js が存在し cache 戦略が成熟 |
| **Path B: 新規 sw.js を起こし、Workbox / 自前構成で全面再構成** | precache / runtime / push を統合管理 | 既存 sw.js が雛形のみ or 不在 |

→ **OD2** で実在確認後、**Path A を第一候補** として動く（最小改変原則）。

### 2-2. ライフサイクル全イベント仕様

| イベント | 役割 | 本設計での振る舞い |
|---------|------|------------------|
| `install` | 初回登録時 | precache 投入（v1 アセット）、`self.skipWaiting()` で即活性化 |
| `activate` | 旧 worker 退役時 | 旧 cache 削除、`self.clients.claim()` で全タブ即適用 |
| `fetch` | リクエスト捕捉 | URL カテゴリ別キャッシュ戦略適用（§2-3） |
| `push` | サーバから push 受信 | payload 復号 → IndexedDB に保存 → notification 表示（§2-4） |
| `notificationclick` | 通知タップ | 既存タブを focus、なければ new tab 起動。passport URL 固定 |
| `notificationclose` | 通知 dismiss | dismiss ログ送出（POST /api/teriha-passport/push/dismissed） |
| `sync` | バックグラウンド同期 | リトライキュー処理（§6） |
| `message` | クライアント側からのメッセージ | フォアグラウンド通知制御、subscription refresh |

### 2-3. キャッシュ戦略（カテゴリ別）

| カテゴリ | 戦略 | 理由 |
|---------|------|------|
| 静的アセット（JS/CSS/font） | **Cache-First**（precache） | 不変、即応答 |
| 画像（恐竜・敵キャラ） | **Cache-First** + LRU 50MB cap | 量多く、頻繁更新なし |
| API（GET /api/teriha-passport/*） | **Network-First**（fallback Cache） | 最新優先、オフライン時はキャッシュ |
| API（POST /api/teriha-passport/*） | **Network-Only** + リトライキュー | 冪等性確保、§6 sync で再送 |
| HTML（index.html） | **Network-First**（fallback Cache） | デプロイ反映優先 |
| Push payload | キャッシュしない | サーバ送信、転送のみ |

### 2-4. push handler 詳細フロー

```
[push event 受信]
  ↓
[event.waitUntil で promise chain 開始]
  ↓
[payload 復号（VAPID 公開鍵検証） — 失敗 → ERR-PUSH-002]
  ↓
[payload schema 検証（type/title/body/url/corr_id 必須）]
  ↓
[IndexedDB push_received ストアに INSERT（dedupe key=corr_id）]
  ↓ 重複 → 即 return（既受信）
[showNotification() 実行]
  - title, body, icon, badge, data={url, corr_id, ceremony_event_id?}
  - tag = corr_id（同一通知の上書き）
  - renotify = false
  ↓
[配信成功ログ POST /api/teriha-passport/push/delivered（best-effort）]
```

### 2-5. バージョニングと自己回復（SH6 パターン適用）

- sw.js のバージョン番号は `SW_VERSION = "v7.1.0"` 形式で頭にコメント記載
- バージョン不一致検知時は activate で旧 cache を強制削除
- worker 起動失敗 3 回連続 → クライアント側で `navigator.serviceWorker.getRegistration().unregister()` し再登録
- 自己再起動上限: 1 時間 5 回（§15 SH6 必須安全装置準拠）
- 手動停止フラグ: `~/.openclaw/disable_pwa_sw` で worker 登録 OFF

### 2-6. オフライン時 fallback ページ

- `/offline.html`（precache 必須）
- 接続復帰検知 → 自動リロード
- リトライキュー件数を表示（「未送信 N 件」）

---

## 3. CeremonyOverlay 演出 5 種

### 3-1. 既存 API 不変方針（中核設計）

既存 `CeremonyOverlay.tsx` の Props は `{kind, message, onDismiss}` の 3 引数。**本書では既存 API を破壊しない**。

```ts
// 既存（変更禁止）
interface CeremonyOverlayProps {
  kind: 'birthday' | 'tier_up' | 'graduation'
  message: string
  onDismiss: () => void
}
```

新 kind を追加せず、演出 5 種は **`variant` という後方互換 optional Props** によって内部分岐する。

### 3-2. 後方互換 optional Props 拡張（§7 SoT）

```ts
// 後方互換拡張（既存呼出箇所はゼロ改修で動く）
interface CeremonyOverlayPropsExtended extends CeremonyOverlayProps {
  variant?: CeremonyVariant       // 演出パターン選択（§3-3）
  ageTier?: AgeTier              // 年齢別演出選択（egg/chick/adventurer/hero/kingdom_warrior）
  source?: CeremonySource        // 'game_victory' | 'visit_checkin' | 'milestone' | 'system'
  ceremonyEventId?: string       // dedupe API key（§3-5）
  onShowComplete?: () => void   // 演出完了時 dedupe 確定コールバック
}

type CeremonyVariant =
  | 'static'              // P1: 既存挙動互換（演出なし、message のみ）
  | 'character_growth'    // P2: 恐竜キャラ進化演出（chick → adventurer 等）
  | 'royal_rite'          // P3: 王国戦士儀礼（kingdom_warrior 専用、勇者語り）
  | 'birthday_classic'    // P4: 既存 birthday 演出を強化
  | 'graduation_classic'  // P5: 既存 graduation 演出を強化
```

### 3-3. 5 演出パターン

| ID | variant | 名称 | 起動条件 | 表示時間 | skip 可否 |
|----|---------|------|----------|---------|----------|
| P1 | `static` | 既存互換（無演出） | optional 未指定の既存呼出 | 既存値（無制限、onDismiss まで） | ○ |
| P2 | `character_growth` | キャラ進化 | tier_up + ageTier 遷移時 | 4 秒 | ○（2 秒経過後） |
| P3 | `royal_rite` | 王国戦士儀礼 | tier_up + ageTier='kingdom_warrior' 到達時 | 6 秒 | ○（3 秒経過後） |
| P4 | `birthday_classic` | 誕生日 | birthday kind 流用 | 5 秒 | ○ |
| P5 | `graduation_classic` | 卒業式典 | graduation kind 流用（15 歳到達） | 8 秒 | ○（5 秒経過後） |

→ **デザイン班スコープ**: 各 variant の具体ビジュアル（パーティクル / 色 / モーション / フォント）は本書では規定しない。

### 3-4. dedupe（重複表示防止）— 概念設計 §2-3 の継承

**State モデル**（OD4 で実在確認のうえ採用、不在なら Phase 7-α migration で追加）:

| カラム | 型 | 意味 |
|--------|----|------|
| `pending_ceremony_at` | timestamptz | サーバが「儀式を表示すべき」と認識した時刻 |
| `last_ceremony_displayed_at` | timestamptz | クライアントが演出完了を確定した時刻 |

**判定式**:

```
should_show_ceremony =
  pending_ceremony_at IS NOT NULL AND
  (last_ceremony_displayed_at IS NULL OR
   pending_ceremony_at > last_ceremony_displayed_at)
```

### 3-5. 状態遷移（5 ステップ）

```
[1. ゲーム勝利 / visit / milestone]
   ↓ recordGameScore / award_xp
[2. engine: rank 昇格判定]
   ↓ if leveled_up
[3. server: pending_ceremony_at = NOW(); ceremony_event INSERT (id 採番)]
   ↓ getDashboard 再フェッチ
[4. client: response.passport.pendingCeremony を受信、CeremonyOverlay マウント]
   ↓ 演出再生 → onShowComplete 発火
[5. client: POST /api/teriha-passport/ceremonies/<id>/displayed]
   ↓ server: last_ceremony_displayed_at = NOW()
[完了 — 次回起動時は判定式 false で再表示しない]
```

### 3-6. 同時昇格・重複発火の扱い

- 1 セッション内で複数 rank 昇格（例: chick→adventurer→hero）が連続発生した場合、**最新 rank への昇格のみ** ceremony_event レコードを採番
- 中間 rank の演出は省略（保護者が長時間放置していた特殊ケースの救済）
- ただし `passport_xp_log` には全段昇格履歴を残す

### 3-7. 中断時の救済

- 演出途中でアプリ kill / タブ閉じ → `last_ceremony_displayed_at` 未更新
- 次回起動時に判定式 true → 演出再生（replay）
- replay 上限: 同一 ceremony_event_id につき 3 回（4 回目以降は自動 dismiss）

### 3-8. 並列セッションコリジョン

- 同一 member_id が複数端末で同時オンライン時、両端末で同一 ceremony_event をマウントしうる
- 解決: `onShowComplete` の `POST /ceremonies/<id>/displayed` を最初に発火した端末で確定、他端末は 409 Conflict 受領 → 即 dismiss
- conflict 時のユーザー体験: 「他の端末で見たのでとじます」と短文メッセージ表示（UX レビュー対象）

### 3-9. アクセシビリティ

- skip ボタンは画面下中央に固定（既存挙動）
- スクリーンリーダー用 `aria-live="polite"` の通知文（既存）
- 動きに敏感なユーザー向け prefers-reduced-motion 検出時は P1 (static) に強制 fallback

---

## 4. parent_consent UI モック

### 4-1. 設計方針

データフロー設計のみ規定し、UI ビジュアルはデザイン班専権。本書は wireframe（テキスト）と DB schema、opt-out フロー、14 歳未満の保護者同意フローを規定する。

> **[再構築・要 ashigaru6 確認]** ashigaru5 detail_design.md は §6 で `passport_kids_consent` テーブルを新規提案している。本書 §4 はそれと整合させる方向で記述する。詳細は ashigaru5 docs/kids_game_detail_design.md §6 を参照。

### 4-2. テキスト wireframe（同意取得モーダル）

```
┌────────────────────────────────────────┐
│ 🦖 てりはキョウリュウおうこくパスポート    │
├────────────────────────────────────────┤
│ ご利用前にお願いがあります             │
│                                        │
│ 本アプリは <お子様の名前> ちゃん専用の  │
│ パスポートです。ゲーム結果や来院記録を │
│ 当院でお預かりします。                 │
│                                        │
│ 保護者の方の同意をお願いします。       │
│                                        │
│ ☑ 同意する内容（タップで詳細）         │
│   - ゲーム結果の保存（30日）            │
│   - 来院日のリマインド通知               │
│   - 経験値・ランクの保存                │
│                                        │
│ □ 通知を受け取る（任意）                │
│                                        │
│ 保護者の方のお名前: [_______________]   │
│ お子様との続柄: [▼ 父 / 母 / 祖父母 ]   │
│                                        │
│ [ 同意する ]  [ あとで ]              │
├────────────────────────────────────────┤
│ ご質問は受付スタッフまで。              │
└────────────────────────────────────────┘
```

### 4-3. DB schema（passport_kids_consent、Phase 7-α 新規）

```sql
CREATE TABLE passport_kids_consent (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  member_id       UUID NOT NULL REFERENCES passport_members(id),
  clinic_id       INT NOT NULL,
  parent_name     TEXT NOT NULL,
  parent_relation TEXT NOT NULL,           -- 'father' / 'mother' / 'grandparent' / 'guardian'
  consent_items   JSONB NOT NULL,         -- {"game_result":true, "push":false, ...}
  consent_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  withdrawn_at    TIMESTAMPTZ,
  withdrawn_by    TEXT,
  withdraw_reason TEXT,
  age_tier_at_consent TEXT,                -- 'egg' / 'chick' / ...
  is_under_14     BOOLEAN NOT NULL,        -- 14 歳未満特別保護フラグ
  corr_id         UUID,                    -- 取得時 correlation_id
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pkc_member ON passport_kids_consent(member_id) WHERE withdrawn_at IS NULL;
CREATE INDEX idx_pkc_clinic ON passport_kids_consent(clinic_id, consent_at);
```

**RLS**:
- 各医院は自医院 clinic_id のみ参照可
- 受付スタッフは consent_items 編集可、子ども本人は read-only

### 4-4. 同意取得時の受付スタッフ通知経路

```
[保護者がモーダルで「あとで」 → 同意未取得状態]
   ↓
[passport_members.parent_consent_pending = true（既存 or 新規カラム）]
   ↓
[受付スタッフ画面で in-app バッジ表示（Supabase Realtime 経由）]
   ↓
[並行で家族の LINE/メール 経路に「同意取得をお願いします」リンク送信]
   ↓ 親がクリック → モバイルで同意モーダル表示 → 同意 INSERT
[passport_members.parent_consent_pending = false]
```

### 4-5. opt-out フロー

```
[保護者が ParentDashboard で「通知を受け取らない」チェック解除]
   ↓
[POST /api/teriha-passport/consent/<id>/opt-out (push)]
   ↓
[passport_kids_consent.consent_items.push = false に更新]
   ↓
[push_subscriptions テーブルから当該 member の有効レコード削除]
   ↓
[次回 push 配信時に subscription 不在 → スキップ + ERR-PUSH-005 (opt-out skip) WARN ログ]
```

### 4-6. 同意撤回フロー（GDPR 風削除権）

```
[保護者が「同意を撤回し、データを削除する」をタップ]
   ↓ 確認ダイアログ「本当に削除しますか？取り消せません」
[POST /api/teriha-passport/consent/<id>/withdraw]
   ↓ atomic transaction:
   - passport_kids_consent.withdrawn_at = NOW()
   - passport_xp_log: clinic_id 内の対応 member データを 30 日後 hard delete スケジュール
   - push_subscriptions: 即削除
   - ceremony_event: 即削除
   ↓
[受付スタッフへ通知 + 院長に連絡（保護者意思の確認推奨）]
[30 日経過 → cron で物理削除実行]
```

医療法上の最低保管期間と GDPR 風削除権の調整は §10 法令最終総合監査で確定。本書では **30 日 grace period** を default 案として提示。

### 4-7. 14 歳未満の特別保護

- `is_under_14 = TRUE` の member には push 通知配信を **デフォルト OFF**（オプトイン必須）
- ゲーム結果も保護者ダッシュボードでのみ閲覧可（子ども本人画面では非表示にする選択肢）
- COPPA / GDPR-K / 改正個人情報保護法 28 条準拠の最終確認は §10 法令最終総合監査で実施

---

## 5. push 通知 Rate Limit + 配信失敗 fallback

### 5-1. トリガー一覧（来院前日 / 当日朝 / その他）

| ID | トリガー | 起動時刻 | 対象 | 内容例 |
|----|---------|---------|------|-------|
| T1 | 来院前日リマインド | 18:00 (JST) | 翌日来院予約者全員 | 「あした は びょういん だよ。はやめに ねよう！」 |
| T2 | 当日朝リマインド | 8:00 (JST) | 当日来院予約者 | 「きょう びょういん いくひだよ！」 |
| T3 | level up 儀式 push | rank 昇格と同期（即時） | 昇格 member のみ | 「<RANK_NAME> に しんかしたよ！アプリで みてね！」 |
| T4 | 連続来院マイルストーン | 達成時即時 | streak 達成 member | 「Nかい れんぞくで がんばったね！」 |
| T5 | 1 週間未来院アラート（保護者） | 週次 月曜 18:00 | 親 LINE/メール | 「最近お子様の来院がありません。お変わりありませんか？」 |
| T6 | カスタム院長メッセージ | 任意 | 全 member or 個別 | 自由文（院長承認必須） |

**夜間モード保護**: 22:00-7:00 (JST) は T1-T6 すべて配信停止（§16 夜間モード踏襲）。例外: T6 で院長が「緊急」フラグ立てた場合のみ配信。

### 5-2. Rate Limit（4 階層）

過剰配信による通知疲労を防止するため 4 階層 Limit を設定:

| Layer | 範囲 | 上限 | 超過時 |
|-------|------|------|--------|
| L1 | 単一 member | 1 日 5 件、1 時間 2 件 | サマリ集約配信 |
| L2 | 単一医院 | 1 日 1000 件、1 分 50 件 | 待機キューへ移動 |
| L3 | 単一エラーコード（同 member） | 5 分 1 件 | 抑止（§10 メール爆撃防止と同型） |
| L4 | システム全体 | 1 日 100,000 件 | 停止 + 緊急アラート（ntfy） |

### 5-3. 配信失敗 fallback（三段、SH3 パターン）

```
[1次: PWA Web Push（VAPID）]
   ↓ 失敗（subscription 失効・端末不在）
[2次: LINE Bot（§17.14 LINE 公式アカウント Bot 経由）]
   ↓ 失敗（友だち未追加・LINE Bot block）
[3次: メール（SendGrid 等、§10 メール通知配線）]
   ↓ 失敗
[dead-letter: push_dead_letter テーブル INSERT、24h 後 retry / 院長へ ntfy]
```

各段階で `push_delivery_log` に試行履歴を構造化ログ記録（CLAUDE.md §1 構造化ログ準拠）。

### 5-4. dead-letter ハンドリング

| 状態 | 振る舞い |
|------|---------|
| dead-letter 投入 | 24 時間後に 1 回再試行 |
| 再試行失敗 | 院長 ntfy（「<member_id> へ通知届かず、対面で確認推奨」） |
| 7 日経過 | 自動破棄 + 配信抑止フラグ立て |

### 5-5. 観測閾値（自動アラート発火条件）

| メトリクス | 閾値 | 通知先 |
|-----------|------|--------|
| 24h 配信失敗率 | > 5% | shogun inbox + dashboard |
| 同一医院 dead-letter | > 10 件/日 | 院長 ntfy + shogun |
| 1 分間配信数 | L2 超過の 80% | dashboard ハイライト |
| VAPID 鍵検証失敗 | 5 回/時間 | CRITICAL ntfy（鍵漏洩疑い） |

### 5-6. opt-out / 既読化フロー

- 通知文末に「もう うけとらない」リンク（`?action=optout&token=...`）
- token は 1 回限り、24h 期限
- クリック → §4-5 opt-out フローへ
- 既読化は `notificationclick` イベントで自動（POST /api/teriha-passport/push/read）

---

## 6. オフライン耐性 + 同期戦略

### 6-1. IndexedDB schema（4 store）

| store 名 | キー | 用途 | TTL |
|---------|------|------|-----|
| `push_received` | corr_id | dedupe key、既受信検知 | 30 日 |
| `retry_queue` | uuid | API 失敗時の再送キュー | 7 日（超過は dead-letter） |
| `cached_dashboard` | member_id | getDashboard レスポンスキャッシュ | 1 時間 |
| `pending_ceremony_local` | ceremony_event_id | サーバ未到達の儀式表示状態 | 確定まで |

### 6-2. リトライキュー詳細

```
[POST 失敗（network error）]
   ↓
[retry_queue に INSERT { method, url, body, attempts:0, next_retry_at:NOW()+1s }]
   ↓
[Service Worker 'sync' event で順次処理]
   ↓ 成功 → DELETE
   ↓ 失敗（attempts < 5）→ exponential backoff（1s→2s→4s→8s→16s）, attempts++
   ↓ attempts >= 5 → push_dead_letter へ移動
```

### 6-3. 冪等性保証（SH8 パターン）

`recordGameScore` 等の POST API は idempotency key を必須化（推奨）:

- key 構成: `{member_id}:{game_code}:{client_timestamp_ms}`
- backend は同 key の重複処理を検知し 200 with no-op を返す
- backend 側は `push_idempotency_keys` テーブル（key, processed_at、24h 自動 purge）で照合

ashigaru5 detail_design.md §3 でゲーム側の idempotency 採用は確認済（§7 で SoT 整合）。

### 6-4. 同期コリジョン解決

オフライン中に同一 member が複数端末で異なる動作 → オンライン復帰時に競合:

| 競合パターン | 解決方針 |
|-------------|---------|
| 同一ゲーム結果が 2 端末から送信 | idempotency key 一致なら no-op、不一致なら timestamp 早い方を採用 |
| 複数端末で同時 rank 昇格イベント | server-side で member.total_xp の最大値を採用 |
| ceremony_event 重複採番 | server で UNIQUE 制約 (member_id, source, triggered_at)、後発は 409 |
| consent 撤回中に push 配信 | consent_check は配信直前で、撤回優先 |

### 6-5. マルチデバイス（同一 member が複数デバイスにインストール）

- 各端末ごとに `push_subscription` レコード（unique endpoint）
- push 配信は全デバイスへ broadcast、ただし重複表示は §3-8 並列セッションコリジョンで抑制
- ParentDashboard で「このデバイスから同意撤回」を選べる（端末ごと粒度）

### 6-6. cache 階層（PWA 全体方針）

```
[precache] 静的アセット（install 時に投入、v1/v2... バージョン管理）
   │
[runtime cache] API レスポンス（Network-First で生成、TTL 1 時間）
   │
[fallback] /offline.html（オフライン起動時）
```

precache 容量上限: 50MB。超過時は LRU で古いアセットから削除。

---

## 7. ashigaru5 連携統合 API 契約（CeremonyOverlay surface SoT）

> **本セクションは ashigaru5 detail_design.md §5 が SoT として採用する契約定義**。整合性は ashigaru5 §5-10 で全 ✓ 確認済。

### 7-1. CeremonyOverlay Props（既存 3 + 後方互換 5）

```ts
// 既存・必須（変更禁止）
interface CeremonyOverlayProps {
  kind: 'birthday' | 'tier_up' | 'graduation'
  message: string
  onDismiss: () => void

  // 後方互換 optional（既存呼出はゼロ改修）
  variant?: 'static' | 'character_growth' | 'royal_rite' | 'birthday_classic' | 'graduation_classic'
  ageTier?: 'egg' | 'chick' | 'adventurer' | 'hero' | 'kingdom_warrior'
  source?: 'game_victory' | 'visit_checkin' | 'milestone' | 'system'
  ceremonyEventId?: string
  onShowComplete?: () => void
}
```

### 7-2. ゲーム勝利後の連携フロー（ashigaru5 がフォローする手順）

```
1. ashigaru5: recordGameScore({score, cleared}) で結果送信
2. server: award_xp 実行 → rank 昇格判定 → leveled_up なら ceremony_event INSERT
3. ashigaru5: getDashboard を再フェッチ
4. response.passport.pendingCeremony を取り出す:
   {
     id: "ce_xxx",                        // ceremony_event_id
     kind: "tier_up",
     ageTier: "adventurer",
     source: "game_victory",
     message: "Adventurer に しんかしたよ！",
     variant_hint: "character_growth"     // server 推奨 variant（ashigaru5 が override 可）
   }
5. ashigaru5: <CeremonyOverlay
     kind={pc.kind}
     message={pc.message}
     onDismiss={...}
     variant={pc.variant_hint}
     ageTier={pc.ageTier}
     source={pc.source}
     ceremonyEventId={pc.id}
     onShowComplete={() => fetch(`/api/teriha-passport/ceremonies/${pc.id}/displayed`, {method:'POST'})}
   />
6. 演出完了 → onShowComplete 発火 → server で last_ceremony_displayed_at = NOW()
```

### 7-3. dedupe API endpoint

| Method | Path | 役割 |
|--------|------|------|
| GET | `/api/teriha-passport/ceremonies/:id` | event 詳細取得 |
| POST | `/api/teriha-passport/ceremonies/:id/displayed` | dedupe 確定 |
| POST | `/api/teriha-passport/ceremonies/:id/replay` | 中断救済（attempts < 3） |

### 7-4. ashigaru5 → ashigaru6 不変約束

ゲーム班は CeremonyOverlay の **演出内部実装に触らない**。Props を渡すだけで本書 §3 の演出 5 種が再生される。これにより ashigaru5/ashigaru6 の責務境界が明確化。

---

## 8. データモデル詳細（DDL 概念 + index 設計）

### 8-1. 新規 / 拡張テーブル一覧

| テーブル | 状態 | 用途 |
|---------|------|------|
| `passport_kids_consent` | 新規（Phase 7-α） | §4 同意管理 |
| `vapid_key_versions` | 新規（Phase 7-α） | §1 鍵ローテ |
| `vapid_key_access_log` | 新規（Phase 7-α） | §1 監査 |
| `push_subscriptions` | 新規（Phase 7-α） | デバイス subscription |
| `push_delivery_log` | 新規（Phase 7-α） | 配信履歴・5 年保管 |
| `push_dead_letter` | 新規（Phase 7-α） | 配信失敗キュー |
| `push_idempotency_keys` | 新規（Phase 7-α） | §6-3 冪等性 |
| `ceremony_event` | 新規（Phase 7-α） | §3 イベント採番 |
| `passport_members.pending_ceremony_at` | カラム追加（OD4） | §3 dedupe |
| `passport_members.last_ceremony_displayed_at` | カラム追加（OD4） | §3 dedupe |
| `passport_members.parent_consent_pending` | カラム追加（OD4） | §4 同意未取得状態 |

### 8-2. push_subscriptions DDL

```sql
CREATE TABLE push_subscriptions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  member_id       UUID NOT NULL REFERENCES passport_members(id),
  clinic_id       INT NOT NULL,
  endpoint        TEXT NOT NULL UNIQUE,
  p256dh_key      TEXT NOT NULL,
  auth_secret     TEXT NOT NULL,
  vapid_version   INT NOT NULL,
  user_agent      TEXT,
  device_label    TEXT,
  subscribed_at   TIMESTAMPTZ DEFAULT NOW(),
  last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
  revoked_at      TIMESTAMPTZ
);
CREATE INDEX idx_ps_member ON push_subscriptions(member_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_ps_clinic ON push_subscriptions(clinic_id);
```

### 8-3. ceremony_event DDL

```sql
CREATE TABLE ceremony_event (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  member_id       UUID NOT NULL REFERENCES passport_members(id),
  clinic_id       INT NOT NULL,
  kind            TEXT NOT NULL CHECK (kind IN ('birthday','tier_up','graduation')),
  source          TEXT NOT NULL,
  age_tier        TEXT,
  variant_hint    TEXT,
  message         TEXT NOT NULL,
  triggered_at    TIMESTAMPTZ DEFAULT NOW(),
  displayed_at    TIMESTAMPTZ,
  replay_count    INT DEFAULT 0,
  corr_id         UUID,
  UNIQUE (member_id, source, triggered_at)
);
CREATE INDEX idx_ce_pending ON ceremony_event(member_id, triggered_at)
  WHERE displayed_at IS NULL;
```

### 8-4. push_delivery_log DDL（5 年保管、医療法準拠）

```sql
CREATE TABLE push_delivery_log (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id UUID REFERENCES push_subscriptions(id),
  member_id     UUID NOT NULL,
  clinic_id     INT NOT NULL,
  trigger_id    TEXT NOT NULL,                     -- 'T1' / 'T2' / 'T3' / ...
  payload_hash  TEXT NOT NULL,                     -- payload の SHA-256
  status        TEXT NOT NULL,                     -- 'sent' / 'failed' / 'opt_out_skip' / 'rate_limited'
  fallback_used TEXT,                              -- 'webpush' / 'line' / 'email' / 'dead_letter'
  err_code      TEXT,
  corr_id       UUID,
  attempted_at  TIMESTAMPTZ DEFAULT NOW(),
  delivered_at  TIMESTAMPTZ
);
CREATE INDEX idx_pdl_member_time ON push_delivery_log(member_id, attempted_at);
CREATE INDEX idx_pdl_clinic_time ON push_delivery_log(clinic_id, attempted_at);
CREATE INDEX idx_pdl_err ON push_delivery_log(err_code) WHERE err_code IS NOT NULL;
```

retention は WORM ストレージへの日次 mirror で 5 年確保（CLAUDE.md §17.3 アクセスログ証跡準拠）。

### 8-5. RLS 概要（ashigaru2 連携）

全テーブルに `clinic_id` 必須、自医院のみ参照可（既存 §17.8 マルチテナント原則踏襲）。詳細 RLS policy は ashigaru2 の RLS 設計タスクへ申し送り（本書 §11 参照）。

---

## 9. エラーコード採番

CLAUDE.md §9 採番台帳（`docs/error_codes.md`）に追記。本書では **暫定採番** を提示し、Phase 7-α 着手時に台帳へ正式登録。

### 9-1. ERR-PUSH-001 〜 012

| コード | 意味 | 重要度 | アラート |
|--------|------|--------|---------|
| ERR-PUSH-001 | VAPID 鍵 未設定 | CRITICAL | 理事長 ntfy + メール |
| ERR-PUSH-002 | push payload 復号失敗 | ERROR | shogun inbox |
| ERR-PUSH-003 | subscription 失効 | WARN | dashboard |
| ERR-PUSH-004 | Rate Limit 超過 (L1-L4) | WARN | dashboard |
| ERR-PUSH-005 | opt-out によるスキップ | INFO | ログのみ |
| ERR-PUSH-006 | LINE Bot fallback 失敗 | ERROR | shogun inbox |
| ERR-PUSH-007 | メール fallback 失敗 | ERROR | shogun inbox |
| ERR-PUSH-008 | dead-letter 投入 | WARN | dashboard |
| ERR-PUSH-009 | dead-letter 7 日超過破棄 | WARN | dashboard |
| ERR-PUSH-010 | 夜間モード抑止 | INFO | ログのみ |
| ERR-PUSH-011 | parent_consent 未取得で配信中止 | WARN | dashboard |
| ERR-PUSH-012 | VAPID ローテ失敗 | CRITICAL | 理事長 ntfy |

### 9-2. ERR-CEREMONY-001 〜 006

| コード | 意味 | 重要度 |
|--------|------|--------|
| ERR-CEREMONY-001 | ceremony_event 採番失敗 | ERROR |
| ERR-CEREMONY-002 | dedupe API 409 conflict（並列セッション） | INFO |
| ERR-CEREMONY-003 | replay 上限超過 | WARN |
| ERR-CEREMONY-004 | variant 不正値（後方互換 fallback） | WARN |
| ERR-CEREMONY-005 | last_ceremony_displayed_at 整合性破れ | ERROR |
| ERR-CEREMONY-006 | onShowComplete 未到達（10 分タイムアウト） | WARN |

### 9-3. ERR-CONSENT-001 〜 002

| コード | 意味 | 重要度 |
|--------|------|--------|
| ERR-CONSENT-001 | parent_consent 取得失敗（DB error） | ERROR |
| ERR-CONSENT-002 | 同意撤回後のデータ削除失敗 | CRITICAL（法令） |

### 9-4. SH パターン採用一覧（CLAUDE.md §15 準拠）

| SH | 採用箇所 | 安全装置 |
|----|---------|---------|
| SH1 Circuit Breaker | push 配信、Supabase 接続 | 失敗 5 回 + 5 分 cooldown |
| SH2 Exponential Backoff | retry_queue（§6-2） | 1s→2s→4s→8s→16s, cap 5 |
| SH3 Fallback | push 三段 fallback（§5-3） | LINE / メール / dead-letter |
| SH8 Idempotent Retry | recordGameScore 等（§6-3） | idempotency_keys テーブル |

**禁止パターン D1-D6 は適用なし**（D1 自動データ書換 / D2 無限再起動 / D3 自動権限昇格 / D4 患者データ自動マージ / D5 課金自動再試行 / D6 migration 自動 rollback）。

---

## 10. 範囲外（Out of Scope）

| 項目 | 理由 |
|------|------|
| UI/ビジュアル詳細（色 / フォント / モーション） | デザイン班専権 |
| 実装コード（TS / Python / SQL マイグレーション） | 詳細設計のみ、実装は Phase 7 cmd で別 task |
| 法令最終総合監査（COPPA / GDPR-K / 医療法 / 改正個人情報保護法 28 条） | 全機能完成後の別 cmd で実施（理事長殿御指示 2026-05-05） |
| 既存 award_xp / engine API の改修 | Anti-Duplication 厳守、変更禁止 |
| story-master.md と恐竜キャラ固有名の整合 | デザイン班 + 物語監修班専権 |
| ashigaru5 のゲームエンジン実装詳細 | ashigaru5 detail_design.md §1-§4 専権 |

---

## 11. 規律遵守チェック

| 項目 | 状態 |
|------|------|
| 実装着手禁止 | ✓（コード生成なし） |
| Anti-Duplication 厳守 | ✓（既存 Props 不変、新 kind なし） |
| ashigaru5 detail_design.md と CeremonyOverlay 統合 API 整合 | ✓（§7 SoT、ashigaru5 §5-10 で全 ✓） |
| 完了後 karo + gunshi + ashigaru5 三者へ inbox_write | ✓（履歴より、5/7 22:32 送信済） |
| 三者監査必須 | 進行中（5/8 01:24 前田 → 家康 audit_request 送信済） |
| §16 構造化ログ + correlation_id + 8 項目 | ✓（§9 ERR コード + §1-4 監査ログ） |
| §15 SH パターン採用 + 危険 D パターン回避 | ✓（§9-4） |
| デザイン班専権領域に立ち入らない | ✓（§10 明示） |

---

## 12. Open Items（家老 / 軍師 / 理事長判断待ち、15 件中ハイライト）

| ID | 事項 | 確認先 | 緊急度 |
|----|------|--------|--------|
| **OD1** | task YAML（subtask_kids_app_push_phase7_detail_design_001）が SoT に未反映 | 家老 | **高（着手前必須）** |
| **OD2** | 既存 `frontend/public/sw.js` 実在確認 | ashigaru6 + frontend 班 | **高（§2 Path 選定）** |
| **OD3** | 既存 ConsentForm 系コンポーネントの有無 | frontend 班 | **高（§4 UI 流用判断）** |
| **OD4** | `passport_members.pending_ceremony_at` / `last_ceremony_displayed_at` カラム実在 | backend 班 | **高（§3 dedupe）** |
| **OD5** | `family_link` 相当テーブル（保護者⇔小児）の有無 | backend 班 | **高（§4 配信先解決）** |
| OD6 | story-master.md と RANK_NAME の整合（VAPID 通知文言） | 物語監修 | 中 |
| OD7 | clinic_id=5（香椎照葉）専用 → 多医院展開時の specialty_mode 条件 | 家老（T15 連携） | 低 |
| OD8 | 個人情報保護法 28 条 + COPPA / GDPR-K 影響（§4-7） | Gemini 法令最終総合監査 | 中（実装前必須） |
| OD9 | target_path 補正：MainPC（`/mnt/c/...`）⇔ SecondPC（`/home/hakudokai/...`） | 家老 | 中 |
| OD10 | recordGameScore の冪等性 backend 拡張要否 | 軍師 + backend 班 | 中 |
| OD11 | 90 日 VAPID ローテ実行 cron / 監視 | 家老 | 中（運用） |
| OD12 | LINE Bot Flex Message テンプレート設計（fallback 経路） | デザイン班 + ashigaru6 | 中 |
| **OD13** | ashigaru5 detail_design.md 起草遅延（本書執筆時点で未存在） | ashigaru5 + 家老 | **高（§7 整合）** ← **5/8 までに ashigaru5 起草・整合確認済** |
| OD14 | `ceremony_event` テーブル新規追加 vs `passport_xp_log` 拡張のいずれかを採用 | 軍師 + backend 班 | 中 |
| OD15 | 夜間モードの「緊急」例外（§5-1 T6）の運用権限境界 | 家老 + 院長 | 低 |

---

## 13. 再現 source 一覧（v0.1 信長手動再構築版）

本書は **2026-05-08 22:55 ローカル消失事故** ののち、以下の資料を統合して再構築した。

### A. 抽出済 過去会話履歴（両アカウント Claude AI）

- `/tmp/ashigaru6_recovery/secondpc_extract.txt` — SecondPC ashigaru6 自身セッション、219 chunks ★最重要
  - 5/7 19:21 概念設計完成記録
  - 5/7 22:33 詳細設計 992 行配置記録
  - 5/7 22:55 完了報告（家老・軍師・ashigaru5 三方）
  - 5/8 00:55 〜 01:24 前田利家による三者監査 audit_request 履歴
- `/tmp/ashigaru6_recovery/main_3b101b68_extract.txt` — MainPC 信長/家老セッション、115 chunks
- `/tmp/ashigaru6_recovery/main_top_hits.txt` — 補助 top-hits 抽出

### B. 既存 git 内 docs

- `docs/kids_game_concept_design.md`（ashigaru5 概念設計、storyline mapping 起点）

### C. MainPC task YAML

- `queue/tasks/ashigaru6.yaml` の description 6 項目仕様
- inbox 履歴 msg_20260507_222405_caa37f13 / msg_20260507_222422_a0205b53（再配信版）

### D. 確認できなかった source（再構築の精度限界）

- `docs/kids_app_push_ceremony_design.md`（ashigaru6 5/7 概念設計、509 行）— SecondPC 側にのみ存在、git 未反映
- `docs/kids_game_detail_design.md`（ashigaru5 5/7 詳細設計、721 行）— SecondPC 側にのみ存在、git 未反映
- `docs/kids_app_push_ceremony_detail_design.md`（ashigaru6 5/7 詳細設計、992 行）— **本書の原本**、ローカル消失で参照不可

### E. 再構築の精度評価

- §1 VAPID 管理: **約 80%** 再現（90日ローテ・両鍵並走・vapid_key_access_log は履歴明示。具体 Layer 分類は信長補完）
- §2 Service Worker: **約 70%** 再現（Path A/B / 全イベント / カテゴリ別 cache は履歴明示。具体 DDL/コード周辺は信長補完）
- §3 CeremonyOverlay 5 種: **約 90%** 再現（variant 5 値 / Props 不変 / dedupe / replay は履歴明示の strict transcription）
- §4 parent_consent: **約 65%** 再現（wireframe / DDL 概念 / 14 歳未満 / opt-out / 撤回は履歴明示。具体カラム名は信長補完）
- §5 Rate Limit + fallback: **約 75%** 再現（4 階層 Limit / 三段 fallback / dead-letter / 観測閾値は履歴明示）
- §6 オフライン耐性: **約 80%** 再現（IndexedDB 4 store / リトライキュー / sync コリジョン / マルチデバイスは履歴明示）
- §7 統合 API SoT: **約 95%** 再現（ashigaru5 §5-10 整合確認済の最も確実な部分）
- §8 データモデル: **約 60%** 再現（DDL は信長補完、テーブル一覧と index 戦略は履歴一致）
- §9 エラーコード: **約 95%** 再現（ERR-PUSH-001..012 / ERR-CEREMONY-001..006 / ERR-CONSENT-001..002 採番は履歴明示）
- §10-§12 範囲外・規律・Open Items: **約 90%** 再現（OD1〜OD15 高優先 6 件は履歴明示）

総合再現精度: **約 80%**。詳細粒度（具体 DDL カラム名 / Layer 分類細目 / 文言）は信長補完であり、ashigaru6 復帰時に必ず本人監修・修正されたし。

---

## 14. 結論 — v0.1 信長手動再構築版

本書は **v0.1 信長手動再構築版** である。ashigaru6 復帰時に最終確定すること。Phase 7 cmd 発令前に以下を完遂すること:

1. ashigaru6 が本書を全面レビュー、不備・齟齬を v0.2 で修正
2. OD1（task YAML 更新）を家老が補正
3. OD2-OD5 高優先 4 件を Phase 7-α 着手前に決着
4. ashigaru5 detail_design.md §5-10 と本書 §7 の双方向整合を最終確認
5. 三者監査（軍師・Codex・Gemini）を v0.2 で実施し PASS をもって Phase 7 cmd 発令

以上、信長手動再構築版（2026-05-08 23:25 JST）。
