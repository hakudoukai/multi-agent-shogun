#!/bin/bash
# km-91 _after/25 ―― 生器 L46 の主張を検む。
#   L46 逐語: 「★時限切れでも bash は讀めた分を変数へ入れる★(man bash: saves any partial input)」
#   之が此の機の bash 3.2 で真か否かで、★時限が効いた時に番人が生きるか死ぬか★ が決まる。
set -u
echo "# bash=$(/bin/bash --version|head -1)"
echo "# 供給: JSON 26字を先に流し、口は閉ぢず N 秒居座る。timeout=1 で時限を必ず踏ませる。"
echo
for d in '-d ""' 'なし(改行区切)'; do
  fifo=$(mktemp -u); mkfifo "$fifo"
  { printf '{"stop_hook_active": true}'; sleep 3; } > "$fifo" &
  if [ "$d" = '-d ""' ]; then
    r=$(/bin/bash -c 'I=""; IFS= read -r -d "" -t 1 I; echo "rc=$?:len=${#I}:[$I]"' < "$fifo")
  else
    r=$(/bin/bash -c 'I=""; IFS= read -r -t 1 I; echo "rc=$?:len=${#I}:[$I]"' < "$fifo")
  fi
  wait 2>/dev/null
  printf '  read %-16s → %s\n' "$d" "$r"
  rm -f "$fifo"
done
echo
echo "## 対照: 口が閉ぢる(EOF)場合 ―― 時限は踏まぬ"
r=$(printf '{"stop_hook_active": true}' | /bin/bash -c 'I=""; IFS= read -r -d "" -t 1 I; echo "rc=$?:len=${#I}"')
printf '  EOF 有り read -d "" -t 1 → %s\n' "$r"
echo
echo "## man bash 3.2 の当該文言(此の機の man より)"
MANWIDTH=200 man bash 2>/dev/null | col -b | grep -n -A2 -B2 'partial input' | head -20 || echo '  (該当語 見当らず)'
