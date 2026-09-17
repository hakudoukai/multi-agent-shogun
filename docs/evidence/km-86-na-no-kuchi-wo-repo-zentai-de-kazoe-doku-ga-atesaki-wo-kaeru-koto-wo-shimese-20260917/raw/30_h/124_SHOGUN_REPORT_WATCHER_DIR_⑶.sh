#!/bin/bash
# 写し器 124 ―― 口 scripts/redundancy/shogun_report_watcher.sh:SHOGUN_REPORT_WATCHER_DIR(合成) / 讀手 scripts/redundancy/shogun_report_watcher.sh:112 類 ⑶ / 派 REPORTS_DIR
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SHOGUN_REPORT_WATCHER_DIR="${SHOGUN_REPORT_WATCHER_DIR:-$SCRIPT_DIR/queue/reports}"
REPORTS_DIR="${SHOGUN_REPORT_WATCHER_DIR:-$SCRIPT_DIR/queue/reports}"
printf 'TARGET='; printf '%s' "$REPORTS_DIR" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
