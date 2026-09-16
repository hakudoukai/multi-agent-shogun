#!/usr/bin/env bash
# 51 — ★「0 は無制限」は憶測にせず測る★
#   gtimeout 0 は「限り無し」か、「即時に断つ」か。sleep 2 を包んで見分ける。
#   限り無し => rc=0 かつ 経過≒2s ／ 即断 => rc=124 かつ 経過≒0s
set -u
GT="$(command -v gtimeout)"
run(){
  t0=$(python3 -c 'import time;print(time.time())')
  "$GT" "$1" sleep 2 >/dev/null 2>&1; rc=$?
  t1=$(python3 -c 'import time;print(time.time())')
  el=$(python3 -c "print(f'{$t1-$t0:.2f}')")
  printf '%s\tgtimeout %-22s\trc=%s\t経過=%ss\t%s\n' "$2" "[$1]" "$rc" "$el" "$3"
}
run 1   陽性対照 "★1秒で断つ筈★"
run 3   陰性対照 "★断たぬ筈(2s<3s)★"
run 0   形08     "★番人が受けた値★"
run 007 形16     "番人が受けた値"
run 010 形17     "番人が受けた値"
run 9223372036854775807 形18 "番人が受けた値"
