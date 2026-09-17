#!/bin/bash
# 写し器 13 ―― scripts/inbox_write.sh:81 旗 IW_DEAD_TEST_ONLY 類 甲 / 口= (口は比較器の中・純粋な口無し)

if [ "${IW_DEAD_TEST_ONLY:-}" = "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
