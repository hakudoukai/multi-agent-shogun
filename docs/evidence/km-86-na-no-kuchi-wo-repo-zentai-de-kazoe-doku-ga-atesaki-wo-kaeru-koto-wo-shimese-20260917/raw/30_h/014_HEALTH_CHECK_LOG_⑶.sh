#!/bin/bash
# 写し器 14 ―― 口 scripts/agent_health_check.sh:HEALTH_CHECK_LOG(合成) / 讀手 scripts/agent_health_check.sh:203 類 ⑶ / 派 LOG
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
HEALTH_CHECK_LOG="${HEALTH_CHECK_LOG:-/tmp/agent_health_check.log}"
LOG="${HEALTH_CHECK_LOG:-/tmp/agent_health_check.log}"
printf 'TARGET='; printf '%s' "$LOG" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
