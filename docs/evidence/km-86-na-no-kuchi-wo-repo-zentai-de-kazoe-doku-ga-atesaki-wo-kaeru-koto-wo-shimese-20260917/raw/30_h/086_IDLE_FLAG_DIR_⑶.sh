#!/bin/bash
# 写し器 86 ―― 口 scripts/inbox_watcher.sh:IDLE_FLAG_DIR(合成) / 讀手 scripts/inbox_watcher.sh:299 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
IDLE_FLAG_DIR="${IDLE_FLAG_DIR:-/tmp}"
printf 'TARGET='; printf '%s' "${IDLE_FLAG_DIR:-/tmp}/shogun_idle_${AGENT_ID}" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
