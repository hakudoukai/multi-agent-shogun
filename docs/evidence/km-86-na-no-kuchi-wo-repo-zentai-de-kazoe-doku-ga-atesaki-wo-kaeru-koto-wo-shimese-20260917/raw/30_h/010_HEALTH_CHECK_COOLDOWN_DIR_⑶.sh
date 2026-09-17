#!/bin/bash
# 写し器 10 ―― 口 scripts/agent_health_check.sh:HEALTH_CHECK_COOLDOWN_DIR(合成) / 讀手 scripts/agent_health_check.sh:137 類 ⑶ / 派 ALERT_COOLDOWN_DIR
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
HEALTH_CHECK_COOLDOWN_DIR="${HEALTH_CHECK_COOLDOWN_DIR:-/tmp/agent_health_check_cooldown}"
ALERT_COOLDOWN_DIR="${HEALTH_CHECK_COOLDOWN_DIR:-/tmp/agent_health_check_cooldown}"
printf 'TARGET='; printf '%s' cf="${ALERT_COOLDOWN_DIR}/${key}.last" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
