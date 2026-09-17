#!/bin/bash
# 写し器 138 ―― 口 scripts/stop_hook_inbox.sh:TMUX_PANE(合成) / 讀手 scripts/stop_hook_inbox.sh:99 類 ⑴
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
TMUX_PANE="${TMUX_PANE:-}"
tmux display-message -t "$TMUX_PANE" -p '#{@agent_id}'
