#!/bin/bash
# 写し器 306 ―― 口 scripts/watchdogs/enter_restart_shogun_third_watchdog.sh:ER_LOG_DIR(逐語) / 讀手 scripts/watchdogs/enter_restart_common_watchdog.sh:56 類 ⑶ / 派 LOG_DIR
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
export ER_LOG_DIR="${ER_LOG_DIR:-/home/hakudoukai/.local/share/enter_restart_shogun_third}"
LOG_DIR="$ER_LOG_DIR"
printf 'TARGET='; printf '%s' "$LOG_DIR" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
