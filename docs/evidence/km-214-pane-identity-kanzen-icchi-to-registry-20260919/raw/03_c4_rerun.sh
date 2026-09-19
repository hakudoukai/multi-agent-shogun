#!/bin/bash
# km-214 C4(python 無し)の取り直し ―― round2 の C4 は PATH を空にした為 dirname も無く器が期待表の前で落ちた(rc127・出目無し)。
# 此処では要る外部命令だけを raw/seed/bin_no_python に link し(python3 は入れぬ)、PYTHON も無い path へ。
set -u
cd "$(dirname "$0")/.."
WT=/Users/momizimac/wt/a1-km214
BIN="$(pwd)/raw/seed/bin_no_python"
echo "# C4 取り直し(刻 $(date '+%Y-%m-%dT%H:%M:%S%z'))・PATH=${BIN}(python3 無し: $(ls "$BIN" | grep -c python))"
env -i PATH="$BIN" HOME="$HOME" TMUX="${TMUX:-}" PYTHON=/nonexistent/python3 PANE_REGISTRY="$WT/queue/pane_registry.yaml" SECTION18_ROLES_LIB=/Users/momizimac/multi-agent-shogun/lib/_section18_roles.sh TMUX_CMD=/opt/homebrew/bin/tmux LAST_RUN_JSON=raw/30_C4b_last_run.json /bin/bash "$WT/scripts/checks/pane_identity.sh" > raw/30_C4b_no_python.out 2> raw/30_C4b_no_python.err; rc=$?
for f in raw/30_C4b_no_python.out raw/30_C4b_no_python.err; do [ -s "$f" ] || printf '\n' > "$f"; done
echo "C4b_no_python | rc=${rc} | 期待表行=[$(grep -h '期待表' raw/30_C4b_no_python.err raw/30_C4b_no_python.out | head -1 | cut -c1-110)] | ❌=$(grep -c '❌' raw/30_C4b_no_python.out raw/30_C4b_no_python.err | awk -F: '{s+=$2} END{print s}')"
echo "対照(同じ PATH に python3 を足す): $(mkdir -p raw/seed/bin_with_python && cp -R "$BIN"/. raw/seed/bin_with_python/ && ln -sf /Users/momizimac/multi-agent-shogun/.venv/bin/python3 raw/seed/bin_with_python/python3 && env -i PATH="$(pwd)/raw/seed/bin_with_python" HOME="$HOME" TMUX="${TMUX:-}" PYTHON=/nonexistent/python3 PANE_REGISTRY="$WT/queue/pane_registry.yaml" SECTION18_ROLES_LIB=/Users/momizimac/multi-agent-shogun/lib/_section18_roles.sh TMUX_CMD=/opt/homebrew/bin/tmux LAST_RUN_JSON=raw/30_C4c_last_run.json /bin/bash "$WT/scripts/checks/pane_identity.sh" 2>&1 | grep -h '期待表' | head -1 | cut -c1-100)"
