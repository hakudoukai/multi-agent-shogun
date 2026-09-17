#!/bin/bash
# 写し器 112 ―― 口 scripts/karo_second_send_iincho.sh:HTTP_CODE(合成) / 讀手 scripts/karo_second_send_iincho.sh:147 類 ⑸
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
HTTP_CODE="${HTTP_CODE:-<empty>}"
printf 'TARGET='; printf '%s' "$HTTP_CODE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; if [ "$HTTP_CODE" = "201" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
