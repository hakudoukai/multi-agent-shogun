#!/bin/bash
# 61_locale.sh ―― ★專任2 の直しの出 byte が「土地(locale)の函数」か検める★
#   當席は「\266 は 1byte 0xB6 ゆゑ不当 UTF-8」と當て、60 で ★外した★(c2 b6 が出た)。
#   ∴ 外した理由を測る ―― tr は土地に依つて別の byte を吐くか。
# 使ひ方: 61_locale.sh <作業dir>
set -u
WD="$1"; mkdir -p "$WD"
V=$(printf '50\n9999')
printf '#土地\t出byte列\tUTF-8\t判\n'
for L in en_US.UTF-8 C POSIX ja_JP.UTF-8; do
  f="$WD/loc_$(printf '%s' "$L" | tr '.' '_').bin"
  LC_ALL="$L" printf '%s' "$V" | LC_ALL="$L" tr '\n\r\t' '\266\215\211' > "$f" 2>"$WD/tr.err"
  by=$(od -An -tx1 < "$f" | tr -s ' \n' ' ' | sed 's/^ //; s/ $//')
  u=$(python3 -c "
import sys
b=open(sys.argv[1],'rb').read()
try:
    s=b.decode('utf-8'); print('妥当|%r'%s)
except UnicodeDecodeError as e: print('★不当★|%s'%e)
" "$f")
  han=OK; case "$u" in ★不当★*) han='★此の土地では不当 UTF-8 を吐く★';; esac
  printf '%s\t%s\t%s\t%s\n' "$L" "$by" "$u" "$han"
done
printf '#―― 常駐器が実際に置かれる土地 ――\n'
printf 'launchd/cron 既定\tLANG/LC_ALL 未設定 → C 相当\t―\t上の C 行を見よ\n'
printf '現シェル\tLANG=%s LC_ALL=%s\t―\t―\n' "${LANG-★未設定★}" "${LC_ALL-★未設定★}"
# 陽性対照: 改行が在る形 / 陰性対照: 無い形(土地に依らず不変の筈)
printf '#対照\n'
for L in en_US.UTF-8 C; do
  a=$(LC_ALL="$L" printf '%s' '30' | LC_ALL="$L" tr '\n\r\t' '\266\215\211' | od -An -tx1 | tr -s ' \n' ' ' | sed 's/^ //; s/ $//')
  printf '陰性(改行無 30)\t%s\t%s\t土地に依らず不変\n' "$L" "$a"
done
