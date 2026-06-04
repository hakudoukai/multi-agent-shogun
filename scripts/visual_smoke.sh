#!/usr/bin/env bash
# visual_smoke.sh — 3PC pixel-identical smoke gate (DD-170 L1 ゲート)
# 副院長裁定 4728acd7 / 66a52b6c Q4 Tier 3:
#   screen_verify.py 再利用 (FKI-NO-DUP)、3PC で同一 URL → screenshot → diff ≤1%
# 実走: 各 PC で ./scripts/visual_smoke.sh [URL] [OUT_DIR]、出力を rsync で集約 → diff
set -euo pipefail

URL="${1:-http://localhost:5173/handover-sheet/01_000001}"
OUT_DIR="${2:-/tmp/visual_smoke_$(hostname)}"
mkdir -p "$OUT_DIR"

echo "[visual_smoke] $(date -Is) host=$(hostname) url=$URL out=$OUT_DIR"

VERIFIER="$(dirname "$(readlink -f "$0")")/screen_verify.py"
if [ ! -f "$VERIFIER" ]; then
  echo "ERR: screen_verify.py not found at $VERIFIER" >&2; exit 1
fi

python3 "$VERIFIER" \
  --url "$URL" \
  --out "$OUT_DIR/screenshot.png" \
  > "$OUT_DIR/result.json" 2>&1 || {
  echo "WARN: screen_verify.py exited non-zero — check $OUT_DIR/result.json" >&2
}

echo "[visual_smoke] screenshot=$OUT_DIR/screenshot.png"
if [ -f "$OUT_DIR/screenshot.png" ]; then
  size=$(stat -c '%s' "$OUT_DIR/screenshot.png")
  echo "[visual_smoke] screenshot bytes=$size"
fi
echo "[visual_smoke] result excerpt:"
head -20 "$OUT_DIR/result.json" || true

echo "[visual_smoke] done — for 3PC diff: rsync $(hostname):$OUT_DIR ./remote/ + compare via odiff/ImageMagick compare"
