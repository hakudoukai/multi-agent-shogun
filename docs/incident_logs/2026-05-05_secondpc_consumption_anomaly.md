# Incident Log: SecondPC 異常消費事件

**日時**: 2026-05-05 17:30〜18:00 (JST)
**重大度**: P0 (容量制限25→38%/26分)
**作成**: 将軍（直接対応）

## 経緯
- SecondPC の Claude Max 使用量が「現在のセッション」枠で26分38%消費（通常の3-5倍）
- 理事長殿の指摘により調査開始

## 根本原因（3層）
1. **fukuincho_reverse_watcher.sh** の self-send retry 無限ループ
2. **heartbeat 305件累積** (受信側 ack なし)
3. **watchdog 自動再起動** が watcher 停止を妨害

## 連鎖被害
- pc_handshake テーブルへの大量INSERT
- SecondPC receiver_poll が拾って ashigaru8 inbox に書込（496行/45メッセージ/225箇所prefix繰返し）
- ashigaru8 が大量メッセージ処理で 52.3k tokens 思考 → API 大量消費

## 対処（実施済）
1. Supabase pc_handshake 一括 ack:
   - self-send: 11件
   - cross_pc_inbox 重複: 11件
   - heartbeat 累積: 295件
   - **合計 317件**
2. プロセス停止（理事長殿手動 kill）:
   - heartbeat (PID 32724)
   - watchdog × 2 (PID 32835, 41959)
   - fukuincho_reverse_watcher (PID 218208)
3. SecondPC receiver/inbox_watcher 停止 (pkill)
4. 過去2分の新規INSERT = 0件確認

## 一括ACKの実害評価（事後確認）
22件の内容を救出し精査した結果、**実害ゼロ**:
- self-send 11件: 昨日5/4のDesktop↔CLI構造改善相談、最終1件「SCOPE_CANCELLED_TODAY_ONLY」で取消済
- cross_pc_inbox 11件: 17:22 の重複バースト本体（内容重複、消去しても実害なし）

## デコポン (Codex) 監査結果
- A案 (self-send対応) の型エラー指摘: timestamp型修正
- B案 (heartbeat) の真因: 専用 `pc_handshake_heartbeat` テーブル migration 未適用
- 追加 P0: Poison message 隔離 (dead-letter queue)
- 他watcher の同型リスク: fukuincho_watcher / secondpc_watcher / task_sync / kuro_desktop_watcher / inbox_write.sh

## 設計欠陥（恒久対策必須）
1. retry 無限ループ防止: retry cap + dead-letter キュー
2. heartbeat 別経路 (pc_handshake_heartbeat migration適用)
3. watchdog の手動停止フラグ尊重
4. inbox dedupe 重複通知抑制
5. cross-PC bridge の DB側 idempotency

## 設計原則（恒久ルール化）
> 「永続的に retry されるメッセージは必ず TTL or retry cap or dead-letter キュー を持つこと」

## 救出済 ID 一覧（22件）
self-send (11件):
- fd7e442d, 2f29288a, 2b48492e, f7255f11, 4bcc824f, dc2acdd6, 1a9ac2a2, 45d20a59, 7eebe976, d9f34cef, 1896fc20

cross_pc_inbox (11件):
- 884897e1, b3d34d64, 6328ca7a, e7bab586, 1530ee77, 14a08e8c, d90f5359, d7df89de, 2f1c7d6d, af065f9b, c778ec8f

heartbeat 295件は省略（topic='heartbeat kouchan'で抽出可）

## 次のアクション
1. ✅ 影響ID救出 + 実害評価 (本ログ)
2. ⏳ ジェミちゃん追加監査 (法令観点)
3. ⏳ hotfix cmd 発令 (P0コード修正)
4. ⏳ 設計原則を CLAUDE.md / docs/audit-framework.md に追記
5. ⏳ docs/restart-and-mcp.md に段階的再起動手順追記
