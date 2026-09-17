#!/bin/bash
# 写し器 24 ―― 口 scripts/agent_health_check.sh:TEST_INBOX_WRITE_LOG(合成) / 讀手 scripts/agent_health_check.sh:197 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
TEST_INBOX_WRITE_LOG="${TEST_INBOX_WRITE_LOG:-}"
printf 'TARGET='; printf '%s' "$TEST_INBOX_WRITE_LOG" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
