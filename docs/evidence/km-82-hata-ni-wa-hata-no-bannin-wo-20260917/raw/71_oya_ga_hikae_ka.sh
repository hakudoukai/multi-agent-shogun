#!/bin/bash
# ★commit を分けた時の断り検め★ ―― 70 は main を基点に測る故、前round分を独立 commit に
#   分けた形(親=前round・子=本弾)を「断り要」と鳴らし続ける。本器は其の形を正しく測る:
#   ★本弾 commit の親の blob が控と一致すれば、本弾の commit は本弾の分しか運ばぬ★。
#   使ひ方: 71_oya_ga_hikae_ka.sh <repo> <path> <控file> <親commit>
R="$1"; P="$2"; H="$3"; OYA="$4"
[ -n "$OYA" ] || { echo "usage: 71_oya_ga_hikae_ka.sh <repo> <path> <控> <親commit>" >&2; exit 2; }
ob=$(git -C "$R" rev-parse "$OYA:$P" 2>/dev/null) || { echo "★親 $OYA に $P が無い★" >&2; exit 2; }
# ★-C は path も其の repo 根から解く★ ゆゑ 控/今 は -C を付けずに(cwd 起点で)測る
hb=$(git hash-object "$H") || { echo "★控 $H が讀めぬ★" >&2; exit 2; }
ib=$(git hash-object "$R/$P") || { echo "★今 $R/$P が讀めぬ★" >&2; exit 2; }
printf '親(%s) blob=%s\n控          blob=%s\n今          blob=%s\n' "$OYA" "${ob:0:12}" "${hb:0:12}" "${ib:0:12}"
printf '親⇔控 の相違行=%s / 控⇔今 の相違行=%s\n' \
  "$(git -C "$R" show "$OYA:$P" | diff - "$H" | grep -c '^[<>]')" \
  "$(diff "$H" "$R/$P" | grep -c '^[<>]')"
if [ "$ob" = "$hb" ]; then
  echo "★断り不要★ 親の blob = 控 ∴ 本弾の commit は ★本弾の分のみ★ を運ぶ"
  exit 0
fi
echo "★断り要★ 親の blob ≠ 控 ∴ 本弾の commit は前round の分も運ぶ" >&2
exit 1
