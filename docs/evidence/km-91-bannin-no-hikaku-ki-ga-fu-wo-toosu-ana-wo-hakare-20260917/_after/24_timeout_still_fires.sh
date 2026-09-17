#!/bin/bash
# km-91 _after/24 (第三版) ―― ★治が時限を殺して居らぬか★ の陽性対照。
#  ★當席の器の疵(隠さず記す)★:
#   ⑴ 初版は `{ printf; sleep 30; } | hook` の形で ★pipeline 全体★ の寿命を測つて居た(壁時計=30s)。
#      hook 自身は 1 秒で戻つて居た(##KM91 elapsed=1 が其の証)。∴ FIFO で供給元と切り離す。
#   ⑵ 裸 read の probe が `set -u` 下で I 未初期化 → `I: unbound variable` で死んだ。I="" を置く。
#   ⑶ 第二版は後片付けに強制終了の器を使ひ ★DD-169 guard に止められた★(正しく止めた)。
#      ∴ 供給元は自ら退く形(sleep 3)にし、其の器を一切使はぬ。
set -u
export __STOP_HOOK_SCRIPT_DIR="$PWD"; export __STOP_HOOK_AGENT_ID="km91-probe"

fire(){ # $1=札 $2=写し $3=timeout ―― FIFO で供給し ★hook 自身の壁時計★ を測る
  local tag="$1" u="$2" t="$3" fifo out err t0 t1 el rc
  fifo=$(mktemp -u); mkfifo "$fifo"; out=$(mktemp); err=$(mktemp)
  { printf '{"stop_hook_active": true}'; sleep 3; } > "$fifo" &
  t0=$(python3 -c 'import time;print(time.time())')
  STOP_HOOK_STDIN_TIMEOUT="$t" /bin/bash "$u" < "$fifo" > "$out" 2> "$err"; rc=$?
  t1=$(python3 -c 'import time;print(time.time())')
  el=$(python3 -c "print('%.2f' % ($t1-$t0))")
  wait 2>/dev/null
  printf '%-26s timeout=%-4s rc=%s ★hook 自身の壁時計=%ss★\n' "$tag" "$t" "$rc" "$el"
  printf '    %s\n' "$(grep '^##KM91' "$out" || echo '印無し')"
  sed 's/^/    stderr| /' "$err"
  rm -f "$fifo" "$out" "$err"
}
echo "## 時限が生きて居るか ―― 口を閉ぢぬ供給(FIFO・3秒居座る)・timeout=1 ⇒ ★hook は約1秒で戻る筈★"
fire "生器の写し(治前)" "$1" 1
fire "治した写し(治後)" "$2" 1
echo
echo "## 上の境 ―― \`read -t\` の實受容上限は 4294967295(實測 _after/13)"
printf '%-12s %-18s %-22s %s\n' 値 '裸 read -t 字数' '治前 番人' '治後 番人'
for v in 86400 86401 4294967295 4294967296; do
  n=$(printf '{"a":1}' | /bin/bash -c 'I=""; IFS= read -r -d "" -t "$1" I 2>/dev/null; echo "${#I}"' _ "$v")
  a=$(printf '{"stop_hook_active": true}' | STOP_HOOK_STDIN_TIMEOUT="$v" /bin/bash "$1" 2>/dev/null | grep -o 'bannin=[^ ]*')
  b=$(printf '{"stop_hook_active": true}' | STOP_HOOK_STDIN_TIMEOUT="$v" /bin/bash "$2" 2>/dev/null | grep -o 'bannin=[^ ]*')
  printf '%-12s %-18s %-22s %s\n' "$v" "$n" "$a" "$b"
done
