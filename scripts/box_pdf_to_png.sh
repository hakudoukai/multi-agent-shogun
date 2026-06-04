#!/usr/bin/env bash
# box_pdf_to_png.sh — PDF (見本カルテ 11本) → PNG baseline (DD-170 L1 用)
# 副院長裁定 4728acd7: NotoSansJP-VF 統一環境で実走、pdftoppm 24.02.0
# 入力: tests/visual/baseline_pdfs/*.pdf
# 出力: tests/visual/baseline/<base>-1.png ...
set -euo pipefail

SRC="${1:-tests/visual/baseline_pdfs}"
DST="${2:-tests/visual/baseline}"
DPI="${3:-150}"

mkdir -p "$DST"
echo "[box_pdf_to_png] $(date -Is) src=$SRC dst=$DST dpi=$DPI"

if ! command -v pdftoppm >/dev/null 2>&1; then
  echo "ERR: pdftoppm not installed (apt: poppler-utils)" >&2
  exit 1
fi
pdftoppm -v 2>&1 | head -1 || true

count=0
for pdf in "$SRC"/*.pdf; do
  [ -f "$pdf" ] || continue
  base="$(basename "$pdf" .pdf)"
  echo "[pdf2png] $pdf -> $DST/$base-N.png @${DPI}dpi"
  pdftoppm -png -r "$DPI" "$pdf" "$DST/$base"
  count=$((count+1))
done

png_count=$(ls "$DST"/*.png 2>/dev/null | wc -l)
echo "DONE: $count PDFs → $png_count PNGs in $DST"
ls -la "$DST" | head -20
