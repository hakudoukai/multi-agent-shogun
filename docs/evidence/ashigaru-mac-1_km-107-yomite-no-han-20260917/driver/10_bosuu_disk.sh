#!/bin/bash
# 10_bosuu_disk.sh ―― ★disk の母數★ を集める(km-107 ㋐)。
# 宣(逐語): 歩き根 = repo 根(/Users/momizimac/multi-agent-shogun)。根直下の .git のみ剪定。
#   定義A = regular file(-type f・symlink は含まぬ) ∧ basename が大小文字を區別せず 'manifest' を含む(-iname '*manifest*')。
#   print(改行區切) と print0(NUL區切) の ★二器★ で出し、本數を grep -c '' と NUL 數 で別々に數へる。
#   rc は pipe を通さず取る。stderr(權限拒否等)は 10_find.err へ。
set -u
REPO=/Users/momizimac/multi-agent-shogun
cd "$(dirname "$0")/.." || exit 2
mkdir -p raw
{
  echo "刻=$(date '+%Y-%m-%dT%H:%M:%S%z')"
  echo "歩き根=$REPO"
  echo "find=$(command -v find)"
  echo "find_version=$(find --version 2>&1 | head -1)"
  echo "grep=$(command -v grep)"
  echo "grep_version=$(command grep --version 2>&1 | head -1)"
  echo "uname=$(uname -a)"
  echo "cwd=$(pwd)"
} > raw/10_env.txt
find "$REPO" -path "$REPO/.git" -prune -o -type f -iname '*manifest*' -print  > raw/10_disk_A.lst 2> raw/10_find.err
echo "find_print_rc=$?" > raw/10_find.rc
find "$REPO" -path "$REPO/.git" -prune -o -type f -iname '*manifest*' -print0 > raw/10_disk_A.nul 2> raw/10_find0.err
echo "find_print0_rc=$?" >> raw/10_find.rc
n_grep=$(command grep -c '' raw/10_disk_A.lst); rc_g=$?
n_nul=$(tr -dc '\0' < raw/10_disk_A.nul | wc -c | tr -d ' '); rc_n=$?
n_wcl=$(wc -l < raw/10_disk_A.lst | tr -d ' ')
{
  echo "刻=$(date '+%Y-%m-%dT%H:%M:%S%z')"
  echo "定義A_本數[grep -c '' 行]=$n_grep rc=$rc_g"
  echo "定義A_本數[NUL 數]=$n_nul rc=$rc_n"
  echo "定義A_本數[wc -l 改行數]=$n_wcl"
  echo "食ひ違ひ(grep-NUL)=$((n_grep - n_nul))"
  echo "find.err 行=$(command grep -c '' raw/10_find.err)"
  cat raw/10_find.rc
} > raw/10_disk_A_count.txt
cat raw/10_disk_A_count.txt
