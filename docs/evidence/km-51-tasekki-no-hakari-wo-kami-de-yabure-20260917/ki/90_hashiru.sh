#!/bin/bash
# 90_hashiru.sh ―― 本弾の器を悉く走らせ、生の一切を 10_kaki.py を通して nama/ へ置く。
# 使ひ方: 90_hashiru.sh <束path> <repo根>
# ★己(此の driver)の出す物も生である★ ―― 90_hashiru.log を臺帳へ載せる。
set -u
B="$1"; R="$2"
K(){ python3 -B "$B/ki/10_kaki.py" "$@"; }
tou(){ # $1=出し先(nama内の名) $2=器名 ; 本文=stdin, stderr は <名>.err へ
  local na="$1" nu="$2"
  K "$B/nama/$na" --nushi "$nu"
}
cd "$R" || exit 2
echo "[90] 刻 $(date '+%Y-%m-%dT%H:%M:%S%z')"

run(){ # $1=出し先基名 $2=器名 残り=実行語
  local na="$1" nu="$2"; shift 2
  "$@" >"$B/nama/.t.out" 2>"$B/nama/.t.err"; local rc=$?
  tou "$na" "$nu" <"$B/nama/.t.out" 2>&1 | tail -1
  tou "${na%.*}.err" "$nu の stderr" <"$B/nama/.t.err" 2>&1 | tail -1
  printf '%s\trc=%d\n' "$na" "$rc" >>"$B/nama/.rcs"
  echo "[90] $na rc=$rc"
  rm -f "$B/nama/.t.out" "$B/nama/.t.err"
}
: >"$B/nama/.rcs"

run 20_bosuu.txt      '20_bosuu.py(母數を彼の生から独立に導く)' \
    python3 -B "$B/ki/20_bosuu.py" "$B/utsushi/km52_raw_30_ate.tsv" "$B/utsushi/km52_raw_60_gai.tsv"
# ★先づ版を固定する ―― 共有樹は同刻に他席が書き換へる(本弾で實際に四本悉く動いた)★
NM="$B/utsushi/namaki"
run 96_kotei.txt      '96_kotei.sh(測る版を其の場で束へ固定する)' \
    bash "$B/ki/96_kotei.sh" "$NM" scripts/inbox_watcher.sh scripts/agent_health_check.sh \
      scripts/checks/context_usage_warn.sh scripts/watchdogs/enter_restart_common_watchdog.sh
run 97_hyoteki.txt    '97_hyoteki.sh(★的として名指された版に番人が居るか★を引いて数へる)' \
    bash "$B/ki/97_hyoteki.sh" a4cafdf scripts/inbox_watcher.sh scripts/agent_health_check.sh \
      scripts/checks/context_usage_warn.sh scripts/watchdogs/enter_restart_common_watchdog.sh
run 71_kougodan.tsv   '71_kougodan.py(18閾の決定の讀手を★凍結版★から引く)' \
    python3 -B "$B/ki/71_kougodan.py" "$NM/inbox_watcher.sh" "$NM/agent_health_check.sh" \
      "$NM/context_usage_warn.sh" "$NM/enter_restart_common_watchdog.sh"
run 70_monosashi.tsv  '70_monosashi.py(己の物差しで126を割り直す)' \
    python3 -B "$B/ki/70_monosashi.py" "$B/utsushi/km52_raw_60_gai.tsv" "$B/nama/71_kougodan.tsv"
run 30_yomite.txt     '30_yomite.sh(四つの讀手を己の手で測る)' \
    bash "$B/ki/30_yomite.sh" /bin/bash
run 40_ichiyou.txt    '40_ichiyou.sh(㋑一様18を四軸で検む ―― ★當席が測つた凍結版(07:2x)★)' \
    bash "$B/ki/40_ichiyou.sh" "$NM/inbox_watcher.sh" "$NM/agent_health_check.sh" \
      "$NM/context_usage_warn.sh" "$NM/enter_restart_common_watchdog.sh"
K2="$B/utsushi/km52ki"   # ★專任2 が己の束へ収めた写し(a4cafdf) ―― 彼の申し立ては★此の版★で測る★
run 42_ichiyou_km52.txt '40_ichiyou.sh(㋑同じ物差しを★專任2 の版★へ当てる ―― 公平の為)' \
    bash "$B/ki/40_ichiyou.sh" "$K2/inbox_watcher.sh" "$K2/agent_health_check.sh" \
      "$K2/context_usage_warn.sh" "$K2/enter_restart_common_watchdog.sh"
WD="$B/saya"; mkdir -p "$WD"          # ★鞘 ―― 器が拵へる中間物を此処だけに置く(生器へは一字も書かぬ)★
# ★毒は四つ。各々に陰性対照(清き値 30)を併せる★
for doku in '-1' '' '0x32' '99999999999999999999' '30'; do
  na="41_ukezara_$(printf '%s' "${doku:-空}" | tr -c 'A-Za-z0-9' '_').txt"
  run "$na" "41_ukezara.sh(受け皿の差・毒=「${doku}」${doku:+}$([ -z "$doku" ] && echo ' ★空文字★')$([ "$doku" = 30 ] && echo ' ★陰性対照★'))" \
      bash "$B/ki/41_ukezara.sh" "$B/utsushi/bannin_kata_watcher.sh" "$doku"
done
run 50_nul.txt        '50_nul.sh(NUL を四つの路で運ぶ)' \
    bash "$B/ki/50_nul.sh" "$B/utsushi/bannin_kata_watcher.sh" "$WD/nul"
run 60_chunyu.txt     '60_chunyu.sh(行注入の直しの限りを測る)' \
    bash "$B/ki/60_chunyu.sh" "$WD/chunyu"
run 61_locale.txt     '61_locale.sh(直しの出す byte が地言に依るか)' \
    bash "$B/ki/61_locale.sh" "$WD/locale"

run 95_sha_ato.txt    '95_sha_ato.sh(版を五面で刷り、動いたのが誰の手かを示す)' \
    bash "$B/ki/95_sha_ato.sh" "$B/nama/03_namaki_sha_mae.txt" "$NM" \
      scripts/inbox_watcher.sh scripts/agent_health_check.sh \
      scripts/checks/context_usage_warn.sh scripts/watchdogs/enter_restart_common_watchdog.sh

run 98_kami.txt      '98_kami.sh(★紙に書いた數を紙とは別の器で数へ直す★)' \
    bash "$B/ki/98_kami.sh" "$B"
echo "[90] rcs:"; cat "$B/nama/.rcs"
mv "$B/nama/.rcs" "$B/nama/.rcs.t"; tou 90_rcs.txt '90_hashiru.sh(各器の rc 一覧)' <"$B/nama/.rcs.t" 2>&1 | tail -1
rm -f "$B/nama/.rcs.t"
echo "[90] 了 $(date '+%Y-%m-%dT%H:%M:%S%z')"
