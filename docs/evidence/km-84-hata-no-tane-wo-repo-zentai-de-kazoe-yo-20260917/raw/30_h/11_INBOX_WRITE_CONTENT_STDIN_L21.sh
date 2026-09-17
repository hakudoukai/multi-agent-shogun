#!/bin/bash
# 写し器 11 ―― scripts/inbox_write.sh:21 旗 INBOX_WRITE_CONTENT_STDIN 類 甲 / 口= (口は比較器の中・純粋な口無し)

if [ "${INBOX_WRITE_CONTENT_STDIN:-}" = "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
