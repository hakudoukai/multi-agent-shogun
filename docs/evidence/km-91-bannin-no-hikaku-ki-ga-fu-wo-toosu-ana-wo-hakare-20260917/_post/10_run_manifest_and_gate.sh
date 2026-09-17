#!/bin/bash
# km-91 driver: 臺帳(★束内相対★ 裁 seq322699)→ 門 四段。★束の根で走らせる★。全段 rc を _post/10_rcs.txt へ。
# 員外(臺帳に入れぬ物)= MANIFEST.txt 自身 / _gate/** / _post/**  ―― 器と其の出目は己を数へぬ。
set -u
R="$1"; T=$(date '+%Y%m%dT%H%M%S'); RC=_post/10_rcs.txt; : > "$RC"
rec(){ printf '%s\t%-24s\trc=%s\n' "$(date '+%H:%M:%S')" "$1" "$2" | tee -a "$RC"; }
FILES=$( { echo README.md; find _after -type f | sort; } )
echo "臺帳 対象=$(printf '%s\n' $FILES | grep -c '')  根=$(pwd)"
# 1) 臺帳
# shellcheck disable=SC2086
python3 -B "$R/scripts/checks/karo_mac_manifest_append.py" MANIFEST.txt $FILES \
  > "_post/11_manifest_append_$T.out" 2> "_post/11_manifest_append_$T.err"; rec manifest_append $?
echo "臺帳 行数=$(grep -c '' MANIFEST.txt)  path行=$(grep -c '^path=' MANIFEST.txt)  lines欄有=$(grep -c 'lines=' MANIFEST.txt)"
# 2) 門 selftest
bash "$R/scripts/checks/karo_mac_dasumae_gate.sh" --selftest \
  > "_gate/mon_km91_${T}_selftest.out" 2> "_gate/mon_km91_${T}_selftest.log"; rec gate_selftest $?
# 3) 門 main(紙 + 臺帳照合・束内相対 base)
KM_GATE_MANIFEST_BASE=. bash "$R/scripts/checks/karo_mac_dasumae_gate.sh" MANIFEST.txt README.md \
  > "_gate/mon_km91_${T}_main.out" 2> "_gate/mon_km91_${T}_main.log"; rec gate_main $?
# 4) 門 all(臺帳の全 path)
# shellcheck disable=SC2086
KM_GATE_MANIFEST_BASE=. bash "$R/scripts/checks/karo_mac_dasumae_gate.sh" MANIFEST.txt $FILES \
  > "_gate/mon_km91_${T}_all.out" 2> "_gate/mon_km91_${T}_all.log"; rec gate_all $?
# 5) 門 nobase(★陰性対照★: base 無しでは 條① が落ちる筈 = 落ちるのが正)
bash "$R/scripts/checks/karo_mac_dasumae_gate.sh" MANIFEST.txt README.md \
  > "_gate/mon_km91_${T}_nobase.out" 2> "_gate/mon_km91_${T}_nobase.log"; rec gate_nobase_control $?
echo "T=$T"
