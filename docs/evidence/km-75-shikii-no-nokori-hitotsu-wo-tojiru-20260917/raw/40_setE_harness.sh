#!/usr/bin/env bash
# 試験器 ―― 裁を経た塊を ★set -euo pipefail の下★ で走らせる(km-75)
set -euo pipefail
# ─── 閾の番人(甲/乙) ───
_th_say(){ echo "[srw_test] $*" >&2; }
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
#   ★乙′(裁 seq323687⑵ 提起 → ★裁 seq323895㋐ にて『hook は黙る儘で据えよ』と定まつた★)★:
#   裁の逐語=「理由=warn は異常でない・prompt毎に別process ゆえ『processに一度』は本器に当たらぬ・
#   刻印file は副作用を負う。異常三形が鳴れば足りる」。∴ 以下は★請ひ★でなく★定め★である。
#   本器は ★UserPromptSubmit hook＝prompt 毎に別 process★
#   ゆゑ「process に一度」＝「prompt 毎に一度」＝★毎回★に成り、裁の趣旨「鳴りすぎる鐘」に真向から当たる。
#   ∴ 未設定は★黙る★儘に据ゑ置き、他三器(watcher/watchdog/health)にのみ一度刷る形を入れた。
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
# 此の器が黙ると CLAUDE.md 三層機構の L2 が丸ごと抜ける。然も本体は exit 0 を強ひられて居る
# (DD-169) ∴ ★鳴らぬ事を rc で知る術が無い★。故に ★言ふ★ 事が唯一の報せである(專任3 第40弾)。
fix_threshold SRW_TEST_THRESH 60 COOLDOWN_SEC
printf "RESULT COOLDOWN_SEC=〔%s〕\n" "${COOLDOWN_SEC}"
