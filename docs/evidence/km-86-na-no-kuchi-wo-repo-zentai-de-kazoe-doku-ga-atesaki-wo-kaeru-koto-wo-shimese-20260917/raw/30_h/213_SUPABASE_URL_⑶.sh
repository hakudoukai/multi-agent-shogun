#!/bin/bash
# 写し器 213 ―― 口 shim/hakudokai/hakudokai_watchdog.sh:SUPABASE_URL(合成) / 讀手 shim/hakudokai/hakudokai_watchdog.sh:728 類 ⑶ / 派 SUPABASE_API
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_API="${SUPABASE_URL}/rest/v1"
printf 'TARGET='; printf '%s' "${SUPABASE_API}/task_tracker?active_on_pc=eq.third_pc&status=eq.in_progress" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
