#!/bin/bash
# 写し器 98 ―― 口 scripts/karo_overload_monitor.sh:DUMP_DIR(逐語) / 讀手 scripts/karo_overload_monitor.sh:383 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${DUMP_DIR:=/tmp}"
printf 'TARGET='; printf '%s' "${DUMP_DIR}/karo_overload_dump.XXXXXX.json" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
