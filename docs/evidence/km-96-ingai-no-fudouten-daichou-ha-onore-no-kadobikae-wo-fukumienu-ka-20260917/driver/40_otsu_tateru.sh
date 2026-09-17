#!/bin/bash
# 乙案 ―― 二段。本体臺帳 MANIFEST_otsu.txt ＋ 領域宣言 RYOUIKI_otsu.txt。
#   要: 領域宣言は ★臺帳に載る★(己を載せぬ故 再帰せぬ)。臺帳が載せられぬのは ★己と門控★ のみ。
set -u
R=/Users/momizimac/multi-agent-shogun
APP="$R/scripts/checks/karo_mac_manifest_append.py"
VER="$R/scripts/checks/karo_mac_manifest_verify.py"
cd "$1" || exit 2

cat > RYOUIKI_otsu.txt <<'TXT'
# 領域宣言(乙案) ―― ★此の領域は臺帳の外である★
# 読み方: 下の 則= 行が、臺帳 MANIFEST_otsu.txt が ★載せ得ぬ★ 領域を名指す。
# 理由: 臺帳が己の sha を己の中に書く事は出来ぬ(書いた刹那に己が変る)。
#       門控は臺帳より ★後に生まれる★ 故、臺帳を建てる刻には未だ無い。
則=MANIFEST_otsu.txt
則=_gate
TXT
rm -f MANIFEST_otsu.txt
find . -type f ! -name 'MANIFEST_otsu.txt' -print0 | sort -z | xargs -0 python3 -B "$APP" MANIFEST_otsu.txt >/dev/null
echo "① 臺帳を建てた rc=$?"
echo "① 領域宣言は臺帳に載つたか = $(grep -c 'path=RYOUIKI_otsu.txt ' MANIFEST_otsu.txt) 行"
echo "① 己(MANIFEST_otsu.txt)を載せたか = $(grep -c 'path=MANIFEST_otsu.txt ' MANIFEST_otsu.txt) 行(★載せぬのが乙の形★)"
echo "=== 乙 照合 ==="
python3 -B "$VER" MANIFEST_otsu.txt "$PWD/" | grep -E '一致|旧形'
echo "乙 verify rc=${PIPESTATUS[0]}"
