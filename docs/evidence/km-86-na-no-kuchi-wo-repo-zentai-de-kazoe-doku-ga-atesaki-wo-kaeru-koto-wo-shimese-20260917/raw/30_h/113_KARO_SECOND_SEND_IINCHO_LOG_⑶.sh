#!/bin/bash
# 写し器 113 ―― 口 scripts/karo_second_send_iincho.sh:KARO_SECOND_SEND_IINCHO_LOG(合成) / 讀手 scripts/karo_second_send_iincho.sh:32 類 ⑶ / 派 FAIL_LOG
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
KARO_SECOND_SEND_IINCHO_LOG="${KARO_SECOND_SEND_IINCHO_LOG:-/tmp/karo_second_send_iincho.log}"
FAIL_LOG="${KARO_SECOND_SEND_IINCHO_LOG:-/tmp/karo_second_send_iincho.log}"
printf 'TARGET='; printf '%s' "$FAIL_LOG" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
