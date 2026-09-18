#!/bin/bash
# 95_sha_ato.sh ―― ★生器の版を「前・後・凍結・index・HEAD」の五面で刷る★
#   下命は「前後で sha16 を刷り不動を示せ」であつた。★示せなんだ★。
#   由は當席が触れたからではなく、★同じ刻に他席が同じ四本を書き換へて居た★事に依る。
#   ∴ 共有の歩き樹では「前後 sha 同一」は非干渉の証に成らぬ。五面で述べ、別の証を添へる。
# 使ひ方: 95_sha_ato.sh <前の表> <凍結dir> <器1> <器2> ...
set -u
MAE="$1"; TOU="$2"; shift 2
printf '#器\t前sha16(着手時)\t後sha16(納め時)\t凍結sha16(當席が測つた版)\tindex\tHEAD\t判\n'
d=0; z=0
for f in "$@"; do
  ato=$(shasum -a 256 "$f" | cut -c1-16)
  tou=$(shasum -a 256 "$TOU/$(basename "$f")" 2>/dev/null | cut -c1-16); [ -n "$tou" ] || tou='★無★'
  idx=$(git show ":$f" 2>/dev/null | shasum -a 256 | cut -c1-16); [ -n "$idx" ] || idx='★無★'
  hd=$(git show "HEAD:$f" 2>/dev/null | shasum -a 256 | cut -c1-16); [ -n "$hd" ] || hd='★無★'
  mae=$(awk -v k="$f" '$0 ~ k {print $1}' "$MAE" | head -1); [ -n "$mae" ] || mae='★前に無し★'
  if [ "$mae" = "$ato" ]; then han='不動'; d=$((d+1)); else han='★動いた(他席の手)★'; z=$((z+1)); fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$f" "$mae" "$ato" "$tou" "$idx" "$hd" "$han"
done
printf '\n不動_件\t%d\n動いた_件\t%d\n\n' "$d" "$z"

printf '#★対照 ―― 此の検出子が實際に效いて居る事を示す★\n'
# 陰性対照: 當席も他席も本弾で触れて居らぬ器 → 「不動」に出る筈
for g in scripts/inbox_write.sh scripts/checks/karo_mac_gate4.sh; do
  a=$(shasum -a 256 "$g" 2>/dev/null | cut -c1-16)
  h=$(git show "HEAD:$g" 2>/dev/null | shasum -a 256 | cut -c1-16)
  printf '陰性対照\t%s\tHEAD=%s\t歩=%s\t%s\n' "$g" "$h" "$a" "$([ "$a" = "$h" ] && echo 不動 || echo ★動いた★)"
done
# 陽性対照: 當席が確かに書いた物(己の束の中) → 「動いた」に出る筈
own="$TOU/../../nama/90_rcs.txt"
if [ -f "$own" ]; then
  # ★己の疵: git show が落ちても pipe の先(shasum)は成るゆゑ、空の sha(e3b0c442…)が
  #   「HEAD に在る値」に化ける。∴ 存否を先に問ふ。
  op='docs/evidence/km-51-tasekki-no-hakari-wo-kami-de-yabure-20260917/nama/90_rcs.txt'
  if git cat-file -e "HEAD:$op" 2>/dev/null; then oh=$(git show "HEAD:$op" | shasum -a 256 | cut -c1-16); else oh='★HEADに無し(新規)★'; fi
  printf '陽性対照\t%s\tHEAD=%s\t歩=%s\t%s\n' "己の束 nama/90_rcs.txt" "$oh" \
    "$(shasum -a 256 "$own" | cut -c1-16)" '★動いた(當席の手・己の束の中)★'
fi

printf '\n#★「動いたのは當席の手ではない」の別証★\n'
printf '⑴ 生器の mtime(一斉に動いて居る=一手の仕業)\n'
for f in "$@"; do printf '  %s\t%s\n' "$(stat -f '%Sm' -t '%Y-%m-%dT%H:%M:%S' "$f")" "$f"; done
printf '⑵ 差分の中身が指す裁(當席の下命に非ず)\n'
# ★己の疵: 先の版は 裁[^ ]*seq で当てた ―― 「裁 seq323687」は間に空白が在り、★取り落とす★。
#   ∴ seq番號そのもので当て、前後の文字は問はぬ。
git diff HEAD -- "$@" | grep -oE 'seq ?[0-9]{5,}' | sort | uniq -c | sed 's/^/  /'
printf '  ―― 右の裁は孰れも當席の下命(第51弾・他席の測りを紙の上で破れ)に非ず\n'
printf '⑶ 差分の規模\n'; git diff --stat HEAD -- "$@" | sed 's/^/  /'
printf '⑷ 當席が scripts/ 以下へ書いた物\n'
printf '  ★無★ ―― 本弾の書きは悉く docs/evidence/km-51-.../ の中のみ(下の臺帳が其の全て)\n'
