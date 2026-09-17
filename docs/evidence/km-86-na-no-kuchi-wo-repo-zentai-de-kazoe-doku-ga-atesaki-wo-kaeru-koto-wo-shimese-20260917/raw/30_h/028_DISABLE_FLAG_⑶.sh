#!/bin/bash
# 写し器 28 ―― 口 scripts/checks/pane_identity.sh:DISABLE_FLAG(逐語) / 讀手 scripts/checks/pane_identity.sh:66 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${DISABLE_FLAG:=$HOME/.openclaw/disable_pane_identity_hook}"
printf 'TARGET='; printf '%s' "$DISABLE_FLAG" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
