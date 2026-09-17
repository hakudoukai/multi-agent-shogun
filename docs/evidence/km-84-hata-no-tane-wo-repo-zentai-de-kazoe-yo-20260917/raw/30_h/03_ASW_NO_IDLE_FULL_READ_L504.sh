#!/bin/bash
# 写し器 3 ―― scripts/inbox_watcher.sh:504 旗 ASW_NO_IDLE_FULL_READ 類 甲 / 口= ASW_NO_IDLE_FULL_READ=${ASW_NO_IDLE_FULL_READ:-1}

ASW_NO_IDLE_FULL_READ=${ASW_NO_IDLE_FULL_READ:-1}
if [ "${ASW_NO_IDLE_FULL_READ:-1}" = "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
