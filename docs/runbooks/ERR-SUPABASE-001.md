---
error_code: ERR-SUPABASE-001
severity: ERROR
title: "Supabase 接続タイムアウト/障害"
auto_fix: true
retry_cap: 3
escalation: "ntfy:director, inbox:shogun"
night_mode: defer_unless_critical
---

# Runbook: ERR-SUPABASE-001 (Supabase 接続障害)

## 症状 (検知パターン)

- Supabase API への接続がタイムアウト (>10秒)
- HTTP 503 Service Unavailable レスポンス
- PostgREST エラー (connection refused)
- watcher 系で Supabase 操作が連続失敗

## 自動診断コマンド

```bash
# 1. Supabase URL 疎通確認
SUPA_URL=$(grep "^SUPABASE_URL" ~/.hakudokai/env 2>/dev/null | cut -d= -f2 | tr -d '"\r ')
if [ -n "$SUPA_URL" ]; then
  HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 10 "${SUPA_URL}/rest/v1/" -H "apikey: anon" 2>/dev/null)
  echo "SUPABASE_HTTP=${HTTP_CODE:-TIMEOUT}"
else
  echo "SUPABASE_URL_NOT_CONFIGURED"
fi

# 2. DNS 解決確認
nslookup pxvnhkiqyxkejzivspde.supabase.co 2>/dev/null | grep -i "address" || echo "DNS_FAIL"

# 3. ネットワーク全般
ping -c 1 -W 3 8.8.8.8 > /dev/null 2>&1 && echo "INTERNET=OK" || echo "INTERNET=DOWN"

# 4. ローカル SQLite フォールバック状態
if [ -f ~/.openclaw/use_local_sqlite_fallback ]; then
  echo "FALLBACK=ACTIVE"
else
  echo "FALLBACK=INACTIVE"
fi

# 5. 直近の Supabase エラー件数
grep -c "ERR-SUPABASE" /tmp/fastapi-server.log 2>/dev/null || echo "0"
```

## 自動修復手順 (冪等、retry cap=3)

```bash
# Step 1: SQLite フォールバック有効化 (SH3パターン)
mkdir -p ~/.openclaw
touch ~/.openclaw/use_local_sqlite_fallback
echo "$(date -Iseconds) Supabase fallback activated" >> /tmp/runbook_actions.log

# Step 2: 接続再試行 (exponential backoff)
for i in 1 2 4; do
  sleep $i
  SUPA_URL=$(grep "^SUPABASE_URL" ~/.hakudokai/env 2>/dev/null | cut -d= -f2 | tr -d '"\r ')
  if [ -n "$SUPA_URL" ]; then
    HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 10 "${SUPA_URL}/rest/v1/" -H "apikey: anon" 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ]; then
      echo "SUPABASE_RECOVERED after ${i}s backoff"
      rm -f ~/.openclaw/use_local_sqlite_fallback
      echo "$(date -Iseconds) Supabase recovered, fallback deactivated" >> /tmp/runbook_actions.log
      break
    fi
  fi
done

# Step 3: 復旧確認
if [ -f ~/.openclaw/use_local_sqlite_fallback ]; then
  echo "STILL_FAILING: fallback remains active"
else
  echo "RECOVERED: normal operation resumed"
fi
```

## 手動対応 (自動修復失敗時)

1. Supabase ステータスページ確認: https://status.supabase.com/
2. Supabase Dashboard でプロジェクト状態確認
3. プロジェクトが paused なら restore: `supabase projects restore`
4. リージョン障害なら待機 (フォールバックで診療継続)
5. 復旧後: `rm ~/.openclaw/use_local_sqlite_fallback` + ローカルデータ同期

## エスカレーション基準

- 30分以上接続不能 → CRITICAL 昇格
- ローカル SQLite に未同期データ100件超 → ERROR (データロスリスク)
- Supabase ステータスページで障害報告あり → 待機 + 理事長殿に状況報告
