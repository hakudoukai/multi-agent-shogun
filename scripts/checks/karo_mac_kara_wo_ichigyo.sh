#!/bin/bash
# karo_mac_kara_wo_ichigyo.sh ―― 「空の産物」を★源で★一行に直す器(裁 seq310228⑶)
#
# 何故要るか:
#   `cmd > x.out 2> x.err` の字面は、出目が無い時 ★0 byte の file★ を必ず残す。
#   0 byte の紙は「測つて居らぬ」と「測つたが何も出なかつた」を ★区別できぬ★。
#   裁 seq310228⑶ ―― ★0byte は源を直す(「空である旨の一行」を書く)形が正★。
#   ★出来た後に直すのではなく、書く其の場で直す。★ 之が「源」の意である。
#
# 使ひ方:
#   karo_mac_kara_wo_ichigyo.sh <out path> <err path> -- <命令...>
#   rc は ★命令の rc を其の儘返す★(器は rc を握り潰さぬ)。
#
# ★通すな★:
#   陽性対照として 0 byte で在らねばならぬ紙は此の器を通すな ―― 対照が壊れる。
#   除いた事と除いた本数を表に書け(「除いた」は「歩いて居らぬ」に非ず)。
set -u
if [ "$#" -lt 4 ]; then
  printf '%s\n' '★引数不足 ―― 要 <out> <err> -- <命令...>★ ★測る物が無い。測れぬは通さぬ(default-deny)★' >&2
  exit 2
fi
OUT="$1"; ERR="$2"; shift 2
if [ "$1" != "--" ]; then
  printf '★第三引数は -- で在らねばならぬ(受けた「%s」)★\n' "$1" >&2
  exit 2
fi
shift
"$@" > "$OUT" 2> "$ERR"
rc=$?
ichigyo(){
  if [ ! -s "$1" ]; then
    printf '(空 ―― %s に一行も出て居らぬ。元の寸法=0 byte。裁 seq310228⑶ に従ひ源で一行を書いた。)\n' "$2" > "$1"
  fi
}
ichigyo "$OUT" '標準出力'
ichigyo "$ERR" '標準エラー'
exit "$rc"
