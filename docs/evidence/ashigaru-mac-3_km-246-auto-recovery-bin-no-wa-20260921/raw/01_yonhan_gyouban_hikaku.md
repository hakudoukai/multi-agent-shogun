# ㋐ 四版の行番号比較（己の器で取り出した實測・當職の値を写さず）

対象ファイル: `scripts/inbox_watcher.sh`（disk/index/HEAD）と `scripts/inbox_watcher.origin778d2334.sh`（走る版のdiskコピー）
disk 上の走る版コピーの blob40 は origin/main 上の `scripts/inbox_watcher.sh` と完全一致（下表参照）。

## 版と blob40 の対応（`git hash-object` / `git ls-files -s` / `git rev-parse HEAD:<path>` / `git rev-parse origin/main:<path>` で實測）

| 版 | blob40 | 行数(`wc -l`) | 取得元 |
|---|---|---|---|
| disk(working) | `73cdfbc4a8dfd684b6ef21c3aad234d8ece335b8` | 1700 | `git hash-object scripts/inbox_watcher.sh` |
| index(staged) | `1d2821a3b4bdb0b265ada2d82df36f6bd5e2e3c8` | 1554 | `git ls-files -s scripts/inbox_watcher.sh` |
| HEAD | `00cd905d6eebd7d85b55ce1e0a1553697fc6cc9a` | 1607 | `git rev-parse HEAD:scripts/inbox_watcher.sh` |
| main(=origin/main=★走る版★) | `778d233445de00b0ac1df9b464dd135024046402` | 1728 | `git rev-parse origin/main:scripts/inbox_watcher.sh` = `git hash-object scripts/inbox_watcher.origin778d2334.sh`(disk上の走る版コピー) |

★行数は下命の宣した値(1700/1554/1607/1728)と當職の實測が悉く一致した。★

## `msg_auto_recovery_` 生成行（`enqueue_recovery_task_assigned` 内・python heredoc）

| 版 | Dedup guard 開始 | `[auto-recovery]` guard 判定行 | `id=` 生成行 | `type` 焼込行(辞書リテラル内) |
|---|---|---|---|---|
| disk 73cdfbc4 | L437 | L443 | L473 | L479 (`"type": "task_assigned"`) |
| index 1d2821a3 | L338 | L344 | L374 | L380 |
| HEAD 00cd905d | L391 | L397 | L427 | L433 |
| main 778d2334(★走る版★) | L338 | L344 | **L374** | L380 |

★命が引いた「L374」は index(1d2821a3) と main(778d2334=走る版) の★両方で一致★（偶然の一致・別コミットの同一パッチ）。
HEAD(00cd905d) は L427、disk(73cdfbc4) は L473 ―― ★同じ機構でも版により33〜99行ずれる★（disk が最も後方＝直近の追記が最も多い）。

## `send_context_reset` / `has_task_assigned` / `NEW_CONTEXT_SENT`（二度目の /clear を送る機構）

| 版 | `has_task_assigned`算出行 | `send_context_reset`定義行 | `[CONTEXT-RESET] Sending ... before task_assigned`ログ行 | 起動条件行(`has_task_assigned=1 && NEW_CONTEXT_SENT=0 && clear_seen=0`) |
|---|---|---|---|---|
| disk 73cdfbc4 | L613 | L795 | L825 | L1429 |
| index 1d2821a3 | L514 | L696 | L726 | L1283 |
| HEAD 00cd905d | L567 | L749 | L779 | L1336 |
| main 778d2334(★走る版★) | L518 | L848 | L878 | **L1457** |

★四版すべてに同一の機構が存在する（行番号は版でずれるが、コード構造・変数名・条件式は同型）。★
∴ 2026-08-10 CLAUDE.md「訂正」の逐語「`send_context_reset` は★死蔵の stub★・呼出 0 件」は
★走る版(main=778d2334)では★誤り★である。當職の器で `send_context_reset` の呼出箇所(main L1462)を實測した。
（CLAUDE.md の訂正が指した `scripts/inbox_watcher.sh` の★sha=691d8b8f★は本弾の四版のいずれとも不一致 ―― 別版を見て書かれた可能性が高いが、
★走る版が現に何を為すかは走る版のblobで判ずる★のが本則ゆゑ、走る版=main=778d2334 の實測を優先する）。
