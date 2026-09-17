#!/bin/bash
# km-91 _after/12 ―― `read -t <v>` を ★生器の形そのまま★(IFS= read -r -d '' -t v INPUT)で単体に叩く。
#   之は「比較器を通つた値が、其の先で何を起こすか」を見る為の器。
set -u
J='{"stop_hook_active": true}'
one(){ # $1=札 $2=timeout値 $3=供給の形(pipe|file|slowpipe)
  local tag="$1" t="$2" how="$3" rc len err tmp
  err=$(mktemp); tmp=$(mktemp); printf '%s' "$J" > "$tmp"
  INPUT=""
  case "$how" in
    pipe)     { printf '%s' "$J" | { IFS= read -r -d '' -t "$t" INPUT; rc=$?; echo "$rc:${#INPUT}"; } ; } 2>"$err" ;;
    file)     { { IFS= read -r -d '' -t "$t" INPUT < "$tmp"; rc=$?; echo "$rc:${#INPUT}"; } ; } 2>"$err" ;;
    slowpipe) { { sleep 0.3; printf '%s' "$J"; } | { sleep 0.5; IFS= read -r -d '' -t "$t" INPUT; rc=$?; echo "$rc:${#INPUT}"; } ; } 2>"$err" ;;
  esac > /tmp/km91_$$.r
  local r; r=$(cat /tmp/km91_$$.r); rc=${r%%:*}; len=${r##*:}
  printf '%-22s 供給=%-9s rc=%-3s 讀めた字数=%-3s stderr=%s\n' "$tag" "$how" "$rc" "$len" "$(tr '\n' '|' < "$err")"
  rm -f "$err" "$tmp" /tmp/km91_$$.r
}
echo "# bash=$(/bin/bash --version|head -1)  供給する JSON は ${#J} 字"
echo "# 註: -d '' ゆゑ NUL 迄讀む＝JSON に NUL は無い故 rc≠0(EOF)が正常。★見るべきは rc でなく『讀めた字数』★"
for t in 10 1 0 -1 -5 010; do
  one "read -t $t" "$t" pipe
  one "read -t $t" "$t" file
done
one "read -t 0 (遅れて来る)" 0 slowpipe
one "read -t 10 (遅れて来る)" 10 slowpipe
