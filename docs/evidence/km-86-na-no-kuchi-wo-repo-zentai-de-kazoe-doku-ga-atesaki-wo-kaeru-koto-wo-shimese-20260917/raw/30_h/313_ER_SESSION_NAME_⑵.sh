#!/bin/bash
# 写し器 313 ―― 口 scripts/watchdogs/enter_restart_shogun_third_watchdog.sh:ER_SESSION_NAME(逐語) / 讀手 scripts/watchdogs/enter_restart_common_watchdog.sh:176 類 ⑵ / 派 SESSION_NAME
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
export ER_SESSION_NAME="${ER_SESSION_NAME:-shogun-third}"
SESSION_NAME="$ER_SESSION_NAME"
tmux has-session -t "$SESSION_NAME"
