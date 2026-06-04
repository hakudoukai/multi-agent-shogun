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
#   ER_PYTHON3_BIN             python3 binary path (default: hermes-agent venv python3)
#                              ★cycle4 Q1 修正で envvar 化、smoke test で stub 化可能★
#   ER_TARGET_PC               shireiko_audit_log.target_pc / 横展開 (default: third_pc)
#                              ★副院長令 baabd1ca 横展開 (main_pc/second_pc) で envvar 化、
#                              第三版 patch、後方互換 strict (未設定時 third_pc 既定)★
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
# ★cycle4 Q1 fix: python3 binary path envvar 化 (smoke test stub 化に対応)★
ER_PYTHON3_BIN="${ER_PYTHON3_BIN:-/home/hakudoukai/.local/share/hermes-agent/venv/bin/python3}"
# ★副院長令 baabd1ca 横展開 patch: target_pc envvar 化 (main_pc/second_pc 対応)★
# 由来: enter_restart 共通実装を main_pc / second_pc に展開する際、shireiko_audit_log
# に投函する target_pc を per-PC 切替できるようにするため。後方互換 strict、未設定時は
# third_pc 既定で third_pc 動作には一切影響なし。設定例: main → ER_TARGET_PC=main_pc。
ER_TARGET_PC="${ER_TARGET_PC:-third_pc}"
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
    # ★副院長令 b0bdfa67 (P0): S1 high (Codex implementation-scope audit 15ff8ff0) 根治★
    # 旧版は heredoc unquoted で ${EVENT_TYPE} 等を bash 展開して Python ソースに混入
    # → wrapper envvar override 経路から Python コード注入の余地。
    # 構造修正: heredoc <<'PYEOF' (quoted = bash expansion 無効) + 環境変数経由 (os.environ)
    # + json.dumps (string→Python literal は json で安全) で literal interpolation を断つ。
    # (= homework#1 audit_gemini.sh と同型根治、FKI-DEV-ROOT-CURE-FIRST 順守)
    ER_EVENT_TYPE_PY="$EVENT_TYPE" \
    ER_RECENT_FIRES_PY="$RECENT_FIRES" \
    ER_FIRE_CAP_COUNT_PY="$FIRE_CAP_COUNT" \
    ER_FIRE_CAP_WINDOW_MIN_PY="$FIRE_CAP_WINDOW_MIN" \
    ER_TARGET_PC_PY="$ER_TARGET_PC" \
    doppler run --project openhands --config dev -- \
      "$ER_PYTHON3_BIN" - <<'PYEOF' || true
import os, json, urllib.request
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
event_type = os.environ.get('ER_EVENT_TYPE_PY', '')
recent_fires = os.environ.get('ER_RECENT_FIRES_PY', '')
fire_cap_count = os.environ.get('ER_FIRE_CAP_COUNT_PY', '')
fire_cap_window_min = os.environ.get('ER_FIRE_CAP_WINDOW_MIN_PY', '')
target_pc = os.environ.get('ER_TARGET_PC_PY', '')
payload = {
    "event_type": event_type,
    "detail": f"Fire cap exceeded ({recent_fires} >= {fire_cap_count}) in last {fire_cap_window_min}min. Skipping cycle.",
    "judgment_level": 2,
    "action_taken": "halted",
    "result": "escalated",
    "engine": "enter_restart",
    "target_pc": target_pc,
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
# ★副院長令 b0bdfa67 (P0): S1 high 根治 (Codex fix_suggestion 準拠)★
# 旧版は ${FROM_PC_FILTER} を URL 文字列に直接展開 → URL injection の余地。
# urllib.parse.urlencode で query 構築 + os.environ 経由値取得。
#
# ★Codex 再監査 (b0bdfa67 cycle2) B1/T1 high 根治: env propagation 順序修正★
# 旧版 `ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" LAST_INFO=$(...)` は両方が
# assignment-only simple command ゆえ bash 評価順で subshell の doppler に
# env が伝播しない (= LAST_INFO は subshell の中で from_pc_filter='' となり
# runtime breakage)。Step 0/7/8 と同形 (env prefix が doppler という command に
# 直接付く形) になるよう、command substitution の括弧の中で env を渡す。
LAST_INFO=$(ER_FROM_PC_FILTER_PY="$FROM_PC_FILTER" doppler run --project openhands --config dev -- \
  "$ER_PYTHON3_BIN" - <<'PYEOF'
import os, json, urllib.request, urllib.parse
from datetime import datetime, timezone
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
base = os.environ['SUPABASE_URL'] + '/rest/v1/pc_handshake'
from_pc_filter = os.environ.get('ER_FROM_PC_FILTER_PY', '')
query = urllib.parse.urlencode({
    'from_pc': f'eq.{from_pc_filter}',
    'select': 'created_at,topic',
    'order': 'created_at.desc',
    'limit': '1',
})
url = base + '?' + query
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
# β改修 (CANON-SHOGUN-COMMS-RESTORE-01 残 regression #1):
#   現 Claude Code TUI は footer (⏵⏵ bypass permissions / esc to interrupt 等) を常時 last_line に表示。
#   旧 -S -3 + last_line 厳格照合では footer を拾い続け mismatch → 一生 fire skip。
#   対策: capture 範囲を -S -10 (= 直近 N 行) に拡大、Step 5 で footer 除外 → last_non_footer_line 抽出。
PANE_META=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_path}|#{pane_title}|#{pane_current_command}' 2>/dev/null || echo "")
# β改修 cycle5 (CANON 残 regression #1 Layer D, α堅牢版):
#   capture 窓を -S -10 → -S -50 に拡張。
#   active pane で output 流入中に input 行 (❯ ...) が直近 10 行範囲外に
#   押し上がる race を吸収、prompt 行を範囲内に含める保証を上げる。
PANE_TAIL=$(tmux capture-pane -t "$PANE_TARGET" -p -S -50 2>/dev/null || echo "")
# β改修 cycle4 (CANON 残 regression #1 Layer C):
#   Claude Code TUI は ASCII space を NBSP (U+00A0, UTF-8 = 0xC2 0xA0) に表示変換する場合がある。
#   POSIX `[[:space:]]` クラスは C locale で NBSP を含まないため、label regex (`❯[[:space:]]+非空`)
#   が NBSP separator に match できず永続 fire skip となる。
#   最小適応 (原状追随): capture 直後に NBSP を ASCII space に正規化、regex は不変。
PANE_TAIL=$(printf '%s' "$PANE_TAIL" | sed 's/\xc2\xa0/ /g')
log "pane meta: $PANE_META"
log "pane tail (last 50 lines, base64, after NBSP normalize): $(printf '%s' "$PANE_TAIL" | base64 -w0)"

# Step 4: idle threshold 判定
SKIP_REASON=""
if [ "$ELAPSED_INT" -lt "$THRESHOLD_MIN" ]; then
    log "${ROLE_NAME} alive (elapsed=${ELAPSED_MIN}min < ${THRESHOLD_MIN}min), no action (result=skipped)"
    SKIP_REASON="alive"
fi

# Step 5: label 照合 (Claude TUI prompt + 非空 input buffer 検出)
# β改修 cycle5 (CANON 残 regression #1 Layer D, α堅牢版):
#   従来 last_non_footer_line は「footer 除外後の最下位行」を取るが、
#   active pane で output 流入中は input 行 (❯ ...) が範囲内のどこに居るか不定で、
#   ★output 末尾文字列が拾われ label_match=0 → 自動 send-keys 不発★ となる現象 (実機 12/12 cycle)。
#   対策: ★prompt 行自体を PANE_TAIL 全体から grep 探索★ (旧 `│ > xxx │` / 新 `^❯ xxx`)
#   tail -1 で最下位 prompt 行を取得。output 流入で押し上がっても prompt 行を確実に捕捉。
#   既存 footer 除外 + NBSP 正規化はそのまま、PROMPT 行探索が cycle3 の last_non_footer_line を代替。
LABEL_MATCH=0
LABEL_REASON=""
FOOTER_PATTERN='⏵⏵ bypass permissions|esc to interrupt|shift\+tab to cycle|⏵ Plan mode|tab to expand|ctrl\+o to expand|\? for shortcuts|[0-9]+% context used|^─+[[:space:]]*$'
# β改修 cycle5c (CANON 残 regression #1 Layer E, anchor 強化):
#   cycle5 の単純な行頭 anchor では output 中の prompt-like plain text (例: Claude が
#   過去 user message を「  ❯ inboxN」形式で再表示する、bash 出力に "│ > xxx │" 含む) を
#   誤検知 → unintended Enter injection リスク (Codex cycle5b B1 high)。
#   strict 化: ★PROMPT 行は ──── ボーダー直後の `❯` / `│ >` 行のみ★ を真の Claude TUI
#   input box と判定。awk の prev_border state で行間関係を判定 (pipefail 影響なし)。
if [ -n "$PANE_TAIL" ]; then
    LAST_LINE=$(printf '%s\n' "$PANE_TAIL" | awk 'NF{last=$0} END{print last}')
    PROMPT_LINE=$(printf '%s\n' "$PANE_TAIL" | awk '
        /^[[:space:]]*─+[[:space:]]*$/ { prev_border = 1; next }
        prev_border && (/^[[:space:]]*❯/ || /^[[:space:]]*│[[:space:]]*>/) { last = $0 }
        { prev_border = 0 }
        END { if (last != "") print last }
    ')
    log "last_line (base64): $(printf '%s' "$LAST_LINE" | base64 -w0)"
    log "prompt_line (base64, border-anchored): $(printf '%s' "$PROMPT_LINE" | base64 -w0)"
    if [ -n "$PROMPT_LINE" ]; then
        # β改修 cycle3 (CANON 残 regression #1 Layer B):
        #   Claude Code TUI prompt 形式が `│ > xxx │` (旧) → `❯ xxx` (新、上下 ──── ボーダー間) に進化。
        if printf '%s' "$PROMPT_LINE" | grep -qE '│[[:space:]]*>[[:space:]]+[^[:space:]│]|^[[:space:]]*❯[[:space:]]+[^[:space:]]'; then
            LABEL_MATCH=1
            LABEL_REASON="claude_ui_with_nonempty_input_buffer"
        elif printf '%s' "$PROMPT_LINE" | grep -qE '│[[:space:]]*>[[:space:]]*│?[[:space:]]*$|^[[:space:]]*❯[[:space:]]*$'; then
            LABEL_REASON="claude_ui_empty_input_buffer"
        else
            LABEL_REASON="prompt_line_unclassifiable"
        fi
    else
        LABEL_REASON="no_border_anchored_prompt_in_pane_tail"
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
# ★副院長令 b0bdfa67 (P0): S1 high 根治 (Step 7 shireiko_audit_log INSERT)★
# heredoc <<'PYEOF' quoted + 環境変数経由で全 bash 値を Python へ渡す。
# 全文字列は json.dumps で安全に literal 化、Python source injection 不能。
ER_EVENT_TYPE_PY="$EVENT_TYPE" \
ER_ROLE_NAME_PY="$ROLE_NAME" \
ER_ELAPSED_MIN_PY="$ELAPSED_MIN" \
ER_THRESHOLD_MIN_PY="$THRESHOLD_MIN" \
ER_DETAIL_EXTRA_PY="$DETAIL_EXTRA" \
ER_ACTION_PY="$ACTION" \
ER_SHIREIKO_RESULT_PY="$SHIREIKO_RESULT" \
ER_TARGET_PC_PY="$ER_TARGET_PC" \
doppler run --project openhands --config dev -- \
  "$ER_PYTHON3_BIN" - <<'PYEOF' || true
import os, json, urllib.request
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
event_type = os.environ.get('ER_EVENT_TYPE_PY', '')
role_name = os.environ.get('ER_ROLE_NAME_PY', '')
elapsed_min = os.environ.get('ER_ELAPSED_MIN_PY', '')
threshold_min = os.environ.get('ER_THRESHOLD_MIN_PY', '')
detail_extra = os.environ.get('ER_DETAIL_EXTRA_PY', '')
action = os.environ.get('ER_ACTION_PY', '')
shireiko_result = os.environ.get('ER_SHIREIKO_RESULT_PY', '')
target_pc = os.environ.get('ER_TARGET_PC_PY', '')
payload = {
    "event_type": event_type,
    "detail": f"{role_name} last handshake {elapsed_min}min ago (threshold {threshold_min}min). {detail_extra}",
    "judgment_level": 2,
    "action_taken": action,
    "result": shireiko_result,
    "engine": "enter_restart",
    "target_pc": target_pc,
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"shireiko_audit_log INSERT rc={r.status}")
PYEOF

# Step 8: heartbeat 投函
# ★副院長令 b0bdfa67 (P0): S1 high 根治 (Step 8 heartbeat INSERT)★
# heredoc <<'PYEOF' quoted + 環境変数経由で全 bash 値を Python へ渡す。
ER_HEARTBEAT_FROM_PC_PY="$HEARTBEAT_FROM_PC" \
ER_HEARTBEAT_TOPIC_PREFIX_PY="$HEARTBEAT_TOPIC_PREFIX" \
ER_ROLE_NAME_PY="$ROLE_NAME" \
ER_ELAPSED_MIN_PY="$ELAPSED_MIN" \
ER_TARGET_PC_PY="$ER_TARGET_PC" \
ER_THRESHOLD_MIN_PY="$THRESHOLD_MIN" \
ER_RESULT_PY="$RESULT" \
ER_ACTION_PY="$ACTION" \
ER_CYCLE_LOG_PREFIX_PY="$CYCLE_LOG_PREFIX" \
doppler run --project openhands --config dev -- \
  "$ER_PYTHON3_BIN" - <<'PYEOF' || true
import os, json, urllib.request, uuid
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/pc_handshake'
heartbeat_from_pc = os.environ.get('ER_HEARTBEAT_FROM_PC_PY', '')
heartbeat_topic_prefix = os.environ.get('ER_HEARTBEAT_TOPIC_PREFIX_PY', '')
role_name = os.environ.get('ER_ROLE_NAME_PY', '')
elapsed_min = os.environ.get('ER_ELAPSED_MIN_PY', '')
target_pc = os.environ.get('ER_TARGET_PC_PY', '')
threshold_min = os.environ.get('ER_THRESHOLD_MIN_PY', '')
result = os.environ.get('ER_RESULT_PY', '')
action = os.environ.get('ER_ACTION_PY', '')
cycle_log_prefix = os.environ.get('ER_CYCLE_LOG_PREFIX_PY', '')
payload = {
    "id": str(uuid.uuid4()),
    "from_pc": heartbeat_from_pc, "to_pc": "fukuincho",
    "topic": f"{heartbeat_topic_prefix}: last_{role_name}={elapsed_min}min ago",
    "content": f"{target_pc} enter_restart heartbeat (5min cycle, engine=enter_restart, role={role_name}). last={elapsed_min}min, threshold={threshold_min}min, result={result}, action={action}",
    "priority": "low", "message_type": "status_update"
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"{cycle_log_prefix} heartbeat rc={r.status}")
PYEOF

log "=== ${CYCLE_LOG_PREFIX} cycle complete (result=${RESULT} action=${ACTION}) ==="
exit 0
