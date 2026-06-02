#!/usr/bin/env bash
#
# Enter Restart — Common Watchdog 共通実装 (cycle3 D1 統合)
#
# 由来: 副院長令 baabd1ca【enter_restart RED 修正 Phase A 即修正】③、Codex audit
#       e7e28c7a-1a77-4c31-bd6a-44176099075e (cycle2 ffa89df red) D1 high close。
#       commander_watchdog.sh と shogun_third_watchdog.sh の重複ロジックを本書 1 本へ
#       統合、安全 fix が片方だけリスクを構造的に解消。
#
# 役割: 指定 PC の指定 pane の Claude TUI が ER_THRESHOLD_MIN 分 idle 時、★既入力
#       buffer 確定★ のため C-m (Enter) のみを 1 回送信。新規コマンド送信絶対禁、
#       send-keys -l 不使用、label-match strict (false positive 防止)。
#
# 必須 envvar (caller wrapper が設定):
#   ER_PANE_TARGET             tmux pane (例 commander-third:0.0)
#   ER_SESSION_NAME            tmux session (has-session 用、例 commander-third)
#   ER_FROM_PC_FILTER          pc_handshake.from_pc 値 (例 commander / third_pc)
#   ER_LOG_DIR                 ログ・fires.log 配置先 (例 ~/.local/share/enter_restart_<name>)
#   ER_EVENT_TYPE              shireiko_audit_log.event_type (例 enter_restart_commander_fire)
#   ER_ROLE_NAME               log 表示用役職名 (例 Commander / shogun-third)
#   ER_HEARTBEAT_FROM_PC       heartbeat INSERT 用 pc_handshake.from_pc 値
#   ER_HEARTBEAT_TOPIC_PREFIX  heartbeat topic 接頭辞 (例 "[enter_restart] commander alive")
#   ER_CYCLE_LOG_PREFIX        cycle start/complete log 接頭辞 (例 enter_restart_commander)
#
# オプション envvar (default あり):
#   ER_THRESHOLD_MIN=10        idle 判定閾値 (分)
#   ER_FIRE_CAP_COUNT=3        連続発火上限
#   ER_FIRE_CAP_WINDOW_MIN=15  発火カウント評価窓 (分)
#
# 終了コード: 0 = 通常完遂 (skip / halt 含む)、2 = 必須 envvar 欠落
#
# Watcher Design Principles 順守: oneshot cycle ゆえ無限 retry 不発生、INSERT 失敗時
#                                 は || true で silent skip。
# 2026-05-05 SecondPC 異常消費事件教訓: ER_FIRE_CAP_COUNT 上限で暴走防止。

set -uo pipefail

# 必須 envvar 検査
for var in ER_PANE_TARGET ER_SESSION_NAME ER_FROM_PC_FILTER ER_LOG_DIR ER_EVENT_TYPE \
           ER_ROLE_NAME ER_HEARTBEAT_FROM_PC ER_HEARTBEAT_TOPIC_PREFIX ER_CYCLE_LOG_PREFIX; do
  if [ -z "${!var:-}" ]; then
    echo "ERROR: enter_restart common watchdog: required envvar $var is unset" >&2
    exit 2
  fi
done

PANE_TARGET="$ER_PANE_TARGET"
SESSION_NAME="$ER_SESSION_NAME"
FROM_PC_FILTER="$ER_FROM_PC_FILTER"
LOG_DIR="$ER_LOG_DIR"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y%m%d).log"
FIRE_HISTORY="$LOG_DIR/fires.log"
THRESHOLD_MIN="${ER_THRESHOLD_MIN:-10}"
FIRE_CAP_COUNT="${ER_FIRE_CAP_COUNT:-3}"
FIRE_CAP_WINDOW_MIN="${ER_FIRE_CAP_WINDOW_MIN:-15}"
EVENT_TYPE="$ER_EVENT_TYPE"
ROLE_NAME="$ER_ROLE_NAME"
HEARTBEAT_FROM_PC="$ER_HEARTBEAT_FROM_PC"
HEARTBEAT_TOPIC_PREFIX="$ER_HEARTBEAT_TOPIC_PREFIX"
CYCLE_LOG_PREFIX="$ER_CYCLE_LOG_PREFIX"

log() { printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"; }

log "=== ${CYCLE_LOG_PREFIX} cycle start (common watchdog) ==="

# Step 0: 連続発火上限チェック (過去 ER_FIRE_CAP_WINDOW_MIN 内 fire 数 >= ER_FIRE_CAP_COUNT なら本 cycle 停止)
if [ -f "$FIRE_HISTORY" ]; then
    NOW_EPOCH=$(date +%s)
    WINDOW_EPOCH=$((NOW_EPOCH - FIRE_CAP_WINDOW_MIN * 60))
    RECENT_FIRES=$(awk -v cutoff="$WINDOW_EPOCH" 'BEGIN{c=0} { if ($1+0 >= cutoff) c++ } END { print c }' "$FIRE_HISTORY" 2>/dev/null || echo 0)
else
    RECENT_FIRES=0
fi
log "fire cap check: recent_fires_in_${FIRE_CAP_WINDOW_MIN}min=${RECENT_FIRES} cap=${FIRE_CAP_COUNT}"
if [ "$RECENT_FIRES" -ge "$FIRE_CAP_COUNT" ]; then
    log "★HALT★ fire cap exceeded (${RECENT_FIRES} >= ${FIRE_CAP_COUNT}) in last ${FIRE_CAP_WINDOW_MIN}min — skip cycle"
    doppler run --project openhands --config dev -- \
      /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << PYEOF || true
import os, json, urllib.request
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
payload = {
    "event_type": "${EVENT_TYPE}",
    "detail": "Fire cap exceeded (${RECENT_FIRES} >= ${FIRE_CAP_COUNT}) in last ${FIRE_CAP_WINDOW_MIN}min. Skipping cycle.",
    "judgment_level": 2,
    "action_taken": "halted",
    "result": "escalated",
    "engine": "enter_restart",
    "target_pc": "third_pc",
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"halt row INSERT rc={r.status}")
PYEOF
    exit 0
fi

# Step 1: tmux pane 存在確認
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    log "WARN: tmux session '$SESSION_NAME' not found, skip"
    exit 0
fi
if ! tmux display-message -t "$PANE_TARGET" -p '#{pane_id}' >/dev/null 2>&1; then
    log "WARN: pane '$PANE_TARGET' not found, skip"
    exit 0
fi

# Step 2: Supabase で最終投函取得 (idle 判定)
LAST_INFO=$(doppler run --project openhands --config dev -- \
  /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << PYEOF
import os, json, urllib.request
from datetime import datetime, timezone
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + "/rest/v1/pc_handshake?from_pc=eq.${FROM_PC_FILTER}&select=created_at,topic&order=created_at.desc&limit=1"
req = urllib.request.Request(url, headers={'apikey':key,'Authorization':f'Bearer {key}'})
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        rows = json.loads(r.read())
except Exception as e:
    print(f"ERR|{e}")
    raise SystemExit(0)
if not rows:
    print("NO_DATA")
else:
    last = rows[0]
    last_at = datetime.fromisoformat(last['created_at'].replace('Z','+00:00'))
    elapsed = (datetime.now(timezone.utc) - last_at).total_seconds() / 60.0
    print(f"{elapsed:.1f}|{last['created_at']}|{last.get('topic','')[:80]}")
PYEOF
)

if [ "$LAST_INFO" = "NO_DATA" ] || [ -z "$LAST_INFO" ] || [[ "$LAST_INFO" == ERR\|* ]]; then
    log "WARN: no ${ROLE_NAME} handshake data ($LAST_INFO), skip"
    exit 0
fi

ELAPSED_MIN=$(echo "$LAST_INFO" | cut -d'|' -f1)
LAST_AT=$(echo "$LAST_INFO" | cut -d'|' -f2)
LAST_TOPIC=$(echo "$LAST_INFO" | cut -d'|' -f3)
ELAPSED_INT=$(echo "$ELAPSED_MIN" | cut -d. -f1)

log "${ROLE_NAME} last handshake: ${ELAPSED_MIN}min ago at $LAST_AT (topic: $LAST_TOPIC)"

# Step 3: pane 状態取得 (label 照合用)
PANE_META=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_path}|#{pane_title}|#{pane_current_command}' 2>/dev/null || echo "")
PANE_TAIL=$(tmux capture-pane -t "$PANE_TARGET" -p -S -3 2>/dev/null || echo "")
log "pane meta: $PANE_META"
log "pane tail (last 3 lines, base64): $(printf '%s' "$PANE_TAIL" | base64 -w0)"

# Step 4: idle threshold 判定
SKIP_REASON=""
if [ "$ELAPSED_INT" -lt "$THRESHOLD_MIN" ]; then
    log "${ROLE_NAME} alive (elapsed=${ELAPSED_MIN}min < ${THRESHOLD_MIN}min), no action (result=skipped)"
    SKIP_REASON="alive"
fi

# Step 5: label 照合 (Claude TUI prompt + 非空 input buffer 検出)
LABEL_MATCH=0
LABEL_REASON=""
if [ -n "$PANE_TAIL" ]; then
    LAST_LINE=$(printf '%s\n' "$PANE_TAIL" | awk 'NF{last=$0} END{print last}')
    log "last_line (base64): $(printf '%s' "$LAST_LINE" | base64 -w0)"
    if printf '%s' "$LAST_LINE" | grep -qE '│[[:space:]]*>[[:space:]]+[^[:space:]│]'; then
        LABEL_MATCH=1
        LABEL_REASON="claude_ui_with_nonempty_input_buffer"
    elif printf '%s' "$LAST_LINE" | grep -qE '│[[:space:]]*>[[:space:]]*│?[[:space:]]*$'; then
        LABEL_REASON="claude_ui_empty_input_buffer"
    else
        LABEL_REASON="no_claude_ui_prompt_in_last_line"
    fi
else
    LABEL_REASON="empty_pane_tail"
fi
log "label_match=${LABEL_MATCH} reason=${LABEL_REASON}"

# Step 6: 発火判定 + Enter 送信 (★C-m only / 新規コマンド送信絶対禁★)
RESULT="skipped"
ACTION="none"
DETAIL_EXTRA=""
if [ "${SKIP_REASON}" = "alive" ]; then
    RESULT="skipped"
    ACTION="none"
    DETAIL_EXTRA="alive (idle=${ELAPSED_MIN}min < threshold=${THRESHOLD_MIN}min)"
elif [ "$LABEL_MATCH" -eq 1 ]; then
    log "★${CYCLE_LOG_PREFIX} FIRE★ idle=${ELAPSED_MIN}min, label=${LABEL_REASON}"
    tmux send-keys -t "$PANE_TARGET" Enter 2>/dev/null
    RC=$?
    log "C-m send rc=$RC"
    if [ "$RC" -eq 0 ]; then
        RESULT="success"
        ACTION="enter_send"
        DETAIL_EXTRA="C-m sent (rc=0), label=${LABEL_REASON}"
        date +%s >> "$FIRE_HISTORY"
    else
        RESULT="failure"
        ACTION="enter_send_failed"
        DETAIL_EXTRA="C-m send rc=$RC, label=${LABEL_REASON}"
    fi
else
    log "label mismatch (${LABEL_REASON}), skip (false positive 防止)"
    RESULT="skipped"
    ACTION="label_mismatch"
    DETAIL_EXTRA="label=${LABEL_REASON}, idle=${ELAPSED_MIN}min"
fi

# Step 7: shireiko_audit_log INSERT
case "$RESULT" in
    success)  SHIREIKO_RESULT="success" ;;
    failure)  SHIREIKO_RESULT="failure" ;;
    skipped)  SHIREIKO_RESULT="detected_only" ;;
    halted)   SHIREIKO_RESULT="escalated" ;;
    *)        SHIREIKO_RESULT="detected_only" ;;
esac
doppler run --project openhands --config dev -- \
  /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << PYEOF || true
import os, json, urllib.request
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
payload = {
    "event_type": "${EVENT_TYPE}",
    "detail": "${ROLE_NAME} last handshake ${ELAPSED_MIN}min ago (threshold ${THRESHOLD_MIN}min). ${DETAIL_EXTRA}",
    "judgment_level": 2,
    "action_taken": "${ACTION}",
    "result": "${SHIREIKO_RESULT}",
    "engine": "enter_restart",
    "target_pc": "third_pc",
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"shireiko_audit_log INSERT rc={r.status}")
PYEOF

# Step 8: heartbeat 投函
doppler run --project openhands --config dev -- \
  /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << PYEOF || true
import os, json, urllib.request, uuid
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/pc_handshake'
payload = {
    "id": str(uuid.uuid4()),
    "from_pc": "${HEARTBEAT_FROM_PC}", "to_pc": "fukuincho",
    "topic": "${HEARTBEAT_TOPIC_PREFIX}: last_${ROLE_NAME}=${ELAPSED_MIN}min ago",
    "content": "third_pc local enter_restart heartbeat (5min cycle, engine=enter_restart, role=${ROLE_NAME}). last=${ELAPSED_MIN}min, threshold=${THRESHOLD_MIN}min, result=${RESULT}, action=${ACTION}",
    "priority": "low", "message_type": "status_update"
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"${CYCLE_LOG_PREFIX} heartbeat rc={r.status}")
PYEOF

log "=== ${CYCLE_LOG_PREFIX} cycle complete (result=${RESULT} action=${ACTION}) ==="
exit 0
