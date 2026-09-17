#!/bin/bash
# 写し器 302 ―― 口 scripts/watchdogs/enter_restart_shogun_second_watchdog.sh:ER_PANE_TARGET(逐語) / 讀手 scripts/watchdogs/enter_restart_common_watchdog.sh:244 類 ⑴ / 派 PANE_TARGET
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
export ER_PANE_TARGET="${ER_PANE_TARGET:-shogun-second:0.0}"
PANE_TARGET="$ER_PANE_TARGET"
tmux display-message -t "$PANE_TARGET" -p '#{pane_current_path}|#{pane_title}|#{pane_current_command}'
