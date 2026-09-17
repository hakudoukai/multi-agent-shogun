#!/bin/bash
# 写し器 3 ―― 口 first_setup.sh:NVM_DIR(逐語) / 讀手 first_setup.sh:207 類 ⑶
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
printf 'TARGET='; printf '%s' "$NVM_DIR/nvm.sh" | od -An -v -tx1 | tr -d ' \n'; printf '\n'
