#!/bin/bash
# 15_aruki_R5.sh ―― 第五の根 ~/hermes-departments-mac(稼働 process の写し 20_ps_hits で見えた) を歩く。
# prune: .git venv .venv node_modules __pycache__ site-packages
OUT="$1"; G=/usr/bin/grep; R="$HOME/hermes-departments-mac"
date '+%Y-%m-%dT%H:%M:%S%z' > "$OUT/15_aruki_R5_toki.txt"
[ -d "$R" ] || { echo "R5 根 無し: $R" | tee "$OUT/15_R5_missing.txt"; exit 3; }
find "$R" \( -name .git -o -name venv -o -name .venv -o -name node_modules -o -name __pycache__ -o -name site-packages \) -prune -o -type f -print0 > "$OUT/15_R5_files.nul"; echo "R5_find_rc=$?" > "$OUT/15_aruki_R5_rc.txt"
tr -cd '\0' < "$OUT/15_R5_files.nul" | wc -c | tr -d ' ' > "$OUT/15_R5_files_count.txt"
xargs -0 $G -l -F -e 'queue/inbox' -e 'inbox_write' < "$OUT/15_R5_files.nul" > "$OUT/15_R5_hits.txt" 2> "$OUT/15_R5_hits.err"; echo "R5_grep_rc=$?" >> "$OUT/15_aruki_R5_rc.txt"
printf 'R5 hits=%s of files=%s\n' "$($G -c '' "$OUT/15_R5_hits.txt")" "$(cat "$OUT/15_R5_files_count.txt")" | tee "$OUT/15_aruki_R5_summary.txt"; cat "$OUT/15_aruki_R5_rc.txt"
