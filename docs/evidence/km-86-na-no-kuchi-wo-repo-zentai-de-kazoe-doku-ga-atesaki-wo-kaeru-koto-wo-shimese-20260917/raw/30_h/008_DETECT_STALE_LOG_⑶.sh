#!/bin/bash
# 写し器 8 ―― 口 scripts/agent_health_check.sh:DETECT_STALE_LOG(合成) / 讀手 scripts/agent_health_check.sh:451 類 ⑶ / 派 _detect_stale_log_file
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
DETECT_STALE_LOG="${DETECT_STALE_LOG:-/tmp/fukuincho_detect_stale.log}"
_detect_stale_log_file="${DETECT_STALE_LOG:-/tmp/fukuincho_detect_stale.log}"
printf 'TARGET='; printf '%s' "$_detect_stale_log_file" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
