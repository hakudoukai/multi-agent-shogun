#!/bin/bash
# 写し器 12 ―― scripts/inbox_write.sh:67 旗 IW_DEAD_ALLOW 類 甲 / 口= (口は比較器の中・純粋な口無し)

if [ "${IW_DEAD_ALLOW:-}" != "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
