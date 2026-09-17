#!/bin/bash
# 写し器 49 ―― 口 scripts/inbox_watcher.sh:AGENT_ID(合成) / 讀手 scripts/inbox_watcher.sh:322 類 ⑶ / 派 NUDGE_FINGERPRINT_FILE
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
AGENT_ID="${AGENT_ID:-unknown}"
NUDGE_FINGERPRINT_FILE=${NUDGE_FINGERPRINT_FILE:-/tmp/inbox_watcher_nudge_fingerprint_${AGENT_ID:-unknown}}
printf 'TARGET='; printf '%s' "$NUDGE_FINGERPRINT_FILE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
