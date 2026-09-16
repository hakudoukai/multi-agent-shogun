#!/bin/bash
# 納め便を出す器。★臺帳の凍結前に書く★(作法⑷・當席の控へ)。
# usage 逐語(scripts/inbox_write.sh:6-8 より):
#   Usage: inbox_write.sh <target_agent> <content> [type] [from]
#   Example: inbox_write.sh karo "cmd_048を書いた。実行せよ。" cmd_new shogun
# ∴ ★宛先は argv[1]・胴は argv[2]★(位置で受ける器 ―― 胴の位置へ宛先を置くと宛先が胴に成る)
set -u
cd /Users/momizimac/multi-agent-shogun || exit 9
D=docs/evidence/km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917/_bin
P=/opt/homebrew/bin/python3
echo "=== 送る前の刻 ==="; date '+%Y-%m-%dT%H:%M:%S%z'
for i in 1 2 3 4 5 6 7; do
  f="$D/90_osame_$i.txt"
  n="$("$P" -c "import sys;print(len(open(sys.argv[1],encoding='utf-8').read().rstrip(chr(10))))" "$f")"
  if [ "$n" -gt 300 ]; then echo "★$i 便 $n 字 ―― 300 條 超ゆ。出さぬ(fail-closed)★" >&2; exit 3; fi
  body="$("$P" -c "import sys;sys.stdout.write(open(sys.argv[1],encoding='utf-8').read().rstrip(chr(10)))" "$f")"
  bash scripts/inbox_write.sh karo-mac "$body" report_received ashigaru-mac-2
  rc=$?   # ★管を通すな★(rc は直後に取る)
  echo "便 $i/7 字数=$n rc=$rc"
  [ "$rc" -ne 0 ] && { echo "★rc 非零 ―― 以降を出さぬ★" >&2; exit "$rc"; }
done
echo "=== 送つた後の刻 ==="; date '+%Y-%m-%dT%H:%M:%S%z'
