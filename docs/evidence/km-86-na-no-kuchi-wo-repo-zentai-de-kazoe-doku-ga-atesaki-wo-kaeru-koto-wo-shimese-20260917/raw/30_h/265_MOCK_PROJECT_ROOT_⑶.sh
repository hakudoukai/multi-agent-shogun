#!/bin/bash
# 写し器 265 ―― 口 tests/e2e/mock_cli.sh:MOCK_PROJECT_ROOT(逐語) / 讀手 tests/e2e/mock_cli.sh:120 類 ⑶ / 派 INBOX_FILE
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MOCK_PROJECT_ROOT="${MOCK_PROJECT_ROOT:-.}"
INBOX_FILE="$MOCK_PROJECT_ROOT/queue/inbox/${MOCK_AGENT_ID}.yaml"
printf 'TARGET='; printf '%s' "$INBOX_FILE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
