#!/bin/bash
# 写し器 104 ―― 口 scripts/karo_overload_monitor.sh:KARO_INBOX(逐語) / 讀手 scripts/karo_overload_monitor.sh:226 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${KARO_INBOX:=$REPO_ROOT/queue/inbox/karo.yaml}"
printf 'TARGET='; printf '%s' "$KARO_INBOX" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
