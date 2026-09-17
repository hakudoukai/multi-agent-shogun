#!/bin/bash
# 写し器 26 ―― 口 scripts/checks/pane_identity.sh:CLAUDE_MD(逐語) / 讀手 scripts/checks/pane_identity.sh:293 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${CLAUDE_MD:=$REPO_ROOT/CLAUDE.md}"
printf 'TARGET='; printf '%s' "$CLAUDE_MD" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
