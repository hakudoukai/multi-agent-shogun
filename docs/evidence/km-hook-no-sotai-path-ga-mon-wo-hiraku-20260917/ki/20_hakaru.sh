#!/bin/bash
# 測り器 ―― hook の command が相対path である事が、cwd の移動で門を開くかを測る。
# 引数: $1=repo根  $2=移動先(束の中)
set -u
R="$1"; M="$2"
echo "# 刻 = $(date '+%Y-%m-%dT%H:%M:%S%z')"
echo "# repo根 = $R"
echo "# 移動先 = $M"
echo
echo "## settings.json の hook 宣言(逐語・event と command のみ)"
python3 - "$R/.claude/settings.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
for ev,arr in (d.get('hooks') or {}).items():
    for g in arr:
        for h in g.get('hooks',[]):
            c=h.get('command','')
            print("event=%s\tcommand=%s\t絶対path=%s" % (ev,c,'有' if c.lstrip().startswith(('/','$','~')) else '★無(相対)★'))
PY
echo
echo "## 呼ばれる器の実在(repo根から)"
for f in scripts/stop_hook_inbox.sh scripts/goal_stop_hook.py scripts/checks/pretooluse_bash_guard.sh \
         scripts/checks/dd169_kill_term_guard.sh scripts/checks/context_usage_warn.sh scripts/goal_stopfailure_hook.py; do
  if [ -f "$R/$f" ]; then echo "在	$f	$(wc -c < "$R/$f" | tr -d ' ')byte"; else echo "★無★	$f	-"; fi
done
echo
echo "## 実走 ―― 同じ command を 二つの cwd から呼ぶ(胴は空json)"
printf '%s\t%s\t%s\t%s\n' "cwd" "command" "rc" "一行目"
while IFS= read -r c; do
  [ -z "$c" ] && continue
  for d in "$R" "$M"; do
    t=$(mktemp); ( cd "$d" && printf '{}' | eval "$c" ) >"$t" 2>&1
    rc=$?          # ★pipe を挟まぬ★(v1 は head の rc を書いて居た=疵)
    o=$(head -1 "$t"); rm -f "$t"
    lbl=$( [ "$d" = "$R" ] && echo "根" || echo "★移動後★" )
    printf '%s\t%s\trc=%s\t%s\n' "$lbl" "$c" "$rc" "$(printf '%s' "$o" | cut -c1-72)"
  done
done <<'CMDS'
bash scripts/stop_hook_inbox.sh
python3 scripts/goal_stop_hook.py
scripts/checks/pretooluse_bash_guard.sh
bash scripts/checks/dd169_kill_term_guard.sh
bash scripts/checks/context_usage_warn.sh
python3 scripts/goal_stopfailure_hook.py
CMDS
