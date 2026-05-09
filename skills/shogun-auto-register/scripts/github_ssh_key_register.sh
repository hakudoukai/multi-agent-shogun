#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# github_ssh_key_register.sh — GitHub SSH key 自動登録 template
#
# Usage:
#   github_ssh_key_register.sh <pubkey_path> <title>
#   github_ssh_key_register.sh ~/.ssh/id_ed25519.pub "ieyasu-secondpc-20260509"
#
# 前提: gh CLI が target GitHub account で認証済
# 自動化率: 95% (= 陛下の browser 認可 1 click のみ手動)
# ════════════════════════════════════════════════════════════════
set -eu

PUBKEY_PATH="${1:-}"
TITLE="${2:-}"

if [ -z "$PUBKEY_PATH" ] || [ -z "$TITLE" ]; then
  cat <<USAGE
Usage: $0 <pubkey_path> <title>
Example: $0 ~/.ssh/id_ed25519.pub "ieyasu-secondpc-20260509"
USAGE
  exit 2
fi

[ -f "$PUBKEY_PATH" ] || { echo "ERR: pubkey not found: $PUBKEY_PATH"; exit 2; }
PUB_KEY=$(cat "$PUBKEY_PATH")

echo "═══ Step 0 — 認証アカウント確認 ═══"
gh auth status 2>&1 | head -10
ACCOUNT=$(gh auth status 2>&1 | grep -oP "account \K\S+" | head -1)
echo ""
echo "登録先 account: $ACCOUNT"
echo "登録 pubkey: ${PUB_KEY:0:50}..."
echo "title: $TITLE"
echo ""
read -p "この account で進めて宜しいか? [y/N] " ans
[ "$ans" = "y" ] || { echo "中止仕る"; exit 1; }

echo ""
echo "═══ Step 1 — admin:public_key scope 確認 ═══"
if gh auth status 2>&1 | grep -q "admin:public_key"; then
  echo "✅ scope 既保有、Step 1 skip"
else
  echo "scope 不足、gh auth refresh 起動 — 陛下の browser 認可要"
  echo ""
  echo "⚠ 重要: gh が device code を表示するゆえ、其れを browser に入力 → Authorize クリック"
  echo "         Authorize 完遂までこのスクリプトは待機仕る"
  echo ""
  # foreground 駆動 (= 早期 exit の罠回避)
  gh auth refresh -h github.com -s admin:public_key
  echo ""
  echo "✅ scope 取得完遂"
fi

echo ""
echo "═══ Step 2 — 鍵登録 ═══"
echo "$PUB_KEY" | gh ssh-key add - --title "$TITLE" --type authentication
echo ""

echo "═══ Step 3 — 検証 ═══"
echo "登録鍵一覧 (= title grep):"
gh ssh-key list | grep -F "$TITLE" || { echo "❌ 登録確認失敗"; exit 3; }
echo ""

echo "ssh -T git@github.com 試行 (= 当 PC から):"
if timeout 10 ssh -T -o BatchMode=yes -o StrictHostKeyChecking=accept-new git@github.com 2>&1 | grep -q "successfully authenticated"; then
  echo "✅ 当 PC から GitHub SSH 認証成功"
else
  echo "ℹ 当 PC ではない別 PC 鍵の登録の可能性あり (= 別 PC で検証要)"
fi

echo ""
echo "═══ ✅ 完遂 — title=$TITLE ═══"
echo "次手: 鍵保有 PC で git fetch origin / ssh -T git@github.com 検証、"
echo "      関係者に bridge 経由で ack 通知 (= 必要なら)"
