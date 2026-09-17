#!/bin/bash
# 写し器 6 ―― 口 first_setup.sh:REPLY(逐語) / 讀手 first_setup.sh:454 類 ⑸
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
REPLY=${REPLY:-Y}
printf 'TARGET='; printf '%s' "$REPLY" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; if [[ $REPLY =~ ^[Yy]$ ]]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
