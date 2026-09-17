#!/bin/bash
# 写し器 250 ―― 口 tests/e2e/mock_cli.sh:MOCK_AGENT_ID(逐語) / 讀手 tests/e2e/mock_cli.sh:106 類 ⑸
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
MOCK_AGENT_ID="${MOCK_AGENT_ID:-unknown}"
printf 'TARGET='; printf '%s' "$MOCK_AGENT_ID" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; if [ "$MOCK_AGENT_ID" = "karo" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
