#!/bin/bash
# 丙案 ―― ★第六條「員外は己の控のみ」★ を ★走る器★ として建て、乙の宣言を喰はせる。
#  ①門控を臺帳の外と宣した時、第六條は通るか
#  ②宣言に無い物が混れば ★落ちるか★(守りであつて数へではない事の證)
#  ③第六條の出目は ★何時走らせたか★ に依るか(門控は門より後に生まれる)
#  ④第六條は ★配られた門から呼ばれて居るか★(字面・陽性対照付き)
set -u
R=/Users/momizimac/multi-agent-shogun
APP="$R/scripts/checks/karo_mac_manifest_append.py"
G="$R/scripts/checks/karo_mac_dasumae_gate.sh"
D="$PWD/driver/20_ingai.py"
UTS="$1"

echo "=== ④(字面): 配られた門は第六條/員外を呼ぶか ==="
for k in 第六 員外 rokujou ingai 20_ingai; do
  n=$(grep -F -c -- "$k" "$G" 2>/dev/null); rc=$?
  echo "  語「${k}」= ${n} 件(grep rc=${rc})"
done
echo "  ★陽性対照★ 語「條⑤」= $(grep -F -c -- '條⑤' "$G") 件 / 語「manifest_verify」= $(grep -F -c -- 'manifest_verify' "$G") 件"

cd "$UTS" || exit 2
echo
echo "=== 乙の宣言を復し、臺帳を建て直す(出鱈目版を捨てる) ==="
cp -p ../../raw/41_ryouiki_mae.txt RYOUIKI_otsu.txt
rm -f MANIFEST_otsu.txt
find . -type f ! -name 'MANIFEST_otsu.txt' -print0 | sort -z | xargs -0 python3 -B "$APP" MANIFEST_otsu.txt >/dev/null
echo "復した rc=$? / 宣言 sha=$(shasum -a 256 RYOUIKI_otsu.txt | cut -c1-16)"

NORI=()
while IFS= read -r line; do NORI+=(--hikae-nori "${line#則=}"); done < <(grep '^則=' RYOUIKI_otsu.txt)
echo "宣言から読んだ則 = ${NORI[*]}"

echo
echo "=== ①③(前): 門を通す前に第六條を当てる ==="
python3 -B "$D" MANIFEST_otsu.txt . --rokujou "${NORI[@]}" | grep -E '刻|員外|控 |★他★|第六條'
echo "第六條(前) rc=${PIPESTATUS[0]}"

echo
echo "=== ③: 門を一走させる(控は此の束の _gate/ へ落ちる) ==="
T=$(date '+%Y%m%dT%H%M%S')
mkdir -p _gate
KM_GATE_MANIFEST_BASE="$PWD/" bash "$G" MANIFEST_otsu.txt RYOUIKI_otsu.txt \
  > "_gate/km96_hei_${T}.out" 2> "_gate/km96_hei_${T}.err"; grc=$?
echo "$grc" > "_gate/km96_hei_${T}.rc"
echo "門 rc=${grc} / 控3本 = _gate/km96_hei_${T}.{out,err,rc}"
grep -E '條①|條⑤|門' "_gate/km96_hei_${T}.err" | head -5

echo
echo "=== ①③(後): 同じ第六條を、門の後に当てる ==="
python3 -B "$D" MANIFEST_otsu.txt . --rokujou "${NORI[@]}" | grep -E '刻|員外|★他★|第六條'
echo "第六條(後) rc=${PIPESTATUS[0]}"

echo
echo "=== ②: 宣言に無い物を一本置いて、落ちるか ==="
printf 'km-96 陽性対照 ―― 臺帳にも宣言にも無い一本。\n' > raw/km96_youseitaishou_hei.txt
python3 -B "$D" MANIFEST_otsu.txt . --rokujou "${NORI[@]}" | grep -E '員外|★他★|第六條'
echo "第六條(陽性対照) rc=${PIPESTATUS[0]}"
