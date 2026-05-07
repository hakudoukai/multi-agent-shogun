---
name: lessons-to-skill
description: インシデント発生後に再発防止スキルを自動生成する meta-skill。事故の構造化分析 → 既存 skill 重複確認 → 新規 skill 雛形 + check スクリプト + ドキュメント追記提案を一括生成。CLAUDE.md §19 で post-incident に mandatory invoke される。
---

# Lessons to Skill (Meta-Skill)

## いつ使う (= mandatory)

**事故・トラブル・誤作動が発生し、復旧が完了した直後** に必ず invoke。CLAUDE.md §19 Post-Incident Lessons Capture で義務化されている。

## 使わない

- 通常の機能追加・リファクタリング (= 事故ではない)
- 設計判断による方針変更 (= 仕様変更、事故ではない)
- ユーザ依頼による軽微修正
- 事故が発生していないが「念のため」の探索 (= 該当事故事例がないと skill 化できない)

## 処理手順 (Step 1-7)

### Step 1: インシデント構造化

以下を YAML 形式で書き出す。`docs/incident_logs/<date>_<topic>.md` の冒頭に挿入する形でも OK。

```yaml
incident:
  timestamp: 2026-05-07T21:14
  detected_at: 2026-05-07T22:00
  detected_by: 理事長殿  # or shogun, gunshi, watcher, periodic_push, etc.
  what_happened: |
    1 行で事象
  root_cause: |
    5 Why で深掘りした最深層原因
  impact: |
    影響範囲・期間・実害の有無
  recovery_action: |
    どう復旧したか
  prevention_principle: |
    どこで防げたか — 1 文で
  prevention_skill: |
    スキル化可能か (Yes/No) と理由
```

### Step 2: 既存 skill 重複確認

```bash
ls skills/
grep -r "^description:" skills/*/SKILL.md
```

類似 skill があれば **拡張**、なければ **新規作成**。重複生成は禁止。

### Step 3: 新規 skill 雛形生成

`skills/<name>/SKILL.md`:

```markdown
---
name: <kebab-case>
description: 1 行で「何を防ぐ」か
---

# <Title>

## いつ使う (= mandatory)

具体的なトリガー条件 (= 抽象的でなく)

## 使わない

- 偽陽性ケース (重要 — これがないと過剰 invoke で疲弊)

## 必須チェック手順

具体的な bash コマンド or 操作手順

## 過去事例

- <date> <事故概要>
  詳細: docs/incident_logs/<file>.md
  教訓: 1 行で
```

### Step 4: check スクリプト生成

`scripts/checks/<name>.sh`:

要件:
- shebang `#!/usr/bin/env bash`
- `set -uo pipefail` (= `-e` は使わない、警告のみで止めないため)
- timeout 5 秒以内に終了
- exit code: `0=OK, 1=warning, 2=critical`
- stderr に判定根拠を出力 (= stdout は人間用の整形出力)

### Step 5: hook 登録提案

`.claude/settings.json` に PreToolUse hook 雛形を提示 (= 拙者が編集、理事長殿承認後 commit):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash scripts/checks/<name>.sh 2>&1 1>/dev/null || true",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**絶対の制約**:
- `|| true` 必須 (= 失敗してもブロックしない)
- timeout 必須 (= 10 秒以内、ハング防止)
- 警告は **stderr のみ**、stdout は静か (= 拙者の対話を汚さない)

### Step 6: CLAUDE.md 追記案 (= 理事長殿承認待ち)

新規ルールを CLAUDE.md に追記する場合は **必ず承認待ち**。提示形式:

```
追加場所: § X 末尾 / 新規 § N
追記内容: (= 引用ブロック)
理由: 1 行で
影響範囲: 全 agent / 特定 agent / 起動時のみ / etc
```

承認なしで CLAUDE.md を編集しない。

### Step 7: インシデントログ完成

`docs/incident_logs/<date>_<topic>.md` を以下のテンプレで完成:

```markdown
# Incident: <タイトル> (<date>)

## サマリ
## 発生・発見
## 事象
## 根本原因 (= 5 Why)
## 影響範囲
## 復旧アクション
## 防止策 (= 本事例から生成した skill)
## 教訓
## 関連 commit
```

## 強制力ルール

| ルール | 内容 |
|-------|------|
| skill 生成は理事長殿明示承認後に commit | 乱造防止 |
| 月次自己点検 | `docs/skills_telemetry.md` に invoke 回数 / false positive 率 を記録 |
| 3 ヶ月 invoke ゼロの skill は archive 候補 | 死蔵防止 |
| false positive 率 > 3% の skill は要修正 | ノイズ抑制 |
| skill 名は kebab-case | 命名統一 |
| description は 1 行 (= 100 文字以内) | 簡潔性 |

## 過去事例

- 2026-05-07 — pane-identity-verify (= 第 1 号 skill、本 meta-skill と同時生成)
  詳細: docs/incident_logs/2026-05-07_pane_misidentification.md
