#!/bin/bash
# 写し器 29 ―― 口 scripts/checks/pane_identity.sh:LAST_RUN_JSON(逐語) / 讀手 scripts/checks/pane_identity.sh:440 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${LAST_RUN_JSON:=/tmp/pane_identity_last_run.json}"
printf 'TARGET='; printf '%s' "$LAST_RUN_JSON" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
