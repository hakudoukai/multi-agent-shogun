#!/bin/bash
# 写し器 1 ―― scripts/inbox_watcher.sh:1481 旗 ASW_DISABLE_ESCALATION 類 甲 / 口= ASW_DISABLE_ESCALATION=${ASW_DISABLE_ESCALATION:-0}

ASW_DISABLE_ESCALATION=${ASW_DISABLE_ESCALATION:-0}
if [ "${ASW_DISABLE_ESCALATION:-0}" = "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
