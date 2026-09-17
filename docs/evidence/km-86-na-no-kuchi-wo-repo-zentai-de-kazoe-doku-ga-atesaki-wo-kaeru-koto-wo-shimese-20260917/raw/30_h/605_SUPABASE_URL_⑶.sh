#!/bin/bash
# 写し器 605 ―― 口 tests/smoke/test_enter_restart_watchdog.sh:SUPABASE_URL(逐語) / 讀手 scripts/agent_health_check.sh:223 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
export SUPABASE_URL="${SUPABASE_URL:-http://stub.invalid}"
printf 'TARGET='; printf '%s' "${SUPABASE_URL}/rest/v1/pc_handshake?topic=like.cross_pc_inbox_*&created_at=gte.${NOW1_JST}&select=created_at" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
