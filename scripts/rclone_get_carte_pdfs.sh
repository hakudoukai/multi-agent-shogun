#!/usr/bin/env bash
# rclone_get_carte_pdfs.sh — claude/見本カルテ から PDF 11本取得 (rclone ワンタイム OAuth、副院長裁定 5324f0d4)
# 取得先: tests/visual/baseline_pdfs/
# 実走: doppler run --project openhands --config dev -- bash scripts/rclone_get_carte_pdfs.sh
#
# 注: rclone remote は root_folder_id=386318571891 (claude) で限定済 = 「見本カルテ/」は claude 配下のサブフォルダ
set -euo pipefail

DEST="${1:-tests/visual/baseline_pdfs}"
mkdir -p "$DEST"
echo "[rclone_get_carte_pdfs] $(date -Is) dest=$DEST"

if ! command -v rclone >/dev/null 2>&1; then
  echo "ERR: rclone not installed (run rclone_setup.sh first)" >&2; exit 1
fi
if [ -z "${RCLONE_CONFIG_CLAUDE_TOKEN:-}" ]; then
  echo "ERR: RCLONE_CONFIG_CLAUDE_TOKEN 未投入 (理事長 OAuth 完了待ち)" >&2; exit 3
fi

# 1. 見本カルテ subdir 存在確認
echo "[rclone] 見本カルテ/ subdir listing:"
rclone ls 'claude:見本カルテ/' 2>&1 | head -30 || {
  echo "FAIL: claude:見本カルテ/ not accessible (root_folder_id=claude 設定確認要)" >&2
  exit 4
}

# 2. PDF 11本 copy
echo "[rclone] copy *.pdf from claude:見本カルテ/ → $DEST"
rclone copy 'claude:見本カルテ/' "$DEST" --include '*.pdf' --progress 2>&1 | tail -20

count=$(ls "$DEST"/*.pdf 2>/dev/null | wc -l)
echo "DONE: $count PDFs fetched into $DEST"
ls -la "$DEST"
