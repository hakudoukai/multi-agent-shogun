#!/bin/bash
# 写し器 595 ―― 口 shim/hakudokai/hakudokai_start_watchers.sh:SUPABASE_URL(合成) / 讀手 shim/hakudokai/hakudokai_watchdog.sh:69 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SUPABASE_URL="${SUPABASE_URL:-}"
printf 'TARGET='; printf '%s' SUPABASE_API="${SUPABASE_URL}/rest/v1" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
