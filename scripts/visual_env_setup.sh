#!/usr/bin/env bash
# visual_env_setup.sh — 3PC 視覚確認環境 Tier 1 統一 installer
# 副院長裁定 4728acd7 / 66a52b6c Q1+Q2:
#   canon = NotoSansJP-VF + Playwright 1.60.0 + chromium-1217 + pdftoppm 24.02.0 + python playwright
# 冪等 (idempotent)、scp 直書き禁、各 PC で git pull 後 ./scripts/visual_env_setup.sh 実走
set -euo pipefail

echo "[visual_env_setup] $(date -Is) host=$(hostname)"

# 1. NotoSansJP-VF (canon font、frontend design-tokens.css と整合)
FONT_DIR="$HOME/.local/share/fonts"
FONT_FILE="$FONT_DIR/NotoSansJP-VF.ttf"
mkdir -p "$FONT_DIR"
if [ ! -f "$FONT_FILE" ]; then
  echo "[font] NotoSansJP-VF download (canon font)"
  curl -fsSL --retry 3 -o "$FONT_FILE" \
    "https://github.com/notofonts/noto-cjk/raw/main/Sans/Variable/TTF/Subset/NotoSansJP-VF.ttf" \
    || { echo "ERR: NotoSansJP-VF download failed" >&2; exit 1; }
fi
fc-cache -f "$FONT_DIR" 2>&1 | tail -2 || true
if fc-list :lang=ja | grep -qi 'NotoSansJP-VF\|Noto Sans JP'; then
  echo "[font] NotoSansJP detected via fc-list"
else
  echo "WARN: fc-list lacks NotoSansJP (canon mismatch)" >&2
fi

# 2. pdftoppm (poppler-utils)
if command -v pdftoppm >/dev/null 2>&1; then
  pdftoppm -v 2>&1 | head -1
else
  echo "WARN: pdftoppm missing — required: sudo apt install -y poppler-utils (副院長承認後)" >&2
fi

# 3. python playwright (sync_api、screen_verify.py 動作担保)
if python3 -c "import playwright" 2>/dev/null; then
  echo "[python-playwright] installed"
else
  echo "[python-playwright] install via pip --user"
  pip install --user --break-system-packages playwright 2>&1 || pip install --user playwright 2>&1 || {
    echo "WARN: pip install playwright failed (副院長承認後 sudo or pipx で対応)" >&2
  }
  python3 -m playwright install chromium 2>&1 | tail -3 || true
fi
python3 -c "import playwright; print('[python-playwright] OK')" 2>&1 || true

# 4. @playwright/test (Node)、global pin 確認
echo "[playwright-node] global version:"
npx -y @playwright/test --version 2>&1 | head -1 || true
# project 側 1.60.0 align は別 PR (frontend package.json 編集要、副院長承認後)

echo "[visual_env_setup] done"
