#!/bin/bash
# usage: 30_bashn.sh <utsushi-dir> <outdir>  ―― 三つの写しに bash -n を当てる
set -u
UT="${1:?usage: 30_bashn.sh <utsushi-dir> <outdir>}"
OUT="${2:?usage: 30_bashn.sh <utsushi-dir> <outdir>}"
{
  echo "=== ㋐-5 bash -n(写し三本) ==="
  for f in gate_base.sh gate_an_i.sh gate_an_ro.sh; do
    rc=0
    err="$(bash -n "$UT/$f" 2>&1)" || rc=$?
    printf '%s\trc=%s\t%s\n' "$f" "$rc" "${err:-（出目なし）}"
  done
  echo "=== 陽性対照: わざと壊した写しに鳴るか ==="
  tmp="$(mktemp -t km53bad).sh"
  { cat "$UT/gate_an_i.sh"; echo 'case x in'; } > "$tmp"
  rc=0; err="$(bash -n "$tmp" 2>&1)" || rc=$?
  printf 'gate_an_i.sh+壊し\trc=%s\t%s\n' "$rc" "$(printf '%s' "$err" | head -1)"
  rm -f "$tmp"
} > "$OUT/30_bashn.txt" 2>&1
cat "$OUT/30_bashn.txt"
