#!/bin/bash
# 写し器 143 ―― 口 scripts/stop_hook_inbox.sh:TMUX_PANE(合成) / 讀手 scripts/stop_hook_inbox.sh:181 類 ⑷ / 派 AGENT_ID
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
TMUX_PANE="${TMUX_PANE:-}"
AGENT_ID=$(tmux display-message -t "$TMUX_PANE" -p '#{@agent_id}' 2>/dev/null || true)
printf 'TARGET='; printf '%s' INBOX="$SCRIPT_DIR/queue/inbox/${AGENT_ID}.yaml" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
