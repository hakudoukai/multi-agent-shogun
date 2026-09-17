#!/bin/bash
# 写し器 220 ―― 口 skills/shogun-screenshot/scripts/capture_local.sh:MULTI_AGENT_SHOGUN_DIR(合成) / 讀手 skills/shogun-screenshot/scripts/capture_local.sh:78 類 ⑶ / 派 SETTINGS_FILE
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MULTI_AGENT_SHOGUN_DIR="${MULTI_AGENT_SHOGUN_DIR:-}"
SETTINGS_FILE="${MULTI_AGENT_SHOGUN_DIR}/config/settings.yaml"
printf 'TARGET='; printf '%s' "$SETTINGS_FILE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
