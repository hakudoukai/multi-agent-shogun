#!/usr/bin/env bash
# km-187 陽性対照の種(己の束・器ではない)
n=$(git show HEAD:nonexistent 2>&1 | grep -c '')
m=$(ls /nonexistent 2>&1 | wc -l)
out="$(some_cmd 2>&1)"; [ "$out" = "x" ] && echo same
sort_u=$(cat a b 2>&1 | sort -u | wc -l)
plain=$(echo hi 2>&1)
