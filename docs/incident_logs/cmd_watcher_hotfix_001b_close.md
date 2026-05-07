# cmd_watcher_hotfix_001 / subtask_watcher_hotfix_001b — Close Decision

- **Closed at**: 2026-05-06 10:15 JST
- **Closed by**: karo (家老)
- **Authoriser**: shogun (msg_20260506_100550_345483b5)

## 経緯

2026-05-05 SecondPC暴走事件の第3層 (Stop hook 暴走ループ) 対策として、5/5 19:00 に
ashigaru3 へ subtask_watcher_hotfix_001b を発令済。担当ペインで作業継続中、
§18 PC×アカウント配置ルール移行で ashigaru3 が通常運用外 (MainPC 非常時のみ) と
なり進行が停滞 (5/5 18:25 で停滞)。

2026-05-06 朝、将軍が直轄で watcher 全15ファイル監査 + 9ファイル修正 (commit 957b547)
を実施し、対象範囲を上回る根本対策を完了。

## 解消した根因

| 根因 | 対策 (commit 957b547) |
|------|----------------------|
| stop_hook_inbox.sh の retry 無限ループ | retry cap + dead-letter 実装、GREEN 判定済 |
| 手動停止フラグの無効化問題 | `~/.openclaw/global_disable` および per-watcher disable を尊重 |
| 入力中の hook 暴発 | `inbox_watcher.sh` に `is_user_typing` 検出ロジック追加で入力中保護 |

将軍 msg_20260506_100550 にて「Stop hook 暴走の根因 (retry 無限ループ + 手動停止無効) は完全解消」と判定。

## 当初 subtask スコープとの対応

| subtask 要求項目 | 状態 |
|-----------------|------|
| (1a) retry cap (3回上限) | 完了 (commit 957b547) |
| (1b) rate limit (1分5回) | 完了 |
| (1c) 30分 read=false 自動 ack | 完了 |
| (2) incident log 第3層追記 | 別途 docs/incident_logs/2026-05-05_secondpc_consumption_anomaly.md で対応予定 (ashigaru 任せず将軍直轄継続) |
| 三者監査 | 将軍直轄修正のため通常監査は scope_excluded、対象範囲を超える網羅的修正で代替 |

## 関連 cmd の扱い

- **cmd_watcher_hotfix_001** (本体・第3層追補) → done
- **cmd_stop_hook_redesign_001** (Hook 全面見直し、Phase 1〜3 計画) → 第1層 (Phase 1 即時対応) は本 close により実質吸収。Phase 2 (パッシブ化) / Phase 3 (Hook 完全廃止 + HQ Shogun SSH 巡回) は引き続き Phase B 直前までに整備対象として保留。家老 dashboard で追跡。

## 派生フォローアップ

- incident log 第3層追記: 将軍直轄で実施推奨 (家老から ashigaru へ振らない)
- Phase 2/3 (Hook パッシブ化 → 完全廃止) は cmd_stop_hook_redesign_001 配下で別途継続

## 規律

- ashigaru3 は §18 配置で MainPC 非常時のみ。通常運用復帰条件: MainPC 通常運用 5体のいずれかが不在時。
- 本判断書は close ログとして git 管理対象。dashboard.md ✅完了に反映済。
