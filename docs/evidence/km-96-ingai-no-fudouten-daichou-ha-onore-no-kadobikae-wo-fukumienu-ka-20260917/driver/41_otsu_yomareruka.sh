#!/bin/bash
# 乙案の肝 ―― ★領域宣言を、配られた器の何れかが讀むか★。
#  甲(字面)= 器の中に宣言を讀む口が在るか(陽性対照付き grep)
#  乙(振舞)= 宣言の中身を ★出鱈目★ に書き換へ、臺帳を建て直し、門の出目が変るか
set -u
R=/Users/momizimac/multi-agent-shogun
APP="$R/scripts/checks/karo_mac_manifest_append.py"
VER="$R/scripts/checks/karo_mac_manifest_verify.py"
G="$R/scripts/checks/karo_mac_dasumae_gate.sh"
UTS="$1"

echo "=== 甲(字面): 配られた三器に『領域宣言を讀む口』が在るか ==="
for k in RYOUIKI 領域 SCOPE scope 宣言 則=; do
  n=$(grep -F -c -- "$k" "$G" "$VER" "$APP" 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')
  echo "  語「${k}」= ${n} 件"
done
echo "  ★陽性対照★(器が現に持つ語で grep が効く事を示す)"
for k in manifest sha256; do
  n=$(grep -F -c -- "$k" "$G" "$VER" "$APP" 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')
  echo "  語「${k}」= ${n} 件"
done
echo "  根=$G , $VER , $APP (三本・深さ0=file 直指し)"

cd "$UTS" || exit 2
echo
echo "=== 乙(振舞): 宣言を出鱈目に書き換へ、臺帳を建て直し、門を通す ==="
cp -p RYOUIKI_otsu.txt ../../raw/41_ryouiki_mae.txt
python3 -B "$VER" MANIFEST_otsu.txt "$PWD/" | grep -E '一致'
echo "前 verify rc=${PIPESTATUS[0]}"
cat > RYOUIKI_otsu.txt <<'TXT'
# 領域宣言(乙案・★出鱈目版★) ―― 之が讀まれて居れば出目が変る筈である
則=.
則=★全ての file は臺帳の外である★
則=/etc/passwd
TXT
rm -f MANIFEST_otsu.txt
find . -type f ! -name 'MANIFEST_otsu.txt' -print0 | sort -z | xargs -0 python3 -B "$APP" MANIFEST_otsu.txt >/dev/null
python3 -B "$VER" MANIFEST_otsu.txt "$PWD/" | grep -E '一致'
echo "後 verify rc=${PIPESTATUS[0]}"
cp -p RYOUIKI_otsu.txt ../../raw/41_ryouiki_ato.txt
