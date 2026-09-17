#!/bin/bash
# 写し器 247 ―― 口 tests/e2e/mock_behaviors/common.sh:MOCK_AGENT_ID(合成) / 讀手 tests/e2e/mock_behaviors/common.sh:169 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MOCK_AGENT_ID="${MOCK_AGENT_ID:-}"
printf 'TARGET='; printf '%s' "${_flag_dir}/shogun_idle_${MOCK_AGENT_ID}" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
