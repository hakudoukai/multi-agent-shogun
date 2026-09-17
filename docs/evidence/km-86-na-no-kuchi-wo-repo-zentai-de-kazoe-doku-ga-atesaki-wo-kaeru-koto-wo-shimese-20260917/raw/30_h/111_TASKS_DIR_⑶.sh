#!/bin/bash
# 写し器 111 ―― 口 scripts/karo_overload_monitor.sh:TASKS_DIR(逐語) / 讀手 scripts/karo_overload_monitor.sh:317 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${TASKS_DIR:=$REPO_ROOT/queue/tasks}"
printf 'TARGET='; printf '%s' "$TASKS_DIR"/ashigaru*.yaml | od -An -v -tx1 | tr -d ' \n'; printf '\n'
