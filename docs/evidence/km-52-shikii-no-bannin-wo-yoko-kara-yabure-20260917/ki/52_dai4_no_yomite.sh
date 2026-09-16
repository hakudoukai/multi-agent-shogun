#!/usr/bin/env bash
# 52 — ★第四の讀手 gtimeout は 010 を幾つと讀むか★
#   [ ]=10 / $(( ))=8 / python int()=10 は既に測つた。gtimeout は?
#   sleep 9 を包む: 限り10 なら断たず(rc=0,≒9s)、限り8 なら断つ(rc=124,≒8s)
set -u
GT="$(command -v gtimeout)"
run(){
  t0=$(python3 -c 'import time;print(time.time())')
  "$GT" "$1" sleep "$2" >/dev/null 2>&1; rc=$?
  t1=$(python3 -c 'import time;print(time.time())')
  printf 'gtimeout %-5s sleep %-2s\trc=%s\t経過=%ss\t%s\n' "$1" "$2" "$rc" \
    "$(python3 -c "print(f'{$t1-$t0:.2f}')")" "$3"
}
run 010 9 "★8 と讀めば断つ・10 と讀めば断たぬ★"
run 007 9 "★7 と讀めば断つ・07=7 は八進でも十進でも同値ゆゑ判別に非ず★"
run 8   9 "陽性対照(8秒で断つ筈)"
