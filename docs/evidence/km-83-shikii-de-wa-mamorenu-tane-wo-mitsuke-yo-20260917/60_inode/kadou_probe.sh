#!/bin/bash
# ★己の系譜は字面で除けぬ★ ―― 自 PID から祖先を辿り、其の集合を除く。
mine=""
p=$$
while [ -n "$p" ] && [ "$p" != "0" ] && [ "$p" != "1" ]; do
  mine="$mine $p"
  p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
done
echo "除く系譜 PID=[$mine ]"
for pat in pane_enter_watcher_supervisor pane_enter_watcher.py detect_stale enter_restart_commander_watchdog enter_restart_common_watchdog; do
  echo "[pat=$pat]"
  found=0
  while read -r pid rest; do
    [ -z "$pid" ] && continue
    case " $mine " in *" $pid "*) continue ;; esac
    found=$((found+1))
    echo "  pid=$pid  $rest"
  done < <(pgrep -fl "$pat" 2>/dev/null)
  [ "$found" -eq 0 ] && echo "  ★走らず★ (系譜除外後 0件)"
done
