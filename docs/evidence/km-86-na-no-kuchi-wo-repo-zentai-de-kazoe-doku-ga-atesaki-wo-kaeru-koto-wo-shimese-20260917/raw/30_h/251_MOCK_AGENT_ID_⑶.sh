#!/bin/bash
# 写し器 251 ―― 口 tests/e2e/mock_cli.sh:MOCK_AGENT_ID(逐語) / 讀手 tests/e2e/mock_cli.sh:120 類 ⑶ / 派 INBOX_FILE
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MOCK_AGENT_ID="${MOCK_AGENT_ID:-unknown}"
INBOX_FILE="$MOCK_PROJECT_ROOT/queue/inbox/${MOCK_AGENT_ID}.yaml"
printf 'TARGET='; printf '%s' "$INBOX_FILE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
