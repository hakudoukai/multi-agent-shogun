#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# startup_shogun_main.sh — Shogun システム graceful startup (= 両 PC)
#
# 陛下御差配 (2026-05-10): Desktop アイコン → 本 script → 両 PC 順次起動。
# 「将軍出陣.bat」(= /mnt/c/Users/User/Desktop/) からダブルクリック起動。
#
# 順序 (= 上から):
#   1. coherence pre-check (= 既稼働なら shutdown 推奨 warning)
#   2. MainPC shutsujin_departure.sh (= 全 pane deploy + agent CLI 起動)
#   3. MainPC bridge process 起動 (= cross-PC 通信)
#   4. MainPC watcher_supervisor 起動 (= inbox_watcher 動的)
#   5. SSH SecondPC: 同様の startup 起動
#   6. coherence verify (両 PC 10/10 確認)
#
# Usage:
#   bash scripts/startup_shogun_main.sh
#   将軍出陣.bat (Windows Desktop) からダブルクリック (= wt + wsl 経由)
# ════════════════════════════════════════════════════════════════
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# 黒田 kl1 是正: SecondPC で実行された場合の自己再帰防止
# 既定 = local + remote 両 PC 起動、--local-only で remote skip
LOCAL_ONLY="no"
for arg in "$@"; do
    [ "$arg" = "--local-only" ] && LOCAL_ONLY="yes"
done

# hostname 検出で SecondPC 上での実行は自動 --local-only 化
case "$(hostname)" in
    *USER-O6AK*|USER-O6AK917NTU)
        LOCAL_ONLY="yes"
        echo "[auto-local-only] SecondPC 上での実行を検出、remote SSH 段階を skip (= kl1 自己再帰防止)"
        ;;
esac

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/startup_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "═══════════════════════════════════════════════════════════"
echo "  Shogun System Startup — $(date -Iseconds)"
echo "═══════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────
# Step 1: pre-check (既稼働 detect)
# ─────────────────────────────────────────────────────────────
echo ""
echo "═══ Step 1: pre-check ═══"
if tmux has-session -t multiagent 2>/dev/null; then
    echo "⚠ multiagent session 既稼働中"
    echo "  → 既存 tmux session を温存して startup する場合は coherence check のみ実行"
    echo "  → 全クリーン起動するなら先に scripts/shutdown_shogun.sh 実行推奨"
    echo ""
    read -r -p "既存 session 温存で coherence check のみ実行する? [y/N] " ans
    if [ "$ans" = "y" ]; then
        bash skills/shogun-system-coherence/scripts/coherence_check.sh
        echo "完遂、deploy はスキップ"
        exit 0
    fi
    echo "進行: 既存 session 上で shutsujin 再実行 (= deploy 重ね、agent 再起動可能性あり)"
fi

# ─────────────────────────────────────────────────────────────
# Step 2: MainPC shutsujin_departure.sh
# ─────────────────────────────────────────────────────────────
echo ""
echo "═══ Step 2: MainPC shutsujin_departure ═══"
if [ -x ./shutsujin_departure.sh ]; then
    bash ./shutsujin_departure.sh
else
    echo "ERR: shutsujin_departure.sh 不在 or 実行権限なし"
    exit 1
fi

# ─────────────────────────────────────────────────────────────
# Step 3: MainPC bridge process 起動
# ─────────────────────────────────────────────────────────────
echo ""
echo "═══ Step 3: MainPC bridge process 起動 ═══"
if pgrep -f hakudokai_realtime_bridge >/dev/null; then
    echo "  [skip] bridge 既稼働"
else
    if [ -f shim/hakudokai/hakudokai_realtime_bridge.py ]; then
        nohup python3 -u shim/hakudokai/hakudokai_realtime_bridge.py --poll-interval 3 \
            > /tmp/realtime_bridge.log 2>&1 &
        disown
        echo "  [started] bridge PID $!"
    else
        echo "  [skip] bridge script 不在"
    fi
fi

# ─────────────────────────────────────────────────────────────
# Step 4: MainPC watcher_supervisor
# ─────────────────────────────────────────────────────────────
echo ""
echo "═══ Step 4: MainPC watcher_supervisor 起動 ═══"
if pgrep -f scripts/watcher_supervisor.sh >/dev/null; then
    echo "  [skip] supervisor 既稼働"
else
    nohup bash scripts/watcher_supervisor.sh >> "$LOG_DIR/watcher_supervisor.log" 2>&1 &
    disown
    echo "  [started] supervisor PID $!"
fi

# ─────────────────────────────────────────────────────────────
# Step 5: SecondPC startup (= SSH + 同 script を --local-only で実行、kl1 是正)
# ─────────────────────────────────────────────────────────────
echo ""
echo "═══ Step 5: SecondPC startup ═══"
if [ "$LOCAL_ONLY" = "yes" ]; then
    echo "[skip] --local-only 指定、SecondPC 起動段階 skip"
elif ssh -o BatchMode=yes -o ConnectTimeout=5 -p 2222 User@192.168.11.47 'echo OK' 2>/dev/null | grep -q OK; then
    echo "[5a] SecondPC SSH 疎通 ✅"
    # SecondPC 側では --local-only 強制 (= 自己再帰防止)
    ssh -o BatchMode=yes -p 2222 User@192.168.11.47 \
        'wsl -- bash -lc "cd /home/hakudokai/projects/multi-agent-shogun-newbuild && bash scripts/startup_shogun_main.sh --local-only --no-confirm 2>&1 | tail -20"' 2>&1 | head -30
else
    echo "⚠ SecondPC SSH 不通、SecondPC 起動 skip (= 別途 SecondPC で手動起動要)"
fi

# ─────────────────────────────────────────────────────────────
# Step 6: coherence verify
# ─────────────────────────────────────────────────────────────
echo ""
echo "═══ Step 6: coherence verify ═══"
sleep 5
bash skills/shogun-system-coherence/scripts/coherence_check.sh 2>&1 | tail -15

echo ""
echo "═══ Startup 完遂 — $(date -Iseconds) ═══"
echo "log: $LOG_FILE"
