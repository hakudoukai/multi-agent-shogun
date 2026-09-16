#!/bin/bash
# 98_kami.sh ―― ★紙に書いた數を、紙とは別の器で数へ直す★(裁: 便の數は紙から抽出せよ)
# 使ひ方: 98_kami.sh <束path>
set -u
B="$1"
# ★走り中の rc は .rcs に在る(90_rcs.txt は前回の物) ―― 己の行は未だ無いゆゑ +1 する★
RCS="$B/nama/.rcs"; [ -s "$RCS" ] || RCS="$B/nama/90_rcs.txt"
p(){ printf '%s\t%s\t%s\n' "$1" "$2" "$3"; }
printf '#項\t紙の申し立て\t器の實測\t判\n'
chk(){ # $1=項 $2=紙の値 $3=實測
  printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$([ "$2" = "$3" ] && echo 合 || echo ★違★)"
}
kami(){ grep -oE "$1" "$B/km51_report.md" | head -1 | grep -oE '[0-9]+' | head -1; }

chk '器_本'   "$(kami '器 [0-9]+ 本')"        "$(ls -1 "$B/ki" | wc -l | tr -d ' ')"
chk '生_本'   "$(kami '生 [0-9]+ 本')"        "$(ls -1 "$B/nama" | grep -vc '^98_kami\.')"
# ★90_rcs.txt は driver が最後に書く ∴ 此の器が走る時、己の行は未だ無い。+1 して比べ、其の旨を宣す。
chk 'rc_本'   "$(kami '[0-9]+本 悉く rc=0')"   "$(( $(grep -c '' "$RCS") + 1 ))"
chk 'rc0_本'  "$(( $(grep -c '' "$RCS") + 1 ))" "$(( $(grep -c 'rc=0' "$RCS") + 1 ))"
chk '食違_組' "$(kami '食ひ違ひ = [0-9]+組')"  "$(grep -c '^食ひ違ひ	' "$B/nama/70_monosashi.tsv")"
chk '有害_組' "$(grep -oE '\| \*\*57\*\* \|' "$B/km51_report.md" | head -1 | grep -oE '[0-9]+')" \
              "$(awk -F'\t' '$1=="當席_有害_組"{print $2}' "$B/nama/70_monosashi.tsv")"
chk '母數_組' "$(kami '母數 [0-9]+ 組')"              "$(awk -F'\t' '$1=="母數_組"{print $2}' "$B/nama/70_monosashi.tsv")"
chk '閾_本'   '18'                             "$(sed -n '/③受け皿/,$p' "$B/nama/40_ichiyou.txt" | grep -cE '^[A-Z]')"
chk '己_閾'   '10'                             "$(grep -c '己へ書戻す' "$B/nama/40_ichiyou.txt")"
chk '別名_閾' '8'                              "$(grep -c '受け皿が別名' "$B/nama/40_ichiyou.txt")"
chk '動いた_件' '4'                            "$(awk -F'\t' '$1=="動いた_件"{print $2}' "$B/nama/95_sha_ato.txt")"
chk '不動_件'   '0'                            "$(awk -F'\t' '$1=="不動_件"{print $2}' "$B/nama/95_sha_ato.txt")"
printf '#註\t★rc の數は己の行(98_kami.txt)が未だ書かれて居らぬ ∴ +1 して比べた★\n#註\t★生の數は己の産物(98_kami.txt/.err)を除いて数へる ―― 紙は己を含む數を書けぬ★\n#註\t器16本の内 ki/71_kougodan.sh は★棄てた版★(bash では別名の受け皿を追へず 0 行を返した)。器の數には己(98_kami.sh)を含める。\n'
