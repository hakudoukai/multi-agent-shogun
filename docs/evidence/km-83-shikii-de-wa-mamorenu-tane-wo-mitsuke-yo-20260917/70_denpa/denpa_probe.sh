#!/bin/bash
# 甲 L52 の env 渡しで、親の毒が子へ渡るかを一形ずつ測る。
BA="$(cd "$(dirname "$0")/ba" && pwd)"
rm -f "$BA/sv.log" "$BA/sv.lock"
PATH="$(cd "$(dirname "$0")/bin" && pwd):$PATH" timeout 12 bash "$(dirname "$0")/kou_supervisor_denpa.sh" >/dev/null 2>&1
rc=$?
grep '^子が受けた' "$BA/sv.log" 2>/dev/null | tr '\n' '|'
printf ' sv_rc=%s\n' "$rc"
