#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# ssh_check.sh — Cross-PC SSH 双方向健康診断
# 信長 (MainPC) / 家康 (SecondPC) どちらからでも実行可能。
# Usage:
#   bash skills/shogun-ssh-cross-pc/scripts/ssh_check.sh
#   bash skills/shogun-ssh-cross-pc/scripts/ssh_check.sh --self-only
#   bash skills/shogun-ssh-cross-pc/scripts/ssh_check.sh --to-only
# ════════════════════════════════════════════════════════════════
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENDPOINTS_YAML="$SKILL_ROOT/reference/endpoints.yaml"

mode="${1:-full}"
exit_code=0

print_section() { echo ""; echo "═══ $1 ═══"; }

# 自 PC 識別 (= hostname で判定)
my_hostname=$(hostname)
case "$my_hostname" in
  USER-0T4SR8MIQA|*USER-0T4SR8*)
    ME="main_pc"
    PEER_IP="192.168.11.47"
    PEER_PORT="2222"
    PEER_USER="User"
    PEER_NAME="家康殿 (SecondPC)"
    ;;
  USER-O6AK917NTU|*USER-O6AK*)
    ME="second_pc"
    PEER_IP="192.168.11.11"
    PEER_PORT="2223"
    PEER_USER="User"
    PEER_NAME="信長殿 (MainPC)"
    ;;
  *)
    echo "ERR: 未登録 hostname '$my_hostname' — endpoints.yaml に追加要"
    exit 2
    ;;
esac

print_section "0. 自 PC 識別"
echo "hostname=$my_hostname  role=$ME"

print_section "1. 自 PC sshd 稼働確認"
if command -v powershell.exe >/dev/null 2>&1; then
  powershell.exe -NoProfile -Command "Get-Service sshd -ErrorAction SilentlyContinue | Select-Object Status, Name | Format-Table -AutoSize" 2>&1 | head -5
else
  systemctl is-active sshd 2>&1 || service ssh status 2>&1 | head -3
fi

print_section "2. 自 PC 鍵 inventory"
ls -la ~/.ssh/ 2>&1 | grep -E "id_|authorized_keys|config" | head -10
for f in ~/.ssh/id_ed25519.pub ~/.ssh/id_rsa.pub; do
  [ -f "$f" ] && echo "$f: $(ssh-keygen -lf "$f" 2>&1)"
done

print_section "3. 対向 ($PEER_NAME) 到達性"
if ping -c 1 -W 2 "$PEER_IP" >/dev/null 2>&1; then
  echo "ping $PEER_IP: ✅ 到達"
else
  echo "ping $PEER_IP: ❌ 不到達 (= LAN/route 問題、SSH 以前の検証要)"
  exit_code=$((exit_code+1))
fi

print_section "4. 対向 SSH port ($PEER_IP:$PEER_PORT) listening 確認"
if timeout 3 bash -c "echo > /dev/tcp/$PEER_IP/$PEER_PORT" 2>/dev/null; then
  echo "tcp $PEER_IP:$PEER_PORT: ✅ listening"
else
  echo "tcp $PEER_IP:$PEER_PORT: ❌ closed/filtered (= sshd 停止 or firewall)"
  exit_code=$((exit_code+1))
fi

[ "$mode" = "--self-only" ] && exit $exit_code

print_section "5. 対向 SSH 認証 (BatchMode)"
if timeout 8 ssh -o BatchMode=yes -o ConnectTimeout=5 -p "$PEER_PORT" "$PEER_USER@$PEER_IP" 'hostname' 2>&1 | head -3; then
  echo ""
  echo "鍵認証: ✅ 通過"
else
  echo ""
  echo "鍵認証: ❌ 失敗 — pub key を対向 authorized_keys に登録要"
  echo "   自 pub key: $(cat ~/.ssh/id_ed25519.pub 2>/dev/null || echo '(無)')"
  exit_code=$((exit_code+1))
fi

print_section "6. 対向 WSL 経由実行確認 (= wsl -- bash -lc)"
out=$(timeout 12 ssh -o BatchMode=yes -p "$PEER_PORT" "$PEER_USER@$PEER_IP" 'wsl -- bash -lc "echo OK; hostname; whoami"' 2>&1 | head -5)
echo "$out"
if echo "$out" | grep -q "^OK$"; then
  echo "WSL bridge: ✅"
else
  echo "WSL bridge: ⚠ 失敗 (= cmd.exe quote escape か wsl 未起動)"
  exit_code=$((exit_code+1))
fi

print_section "7. 結論"
if [ $exit_code -eq 0 ]; then
  echo "✅ 全 check 通過 — 双方向 SSH 健全"
else
  echo "❌ $exit_code 件 issue 検出 — endpoints.yaml + 鍵登録 + sshd_config 再確認要"
fi

exit $exit_code
