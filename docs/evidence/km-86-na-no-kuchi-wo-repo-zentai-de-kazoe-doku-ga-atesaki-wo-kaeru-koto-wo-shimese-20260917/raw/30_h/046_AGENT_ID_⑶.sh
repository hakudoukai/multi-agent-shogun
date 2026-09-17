#!/bin/bash
# 写し器 46 ―― 口 scripts/inbox_watcher.sh:AGENT_ID(合成) / 讀手 scripts/inbox_watcher.sh:282 類 ⑶ / 派 METRICS_FILE
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
AGENT_ID="${AGENT_ID:-unknown}"
METRICS_FILE=${METRICS_FILE:-${SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}/queue/metrics/${AGENT_ID:-unknown}_selfwatch.yaml}
printf 'TARGET='; printf '%s' "$METRICS_FILE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
