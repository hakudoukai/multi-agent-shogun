#!/bin/bash
# ㋓ ―― 「員外0」と名乗る門は何を見逃すか。★両対照★ で示す。
#  負対照 kiyoi  = 臺帳の載せた物しか無い ★清い束★ → 條①通。だが員外は ★1(臺帳自身)★ ∴「員外0」は恒偽
#  陽性対照 yogore = 臺帳に無い ★他人の一本★ が居る → 條①は ★同じく通る★ ∴「條①通=員外0」は見逃す
set -u
R=/Users/momizimac/multi-agent-shogun
APP="$R/scripts/checks/karo_mac_manifest_append.py"
G="$R/scripts/checks/karo_mac_dasumae_gate.sh"
D="$PWD/driver/20_ingai.py"
BASE="$PWD/raw/yousei"
rm -rf "$BASE"; mkdir -p "$BASE/kiyoi" "$BASE/yogore" "$BASE/_de"
# ★器は己の出力を歩き根の外へ置く★(ver1 では g.out/i.out を根の中へ落し、己を員外に数へた)
echo "刻 $(date '+%Y-%m-%dT%H:%M:%S%z')"

for t in kiyoi yogore; do
  cd "$BASE/$t" || exit 2
  printf '一枚目。\n' > a.txt
  printf '二枚目。\n' > b.txt
  python3 -B "$APP" MANIFEST.txt a.txt b.txt >/dev/null; echo "[$t] 臺帳 rc=$?"
done
printf '★誰も臺帳に載せなんだ一本(他席の置忘れ・生成物の残り 何れも此の形)★\n' > "$BASE/yogore/c_gaibu.txt"

for t in kiyoi yogore; do
  cd "$BASE/$t" || exit 2
  echo "=== ${t} ==="
  echo "  根=$PWD 深さ=無限(os.walk) / disk 本数=$(find . -type f | grep -c '')"
  KM_GATE_MANIFEST_BASE="$PWD/" bash "$G" MANIFEST.txt a.txt b.txt > "$BASE/_de/${t}_g.out" 2> "$BASE/_de/${t}_g.err"; grc=$?
  echo "  ★門(五條) rc=${grc}★ ―― $(grep -E '條① 台帳' "$BASE/_de/${t}_g.err")"
  echo "  $(grep -E '一致' "$BASE/_de/${t}_g.out")"
  python3 -B "$D" MANIFEST.txt . --rokujou > "$BASE/_de/${t}_i.out" 2> "$BASE/_de/${t}_i.err"; irc=$?
  echo "  ★第六條 rc=${irc}★ ―― $(grep -E '員外' "$BASE/_de/${t}_i.out")"
  grep -E '★他★|控 ' "$BASE/_de/${t}_i.out" | sed 's/^/    /'
  echo "  「員外0」を字義通り当てると = $(grep -oE '員外 [0-9]+' "$BASE/_de/${t}_i.out" | head -1) ∴ $(grep -q '員外 0' "$BASE/_de/${t}_i.out" && echo '通' || echo '★落(0 ではない)★')"
done
