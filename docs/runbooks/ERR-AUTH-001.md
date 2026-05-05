---
error_code: ERR-AUTH-001
severity: WARN
title: "認証失敗 (連続)"
auto_fix: false
retry_cap: 0
escalation: "inbox:shogun"
night_mode: defer
---

# Runbook: ERR-AUTH-001 (認証失敗)

## 症状 (検知パターン)

- Supabase Auth でのログイン連続失敗 (3回+)
- JWT トークン期限切れによる API 拒否
- セッション無効化 (リフレッシュトークン失敗)
- AuthGuard でブロックされるリクエスト増加

## 自動診断コマンド

```bash
# 1. Supabase Auth エンドポイント確認
SUPA_URL=$(grep "^SUPABASE_URL" ~/.hakudokai/env 2>/dev/null | cut -d= -f2 | tr -d '"\r ')
if [ -n "$SUPA_URL" ]; then
  HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 5 "${SUPA_URL}/auth/v1/health" 2>/dev/null)
  echo "AUTH_HEALTH=${HTTP_CODE:-TIMEOUT}"
else
  echo "SUPABASE_URL_NOT_CONFIGURED"
fi

# 2. 直近の認証エラーログ
grep -i "auth\|401\|403" /tmp/fastapi-server.log 2>/dev/null | tail -5

# 3. ローカル環境 (localhost はAuthGuard スキップ)
echo "NOTE: localhost/192.168.x.x は AuthGuard スキップ設定済み"

# 4. API キー有効性
SUPA_KEY=$(grep "^SUPABASE_SERVICE_ROLE_KEY" ~/.hakudokai/env 2>/dev/null | cut -d= -f2 | tr -d '"\r ')
if [ -n "$SUPA_KEY" ]; then
  echo "SERVICE_ROLE_KEY=CONFIGURED (length=${#SUPA_KEY})"
else
  echo "SERVICE_ROLE_KEY=MISSING"
fi
```

## 自動修復手順

**自動修復なし (auto_fix: false)**

認証失敗の自動復旧は D3 パターン (自動権限昇格) に該当するリスクがあるため、
人間判断必須。

## 手動対応 (必須)

1. **正常なアクセスか確認**: 不正アクセス試行の可能性を排除
2. **Supabase Dashboard で Auth 設定確認**: JWT secret の有効期限
3. **API キー確認**: service_role_key の有効性 (Supabase Dashboard → Settings → API)
4. **クライアント側**: ブラウザの localStorage/sessionStorage クリア
5. **トークンリフレッシュ**: フロントエンドの supabase.auth.refreshSession() 実行

## エスカレーション基準

- 同一 IP から10回連続失敗 → 不正アクセスの疑い → CRITICAL 昇格
- service_role_key 無効 → CRITICAL (全 API 停止)
- Auth サービス自体が down → ERR-SUPABASE-001 へ移行
