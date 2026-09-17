#!/bin/bash
# 写し器 55 ―― 口 scripts/inbox_watcher.sh:AGENT_ID(合成) / 讀手 scripts/inbox_watcher.sh:776 類 ⑷
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
AGENT_ID="${AGENT_ID:-unknown}"
printf 'TARGET='; printf '%s' startup_prompt="Session Start — do ALL of this in one turn, do NOT stop early: 1) tmux display-message to identify yourself. 2) Read queue/tasks/${AGENT_ID}.yaml. 3) Read queue/inbox/${AGENT_ID}.yaml, mark read:true. 4) Read context_files. 5) Execute the assigned task to completion — edit files, run commands, write reports. Keep working until done." | od -An -v -tx1 | tr -d ' \n'; printf '\n'
