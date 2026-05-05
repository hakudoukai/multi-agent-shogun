---
error_code: ERR-CARTE-001
severity: ERROR
title: "カルテデータ不整合 (reconcile 失敗)"
auto_fix: false
retry_cap: 0
escalation: "ntfy:director, inbox:shogun"
night_mode: defer_unless_critical
---

# Runbook: ERR-CARTE-001 (カルテデータ不整合)

## 症状 (検知パターン)

- カルテット (Quartetto) パーサーの reconcile 処理が失敗
- Supabase と ローカルデータの不一致検出
- visit レコードの重複・欠損
- PDF 出力時にデータ不整合エラー

## 自動診断コマンド

```bash
# 1. 直近のカルテ関連エラー
grep -c "ERR-CARTE" /tmp/fastapi-server.log 2>/dev/null || echo "0"

# 2. Supabase visits テーブル最新10件確認
python3 -c "
import os
from pathlib import Path
env_file = Path.home() / '.hakudokai' / 'env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()
print(f'SUPABASE_URL configured: {bool(os.environ.get(\"SUPABASE_URL\"))}')
"

# 3. ローカル SQLite 状態
sqlite3 /tmp/dentalbi_local.db "SELECT count(*) FROM visits;" 2>/dev/null || echo "LOCAL_DB_MISSING"

# 4. 差分検出 (ローカル vs リモート件数)
echo "MANUAL_CHECK_REQUIRED: データ不整合は自動判定困難"
```

## 自動修復手順

**自動修復なし (auto_fix: false)**

患者データの自動マージは D4 パターン (医療事故リスク) に該当するため禁止。
人間判断が必須。

## 手動対応 (必須)

1. **不整合の特定**: どのレコードが矛盾しているか correlation_id で追跡
2. **データ比較**: Supabase 側とローカル側の差分を CSV 出力して目視確認
3. **正データの判定**: 理事長殿が正しいデータを判定
4. **手動修正**: Supabase Studio or SQL で修正 (必ず修正前バックアップ)
5. **再 reconcile 実行**: 修正後に reconcile を手動で再実行
6. **確認**: PDF 出力して整合性確認

## エスカレーション基準

- 検知即座に理事長殿へ報告 (患者データは自動修復禁止)
- 影響患者数が5名以上 → 全システム一時停止検討
- 診療時間中の発生 → 紙カルテへの一時切替指示
