#!/bin/bash
# 写し器 19 ―― 口 scripts/agent_health_check.sh:HEALTH_CHECK_STRUCT_LOG(合成) / 讀手 scripts/agent_health_check.sh:214 類 ⑶ / 派 STRUCT_LOG
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
HEALTH_CHECK_STRUCT_LOG="${HEALTH_CHECK_STRUCT_LOG:-/tmp/agent_health_check_struct.log}"
STRUCT_LOG="${HEALTH_CHECK_STRUCT_LOG:-/tmp/agent_health_check_struct.log}"
printf 'TARGET='; printf '%s' "$STRUCT_LOG" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
