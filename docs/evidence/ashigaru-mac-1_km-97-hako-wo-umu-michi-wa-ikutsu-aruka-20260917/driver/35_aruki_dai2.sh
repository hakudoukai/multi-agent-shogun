#!/bin/bash
# 35_aruki_dai2.sh ―― 第二歩き。器の根(scripts/ lib/ shim/ .claude/ 直下の .sh .py .json, ~/bin 深さ1, ~/hermes-departments-mac/bin, ~/hermes-departments-mac/*/bin)
# で 字 'inbox'(大小無視) を持つ file のうち、第一歩き(queue/inbox|inbox_write)で拾へなかつた物 = 変数で path を組む丁候補。
OUT="$1"; G=/usr/bin/grep
{ find scripts lib shim .claude -type f \( -name '*.sh' -o -name '*.py' -o -name '*.json' -o -name '*.bash' \) -not -path '*/worktrees/*' -print0
  find "$HOME/bin" -maxdepth 1 -type f -print0
  find "$HOME/hermes-departments-mac/bin" "$HOME"/hermes-departments-mac/*/bin -maxdepth 1 -type f -print0 2>/dev/null
} > "$OUT/35_files.nul"
tr -cd '\0' < "$OUT/35_files.nul" | wc -c | tr -d ' ' > "$OUT/35_files_count.txt"
xargs -0 $G -l -i -F 'inbox' < "$OUT/35_files.nul" | sort > "$OUT/35_hits_inbox_any.txt"; echo "grep_rc=$?" > "$OUT/35_rc.txt"
xargs -0 $G -l -E 'queue/inbox|inbox_write' < "$OUT/35_files.nul" | sort > "$OUT/35_hits_first.txt"; echo "grep2_rc=$?" >> "$OUT/35_rc.txt"
comm -23 "$OUT/35_hits_inbox_any.txt" "$OUT/35_hits_first.txt" > "$OUT/35_tei_kouho.txt"
printf 'files=%s any=%s first=%s tei_kouho=%s\n' "$(cat "$OUT/35_files_count.txt")" "$($G -c '' "$OUT/35_hits_inbox_any.txt")" "$($G -c '' "$OUT/35_hits_first.txt")" "$($G -c '' "$OUT/35_tei_kouho.txt")" | tee "$OUT/35_summary.txt"; cat "$OUT/35_rc.txt"
