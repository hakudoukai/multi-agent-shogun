#!/bin/bash
# 写し器 102 ―― 口 scripts/karo_overload_monitor.sh:HEALTH_FILE(逐語) / 讀手 scripts/karo_overload_monitor.sh:127 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${HEALTH_FILE:=/tmp/karo_overload_monitor.health}"
printf 'TARGET='; printf '%s' "$HEALTH_FILE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
