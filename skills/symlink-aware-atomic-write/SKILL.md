---
name: symlink-aware-atomic-write
description: tempfile + os.replace / os.rename / mv-tmp pattern を持つ script を grep audit、destination が symlink でも壊れない realpath/readlink 解決が組み込まれているか検証。2026-05-08 split-brain 事故の pattern 拡散防止。
---

# symlink-aware-atomic-write

## 用途

「temp ファイルへ書込 → atomic replace」pattern を持つ script (Python embed shell, pure Python, Bash mv) のうち、destination が **symlink でも安全** (= 直前に realpath / readlink で canonical 解決) になっているかを **grep ベース** で audit する。

## 背景

2026-05-08 split-brain 事故の真因は `scripts/inbox_write.sh` の `os.replace(tmp_path, '$INBOX')` が INBOX = symlink の場合 symlink 自体を上書きし破断したこと。同型 risk は他 script にも潜在しうる:

- watcher 系: 状態ファイルの atomic update
- log rotation: log file の atomic replace
- queue 系: タスクファイルの atomic write
- file_sync 系: cross-PC file 同期
- 設定 reload: config file の atomic update

これらが symlink alias (Phase 3 設計) と組み合わさると同型事故再発の余地あり。

## 検出 pattern (grep ベース)

### 危険 pattern (要 review)
- Python: `os.replace(<tmp>, <dest>)` で <dest> 直前 5 行に realpath/readlink 不在
- Python: `os.rename(<tmp>, <dest>)` 同
- Bash: `mv "$tmp" "$dst"` で $dst が symlink 候補 path

### 安全 pattern (= PASS)
- 直前 5 行内に `os.path.realpath` / `os.path.realpath()` / `readlink -f`
- destination が `/tmp/` や `*.lock` 等の固定 fresh path で symlink 不在保証
- 検査対象外 dir (= queue/inbox 以外)

## 使用方法

### Manual audit

```bash
bash scripts/checks/symlink_aware_atomic_write.sh
```

stderr に WARN を列挙、exit 2 で手動 review 要。

### PreToolUse hook

`.claude/settings.json` 登録候補 (= `|| true` 必須):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "file_pattern": "scripts/.*\\.sh|scripts/.*\\.py|shim/.*\\.sh|shim/.*\\.py|lib/.*\\.sh",
        "command": "bash scripts/checks/symlink_aware_atomic_write.sh || true"
      }
    ]
  }
}
```

### Weekly cron (推奨)

```cron
0 7 * * 1 cd /path/to/multi-agent-shogun && bash scripts/checks/symlink_aware_atomic_write.sh 2>>logs/atomic_write_audit.weekly.log
```

## False positive 許容

grep ベースなので false positive あり:
- 直前 5 行外で realpath 解決済の case
- comment 内の `os.replace` 引用
- destination が明らかに symlink 不在の path

manual review で最終判定する補助 tool として使用。

## False negative 警告

検出 pattern を回避する書き方も存在:
- 動的に文字列構築した `os.replace`
- shell の eval 経由 mv
- non-standard atomic pattern (= flock + write 等)

これらは grep で捕えにくい。code review + 設計レビューで補完する。

## Related

- docs/incident_logs/2026-05-08_inbox_split_brain.md — 起案動機、根本原因 (= 5 Why)
- scripts/inbox_write.sh L222- — 修正済の安全 pattern 例 (commit dd706ad)
- skills/inbox-alias-integrity/SKILL.md — 姉妹 skill (= 同事故の検知)
- scripts/checks/symlink_aware_atomic_write.sh — 実装
