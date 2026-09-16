#!/usr/bin/env bash
# 40_kougo.sh — ★番人が受けた値を、後段の三つの讀手が同じ値と讀むか★
#   讀手甲 [ ] (test(1) 整数比較) / 讀手乙 $(( )) (bash 算術) / 讀手丙 python3 int()
#   ★甲は printf で覗くな(printf は別の讀手である)★ ―― 甲自身の -eq で候補へ当てて値を決める。
#   ★二分探索は使はぬ★: lo=-2^63 hi=2^63-1 では (hi-lo) が int64 を溢れ mid が壊れ、無限に廻る(實測)。
set -u
yomite_kou(){                      # 甲の値を [ -eq ] だけで決める
  v="$1"; shift
  [ "$v" -eq "$v" ] 2>/dev/null || { printf 'ERR(比較器が扱へぬ)'; return; }
  for cand in "$@"; do
    if [ "$v" -eq "$cand" ] 2>/dev/null; then printf '%s' "$cand"; return; fi
  done
  printf '候補外'
}
printf '#colspec\t形札\t逐語(改行は?)\t甲[ ]\t乙$(())\t丙python3\t一致?\n'
emit(){
  tag="$1"; v="$2"
  b="$( (echo "$((v))") 2>/dev/null || echo ERR )"
  c="$(KM52V="$v" /opt/homebrew/bin/python3 -B -c 'import os;print(int(os.environ["KM52V"]))' 2>/dev/null || echo ERR)"
  a="$(yomite_kou "$v" "$b" "$c" 0 7 8 10 50 -1 9223372036854775807)"
  if [ "$a" = "$b" ] && [ "$b" = "$c" ]; then u="一致"; else u="★割れ★"; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$tag" "$(printf '%s' "$v" | tr '\n' '?')" "$a" "$b" "$c" "$u"
}
emit 07 "-0"; emit 08 "0"; emit 09 "+50"; emit 10 " 50 "
emit 16 "007"; emit 17 "010"; emit 18 "9223372036854775807"
