#!/bin/bash
# 板97774de5: km-222 束25本を main 版の門(blob 04672e15)で再走。門と依存2本の sha256 を命の中で照合し、一つでも違へば走らせず rc=90 で止まる。
# 用法: bash run_pinned.sh <km-222束dir> <filelist> <raw出力dir>
set -u
G="$(cd "$(dirname "$0")" && pwd)/raw/gate"
PIN_GATE=3b8b7182566cc8c4e81533d27d2f6c5d98a9b56429d2d7205dfca9d3a9295bac
PIN_VERIFY=9e831137f1d33f41b6ba88414b26d44dfb93ebc9c544d263f7c0c1d1234e4d8f
PIN_FUKA=8c06f5c58147ccba3b1e040c0930a6f10374987fb717d29b3cd5dc2e766800ad
BUNDLE=$1; LIST=$2; OUT=$3
for pair in "karo_mac_dasumae_gate.sh:$PIN_GATE" "karo_mac_manifest_verify.py:$PIN_VERIFY" "karo_mac_fukashiji.py:$PIN_FUKA"; do
  f=${pair%%:*}; want=${pair#*:}
  got=$(shasum -a 256 "$G/$f" | cut -d' ' -f1)
  echo "pin $f want=$want got=$got"
  [ "$got" = "$want" ] || { echo "PIN不一致 $f ―― 走らせぬ"; exit 90; }
done
args=()
while IFS= read -r l; do args+=("$l"); done < "$LIST"
echo "argc=${#args[@]}"
cd "$BUNDLE" || exit 91
KM_GATE_MANIFEST_BASE=. bash "$G/karo_mac_dasumae_gate.sh" manifest.txt "${args[@]}" > "$OUT/70_gate_main.out" 2> "$OUT/70_gate_main.err"
rc=$?
echo "$rc" > "$OUT/70_gate_main.rc"
echo "gate_rc=$rc"
exit $rc
