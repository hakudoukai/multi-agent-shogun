#!/usr/bin/env bash
# agent_health_check.sh — multi-agent-shogun 健康診断 + 異常時 ntfy 通知
#
# 用途: 5分毎に systemd user timer で実行、異常検知時に理事長殿に通知
# Created: 2026-05-07 (理事長殿御指示「対話依存タイマー脱却、機械的仕組みへ」)
#
# Check 項目:
#   1. Supabase 増殖ループ予兆 (1分間 5件超 INSERT)
#   2. claude プロセスの稼働状況 (= 各 pane で claude が動いているか)
#   3. inbox 滞留 (= 未読 10件超 = block loop の前兆)
#   4. SecondPC SSH 接続性
#   5. token 飽和警告蓄積 (= 各 agent の context size)
#
# Usage: bash scripts/agent_health_check.sh [--quiet]
# Output: /tmp/agent_health_check.log + ntfy (異常時のみ)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="/tmp/agent_health_check.log"
QUIET=false
[ "${1:-}" = "--quiet" ] && QUIET=true

ALERTS=()

# ─── 1. Supabase 増殖ループ予兆検知 ───
SB_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" 2>/dev/null | cut -d= -f2- | tr -d '\r')
SB_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" 2>/dev/null | cut -d= -f2- | tr -d '\r')
INSERT_COUNT=0
if [ -n "$SB_URL" ] && [ -n "$SB_KEY" ]; then
    NOW1_JST=$(date -d '1 minute ago' '+%Y-%m-%dT%H:%M:%S')
    INSERT_COUNT=$(curl -sS --max-time 10 \
        "${SB_URL}/rest/v1/pc_handshake?topic=like.cross_pc_inbox_*&created_at=gte.${NOW1_JST}&select=created_at" \
        -H "Authorization: Bearer ${SB_KEY}" -H "apikey: ${SB_KEY}" 2>/dev/null \
        | python3 -c "import sys,json;print(len(json.loads(sys.stdin.read())))" 2>/dev/null || echo 0)
    if [ "${INSERT_COUNT:-0}" -gt 5 ]; then
        ALERTS+=("ERR-INFRA-LOOP: Supabase ${INSERT_COUNT} INSERTs/1min (=loop suspect, threshold=5)")
    fi
fi

# ─── 2. claude プロセス稼働確認 (MainPC) ───
for entry in "shogun:main.0:shogun" "multiagent:agents.0:karo" "multiagent:agents.1:ashigaru1" "multiagent:agents.2:ashigaru2" "multiagent:agents.3:gunshi"; do
    pane="${entry%:*}"
    name="${entry##*:}"
    cmd=$(tmux list-panes -t "$pane" -F '#{pane_current_command}' 2>/dev/null | head -1)
    if [ -z "$cmd" ]; then
        ALERTS+=("ERR-AGENT-DOWN: pane ${pane} (${name}) missing")
    elif [ "$cmd" != "claude" ] && [ "$cmd" != "node" ]; then
        ALERTS+=("ERR-AGENT-DOWN: pane ${pane} (${name}) claude not running (cmd=${cmd})")
    fi
done

# ─── 3. inbox 滞留検知 (= block loop 前兆) ───
for a in shogun karo gunshi ashigaru1 ashigaru2; do
    inbox="$SCRIPT_DIR/queue/inbox/${a}.yaml"
    [ -f "$inbox" ] || continue
    n=$(grep -c 'read: false' "$inbox" 2>/dev/null || echo 0)
    n=${n%%[^0-9]*}
    if [ "${n:-0}" -gt 10 ]; then
        ALERTS+=("ERR-INBOX-OVERFLOW: ${a} unread=${n} (threshold=10, loop の前兆)")
    fi
done

# ─── 4. SecondPC 接続性 ───
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o BatchMode=yes hakudokai@192.168.11.47 'true' 2>/dev/null; then
    ALERTS+=("ERR-SECONDPC-DOWN: SSH unreachable to 192.168.11.47")
fi

# ─── 5. SecondPC inbox 滞留 ───
if ssh -o ConnectTimeout=5 -o BatchMode=yes hakudokai@192.168.11.47 'true' 2>/dev/null; then
    for a in ashigaru5 ashigaru6 ashigaru7; do
        n=$(ssh -o ConnectTimeout=5 -o BatchMode=yes hakudokai@192.168.11.47 \
            "grep -c 'read: false' ~/projects/multi-agent-shogun/queue/inbox/${a}.yaml 2>/dev/null || echo 0" 2>/dev/null)
        n=${n%%[^0-9]*}
        if [ "${n:-0}" -gt 10 ]; then
            ALERTS+=("ERR-INBOX-OVERFLOW: SecondPC ${a} unread=${n}")
        fi
    done
fi

# ─── 結果記録 ───
{
    echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] health_check"
    echo "  insert_count_1min: ${INSERT_COUNT}"
    echo "  alerts: ${#ALERTS[@]}"
    for alert in "${ALERTS[@]}"; do
        echo "    - $alert"
    done
} >> "$LOG"

# ─── 異常時 ntfy 通知 ───
if [ "${#ALERTS[@]}" -gt 0 ]; then
    MSG="🚨 multi-agent-shogun 異常検知 ($(date '+%H:%M'))"
    for alert in "${ALERTS[@]}"; do
        MSG="${MSG}
  ${alert}"
    done
    if [ -x "$SCRIPT_DIR/scripts/ntfy.sh" ]; then
        bash "$SCRIPT_DIR/scripts/ntfy.sh" "$MSG" 2>>"$LOG" || true
    fi
    [ "$QUIET" = "false" ] && echo -e "$MSG" >&2
    exit 1
fi

[ "$QUIET" = "false" ] && echo "[health_check] OK (insert_count_1min=${INSERT_COUNT}, alerts=0)"
exit 0
