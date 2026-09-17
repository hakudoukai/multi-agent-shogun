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
  # ★行注入の封じ(裁 seq323980⑵)★ 値は env 由来ゆゑ改行を含み得、偽の log 行を一本生む。
  #   乙=可視印へ置換(UTF-8 正・fork 無し・bash 3.2 で可)。甲(tr 0xB6)は UTF-8 不正ゆゑ採らず。
  #   ★印の曖昧性★=値が元から印を含めば注入と区別できぬ ∴ 其の時は刷らずに倒す(fail-closed)。
  case "$_ft_v" in
    *␊*|*␍*|*␉*) _th_say "★閾 ${_ft_n} が可視印(␊␍␉)を既に含む ―― 値を刷らず既定 ${_ft_d} へ倒す(fail-closed・裁 seq323980⑵)★"; eval "$_ft_o=\$_ft_d"; return 0 ;;
  esac
  _ft_vp="${_ft_v//$'\n'/␊}"; _ft_vp="${_ft_vp//$'\r'/␍}"; _ft_vp="${_ft_vp//$'\t'/␉}"
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
  eval "$_ft_o=\$_ft_d"
}
fix_threshold ASW_PROCESS_TIMEOUT 1 ASW_PROCESS_TIMEOUT; printf "FT_RC=%s\n" "$?"
if [ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; then
  printf "BRANCH=timeout_process\n"
else
  printf "BRANCH=event_only\n"
fi
[ "${ASW_PROCESS_TIMEOUT:-1}" = "1" ]; printf "TEST_RC=%s\n" "$?"
printf "VALUE=[%s]\n" "${ASW_PROCESS_TIMEOUT-<unset>}"
