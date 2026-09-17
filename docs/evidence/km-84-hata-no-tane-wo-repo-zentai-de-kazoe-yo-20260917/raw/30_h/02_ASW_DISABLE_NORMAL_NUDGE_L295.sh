#!/bin/bash
# 写し器 2 ―― scripts/inbox_watcher.sh:295 旗 ASW_DISABLE_NORMAL_NUDGE 類 甲 / 口= (口は比較器の中・純粋な口無し)

if [ "${ASW_DISABLE_NORMAL_NUDGE:-0}" != "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
