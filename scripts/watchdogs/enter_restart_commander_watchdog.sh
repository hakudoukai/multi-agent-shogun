#!/usr/bin/env bash
#
# Enter Restart — Commander Watchdog (Phase 2 (β) third_pc local 番人)
#
# 由来: commander_failsafe_watchdog.sh (May 30) を rename + 命名統一
#       (ee4d6ce4 / 副院長令 21e94f35 / 司令庫 538b59ff §「番人死活監視」 / 副院長令 e6b027a6 §「番人の番人」)
#
# 目的:
#   - Commander 最終 pc_handshake 投函 > 10分 detect → tmux send-keys wake
#   - Commander daemon と本 systemd timer は別 process =
#     Commander TUI stuck でも timer 生存 → wake 発火可能
#
# 道連れリスク:
#   - 同 PC (third_pc) 内 → OS down 時は道連れ (副院長令明示「第2優先」)
#   - 副院長令 e6b027a6 §「(γ) SSH 開設は保留」 = main_pc/second_pc 経由番人は除外
#
# 司令庫 538b59ff §「番人死活監視」整合: 本 wake 発火 row を shireiko_audit_log に記録
# Watcher Design Principles 順守: シングルショット oneshot timer ゆえ無限ループ不発生、
#                                 INSERT 失敗時は || true で silent skip
#
set -uo pipefail
LOG_DIR="/home/hakudoukai/.local/share/enter_restart_commander"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y%m%d).log"

log() { printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"; }

log "=== enter_restart_commander cycle start ==="

# Step 1: Supabase で Commander 最終投函 取得
LAST_INFO=$(doppler run --project openhands --config dev -- \
  /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << 'PYEOF'
import os, json, urllib.request
from datetime import datetime, timezone
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
# Commander の最終 pc_handshake (heartbeat or status_update)
url = os.environ['SUPABASE_URL'] + "/rest/v1/pc_handshake?from_pc=eq.commander&select=created_at,topic&order=created_at.desc&limit=1"
req = urllib.request.Request(url, headers={'apikey':key,'Authorization':f'Bearer {key}'})
with urllib.request.urlopen(req, timeout=15) as r:
    rows = json.loads(r.read())
if not rows:
    print("NO_DATA")
else:
    last = rows[0]
    last_at = datetime.fromisoformat(last['created_at'].replace('Z','+00:00'))
    elapsed = (datetime.now(timezone.utc) - last_at).total_seconds() / 60.0
    print(f"{elapsed:.1f}|{last['created_at']}|{last.get('topic','')[:80]}")
PYEOF
)

if [ "$LAST_INFO" = "NO_DATA" ] || [ -z "$LAST_INFO" ]; then
    log "WARN: no commander handshake data, skip"
    exit 0
fi

ELAPSED_MIN=$(echo "$LAST_INFO" | cut -d'|' -f1)
LAST_AT=$(echo "$LAST_INFO" | cut -d'|' -f2)
LAST_TOPIC=$(echo "$LAST_INFO" | cut -d'|' -f3)

log "Commander last handshake: ${ELAPSED_MIN}min ago at $LAST_AT"
log "  topic: $LAST_TOPIC"

# Step 2: 10分 threshold 判定
THRESHOLD_MIN=10
ELAPSED_INT=$(echo "$ELAPSED_MIN" | cut -d. -f1)

if [ "$ELAPSED_INT" -ge "$THRESHOLD_MIN" ]; then
    log "★ENTER_RESTART_COMMANDER FIRE★ elapsed=${ELAPSED_MIN}min >= ${THRESHOLD_MIN}min"

    # Step 3: tmux send-keys wake
    WAKE_MSG="[enter_restart-wake] Commander 自動 wake-up: 最終投函 ${ELAPSED_MIN}分前。pc_handshake 着信確認 + watcher heartbeat 状態 verify を即実行せよ。enter_restart_commander by third_pc local timer (ee4d6ce4 / 2630d511 (β) e6b027a6 GO)。"
    tmux send-keys -l -t commander-third:0.0 -- "$WAKE_MSG" 2>/dev/null
    sleep 0.3
    tmux send-keys -t commander-third:0.0 Enter 2>/dev/null
    RC=$?
    log "wake send-keys rc=$RC"

    # Step 4: shireiko_audit_log INSERT (event=enter_restart_commander_fire)
    doppler run --project openhands --config dev -- \
      /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << PYEOF || true
import os, json, urllib.request
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
payload = {
    "event_type": "enter_restart_commander_fire",
    "detail": "Commander last handshake ${ELAPSED_MIN}min ago (threshold ${THRESHOLD_MIN}min). Wake send-keys to commander-third:0.0 (rc=$RC).",
    "judgment_level": 2,  # 1=info, 2=warn, 3=error (旧版 "warn" 文字列は constraint 違反で silent fail していた、ee4d6ce4 で根治)
    "action_taken": "auto_resolve",
    "result": "success" if $RC == 0 else "failure",
    "engine": "enter_restart",
    "target_pc": "third_pc",
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"shireiko_audit_log INSERT rc={r.status}")
PYEOF
else
    log "Commander alive (elapsed=${ELAPSED_MIN}min < ${THRESHOLD_MIN}min), no action"
fi

# Step 5: heartbeat 投函 (本番人自身の死活信号、副院長令 538b59ff §「番人死活」)
doppler run --project openhands --config dev -- \
  /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << PYEOF || true
import os, json, urllib.request, uuid
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/pc_handshake'
payload = {
    "id": str(uuid.uuid4()),
    "from_pc": "commander", "to_pc": "fukuincho",
    "topic": "[enter_restart] commander alive: last_commander=${ELAPSED_MIN}min ago",
    "content": "third_pc local 番人 heartbeat (5min cycle, engine=enter_restart). Commander last=${ELAPSED_MIN}min, threshold=${THRESHOLD_MIN}min, action=$([ "$ELAPSED_INT" -ge "$THRESHOLD_MIN" ] && echo wake_send_keys || echo none)",
    "priority": "low", "message_type": "status_update"
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"enter_restart_commander heartbeat rc={r.status}")
PYEOF

log "=== enter_restart_commander cycle complete ==="
exit 0
