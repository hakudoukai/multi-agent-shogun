---
error_code: ERR-INFRA-001
severity: CRITICAL
title: "インフラ障害 (tmux/WSL/SSH/unack閾値超過)"
auto_fix: true
retry_cap: 3
escalation: "ntfy:director, inbox:shogun"
night_mode: immediate
---

# Runbook: ERR-INFRA-001 (インフラ障害)

## 症状 (検知パターン)

- tmux session が消失 (shogun/multiagent)
- WSL2 プロセス異常 (メモリ不足、vmmem 暴走)
- SSH 接続断 (SecondPC への疎通不可)
- Supabase pc_handshake unack 件数閾値超過 (50件+)

## 自動診断コマンド

```bash
# 1. tmux session 確認
tmux list-sessions 2>/dev/null || echo "TMUX_DOWN"

# 2. WSL メモリ使用量
free -m | awk '/Mem:/{print "MEM_USED=" $3 "MB MEM_TOTAL=" $2 "MB USAGE=" int($3/$2*100) "%"}'

# 3. ディスク使用量
df -h / | tail -1 | awk '{print "DISK=" $5}'
df -h /mnt/c 2>/dev/null | tail -1 | awk '{print "WINDOWS_DISK=" $5}'

# 4. SSH SecondPC 疎通 (タイムアウト3秒)
ssh -o ConnectTimeout=3 -o BatchMode=yes hakudokai@192.168.11.47 "echo OK" 2>/dev/null || echo "SECONDPC_UNREACHABLE"

# 5. 重要プロセス確認
pgrep -f "inbox_watcher" > /dev/null && echo "INBOX_WATCHER=UP" || echo "INBOX_WATCHER=DOWN"
pgrep -f "activity_monitor" > /dev/null && echo "ACTIVITY_MONITOR=UP" || echo "ACTIVITY_MONITOR=DOWN"

# 6. inotify 上限確認
cat /proc/sys/fs/inotify/max_user_watches 2>/dev/null
find /proc/*/fd -lname "inotify" 2>/dev/null | wc -l
```

## 自動修復手順 (冪等、retry cap=3)

```bash
# Step 1: tmux session 復旧
if ! tmux has-session -t shogun 2>/dev/null; then
  echo "$(date -Iseconds) TMUX_RECOVERY: shogun session missing" >> /tmp/runbook_actions.log
  # tmux session の再作成は shutsujin_departure.sh が担当
  echo "ACTION_REQUIRED: run ./shutsujin_departure.sh to restore tmux"
fi

# Step 2: メモリ逼迫時のキャッシュ解放
MEM_AVAIL=$(free -m | awk '/Mem:/{print $7}')
if [ "${MEM_AVAIL:-0}" -lt 500 ]; then
  sync
  echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
  echo "$(date -Iseconds) CACHE_DROPPED: available was ${MEM_AVAIL}MB" >> /tmp/runbook_actions.log
fi

# Step 3: unack 件数チェック + emergency_ack
python3 -c "
import json, os, time
from pathlib import Path

env_file = Path.home() / '.hakudokai' / 'env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip().strip('\"').strip(\"'\")

print('UNACK_CHECK: requires Supabase client - manual verification recommended')
"

# Step 4: inbox_watcher 再起動 (停止時)
if ! pgrep -f "inbox_watcher" > /dev/null; then
  cd /mnt/c/Users/User/projects/multi-agent-shogun
  nohup bash scripts/inbox_watcher.sh > /tmp/hakudokai_inbox_watcher.log 2>&1 </dev/null &
  echo "$(date -Iseconds) inbox_watcher restarted" >> /tmp/runbook_actions.log
fi
```

## 手動対応 (自動修復失敗時)

1. WSL 再起動: PowerShell `wsl --shutdown` → `wsl` で再起動
2. tmux 完全再構築: `./shutsujin_departure.sh`
3. SecondPC 確認: 物理的にモニタ確認 or Tailscale ping
4. unack emergency_ack: `docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md` §対処法 参照
5. inotify 上限拡張: `echo 65536 | sudo tee /proc/sys/fs/inotify/max_user_watches`

## エスカレーション基準

- tmux 全消失 → CRITICAL (全エージェント停止)
- メモリ使用率 95%+ → CRITICAL
- SecondPC 5分以上到達不能 → ERROR
- unack 100件超過 → CRITICAL (暴走の兆候)
