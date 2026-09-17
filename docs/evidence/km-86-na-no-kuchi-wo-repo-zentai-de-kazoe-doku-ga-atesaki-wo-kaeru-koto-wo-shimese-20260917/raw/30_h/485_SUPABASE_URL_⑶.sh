#!/bin/bash
# 写し器 485 ―― 口 shim/hakudokai/hakudokai_minimal_install.sh:SUPABASE_URL(合成) / 讀手 shim/hakudokai/hakudokai_secondpc_receiver.sh:65 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SUPABASE_URL="${SUPABASE_URL:-}"
printf 'TARGET='; printf '%s' "${SUPABASE_URL}/rest/v1/pc_handshake?select=id,from_pc,to_pc,topic,content,context_data,priority,message_type,created_at&to_pc=eq.second_pc&acknowledged_at=is.null&order=created_at.asc&limit=10" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
