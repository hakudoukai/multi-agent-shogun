#!/bin/bash
# 30_gyou.sh ―― 器候補の逐語行(path:行番号)を抜く。pattern は 'queue/inbox|inbox_write|inbox_path|INBOX' (ERE・大文字小文字区別)。
# 用法: bash 30_gyou.sh <list> <出力file>
L="$1"; O="$2"; G=/usr/bin/grep; : > "$O"
while IFS= read -r f; do
  [ -f "$f" ] || { printf '### %s ★実体無★\n' "$f" >> "$O"; continue; }
  n=$($G -c -E 'queue/inbox|inbox_write|inbox_path|INBOX' "$f"); printf '### %s (hit行=%s)\n' "$f" "$n" >> "$O"
  $G -n -E 'queue/inbox|inbox_write|inbox_path|INBOX' "$f" | cut -c1-220 >> "$O"
done < "$L"
echo "files=$($G -c '^### ' "$O") lines=$($G -c '' "$O")"
