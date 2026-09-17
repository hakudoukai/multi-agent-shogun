#!/bin/bash
# doku_na.sh ―― ★名の毒★: pane target に毒を当て、tmux が何を返すかを測る。
# 讀取のみ(display-message は問ふだけ・send-keys は一切打たぬ)。
set -u
printf '%-34s %-4s %-10s %-26s %s\n' "的(名)" rc "出力" "親 甲:rc のみ" "子 py:rc かつ %% 起し"
printf '%s\n' "--------------------------------------------------------------------------------------------------"
probe(){
  local t="$1" out rc
  out=$(tmux display-message -t "$t" -p '#{pane_id}' 2>/dev/null); rc=$?
  local oya ko
  if [ "$rc" -eq 0 ]; then oya="在ると判ず"; else oya="無いと判ず"; fi
  if [ "$rc" -eq 0 ] && [ "${out#%}" != "$out" ]; then ko="在ると判ず"; else ko="無いと判ず"; fi
  local mark=""
  [ "$oya" != "$ko" ] && mark="★親子の判が割れる★"
  printf '%-34s %-4s %-10s %-26s %s\n' "$t" "$rc" "${out:-(空)}" "$oya" "$ko $mark"
}
# 陰性対照(宣どほりの正しい名・本 Mac に実在する物)
probe "multiagent-mac:0.0"
# 陽性対照(毒)
probe "km83-nonexistent-pane-zzz:0.0"
probe "multiagent-mac:99.99"
probe "commander-third:0.0"
probe ""
probe " "
probe "0"
probe "%99999"
