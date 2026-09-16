#!/bin/bash
# 97_jigen.sh ―― 閾が ★timeout(1) の語法★ で何と読まれるかを測る。
#
# 理: 番人(甲)は「後段の比較に使ふのと同じ演算子で検める」と言ふ。
#     然れど DASUMAE_READ_TIMEOUT の後段は ★[ -ge ] ではなく timeout(1)★ である。
#     二つの語法は一致せぬ ―― 其の差を実測で出す。
# usage: 97_jigen.sh <出し先.tsv>
# rc: 0=測れた / 2=引数の誤り
# ★讀取のみ。★
set -u
OUT="${1:?usage: 97_jigen.sh <出し先.tsv>}"
T="$(command -v timeout || command -v gtimeout)"
{
  printf '# timeout(1) の語法 ―― 器 %s\n' "$T"
  printf '# 版 %s\n' "$("$T" --version 2>&1 | head -1)"
  printf '閾\ttimeout の rc\t経た秒\t読まれ方\n'
  for v in 10 0 -1 -0 " 50 " 007 9223372036854775807 10m; do
    s=$(date +%s)
    "$T" "$v" sleep 2 >/dev/null 2>&1; rc=$?
    e=$(( $(date +%s) - s ))
    case "$rc" in
      0)   yomi="通つた(2秒の眠りが最後まで走つた)" ;;
      124) yomi="★時限が効いた(打ち切り)★" ;;
      125) yomi="★timeout が拒んだ(語法外)★" ;;
      *)   yomi="rc=$rc" ;;
    esac
    printf '「%s」\t%s\t%s\t%s\n' "$v" "$rc" "$e" "$yomi"
  done
  printf '# 註 時限が効くか否かは 2 秒の眠りに 1 秒未満の閾を当てねば見えぬ ―― 下段で別に測る\n'
  for v in 1 0; do
    s=$(date +%s); "$T" "$v" sleep 3 >/dev/null 2>&1; rc=$?; e=$(( $(date +%s) - s ))
    printf '「%s」(3秒の眠りへ)\t%s\t%s\t%s\n' "$v" "$rc" "$e" \
      "$([ "$rc" = 124 ] && printf '★時限 効く★' || printf '★時限 無し ―― 最後まで走つた★')"
  done
} > "$OUT"
cat "$OUT"
