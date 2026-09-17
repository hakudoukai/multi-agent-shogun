#!/bin/bash
# 写し器 296 ―― 口 scripts/watchdogs/enter_restart_shogun_main_watchdog.sh:ER_PANE_TARGET(逐語) / 讀手 scripts/watchdogs/enter_restart_common_watchdog.sh:322 類 ⑴ / 派 PANE_TARGET
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
export ER_PANE_TARGET="${ER_PANE_TARGET:-shogun-main:shogun.0}"
PANE_TARGET="$ER_PANE_TARGET"
tmux send-keys -t "$PANE_TARGET" Enter
