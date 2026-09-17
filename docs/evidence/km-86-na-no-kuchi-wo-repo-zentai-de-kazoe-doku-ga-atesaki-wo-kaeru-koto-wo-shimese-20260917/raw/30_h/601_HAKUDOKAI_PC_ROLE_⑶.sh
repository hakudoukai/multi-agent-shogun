#!/bin/bash
# 写し器 601 ―― 口 shutsujin_departure.sh:HAKUDOKAI_PC_ROLE(合成) / 讀手 shim/hakudokai/hakudokai_watchdog.sh:177 類 ⑶ / 派 PC_ROLE
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
HAKUDOKAI_PC_ROLE="${HAKUDOKAI_PC_ROLE:-MainPC}"
PC_ROLE="${HAKUDOKAI_PC_ROLE:-MainPC}"
printf 'TARGET='; printf '%s' "$PC_ROLE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
