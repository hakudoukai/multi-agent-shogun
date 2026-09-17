#!/bin/bash
# 写し器 326 ―― 口 shim/hakudokai/hakudokai_audit_scheduler.sh:SUPABASE_URL(合成) / 讀手 scripts/commander_send_shogun_second.sh:88 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SUPABASE_URL="${SUPABASE_URL:-}"
printf 'TARGET='; printf '%s' "${SUPABASE_URL}/rest/v1/pc_handshake" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
