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
    if tmux has-session -t shogun 2>/dev/null; then
        echo "  [exists] shogun session 既存"
        local pane_state
        pane_state=$(tmux capture-pane -t shogun:main.0 -p 2>&1 | tail -3)
        echo "  pane 末尾 3 行:"
        echo "$pane_state" | sed 's/^/    /'
        echo "  → attach 経路は: tmux attach -t shogun"
    else
        echo "  [missing] shogun session 不在 — 復元中"
        tmux new-session -d -s shogun -n main
        tmux set-option -t shogun:main -p @agent_id "shogun"
        tmux set-option -t shogun:main -p @agent_cli "claude"
        # claude 起動
        tmux send-keys -t shogun:main "cd $REPO_ROOT && claude --model opus --effort max" Enter
        echo "  [created] shogun session、claude 起動投入"
        sleep 3
        echo "  pane 確認:"
        tmux capture-pane -t shogun:main.0 -p 2>&1 | tail -5 | sed 's/^/    /'
    fi
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
    if ssh -o BatchMode=yes -p 2222 User@192.168.11.47 'wsl -- bash -lc "tmux has-session -t shogun"' 2>&1 | grep -q "0$\|^$"; then
        echo "  [exists] SecondPC shogun session 既存"
    else
        echo "  [missing] SecondPC shogun session 不在 — 復元中"
        ssh -o BatchMode=yes -p 2222 User@192.168.11.47 \
            'wsl -- bash -lc "tmux new-session -d -s shogun -n main && tmux set-option -t shogun:main -p @agent_id shogun && tmux set-option -t shogun:main -p @agent_cli claude"' 2>&1
        ssh -o BatchMode=yes -p 2222 User@192.168.11.47 \
            'wsl -- bash -lc "tmux send-keys -t shogun:main \"cd /home/hakudokai/projects/multi-agent-shogun-newbuild && claude --model opus --effort max\" Enter"' 2>&1
        echo "  [created] SecondPC shogun + claude 起動"
    fi
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
# 実行
# ─────────────────────────────────────────────────────────────
[ "$SCOPE" = "main" ] || [ "$SCOPE" = "both" ] && recover_main
[ "$SCOPE" = "second" ] || [ "$SCOPE" = "both" ] && recover_second
verify_coherence

echo ""
echo "═══ Recovery 完遂 — $(date -Iseconds) ═══"
echo "log: $LOG_FILE"
echo ""
echo "→ 信長 attach: tmux attach -t shogun"
echo "→ 家康 attach: ssh -p 2222 User@192.168.11.47 'wsl -- tmux attach -t shogun'"
