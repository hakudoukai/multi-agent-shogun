#!/bin/bash
# 65_merge_tree_taishou.sh ―― 零(衝突 0)の陽性対照: 残45本の tip 同士 45×44/2 対へ同じ器(merge-tree --write-tree)を当て、鳴る対が在る事を示す。
# 用法: bash driver/65_merge_tree_taishou.sh <REPO> raw/02_karo_60tips_utsushi.tsv raw/03_karo_fuyou15_utsushi.tsv raw/90_merge_tree_taishou.tsv
set -u
REPO=$1; TIPS=$2; FUYOU=$3; OUT=$4
awk -F'\t' 'NR>1{print $2}' "$FUYOU" | LC_ALL=C sort > /tmp/km100_fuyou_names.$$
awk -F'\t' 'NR>1{print $1"\t"$2}' "$TIPS" | LC_ALL=C sort -k2 > /tmp/km100_all.$$
: > /tmp/km100_nokori.$$
while IFS=$'\t' read -r s n; do grep -qxF "$n" /tmp/km100_fuyou_names.$$ || printf '%s\t%s\n' "$s" "$n" >> /tmp/km100_nokori.$$; done < /tmp/km100_all.$$
N=$(grep -c '' /tmp/km100_nokori.$$)
printf '# 残=%s 対=%s\n' "$N" $((N*(N-1)/2)) > "$OUT"
printf 'A\tB\trc\tconflict_n\tfiles\n' >> "$OUT"
pairs=0; ring=0
L=(); while IFS= read -r l; do L+=("$l"); done < /tmp/km100_nokori.$$   # bash 3.2 に mapfile 無し
[ "${#L[@]}" = "$N" ] || { echo "★配列長 ${#L[@]} ≠ N $N ―― 止★" >&2; exit 9; }
for ((i=0;i<N;i++)); do for ((j=i+1;j<N;j++)); do
  sa=${L[i]%%$'\t'*}; na=${L[i]#*$'\t'}; sb=${L[j]%%$'\t'*}; nb=${L[j]#*$'\t'}
  [ -n "$sa" ] && [ -n "$sb" ] || { echo "★空 sha ―― 止★" >&2; exit 9; }
  o=$(git -c core.quotePath=false -C "$REPO" merge-tree --write-tree --name-only "$sa" "$sb" 2>&1); rc=$?
  [ "$rc" -le 1 ] || { echo "★merge-tree rc=$rc(器の誤り) $na $nb: $o ―― 止★" >&2; exit 9; }
  pairs=$((pairs+1))
  if [ "$rc" != 0 ]; then ring=$((ring+1)); f=$(printf '%s\n' "$o" | tail -n +2 | grep -v '^$' | tr '\n' ';'); printf '%s\t%s\t%s\t%s\t%s\n' "$na" "$nb" "$rc" "$(printf '%s\n' "$o" | tail -n +2 | grep -v '^$' | grep -c '')" "$f" >> "$OUT"; fi
done; done
printf '# 走つた対=%s 鳴つた対=%s\n' "$pairs" "$ring" >> "$OUT"
rm -f /tmp/km100_fuyou_names.$$ /tmp/km100_all.$$ /tmp/km100_nokori.$$
echo "pairs=$pairs ring=$ring"
