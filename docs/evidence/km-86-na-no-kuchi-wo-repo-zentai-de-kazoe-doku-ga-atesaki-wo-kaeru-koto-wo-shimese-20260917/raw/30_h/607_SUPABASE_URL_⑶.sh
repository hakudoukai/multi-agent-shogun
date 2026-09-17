#!/bin/bash
# 写し器 607 ―― 口 tests/smoke/test_enter_restart_watchdog.sh:SUPABASE_URL(逐語) / 讀手 scripts/inbox_write.sh:197 類 ⑶ / 派 sb_url
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
export SUPABASE_URL="${SUPABASE_URL:-http://stub.invalid}"
sb_url="${SUPABASE_URL:-$sb_url}"
printf 'TARGET='; printf '%s' "${sb_url}/rest/v1/pc_handshake" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
