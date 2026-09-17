#!/bin/bash
# ㋑ ★零を「數であるが無意味な物」として拒む述語★
# 順 ―― ⑴先に ★閾0 の器が恒真である事★ を陽性対照で見せ ⑵其の後に直した述語を見せる。
# 器の本体は raw/05_ki.sh に一つだけ在る(此処には写さぬ)。
set -u
cd "$(dirname "$0")" || exit 2
. ./05_ki.sh

printf '刻 = %s\n' "$(date '+%Y-%m-%dT%H:%M:%S')"
printf '\n★甲 ―― ★直す前★ の陽性対照。閾0 を据ゑて生器と同じ判を当てる★\n'
printf '  判の字句 = [ "$total" -ge "$MAXB" ] ―― 生器 scripts/checks/karo_mac_dasumae_gate.sh:196 の写し\n'
printf '  ★-ge である(-gt ではない)。∴ byte和 0 すら閾0 では鳴る。★\n\n'
printf '  %-14s %-8s %s\n' 'byte和' '閾=0' '閾=10485760(現行)'
naru=0; kazu=0
for t in 0 1 6 142925 10485759 10485760; do
  a=$(jou5 "$t" 0); b=$(jou5 "$t" 10485760)
  kazu=$((kazu+1)); [ "$a" = 鳴 ] && naru=$((naru+1))
  printf '  %-14s %-8s %s\n' "$t" "$a" "$b"
done
printf '\n  ★閾0 では %s/%s が鳴つた ―― ★恒真★。★\n' "${naru}" "${kazu}"
printf '  ★恒真の器は、鳴らぬ器と同じく誰も見ぬ。之が「零は is_num を素通りする」の実体である。★\n'
if is_num 0; then r=0; else r=1; fi
printf '  is_num "0" の rc = %s ―― ★零は is_num を通る。is_num は「數でない物」しか拒まぬ。★\n' "${r}"

printf '\n★乙 ―― ★直した述語★ shikii_yuui(raw/05_ki.sh)★\n'
printf '  rc: 0=有意 / 1=數でない / 2=★恒真★ / 3=★算が届かぬ★ / 4=実質恒真(警)\n\n'
for v in 0 -5 1 2 4096 10485760 9223372036854775807 9223372036854775808 18446744073709551616; do
  o=$(shikii_yuui "$v"); r=$?
  b=$(printf '%s' "$v" | wc -c | tr -d ' ')
  printf '  閾「%s」(%s byte) rc=%s 判=%s\n' "$v" "$b" "${r}" "$o"
done

printf '\n★札 ㋑ が名指した四つ★\n'
printf '  0    → rc=2 ★拒む★ ―― 恒真。is_num は通すが本述語が止める。\n'
printf '  負   → rc=1 ★拒む★ ―― 「-」が數字でなく ★is_num が既に止めて居る★(本述語の手柄ではない)。\n'
printf '  1    → rc=4 ★警★  ―― 恒真ではない(byte和 0 は通る)が 0byte 以外は悉く鳴る。★拒まず名指して警を出す。★\n'
printf '  極大 → rc=3 ★拒む★ ―― is_num は「悉く數字」ゆゑ通す。落ちるのは ★[ -ge ] の側★ である。\n'
printf '\n★本弾で新たに出た物(第49弾には無い)★\n'
printf '  ★2^63 = 9223372036854775808 は is_num を通り、[ -ge ] が rc=2 で落ちる。★\n'
printf '  生器 karo_mac_dasumae_gate.sh:196 は其の落ちを `if` の偽として受け ―― ★「閾未満」と刷つて rc=0 を出す。★\n'
printf '  ∴ ★是は fail-open である。★ 生器の註(:52-54)が「閾が數でなければ倒す」と書いた病の ★數である版★ が残つて居る。\n'
printf '  ★之は本弾では塞いで居らぬ(読取のみ・束の中・変更0 の札に従ふ)。紙に書いて上げる。★\n'
