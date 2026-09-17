#!/bin/bash
# 写し器 30 ―― 口 scripts/checks/pane_identity.sh:PANE_REGISTRY(逐語) / 讀手 scripts/checks/pane_identity.sh:208 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${PANE_REGISTRY:=$REPO_ROOT/queue/pane_registry.yaml}"
printf 'TARGET='; printf '%s' "$PANE_REGISTRY" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
