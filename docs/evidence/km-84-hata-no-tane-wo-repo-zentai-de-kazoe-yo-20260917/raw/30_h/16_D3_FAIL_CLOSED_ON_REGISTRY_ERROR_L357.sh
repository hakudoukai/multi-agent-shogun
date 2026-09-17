#!/bin/bash
# 写し器 16 ―― shim/hakudokai/hakudokai_watchdog.sh:357 旗 D3_FAIL_CLOSED_ON_REGISTRY_ERROR 類 甲 / 口= D3_FAIL_CLOSED_ON_REGISTRY_ERROR="${D3_FAIL_CLOSED_ON_REGISTRY_ERROR:-1}"

D3_FAIL_CLOSED_ON_REGISTRY_ERROR="${D3_FAIL_CLOSED_ON_REGISTRY_ERROR:-1}"
if [ "${D3_FAIL_CLOSED_ON_REGISTRY_ERROR:-1}" = "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
