#!/bin/bash
# 写し器 136 ―― 口 scripts/stop_hook_inbox.sh:IDLE_FLAG_DIR(合成) / 讀手 scripts/stop_hook_inbox.sh:216 類 ⑶ / 派 FLAG
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
IDLE_FLAG_DIR="${IDLE_FLAG_DIR:-/tmp}"
FLAG="${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}"
printf 'TARGET='; printf '%s' "$FLAG" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
