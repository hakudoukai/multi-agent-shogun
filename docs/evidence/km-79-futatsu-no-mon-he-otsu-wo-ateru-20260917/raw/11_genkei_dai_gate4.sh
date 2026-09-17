#!/bin/bash
# ★台 ―― scripts/checks/karo_mac_gate4.sh から機械で切り出した(手写しに非ず)★
set -u
say(){ printf '%s\n' "$*" >&2; }
num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }

# ★乙(裁 seq322952)★ 未設定/空文字/空白のみ を ★分けて名指し★、既定へ倒す時は ★必ず刷る★。
#   旧形の `${VAR:-50}` は ★未設定と空文字を一つに混ぜ、黙つて既定へ倒して居た★。
#   註: 「空白のみ」は ASCII の空白類のみを見る(全角空白は value 側へ落ち、比較器が拒む)。
env_state(){
  eval "_es_set=\"\${$1+set}\"; _es_v=\"\${$1-}\""
  if [ -z "${_es_set}" ]; then printf 'unset\n'
  elif [ -z "${_es_v}" ]; then printf 'empty\n'
  elif [ -z "$(printf '%s' "${_es_v}" | tr -d '[:space:]')" ]; then printf 'blank\n'
  else printf 'value\n'; fi
}

# 閾を一本の道で定める ―― $1=変数名 $2=既定 $3=受け皿の変数名
fix_threshold(){
  local name="$1" dflt="$2" out="$3" st raw
  st="$(env_state "$name")"
  eval "raw=\"\${$name-}\""
  case "$st" in
    unset) say "閾 ${name} = 未設定 ―― 既定 ${dflt} を用ゐる(★倒した事を刷る★)"; eval "$out=\$dflt"; return 0 ;;
    empty) say "★閾 ${name} が空文字 ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
    blank) say "★閾 ${name} が空白のみ ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
  esac
  if num_same_op "$raw"; then eval "$out=\$raw"; return 0; fi
  say "★閾 ${name} が比較器で扱へぬ(「${raw}」) ―― 既定 ${dflt} へ倒す(fail-closed)★"
  eval "$out=\$dflt"
}

fix_threshold KM79_PROBE 50 OUT
printf %s\\n "${OUT}"
