#!/bin/bash
# 写し器 264 ―― 口 tests/e2e/mock_cli.sh:MOCK_PROJECT_ROOT(逐語) / 讀手 tests/e2e/mock_cli.sh:103 類 ⑶ / 派 inbox_write_script
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MOCK_PROJECT_ROOT="${MOCK_PROJECT_ROOT:-.}"
inbox_write_script="$MOCK_PROJECT_ROOT/scripts/inbox_write.sh"
printf 'TARGET='; printf '%s' "$inbox_write_script" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
