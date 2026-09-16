#!/bin/bash
# ★負テスト器(km-74・裁 seq323062⑷「各1形負テスト」/裁 seq323980⑵)★
# 常駐 loop を起さぬ為、器ごとに ★閾函数の塊だけ★ を抜いて source する。
# 抜く範囲=「_th_say() の行」から「fix_threshold の閉じ }」まで。境は grep で毎回測り、行番号は焼かぬ。
# 出す物: ㋐刷つた行数(1でなければ注入が通つた) ㋑倒れた先の値 ㋒rc
set +e
cd "$(/usr/bin/dirname "$0")/../../../.." || exit 9
run_one(){
  local f="$1" name="$2" dflt="$3" out="$4" val="$5" tag="$6"
  local b e frag
  b=$(/usr/bin/grep -n '_th_say()' "$f" | /usr/bin/head -1 | /usr/bin/cut -d: -f1)
  e=$(/usr/bin/awk -v s="$(/usr/bin/grep -n 'fix_threshold()' "$f" | /usr/bin/head -1 | /usr/bin/cut -d: -f1)" \
        'NR>=s && $0=="}" {print NR; exit}' "$f")
  [ -n "$b" ] && [ -n "$e" ] || { echo "★境 測れぬ f=$f b=$b e=$e★"; return 9; }
  frag=$(/usr/bin/mktemp /tmp/km74frag.XXXXXX) || return 9
  { echo 'log(){ printf "%s\n" "[stub_log] $*" >&2; }'      # watchdog の _th_say は log() を呼ぶ
    /usr/bin/sed -n "${b},${e}p" "$f"; } > "$frag"
  local o rc n v
  o=$( ( . "$frag"; eval "$out=未設定"; export "$name=$val"
         fix_threshold "$name" "$dflt" "$out"; echo "rc=$?" >&2
         eval "echo \"値=\$$out\"" >&2 ) 2>&1 )
  n=$(printf '%s\n' "$o" | /usr/bin/grep -v '^rc=' | /usr/bin/grep -vc '^値=' ); [ -n "$n" ] || n=測れぬ
  echo "── $tag  器=$f  閾=$name(既定 $dflt)  抜いた行 ${b}〜${e}"
  printf '%s\n' "$o" | /usr/bin/sed 's/^/     /'
  echo "     ★刷つた log 行数(rc=/値= は除く・1 でなければ注入が通つた)=${n}★"
  /bin/rm -f "$frag"
}
printf 'BASH_VERSION=%s  刻=%s\n\n' "$BASH_VERSION" "$(/bin/date '+%F %T')"
INJ=$'9x\n★閾 偽の行 ―― 既定へ倒す(fail-closed)★'   # 陽性=改行注入
PRE=$'9x␊偽'                                          # 陽性=印既在(fail-closed で拒む形)
echo "【形一 行注入】値=「9x」+改行+「★閾 偽の行…★」 ―― 期待=1行に収まり、値は既定へ倒れる"
run_one scripts/inbox_watcher.sh                           NUDGE_COOLDOWN_SEC      60      NUDGE_COOLDOWN_SEC  "$INJ" 甲
run_one scripts/watchdogs/enter_restart_common_watchdog.sh ER_THRESHOLD_MIN        10      THRESHOLD_MIN       "$INJ" 乙
run_one scripts/agent_health_check.sh                      HEALTH_CHECK_TOKEN_WARN 200000  TOKEN_WARN_THRESHOLD "$INJ" 丙
run_one scripts/checks/context_usage_warn.sh               CONTEXT_WARN_BYTES      1600000 WARN_BYTES          "$INJ" 丁
echo
echo "【形二 印既在】値=「9x␊偽」 ―― 期待=値を刷らず既定へ倒す(裁 seq323980⑵ の fail-closed)"
run_one scripts/inbox_watcher.sh                           NUDGE_COOLDOWN_SEC      60      NUDGE_COOLDOWN_SEC  "$PRE" 甲
run_one scripts/watchdogs/enter_restart_common_watchdog.sh ER_THRESHOLD_MIN        10      THRESHOLD_MIN       "$PRE" 乙
run_one scripts/agent_health_check.sh                      HEALTH_CHECK_TOKEN_WARN 200000  TOKEN_WARN_THRESHOLD "$PRE" 丙
run_one scripts/checks/context_usage_warn.sh               CONTEXT_WARN_BYTES      1600000 WARN_BYTES          "$PRE" 丁

echo
echo "【形三 陰性=正しい数】値=「42」 ―― 期待=★log 0 行(黙る)★・値は 42 そのまま(直しが happy path を壊して居らぬ証)"
run_one scripts/inbox_watcher.sh                           NUDGE_COOLDOWN_SEC      60      NUDGE_COOLDOWN_SEC  "42" 甲
run_one scripts/watchdogs/enter_restart_common_watchdog.sh ER_THRESHOLD_MIN        10      THRESHOLD_MIN       "42" 乙
run_one scripts/agent_health_check.sh                      HEALTH_CHECK_TOKEN_WARN 200000  TOKEN_WARN_THRESHOLD "42" 丙
run_one scripts/checks/context_usage_warn.sh               CONTEXT_WARN_BYTES      1600000 WARN_BYTES          "42" 丁

echo
echo "【形四 陰性=空文字】値=「」 ―― 期待=★「空文字」の1行★(乙 322952 の既存枝・印の枝に食はれて居らぬ証)・既定へ"
run_one scripts/inbox_watcher.sh                           NUDGE_COOLDOWN_SEC      60      NUDGE_COOLDOWN_SEC  "" 甲
run_one scripts/watchdogs/enter_restart_common_watchdog.sh ER_THRESHOLD_MIN        10      THRESHOLD_MIN       "" 乙
run_one scripts/agent_health_check.sh                      HEALTH_CHECK_TOKEN_WARN 200000  TOKEN_WARN_THRESHOLD "" 丙
run_one scripts/checks/context_usage_warn.sh               CONTEXT_WARN_BYTES      1600000 WARN_BYTES          "" 丁
