#!/usr/bin/env bash
set -euo pipefail

# Keep inbox watchers alive in a persistent tmux-hosted shell.
# This script is designed to run forever.
#
# 配置 (CLAUDE.md §18 PC × アカウント × エージェント配置ルール 準拠):
#   MainPC (sasebo@sasebo.or.jp / Claude Max 20x)
#     通常 5体: 信長 + 家老 + 家康 + 足軽1 + 足軽2
#     非常時 +1: 足軽3 (本 supervisor は通常 5体のみ管理、足軽3 は手動起動)
#   足軽4: 欠番 (PC 境界の視覚的区切り)
#   SecondPC: 足軽5/6/7/8 (本 supervisor 管理外、SecondPC 側で別 supervisor 起動)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs queue/inbox

# Manual disable flags (Watcher Design Principles 必須項目)
GLOBAL_DISABLE="$HOME/.openclaw/global_disable"
SUPERVISOR_DISABLE="$HOME/.openclaw/disable_watcher_supervisor"

ensure_inbox_file() {
    local agent="$1"
    if [ ! -f "queue/inbox/${agent}.yaml" ]; then
        printf 'messages: []\n' > "queue/inbox/${agent}.yaml"
    fi
}

pane_exists() {
    local pane="$1"
    tmux list-panes -a -F "#{session_name}:#{window_name}.#{pane_index}" 2>/dev/null | grep -qx "$pane"
}

start_watcher_if_missing() {
    local agent="$1"
    local pane="$2"
    local log_file="$3"
    local cli

    # Per-agent disable flag (ex: ~/.openclaw/disable_inbox_watcher_shogun)
    # supervisor が watcher を再起動しないようにする (= disable flag 永続尊重)
    if [ -f "$HOME/.openclaw/disable_inbox_watcher_${agent}" ]; then
        return 0
    fi

    ensure_inbox_file "$agent"
    if ! pane_exists "$pane"; then
        return 0
    fi

    if pgrep -f "scripts/inbox_watcher.sh ${agent} " >/dev/null 2>&1; then
        return 0
    fi

    cli=$(tmux show-options -p -t "$pane" -v @agent_cli 2>/dev/null || echo "claude")
    nohup bash scripts/inbox_watcher.sh "$agent" "$pane" "$cli" >> "$log_file" 2>&1 &
}

while true; do
    # Manual disable flag check (Watcher Design Principles 必須項目)
    if [ -f "$GLOBAL_DISABLE" ] || [ -f "$SUPERVISOR_DISABLE" ]; then
        echo "[$(date)] watcher_supervisor DISABLED by flag file — exiting" >&2
        exit 0
    fi

    # MainPC 通常運用 5体 (CLAUDE.md §18.1)
    start_watcher_if_missing "shogun"    "shogun:main.0"        "logs/inbox_watcher_shogun.log"
    start_watcher_if_missing "karo"      "multiagent:agents.0"  "logs/inbox_watcher_karo.log"
    start_watcher_if_missing "ashigaru1" "multiagent:agents.1"  "logs/inbox_watcher_ashigaru1.log"
    start_watcher_if_missing "ashigaru2" "multiagent:agents.2"  "logs/inbox_watcher_ashigaru2.log"
    start_watcher_if_missing "gunshi"    "multiagent:agents.3"  "logs/inbox_watcher_gunshi.log"
    # 非常時 ashigaru3 を起動するなら、~/.openclaw/enable_ashigaru3 を touch 後に
    # 以下行を一時的に有効化する (本 supervisor は通常時は ashigaru3 を起動しない):
    # if [ -f "$HOME/.openclaw/enable_ashigaru3" ] && pane_exists "multiagent:agents.4"; then
    #     start_watcher_if_missing "ashigaru3" "multiagent:agents.4" "logs/inbox_watcher_ashigaru3.log"
    # fi
    sleep 5
done
