#!/bin/sh
# hashiru.sh ―― ★argv を其の儘 焼く 走り手★（km-220 再提出・軍師mac 判 seq342967 の療法）
# 因: 初提出の raw 26本には argv が一字も焼かれて居らず(grep 'argv' = 0本)、
#     argv は紙の表に「argv の要」として★要約★で書かれて居た。
#     雛形 v1.3 ③ は「同一 run の argv 其の儘」を求める ∴ 走り手が己で焼く形へ据ゑる。
# 使ひ方: hashiru.sh <札> -- <命 argv...>
#   産: raw2/<札>.argv (cwd/刻/env/argc/argv 各一行/rc) / .out / .err / .rc
# ★rc は管を通さぬ★ ―― `"$@" > out 2> err; rc=$?` の形で取る。
# ★己の rc に門の rc を混ぜぬ★ ―― 走り手は常に 0 で了へ、門の rc は .rc へ焼く。
set -u
[ $# -ge 3 ] || { echo '★拒★ 使ひ方: hashiru.sh <札> -- <命...>' >&2; exit 2; }
lab="$1"; shift
[ "$1" = "--" ] || { echo "★拒★ 第二引数は -- でなければならぬ: $1" >&2; exit 2; }
shift
D="$(/usr/bin/dirname "$0")/../raw2"
[ -d "$D" ] || { echo "★拒★ raw2 が無い: $D" >&2; exit 2; }
A="$D/$lab.argv"
{
  printf '札=%s\n' "$lab"
  printf 'cwd=%s\n' "$(/bin/pwd)"
  printf '刻(UTC)=%s\n' "$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')"
  printf 'env DASUMAE_JOU4_SCOPE=%s\n' "${DASUMAE_JOU4_SCOPE-★未設定★}"
  printf 'env KM_GATE_MANIFEST_BASE=%s\n' "${KM_GATE_MANIFEST_BASE-★未設定★}"
  printf 'argc=%d\n' "$#"
  i=0
  for a in "$@"; do i=$((i+1)); printf 'argv[%d]=%s\n' "$i" "$a"; done
} > "$A"
"$@" > "$D/$lab.out" 2> "$D/$lab.err"
rc=$?
printf '%d\n' "$rc" > "$D/$lab.rc"
printf 'rc=%d\n' "$rc" >> "$A"
# ★空の stream は二段で書け★(裁310228⑶) ―― 0byte なら非空白字の一行を★註として★足す。
for s in out err; do
  f="$D/$lab.$s"
  if [ ! -s "$f" ]; then
    printf '(★空★ ―― %s.%s は實走で一字も出なかつた。之は後から走り手が書いた★註★の一行であり、測りを書き替へた物ではない。裁310228⑶「空である旨を非空白字で一行」に從ふ。)\n' "$lab" "$s" > "$f"
  fi
done
exit 0
