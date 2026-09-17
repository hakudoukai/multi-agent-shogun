#!/bin/bash
# 80_totonoe.sh ―― 門へ出す前の整へ。順: ①前寸法を焼く ②慣例の正規化(末尾空白/CR 剥ぎ・EOF 改行丁度1・LF) ③R5 .nul を gzip ④第一走の臺帳を _gate へ退け建て直す ⑤argv から★宣して除く★物を列べる ⑥臺帳 append ⑦出す前の門 ⑧gate7(source して呼ぶ)
# 用法: bash driver/80_totonoe.sh   (束の根で呼ぶ)
set -u
REPO=/Users/momizimac/multi-agent-shogun; TS=$(date '+%Y%m%dT%H%M%S'); G=/usr/bin/grep
echo "刻=$TS" > _gate/80_totonoe_$TS.log
# ① 前寸法(触る物すべて)
NORM="raw/20_ps_all.txt raw/30_gyou_all.txt raw/32_tsuiho_chikugo.txt raw/40_hako_jinkou.tsv raw/10_R1_files.nul"
{ echo "# 前寸法(正規化/gzip の前) 刻=$TS  path bytes lines(grep -c '') sha256"
  for f in $NORM raw/15_R5_files.nul; do printf '%s %s %s %s\n' "$f" "$(stat -f %z "$f")" "$($G -c '' "$f")" "$(shasum -a 256 "$f" | cut -d' ' -f1)"; done; } > _gate/95_mae_sunpou_$TS.txt
# ② 正規化(慣例: 軍師mac 2026-09-07 の pipeline)。.nul は NUL 区切りゆゑ触らぬ(末尾空白 2 行は名の中の空白=触るな)
for f in raw/20_ps_all.txt raw/30_gyou_all.txt raw/32_tsuiho_chikugo.txt raw/40_hako_jinkou.tsv; do perl -pi -e 's/[ \t\r]+$//' "$f"; perl -0pi -e 's/\n+\z/\n/' "$f"; done
# ③ R5 の一覧(30MB)を gzip -9(前 sha は ① に在る)
[ -f raw/15_R5_files.nul ] && gzip -9 raw/15_R5_files.nul
# ④ 第一走の臺帳を退ける
[ -f MANIFEST.txt ] && mv MANIFEST.txt _gate/MANIFEST_hashiri1_$TS.txt
# ⑤ argv から宣して除く物: (a) NUL 区切り一覧 .nul / .nul.gz (改行構造を持たぬ・寸法大) (b) 0byte の .err/.out/.txt(陰性の證・裁 seq310228⑶「空は 0byte」)
find . -type f -not -name README.md -not -name MANIFEST.txt -not -path './_gate/*' | sed 's#^\./##' | LC_ALL=C sort > _gate/96_zenbu_$TS.txt
{ echo "# argv から宣して除く(第四の道) 刻=$TS  理由 path bytes"
  while IFS= read -r f; do case "$f" in *.nul|*.nul.gz) echo "NUL区切り $f $(stat -f %z "$f")";; *) [ "$(stat -f %z "$f")" = 0 ] && echo "0byte $f 0";; esac; done < _gate/96_zenbu_$TS.txt; } > _gate/96_argv_nozoita_$TS.txt
awk 'NR>1{print $2}' _gate/96_argv_nozoita_$TS.txt | LC_ALL=C sort > _gate/96_nozoita_paths_$TS.txt
LC_ALL=C comm -23 _gate/96_zenbu_$TS.txt _gate/96_nozoita_paths_$TS.txt > _gate/96_argv_$TS.txt
printf '全=%s 除=%s argv=%s\n' "$($G -c '' _gate/96_zenbu_$TS.txt)" "$($G -c '' _gate/96_nozoita_paths_$TS.txt)" "$($G -c '' _gate/96_argv_$TS.txt)" | tee -a _gate/80_totonoe_$TS.log
# ⑥ 臺帳(全 file・除いた物も載せる)
python3 -B $REPO/scripts/checks/karo_mac_manifest_append.py MANIFEST.txt $(cat _gate/96_zenbu_$TS.txt) > _gate/90_append2_$TS.out 2> _gate/90_append2_$TS.err; echo $? > _gate/90_append2_$TS.rc
echo "append rc=$(cat _gate/90_append2_$TS.rc) $(tail -1 _gate/90_append2_$TS.out)" | tee -a _gate/80_totonoe_$TS.log
# ⑦ 出す前の門 第二走
echo "KM_GATE_MANIFEST_BASE=. bash $REPO/scripts/checks/karo_mac_dasumae_gate.sh MANIFEST.txt \$(cat _gate/96_argv_$TS.txt)" > _gate/km97_hashiri2_$TS.cmd
KM_GATE_MANIFEST_BASE=. bash $REPO/scripts/checks/karo_mac_dasumae_gate.sh MANIFEST.txt $(cat _gate/96_argv_$TS.txt) > _gate/km97_hashiri2_$TS.out 2> _gate/km97_hashiri2_$TS.err; echo $? > _gate/km97_hashiri2_$TS.rc
echo "第二走 rc=$(cat _gate/km97_hashiri2_$TS.rc)" | tee -a _gate/80_totonoe_$TS.log
# ⑧ gate7(文の門)を README の胴(1 行目を除く)へ ―― 器は関数定義のみゆゑ source して呼ぶ
tail -n +2 README.md > _gate/gate7_body_input_$TS.md
bash -c "source $HOME/bin/karo_mac_gate7.sh; gate7 _gate/gate7_body_input_$TS.md" > _gate/gate7_body_$TS.out 2> _gate/gate7_body_$TS.err; echo $? > _gate/gate7_body_$TS.rc
echo "gate7 rc=$(cat _gate/gate7_body_$TS.rc) 出目=$(cat _gate/gate7_body_$TS.out)" | tee -a _gate/80_totonoe_$TS.log
echo "TS=$TS"
