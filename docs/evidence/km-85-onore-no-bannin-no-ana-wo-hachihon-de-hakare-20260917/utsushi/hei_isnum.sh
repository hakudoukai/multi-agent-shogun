#!/bin/bash
# ★寫し器★ hei_isnum(㋔ の裏付け・型=丙) ―― scripts/checks/karo_mac_dasumae_gate.sh:29 と :36 の★逐語一行づつ★
#   作つた刻=2026-09-17T11:40:17+0900 ／ 生器へは一字も書いて居らぬ
set -u
# ===== 寫し ここから(逐語) =====
is_num(){ case "${1:-}" in (''|*[!0-9]*) return 1 ;; (*) return 0 ;; esac }
num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }
# ===== 寫し ここまで =====
# ===== 附録(當席の駆動部) =====
v="${1-}"
if is_num "$v"; then a=通; else a=落; fi
if num_same_op "$v"; then b=通; else b=落; fi
if num_same_op "$v" && [ "$v" -ge 0 ] 2>/dev/null; then c=通; else c=落; fi
printf "%s\t%s\t%s\n" "$a" "$b" "$c"
