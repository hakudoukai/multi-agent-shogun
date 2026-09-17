#!/bin/bash
# 90_final_gen.sh ―― 最終臺帳を append.py のみで三度生成し cmp で当てる(裁326273)。cwd=子束。$1=append.py
set -u
AP="$1"; mkdir -p 99_final_gen
{ echo 00_tsuimei.md; find driver raw -type f; echo manifest_jou1.txt; echo raw_append_jou1.out; echo raw_append_jou1.err; } | LC_ALL=C sort > 99_final_gen/59_argv.txt
for i in 1 2 3; do rm -f "99_final_gen/gen$i.txt"; xargs python3 -B "$AP" "99_final_gen/gen$i.txt" < 99_final_gen/59_argv.txt > "99_final_gen/gen$i.append.out" 2>&1; echo "gen$i append rc=$?"; sleep 1; done
rm -f manifest.txt; xargs python3 -B "$AP" manifest.txt < 99_final_gen/59_argv.txt > raw_append.out 2> raw_append.err; echo "manifest append rc=$?"
{ for f in 99_final_gen/gen1.txt 99_final_gen/gen2.txt 99_final_gen/gen3.txt manifest.txt; do printf '%s sha256=%s bytes=%s lines=%s\n' "$f" "$(shasum -a 256 < "$f" | cut -c1-64)" "$(stat -f %z "$f")" "$(grep -c '' "$f")"; done
  cmp 99_final_gen/gen1.txt 99_final_gen/gen2.txt; echo "cmp gen1 gen2 rc=$?"
  cmp 99_final_gen/gen2.txt 99_final_gen/gen3.txt; echo "cmp gen2 gen3 rc=$?"
  cmp 99_final_gen/gen1.txt 99_final_gen/gen3.txt; echo "cmp gen1 gen3 rc=$?"
  cmp 99_final_gen/gen1.txt manifest.txt; echo "cmp gen1 manifest.txt rc=$?"
  printf 'x\n' > 99_final_gen/posctl_x.txt; cmp 99_final_gen/posctl_x.txt 99_final_gen/gen1.txt >/dev/null 2>&1; echo "陽性対照 cmp x gen1 rc=$?"
  echo "刻=$(date '+%Y-%m-%dT%H:%M:%S%z')"; } > 99_final_gen/70_cmp_result.txt; cat 99_final_gen/70_cmp_result.txt
