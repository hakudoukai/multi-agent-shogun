#!/bin/bash
# 写し器 544 ―― 口 shim/hakudokai/hakudokai_reports_sync.sh:HAKUDOKAI_CLINIC_ID(合成) / 讀手 shim/hakudokai/hakudokai_watchdog.sh:390 類 ⑷ / 派 CLINIC_ID
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
HAKUDOKAI_CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-}"
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"
printf 'TARGET='; printf '%s' "{\"message_type\":\"urgent_stop\",\"from_pc\":\"second_pc\",\"to_pc\":\"fukuincho\",\"topic\":\"watchdog_failsafe\",\"content\":\"${msg}\",\"requires_response\":true,\"priority\":\"urgent\",\"clinic_id\":\"${CLINIC_ID}\",\"bypass_5round_limit\":false,\"is_meta_only\":false}" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
