#!/bin/bash
# ★読取のみ・信号 0★ ―― 稼働中の watcher が開く inode と disk の inode を突き合はせる。
#   目的= 「repo を直した」と「稼働中の器が直つた」は別物である事を數で示す(裁 seq323062⑷)。
R=${1:-../../..}
F="$R/scripts/inbox_watcher.sh"
printf 'disk\tinode=%s\tbytes=%s\tsha16=%s\n' \
  "$(stat -f '%i' "$F")" "$(stat -f '%z' "$F")" "$(shasum -a256 "$F" | cut -c1-16)"
N=0
for p in $(pgrep -f 'inbox_watcher\.sh' 2>/dev/null); do
  N=$((N+1))
  L=$(ps -o lstart= -p "$p" 2>/dev/null | tr -s ' ')
  I=$(lsof -p "$p" 2>/dev/null | grep 'inbox_watcher\.sh' | awk '{print $(NF-1)"/"$NF}' | head -1)
  printf 'pid=%s\t起動=%s\t開いて居る=%s\n' "$p" "$L" "${I:-★讀めず★}"
done
printf '稼働本数=%d\n' "$N"
