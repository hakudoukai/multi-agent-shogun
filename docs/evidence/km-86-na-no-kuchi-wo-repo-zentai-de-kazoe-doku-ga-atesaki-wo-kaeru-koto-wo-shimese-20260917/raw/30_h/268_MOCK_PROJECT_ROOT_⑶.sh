#!/bin/bash
# 写し器 268 ―― 口 tests/e2e/mock_cli.sh:MOCK_PROJECT_ROOT(逐語) / 讀手 tests/e2e/mock_cli.sh:193 類 ⑶ / 派 cmd_file
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MOCK_PROJECT_ROOT="${MOCK_PROJECT_ROOT:-.}"
cmd_file="$MOCK_PROJECT_ROOT/queue/shogun_to_karo.yaml"
printf 'TARGET='; printf '%s' "$cmd_file" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
