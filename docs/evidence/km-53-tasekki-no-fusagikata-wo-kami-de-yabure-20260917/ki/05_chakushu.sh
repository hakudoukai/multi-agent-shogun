#!/bin/bash
# usage: 05_chakushu.sh <body-file> <outdir>
#   ★呼ぶ前に inbox_write.sh の usage を引いて argv の数と位置を照らす(本弾の題)★
#   inbox_write.sh usage(逐語 L4): bash scripts/inbox_write.sh <target_agent> <content> <type> <from>
set -u
bodyf="${1:?usage: 05_chakushu.sh <body-file> <outdir>}"
outdir="${2:?usage: 05_chakushu.sh <body-file> <outdir>}"
R=/Users/momizimac/multi-agent-shogun
body="$(cat "$bodyf")"
# 字数(字=python len・byte に非ず)
/opt/homebrew/bin/python3 -c 'import sys;print("ji="+str(len(open(sys.argv[1],encoding="utf-8").read().rstrip("\n"))))' "$bodyf" > "$outdir/05_ji.txt"
date '+%Y-%m-%dT%H:%M:%S%z' > "$outdir/05_koku.txt"
rc=0
bash "$R/scripts/inbox_write.sh" karo-mac "$body" report_received ashigaru-mac-2 > "$outdir/05_send.out" 2> "$outdir/05_send.err" || rc=$?
echo "$rc" > "$outdir/05_send.rc"
echo "rc=$rc"
