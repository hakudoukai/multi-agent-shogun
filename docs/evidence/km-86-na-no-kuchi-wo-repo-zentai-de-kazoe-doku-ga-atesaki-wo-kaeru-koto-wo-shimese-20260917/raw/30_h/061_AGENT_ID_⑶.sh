#!/bin/bash
# 写し器 61 ―― 口 scripts/inbox_watcher.sh:AGENT_ID(合成) / 讀手 scripts/inbox_watcher.sh:1107 類 ⑶ / 派 skip_state_file
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
AGENT_ID="${AGENT_ID:-unknown}"
skip_state_file="/tmp/inbox_watcher_typing_skip_${AGENT_ID}"
printf 'TARGET='; printf '%s' "$skip_state_file" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
