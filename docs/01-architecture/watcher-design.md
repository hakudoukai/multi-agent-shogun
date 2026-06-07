# Watcher Design Principles (理事長直接指示 — 2026-05-05 暴走事件後)

出典: CLAUDE.md (元「Watcher Design Principles」節) からの移設実体 (副院長令 7de922ec 裁定、2026-06-04 Commander)。改訂責務は理事長殿の専権事項。

過去事故: 2026-05-05 SecondPC 異常消費事件 (26分38%) — `fukuincho_reverse_watcher` の self-send retry 無限ループ + heartbeat 305件累積 + watchdog 自動再起動が連鎖し、API消費が暴走。詳細: [docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md](../incident_logs/2026-05-05_secondpc_consumption_anomaly.md)

## 必須原則 (全 watcher / poll / receiver 系)

1. **retry 無限ループ禁止**: 失敗メッセージは必ず以下のいずれかで終端:
   - **retry cap**: 最大 N 回 (推奨 3-5) で諦め、`acknowledged_at = NOW()` + `acknowledged_by = 'system'` + `context_data.close_reason = 'retry_exceeded'` で記録
   - **dead-letter キュー**: `dead_lettered_at` カラムへ移動、本キューから除外
   - **TTL**: 古いメッセージ (例: 24h以上) は自動 ack してスキップ
2. **self-send 即 ack**: from_pc = to_pc 検出時は即時 `acknowledged_at` を更新し再試行しない
3. **手動停止フラグ尊重**: `~/.openclaw/global_disable` 等のフラグがあれば watchdog は再起動しない
4. **重複検知 (dedupe)**: 同一 message_id 受信時は 2回目以降をスキップ
5. **idempotency**: cross-PC bridge 等で同じ操作を再送しても結果が同じになるよう設計
6. **専用テーブル分離**: heartbeat 等の高頻度メタメッセージは運用 inbox とは別テーブル (例: `pc_handshake_heartbeat`)

## 設計レビュー時のチェックリスト

新規 watcher / poll / receiver スクリプト作成時、以下を必ず確認:

- [ ] retry cap or TTL or dead-letter のいずれかが実装されているか
- [ ] self-send 検出時の即 ack ロジックがあるか
- [ ] 同一 message_id の重複処理を抑止するか
- [ ] outbound 失敗時 (例: ntfy 送信失敗) でもメッセージを ack で消失させていないか
- [ ] watchdog の自動再起動は手動停止フラグを尊重するか
- [ ] DB側に idempotency 制約 (UNIQUE 等) があるか
- [ ] 監査ログ (`acknowledged_by` + `context_data.close_reason`) に終端理由が記録されるか

これらを満たさない実装は本番投入禁止。三者監査 (Codex Axis 2バグ + Axis 6Git) でも必ずチェックする。
