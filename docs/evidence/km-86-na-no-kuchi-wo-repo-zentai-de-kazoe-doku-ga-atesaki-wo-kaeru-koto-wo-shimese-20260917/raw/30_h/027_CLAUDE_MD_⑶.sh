#!/bin/bash
# 写し器 27 ―― 口 scripts/checks/pane_identity.sh:CLAUDE_MD(逐語) / 讀手 scripts/checks/pane_identity.sh:321 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${CLAUDE_MD:=$REPO_ROOT/CLAUDE.md}"
printf 'TARGET='; printf '%s' "  [WARN] source D 不在: $CLAUDE_MD (degraded mode)" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
