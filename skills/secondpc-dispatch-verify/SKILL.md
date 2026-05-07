---
name: secondpc-dispatch-verify
description: SecondPC ashigaru5/6/7 へのタスク発令時、queue/tasks ファイル更新だけでなく inbox_write での cross_pc_bridge 配信を必ず行うことを検証する。MainPC 家老の発令漏れによる SecondPC 空回りを防止。
---

# SecondPC Dispatch Verify

## いつ使う (= mandatory)

家老が **SecondPC ashigaru5/6/7 にタスクを発令** する全ての場面。

## 必須手順

```bash
# Step 1: queue/tasks ファイル更新 (= 履歴記録)
# (拙者は既にこのstepを実行している前提)

# Step 2: inbox_write での配信 — これが抜けると SecondPC に届かない
TARGET="ashigaru5"  # or 6, 7
TASK_SUMMARY="<タスク内容、task_id 含む>"
bash scripts/inbox_write.sh "$TARGET" "$TASK_SUMMARY" task_assigned karo

# Step 3: 配信確認
bash scripts/checks/secondpc_dispatch.sh "$TARGET"
```

## 使わない

- MainPC ashigaru1/2 への発令 (= ローカル inotify で OK)
- gunshi/karo への発令 (= 同 PC)
- 単なるファイル更新 (= 配信を伴わない情報共有)

## 過去事例

- 2026-05-07 — 家老が MainPC 側 queue/tasks/ashigaru5/6/7.yaml を更新したが
  inbox_write を実行せず、SecondPC ashigaru が 4h 空回り、token 130-150k 蓄積
  詳細: 同日付の incident_log を参照
  教訓: **ファイル更新と配信は別工程**。queue/tasks 書込 ≠ 配信完了。
