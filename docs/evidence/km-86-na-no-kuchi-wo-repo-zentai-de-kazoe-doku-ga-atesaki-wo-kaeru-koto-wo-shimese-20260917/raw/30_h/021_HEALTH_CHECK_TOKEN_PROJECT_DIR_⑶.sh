#!/bin/bash
# 写し器 21 ―― 口 scripts/agent_health_check.sh:HEALTH_CHECK_TOKEN_PROJECT_DIR(合成) / 讀手 scripts/agent_health_check.sh:405 類 ⑶ / 派 TOKEN_PROJECT_DIR
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
HEALTH_CHECK_TOKEN_PROJECT_DIR="${HEALTH_CHECK_TOKEN_PROJECT_DIR:-$HOME/.claude/projects/-mnt-c-Users-User-projects-multi-agent-shogun}"
TOKEN_PROJECT_DIR="${HEALTH_CHECK_TOKEN_PROJECT_DIR:-$HOME/.claude/projects/-mnt-c-Users-User-projects-multi-agent-shogun}"
printf 'TARGET='; printf '%s' "$TOKEN_PROJECT_DIR" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
