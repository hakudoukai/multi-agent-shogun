#!/bin/bash
# 写し器 577 ―― 口 shim/hakudokai/hakudokai_start_watchers.sh:SUPABASE_URL(合成) / 讀手 scripts/inbox_write.sh:197 類 ⑶ / 派 sb_url
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SUPABASE_URL="${SUPABASE_URL:-}"
sb_url="${SUPABASE_URL:-$sb_url}"
printf 'TARGET='; printf '%s' "${sb_url}/rest/v1/pc_handshake" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
