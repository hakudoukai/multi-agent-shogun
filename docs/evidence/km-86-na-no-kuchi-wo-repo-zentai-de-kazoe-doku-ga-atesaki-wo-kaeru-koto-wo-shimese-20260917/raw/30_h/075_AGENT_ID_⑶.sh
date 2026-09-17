#!/bin/bash
# 写し器 75 ―― 口 scripts/inbox_watcher.sh:AGENT_ID(合成) / 讀手 scripts/inbox_watcher.sh:1577 類 ⑶ / 派 WATCHER_DISABLE_FLAG
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
AGENT_ID="${AGENT_ID:-unknown}"
WATCHER_DISABLE_FLAG="$HOME/.openclaw/disable_inbox_watcher_${AGENT_ID}"
printf 'TARGET='; printf '%s' "$WATCHER_DISABLE_FLAG" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
