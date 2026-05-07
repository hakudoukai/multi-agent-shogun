---
name: inbox-alias-integrity
description: queue/inbox/ の旧名 alias↔canonical symlink 整合性を検証する。2026-05-08 split-brain 事故 (docs/incident_logs/2026-05-08_inbox_split_brain.md) の再発防止 mandate skill。
---

# inbox-alias-integrity

## 用途

queue/inbox/ で 3 つの旧名 alias が canonical へ正しく symlink されているか検証する:

- `queue/inbox/shogun.yaml` → `queue/inbox/nobunaga.yaml`
- `queue/inbox/karo.yaml` → `queue/inbox/hideyoshi.yaml`
- `queue/inbox/gunshi.yaml` → `queue/inbox/ieyasu.yaml`

`maeda.yaml` には alias 不在 (= 旧名なし、Phase 1 新設)。

## 背景

2026-05-08 00:14-00:52 に発生した queue/inbox/ split-brain 事故の真因は、`scripts/inbox_write.sh` の atomic replace `os.replace(tmp_path, $INBOX)` が INBOX が symlink の場合 symlink 自体を tmp で置換し、Phase 3 で設置された alias を破断したことにあった。

旧名 alias 経由で動作する agent (= 秀吉 AGENT_ID=karo, 家康 AGENT_ID=gunshi) と、新名 alias を直接書く agent (= 信長 inbox_write hideyoshi/ieyasu) の間で通信路が分裂し、約 37 分間「家老処理進まず」状態を引き起こした。

inbox_write.sh は dd706ad で恒久 fix 済 (= realpath 経由)。本 skill は再発検知の自動化を担う。

## 検出パターン

| パターン | 状態 | exit code | 影響 |
|---------|------|----------|------|
| alias が regular file 化 | symlink 破断 | 2 | split-brain 進行中 |
| alias が存在しない | alias 欠損 | 2 | 旧名経路の通信不通 |
| alias の symlink target が期待 canonical でない | mismatched | 2 | 誤動作 |
| canonical が存在しない | dangling | 2 | broken symlink |
| md5 不一致 (alias dereferenced ≠ canonical) | 内部不整合 | 2 | データ破損 |
| 全 pair 整合 | 健全 | 0 | OK |

## 使用方法

### Manual

```bash
bash scripts/checks/inbox_alias_integrity.sh
```

### PreToolUse hook (advisory only)

`.claude/settings.json` の `hooks.PreToolUse` に登録候補。**`|| true` 必須、絶対ブロック禁止** (CLAUDE.md §19.3 mandate):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command_pattern": "scripts/inbox_write\\.sh|scripts/inbox_watcher\\.sh",
        "command": "bash scripts/checks/inbox_alias_integrity.sh || true"
      }
    ]
  }
}
```

### Weekly cron (推奨)

```cron
0 7 * * 1 cd /path/to/multi-agent-shogun && bash scripts/checks/inbox_alias_integrity.sh 2>>logs/inbox_alias_integrity.weekly.log
```

## Implementation

`scripts/checks/inbox_alias_integrity.sh` 参照。timeout 5 秒、stderr 警告のみ、exit 1 は予約 (不使用)。

## False positive 想定

なし (= alias 構造の検査ゆえ deterministic)。

## Related

- docs/incident_logs/2026-05-08_inbox_split_brain.md — 起案動機、5 Why 分析
- scripts/inbox_write.sh — symlink 保護 atomic write (commit dd706ad)
- skills/symlink-aware-atomic-write/SKILL.md — 同事故の pattern audit 姉妹 skill
