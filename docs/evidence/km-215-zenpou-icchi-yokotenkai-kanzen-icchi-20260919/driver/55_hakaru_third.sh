#!/usr/bin/env bash
# 55 ―― watcher_supervisor_third.sh の resolve_agent_pane() を実引数で測る。
# ★全体を走らせぬ★: 本体は無限loop(while true)で start_watcher_if_missing を呼び、
#   宛先 pane が生きて居れば setsid nohup で inbox_watcher.sh を起動し得る(受入⑺の外だが
#   本弾の対象外・別プロセス起動を避ける為、resolve_agent_pane() のみ抽出して測る)。
set -uo pipefail
cd "$(dirname "$0")/../../../.."   # → repo root (worktree)
PROJECT_ROOT="$(pwd)"
SCRIPT="scripts/watcher_supervisor_third.sh"

FUNC_SRC=$(awk '/^resolve_agent_pane\(\) \{/{p=1} p{print} p&&/^}/{exit}' "$SCRIPT")
eval "$FUNC_SRC"

for AGENT in ashigaru-third-1 gunshi-third; do
    echo "=== argv=\"$AGENT\" ==="
    out=$(resolve_agent_pane "$AGENT" 2>err.$$.tmp)
    rc=$?
    err=$(cat err.$$.tmp); rm -f err.$$.tmp
    echo "cwd=$PROJECT_ROOT"
    echo "argv=resolve_agent_pane $AGENT"
    echo "rc=$rc"
    echo "stdout=${out:-<空>}"
    echo "stderr="
    echo "$err" | sed 's/^/  /'
    echo ""
done
