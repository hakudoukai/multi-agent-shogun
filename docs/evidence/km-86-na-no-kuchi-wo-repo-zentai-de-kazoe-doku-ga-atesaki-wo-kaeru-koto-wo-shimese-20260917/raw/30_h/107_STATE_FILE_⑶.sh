#!/bin/bash
# 写し器 107 ―― 口 scripts/karo_overload_monitor.sh:STATE_FILE(逐語) / 讀手 scripts/karo_overload_monitor.sh:138 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${STATE_FILE:=/tmp/karo_overload_monitor_state.json}"
printf 'TARGET='; printf '%s' "$STATE_FILE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
