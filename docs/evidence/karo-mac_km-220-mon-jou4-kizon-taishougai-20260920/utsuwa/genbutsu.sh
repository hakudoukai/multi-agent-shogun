#!/bin/bash
# genbutsu.sh ―― ★現物対照の argv を 其の儘 展べて 走らせる 器★(km-220 再提出)
# 因: 初提出の紙は argv を `<87本>` `<56本>` と★要約★で書いた(軍師mac 判 seq342967)。
#     ∴ 母數を find で作り、hashiru.sh に argv 其の儘を渡して焼かせる。
# 使ひ方: genbutsu.sh <札> <他席の樹の根> <束の相対path> <門の path>
# ★他席の樹は讀取のみ★ ―― find で歩くのみ・HEAD/index/作業樹に一指も触れぬ(第一条「読み取りは可」)
set -u
[ $# -eq 4 ] || { echo '★拒★ 引数は4つ: <札> <樹の根> <束の相対path> <門>' >&2; exit 2; }
lab="$1"; tree="$2"; rel="$3"; gate="$4"
H="$(/usr/bin/dirname "$0")/hashiru.sh"
[ -f "$H" ] || { echo "★拒★ 走り手が無い: $H" >&2; exit 2; }
[ -d "$tree/$rel" ] || { echo "★拒★ 歩き根が無い: $tree/$rel" >&2; exit 2; }
files=()
while IFS= read -r -d '' f; do files+=("$f"); done < <(/usr/bin/find "$tree/$rel" -type f -print0 | /usr/bin/sort -z)
printf '母數=%d本 ―― 歩き根=%s/%s ／ 深さ=無制限 ／ type=f ／ 刻(UTC)=%s\n' \
  "${#files[@]}" "$tree" "$rel" "$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')" >&2
[ "${#files[@]}" -gt 0 ] || { echo '★拒★ 母數=0 ―― 歩き根を検めよ' >&2; exit 2; }
exec /bin/sh "$H" "$lab" -- /bin/bash "$gate" -- "${files[@]}"
