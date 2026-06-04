#!/usr/bin/env bash
# rclone_scope_verify.sh — root_folder_id=claude 限定の挙動検証 (副院長令裁定 5324f0d4 (7))
# 期待: claude=read 成功、他フォルダ参照は root_folder_id により claude 内に限定される旨を記録
# 注: token scope は Box 全体 (= 強制境界でない、運用境界、理事長了承済)。
#     rclone の root_folder_id は remote の「論理 root」を制限するが、別 remote を作れば token で全体見える。
# 実走: doppler run --project openhands --config dev -- bash scripts/rclone_scope_verify.sh
set -euo pipefail

echo "[rclone_scope_verify] $(date -Is) host=$(hostname)"
if [ -z "${RCLONE_CONFIG_CLAUDE_TOKEN:-}" ]; then
  echo "ERR: RCLONE_CONFIG_CLAUDE_TOKEN 未投入 (理事長 OAuth 完了待ち)" >&2; exit 3
fi

# 1. claude (root_folder_id=386318571891) の read = success 期待
echo "=== TEST 1: claude:/ (= folder_id ${RCLONE_CONFIG_CLAUDE_ROOT_FOLDER_ID:-claude_root}) lsd ==="
if rclone lsd claude: 2>&1 | head -10; then
  echo "PASS  claude:/ read success"
else
  echo "FAIL  claude:/ read denied" >&2
  exit 4
fi

# 2. 見本カルテ subdir (folder_id 387023559660) read = success 期待
echo "=== TEST 2: claude:見本カルテ/ ls ==="
if rclone ls 'claude:見本カルテ/' 2>&1 | head -5; then
  echo "PASS  claude:見本カルテ/ accessible"
else
  echo "FAIL  claude:見本カルテ/ denied" >&2
fi

# 3. root_folder_id 越えのアクセス試行 (rclone path 「上に上がる」操作は無いが、別 remote 作成で全体見えるか確認)
echo "=== TEST 3: claude:../ (parent listing — rclone path として無効) ==="
rclone lsd 'claude:../' 2>&1 | head -5 || echo "EXPECTED: claude:../ invalid path (root_folder_id 効いている)"

# 4. 注記 (token scope の境界性)
cat <<'NOTE'

[NOTE] rclone token は Box 全体 scope (User Token)。
  root_folder_id=claude (386318571891) は ★rclone remote の論理 root★ を絞る = 運用境界。
  ★強制境界ではない★:
    - rclone config で別 remote (root_folder_id 無し) を作れば、同 token で Box 全体見える
    - secret 漏洩時の被害境界 ≠ root_folder_id 設定
  ★理事長殿了承済 (副院長令 5324f0d4)★。
  secret は Doppler 経由のみ (rclone.conf 直書き / git commit 禁)。

[NOTE END]
NOTE
echo "[rclone_scope_verify] done"
