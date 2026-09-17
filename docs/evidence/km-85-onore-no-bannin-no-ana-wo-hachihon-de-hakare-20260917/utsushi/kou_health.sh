#!/bin/bash
# ★寫し器★ kou_health(型=甲) ―― 生器 scripts/agent_health_check.sh の逐語切片。★生器へは一字も書いて居らぬ★
#   生器 sha16=7d11ba9f852ac759 / 切り出した行域=85-129 / 作つた刻=2026-09-17T11:35:17+0900
#   生器と同じ shell 宣: set -uo pipefail
set -uo pipefail
# ===== 寫し ここから(生器 逐語・一字も違へず) =====
# ─── 閾の番人(甲/乙) ───
_th_say(){ printf '%s\n' "[health_check] $*" >&2; }
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
#   ★乙′(裁 seq323687⑵ ―― 可)★: 未設定＝既定 は本器の★設計上の常態★ゆゑ、★本 process に一度だけ★刷る。
#   閾の数だけ逐回鳴らせば★鳴りすぎる鐘★(裁の逐語)ゆゑ一度に纏める。★異常の三形★
#   (空文字・空白のみ・比較器で扱へぬ)は必ず鳴る。門(低頻度器)では四形悉く刷る。
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
# 比較器で扱へぬ閾は器を殺さず番人だけ黙らせる／氾濫させる(專任3 第40弾・裁 322099)。閾の意味は不変。
fix_threshold HEALTH_CHECK_COOLDOWN_SEC 300 ALERT_COOLDOWN_SEC  # 5 min (= task spec)
# ===== 寫し ここまで =====
# ===== 附録(當席が書いた駆動部・寫しに非ず) =====
__uke="${ALERT_COOLDOWN_SEC-《受け皿が立たず》}"
__kbranch=UNRUN
# ↓ 下流 逐語(scripts/agent_health_check.sh:144-146) ―― elapsed(=0秒) を閾と比べ、冷却中なら報せを抑へる ／ 前後の括りは當席の物、中は一字も違へず
__k(){ elapsed=0
# --- 下流 寫し ここから ---
    if [ "$elapsed" -lt "$ALERT_COOLDOWN_SEC" ]; then
        return 1
    fi
# --- 下流 寫し ここまで ---
  return 0
}
__k; __krc=$?
[ "${__krc}" = 1 ] && __kbranch="TAKEN(冷却中=報せを抑へる)" || __kbranch="NOTTAKEN(報せを出す)"
__k3="${__read_rc-―}"   # read の rc(在る器のみ)
printf "RESULT\t%s\t%s\t%s\n" "$__uke" "$__kbranch" "$__k3"
