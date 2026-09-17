#!/bin/bash
# 写し器 58 ―― 口 scripts/inbox_watcher.sh:AGENT_ID(合成) / 讀手 scripts/inbox_watcher.sh:937 類 ⑶ / 派 alert_file
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
AGENT_ID="${AGENT_ID:-unknown}"
alert_file="${APPROVAL_ALERT_FILE:-/tmp/inbox_watcher_approval_${AGENT_ID}}"
printf 'TARGET='; printf '%s' "$alert_file" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
