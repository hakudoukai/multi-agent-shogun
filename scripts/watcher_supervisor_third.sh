#!/usr/bin/env bash
set -euo pipefail

# Keep inbox watchers alive for third_pc agents.
# 配置 (third_pc — Phase 2 拡張、CLAUDE.md §18 未反映):
#   tmux session: multiagent-third
#     pane 0 = karo-third
#     pane 1-7 = ashigaru-third-1..7
#     pane 8 = gunshi-third
# Disable flags 尊重 (= ~/.openclaw/disable_inbox_watcher_<agent>):
#   2026-05-29 codex auth revoked により pane 6 + 8 は disable 中

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs queue/inbox

GLOBAL_DISABLE="$HOME/.openclaw/global_disable"
SUPERVISOR_DISABLE="$HOME/.openclaw/disable_watcher_supervisor_third"

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

# Resolve a pane by its @agent_id rather than a static pane index.
# Fixes off-by-one misroute after pane reshuffle (e.g. one pane removed
# shifts all higher indices). Watcher Design 6 原則 = 動的アドレッシング順守。
# Returns the fully-qualified pane target on stdout, or empty if no pane
# currently carries that @agent_id (e.g. agent retired or pane dead).
# 真因事例: 2026-06-05 ashigaru-third-2 pane 消滅 → -3..-7 + gunshi-third
# が 6 watcher misrouted、wake-up 不達 + 隣 pane 誤着弾。gunshi-third 診断
# msg_20260605_172549_27c4acfb で確認。
resolve_agent_pane() {
    local agent="$1"
    tmux list-panes -t multiagent-third:agents \
        -F '#{pane_index}:#{@agent_id}' 2>/dev/null \
        | awk -F: -v a="$agent" '$2==a {print "multiagent-third:agents."$1; exit}'
}

start_watcher_if_missing() {
    local agent="$1"
    local pane="$2"
    local log_file="$3"
    local cli

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
    setsid nohup bash scripts/inbox_watcher.sh "$agent" "$pane" "$cli" >> "$log_file" 2>&1 < /dev/null &
}

while true; do
    if [ -f "$GLOBAL_DISABLE" ] || [ -f "$SUPERVISOR_DISABLE" ]; then
        sleep 30
        continue
    fi

    for n in 1 2 3 4 5 6 7; do
        pane=$(resolve_agent_pane "ashigaru-third-${n}")
        [ -n "$pane" ] || continue
        start_watcher_if_missing "ashigaru-third-${n}" "$pane" "logs/inbox_watcher_ashigaru-third-${n}.log"
    done
    pane=$(resolve_agent_pane "gunshi-third")
    if [ -n "$pane" ]; then
        start_watcher_if_missing "gunshi-third" "$pane" "logs/inbox_watcher_gunshi-third.log"
    fi

    sleep 10
done
