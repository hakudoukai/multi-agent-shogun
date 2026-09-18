#!/usr/bin/env bash
# km-188 陽性対照の種(己の束・器ではない)
n=$(cat /nonexistent | wc -l)
c=$(grep -c '' /nonexistent | tr -d ' ')
false | head -1
ls /nonexistent | sort -u
cat /nonexistent | wc -l
rc=$?
echo constant | wc -l
