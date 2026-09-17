#!/bin/bash
# 写し器 8 ―― scripts/inbox_watcher.sh:671 旗 NEW_CONTEXT_SENT 類 乙 / 口= NEW_CONTEXT_SENT=${NEW_CONTEXT_SENT:-0}

NEW_CONTEXT_SENT=${NEW_CONTEXT_SENT:-0}
if [ "${NEW_CONTEXT_SENT:-0}" -eq 1 ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
