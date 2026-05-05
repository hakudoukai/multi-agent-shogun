---
error_code: ERR-EKARTE-001
severity: ERROR
title: "電子カルテ visit 作成失敗"
auto_fix: true
retry_cap: 3
escalation: "ntfy:director, inbox:shogun"
night_mode: defer_unless_critical
---

# Runbook: ERR-EKARTE-001 (電子カルテ visit 作成失敗)

## 症状 (検知パターン)

- ekarte 入力時、Supabase visits テーブルへの INSERT が失敗
- フロントエンドで「カルテの記録に失敗しました」エラー表示
- backend ログに `ERR-EKARTE-001` + HTTP 500/503

## 自動診断コマンド

```bash
# 1. FastAPI バックエンド稼働確認
curl -sf http://localhost:8000/api/health || echo "BACKEND_DOWN"

# 2. Supabase 接続確認
python3 -c "
from pathlib import Path
import os
env_file = Path.home() / '.hakudokai' / 'env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()
url = os.environ.get('SUPABASE_URL', '')
print(f'SUPABASE_URL={url[:30]}...' if url else 'SUPABASE_URL=MISSING')
"

# 3. 直近エラーログ確認
grep -c "ERR-EKARTE-001" /tmp/fastapi-server.log 2>/dev/null || echo "0"

# 4. ディスク容量
df -h / | tail -1 | awk '{print "DISK_USAGE=" $5}'
```

## 自動修復手順 (冪等、retry cap=3)

```bash
# Step 1: SQLite フォールバック有効化
mkdir -p ~/.openclaw
touch ~/.openclaw/use_local_sqlite_fallback
echo "$(date -Iseconds) fallback enabled by diagnose.sh" >> /tmp/runbook_actions.log

# Step 2: FastAPI 再起動 (プロセス存在時のみ)
if pgrep -f "uvicorn backend.main:app" > /dev/null; then
  pkill -f "uvicorn backend.main:app"
  sleep 2
  cd /mnt/c/Users/User/Documents/DentalBI
  nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi-server.log 2>&1 </dev/null &
  echo "$(date -Iseconds) FastAPI restarted" >> /tmp/runbook_actions.log
fi

# Step 3: 再接続確認
sleep 3
curl -sf http://localhost:8000/api/health && echo "RECOVERED" || echo "STILL_FAILING"
```

## 手動対応 (自動修復失敗時)

1. Supabase ステータス確認: https://status.supabase.com/
2. SecondPC からの疎通確認 (Tailscale 経由)
3. DentalBI 一時停止判断 (理事長殿へ報告)
4. ローカル SQLite に蓄積されたデータの手動同期

## エスカレーション基準

- 自動修復3回失敗 → 理事長 ntfy 即時通知
- 同じエラーが10分以内に5回再発 → CRITICAL 昇格
- 患者データ不整合の疑い → 即時エスカレーション (D1パターン禁止)
