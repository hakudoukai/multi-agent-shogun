#!/bin/bash
# 第39弾 問一 ㋓ の裏(第二版) ―― 15_ が ★閾を一度も渡せて居らぬ★ 儘 五行を刷つた故の作り直し。
#   15_ の疵: `bash -c '…' MASS_UNREAD_THRESHOLD="$thr"` は ★env ではなく $0 の位置★ ∴ 子に届かぬ。
#            五行が悉く同じ出目であつたのに、器は「數でない字は殺す」と ★測らずに宣つた★。
#            ★15_ は消さぬ。疵の現物として束に残す。★
# ★的(scripts/stop_hook_inbox.sh)は走らせて居らぬ。★ 的から写したのは L37 と L147 の ★形★ のみ。
set -u
FORM='set -euo pipefail; UNREAD_COUNT=3; MASS_UNREAD_THRESHOLD=${MASS_UNREAD_THRESHOLD:-5};
if [ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]; then echo "枝=exit0(mass_guard)"; else echo "枝=block_へ落ちる"; fi
echo "到達=比較の後"'

printf '★的から写した形★\n  L37 : set -euo pipefail\n  L147: if [ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]; then\n'
printf '★未讀 n は 3 に固定★(帯 1〜5 の中)。動かすは ★閾のみ★。\n\n'

run_one(){ # $1=札 $2=如何に渡すか(unset|set) $3=値
  local label="$1" how="$2" val="${3-}" out rc
  if [ "$how" = "unset" ]; then
    out=$(env -u MASS_UNREAD_THRESHOLD bash -c "$FORM" 2>&1); rc=$?
  else
    out=$(MASS_UNREAD_THRESHOLD="$val" bash -c "$FORM" 2>&1); rc=$?
  fi
  printf '%-14s rc=%-3s 出目=%s\n' "$label" "$rc" "$(printf '%s' "$out" | tr '\n' '|')"
  printf '%s\t%s\n' "$label" "$rc" >> "$TMPTBL"
}

TMPTBL=$(mktemp) || exit 2
run_one "閾=未設定"    unset
run_one "閾='5'"       set 5
run_one "閾=''(空)"    set ""
run_one "閾='abc'"     set abc
run_one "閾='0'"       set 0
run_one "閾='-1'"      set -1
run_one "閾='5 '(尾空白)" set "5 "

printf '\n★器の自己検め(陽性対照)★ ―― 出目が ★悉く同じ★ なら「閾を渡せて居らぬ」疑ひ(15_ の形)。\n'
n_distinct=$(cut -f2 "$TMPTBL" | sort -u | wc -l | tr -d ' ')
printf '  rc の相異なる値の數 = %s\n' "$n_distinct"
if [ "$n_distinct" -le 1 ]; then
  printf '  ★悉く同じ ―― 此の器は閾を渡せて居らぬ。數を讀むな。★\n'
else
  printf '  ★相異なる rc が出た ―― 閾は確かに子へ届いて居る。★\n'
fi
rm -f "$TMPTBL"
