#!/bin/bash
# 写し器 10 ―― scripts/inbox_watcher.sh:1469 旗 STARTUP_PROMPT_SENT 類 乙 / 口= STARTUP_PROMPT_SENT=${STARTUP_PROMPT_SENT:-0}

STARTUP_PROMPT_SENT=${STARTUP_PROMPT_SENT:-0}
if [ "$STARTUP_PROMPT_SENT" -eq 1 ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
