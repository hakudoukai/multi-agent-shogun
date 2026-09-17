#!/bin/bash
# 写し器 129 ―― 口 scripts/redundancy/shogun_report_watcher.sh:SHOGUN_REPORT_WATCHER_STATE(合成) / 讀手 scripts/redundancy/shogun_report_watcher.sh:139 類 ⑶ / 派 STATE_FILE
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SHOGUN_REPORT_WATCHER_STATE="${SHOGUN_REPORT_WATCHER_STATE:-/tmp/.shogun_report_watcher_state.json}"
STATE_FILE="${SHOGUN_REPORT_WATCHER_STATE:-/tmp/.shogun_report_watcher_state.json}"
printf 'TARGET='; printf '%s' "$STATE_FILE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
