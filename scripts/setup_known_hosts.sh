#!/usr/bin/env bash
# setup_known_hosts.sh — multi-agent-shogun 信頼済みホスト群の known_hosts 事前登録
#
# 用途:
#   agent_health_check.sh 等で StrictHostKeyChecking=yes 強制するため、
#   信頼済みホスト群の SSH host key fingerprint を $HOME/.ssh/known_hosts に
#   予め追加する。MITM (=man in the middle) 解消のための事前登録手順。
#
# Created: 2026-05-08 cmd_health_check_secret_hardening_001 (ashigaru3)
# Reference: 家康殿 audit msg_20260507_223206 (StrictHostKeyChecking 強制必須)
#
# Usage:
#   bash scripts/setup_known_hosts.sh                # default hosts 登録
#   KNOWN_HOSTS=/path/to/known_hosts bash scripts/setup_known_hosts.sh   # custom path
#
# Exit:
#   0: 全ホスト処理完了 (= 既に登録済 or 新規追加)
#   1: 1件以上の ssh-keyscan 失敗

set -uo pipefail

KNOWN_HOSTS="${KNOWN_HOSTS:-$HOME/.ssh/known_hosts}"
KEYSCAN_TIMEOUT=5

# 信頼済みホスト一覧 (= multi-agent-shogun から SSH 接続するすべての宛先)
HOSTS=(
    "192.168.11.47"   # SecondPC (= hakudokai@192.168.11.47)
)

echo "[setup_known_hosts] target known_hosts: ${KNOWN_HOSTS}"

# .ssh ディレクトリと known_hosts ファイルを安全な権限で作成 (= 700 / 600)
mkdir -p "$(dirname "$KNOWN_HOSTS")"
chmod 700 "$(dirname "$KNOWN_HOSTS")"
touch "$KNOWN_HOSTS"
chmod 600 "$KNOWN_HOSTS"

added=0
skipped=0
failed=0

for host in "${HOSTS[@]}"; do
    if ssh-keygen -F "$host" -f "$KNOWN_HOSTS" >/dev/null 2>&1; then
        echo "[setup_known_hosts] SKIP ${host} (= 既に登録済)"
        skipped=$((skipped + 1))
        continue
    fi

    echo "[setup_known_hosts] ADD  ${host} (= ssh-keyscan via known_hosts append)"
    if ssh-keyscan -T "$KEYSCAN_TIMEOUT" -H "$host" 2>/dev/null >> "$KNOWN_HOSTS"; then
        added=$((added + 1))
    else
        echo "[setup_known_hosts] FAIL ${host} (= ssh-keyscan failed、ホストが reachable か確認のこと)" >&2
        failed=$((failed + 1))
    fi
done

echo "[setup_known_hosts] done. added=${added} skipped=${skipped} failed=${failed}"

if [ "$failed" -gt 0 ]; then
    exit 1
fi
exit 0
