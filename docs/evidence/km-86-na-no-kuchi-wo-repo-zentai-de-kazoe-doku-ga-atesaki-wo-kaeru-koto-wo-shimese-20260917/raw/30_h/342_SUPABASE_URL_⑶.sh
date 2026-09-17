#!/bin/bash
# 写し器 342 ―― 口 shim/hakudokai/hakudokai_audit_scheduler.sh:SUPABASE_URL(合成) / 讀手 shim/hakudokai/hakudokai_secondpc_watcher.sh:82 類 ⑶ / 派 SUPABASE_API
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_API="${SUPABASE_URL}/rest/v1"
printf 'TARGET='; printf '%s' "${SUPABASE_API}/pc_handshake?select=id,from_pc,to_pc,topic,content,priority,message_type,created_at&or=(to_pc.eq.main_pc,to_pc.eq.broadcast)&from_pc=eq.second_pc&acknowledged_at=is.null&clinic_id=eq.${CLINIC_ID}&order=created_at.asc&limit=10" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
