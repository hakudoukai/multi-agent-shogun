#!/usr/bin/env bash
# 負テスト器(現形) ―― ~/bin/fleet_liveness_check.sh の L18/28/31/32/46 を★逐語で★写し、
# 閾の値が比較器に届く迄を再現する(家老mac km-76・読取のみで作つた複製・本体は触らず)
set -uo pipefail
MIN_WIDTH="${FLEET_MIN_PANE_WIDTH:-80}"
is_num(){ case "${1:-}" in (''|*[!0-9]*) return 1 ;; (*) return 0 ;; esac }
is_num "${MIN_WIDTH}" || { printf '%s\n' "[fleet_liveness] ★閾 MIN_WIDTH が數でない(「${MIN_WIDTH}」) ―― 既定 80 へ倒す(fail-closed)★" >&2; MIN_WIDTH=80; }
w=40   # ★狹い pane(40桁)= 必ず報せねばならぬ形★
if [ -n "$w" ] && [ "$w" -lt "$MIN_WIDTH" ] 2>/dev/null; then
  printf '狹い pane を報せた(正)\n'
else
  printf '★報せ落ち(狹い pane が見逃された)★\n'
fi
printf 'RESULT MIN_WIDTH=〔%s〕\n' "${MIN_WIDTH}"
