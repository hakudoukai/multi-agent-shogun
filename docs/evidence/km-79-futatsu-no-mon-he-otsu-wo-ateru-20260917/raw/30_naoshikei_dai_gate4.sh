#!/bin/bash
# ★台 ―― scripts/checks/karo_mac_gate4.sh から機械で切り出した(手写しに非ず)★
set -u
say(){ printf '%s\n' "$*" >&2; }
num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }

# ★乙(裁 seq322952)★ 未設定/空文字/空白のみ を ★分けて名指し★、既定へ倒す時は ★必ず刷る★。
#   旧形の `${VAR:-50}` は ★未設定と空文字を一つに混ぜ、黙つて既定へ倒して居た★。
#   註: 「空白のみ」は tr -d '[:space:]' で見る。★此の註は先に誤つて居た★ ――
#   「全角空白(U+3000)は value 側へ落ちる」と書いて在つたが、BSD tr は之を空白と讀む。
#   實測(km-79): printf '　' | tr -d '[:space:]' → ★空★ ∴ ④全角空白は ★blank 側★ へ落ちる。
env_state(){
  eval "_es_set=\"\${$1+set}\"; _es_v=\"\${$1-}\""
  if [ -z "${_es_set}" ]; then printf 'unset\n'
  elif [ -z "${_es_v}" ]; then printf 'empty\n'
  elif [ -z "$(printf '%s' "${_es_v}" | tr -d '[:space:]')" ]; then printf 'blank\n'
  else printf 'value\n'; fi
}

# 閾を一本の道で定める ―― $1=変数名 $2=既定 $3=受け皿の変数名
fix_threshold(){
  local name="$1" dflt="$2" out="$3" st raw vp
  st="$(env_state "$name")"
  eval "raw=\"\${$name-}\""
  case "$st" in
    unset) say "閾 ${name} = 未設定 ―― 既定 ${dflt} を用ゐる(★倒した事を刷る★)"; eval "$out=\$dflt"; return 0 ;;
    empty) say "★閾 ${name} が空文字 ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
    blank) say "★閾 ${name} が空白のみ ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
  esac
  if num_same_op "$raw"; then eval "$out=\$raw"; return 0; fi
  # ★乙 行注入の封じ(裁 seq323980⑵ ―― 兄弟器 scripts/redundancy/shogun_report_watcher.sh L63-69 と同形)★
  #   値は env 由来ゆゑ改行を含み得、★己の判定の道(stderr)へ偽の報せ行を一本生む★。
  #   實測(本器・km-79 raw/20・21): 現形は ⑦改行注入 で ★報せ行 2(期待1)・注入痕 1★ であつた。
  #   乙=可視印(␊␍␉)へ置換(UTF-8 正・fork 無し・bash 3.2 可)。甲(0xB6)は UTF-8 不正ゆゑ採らず。
  #   ★印の曖昧性★=値が元から印を含めば注入と區別できぬ ∴ 其の時は ★刷らずに★ 倒す(fail-closed)。
  case "$raw" in
    *␊*|*␍*|*␉*) say "★閾 ${name} が可視印(␊␍␉)を既に含む ―― 値を刷らず既定 ${dflt} へ倒す(fail-closed・裁 seq323980⑵)★"; eval "$out=\$dflt"; return 0 ;;
  esac
  vp="${raw//$'\n'/␊}"; vp="${vp//$'\r'/␍}"; vp="${vp//$'\t'/␉}"
  say "★閾 ${name} を比較器が扱へぬ(「${vp}」) ―― 既定 ${dflt} へ倒す(fail-closed)★"
  eval "$out=\$dflt"
}

fix_threshold KM79_PROBE 50 OUT
printf %s\\n "${OUT}"
