#!/bin/bash
# 写し器 35 ―― 口 scripts/checks/pane_identity.sh:WATCHER_SUPERVISOR(逐語) / 讀手 scripts/checks/pane_identity.sh:281 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${WATCHER_SUPERVISOR:=$REPO_ROOT/scripts/watcher_supervisor.sh}"
printf 'TARGET='; printf '%s' "  [WARN] source C 不在: $WATCHER_SUPERVISOR (degraded mode)" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
