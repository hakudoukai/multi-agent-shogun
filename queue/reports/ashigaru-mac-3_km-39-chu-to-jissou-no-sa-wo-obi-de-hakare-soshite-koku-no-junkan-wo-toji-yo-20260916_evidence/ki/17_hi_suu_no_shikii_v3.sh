#!/bin/bash
# 第39弾 問一 ㋓ の裏(第三版) ―― 16_ は ★閾を確かに渡せて居た★ のに、
#   自己検めが ★rc の列★ を見た故「渡せて居らぬ」と刷つた(疵)。★弁ずる列が違つた。★
#   rc は悉く 0 である ―― 因は ★`if` の条件は set -e の埒外★ だからであり、
#   ∴ 分けるのは rc ではなく ★枝(出目の字)★ である。
#   ★15_ も 16_ も消さぬ。★
# ★的(scripts/stop_hook_inbox.sh)は走らせて居らぬ。★
set -u
FORM='set -euo pipefail; UNREAD_COUNT=3; MASS_UNREAD_THRESHOLD=${MASS_UNREAD_THRESHOLD:-5};
if [ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]; then echo "枝=exit0_mass_guard"; else echo "枝=block_へ落ちる"; fi
echo "到達=比較の後"'

printf '★未讀 n=3 固定(帯の中)。動かすは閾のみ。分ける列 = ★枝★(rc に非ず)★\n\n'
TBL=$(mktemp) || exit 2
row(){ # $1=札 $2=unset|set $3=値
  local label="$1" how="$2" val="${3-}" out rc branch err
  if [ "$how" = unset ]; then out=$(env -u MASS_UNREAD_THRESHOLD bash -c "$FORM" 2>&1); rc=$?
  else out=$(MASS_UNREAD_THRESHOLD="$val" bash -c "$FORM" 2>&1); rc=$?; fi
  branch=$(printf '%s\n' "$out" | grep -o '枝=[^ ]*' | head -1)
  err=$(printf '%s\n' "$out" | grep -c 'integer expression expected')
  printf '%-16s rc=%-2s 枝=%-18s [の苦情=%s 到達=%s\n' "$label" "$rc" "${branch#枝=}" "$err" \
    "$(printf '%s\n' "$out" | grep -c '到達=比較の後')"
  printf '%s\t%s\n' "$label" "${branch#枝=}" >> "$TBL"
}
row "閾=未設定"      unset
row "閾=5"           set 5
row "閾=空"          set ""
row "閾=abc"         set abc
row "閾=0"           set 0
row "閾=-1"          set -1
row "閾=5(尾空白)"   set "5 "
row "閾=00005"       set 00005

printf '\n★自己検め(陽性対照)★ ―― ★枝★ の列に二種以上 出たか\n'
nb=$(cut -f2 "$TBL" | sort -u | wc -l | tr -d ' ')
printf '  相異なる枝の數 = %s\n' "$nb"
if [ "$nb" -le 1 ]; then printf '  ★一種のみ ―― 閾が届いて居らぬ疑ひ。數を讀むな。★\n'
else printf '  ★二種以上 ―― 閾は届いて居る。此の表は讀んでよい。★\n'; fi
rm -f "$TBL"

printf '\n★併せて測る ―― 「[ の rc=2 は set -e に殺されるか」★\n'
o1=$(bash -c 'set -euo pipefail; if [ 3 -gt abc ]; then echo y; else echo n; fi; echo 後の行へ到達' 2>&1); r1=$?
printf '  条件の中 : rc=%s 出目=%s\n' "$r1" "$(printf '%s' "$o1" | tr '\n' '|')"
o2=$(bash -c 'set -euo pipefail; [ 3 -gt abc ]; echo 後の行へ到達' 2>&1); r2=$?
printf '  条件の外 : rc=%s 出目=%s\n' "$r2" "$(printf '%s' "$o2" | tr '\n' '|')"
printf '  ★∴ `if` の条件は set -e の埒外 ―― 殺されぬ。★ 裸で置けば殺される(rc=%s)。\n' "$r2"
printf '  ★15_ が「非數は殺す」と宣つたのは ★誤★ である。現物は上の二行。★\n'
