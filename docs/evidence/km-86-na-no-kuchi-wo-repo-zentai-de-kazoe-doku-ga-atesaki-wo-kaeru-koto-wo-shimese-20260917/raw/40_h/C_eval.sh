#!/bin/bash
# 対照の写し器(第79弾 km-86)
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
P="${P:-kaname86}"
eval "x=$P"
printf 'TARGET='; printf '%s' "$x" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
