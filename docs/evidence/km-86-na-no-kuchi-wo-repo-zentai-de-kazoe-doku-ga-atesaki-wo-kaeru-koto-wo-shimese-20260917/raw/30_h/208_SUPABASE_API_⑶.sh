#!/bin/bash
# 写し器 208 ―― 口 shim/hakudokai/hakudokai_watchdog.sh:SUPABASE_API(合成) / 讀手 shim/hakudokai/hakudokai_watchdog.sh:413 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SUPABASE_API="${SUPABASE_API:-}"
printf 'TARGET='; printf '%s' "${SUPABASE_API}/dev_lessons" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
