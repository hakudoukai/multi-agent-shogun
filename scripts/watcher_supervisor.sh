#!/usr/bin/env bash
set -euo pipefail

# Keep inbox watchers alive in a persistent tmux-hosted shell.
# This script is designed to run forever.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs queue/inbox

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

    ensure_inbox_file "$agent"
    if ! pane_exists "$pane"; then
        return 0
    fi

    if pgrep -f "scripts/inbox_watcher.sh ${agent} " >/dev/null 2>&1; then
        return 0
    fi

    cli=$(tmux show-options -p -t "$pane" -v @agent_cli 2>/dev/null || echo "codex")
    nohup bash scripts/inbox_watcher.sh "$agent" "$pane" "$cli" >> "$log_file" 2>&1 &
}

start_report_watcher_if_missing() {
    local log_file="$1"
    if pgrep -f "scripts/redundancy/shogun_report_watcher.sh" >/dev/null 2>&1; then
        return 0
    fi
    nohup bash scripts/redundancy/shogun_report_watcher.sh >> "$log_file" 2>&1 &
}

# ════════════════════════════════════════════════════════════════
# Dynamic agent enumeration (= refactor 2026-05-10、上流 H-3 残課題の解)
# config/settings.yaml の cli.agents から動的読込、編成変更時の再起動忘れ根絶
# 慣例: shogun → shogun:main.0、他は出現順で multiagent:agents.{idx} (idx=0..)
# ════════════════════════════════════════════════════════════════
read_agents_from_settings() {
    awk '/^  agents:/{f=1;next} f&&/^  [^ ]/{exit} f&&/^[ ]{4}[A-Za-z0-9_]+:/{
        sub(/^[ ]*/,""); sub(/:.*/,""); print
    }' config/settings.yaml
}

while true; do
    idx=0
    while read -r agent; do
        [ -z "$agent" ] && continue
        if [ "$agent" = "shogun" ]; then
            pane="shogun:main.0"
        else
            pane="multiagent:agents.${idx}"
            idx=$((idx+1))
        fi
        start_watcher_if_missing "$agent" "$pane" "logs/inbox_watcher_${agent}.log"
    done < <(read_agents_from_settings)
    start_report_watcher_if_missing "logs/shogun_report_watcher.log"
    sleep 5
done
