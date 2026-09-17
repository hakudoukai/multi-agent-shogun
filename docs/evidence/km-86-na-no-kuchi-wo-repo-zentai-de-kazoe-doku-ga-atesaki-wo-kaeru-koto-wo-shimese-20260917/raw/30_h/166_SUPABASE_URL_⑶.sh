#!/bin/bash
# 写し器 166 ―― 口 shim/hakudokai/hakudokai_fukuincho_reverse_watcher.sh:SUPABASE_URL(合成) / 讀手 shim/hakudokai/hakudokai_fukuincho_reverse_watcher.sh:99 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SUPABASE_URL="${SUPABASE_URL:-}"
printf 'TARGET='; printf '%s' "${SUPABASE_URL}/rest/v1/pc_handshake?to_pc=eq.fukuincho&acknowledged_at=is.null&order=created_at.asc&limit=5" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
