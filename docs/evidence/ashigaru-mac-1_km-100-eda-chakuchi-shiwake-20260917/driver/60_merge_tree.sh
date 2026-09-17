#!/bin/bash
# 60_merge_tree.sh ―― ㋔ PR 衝突の決定測り。`git merge-tree --write-tree` は ★refs/工作樹/index を触らず★ object(dangling tree)のみ書く。
# rc=0 衝突無 / rc=1 衝突有(衝突 file 名を刷る) / その他=器の誤り。用法: bash driver/60_merge_tree.sh <REPO> <MAIN sha> raw/05_warimochi18.tsv raw/89_merge_tree.tsv
set -u
REPO=$1; MAIN=$2; WARI=$3; OUT=$4
printf 'branch\tsha12\tmerge_tree_rc\tconflict_files_n\tconflict_files\n' > "$OUT"
while IFS=$'\t' read -r sha name; do
  [ -z "$sha" ] && continue
  o=$(git -c core.quotePath=false -C "$REPO" merge-tree --write-tree --name-only "$MAIN" "$sha" 2>&1); rc=$?
  files=$(printf '%s\n' "$o" | tail -n +2 | grep -v '^$' | grep -v '^[0-9a-f]\{40\}$' | tr '\n' ';')
  n=$(printf '%s\n' "$o" | tail -n +2 | grep -v '^$' | grep -c '')
  [ "$rc" = 0 ] && { n=0; files=''; }
  printf '%s\t%s\t%s\t%s\t%s\n' "$name" "${sha:0:12}" "$rc" "$n" "$files" >> "$OUT"
done < "$WARI"
