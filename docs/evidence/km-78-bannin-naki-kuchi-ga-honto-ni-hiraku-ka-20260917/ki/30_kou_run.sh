#!/bin/bash
# 30 甲の走り(第56弾 km-78 ㋐㋒㋓)
# 8形 × 二つの stdin 相(閉=EOF即時 / 不達=時限切れを誘ふ)を ★写し★ へ与へる。生器は呼ばぬ。
# ★不達相★ は process substitution `< <(sleep 12)` で作る ―― 初走は `sleep 30 |` で
#   殻が書き手を待ち 一走 30 秒を費した(出目は同じだが 8 分を無駄にした)。
# ★蓋★ 各走を perl alarm 8 秒で切る。SIGALRM で果てれば rc=142(128+14)。
#   蓋に SIGKILL を使はぬ ―― DD-169 の番人が塞ぐゆゑ(★之も本弾が実地で当てた番人の一つ★)。
# ★陽性対照★ = 5正常値1 × 不達。此処で「時限切れ」の一行が出なければ器が壊れて居る。
set -u
B="$1"; H="$B/utsushi/kou_harness.sh"
TWENTY='99999999999999999999'   # 20桁(符号付 64bit の上限 9223372036854775807=19桁 を超える)
cap(){ perl -e 'alarm 8; exec @ARGV' -- "$@"; }
printf 'form\tstdin\trc\twall_s\tkeigo\tstderr_1\tstdout_1\n'
run(){
  local lab="$1" mode="$2"; shift 2
  local t0=$SECONDS o e rc
  o=$(mktemp); e=$(mktemp)
  if [ "$mode" = 閉 ]; then
    env "$@" "$0.cap" "$H" >"$o" 2>"$e" </dev/null; rc=$?
  else
    env "$@" "$0.cap" "$H" >"$o" 2>"$e" < <(sleep 12); rc=$?
  fi
  local el=$(( SECONDS - t0 )) keigo=無
  grep -q '時限切れ' "$e" && keigo=★有★
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$lab" "$mode" "$rc" "$el" "$keigo" \
    "$(head -1 "$e" | tr '\n' ' ' | cut -c1-58)" "$(head -1 "$o" | tr '\n' ' ' | cut -c1-58)"
  rm -f "$o" "$e"
}
for mode in 閉 不達; do
  run 1未設定     "$mode" __X=1
  run 2空文字     "$mode" STOP_HOOK_STDIN_TIMEOUT=
  run 3空白のみ   "$mode" 'STOP_HOOK_STDIN_TIMEOUT= '
  run 4二十桁     "$mode" STOP_HOOK_STDIN_TIMEOUT="$TWENTY"
  run 5正常値1    "$mode" STOP_HOOK_STDIN_TIMEOUT=1
  run 6負数       "$mode" STOP_HOOK_STDIN_TIMEOUT=-5
  run 7改行入り   "$mode" "STOP_HOOK_STDIN_TIMEOUT=1
2"
  run 8既存␊     "$mode" STOP_HOOK_STDIN_TIMEOUT='1␊2'
done
