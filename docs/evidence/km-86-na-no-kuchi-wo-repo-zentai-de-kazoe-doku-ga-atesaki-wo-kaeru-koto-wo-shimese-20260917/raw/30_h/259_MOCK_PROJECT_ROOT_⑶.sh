#!/bin/bash
# 写し器 259 ―― 口 tests/e2e/mock_cli.sh:MOCK_PROJECT_ROOT(逐語) / 讀手 tests/e2e/mock_cli.sh:43 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MOCK_PROJECT_ROOT="${MOCK_PROJECT_ROOT:-.}"
printf 'TARGET='; printf '%s' INBOX_FILE="$MOCK_PROJECT_ROOT/queue/inbox/${MOCK_AGENT_ID}.yaml" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
