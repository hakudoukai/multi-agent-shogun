#!/usr/bin/env bash
set -euo pipefail
COOLDOWN_SEC="${SHOGUN_REPORT_WATCHER_COOLDOWN:-60}"
is_num(){ case "${1:-}" in (''|*[!0-9]*) return 1 ;; (*) return 0 ;; esac }
is_num "${COOLDOWN_SEC}" || { printf '%s\n' "[shogun_report_watcher] ★閾 COOLDOWN_SEC が數でない(「${COOLDOWN_SEC}」) ―― 既定 60 へ倒す(fail-closed)★" >&2; COOLDOWN_SEC=60; }
diff=0
if [ "$diff" -lt "$COOLDOWN_SEC" ]; then printf "COOLDOWN 効(skip)\n"; else printf "★COOLDOWN 抜け(通知が出る)★\n"; fi
printf "RESULT COOLDOWN_SEC=〔%s〕\n" "${COOLDOWN_SEC}"
