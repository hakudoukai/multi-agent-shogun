#!/bin/bash
log(){ printf '%s\n' "$*" >&2; }
_th_say(){ printf '%s\n' "[watcher] $*" >&2; }
num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }
env_state(){
  eval "_es_set=\"\${$1+set}\"; _es_v=\"\${$1-}\""
  if [ -z "${_es_set}" ]; then printf 'unset\n'
  elif [ -z "${_es_v}" ]; then printf 'empty\n'
  elif [ -z "$(printf '%s' "${_es_v}" | tr -d '[:space:]')" ]; then printf 'blank\n'
  else printf 'value\n'; fi
}
fix_threshold(){
  _ft_n="$1"; _ft_d="$2"; _ft_o="$3"; _ft_s="$(env_state "$_ft_n")"; eval "_ft_v=\"\${$_ft_n-}\""
  case "$_ft_s" in
    unset)
      if [ "${_th_unset_told:-0}" -eq 0 ]; then
        _th_say "★閾 未設定 ―― 既定へ倒す(${_ft_n}=${_ft_d}) ／ 本 process の未設定の報せは★此の一度のみ★(裁 seq323687⑵)★"
        _th_unset_told=1
      fi
      eval "$_ft_o=\$_ft_d"; return 0 ;;
    empty) _th_say "★閾 ${_ft_n} が空文字 ―― 既定 ${_ft_d} へ倒す(fail-closed)★"; eval "$_ft_o=\$_ft_d"; return 0 ;;
    blank) _th_say "★閾 ${_ft_n} が空白のみ ―― 既定 ${_ft_d} へ倒す(fail-closed)★"; eval "$_ft_o=\$_ft_d"; return 0 ;;
  esac
  if num_same_op "$_ft_v" && [ "$_ft_v" -ge 0 ]; then eval "$_ft_o=\$_ft_v"; return 0; fi
  _ft_vp="$(printf '%q' "${_ft_v}")"  # 丙1: bash 組込 printf %q(可逆・ASCII のみ)
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
  eval "$_ft_o=\$_ft_d"
}

fix_threshold KM73_TH 99 KM73_OUT
printf "OUT=%s\n" "${KM73_OUT-（未設定）}"
