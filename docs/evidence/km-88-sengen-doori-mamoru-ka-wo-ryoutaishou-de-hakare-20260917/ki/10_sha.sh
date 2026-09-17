#!/bin/bash
# 版を凍結し、走る器の inode/大きさを控へる。★読取のみ★。
# usage: (cd <束> && bash ki/10_sha.sh)
set -u
R=/Users/momizimac/multi-agent-shogun
echo "刻=$(date '+%Y-%m-%dT%H:%M:%S%z')"
echo "HEAD=$(git -C "$R" rev-parse HEAD)"
echo "-- 凍結した四版(束内 ki/) --"
for f in kyuu index shin hashiru_kouho; do
  p="ki/$f.sh"
  printf '%-16s sha16=%s bytes=%s lines=%s\n' "$f" "$(shasum -a 256 "$p" | cut -c1-16)" "$(wc -c < "$p" | tr -d ' ')" "$(wc -l < "$p" | tr -d ' ')"
done
echo "-- 生器(scripts/inbox_watcher.sh) 現況 --"
stat -f 'ino=%i bytes=%z mtime=%Sm' -t '%Y-%m-%dT%H:%M:%S' "$R/scripts/inbox_watcher.sh"
printf 'sha16=%s\n' "$(shasum -a 256 "$R/scripts/inbox_watcher.sh" | cut -c1-16)"
echo "-- 走つて居る watcher(自席 ashigaru-mac-3) が握る fd --"
pid="$(ps -eo pid,command | awk '/[i]nbox_watcher\.sh ashigaru-mac-3 /{print $1}')"
echo "pid=${pid:-★見えず★}"
if [ -n "${pid:-}" ]; then
  # ★lsof の列: 1=COMMAND 2=PID 3=USER 4=FD 5=TYPE 6=DEVICE 7=SIZE/OFF 8=NODE 9=NAME★
  #   (先に $6 を ino と名づけて "1,14"(=DEVICE) を刷つた ―― 名を値に合はせ直す)
  lsof -p "$pid" 2>/dev/null | awk '$4 ~ /^255/ {printf "fd=%s dev=%s bytes=%s ino=%s path=%s\n", $4, $6, $7, $8, $9}'
fi
echo "-- 走る器と disk の突合 --"
echo "(inode が違へば ★走る器は disk の直しを読んで居らぬ★)"
