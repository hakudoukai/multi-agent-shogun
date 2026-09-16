#!/bin/bash
# 98_locale.sh ―― env_state の ★出目が locale で変る★ かを測る。
# 理: env_state は blank を `tr -d '[:space:]'` で判ずる。[:space:] の意味は locale に依る。
# usage: 98_locale.sh <抜いた番人.sh> <出し先.tsv>
# rc: 0=測れた / 2=引数の誤り  ★讀取のみ★
set -u
FN="${1:?usage: 98_locale.sh <抜いた番人.sh> <出し先.tsv>}"
OUT="${2:?usage: 98_locale.sh <抜いた番人.sh> <出し先.tsv>}"
{
  printf '# 値は ★U+3000(全角空白) 一つ★ = byte e3 80 80 ―― 一つの値・一つの番人\n'
  printf 'LC_ALL\t㋑env_state\ttr 後の byte 数\t門票に出る文言\n'
  for L in C.UTF-8 C en_US.UTF-8 ja_JP.UTF-8; do
    o="$(LC_ALL="$L" env KM49_T="$(printf '\xe3\x80\x80')" bash -c ". \"$FN\"; env_state KM49_T" 2>/dev/null)"
    n="$(LC_ALL="$L" printf '\xe3\x80\x80' | LC_ALL="$L" tr -d '[:space:]' | wc -c | tr -d ' ')"
    case "$o" in
      blank) moji='★閾 … が空白のみ ―― 既定へ倒す(fail-closed)★' ;;
      value) moji='★閾 … が比較器で扱へぬ(「　」) ―― 既定へ倒す(fail-closed)★' ;;
      *)     moji="(出目 $o)" ;;
    esac
    printf '%s\t%s\t%s\t%s\n' "$L" "${o:-★測れぬ★}" "$n" "$moji"
  done
  printf '# 判 = ★同じ値・同じ番人で ㋑ の出目が二つに割れる★(判は両方とも既定へ倒す故 実害は無い)\n'
} > "$OUT"
cat "$OUT"
