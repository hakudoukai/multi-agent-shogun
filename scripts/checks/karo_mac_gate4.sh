#!/bin/bash
# karo_mac_gate4.sh ―― 家老mac の門(四條)を ★落ちた時 に止まる★ 形 で当てる。
#
# 由来: 2026-09-09。家老 が `git diff --cached --check && echo 通; git commit …` と繋いだ為、
#       ★check が 4 行 の末尾空白 を吐いたのに 後段 の commit/push が走つた★。
#       ―― ★門 は「当てた」だけ では 門 に成らぬ。落ちた時 に 止まる 形 で書かねば 門 では無い。★
#
# usage: bash scripts/checks/karo_mac_gate4.sh <worktree> <path...>
#   rc=0 : 四條 悉く 満つ(押してよい)
#   rc!=0: 何處 が落ちたか を stderr へ出して ★止まる★
set -u
W="${1:?usage: karo_mac_gate4.sh <worktree> <path...>}"; shift
[ $# -ge 1 ] || { echo "★path が無い★" >&2; exit 2; }
cd "$W" || { echo "★樹 が無い: $W★" >&2; exit 2; }

fail=0
say(){ printf '%s\n' "$*" >&2; }

# ―― 條④ diff --check(末尾空白・空白のみ の行・CRLF)
out=$(git diff --cached --check -- "$@" 2>&1); rc=$?
if [ $rc -ne 0 ] || [ -n "$out" ]; then
  n=$(printf '%s\n' "$out" | grep -c .)
  say "★條④ diff --check が落ちた ―― $n 行★"
  printf '%s\n' "$out" | head -20 | sed 's/^/    /' >&2
  fail=1
else
  say "條④ diff --check = 0"
fi

# ―― staged が空 で無い事(空 commit を「通」と読まぬ)
n_staged=$(git diff --cached --name-only -- "$@" | grep -c .)
if [ "$n_staged" -eq 0 ]; then
  say "★staged が 0 file ―― 押す物 が無い(之 を『通』と読むな)★"
  fail=1
else
  say "staged = $n_staged file"
fi

# ―― 條① 押し先 が origin に在るか(枝 の追跡)
br=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if git rev-parse --verify -q "refs/remotes/origin/$br" >/dev/null; then
  say "條① 遠 の枝 refs/remotes/origin/$br 在り"
else
  say "★條① 遠 に枝 origin/$br が無い ―― 押し先 を確かめよ★"
  fail=1
fi

if [ $fail -ne 0 ]; then
  say ""
  say "★門 が落ちた。押すな。★"
  exit 1
fi
say "★門 四條 通。押してよい。★"
exit 0
