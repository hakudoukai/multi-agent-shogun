# ─── 閾の番人(甲/乙) ───
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
  _th_say "★閾 ${_ft_n} を比較器が扱へぬ(「${_ft_v}」) ―― 既定 ${_ft_d} へ倒す(fail-closed)★"
  eval "$_ft_o=\$_ft_d"
}
# ★此の器だけは「黙る」形が0本、出目は悉く ★暴発★ か ★氾濫★ である(專任3 第40弾・裁 322099)。
#   殊に ESCALATE_PHASE1/2 が比較器で扱へぬと if も elif も偽 → ★else = Phase3★ へ落ち、
