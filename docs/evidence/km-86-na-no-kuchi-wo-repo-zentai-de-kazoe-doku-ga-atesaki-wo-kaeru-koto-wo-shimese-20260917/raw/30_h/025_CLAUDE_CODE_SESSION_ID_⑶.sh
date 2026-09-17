#!/bin/bash
# 写し器 25 ―― 口 scripts/checks/context_usage_warn.sh:CLAUDE_CODE_SESSION_ID(合成) / 讀手 scripts/checks/context_usage_warn.sh:84 類 ⑶ / 派 SESSION_ID
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
CLAUDE_CODE_SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"
SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"
printf 'TARGET='; printf '%s' JSONL_PATH="$HOME/.claude/projects/$PROJECT_SLUG/$SESSION_ID.jsonl" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
