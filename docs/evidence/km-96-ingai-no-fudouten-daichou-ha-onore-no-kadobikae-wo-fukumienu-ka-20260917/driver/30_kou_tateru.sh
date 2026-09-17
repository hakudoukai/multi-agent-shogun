#!/bin/bash
# 甲案 ―― 臺帳が己の path を載せる。二形を建てる。
#   甲1 = ★番人語を使はず★ 正しい sha で己を載せる(唯一の書き手 append.py のみで建つ)
#   甲2 = sha 欄に ★番人語 SELF★ を置く(append.py では書けぬ ∴ 手で足す=案一違背を記録)
# 根は argv[1](写しの根)。出目は stdout/stderr へ。
set -u
R=/Users/momizimac/multi-agent-shogun
APP="$R/scripts/checks/karo_mac_manifest_append.py"
VER="$R/scripts/checks/karo_mac_manifest_verify.py"
UTS="$1"
cd "$UTS" || exit 2

echo "=== 甲1: append.py だけで 己を載せる ==="
rm -f MANIFEST_kou.txt
# ①束の物(己の前に在る物)を載せる
find . -type f ! -name 'MANIFEST_kou*.txt' -print0 | sort -z | xargs -0 python3 -B "$APP" MANIFEST_kou.txt
echo "① rc=$?"
echo "① 臺帳 sha(己を載せる前) = $(shasum -a 256 MANIFEST_kou.txt | cut -c1-64)"
# ②己自身を載せる ―― 此の一行を書いた刹那、①で測つた sha は古びる
python3 -B "$APP" MANIFEST_kou.txt MANIFEST_kou.txt
echo "② rc=$?"
echo "② 臺帳 sha(己を載せた後) = $(shasum -a 256 MANIFEST_kou.txt | cut -c1-64)"
echo "② 己の行 = $(grep -n . /dev/null; grep 'path=MANIFEST_kou.txt ' MANIFEST_kou.txt)"
echo "=== 甲1 照合 ==="
python3 -B "$VER" MANIFEST_kou.txt "$PWD/"
echo "甲1 verify rc=$?"

echo
echo "=== 甲2: sha 欄に番人語 SELF ==="
rm -f MANIFEST_kou2.txt
find . -type f ! -name 'MANIFEST_kou*.txt' -print0 | sort -z | xargs -0 python3 -B "$APP" MANIFEST_kou2.txt
echo "① rc=$?"
echo "③ append.py に番人語を書かせられるか ―― 器は digest() を必ず計る ∴ 口が無い(後述の逐語)"
B=$(stat -f %z MANIFEST_kou2.txt); L=$(grep -c '' MANIFEST_kou2.txt)
printf 'path=MANIFEST_kou2.txt sha256=SELF bytes=%s lines=%s\n' "$B" "$L" >> MANIFEST_kou2.txt
echo "④ 手で足した(★案一「書き手は append.py のみ」に違背★ ―― 之が甲2の代価)"
echo "④ 己の行 = $(grep 'path=MANIFEST_kou2.txt ' MANIFEST_kou2.txt)"
echo "=== 甲2 照合 ==="
python3 -B "$VER" MANIFEST_kou2.txt "$PWD/"
echo "甲2 verify rc=$?"
