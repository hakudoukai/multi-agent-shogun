# 小児アプリ ミニゲーム概念設計 — 恐竜 vs 虫歯菌

- task_id: subtask_kids_game_concept_design_001
- parent_cmd: cmd_full_activation_2026_05_07
- 文書種別: 概念設計（Phase 7 パスポート連携の準備段階）
- 範囲: 設計のみ。実装コード・UI ビジュアル要素は含まない（デザイン班専権）
- base_commit: 79ac2e74
- author: ashigaru5（SecondPC, hakudoukai@gmail.com）
- updated: 2026-05-07

---

## 0. 前提・正本参照と未参照事項（Anti-Duplication）

### 0-1. 参照済み正本

| # | 正本 | 所在 | 利用方法 |
|---|------|------|----------|
| A | DD-126 README | `frontend/src/features/teriha-passport/README.md` (DentalBI) | 全体仕様・テーブル群・ミニゲーム6種一覧 |
| B | 型定義 | `frontend/src/features/teriha-passport/types.ts` | AgeTier / RankCode / GameCode / PassportStats |
| C | 既存 MinigameMenu | `frontend/src/features/teriha-passport/components/MinigameMenu.tsx` | 6種メニュー実装、recordGameScore 接続点、cleared 判定 (score>=50) |
| D | 既存 CeremonyOverlay | `frontend/src/features/teriha-passport/components/CeremonyOverlay.tsx` | kind=`tier_up`/`birthday`/`graduation`、勝利時拡張呼び出し点 |
| E | 既存 MyStatusCard | `frontend/src/features/teriha-passport/components/MyStatusCard.tsx` | XP バー / ランク表示、xp_log 加算で自動更新 |
| F | 既存 ageTier engine | `frontend/src/features/teriha-passport/engine/ageTier.ts` | RANK_TABLE / resolveAgeTier / rankForXp / xpToNext |
| G | 既存 engine (backend) | `backend/services/teriha_passport_engine.py` | award_xp / mission_assign / passport_adventure_mapping 参照 |
| H | 既存 API | `backend/routers/teriha_passport.py` (prefix `/api/teriha-passport`) | recordGameScore / assignMission / completeMission / getDashboard |
| I | 棚卸し台帳 | `context/dentalbi-inventory.md` | 47モジュール / ~1,100ファイル / ~227,000行 |
| J | 統合実証マスターコンテキスト | `context/teriha-zero-wait.md` §2-4 / §3 / §11 | 残件分類・既存資産マップ・cmd_t13_002 監査結果 |

### 0-2. 本タスクで参照できなかった正本（要 follow-up）

| # | 正本 | 状況 | 影響範囲 | 対処 |
|---|------|------|----------|------|
| α | `docs/story-master.md`（69KB / 5/5 完成、世界観・物語設計の正本） | SecondPC 側に未同期 | 恐竜キャラ造形・固有名・物語接続点 | **本設計書ではキャラ固有名を伏せ字で記述**（後段 §3-1 参照）。MainPC 側で家老が story-master.md と整合性監査を行うこと。改変禁止は遵守。 |
| β | `biロゴ/アプリ/てりはキョウリュウおうこくパスポート.pdf` | デザイン班正本、参照不要（ビジュアルは範囲外） | — | 範囲外につき扱わない |

### 0-3. Anti-Duplication 確認チェックリスト

```
[x] DentalBI で teriha-passport / minigame / cavity_hunt / CeremonyOverlay / passport_xp_log を grep 済
[x] context/teriha-zero-wait.md §2-4・§3・§11 既存資産リスト確認済
[x] context/dentalbi-inventory.md 棚卸し参照済
[x] 新規ファイルは本概念設計書 1 本のみ（kids_game_concept_design.md）
[x] 既存 MinigameMenu / CeremonyOverlay / MyStatusCard / passport_xp_log / passport_adventure_mapping を **全て流用前提** とし、新規テーブル / 新規 renderer / 新規エンジン / 新規キャラを設計しない
```

---

## 1. ゲームコア仕様

### 1-1. ポジショニング

「恐竜 vs 虫歯菌」は、DD-126 で既に登録されている **既存ゲームコード `cavity_hunt`（むしばさがし）** の戦闘ロジック詳細化である。新規 GameCode は追加しない。

```
GameCode = 'cavity_hunt'   ← 本概念設計の対象
（他5種 brushing_rhythm / food_quiz / prevention_quiz / mouth_exercise / tooth_adventure_rpg は別 DD で扱う）
```

### 1-2. 1 ゲームの長さ

| 項目 | 値 | 根拠 |
|------|-----|------|
| 標準プレイ時間 | 30 秒 | タスク要件 |
| 起動～開始までのバッファ | 3 秒以内 | 来院前後の隙間時間（待合・帰路）想定 |
| 結果表示～Ceremony までの遷移 | 2 秒以内 | 注意散漫前に勝利演出を見せる |

### 1-3. 年齢別難易度（既存 AgeTier 5 段階に準拠）

タスク文「3-6歳 / 7-12歳 / 13歳+」は、既存 AgeTier の 5 区分にマップする。**新規難易度区分を作らない**（重複防止）。

| AgeTier | 年齢 | 既存ランク | 推奨難易度パラメータ（概念） | コピー調 |
|---------|------|------------|--------------------------------|----------|
| egg | 0-2 | tamago | プレイ不可。保護者代理タップで「みた」扱い、XP 付与は最小 | おうちの人と一緒 |
| chick | 3-6 | hiyoko | 敵速度 1.0x / HP 1 / 敵数少 / 救済しきい値 高 | 博多弁・絵本調 |
| adventurer | 7-9 | bokensha | 敵速度 1.3x / HP 1-2 / 波状出現 | ミッション系 |
| hero | 10-12 | yusha | 敵速度 1.6x / HP 2 / 波状+ボス1 | 勇者語り |
| kingdom_warrior | 13-15 | okoku_senshi | 敵速度 2.0x / HP 2-3 / 波状+ボス1+連戦 | 王国戦士・卒業 |
| parent | 保護者 | — | プレイ対象外（観覧 / 履歴閲覧のみ） | ダッシュボード |

数値はパラメータ枠の **概念配分** であり、実装時にゲーム班が数式化する。色・サイズ・モーション具体は範囲外。

### 1-4. 勝敗条件

| 状態 | 判定 |
|------|------|
| **勝利**（cleared=true） | 制限時間内に敵討伐数 ≥ ageTier 別しきい値、**かつ** スコア ≥ 50（既存 cleared 判定値、`MinigameMenu.tsx` 既定） |
| **敗北**（cleared=false） | 上記未達 |

スコアは `0..100` 正規化値。既存 `recordGameScore({score, cleared})` 引数仕様を変更しない。

### 1-5. 敗北時の救済

| 段階 | 振る舞い |
|------|----------|
| 1 回目 | 即やり直し可。敗北分の XP 付与なし。 |
| 2 回目以降 | 「まだまだだね」表示は既存仕様（MinigameMenu.tsx 64 行目）。**XP 半減付与は行わない**（passport_xp_log の付与トリガを `cleared=true` に固定し、XP 経済の乱れを避ける）。 |
| 連敗時 | 1 日 3 連敗で別ゲーム推薦オーバーレイ（過剰挫折防止）。具体オーバーレイは Phase 7 本実装時にデザイン班案を待つ。 |

> **設計判断**: タスク文の「経験値半減付与」案は既存 XP 設計（visit:30 自動 / mission_complete:reward_xp）との整合性を検討した結果、**採用しない**。理由は二重: (a) 敗北報酬は学習動機を逆転させる懸念、(b) 既存 award_xp は単一トリガ前提で書かれており、「半減」分岐を入れると engine API が膨らむ。家老 / 家康の判断で覆って良い。

---

## 2. 戦闘ロジック概念

### 2-1. プレイヤー側キャラクター（恐竜）

**新規キャラ作成禁止**。以下の既存アセットのみを参照する。

| 既存アセット | 所在 | 役割 |
|--------------|------|------|
| `assets/characters/dino_family.png` | `frontend/src/features/teriha-passport/assets/` | プレイヤー恐竜の画像ソース |
| 怪獣ロゴ（`怪獣.png` 他） | `Desktop/biロゴ/ロゴ/` | ヒーロー恐竜のシンボル |
| `world_theme_id=3`（恐竜王国） | passport_members 既定値 | 世界観テーマ ID 固定 |

プレイヤー恐竜の **固有名・性格・台詞** は `docs/story-master.md` に依存する。本書ではプレースホルダ `<DINO_HERO>` で記述し、固有名割当は story-master.md 整合性監査時に確定（後段 §8 Open Items）。

### 2-2. 敵キャラクター（虫歯菌）

**既存 90 敵テーブル流用前提**（context/teriha-zero-wait.md §3 #7 「passport_*テーブル群: 9テーブル+95mapping+12rank+90敵」）。`asset_master` に placeholder key 登録済（DD-126 README §非対象 / 残件 より）。

| 種別 | 概念 | 既存 90 敵プールからの選定基準 |
|------|------|--------------------------------|
| 雑魚菌 | HP 1、移動のみ | 「mutans 系」相当を当てる |
| 中ボス菌 | HP 2、攻撃あり | 「lactobacillus 系」相当 |
| ボス菌 | HP 3、特殊行動 | 各 AgeTier ボス想定（hero/kingdom_warrior 用） |
| 群体 | HP 1×N、波状 | 雑魚菌の演出変種 |

**90 敵プールの構造詳細は本書範囲外**（asset_master の placeholder→実体化はデザイン班作業）。本設計は「型」の枠だけ提示する。

### 2-3. 敵出現パターン

| パターン | AgeTier 適用 | 概念 |
|----------|--------------|------|
| 単発 | egg / chick | 1 体ずつ、画面端から登場 |
| 波状 | adventurer / hero | 3-5 体ずつのウェーブ ×3 |
| ボス戦 | hero / kingdom_warrior | 雑魚 1 ウェーブ → ボス 1 体 |
| 連戦 | kingdom_warrior | 波状 + ボス、勝利後即次戦オプション |
| ランダム要素 | 全 tier | 出現位置は擬似乱数（同一 member_id+日付シードで再現性確保、デバッグ容易化） |

### 2-4. 攻撃方法

| 方法 | 適用 tier | 端末 | 備考 |
|------|-----------|------|------|
| タップ | 全 tier | iPad / スマホ / タブレット | 一次入力。マルチタッチ対応 |
| スワイプ | adventurer 以上 | 同上 | 連続討伐コンボ |
| ボタン押下 | 全 tier（アクセシビリティ） | 同上 | 単一スイッチ操作対応 |

ジャイロ / 音声 / カメラ入力は **範囲外**（Phase 7 で再評価）。理由は保護者同意フロー（§7-7）を簡素化するため。

### 2-5. passport_adventure_mapping（95 マッピング）連携

既存 `passport_adventure_mapping` テーブル（context/teriha-zero-wait.md §3 #7、約 95 件）は、来院処置コード（`procedure_code`）→ ミッション / 敵討伐 への変換を担う。

```
[来院/予約] → assignMission API
       → passport_adventure_mapping 参照（既存：teriha_passport_engine.py L211-)
       → passport_mission_log INSERT（mission_type='minigame' 含む）
       → ホーム画面で「今日の冒険：cavity_hunt をプレイ」が出現
       → ゲーム終了 → recordGameScore + completeMission（cleared 時）
```

**このフローに新規テーブル / 新規マッピングは追加しない**。既存 95 件のうち `mission_type='minigame'` 行が cavity_hunt の起動条件となる。具体 procedure_code → cavity_hunt 紐付け一覧の改訂は本タスク範囲外（マッピング表のメンテナンスはデータ運用班 / 家老マター）。

---

## 3. データフロー

### 3-1. ゲーム開始から MyStatus 反映までの流れ

```
[ユーザー操作]
   ↓ MinigameMenu から cavity_hunt をタップ
[フロント: cavity_hunt ゲームコンポーネント（Phase 7 新設、本書はその仕様骨格）]
   ↓ 30 秒プレイ → score / cleared 算出
[既存 API: api.recordGameScore({member_id, game_code:'cavity_hunt', score, cleared})]
   ↓
[既存 backend: routers/teriha_passport.py /games/score]
   ↓
[既存 engine: teriha_passport_engine.py]
   ├─ passport_game_score INSERT
   ├─ cleared=true なら award_xp(cavity_hunt 報酬 XP)
   │     ├─ passport_xp_log INSERT
   │     └─ passport_members.total_xp UPDATE + rank 昇格判定
   └─ rank が変わった場合は member_id に「tier_up_pending」フラグ返却（既存仕様の有無は実装時要確認）
[フロント: getDashboard で再取得]
   ↓
[MyStatusCard が xp / rank を再描画（既存）]
   ↓ rank 昇格時
[CeremonyOverlay kind='tier_up' 拡張呼び出し]
   message: "<RANK_NAME> にしんかしたよ！"  ← story-master.md 整合性は後段 §8
```

### 3-2. CeremonyOverlay 接続点（ashigaru6 タスクと連動）

既存 `CeremonyOverlay.tsx` の Props は `{ kind, message, onDismiss }` の 3 引数。**API 変更は不要**。

| 既存 kind | 既存用途 | 本ゲーム連携 |
|-----------|----------|--------------|
| `tier_up` | 年齢移行儀式 | **rank 昇格時に流用**（cavity_hunt 勝利が引鉄になり得る） |
| `birthday` | 誕生日 | 連携なし |
| `graduation` | 15 歳卒業式典 | 連携なし |

ashigaru6 が担当する儀式拡張側で、`tier_up` の発火条件に「cavity_hunt 勝利による昇格」を含めるかは ashigaru6 の設計領域。本書では **API 表面を変えない方針** のみ提示。

### 3-3. 推奨 XP 報酬テーブル（cavity_hunt 専用、概念）

| AgeTier | 勝利 XP | 完全勝利（時間 5 秒以上残し） |
|---------|---------|-------------------------------|
| egg | 5 | 5 |
| chick | 10 | 12 |
| adventurer | 15 | 20 |
| hero | 20 | 28 |
| kingdom_warrior | 25 | 35 |

数値は既存 RANK_TABLE（tamago=0 / hiyoko=100 / bokensha=300 / yusha=700 / okoku_senshi=1500）を踏まえ、**1 日複数回プレイで 1 ランク跳ばないバランス**を概念配分。実装時に運用班が調整。

---

## 4. RLS 整合性（ashigaru2 タスクと連動）

### 4-1. 原則

| ルール | 実装方針 |
|--------|----------|
| `clinic_id` 別データ分離 | 全 passport_* テーブル既存 RLS に準拠（**新規ポリシーを書かない**） |
| 患者本人のみ自身のスコア閲覧可 | `passport_game_score` の SELECT を `auth.uid()` ↔ `passport_members.patient_id` で照合（既存パターン踏襲） |
| 保護者モード | `passport_members.parent_mode_enabled=true` の場合、子の score を保護者 auth.uid で閲覧可。書込は本人のみ。 |
| clinic_id=5 専用設定 | 香椎照葉こどもとママの歯科医院専用。多医院展開時は specialty_mode=`teriha_kingdom` を条件に追加（既存 T15 基盤） |

### 4-2. ashigaru2 RLS 設計タスクへの依頼事項

ashigaru2 の RLS 設計タスク（task_id 不明、要 inbox 連携）に対して、本書から以下の **要件のみ** を申し送る：

```
- passport_game_score への INSERT/SELECT は member_id 経由
- 子 ↔ 保護者のリンクは passport_family_link を SoT とする
- 新規ポリシーは作らない、既存 9 テーブルの RLS パターンに合わせる
```

具体ポリシー文（`CREATE POLICY ...`）は ashigaru2 の専権領域につき、本書では記述しない。

---

## 5. パフォーマンス目標

### 5-1. ハードウェア前提

| 端末 | 想定 |
|------|------|
| iPad | iPad 第 9 世代以降（A13 以上） |
| スマホ | iPhone SE 第 2 世代 / Android Snapdragon 7-series 以降 |
| タブレット (Android) | 上記同等以上 |

### 5-2. 数値目標

| 指標 | 目標 | 根拠 |
|------|------|------|
| フレームレート | 60fps（最低保証 30fps） | 30 秒短時間ゲームのため没入優先 |
| メモリ消費 | < 100MB（PWA / WebView） | 親アプリ DentalBI と同居前提 |
| 起動～プレイ可能 | < 3 秒 | 待合時間の隙間想定 |
| アセット初回 DL | < 2MB（gzipped） | モバイル回線配慮 |
| アセット 2 回目以降 | キャッシュヒット 100%（Service Worker） | オフライン耐性（次項） |

### 5-3. オフライン耐性（ashigaru6 タスクと連動）

| 状態 | 振る舞い |
|------|----------|
| オンライン | 通常フロー |
| 一時オフライン（送信失敗） | スコアを localStorage に保留 → 再オンライン時に `recordGameScore` リトライ |
| 完全オフライン起動 | プレイ可（ローカルのみ）、結果は次回オンライン時 sync。CeremonyOverlay の rank 昇格判定はオフラインでは保留（rank 計算は backend 経由が現状仕様） |
| Service Worker 戦略 | アセットは Cache-First、API は Network-First（リトライキューあり） |

具体 Service Worker 実装は ashigaru6 担当領域。本書は API 契約（リトライ可能、冪等性）のみ要件化する。

> **冪等性メモ**: `recordGameScore` の冪等性は現状の API 表面では保証されていない可能性あり。リトライキュー実装時に「同一 member_id + game_code + 端末発生 timestamp」での重複排除を ashigaru6 側で行うことを推奨。backend 拡張は後続 DD。

---

## 6. 推奨実装順（難易度・優先度ソート）

```
Phase 7-α（必須・軽）
  1. cavity_hunt ゲーム本体スケルトン
     - MinigameMenu の handlePlay からタップ起動
     - 30秒タイマー / score=0..100 / cleared 判定
     - 既存 recordGameScore 呼出（既存 API 改修ゼロ）

Phase 7-β（必須・中）
  2. 敵出現パターン（雑魚波状のみ）
  3. AgeTier 別パラメータ反映
  4. 敗北時やり直し UI
  5. 完全勝利ボーナス XP

Phase 7-γ（推奨・重）
  6. 中ボス / ボス
  7. 連戦モード（kingdom_warrior 限定）
  8. CeremonyOverlay tier_up 連携（ashigaru6 と協調）

Phase 7-δ（任意・軽〜中）
  9. オフライン Service Worker（ashigaru6）
 10. 連敗救済オーバーレイ
 11. アクセシビリティ対応（単一スイッチ / 大ボタンモード）
```

各 Phase は独立 DD として切り出し可能。Phase 7-α だけで MVP は機能する。

---

## 7. デザイン班との擦り合せ事項リスト

本書では **書かない** 事項を以下に列挙し、デザイン班マターとして申し送る。

| # | 事項 | 担当 | 期限の参考 |
|---|------|------|------------|
| 1 | 恐竜ヒーローのビジュアル / 色 / 表情変化 | デザイン班 | Phase 7-α 着手前 |
| 2 | 90 敵プールの placeholder → 実イラスト化 | デザイン班 | Phase 7-β 着手前 |
| 3 | タップ / スワイプの視覚フィードバック（パーティクル等具体） | デザイン班 | Phase 7-α 着手前 |
| 4 | CeremonyOverlay の演出強化（既存ベースを尊重） | デザイン班 + ashigaru6 | Phase 7-γ |
| 5 | コピー文言（AgeTier 別、博多弁 / 勇者語り 等） | デザイン班 + 物語監修 | story-master.md と整合 |
| 6 | サウンド（BGM / SE） | デザイン班 | Phase 7-β |
| 7 | プレイ時の保護者向け表示（途中介入抑止 vs 危険時介入のバランス） | デザイン班 + 法令 | §8 と連動 |
| 8 | 9 歳以下向け簡易チュートリアル | デザイン班 | Phase 7-α |

---

## 8. Open Items（家老 / 家康 / 理事長判断待ち）

| # | 事項 | 確認先 | 緊急度 |
|---|------|--------|--------|
| O1 | story-master.md と本書の整合性確認（恐竜ヒーロー固有名 / 物語接続） | 家老 + 物語監修 | 高（Phase 7 着手前必須） |
| O2 | 敗北時 XP 半減を採用するか（本書では非採用案） | 家康 + 理事長 | 中 |
| O3 | passport_adventure_mapping のうち cavity_hunt 紐付け対象 procedure_code 一覧の改訂可否 | データ運用班 + 家老 | 中 |
| O4 | recordGameScore の冪等性（端末側 timestamp / nonce 受入）API 拡張可否 | 家康 + backend 班 | 低（Phase 7-δ で再評価） |
| O5 | clinic_id=5 専用 → 多医院展開時の specialty_mode 条件追加 | 家老（T15 連携） | 低（後続 DD） |
| O6 | 個人情報保護・保護者同意フローへの影響（§7-7） | Gemini 法令監査 | 中（実装前必須） |
| O7 | target_path 補正：タスク YAML の `/mnt/c/Users/User/projects/...` は SecondPC では存在しないため WSL 経路 `/home/hakudokai/projects/multi-agent-shogun/docs/` に配置した。MainPC へ git 反映時の同期方針を家老が決定。 | 家老 | 中（次タスク発令前） |

---

## 9. 完成基準（acceptance_criteria）対照

| タスクYAML 完成基準 | 本書での対応箇所 | 充足 |
|---------------------|------------------|------|
| 30秒1ゲーム / 年齢別難易度 / 勝利演出経路 全て概念設計 | §1-2 / §1-3 / §3-1, §3-2 | ✓ |
| story-master.md 既存キャラとの整合性確認（キャラ新規追加禁止） | §0-2 α / §2-1 / §8 O1 | △（参照不能のため伏せ字 + 監査依頼） |
| 95 mapping との連携経路明示 | §2-5 | ✓ |
| CeremonyOverlay 接続点明示（ashigaru6 タスクと連動） | §3-2 | ✓ |
| clinic_id 別 RLS 整合性（ashigaru2 タスクと連動） | §4 | ✓ |
| 新規ファイルは docs/kids_game_concept_design.md 1 本のみ | 本書のみ作成 | ✓ |

△項目は §8 O1 で家老監査を要求しているため、家老マターとして完了報告に含める。

---

## 10. 規律遵守チェック

| 規律 | 状態 |
|------|------|
| Anti-Duplication 厳守（既存 teriha-passport / story-master / mapping 改変なし、流用前提） | ✓ |
| 実装コード生成禁止 | ✓（型シグネチャ言及はあるが疑似コード / 実装なし） |
| UI/ビジュアル要素はデザイン班専権につき記述しない（色 / 配置 / アニメーション具体） | ✓（§7 で申し送りのみ） |
| commit/push 不要（ドラフト）、家老レビュー後に commit 判断 | 遵守（push しない） |
| Test Rules: SKIP=FAIL / preflight | 概念設計のためテスト対象外 |
| Root Cause 4 パターン | 旧版併存・同名重複なし（cavity_hunt 既存を流用、新 GameCode 追加なし） |

---

以上。
