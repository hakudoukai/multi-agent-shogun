#!/bin/bash
# km-214 両対照 + fail-closed 四形 ―― 同一 run。前版 = raw/utsushi/pane_identity.before.sh(生きた版の写し 33a37e49)・後版 = 己の樹の器。
# 生きた pane・箱・他席の樹には触らぬ(tmux は読取のみ)。rc は file へ落とし直後の $? で取る。
set -u
cd "$(dirname "$0")/.."
WT=/Users/momizimac/wt/a1-km214
AFTER="$WT/scripts/checks/pane_identity.sh"; BEFORE="raw/utsushi/pane_identity.before.sh"
REG="$WT/queue/pane_registry.yaml"
PY_VENV=/Users/momizimac/multi-agent-shogun/.venv/bin/python3
run(){ # $1=札 $2=器 残り=env
  local tag="$1" tool="$2"; shift 2
  env "$@" SECTION18_ROLES_LIB=/Users/momizimac/multi-agent-shogun/lib/_section18_roles.sh TMUX_CMD=/opt/homebrew/bin/tmux LAST_RUN_JSON="raw/43_${tag}_last_run.json" bash "$tool" > "raw/43_${tag}.out" 2> "raw/43_${tag}.err"; rc=$?
  for f in "raw/43_${tag}.out" "raw/43_${tag}.err"; do [ -s "$f" ] || printf '\n' > "$f"; done
  printf '%s | rc=%s | ❌=%s ⚠=%s ✅=%s | 期待表行=[%s] | 偽の掴み(実態=karo-mac|ashigaru-mac)=%s\n' "$tag" "$rc" \
    "$(grep -c '❌' "raw/43_${tag}.out" "raw/43_${tag}.err" | awk -F: '{s+=$2} END{print s}')" \
    "$(grep -c '⚠' "raw/43_${tag}.out" "raw/43_${tag}.err" | awk -F: '{s+=$2} END{print s}')" \
    "$(grep -c '✅' "raw/43_${tag}.out" | tr -d ' ')" \
    "$(grep -h '期待表' "raw/43_${tag}.out" "raw/43_${tag}.err" | head -1 | cut -c1-70)" \
    "$(grep -c '実態=karo-mac\|実態=ashigaru-mac' "raw/43_${tag}.out" "raw/43_${tag}.err" | awk -F: '{s+=$2} END{print s}')"
}
echo "# round2: SECTION18_ROLES_LIB を生きた樹の lib へ(己の樹の lib は bash 3.2 で source が落ち器が黙る・raw/34)。round1 は raw/31_tests_round1.txt に残置。"
echo "# km-214 両対照 + fail-closed(刻 $(date '+%Y-%m-%dT%H:%M:%S%z')・/bin/bash $(/bin/bash -c 'echo ${BASH_VERSION}')・tmux $(/opt/homebrew/bin/tmux -V)・TMUX=${TMUX:+set})"
echo "## A 前版(生きた版の写し・sha $(shasum -a 256 $BEFORE | cut -c1-16)) ―― 陽性対照: 前方一致で Mac の pane を掴む形"
run A_before "$BEFORE" PANE_REGISTRY="$REG"
grep -h '❌' raw/43_A_before.out raw/43_A_before.err | head -4 | sed 's/^/    /' | cut -c1-120
echo "## B 後版(己の樹・sha $(shasum -a 256 $AFTER | cut -c1-16)) ―― 正しい registry・python 在り"
run B_after_ok "$AFTER" PANE_REGISTRY="$REG" PYTHON="$PY_VENV"
grep -h '期待表\|⚠' raw/43_B_after_ok.out raw/43_B_after_ok.err | head -9 | sed 's/^/    /' | cut -c1-120
echo "## C 後版 fail-closed 四形(各々別の出目)"
run C1_no_registry "$AFTER" PANE_REGISTRY="raw/seed/registry_nai.yaml" PYTHON="$PY_VENV"
run C2_parse_error "$AFTER" PANE_REGISTRY="raw/seed/registry_broken.yaml" PYTHON="$PY_VENV"
run C3_empty      "$AFTER" PANE_REGISTRY="raw/seed/registry_empty.yaml" PYTHON="$PY_VENV"
run C3b_no_mainpc "$AFTER" PANE_REGISTRY="raw/seed/registry_no_mainpc.yaml" PYTHON="$PY_VENV"
run C4_no_python  "$AFTER" PANE_REGISTRY="$REG" PYTHON="/nonexistent/python3" PATH="/nonexistent_bin"
for t in C1_no_registry C2_parse_error C3_empty C3b_no_mainpc C4_no_python; do echo "    ${t}: $(grep -h '期待表' raw/43_${t}.err raw/43_${t}.out | head -1 | cut -c1-110)"; done
echo "## D 後版 陰性対照: 前版の tmux_target を持つ session が★無い★のに違反を数へぬ(⚠ のみ)・前版は偽の ❌ を数へる"
echo "    前版 ❌(偽の掴み)=$(grep -c '実態=karo-mac\|実態=ashigaru-mac' raw/43_A_before.out raw/43_A_before.err | awk -F: '{s+=$2} END{print s}') / 後版 ❌(偽の掴み)=$(grep -c '実態=karo-mac\|実態=ashigaru-mac' raw/43_B_after_ok.out raw/43_B_after_ok.err | awk -F: '{s+=$2} END{print s}')"
echo "## E 前後の rc と violations の刷り(器の末尾の行)"
for t in A_before B_after_ok; do echo "    ${t}: $(grep -h 'violations\|warnings\|違反\|警告' raw/43_${t}.out raw/43_${t}.err | tail -2 | tr '\n' ' ' | cut -c1-160)"; done
