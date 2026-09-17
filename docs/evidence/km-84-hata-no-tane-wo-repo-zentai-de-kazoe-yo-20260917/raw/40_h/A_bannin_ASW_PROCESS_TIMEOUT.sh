#!/bin/bash
# 陽性A の写し器 ―― 番人付き(定義三本は disk の inbox_watcher.sh 494c8c788d50d724 から逐語)
_th_say(){ printf '%s\n' "[watcher] $*" >&2; }
# ★甲 ―― 閾は「比較に使ふのと同じ演算子」で検めよ(裁 seq322952・横展開 裁 seq323062)★
#   舊 is_num は case の字面判定ゆゑ 99999999999999999999 を「數」と呼ぶ。然し後段の
#   [ "$x" -ge "$閾" ] は其の値で ★rc=2★ に倒れ、if も elif も偽＝★黙つて既定の枝へ落ちる★。
#   ∴ 検める器と使ふ器を同じ演算子に揃へる。
num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }
# ★乙 ―― 未設定/空文字/空白のみ を分けて名指す(裁 seq322952)★
#   ${x+set} は空文字でも set を返す ∴ 未設定と空文字は此処でのみ分かれる。
env_state(){
  eval "_es_set=\"\${$1+set}\"; _es_v=\"\${$1-}\""
  if [ -z "${_es_set}" ]; then printf 'unset\n'
  elif [ -z "${_es_v}" ]; then printf 'empty\n'
  elif [ -z "$(printf '%s' "${_es_v}" | tr -d '[:space:]')" ]; then printf 'blank\n'
  else printf 'value\n'; fi
}
env_state(){
  eval "_es_set=\"\${$1+set}\"; _es_v=\"\${$1-}\""
  if [ -z "${_es_set}" ]; then printf 'unset\n'
  elif [ -z "${_es_v}" ]; then printf 'empty\n'
  elif [ -z "$(printf '%s' "${_es_v}" | tr -d '[:space:]')" ]; then printf 'blank\n'
  else printf 'value\n'; fi
}
fix_flag(){
  _fg_n="$1"; _fg_d="$2"; _fg_o="$3"; _fg_s="$(env_state "$_fg_n")"; eval "_fg_v=\"\${$_fg_n-}\""
  case "$_fg_s" in
    unset)
      if [ "${_th_unset_told:-0}" -eq 0 ]; then
        _th_say "★旗/閾 未設定 ―― 既定へ倒す(${_fg_n}=${_fg_d}) ／ 本 process の未設定の報せは★此の一度のみ★(裁 seq323687⑵)★"
        _th_unset_told=1
      fi
      eval "$_fg_o=\$_fg_d"; return 0 ;;
    empty) _th_say "★旗 ${_fg_n} が空文字 ―― 既定 ${_fg_d} へ倒す(fail-closed)★"; eval "$_fg_o=\$_fg_d"; return 0 ;;
    blank) _th_say "★旗 ${_fg_n} が空白のみ ―― 既定 ${_fg_d} へ倒す(fail-closed)★"; eval "$_fg_o=\$_fg_d"; return 0 ;;
  esac
  case "$_fg_v" in
    0|1) eval "$_fg_o=\$_fg_v"; return 0 ;;
  esac
  # ★行注入の封じ(乙・裁 seq323980⑵)★ 印が既在なら値を刷らず倒す(fail-closed)
  case "$_fg_v" in
    *␊*|*␍*|*␉*) _th_say "★旗 ${_fg_n} が可視印(␊␍␉)を既に含む ―― 値を刷らず既定 ${_fg_d} へ倒す(fail-closed・裁 seq323980⑵)★"; eval "$_fg_o=\$_fg_d"; return 0 ;;
  esac
  _fg_vp="${_fg_v//$'\n'/␊}"; _fg_vp="${_fg_vp//$'\r'/␍}"; _fg_vp="${_fg_vp//$'\t'/␉}"
  _th_say "★旗 ${_fg_n} は 0|1 の外(「${_fg_vp}」) ―― 既定 ${_fg_d} へ倒す(fail-closed)★"
  eval "$_fg_o=\$_fg_d"
}
fix_flag ASW_PROCESS_TIMEOUT 1 ASW_PROCESS_TIMEOUT
if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then printf 'BRANCH=then\n'; else printf 'BRANCH=else\n'; fi
