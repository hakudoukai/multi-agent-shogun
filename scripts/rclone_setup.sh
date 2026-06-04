#!/usr/bin/env bash
# rclone_setup.sh — rclone 確認 + Doppler 経由 box remote 設定 verify
# 副院長裁定 5324f0d4 (理事長令): CCG App → rclone ワンタイム OAuth へ転換
# DD-164: rclone authorize box (= OAuth ログイン/許可/token 取得) は理事長専権、本 script は token 投入後の検証のみ
#
# 前提:
#   理事長殿が rclone authorize box を実行 → token JSON 取得 → Doppler 投入済 (RCLONE_CONFIG_CLAUDE_TOKEN)
#   Commander が公開値投入済 (RCLONE_CONFIG_CLAUDE_TYPE=box / RCLONE_CONFIG_CLAUDE_ROOT_FOLDER_ID=386318571891)
#
# 実走:
#   doppler run --project openhands --config dev -- bash scripts/rclone_setup.sh
set -euo pipefail

echo "[rclone_setup] $(date -Is) host=$(hostname)"

# 1. rclone install verify
if command -v rclone >/dev/null 2>&1; then
  echo "[rclone] $(rclone version | head -1)"
else
  echo "ERR: rclone not installed. Install on this PC (副院長令 main_pc 優先):"
  echo "  Ubuntu/WSL: sudo apt install -y rclone   (or curl https://rclone.org/install.sh | sudo bash)"
  echo "  macOS:      brew install rclone"
  exit 1
fi

# 2. Doppler env presence check (値は出さない)
echo "[doppler] slot presence"
for slot in RCLONE_CONFIG_CLAUDE_TYPE RCLONE_CONFIG_CLAUDE_ROOT_FOLDER_ID RCLONE_CONFIG_CLAUDE_TOKEN; do
  if [ -n "${!slot:-}" ]; then
    echo "  $slot: present"
  else
    echo "  $slot: MISSING" >&2
  fi
done

# 3. rclone box remote connectivity test (claude root_folder_id 経由)
if [ -z "${RCLONE_CONFIG_CLAUDE_TOKEN:-}" ]; then
  echo "SKIP: RCLONE_CONFIG_CLAUDE_TOKEN 未投入 (理事長 OAuth 完了待ち)" >&2
  exit 3
fi

echo "[rclone] lsd claude: (root_folder_id=$RCLONE_CONFIG_CLAUDE_ROOT_FOLDER_ID 経由で claude 配下のフォルダ列挙)"
rclone lsd claude: 2>&1 | head -20 || {
  echo "FAIL rclone lsd claude: — token expired or invalid?" >&2
  exit 4
}

echo "[rclone_setup] done"
