#!/bin/bash
# 写し器 103 ―― 口 scripts/karo_overload_monitor.sh:INBOX_WRITE_CMD(逐語) / 讀手 scripts/karo_overload_monitor.sh:350 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
: "${INBOX_WRITE_CMD:=$SCRIPT_DIR/inbox_write.sh}"
printf 'TARGET='; printf '%s' "$INBOX_WRITE_CMD" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
