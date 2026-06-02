#!/usr/bin/env bash
#
# Enter Restart — Commander Watchdog (Phase 2 (β) third_pc local 番人)
#
# 由来: commander_failsafe_watchdog.sh (May 30) を rename + 命名統一
#       (ee4d6ce4 / 副院長令 21e94f35 / 司令庫 538b59ff §「番人死活監視」 / 副院長令 e6b027a6 §「番人の番人」)
# redo: 2026-06-02 gunshi-third Gemini cycle1 FAIL (spec_compliance 違反) close
#       — 旧版は WAKE_MSG literal text を tmux send-keys -l で送信していたが、
#         docs/runbooks/enter_restart_shogun_reference.md §1 「全 4 unit 共通: 新規コマンド送信絶対禁・
#         C-m (Enter) のみ」原則に違反。本 redo で Enter-only + label-match strict 化。
#
# 目的:
#   - commander-third:0.0 pane の Commander TUI が 10min idle 時、★既入力 buffer 確定★ のため
#     C-m (Enter) のみを 1 回送信する。
#   - 新規コマンド送信 絶対禁。tmux send-keys -l (literal text 送信) 禁。
#
# label 照合 strict (false positive 防止):
#   (i) tmux display-message で pane の現状取得
#   (ii) tmux capture-pane -p -S -3 で末尾 3 行取得
#   (iii) Claude UI prompt の特徴 (`│ > ...` 末尾文字列、非空 input buffer) を検出
#   (iv) 一致時のみ C-m 送信、不一致なら exit 0 + 静かに skip
#
# 連続発火上限:
#   - 過去 15min 内 fire 数 >= 3 → 本 cycle 停止 (result=halted)
#   - 2026-05-05 SecondPC 異常消費事件教訓 (副院長令 e6b027a6 watcher 暴走防止 mandate)
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

PANE_TARGET="commander-third:0.0"
# pc_handshake.from_pc 実データ: Commander は from_pc='commander' で投函 (DB constraint 整合)
FROM_PC_FILTER="commander"
LOG_DIR="/home/hakudoukai/.local/share/enter_restart_commander"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y%m%d).log"
FIRE_HISTORY="$LOG_DIR/fires.log"
THRESHOLD_MIN=10
FIRE_CAP_COUNT=3
FIRE_CAP_WINDOW_MIN=15

log() { printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"; }

log "=== enter_restart_commander cycle start ==="

# Step 0: 連続発火上限チェック (過去 15min 内 fire 数 >= 3 なら本 cycle 停止)
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
    # shireiko_audit_log に halted row INSERT (証跡)
    doppler run --project openhands --config dev -- \
      /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << PYEOF || true
import os, json, urllib.request
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
payload = {
    "event_type": "enter_restart_commander_fire",
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

# Step 1: tmux pane 存在確認 (commander-third session 未起動なら skip)
if ! tmux has-session -t commander-third 2>/dev/null; then
    log "WARN: tmux session 'commander-third' not found, skip"
    exit 0
fi
if ! tmux display-message -t "$PANE_TARGET" -p '#{pane_id}' >/dev/null 2>&1; then
    log "WARN: pane '$PANE_TARGET' not found, skip"
    exit 0
fi

# Step 2: Supabase で Commander 最終投函 取得
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
    log "WARN: no commander handshake data ($LAST_INFO), skip"
    exit 0
fi

ELAPSED_MIN=$(echo "$LAST_INFO" | cut -d'|' -f1)
LAST_AT=$(echo "$LAST_INFO" | cut -d'|' -f2)
LAST_TOPIC=$(echo "$LAST_INFO" | cut -d'|' -f3)
ELAPSED_INT=$(echo "$ELAPSED_MIN" | cut -d. -f1)

log "Commander last handshake: ${ELAPSED_MIN}min ago at $LAST_AT (topic: $LAST_TOPIC)"

# Step 3: pane 状態取得 (label 照合用)
PANE_META=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_path}|#{pane_title}|#{pane_current_command}' 2>/dev/null || echo "")
PANE_TAIL=$(tmux capture-pane -t "$PANE_TARGET" -p -S -3 2>/dev/null || echo "")
log "pane meta: $PANE_META"
log "pane tail (last 3 lines, base64): $(printf '%s' "$PANE_TAIL" | base64 -w0)"

# Step 4: idle threshold 判定
if [ "$ELAPSED_INT" -lt "$THRESHOLD_MIN" ]; then
    log "Commander alive (elapsed=${ELAPSED_MIN}min < ${THRESHOLD_MIN}min), no action (result=skipped)"
    SKIP_REASON="alive"
fi

# Step 5: label 照合 (Claude TUI prompt + 非空 input buffer の検出)
#   許容パターン: 末尾行に "│ > " もしくは "│ >" のあとに非空白文字が続く
#   ※ ` > ` のみで終わるケース (空 buffer) は対象外 (新規 input 無しで Enter のみ送ると意味なし)
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
if [ "${SKIP_REASON:-}" = "alive" ]; then
    RESULT="skipped"
    ACTION="none"
    DETAIL_EXTRA="alive (idle=${ELAPSED_MIN}min < threshold=${THRESHOLD_MIN}min)"
elif [ "$LABEL_MATCH" -eq 1 ]; then
    log "★ENTER_RESTART_COMMANDER FIRE★ idle=${ELAPSED_MIN}min, label=${LABEL_REASON}"
    # ★C-m (Enter) のみ 1 回送信。新規コマンド送信絶対禁、send-keys -l 不使用★
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

# Step 7: shireiko_audit_log INSERT (event=enter_restart_commander_fire)
# constraint: judgment_level ∈ {1,2,3}, result ∈ {success,failure,partial,dry_run,escalated,detected_only}
case "$RESULT" in
    success)        SHIREIKO_RESULT="success" ;;
    failure)        SHIREIKO_RESULT="failure" ;;
    skipped)        SHIREIKO_RESULT="detected_only" ;;
    halted)         SHIREIKO_RESULT="escalated" ;;
    *)              SHIREIKO_RESULT="detected_only" ;;
esac
doppler run --project openhands --config dev -- \
  /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << PYEOF || true
import os, json, urllib.request
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
payload = {
    "event_type": "enter_restart_commander_fire",
    "detail": "Commander last handshake ${ELAPSED_MIN}min ago (threshold ${THRESHOLD_MIN}min). ${DETAIL_EXTRA}",
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

# Step 8: heartbeat 投函 (本番人自身の死活信号、副院長令 538b59ff §「番人死活」)
doppler run --project openhands --config dev -- \
  /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 - << PYEOF || true
import os, json, urllib.request, uuid
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/pc_handshake'
payload = {
    "id": str(uuid.uuid4()),
    "from_pc": "commander", "to_pc": "fukuincho",
    "topic": "[enter_restart] commander alive: last_commander=${ELAPSED_MIN}min ago",
    "content": "third_pc local 番人 heartbeat (5min cycle, engine=enter_restart). Commander last=${ELAPSED_MIN}min, threshold=${THRESHOLD_MIN}min, result=${RESULT}, action=${ACTION}",
    "priority": "low", "message_type": "status_update"
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"enter_restart_commander heartbeat rc={r.status}")
PYEOF

log "=== enter_restart_commander cycle complete (result=${RESULT} action=${ACTION}) ==="
exit 0
