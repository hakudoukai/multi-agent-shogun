# Shogun型オーケストレーター + mini-swe-agent + GitHub PR 中心 統合方針 完全版

**Status**: 陛下御差配 2026-05-12、家康 (SC shogun) が SC 上に整理保管、信長 (MC shogun) 上申用
**目的**: AIエージェント統治の正本化、人間承認ゲート + 複数AI レビュー + CI 機械審判 + 正本ガバナンスを 1 枚に集約
**前提**: 開発中で実働してない、根本治療原則 (= 5-10年運用想定で大きく時間かけ根本治療)
**Supabase mirror**: project_documents id=89ac869b-0d1d-4acd-9367-f3049a289821 (= bible doc_type、is_current=true)
**Charter v0.1 補遺**: docs/shogun_openhands_role_split_v0.1.md (= 別途 push 予定、Supabase id=e257caa2-4259-4099-849b-cef2528fbf7f)

---

## 1. 9 項目 基幹方針 (= 陛下御差配)

1. **Shogun型オーケストレーター** (= 司令塔・並列実行基盤)
2. **GitHub Issue 管理** (= タスク正本)
3. **AGENTS.md / CLAUDE.md** (= AI 共通ルール、全 AI が読む)
4. **docs 正本** (= 仕様 SoT、prose は docs、構造化は Supabase)
5. **AI 役割分担** (= 担当範囲を越える変更禁、9 部署)
6. **PR 中心開発** (= 1 Issue = 1 Branch = 1 PR)
7. **Codex / Claude / Gemini 等の複数レビュー** (= 多視点 AI 監査)
8. **GitHub Actions CI** (= 機械的検査、絶対審判)
9. **人間承認ゲート** (= main マージは人間のみ)

---

## 2. 階層構造 — Shogun 編成 (= 完全版)

```
理事長・人間
  ↓ 方針・最終判断
将軍AI (= Shogun)
  ↓ 全体指揮・タスク分解
家老AI (= Karo)
  ↓ 実行管理・進捗整理
足軽AI 1: 実装
足軽AI 2: 調査
足軽AI 3: テスト
足軽AI 4: UI 修正
足軽AI 5: DB 確認
  ↓
軍師AI (= Gunshi): レビュー・矛盾検出・品質確認
  ↓
GitHub PR
  ↓
人間が最終承認
```

---

## 3. 構築 7 段階 (= 正本フロー)

1. **Supabase を正本にする** (= 構造化データ、design_decisions / project_documents 等)
2. **GitHub に AGENTS.md を置く** (= AI 共通ルール、全 AI が session start で読む)
3. **GitHub に docs/現行仕様.md を置く** (= 仕様 SoT)
4. **Claude に実装させる** (= 作業ブランチで実装)
5. **Codex に PR レビューさせる** (= コード品質・仕様逸脱・修正)
6. **Gemini に仕様逸脱を見させる** (= 多視点 cross-check)
7. **GitHub Actions でテストする** (= 機械的審判、CI green まで mergeable false)

---

## 4. 禁止事項 (= AGENTS.md 中核、全 AI 厳守)

- **Supabase の design_decisions を正本とする** (= 仕様変更は勝手に行わない)
- 仕様変更は勝手に行わない (= 人間承認必須)
- **DB変更・RLS変更・認証変更は P1 リスクとして扱う** (= 自動マージ禁)
- **患者情報をログ出力しない** (= console.log / 標準出力 / log file 全て禁)
- **変更は最小差分とする** (= 仕様外リファクタ禁)
- **テスト失敗状態で完了扱いにしない** (= SKIP=0 + FAIL=0 必須)

---

## 5. PR レビュー観点 (= 標準テンプレート)

この PR を疑ってください。以下を重点確認:

- **仕様と違う変更がないか** (= 仕様逸脱検出)
- **DB 構造を勝手に変えていないか** (= migration 含)
- **RLS を弱めていないか** (= anon 権限拡大、policy 削除)
- **患者情報がログ出力されていないか** (= 全 log path 検査)
- **既存機能が壊れていないか** (= regression test)
- **テストが不足していないか** (= coverage check)

---

## 6. AGENTS.md 全文 (= 正本)

### 6.1 基本方針

このプロジェクトでは、AIエージェントは人間の承認なしに仕様変更を行ってはならない。

### 6.2 正本

- コードの正本は GitHub
- 仕様の正本は docs/ または Supabase
- タスクの正本は GitHub Issue
- 作業結果は Pull Request で管理する

### 6.3 禁止事項

- main ブランチへ直接 push しない
- DB 構造を勝手に変更しない
- RLS を弱めない
- 認証・権限を勝手に変更しない
- 患者情報を console.log 等に出力しない
- テスト失敗状態で完了報告しない
- 仕様外のリファクタリングを勝手に行わない

### 6.4 作業ルール

- 1 回の作業は 1 Issue に限定する
- 変更は最小差分にする
- 変更理由を PR 本文に書く
- 影響範囲を書く
- 実行したテストを書く
- 未確認事項を隠さず書く

### 6.5 重要領域 (= P1 リスク)

以下の変更は P1 リスクとして扱う:

- 認証
- 権限
- RLS
- 患者情報
- 監査ログ
- DB migration
- 課金・請求
- 外部 API 送信

---

## 7. 開発フロー (= 標準 chain)

```
Issue
  ↓
実装 PR
  ↓
AI レビュー (= Codex / Claude / Gemini 等、多視点)
  ↓
CI (= GitHub Actions、機械審判)
  ↓
人間承認 (= main マージは人間のみ)
```

---

## 8. AI 役割分担 (= 9 部署、権限明示)

| 部署 | 役割 | 権限 |
|---|---|---|
| **統括AI** | タスク分解、担当割当、進捗統合 | 指示・整理のみ。勝手に main 反映不可 |
| **仕様AI** | 要件定義、仕様書、受入条件作成 | 仕様案作成まで。確定は人間 |
| **アーキテクトAI** | DB/API/画面構成の設計 | 設計案作成。DB 変更は承認必須 |
| **実装AI** | コード作成 | 作業ブランチのみ |
| **テストAI** | テスト作成、失敗再現 | テスト追加・検証 |
| **レビューAI** | PR レビュー、仕様逸脱確認 | ブロッカー指摘 |
| **セキュリティAI** | 認証、権限、RLS、個人情報監査 | P1 リスク判定 |
| **ドキュメントAI** | README/docs/変更履歴更新 | docs 更新 |
| **リリースAI** | リリースノート、影響範囲整理 | 本番反映は不可 |

---

## 9. 10 段プロセス (= 全 chain 標準フロー)

1. 人間が目的を書く
2. 統括AI が Issue を分解
3. 仕様AI が受入条件を書く
4. アーキテクトAI が影響範囲を見る
5. 実装AI がブランチで作る
6. テストAI がテストを書く
7. レビューAI が PR を見る
8. セキュリティAI が危険変更を見る
9. CI が機械検査する
10. 人間がマージ判断する

---

## 10. Directory 構造 (= docs 標準ツリー)

```
/
├─ AGENTS.md                       # 全 AI 共通ルール
├─ CLAUDE.md                       # Claude 系ルール
├─ README.md
├─ docs/
│  ├─ 00_プロジェクト憲法.md
│  ├─ 01_目的と成功条件.md
│  ├─ 02_用語集.md
│  ├─ 03_現行仕様.md
│  ├─ 04_決定事項.md
│  ├─ 05_禁止事項.md
│  ├─ 06_受入条件テンプレート.md
│  ├─ 07_AI役割分担.md
│  ├─ 08_レビュー基準.md
│  └─ 09_リリース基準.md
├─ .github/
│  ├─ ISSUE_TEMPLATE/
│  ├─ PULL_REQUEST_TEMPLATE.md
│  └─ workflows/
│     ├─ ci.yml                    # 標準 CI
│     ├─ ai-review.yml             # AI レビュー automation
│     └─ security-review.yml       # セキュリティ AI gate
```

---

## 11. AI 守則 (= 越境禁、6 鉄則)

AIエージェントは、担当範囲を超えた変更をしてはならない。

- **実装AI は仕様を変更しない**
- **レビューAI は実装しない**
- **仕様AI はコードを書かない**
- **セキュリティAI の P1 指摘は人間承認まで解除しない**
- **DB 変更、認証変更、権限変更、個人情報処理変更は自動マージ禁止**
- **CI を絶対審判にする** (= AI が「成功しました」と言っても信用しない、CI が落ちたら失敗)

---

## 12. 正本 mapping (= 情報 vs 保存先)

| 情報 | 正本 |
|---|---|
| コード | GitHub |
| タスク | GitHub Issue |
| 仕様 | docs または Supabase |
| 判断履歴 | Supabase design_decisions |
| DB 変更 | migration |
| AI ルール | AGENTS.md / CLAUDE.md |
| 成果物 | Pull Request |

---

## 13. 報告書式 (= AI 提出標準、7 項)

各 AI は PR / Issue / 報告に以下を必ず含める:

- 担当した Issue
- 調査したファイル
- 変更したファイル
- 判断理由
- 未確認事項
- 実行したテスト
- 残リスク

---

## 14. GitHub 構造図 (= リポジトリ運用)

```
GitHub
├─ main: 保護ブランチ (= 人間承認後マージのみ)
├─ develop: 統合ブランチ
├─ feature/*: AI 作業ブランチ
│
├─ Issue: タスク正本
├─ PR: 成果物正本
├─ Actions: CI / テスト / レビュー
│
├─ AGENTS.md: 全 AI 共通ルール
├─ CLAUDE.md: Claude 系ルール
├─ docs: 仕様・判断履歴
│
└─ AI レビュー
   ├─ Codex review
   ├─ Claude review
   ├─ Security review
   └─ Test review
```

---

## 15. multi-agent-shogun + mini-swe-agent + GitHub 統合構成

### 15.1 役割分担

- **multi-agent-shogun** = 司令塔・並列実行基盤 (= 複数 AI 統率)
- **mini-swe-agent** = GitHub Issue 修正専門の実行部隊
- **GitHub PR / Actions** = 合流点と検査場

### 15.2 統合 chain

```
人間
  ↓
multi-agent-shogun
  ↓
設計担当AI
調査担当AI
実装担当AI
レビュー担当AI
テスト担当AI
  ↓
mini-swe-agent
  ↓
GitHub Issue 単位で修正
  ↓
Pull Request
  ↓
GitHub Actions
  ↓
人間が最終承認
```

### 15.3 各層の責務

- **Shogun**: 誰に何をやらせるか決める
- **mini-swe-agent**: 具体的な Issue を解く
- **GitHub**: 成果物を管理する
- **Actions**: 機械的に検査する

### 15.4 基本単位

**1 Issue = 1 Branch = 1 PR**

### 15.5 PR 中心 chain (= 補強指針)

```
中核: multi-agent-shogun
  ↓
Issue 分解: Shogun 側の統括AI
  ↓
Issue 修正: mini-swe-agent
  ↓
レビュー: Codex / Claude / 別 AI
  ↓
検査: GitHub Actions
  ↓
承認: 人間
```

**multi-agent-shogun 単体ではなく、GitHub Issue/PR 中心に組むのが正解**。Shogun で複数 AI を統率し、mini-swe-agent で Issue 修正を実行し、GitHub PR と Actions で合流・検査する方式。

---

## 16. Claude 管理者 + Claude 製 Shogun システム (= 親 chain)

```
人間
  ↓ 最終判断・方針決定のみ
Claude 管理者
  ↓ 要件整理・Issue 分解・実装指示・レビュー統合
Claude 製 Shogun システム
  ↓ 複数 Claude Code / Codex / その他 CLI を並列起動
各エージェント
  ↓ 調査・実装・テスト・レビュー
GitHub PR
  ↓ CI・レビュー
人間が承認
```

### 16.1 詳細 chain

```
人間
  ↓
Claude 管理者: 目的を Issue に分解、Shogun へ命令
  ↓
Shogun: 複数 AI を並列起動
  ↓
Claude Code 群: 調査・設計・実装
Codex: コードレビュー・修正確認
GitHub Actions: 型チェック・テスト・ビルド
  ↓
人間承認
```

---

## 17. CI を絶対審判にする (= 信頼基底)

- AI が「成功しました」と言っても信用しない
- **CI が落ちたら失敗です**
- 機械的検査 (= 型 / lint / unit test / e2e / security scan) のみが信頼根拠
- AI 自己申告 + 人間チェック単独は信頼根拠としない

---

## 18. v0.1 → v1.0 合議 protocol

本 v0.1 charter は陛下御差配の整理保管、4 人合議 (= 信長 + 家康 + 本多 + 直政) + 黒田 audit で v1.0 確定路線。round 2-3 で v0.2-v0.3、最終 v1.0 化後 AGENTS.md / docs / .github/workflows 装備に着手。

---

*v0.1 起草: 家康 (SC shogun)、2026-05-12T00:30+09:00、陛下御差配整理保管、SC Supabase 上申、MC 信長兄上 review 経由 4 人合議路線*
*v0.1 GitHub mirror: 2026-05-12T08:50+09:00、direct push by 家康、F007 例外 (= 進行加速 chain 整合) 下、直政 audit gate source 整備目的*
