#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# recover_shogun.sh — 信長/家康 (shogun pane) 蘇生
#
# 陛下御差配 (2026-05-10): MainPC 信長 or SecondPC 家康 が消えると操作不能。
# Desktop アイコン「将軍復活.bat」からダブルクリック → 本 script で蘇生。
#
# 検出 + 対処:
#   - shogun:main session 不在 → tmux new-session で復元 + claude 起動
#   - shogun:main あるが pane idle (= 古い prompt) → 状況保持で attach のみ
#   - SecondPC 同様 (= SSH 経由)
#   - coherence verify で復活確認
#
# Usage:
#   bash scripts/recover_shogun.sh           # 自動 detect + 復活
#   bash scripts/recover_shogun.sh --main    # MainPC のみ復活
#   bash scripts/recover_shogun.sh --second  # SecondPC のみ復活
# ════════════════════════════════════════════════════════════════
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

MODE="${1:-auto}"
case "$MODE" in
    --main)   SCOPE='main' ;;
    --second) SCOPE='second' ;;
    *)        SCOPE='both' ;;
esac

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/recover_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "═══════════════════════════════════════════════════════════"
echo "  Shogun Recovery — $(date -Iseconds) scope=$SCOPE"
echo "═══════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────
# MainPC 信長復活 (= shogun:main session)
# ─────────────────────────────────────────────────────────────
recover_main() {
    echo ""
    echo "═══ MainPC 信長復活 ═══"
    # 黒田 kl2 是正: tmux has-session の exit code で判定 (= grep 出力依存しない)
    if tmux has-session -t shogun 2>/dev/null; then
        echo "  [exists] shogun session 既存 (= exit code 0、pane 上書きせず)"
        local pane_state
        pane_state=$(tmux capture-pane -t shogun -p 2>&1 | tail -3 || echo '(capture 不能)')
        echo "  pane 末尾 3 行:"
        echo "$pane_state" | sed 's/^/    /'
        echo "  → attach 経路は: tmux attach -t shogun"
    else
        echo "  [missing] shogun session 不在 (= exit code != 0) — 復元中"
        tmux new-session -d -s shogun -n main
        tmux set-option -t shogun:main -p @agent_id "shogun"
        tmux set-option -t shogun:main -p @agent_cli "claude"
        tmux send-keys -t shogun:main "cd $REPO_ROOT && claude --model opus --effort max" Enter
        echo "  [created] shogun session、claude 起動投入"
        sleep 3
        echo "  pane 確認:"
        tmux capture-pane -t shogun:main -p 2>&1 | tail -5 | sed 's/^/    /'
    fi
}

# ─────────────────────────────────────────────────────────────
# 監視系 (supervisor + bridge + watcher) 蘇生 (= 黒田 kl4 是正)
# 信長 pane だけ起こしても伝令断絶残るゆえ、補助 daemon も保証
# ─────────────────────────────────────────────────────────────
recover_supporting_daemons() {
    echo ""
    echo "═══ 監視系 (supervisor + bridge + watcher) 蘇生 ═══"
    local fail=0

    # bridge process
    if pgrep -f hakudokai_realtime_bridge >/dev/null; then
        echo "  [running] bridge process 稼働中"
    else
        if [ -f shim/hakudokai/hakudokai_realtime_bridge.py ]; then
            nohup python3 -u shim/hakudokai/hakudokai_realtime_bridge.py --poll-interval 3 \
                > /tmp/realtime_bridge.log 2>&1 &
            disown
            echo "  [started] bridge PID $!"
        else
            echo "  [skip] bridge script 不在"
            fail=$((fail+1))
        fi
    fi

    # watcher_supervisor
    if pgrep -f scripts/watcher_supervisor.sh >/dev/null; then
        echo "  [running] watcher_supervisor 稼働中"
    else
        nohup bash scripts/watcher_supervisor.sh >> "$LOG_DIR/watcher_supervisor.log" 2>&1 &
        disown
        echo "  [started] supervisor PID $!"
        sleep 5  # supervisor が child watchers を spawn する待ち
    fi

    # 個別 watcher 全数 (= supervisor 経由で起動済 のはず、不足なら fail)
    local expected_watchers=10
    local actual_watchers
    actual_watchers=$(pgrep -fc "scripts/inbox_watcher.sh")
    if [ "$actual_watchers" -ge "$expected_watchers" ]; then
        echo "  [ok] inbox_watcher $actual_watchers 件 (期待 $expected_watchers)"
    else
        echo "  [warn] inbox_watcher $actual_watchers 件、期待 $expected_watchers 未満"
        fail=$((fail+1))
    fi

    return $fail
}

# ─────────────────────────────────────────────────────────────
# SecondPC 家康復活 (= SSH 経由)
# ─────────────────────────────────────────────────────────────
recover_second() {
    echo ""
    echo "═══ SecondPC 家康復活 ═══"
    if ! ssh -o BatchMode=yes -o ConnectTimeout=5 -p 2222 User@192.168.11.47 'echo OK' 2>/dev/null | grep -q OK; then
        echo "  ⚠ SecondPC SSH 不通、家康復活 skip"
        return 1
    fi
    # 黒田 kl2 是正: ssh で remote tmux has-session の exit code を直接受け取る
    if ssh -o BatchMode=yes -p 2222 User@192.168.11.47 'wsl -- bash -lc "tmux has-session -t shogun"' 2>/dev/null; then
        echo "  [exists] SecondPC shogun session 既存 (= exit code 0)"
    else
        echo "  [missing] SecondPC shogun session 不在 — 復元中"
        ssh -o BatchMode=yes -p 2222 User@192.168.11.47 \
            'wsl -- bash -lc "tmux new-session -d -s shogun -n main && tmux set-option -t shogun:main -p @agent_id shogun && tmux set-option -t shogun:main -p @agent_cli claude"' 2>&1
        ssh -o BatchMode=yes -p 2222 User@192.168.11.47 \
            'wsl -- bash -lc "tmux send-keys -t shogun:main \"cd /home/hakudokai/projects/multi-agent-shogun-newbuild && claude --model opus --effort max\" Enter"' 2>&1
        echo "  [created] SecondPC shogun + claude 起動"
    fi

    # 黒田 kl4 是正: SecondPC の bridge + supervisor も蘇生
    ssh -o BatchMode=yes -p 2222 User@192.168.11.47 'wsl -- bash -lc "cd /home/hakudokai/projects/multi-agent-shogun-newbuild && pgrep -f hakudokai_realtime_bridge >/dev/null || nohup python3 -u shim/hakudokai/hakudokai_realtime_bridge.py --poll-interval 3 > /tmp/realtime_bridge.log 2>&1 & pgrep -f scripts/watcher_supervisor.sh >/dev/null || nohup bash scripts/watcher_supervisor.sh >> logs/watcher_supervisor.log 2>&1 &"' 2>&1
    echo "  [supporting] SecondPC bridge + supervisor 起動 verify 投下"
}

# ─────────────────────────────────────────────────────────────
# coherence verify
# ─────────────────────────────────────────────────────────────
verify_coherence() {
    echo ""
    echo "═══ coherence verify ═══"
    bash skills/shogun-system-coherence/scripts/coherence_check.sh 2>&1 | tail -5
}

# ─────────────────────────────────────────────────────────────
# 実行 (= 黒田 kl4 是正、監視系 + 失敗時 非0 終了)
# ─────────────────────────────────────────────────────────────
RECOVERY_FAIL=0
[ "$SCOPE" = "main" ] || [ "$SCOPE" = "both" ] && recover_main
[ "$SCOPE" = "main" ] || [ "$SCOPE" = "both" ] && recover_supporting_daemons || RECOVERY_FAIL=$((RECOVERY_FAIL+1))
[ "$SCOPE" = "second" ] || [ "$SCOPE" = "both" ] && recover_second
verify_coherence

echo ""
if [ "$RECOVERY_FAIL" -eq 0 ]; then
    echo "═══ Recovery 完遂 (= 全 ✅) — $(date -Iseconds) ═══"
else
    echo "═══ Recovery 完了 (= 警告 $RECOVERY_FAIL 件、要確認) — $(date -Iseconds) ═══"
fi
echo "log: $LOG_FILE"
echo ""
echo "→ 信長 attach: tmux attach -t shogun"
echo "→ 家康 attach: ssh -p 2222 User@192.168.11.47 'wsl -- tmux attach -t shogun'"

exit $RECOVERY_FAIL
