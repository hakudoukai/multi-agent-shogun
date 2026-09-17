#!/bin/bash
# 写し器 597 ―― 口 shim/hakudokai/hakudokai_start_watchers.sh:SUPABASE_URL(合成) / 讀手 shim/hakudokai/hakudokai_watchdog.sh:413 類 ⑶ / 派 SUPABASE_API
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_API="${SUPABASE_URL}/rest/v1"
printf 'TARGET='; printf '%s' "${SUPABASE_API}/dev_lessons" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
