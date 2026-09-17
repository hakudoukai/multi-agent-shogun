#!/bin/bash
# 写し器 244 ―― 口 tests/e2e/mock_behaviors/common.sh:IDLE_FLAG_DIR(合成) / 讀手 tests/e2e/mock_behaviors/common.sh:150 類 ⑶ / 派 _flag_dir
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
IDLE_FLAG_DIR="${IDLE_FLAG_DIR:-/tmp}"
_flag_dir="${IDLE_FLAG_DIR:-/tmp}"
printf 'TARGET='; printf '%s' "${_flag_dir}/shogun_idle_${MOCK_AGENT_ID}" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
