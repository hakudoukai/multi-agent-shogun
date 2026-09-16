#!/bin/bash
# 91_ichi.sh ―― 閾 一形 を ★生器から抜いた番人★ に当てる(當てるだけ・書かぬ)。
#
# usage: bash 91_ichi.sh <抜いた函數の file> <変数名>
#   stdout: <env_state の出目>\t<num_same_op の rc>\t<num_same_op の判>
#   ★源は生器★ ―― 函數は karo_mac_gate4.sh / karo_mac_dasumae_gate.sh から
#   ★逐語で抜いた物★ を source する(書き写しではない・裁「己が走らす版を讀め」)。
set -u
FN="${1:?usage: 91_ichi.sh <fn.sh> <VARNAME>}"
VAR="${2:?usage: 91_ichi.sh <fn.sh> <VARNAME>}"
. "$FN"
st="$(env_state "$VAR")"
eval "raw=\"\${$VAR-}\""
num_same_op "$raw"; nrc=$?
if [ $nrc -eq 0 ]; then han='通(閾として使ふ)'; else han='拒(既定へ倒す)'; fi
printf '%s\t%s\t%s\n' "$st" "$nrc" "$han"
