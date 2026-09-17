#!/bin/bash
# 写し器 38 ―― 口 scripts/inbox_watcher.sh:AGENT_ID(合成) / 讀手 scripts/inbox_watcher.sh:35 類 ⑷
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
AGENT_ID="${AGENT_ID:-unknown}"
printf 'TARGET='; printf '%s' INBOX="$SCRIPT_DIR/queue/inbox/${AGENT_ID}.yaml" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
