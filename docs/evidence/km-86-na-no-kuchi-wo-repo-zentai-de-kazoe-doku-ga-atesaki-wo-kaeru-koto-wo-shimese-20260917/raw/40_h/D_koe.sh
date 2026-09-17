#!/bin/bash
# 対照の写し器(第79弾 km-86)
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
P="${P:-1}"
if [ "$P" -eq 1 ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
