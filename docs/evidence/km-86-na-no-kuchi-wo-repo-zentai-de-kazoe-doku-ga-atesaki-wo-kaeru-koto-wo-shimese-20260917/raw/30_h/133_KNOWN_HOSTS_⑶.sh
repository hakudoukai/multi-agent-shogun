#!/bin/bash
# 写し器 133 ―― 口 scripts/setup_known_hosts.sh:KNOWN_HOSTS(逐語) / 讀手 scripts/setup_known_hosts.sh:36 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
KNOWN_HOSTS="${KNOWN_HOSTS:-$HOME/.ssh/known_hosts}"
printf 'TARGET='; printf '%s' "$KNOWN_HOSTS" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
