# Runbook: ERR-EKARTE-001 (カルテ visit 作成失敗)

## 自動対応可能ステップ（shogun 実行）

1. **健康診断**: `curl /api/health` 確認
2. **DB接続確認**: `python3 -c "from backend.db.supabase_client import get_supabase_client; c=get_supabase_client(); print(c.table('visits').select('count').limit(1).execute())"`
3. **ローカルSQLiteフォールバック確認**: `sqlite3 dentalbi_local.db ".tables" | grep visits`
4. **直近ログ収集**: `tail -200 /tmp/fastapi-server.log | grep ERR-EKARTE-001`
5. **失敗パターンA (Supabase 503)** → SH3 fallback 自動有効化:
   ```bash
   touch ~/.openclaw/use_local_sqlite_fallback
   echo "fallback enabled at $(date)" >> /tmp/runbook_actions.log
   ```
6. **再試行**: 同一処理を1回再実行
7. **成功時**: error_log resolved=NOW(), notes="auto-recovered via SH3"
8. **失敗時**: 理事長 ntfy 緊急発火、本 runbook の手動対応セクションへ

## 手動対応（理事長介入が必要）

- Supabase ステータス確認: https://status.supabase.com/
- 別経路（SecondPC）からの確認
- 必要なら DentalBI 一時停止判断

## エスカレーション基準

- 自動対応3回失敗 → 理事長 ntfy
- 同じエラー連鎖（A→B→C）3つ以上 → 理事長 + 緊急会議
```

### 既知 runbook 一覧（初期セット作成必須）

家老が以下を順次作成：

| エラーコード | 内容 | 自動対応可能性 |
|------------|------|--------------|
| ERR-EKARTE-001 | visit 作成失敗 | 高（fallback切替） |
| ERR-WATCHER-001 | retry上限到達 | 中（dead-letter移動） |
| ERR-CARTE-001 | カルテット reconcile 失敗 | 低（手動確認必要） |
| ERR-INFRA-001 | unack 件数閾値超過 | 高（自動 ack スクリプト） |
| ERR-SUPABASE-001 | 接続タイムアウト | 高（retry + fallback） |
| ERR-PDF-001 | PDF 生成失敗 | 中（テンプレート不在検知） |
| ERR-AUTH-001 | 認証失敗連続 | 低（人間判断） |
| ERR-BILLING-001 | 算定ルール照合失敗 | 中（マスタ再ロード） |

### 信長の自動応答設定（Claude Code 制約への対処）

Claude Code は受動的（メッセージ受信時のみ応答）のため、以下の仕組みで「24時間自動応答」を実現：

1. **inbox_watcher が CRITICAL を検知**: tmux send-keys で shogun ペインに「critical_alert detected, run diagnose ERR-XXX-NNN」と nudge
2. **信長は受信即診断モード**: 通常作業中でも CRITICAL 受信時は最優先で対応
3. **理事長就寝中の対応**: 自動対応成功なら朝にサマリ報告、失敗なら ntfy で起こす（ただし夜間 22:00-7:00 は **CRITICAL のみ**通知、ERROR は朝まで保留）

### 夜間モード（理事長殿の睡眠保護）

- **22:00-7:00 (JST)**:
  - CRITICAL のみ ntfy 即時通知
  - ERROR / WARN は morning_digest として翌朝 7:30 にまとめて通知
  - 自動対応は通常通り継続、結果は朝報告
- **理事長フラグ**: `~/.openclaw/disable_night_mode` で無効化可

### 監査・改善ループ

- 毎週、自動対応成功率を集計（dashboard.md）
- 失敗パターンを runbook 改善に反映
- 自動対応で解決できなかったケースは新規 runbook 候補としてリスト化
- 月次で信長が runbook 全レビュー、理事長承認後反映

