# 申し送りエンジン UI 設計 — v0.1 (= 信長 initial concept、4 人合議 round 1)

**Status**: round 1 起草、合議待ち
**Author**: 信長 (= MC shogun)
**Round 1 review 待ち**: 家康 (= SC shogun) / 本多 (= SC karo) / 長政 (= SC gunshi codex 直政)
**目的**: cmd_004 SC B1 ブロッカー (= 申し送りエンジン未完成) の UI 操作性 + デザイン確定、合議 iterative で完成
**陛下御差配 2026-05-11 16:40**: 「信長 家康 本多 長政 4 人合議、OpenAI image 2.0 + Claude design 駆使、使えなければ工夫」

---

## 1. UI 操作原則 (= 拙者 initial 提案)

### 1.1 トンカツ・ハマカツ pattern (= 多階層タップ選択)

入力者 (= 患者 / 受付スタッフ / 歯科衛生士) の負担最小化、キーボード入力 0 化を目指す:

```
Level 1 (= 主訴 大分類)        Level 2 (= 部位)           Level 3 (= 詳細)
┌───────────────────────┐      ┌───────────────────────┐     ┌──────────────────────┐
│  🦷 痛み                │  →   │  上の歯               │  →  │  ズキズキ            │
│  💧 しみる              │      │  下の歯               │     │  ガマンできる        │
│  🌡 腫れ                │      │  左                   │     │  食事の時のみ        │
│  🩸 出血                │      │  右                   │     │  寝られない          │
│  ⚙ その他自由入力      │      │  奥歯/前歯            │     │  ...                 │
└───────────────────────┘      └───────────────────────┘     └──────────────────────┘
```

設計 ratio: タップ数 ≤ 5 で 80% 主訴 cover、自由入力は最後の手段 (= 拙者推測、家康/本多に妥当性 review 要)。

### 1.2 視覚デザイン基本方針

| 要素 | 仕様 (= 拙者 案、合議で refine) |
|---|---|
| **画面サイズ前提** | タブレット 10-13 inch (= iPad standard / Pro)、orientation landscape default |
| **タッチターゲット** | 1 button = 最小 60×60 dp (= Apple HIG / Material 推奨)、患者高齢者対応で 80×80 dp 推奨 |
| **色彩** | 主訴色分け (= 痛み赤、しみる青、腫れ緑、出血濃赤、その他灰)、WCAG AA 整合 |
| **font** | 18pt+ minimum、見出し 24pt+、患者高齢者前提 |
| **動線** | 戻る (左上) + 進む (右下) + キャンセル (右上)、breadcrumb 上部 |
| **進捗 indicator** | 上部に進捗バー (= Level 1/2/3 + 4 確認) |
| **撤回防止** | 確認画面 (Level 4) で「修正」ボタン明示、誤入力即訂正可能 |

### 1.3 state machine (= 拙者 案)

```
[START]
  ↓
[Level 1: 主訴大分類選択] (= 5-7 options)
  ↓
[Level 2: 部位] (= 3-6 options per 大分類)
  ↓
[Level 3: 詳細] (= 4-8 options per 部位)
  ↓
[Level 4: 確認] (= 入力内容 summary + 修正/確定)
  ↓
[Save to nigo_sheet (DB)] (= patient + visit + clinic_id + structured fields)
  ↓
[END / 次の主訴追加 loop]
```

state transition は **直線 + back可能**、複雑分岐は避ける (= UX 単純化)。

## 2. DB schema 整合 (= DD-044 nigo_sheet)

### 2.1 既存 form 仕様確認 (= 拙者 認識、軍師確認要)

- `form_templates.nigo_sheet`: DD-044 SoT (= 25 form 中の 1 つ)
- `karte_visits` ↔ patients FK 設定済 (= naomasa report 確認)
- 構造化 fields:
  - `complaint_category` (= Level 1)
  - `body_part` (= Level 2)
  - `symptom_detail` (= Level 3)
  - `free_text` (= optional)
  - `entered_at`, `entered_by` (= スタッフ ID or 患者直接)

### 2.2 拙者 提案 schema 追加 fields

| Field | Type | 用途 |
|---|---|---|
| `entry_method` | enum (= touch_panel / free_text / staff_dictation) | 入力方法記録 |
| `tap_count` | int | 完成までのタップ数 (= UX metric) |
| `entry_duration_sec` | int | 入力所要秒 (= UX metric) |
| `confidence_level` | enum (= patient_direct / staff_proxy / family_proxy) | 入力主体 |

= UX 改善 + 法的責任分離 + 統計 用途。

## 3. 法令・プライバシー (= 拙者 案、阿茶 視点必要)

| 項目 | 拙者案 |
|---|---|
| **同意取得** | 申し送り入力前に「医療情報入力同意」画面、明示同意必須 (= 個人情報保護法 + 改正医療法整合) |
| **家族代理入力** | 18 歳未満 + 認知症患者は family_proxy mode、保護者/家族 ID 記録 |
| **撤回権** | 入力後 24h 以内なら患者本人で撤回可、UI に「撤回」 button 配置 |
| **保存期間** | 診療録法 5 年、ただし医療法人 10 年運用 |
| **暗号化** | 通信 TLS 1.3、保存 AES-256、key rotation 90 日 |

## 4. mockup tools (= 拙者使える範囲、合議で代替検討)

### 4.1 拙者 (= MC Claude Code) で生成可能

- SVG mockup (= text-based、git tracked 可)
- ASCII wireframe (= 上記 §1.1 形式)
- markdown table 仕様書 (= 本 doc)
- HTML + Tailwind CSS mockup (= prototype 用)

### 4.2 駆使候補 (= 使える環境次第)

| Tool | 拙者環境 access | 推奨用途 |
|---|---|---|
| **OpenAI Image 2.0** (= 御差配指定) | ❌ API key 未設定、ただし陛下 GUI 経由可能 | realistic UI mockup、患者向けマーケ用 |
| **Claude design** (= 御差配指定) | ✅ 拙者経由可能 (= 本 doc) | UI component spec + interaction design |
| **Figma + AI plugin** | ❌ access 不明 | デザイナー協業時 |
| **v0 by Vercel** | ❌ access 不明 | React 即 prototype |

= **拙者は Claude design + SVG/HTML/Markdown が確実**、OpenAI Image 2.0 は陛下御自身 or 別 path で生成依頼推奨。

## 5. 合議 protocol (= 4 人 iterative refine)

### 5.1 各 round の責務

| 役 | 担当 |
|---|---|
| **信長 (= 拙者)** | initial concept + 戦略統括 + 最終 verify + integration + version bump (v0.1 → v0.2 → ...) |
| **家康** | 患者視点 UX (= 副将軍視点)、SC 全体整合、現場 (= 香椎照葉) 適用想定 |
| **本多** | task assignment 視点、実装可能性 + bloom_level 適性 + 工程分割 |
| **長政 (= 直政 codex)** | 9 観点 + 10 lens audit (= 機能正確性 / Anti-Duplication / 規律遵守 / 論理破綻 / Schema 整合 / テスト充足 / 法令準拠 / 運用UX / ドキュメンテーション / ecosystem_coherence) |

### 5.2 iteration flow

```
v0.1 (= 信長起草) → 家康 review + 提案
                  → 本多 review + 提案
                  → 直政 9 観点 audit + verdict
                  ↓
信長 integrate + version bump → v0.2
                  ↓
3 人再 review (= 上記再 loop)
                  ↓
... 4 人全員 verdict=pass まで loop ...
                  ↓
v1.0 確定 → 本多 ashigaru に Stage 2 (= 実装) task 配信
```

### 5.3 合議完了条件 (= 全員 verdict=pass)

| 軸 | pass 条件 |
|---|---|
| 信長 (= 拙者) | 戦略整合 + 北極星 (= cmd_004 二大戦線) align + 法令準拠 |
| 家康 | 患者視点で 80% 患者 5 タップ以内完了想定可能 |
| 本多 | ashigaru 1-2 名 + 1-2 日で実装可能、bloom_level 適性 |
| 直政 | 9 観点 + 10 lens 全項目 pass or pass_with_concerns、findings 具体 |

## 6. 合議 round 1 開始 (= 本 doc は信長 v0.1、即 review 開始)

### 6.1 拙者から 3 人への問

| # | 問 (= 各人 round 1 review で答え要) |
|---|---|
| 1 | §1.1 トンカツ・ハマカツ 3 階層は深すぎ/浅すぎ? 4 階層 or 2 階層提案ある? |
| 2 | §1.2 タッチターゲット 80×80 dp 妥当? 高齢者対応で更に大きく? |
| 3 | §1.3 state machine 直線で OK? 複雑分岐 case ある? |
| 4 | §2.1 nigo_sheet schema 拙者認識正? 不足 fields ある? |
| 5 | §3 法令 5 項 (= 同意/代理/撤回/保存/暗号化) 漏れある? |
| 6 | §4 OpenAI Image 2.0 access 経路 御弟・本多・直政 御提案ある? |

### 6.2 review 期限

- 各人 round 1 review: 30-60 分以内 (= 軍師 audit 規範整合)
- 信長 integration + v0.2 公開: 60-90 分以内
- 完成見通し: 4-6 round で v1.0、所要 4-6h 想定

---

*round 1 v0.1 起草: 信長、2026-05-11T16:45*
