#!/bin/bash
# 80_totonoe.sh ―― 門へ出す前の整へ。①己の生成 text の正規化(末尾空白/CR 剥ぎ・EOF 改行丁度1) ②全 file 一覧 ③宣して除く物(第四の道: 0byte・他席/他器の写し=触らぬ) ④臺帳 append(束内相対・cd 束) ⑤出す前の門 ⑥gate7(README 胴=1 行目を除く)
# 用法: bash driver/80_totonoe.sh   (束の根で呼ぶ)   第二引数に "2" を渡すと第二走として log 名を変へる
set -u
REPO=/Users/momizimac/multi-agent-shogun; TS=$(date '+%Y%m%dT%H%M%S'); G=/usr/bin/grep; HASHIRI=${1:-1}
mkdir -p _gate; LOG=_gate/80_totonoe_h${HASHIRI}_$TS.log; echo "刻=$TS 走=$HASHIRI" > $LOG
# ① 正規化するのは ★己の器が生んだ text★ のみ(写し・他器の出力は触らぬ)
NORM=$(ls raw/*.tsv raw/*.txt an/*.tsv an/*.md 2>/dev/null | $G -vE 'raw/0[1-5]_|raw/30_d1|raw/31_d2')
{ echo "# 正規化前の寸法 刻=$TS  path bytes lines sha256"; for f in $NORM; do printf '%s %s %s %s\n' "$f" "$(stat -f %z "$f")" "$($G -c '' "$f")" "$(shasum -a 256 "$f" | cut -d' ' -f1)"; done; } > _gate/95_mae_sunpou_h${HASHIRI}_$TS.txt
for f in $NORM; do [ -s "$f" ] || continue; perl -pi -e 's/[ \t\r]+$//' "$f"; perl -0pi -e 's/\n+\z/\n/' "$f"; done
[ -f MANIFEST.txt ] && mv MANIFEST.txt _gate/MANIFEST_h$((HASHIRI-1))_$TS.txt
# ② 全 file
find . -type f -not -name README.md -not -name MANIFEST.txt -not -path './_gate/*' | sed 's#^\./##' | LC_ALL=C sort > _gate/96_zenbu_h${HASHIRI}_$TS.txt
# ③ 宣して除く: (a) 0byte(陰性の證) (b) 写し(raw/01〜05・他席の臺帳写し=触らぬ・末尾空白は原本の物) (c) 他器の出力写し(raw/75_logs/*.gate.* / *.jou1.* / raw/30_d1 raw/31_d2 の名一覧=名に制御字を含む行有)
{ echo "# argv から宣して除く(第四の道) 刻=$TS  理由 path bytes"
  while IFS= read -r f; do sz=$(stat -f %z "$f"); case "$f" in
    raw/0[1-5]_*) echo "写し(原本を触らぬ) $f $sz";;
    raw/75_logs/*) echo "他器(門/照合器)の出力写し $f $sz";;
    raw/30_d1_3dot_*|raw/31_d2_own_*|raw/32_anc_cands_*) echo "git名一覧(制御字を含む名有・正規化不可) $f $sz";;
    *) [ "$sz" = 0 ] && echo "0byte $f 0";; esac; done < _gate/96_zenbu_h${HASHIRI}_$TS.txt; } > _gate/96_argv_nozoita_h${HASHIRI}_$TS.txt
awk 'NR>1{print $2}' _gate/96_argv_nozoita_h${HASHIRI}_$TS.txt | LC_ALL=C sort > _gate/96_nozoita_paths_h${HASHIRI}_$TS.txt
LC_ALL=C comm -23 _gate/96_zenbu_h${HASHIRI}_$TS.txt _gate/96_nozoita_paths_h${HASHIRI}_$TS.txt > _gate/96_argv_h${HASHIRI}_$TS.txt
printf '全=%s 除=%s argv=%s\n' "$($G -c '' _gate/96_zenbu_h${HASHIRI}_$TS.txt)" "$($G -c '' _gate/96_nozoita_paths_h${HASHIRI}_$TS.txt)" "$($G -c '' _gate/96_argv_h${HASHIRI}_$TS.txt)" | tee -a $LOG
# ④ 臺帳(全 file・除いた物も載せる・★束内相対★=cd 束済み)
python3 -B $REPO/scripts/checks/karo_mac_manifest_append.py MANIFEST.txt $(cat _gate/96_zenbu_h${HASHIRI}_$TS.txt) > _gate/90_append_h${HASHIRI}_$TS.out 2> _gate/90_append_h${HASHIRI}_$TS.err; echo $? > _gate/90_append_h${HASHIRI}_$TS.rc
echo "append rc=$(cat _gate/90_append_h${HASHIRI}_$TS.rc) $(tail -1 _gate/90_append_h${HASHIRI}_$TS.out)" | tee -a $LOG
# ⑤ 出す前の門
echo "KM_GATE_MANIFEST_BASE=. bash $REPO/scripts/checks/karo_mac_dasumae_gate.sh MANIFEST.txt \$(cat _gate/96_argv_h${HASHIRI}_$TS.txt)" > _gate/km100_h${HASHIRI}_$TS.cmd
KM_GATE_MANIFEST_BASE=. bash $REPO/scripts/checks/karo_mac_dasumae_gate.sh MANIFEST.txt $(cat _gate/96_argv_h${HASHIRI}_$TS.txt) > _gate/km100_h${HASHIRI}_$TS.out 2> _gate/km100_h${HASHIRI}_$TS.err; echo $? > _gate/km100_h${HASHIRI}_$TS.rc
echo "門 rc=$(cat _gate/km100_h${HASHIRI}_$TS.rc)" | tee -a $LOG; $G -E '一致|條|落ちた|通。' _gate/km100_h${HASHIRI}_$TS.out _gate/km100_h${HASHIRI}_$TS.err | sed 's/^[^:]*://' | tee -a $LOG
# ⑥ gate7
tail -n +2 README.md > _gate/gate7_body_input_h${HASHIRI}_$TS.md
bash -c "source $HOME/bin/karo_mac_gate7.sh; gate7 _gate/gate7_body_input_h${HASHIRI}_$TS.md" > _gate/gate7_body_h${HASHIRI}_$TS.out 2> _gate/gate7_body_h${HASHIRI}_$TS.err; echo $? > _gate/gate7_body_h${HASHIRI}_$TS.rc
echo "gate7 rc=$(cat _gate/gate7_body_h${HASHIRI}_$TS.rc) 出目=$(cat _gate/gate7_body_h${HASHIRI}_$TS.out)" | tee -a $LOG
echo "TS=$TS"
