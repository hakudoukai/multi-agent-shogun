#!/bin/bash
# 10_aruki.sh ―― 路の母數を歩く器。字 'queue/inbox' 又は 'inbox_write' を持つ file を根ごとに列べる。
# 用法: bash 10_aruki.sh <出力dir>   (repo 直下で呼ぶ)
# 根と深さ: R1=repo(-type f, .git/ queue/ logs/ node_modules/ を prune・★prune した事は此処に宣す★)
#           R2=~/bin(深さ1)  R3=~/.claude(深さ3)  R4=~/Library/LaunchAgents(深さ1)
OUT="$1"; [ -d "$OUT" ] || { echo "出力dir 無し" >&2; exit 2; }
G=/usr/bin/grep   # ★ugrep(.gitignore を読む)を避け BSD grep を名指す★
date '+%Y-%m-%dT%H:%M:%S%z' > "$OUT/10_aruki_toki.txt"
# R1 repo
find . \( -path ./.git -o -path ./queue -o -path ./logs -o -path ./node_modules \) -prune -o -type f -print0 \
  > "$OUT/10_R1_files.nul"; echo "R1_find_rc=$?" >> "$OUT/10_aruki_rc.txt"
tr -cd '\0' < "$OUT/10_R1_files.nul" | wc -c | tr -d ' ' > "$OUT/10_R1_files_count.txt"
xargs -0 $G -l -F -e 'queue/inbox' -e 'inbox_write' < "$OUT/10_R1_files.nul" > "$OUT/10_R1_hits.txt" 2> "$OUT/10_R1_hits.err"; echo "R1_grep_rc=$?" >> "$OUT/10_aruki_rc.txt"
# R2 ~/bin
find "$HOME/bin" -maxdepth 1 -type f -print0 > "$OUT/10_R2_files.nul"; echo "R2_find_rc=$?" >> "$OUT/10_aruki_rc.txt"
tr -cd '\0' < "$OUT/10_R2_files.nul" | wc -c | tr -d ' ' > "$OUT/10_R2_files_count.txt"
xargs -0 $G -l -F -e 'queue/inbox' -e 'inbox_write' < "$OUT/10_R2_files.nul" > "$OUT/10_R2_hits.txt" 2> "$OUT/10_R2_hits.err"; echo "R2_grep_rc=$?" >> "$OUT/10_aruki_rc.txt"
# R3 ~/.claude (projects/ は session jsonl ゆゑ prune)
find "$HOME/.claude" -maxdepth 3 \( -path "$HOME/.claude/projects" \) -prune -o -type f -print0 > "$OUT/10_R3_files.nul"; echo "R3_find_rc=$?" >> "$OUT/10_aruki_rc.txt"
tr -cd '\0' < "$OUT/10_R3_files.nul" | wc -c | tr -d ' ' > "$OUT/10_R3_files_count.txt"
xargs -0 $G -l -F -e 'queue/inbox' -e 'inbox_write' < "$OUT/10_R3_files.nul" > "$OUT/10_R3_hits.txt" 2> "$OUT/10_R3_hits.err"; echo "R3_grep_rc=$?" >> "$OUT/10_aruki_rc.txt"
# R4 LaunchAgents
find "$HOME/Library/LaunchAgents" -maxdepth 1 -type f -print0 > "$OUT/10_R4_files.nul"; echo "R4_find_rc=$?" >> "$OUT/10_aruki_rc.txt"
tr -cd '\0' < "$OUT/10_R4_files.nul" | wc -c | tr -d ' ' > "$OUT/10_R4_files_count.txt"
xargs -0 $G -l -F -e 'queue/inbox' -e 'inbox_write' -e 'inbox_watcher' < "$OUT/10_R4_files.nul" > "$OUT/10_R4_hits.txt" 2> "$OUT/10_R4_hits.err"; echo "R4_grep_rc=$?" >> "$OUT/10_aruki_rc.txt"
# 陽性対照: 門 其の物が R1 の hits に在るか(同じ器 $G で)
$G -c -F 'scripts/inbox_write.sh' "$OUT/10_R1_hits.txt" > "$OUT/10_R1_positive_control.txt"; echo "R1_pc_rc=$?" >> "$OUT/10_aruki_rc.txt"
for r in R1 R2 R3 R4; do printf '%s hits=%s of files=%s\n' $r "$($G -c '' "$OUT/10_${r}_hits.txt")" "$(cat "$OUT/10_${r}_files_count.txt")"; done > "$OUT/10_aruki_summary.txt"
cat "$OUT/10_aruki_summary.txt" "$OUT/10_aruki_rc.txt"
