#!/bin/sh
# 10_bosuu.txt に記した sha256 と、今の disk の sha256 を突き合はせる（読むのみ）。origin/main 版は git の blob からも取る。
date '+# 刻 %Y-%m-%dT%H:%M:%S%z'
grep -E '^/[^ ]+ lines=[0-9]+ sha256=[0-9a-f]{64}$' "$(dirname "$0")/10_bosuu.txt" | while read -r p l s; do
  now=$(shasum -a 256 "$p" | cut -d' ' -f1)
  [ "$now" = "${s#sha256=}" ] && echo "同 $p" || echo "★違 $p rec=${s#sha256=} now=$now"
done
echo "origin/main b9573b2d:scripts/inbox_write.sh sha256=$(git -C /Users/momizimac/wt/a1-km200b show b9573b2d:scripts/inbox_write.sh | shasum -a 256 | cut -d' ' -f1)"
