#!/bin/bash
# 写し器 101 ―― 口 scripts/karo_overload_monitor.sh:GLOBAL_DISABLE_FLAG(逐語) / 讀手 scripts/karo_overload_monitor.sh:108 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${GLOBAL_DISABLE_FLAG:=$HOME/.openclaw/global_disable}"
printf 'TARGET='; printf '%s' "$GLOBAL_DISABLE_FLAG" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
