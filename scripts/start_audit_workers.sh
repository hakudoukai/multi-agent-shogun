#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# start_audit_workers.sh — audit_queue_worker daemon を恒常起動
#
# 陛下御差配 (2026-05-10): 「worker daemon の永続化を恒常化」
# 動作: hostname 自動検出で main_pc / second_pc を判別、
#       既存 worker 不在時のみ setsid + nohup で永続起動。
#       SSH 切断 / SIGHUP 耐性、orphan 化しても codex/gemini 完遂。
#
# 統合先:
#   - shutsujin_departure.sh の startup chain に call (= 出陣時 auto)
#   - scripts/recover_shogun.sh の recover_supporting_daemons() で call
#   - cron @reboot or systemd unit (= OS 再起動 auto)
# ════════════════════════════════════════════════════════════════
set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# hostname 自動検出
case "$(hostname)" in
    *USER-0T4SR8*|USER-0T4SR8MIQA) MY_PC='main_pc' ;;
    *USER-O6AK*|USER-O6AK917NTU)   MY_PC='second_pc' ;;
    *) MY_PC='main_pc' ;;  # default
esac

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/audit_queue_worker_${MY_PC}.log"

# 既存 worker 確認 (= 同 PC 用 daemon が稼働中なら何もしない)
if pgrep -fa "audit_queue_worker.sh ${MY_PC}\b" >/dev/null 2>&1; then
    echo "[start_audit_workers] worker 既稼働 (${MY_PC})、起動 skip"
    pgrep -fa "audit_queue_worker.sh ${MY_PC}\b" | head -3
    exit 0
fi

# 永続起動 (= SSH 切断耐性)
echo "[start_audit_workers] 起動 ${MY_PC}"
nohup setsid bash "$REPO_ROOT/scripts/audit_queue_worker.sh" "$MY_PC" \
    < /dev/null >> "$LOG_FILE" 2>&1 &
PID=$!
disown
sleep 2

# 起動 verify
if ps -p "$PID" >/dev/null 2>&1; then
    echo "[start_audit_workers] ✅ 起動成功 PID=$PID my_pc=${MY_PC}"
else
    echo "[start_audit_workers] ❌ 起動失敗、log: $LOG_FILE"
    exit 1
fi
