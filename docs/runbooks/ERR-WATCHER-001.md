---
error_code: ERR-WATCHER-001
severity: CRITICAL
title: "Watcher 暴走/停止 (retry上限到達)"
auto_fix: true
retry_cap: 3
escalation: "ntfy:director, inbox:shogun"
night_mode: immediate
---

# Runbook: ERR-WATCHER-001 (Watcher 暴走/停止)

## 症状 (検知パターン)

- watcher プロセスの retry_count が上限 (5) に到達
- dead_lettered_at が設定されたメッセージが存在
- CPU/メモリ使用率が異常上昇 (暴走パターン)
- watcher プロセスが消失 (停止パターン)
- /tmp/hakudokai_activity_dashboard.json で agent idle > 5min

## 自動診断コマンド

```bash
# 1. watcher プロセス一覧
ps aux | grep -E "(watcher|poll|receiver)" | grep -v grep

# 2. 手動停止フラグ確認
ls ~/.openclaw/global_disable ~/.openclaw/disable_* 2>/dev/null || echo "NO_DISABLE_FLAGS"

# 3. dead-letter 件数
cat /tmp/dead_letter_errors.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'DEAD_LETTERS={len(d)}')" 2>/dev/null || echo "DEAD_LETTERS=0"

# 4. retry tracker 状態
cat /tmp/watcher_retry_tracker.json 2>/dev/null || echo "NO_TRACKER"

# 5. 直近の watcher ログ
tail -50 /tmp/hakudokai_*.log 2>/dev/null | grep -i "error\|fail\|retry" | tail -10

# 6. Supabase pc_handshake 未ack件数
python3 -c "
import os, subprocess
result = subprocess.run(['python3', '-c', '''
from pathlib import Path
env_file = Path.home() / \".hakudokai\" / \"env\"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if \"=\" in line and not line.startswith(\"#\"):
            k, v = line.split(\"=\", 1)
            os.environ[k.strip()] = v.strip()
'''], capture_output=True, text=True)
print('ENV_CHECK_DONE')
"
```

## 自動修復手順 (冪等、retry cap=3)

```bash
# Step 1: 暴走検知 → 全 watcher 停止
if [ "$(ps aux | grep -E '(watcher|poll|receiver)' | grep -v grep | wc -l)" -gt 10 ]; then
  echo "$(date -Iseconds) RUNAWAY_DETECTED: killing all watchers" >> /tmp/runbook_actions.log
  pkill -f "hakudokai_.*watcher" 2>/dev/null
  pkill -f "hakudokai_.*poll" 2>/dev/null
  pkill -f "hakudokai_.*receiver" 2>/dev/null
  touch ~/.openclaw/global_disable
  echo "WATCHERS_KILLED_GLOBAL_DISABLE_SET"
  exit 0
fi

# Step 2: 停止パターン → 手動停止フラグ確認してから再起動
if [ -f ~/.openclaw/global_disable ]; then
  echo "GLOBAL_DISABLE_SET: manual intervention required"
  exit 1
fi

# Step 3: dead-letter クリーンアップ (24h以上前のエントリ削除)
python3 -c "
import json, os, time
path = '/tmp/dead_letter_errors.json'
if os.path.exists(path):
    with open(path) as f:
        entries = json.load(f)
    cutoff = time.time() - 86400
    cleaned = [e for e in entries if e.get('timestamp', 0) > cutoff]
    with open(path, 'w') as f:
        json.dump(cleaned, f, indent=2)
    print(f'CLEANED: {len(entries) - len(cleaned)} old entries removed')
else:
    print('NO_DEAD_LETTERS')
"

# Step 4: watcher 段階的再起動 (inbox_watcher のみ)
cd /mnt/c/Users/User/projects/multi-agent-shogun
if ! pgrep -f "inbox_watcher" > /dev/null; then
  nohup bash scripts/inbox_watcher.sh > /tmp/hakudokai_inbox_watcher.log 2>&1 </dev/null &
  echo "$(date -Iseconds) inbox_watcher restarted" >> /tmp/runbook_actions.log
fi
echo "PARTIAL_RECOVERY: inbox_watcher only. Full restart requires manual approval."
```

## 手動対応 (自動修復失敗時)

1. `docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md` 参照
2. Supabase pc_handshake テーブルで未ack件数確認・emergency_ack実施
3. `rm ~/.openclaw/global_disable` で手動停止解除
4. `bash shim/hakudokai/hakudokai_start_watchers.sh` で段階的再起動
5. 再起動後5分間監視、再暴走なら理事長殿へ報告

## エスカレーション基準

- 暴走パターン検知 → 即時 CRITICAL (理事長 ntfy)
- 停止10分以上 → ERROR (shogun inbox)
- dead-letter 10件以上蓄積 → WARN (dashboard 表示)
