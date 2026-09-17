#!/bin/bash
# 写し器 126 ―― 口 scripts/redundancy/shogun_report_watcher.sh:SHOGUN_REPORT_WATCHER_LOCK(合成) / 讀手 scripts/redundancy/shogun_report_watcher.sh:117 類 ⑶ / 派 LOCK_FILE
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SHOGUN_REPORT_WATCHER_LOCK="${SHOGUN_REPORT_WATCHER_LOCK:-/tmp/.shogun_report_watcher.lock}"
LOCK_FILE="${SHOGUN_REPORT_WATCHER_LOCK:-/tmp/.shogun_report_watcher.lock}"
printf 'TARGET='; printf '%s' "$LOCK_FILE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
