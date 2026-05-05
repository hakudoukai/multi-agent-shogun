---
error_code: ERR-BILLING-001
severity: ERROR
title: "会計処理エラー (算定ルール照合失敗)"
auto_fix: true
retry_cap: 3
escalation: "ntfy:director, inbox:shogun"
night_mode: defer_unless_critical
---

# Runbook: ERR-BILLING-001 (会計処理エラー)

## 症状 (検知パターン)

- 算定ルール (14区分マッピング) の照合失敗
- 点数計算で不正値 (負の値、上限超過)
- 日計表の集計不一致
- 負担金徴収額の計算エラー

## 自動診断コマンド

```bash
# 1. バックエンド稼働確認
curl -sf http://localhost:8000/api/health || echo "BACKEND_DOWN"

# 2. 算定マスタデータ確認
DENTALBI="/mnt/c/Users/User/Documents/DentalBI"
if [ -d "${DENTALBI}/backend" ]; then
  find "${DENTALBI}/backend" -name "*billing*" -o -name "*14区分*" -o -name "*mapping*" 2>/dev/null | head -5
  echo "BILLING_FILES_FOUND"
else
  echo "DENTALBI_BACKEND_MISSING"
fi

# 3. 直近のエラー
grep -c "ERR-BILLING" /tmp/fastapi-server.log 2>/dev/null || echo "0"

# 4. Supabase billing テーブル確認
echo "CHECK: Supabase daily_reports / billing_items テーブル状態"
```

## 自動修復手順 (冪等、retry cap=3)

```bash
# Step 1: マスタデータ再読み込み
cd /mnt/c/Users/User/Documents/DentalBI
python3 -c "
try:
    # マスタキャッシュクリア (実装依存)
    import importlib, sys
    modules_to_reload = [m for m in sys.modules if 'billing' in m or 'mapping' in m]
    for m in modules_to_reload:
        del sys.modules[m]
    print(f'CACHE_CLEARED: {len(modules_to_reload)} modules')
except Exception as e:
    print(f'CACHE_CLEAR_SKIP: {e}')
"
echo "$(date -Iseconds) billing master reload attempted" >> /tmp/runbook_actions.log

# Step 2: FastAPI 再起動 (マスタ再読込のため)
if pgrep -f "uvicorn backend.main:app" > /dev/null; then
  pkill -f "uvicorn backend.main:app"
  sleep 2
  cd /mnt/c/Users/User/Documents/DentalBI
  nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi-server.log 2>&1 </dev/null &
  echo "$(date -Iseconds) FastAPI restarted for billing master reload" >> /tmp/runbook_actions.log
fi

# Step 3: 再計算テスト
sleep 3
curl -sf http://localhost:8000/api/health && echo "BACKEND_UP" || echo "BACKEND_STILL_DOWN"
```

## 手動対応 (自動修復失敗時)

1. 14区分マッピングテーブル (DD-044) の整合性確認
2. 該当患者の算定データを手動再計算
3. 日計表の手動修正 (差分修正、全件再計算は禁止)
4. 理事長殿に影響範囲報告 (金額影響あり → 優先対応)

## エスカレーション基準

- 金額計算エラー → ERROR (患者請求に直結)
- 同一算定ルールで複数患者に影響 → CRITICAL 昇格
- 日計表が当日中に確定できない → 理事長殿へ即報告
- D5 パターン注意: 課金処理の自動再試行は二重課金リスクあり (同一トランザクション再試行禁止)
