#!/bin/bash
# km-91 _after/11 ―― 写しを ★両対照★ で叩く。
#   陽性対照の stdin = stop_hook_active:true の真な hook JSON。
#     讀めれば 番人=効く／讀めねば 番人=★効かぬ★(= 無限ループ防ぎが消える)。
#   出目: rc / stderr 行数 / stderr 逐語 / 讀めた字数 / 経過秒(壁時計・小数) / stop_hook_active / 番人
set -u
UTSUSHI="$1"            # 写しの path
JSON='{"stop_hook_active": true, "session_id": "km91", "hook_event_name": "Stop"}'
export __STOP_HOOK_SCRIPT_DIR="$PWD"
export __STOP_HOOK_AGENT_ID="km91-probe"

run() {  # $1=札 $2=未設定なら "UNSET" さもなくば値
  local tag="$1" mode="$2" val="${3-}"
  local out err rc t0 t1 el
  out=$(mktemp); err=$(mktemp)
  t0=$(python3 -c 'import time;print(time.time())')
  if [ "$mode" = "UNSET" ]; then
    printf '%s' "$JSON" | env -u STOP_HOOK_STDIN_TIMEOUT /bin/bash "$UTSUSHI" > "$out" 2> "$err"
  else
    printf '%s' "$JSON" | STOP_HOOK_STDIN_TIMEOUT="$val" /bin/bash "$UTSUSHI" > "$out" 2> "$err"
  fi
  rc=$?
  t1=$(python3 -c 'import time;print(time.time())')
  el=$(python3 -c "print('%.2f' % ($t1-$t0))")
  local km; km=$(grep '^##KM91' "$out" || true)
  local errn; errn=$(grep -c '' "$err")
  printf '── %s\n' "$tag"
  printf '   rc=%s  壁時計経過=%ss  stderr行数=%s\n' "$rc" "$el" "$errn"
  printf '   %s\n' "${km:-##KM91 印 ★無し★(写しが此処へ届かなんだ)}"
  if [ "$errn" -gt 0 ]; then sed 's/^/   stderr| /' "$err"; else printf '   stderr| (空)\n'; fi
  rm -f "$out" "$err"
}

echo "# 対象写し = $UTSUSHI  sha16=$(shasum -a 256 "$UTSUSHI"|cut -c1-16)"
echo "# stdin(陽性対照) = $JSON"
echo "# bash = $(/bin/bash --version|head -1)"
echo "# 判読: 番人「効く」= 無限ループ防ぎが生きて居る／「★効かぬ★」= 消えて居る"
echo
echo "════ 陰性(守る筈) ════"
run "陰性 10"        VAL 10
run "陰性 0"         VAL 0
run "陰性 既定(未設定)" UNSET
echo
echo "════ 陽性(開く筈) ════"
run "陽性 -5"        VAL -5
run "陽性 -1"        VAL -1
echo
echo "════ 境 ════"
run "境 空文字"       VAL ""
run "境 空白のみ"     VAL " "
run "境 非数 abc"     VAL abc
run "境 010"          VAL 010
run "境 2^63超(20桁)" VAL 99999999999999999999
run "境 可視印␊既在"  VAL "1␊0"
