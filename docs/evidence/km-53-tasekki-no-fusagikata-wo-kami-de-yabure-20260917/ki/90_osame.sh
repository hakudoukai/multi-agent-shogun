#!/bin/bash
# usage: 90_osame.sh <束> <便の胴file>
# inbox_write.sh の usage 逐語(scripts/inbox_write.sh 冠より):
#   通常 (argv 経由): bash scripts/inbox_write.sh <target_agent> <content> <type> <from>
# ∴ 宛先 argv[1] / 胴 argv[2] / 型 argv[3] / 差出 argv[4]。★胴の位置を違へぬ事★(第51弾の疵)。
set -u
B="$1"; BODY="$2"; R="$(cd "$(dirname "$0")/.." && pwd)"
N=$(/opt/homebrew/bin/python3 -c "import io,sys;print(len(io.open(sys.argv[1],encoding='utf-8').read().rstrip(chr(10))))" "$BODY")
echo "字=$N" | tee "${BODY%.txt}.ji.txt"
date '+%Y-%m-%dT%H:%M:%S%z' > "${BODY%.txt}.koku.txt"
rc=0
bash /Users/momizimac/multi-agent-shogun/scripts/inbox_write.sh karo-mac \
  "$(cat "$BODY")" report_received ashigaru-mac-2 > "${BODY%.txt}.out.txt" 2>&1 || rc=$?
echo "$rc" > "${BODY%.txt}.rc"
echo "rc=$rc"
