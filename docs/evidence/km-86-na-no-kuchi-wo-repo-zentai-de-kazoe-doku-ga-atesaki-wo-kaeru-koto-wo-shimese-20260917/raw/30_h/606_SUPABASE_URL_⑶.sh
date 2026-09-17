#!/bin/bash
# 写し器 606 ―― 口 tests/smoke/test_enter_restart_watchdog.sh:SUPABASE_URL(逐語) / 讀手 scripts/commander_send_shogun_second.sh:88 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
export SUPABASE_URL="${SUPABASE_URL:-http://stub.invalid}"
printf 'TARGET='; printf '%s' "${SUPABASE_URL}/rest/v1/pc_handshake" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
