#!/bin/bash
# 写し器 218 ―― 口 skills/shogun-screenshot/scripts/capture_local.sh:MULTI_AGENT_SHOGUN_DIR(合成) / 讀手 skills/shogun-screenshot/scripts/capture_local.sh:29 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MULTI_AGENT_SHOGUN_DIR="${MULTI_AGENT_SHOGUN_DIR:-}"
printf 'TARGET='; printf '%s' "${MULTI_AGENT_SHOGUN_DIR:-}" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
