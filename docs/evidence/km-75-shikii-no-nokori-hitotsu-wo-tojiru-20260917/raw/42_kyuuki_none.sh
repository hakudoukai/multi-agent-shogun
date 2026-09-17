#!/usr/bin/env bash
set -euo pipefail
COOLDOWN_SEC="${SHOGUN_REPORT_WATCHER_COOLDOWN:-60}"
diff=0
if [ "$diff" -lt "$COOLDOWN_SEC" ]; then printf "COOLDOWN 効(skip)\n"; else printf "★COOLDOWN 抜け(通知が出る)★\n"; fi
printf "RESULT COOLDOWN_SEC=〔%s〕\n" "${COOLDOWN_SEC}"
