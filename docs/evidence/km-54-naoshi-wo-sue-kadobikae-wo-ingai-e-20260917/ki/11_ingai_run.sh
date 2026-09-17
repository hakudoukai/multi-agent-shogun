#!/bin/bash
# 員外器の駆り手。★三束へ掛ける★ ―― 陽性対照(km-53: 家老が手で 21本 と数へた束)を必ず含める。
# rc は ★管を通さず★ 取る。出目は raw/ へ。
set -u
R=/Users/momizimac/multi-agent-shogun
K="$R/docs/evidence/km-54-naoshi-wo-sue-kadobikae-wo-ingai-e-20260917/ki/10_ingai.py"
O="$R/docs/evidence/km-54-naoshi-wo-sue-kadobikae-wo-ingai-e-20260917/raw"
PY=/opt/homebrew/bin/python3
for n in km-52-shikii-no-bannin-wo-yoko-kara-yabure-20260917 \
         km-53-tasekki-no-fusagikata-wo-kami-de-yabure-20260917 \
         km-53b-gyou-chunyu-no-naoshi-wo-sueru-20260917; do
  s=$(printf '%s' "$n" | cut -d- -f1-2)
  ( cd "$R/docs/evidence/$n" && "$PY" -B "$K" . _manifest.txt \
      > "$O/11_ingai_$s.tsv" 2> "$O/11_ingai_$s.err" )
  echo "rc=$? $s"
done
