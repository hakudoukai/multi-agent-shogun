#!/usr/bin/env bash
# secondpc_dispatch.sh — SecondPC への発令が cross_pc_bridge 配信まで完了したか検証
# 用途: 家老が SecondPC ashigaru5/6/7 に発令した直後の確認
# exit: 0=配信成功確認, 1=warning, 2=critical

set -uo pipefail

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
    echo "usage: secondpc_dispatch.sh <ashigaru5|ashigaru6|ashigaru7>" >&2
    exit 2
fi

case "$TARGET" in
    ashigaru5|ashigaru6|ashigaru7) ;;
    *)
        echo "[ERROR] $TARGET は SecondPC agent ではない" >&2
        exit 2
        ;;
esac

# MainPC 側 queue/tasks/<TARGET>.yaml が更新済みか
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TASK_FILE="$SCRIPT_DIR/queue/tasks/${TARGET}.yaml"
if [ ! -f "$TASK_FILE" ]; then
    echo "[WARN] $TASK_FILE が存在しない (= タスク未割当?)" >&2
    exit 1
fi
TASK_AGE=$(( $(date +%s) - $(stat -c %Y "$TASK_FILE") ))

# SecondPC 側 inbox 直近書込 mtime
SP_INBOX_AGE=$(ssh -o ConnectTimeout=5 -o BatchMode=yes hakudokai@192.168.11.47 \
    "stat -c %Y ~/projects/multi-agent-shogun/queue/inbox/${TARGET}.yaml 2>/dev/null" 2>/dev/null)
SP_INBOX_AGE=${SP_INBOX_AGE:-0}
SP_INBOX_AGE_DIFF=$(( $(date +%s) - SP_INBOX_AGE ))

echo "▼ $TARGET 配信検証"
echo "  MainPC task YAML 更新: ${TASK_AGE}s 前"
echo "  SecondPC inbox 最終書込: ${SP_INBOX_AGE_DIFF}s 前"

# 判定: SecondPC inbox が task YAML より古い → 配信されていない可能性
if [ "$SP_INBOX_AGE_DIFF" -gt "$TASK_AGE" ]; then
    diff_min=$(( (SP_INBOX_AGE_DIFF - TASK_AGE) / 60 ))
    echo "  ❌ SecondPC inbox は task YAML より ${diff_min} 分古い → 配信未完了の可能性" >&2
    echo "     対処: bash scripts/inbox_write.sh $TARGET '<task content>' task_assigned karo" >&2
    exit 2
fi

# task YAML 更新後、5 分以内に SecondPC inbox に書込があれば配信成功
if [ "$TASK_AGE" -lt 300 ] && [ "$SP_INBOX_AGE_DIFF" -lt "$TASK_AGE" ]; then
    echo "  ✅ task 更新後に SecondPC inbox 書込確認、配信成功"
    exit 0
fi

echo "  ⚪ 古い task のため判定不能 (= 過去の配信を検証中、現状問題なし)"
exit 0
