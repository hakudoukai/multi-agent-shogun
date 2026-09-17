#!/bin/bash
# 54 ★直した後の甲★ を八形で測る(㋓)
# 旧版(30器)と同じ八形を、他席が直した後の写し(kou_new_harness.sh)へ当てる。
# stdin は ★不達★(書き手が閉ぢぬ)相のみ ―― 時限切れが起きるべき相である。
# 上限 12 秒の砂時計を掛け、其れを超えたら ★止(永久待ち)★ と刷る。
B="$1"; H="$B/utsushi/kou_new_harness.sh"
printf '形\t與へた値\t砂時計\twall_s\t時限切れの報せ\tOUT\tstderr_1\n'
run(){
  local lab="$1" val="$2" t0 el out err arc
  t0=$(date +%s)
  if [ "$val" = "__UNSET__" ]; then
    out=$(perl -e 'alarm 12; exec @ARGV' -- env -u STOP_HOOK_STDIN_TIMEOUT /bin/bash "$H" 2>"$B/raw/54.e" < <(sleep 20)); arc=$?
  else
    out=$(perl -e 'alarm 12; exec @ARGV' -- env STOP_HOOK_STDIN_TIMEOUT="$val" /bin/bash "$H" 2>"$B/raw/54.e" < <(sleep 20)); arc=$?
  fi
  el=$(( $(date +%s) - t0 ))
  err=$(head -1 "$B/raw/54.e")
  grep -q '時限切れ' "$B/raw/54.e" && keigo='★有★' || keigo='無'
  [ "$arc" -ne 0 ] && [ "$el" -ge 12 ] && keigo='★止(砂時計が切る迄 返らず)★'
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$lab" "${val//$'\n'/␊}" "$arc" "$el" "$keigo" "${out:-(無)}" "${err:0:70}"
}
run 1未設定 __UNSET__
run 2空文字 ""
run 3空白のみ " "
run 4二十桁 "99999999999999999999"
run 5正常値1 "1"
run 6負数 "-5"
run 7改行入り "$(printf '1\n2')"
run 8既存␊ "1␊2"
run 9二の32乗引1 "4294967295"
run 10二の32乗 "4294967296"
run 11二の63乗引1 "9223372036854775807"
