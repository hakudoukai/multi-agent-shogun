#!/bin/bash
# 写し器 248 ―― 口 tests/e2e/mock_cli.sh:MOCK_AGENT_ID(逐語) / 讀手 tests/e2e/mock_cli.sh:43 類 ⑷
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MOCK_AGENT_ID="${MOCK_AGENT_ID:-unknown}"
printf 'TARGET='; printf '%s' INBOX_FILE="$MOCK_PROJECT_ROOT/queue/inbox/${MOCK_AGENT_ID}.yaml" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
