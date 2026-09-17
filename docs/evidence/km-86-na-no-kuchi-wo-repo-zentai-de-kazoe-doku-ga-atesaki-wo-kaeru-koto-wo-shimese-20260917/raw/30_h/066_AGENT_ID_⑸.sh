#!/bin/bash
# 写し器 66 ―― 口 scripts/inbox_watcher.sh:AGENT_ID(合成) / 讀手 scripts/inbox_watcher.sh:1288 類 ⑸
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
AGENT_ID="${AGENT_ID:-unknown}"
printf 'TARGET='; printf '%s' "$AGENT_ID" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; if [ "$AGENT_ID" = "shogun" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
