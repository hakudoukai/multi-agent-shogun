#!/bin/bash
# 写し器 222 ―― 口 tests/e2e/helpers/setup.bash:E2E_QUEUE(合成) / 讀手 tests/e2e/helpers/setup.bash:28 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
E2E_QUEUE="${E2E_QUEUE:-}"
printf 'TARGET='; printf '%s' "$E2E_QUEUE/scripts" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
