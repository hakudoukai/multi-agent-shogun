#!/bin/bash
# 写し器 7 ―― scripts/inbox_watcher.sh:1032 旗 INBOX_WATCHER_DISABLE_TYPING_CHECK 類 甲 / 口= (口は比較器の中・純粋な口無し)

if [ "${INBOX_WATCHER_DISABLE_TYPING_CHECK:-0}" = "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
