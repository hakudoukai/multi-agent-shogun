#!/bin/bash
# 写し器 97 ―― 口 scripts/karo_overload_monitor.sh:DISABLE_FLAG(逐語) / 讀手 scripts/karo_overload_monitor.sh:113 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${DISABLE_FLAG:=$HOME/.openclaw/disable_karo_overload_monitor}"
printf 'TARGET='; printf '%s' "$DISABLE_FLAG" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
