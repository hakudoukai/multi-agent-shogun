#!/bin/bash
# 写し器 279 ―― 口 scripts/checks/pane_identity.sh:TMPDIR(合成) / 讀手 scripts/checks/verify_state_before_asserting.sh:51 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
TMPDIR="${TMPDIR:-/tmp}"
printf 'TARGET='; printf '%s' "         → git fetch -q origin && touch \"${TMPDIR:-/tmp}/.vsba_fetch_$$\" を先 に" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
