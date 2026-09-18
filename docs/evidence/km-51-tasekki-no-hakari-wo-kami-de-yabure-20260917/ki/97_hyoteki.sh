#!/bin/bash
# 97_hyoteki.sh ―― ★的として名指された版に、番人は居るか★
#   專任2 は的を「branch=…/km-52…, tip=a4cafdf, tree=b4220e7a9b50」と宣した。
#   ∴ 其の版を引けば彼の測定は再現できねばならぬ。當席は引いて数へる。
# 使ひ方: 97_hyoteki.sh <commit> <器path>...
set -u
C="$1"; shift
printf '#的\t%s\n' "$C"
printf '#親\t%s\n' "$(git log -1 --format='%h %s' "$C^" 2>/dev/null)"
printf '#當席HEADとの共通祖先\t%s\n' "$(git merge-base "$C" HEAD 2>/dev/null)"
printf '#器path\tfix_threshold_件\t_th_say_件\tnum_same_op_件\t行\t判\n'
for p in "$@"; do
  if ! git cat-file -e "$C:$p" 2>/dev/null; then
    printf '%s\t-\t-\t-\t-\t★的の版に此の path 無し★\n' "$p"; continue
  fi
  b=$(git show "$C:$p")
  a=$(printf '%s\n' "$b" | grep -cE 'fix_threshold')
  c=$(printf '%s\n' "$b" | grep -cE '_th_say')
  d=$(printf '%s\n' "$b" | grep -cE 'num_same_op')
  n=$(printf '%s\n' "$b" | wc -l | tr -d ' ')
  if [ "$a" -eq 0 ] && [ "$c" -eq 0 ]; then han='★番人不在 ―― 此の版では彼の396組を再現できぬ★'; else han='番人在り'; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$p" "$a" "$c" "$d" "$n" "$han"
done
printf '#註\t彼の測定を再現し得るのは束内の写し(utsushi/scripts_*.sh)のみである。★的の宣と、測つた物が違ふ★\n'
