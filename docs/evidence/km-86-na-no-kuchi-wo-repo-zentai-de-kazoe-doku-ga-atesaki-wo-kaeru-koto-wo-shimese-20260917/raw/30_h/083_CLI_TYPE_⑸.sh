#!/bin/bash
# 写し器 83 ―― 口 scripts/inbox_watcher.sh:CLI_TYPE(合成) / 讀手 scripts/inbox_watcher.sh:376 類 ⑸
tmux(){ for __a in "$@"; do printf 'TMUX_ARG='; printf '%s' "$__a" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; done; printf 'TMUX_NARGS=%s\n' "$#"; }; timeout(){ shift; "$@"; }; gtimeout(){ shift; "$@"; }
CLI_TYPE="${CLI_TYPE:-}"
printf 'TARGET='; printf '%s' "$CLI_TYPE" | od -An -v -tx1 | tr -d ' \n'; printf '\n'; if [ "$pane_cli" != "${CLI_TYPE}" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
