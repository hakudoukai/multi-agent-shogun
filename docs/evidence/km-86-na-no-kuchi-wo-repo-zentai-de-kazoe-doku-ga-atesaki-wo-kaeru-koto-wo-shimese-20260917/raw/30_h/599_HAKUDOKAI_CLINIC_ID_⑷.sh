#!/bin/bash
# 写し器 599 ―― 口 shim/hakudokai/hakudokai_task_sync.sh:HAKUDOKAI_CLINIC_ID(合成) / 讀手 shim/hakudokai/hakudokai_fukuincho_watcher.sh:80 類 ⑷ / 派 CLINIC_ID
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
HAKUDOKAI_CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"
printf 'TARGET='; printf '%s' "{\"message_type\":\"urgent_stop\",\"from_pc\":\"main_pc\",\"to_pc\":\"fukuincho\",\"topic\":\"watcher_alert\",\"content\":\"$msg\",\"requires_response\":false,\"priority\":\"urgent\",\"clinic_id\":\"${CLINIC_ID}\",\"bypass_5round_limit\":false,\"is_meta_only\":false}" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
