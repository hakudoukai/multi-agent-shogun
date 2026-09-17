#!/bin/bash
# 写し器 4 ―― scripts/inbox_watcher.sh:1633 旗 ASW_PROCESS_TIMEOUT 類 甲 / 口= (口は比較器の中・純粋な口無し)

if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
