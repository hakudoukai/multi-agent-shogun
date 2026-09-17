#!/bin/bash
# 便の器(第54弾) ―― 胴の紙を受け、★字数を測り★、300超は出さぬ(fail-closed)。
# 使ひ方(逐語・scripts/inbox_write.sh の usage より):
#   bash scripts/inbox_write.sh <target_agent> "<message>" <type> <from>
#   ∴ 宛先=argv[1] 胴=argv[2] ―― ★位置で受ける器★。名で渡すな。
set -u
PY=/opt/homebrew/bin/python3
R=/Users/momizimac/multi-agent-shogun
for f in "$@"; do
  n=$("$PY" -c 'import sys;print(len(open(sys.argv[1],encoding="utf-8").read().rstrip("\n")))' "$f")
  if [ "$n" -gt 300 ]; then echo "★300 超 ―― 出さぬ★ ${f}=${n}字"; exit 3; fi
  echo "字数 $f=$n"
done
for f in "$@"; do
  body=$("$PY" -c 'import sys;print(open(sys.argv[1],encoding="utf-8").read().rstrip("\n"),end="")' "$f")
  bash "$R/scripts/inbox_write.sh" karo-mac "$body" notification ashigaru-mac-2
  rc=$?
  echo "rc=$rc $f"
  [ "$rc" -eq 0 ] || exit "$rc"
done
