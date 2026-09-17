#!/bin/bash
# 写し器 14 ―― scripts/inbox_write.sh:48 旗 IW_DEFERRAL_TEST_ONLY 類 甲 / 口= (口は比較器の中・純粋な口無し)

if [ "${IW_DEFERRAL_TEST_ONLY:-}" = "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
