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
# 閾を一本の道で定める ―― $1=環境変数名 $2=既定 $3=受け皿の変数名
#   ★乙′(高頻度器の例外・家老mac 申告)★: 未設定＝既定 は本器の★設計上の常態★ゆゑ黙る。
#   逐回鳴らせば起動毎/prompt 毎の空鳴り＝氾濫(本器の旧註と同旨)。★異常の三形★
#   (空文字・空白のみ・比較器で扱へぬ)は必ず鳴る。門(低頻度器)では四形悉く刷る。
fix_threshold(){
  _ft_n="$1"; _ft_d="$2"; _ft_o="$3"; _ft_s="$(env_state "$_ft_n")"; eval "_ft_v=\"\${$_ft_n-}\""
  case "$_ft_s" in
    unset) eval "$_ft_o=\$_ft_d"; return 0 ;;
    empty) _th_say "★閾 ${_ft_n} が空文字 ―― 既定 ${_ft_d} へ倒す(fail-closed)★"; eval "$_ft_o=\$_ft_d"; return 0 ;;
    blank) _th_say "★閾 ${_ft_n} が空白のみ ―― 既定 ${_ft_d} へ倒す(fail-closed)★"; eval "$_ft_o=\$_ft_d"; return 0 ;;
  esac
  if num_same_op "$_ft_v" && [ "$_ft_v" -ge 0 ]; then eval "$_ft_o=\$_ft_v"; return 0; fi
  _ft_vp="$(printf '%s' "${_ft_v}" | tr '\n\r\t' '\266\215\211')"  # ★行注入封じ: 改行/復帰/TAB を可視印へ均す(判定は不変・表示のみ)★
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_vp}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
  eval "$_ft_o=\$_ft_d"
}
