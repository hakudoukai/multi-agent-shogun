#!/bin/bash
# ★陰性対照★ 一形も無い(字で切る器のみ)
echo "$v" | /opt/homebrew/bin/python3 -c 'import sys;print(sys.stdin.read()[:40])'
printf '%s\n' "$v"
echo "${v}"
