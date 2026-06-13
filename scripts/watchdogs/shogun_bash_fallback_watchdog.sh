#!/usr/bin/env bash
#
# Shogun Bash-Fallback / Stuck-Retry Watchdog (各PC ローカル, oneshot 60s cycle)
#
# 由来: 副院長追命 670ffbfe(2) via Commander msg_20260613_104819
#       (shogun bash 落ち再発防止)。task=subtask_thirdpc_shogun_bash_fallback_watchdog。
#
# ═══ 防ぐ事象 (enter_restart_common_watchdog.sh とは別 failure mode) ═══
#   enter_restart 系 = 「idle 時に既入力 buffer を C-m で確定」(Enter のみ)。
#   本書       = 「Claude プロセスが落ちた/詰まった時に doppler env 付きで再起動」。
#   両者は補完関係 (重複ではない、Anti-Duplication 順守)。
#
#   shogun launch wrapper (setup_shogun_standard.sh):
#     `... && doppler run --project openhands --config dev -- claude 2>>log`
#   Claude が exit (crash / OOM / 完了 / API 致命 / retry 枯渇) すると `&&` chain が
#   終わり、pane は素の bash prompt に落ちる (= 概念上の `exec bash`)。
#   pane は tmux 上で見かけ alive だが agent は不在。以後 inboxN nudge が bash に
#   当たり「inboxN: command not found」を連発する (second_pc inbox808 堆積が症状)。
#   さらに bare `claude` 再起動は doppler/ccflare env 欠落で API retry 滞留 (env-gap)。
#
# ═══ 検知 2 failure mode ═══
#   (A) bash-fallback : pane が bash prompt + 「command not found」/ shell prompt、
#                       かつ Claude TUI chrome 不在。pane_current_command=bash で補強。
#   (B) stuck-retry   : Claude TUI chrome 在り + 「Retrying… attempt N/M」/ spinner が
#                       ★SBW_STUCK_MIN 分継続 (fingerprint 不変で persistence 判定)★。
#                       spinner 語 (Crunching 等) は正常時も出るため persistence 必須。
#
# ═══ 復旧 ═══
#   ① @agent_id 取得 (永続) ② (B のみ) Claude を停止し pane 解放 (Esc→C-c→必要なら
#      子 PID へ SIGTERM、★ローカルのみ・cross-PC kill 無 ∴ DD-169 guard 不要★)
#   ③ ★doppler env 付き relaunch★ (SBW_RELAUNCH_CMD 既定 = doppler run … claude
#      --permission-mode auto。bare claude 禁 = env-gap 回避)
#   ④ kickoff directive (自己識別→CLAUDE.md/instructions→停滞 task 再開) を boot 後送出
#   ⑤ incident 記録 (shireiko_audit_log + pc_handshake)。
#
# ═══ 安全 (Watcher Design Principles 6 原則順守) ═══
#   - 冪等: restart_in_progress flag (TTL=SBW_INPROGRESS_TTL_SEC) で二重起動防止
#   - 連続再起動上限: SBW_RESTART_CAP/SBW_RESTART_WINDOW_MIN、超過で human_required escalate
#     (2026-05-05 SecondPC 暴走事件教訓 = enter_restart fire-cap と同型)
#   - 手動停止 flag 尊重: ~/.openclaw/global_disable / <log_dir>/DISABLE があれば一切起動しない
#   - 高頻度 heartbeat を DB に流さない (305 件 heartbeat 堆積教訓) = fire/escalate 時のみ INSERT
#   - 監査ログ終端理由を残す
#
# 終了コード: 0 = 通常完遂 (skip / fire / halt / escalate 含む)、2 = 必須 envvar 欠落
#
# テスト用フック (DoD fixture 再現に使用):
#   SBW_CLASSIFY_ONLY=1   classification だけ実行し MODE を stdout に出して exit
#   SBW_CAPTURE_FILE=path tmux capture の代わりに file 内容を pane tail として読む
#   SBW_PANE_CMD_OVERRIDE pane_current_command の代わりにこの値を使う
#   SBW_NO_DB=1           Supabase INSERT を全 skip (fixture 用)
#   SBW_DRY_RUN=1         send-keys / kill を実行せず "would …" を log するのみ
#   SBW_NOW_EPOCH         now() を固定 (cap / persistence の決定的テスト用)
#
# 安全 heredoc パターン (quoted <<'PYEOF' + os.environ + json.dumps) は
# enter_restart_common_watchdog.sh の S1 (Python source injection) 根治系譜を踏襲。

set -uo pipefail

# ─── 必須 envvar ───
for var in SBW_PANE_TARGET SBW_SESSION_NAME SBW_ROLE_NAME; do
  if [ -z "${!var:-}" ]; then
    echo "ERROR: shogun_bash_fallback_watchdog: required envvar $var is unset" >&2
    exit 2
  fi
done

PANE_TARGET="$SBW_PANE_TARGET"
SESSION_NAME="$SBW_SESSION_NAME"
ROLE_NAME="$SBW_ROLE_NAME"
REPO_DIR="${SBW_REPO_DIR:-/home/hakudoukai/multi-agent-shogun}"
TARGET_PC="${SBW_TARGET_PC:-third_pc}"
FROM_PC="${SBW_FROM_PC:-third_pc}"
STUCK_MIN="${SBW_STUCK_MIN:-5}"
RESTART_CAP="${SBW_RESTART_CAP:-3}"
RESTART_WINDOW_MIN="${SBW_RESTART_WINDOW_MIN:-60}"
INPROGRESS_TTL_SEC="${SBW_INPROGRESS_TTL_SEC:-150}"
BOOT_DELAY_SEC="${SBW_BOOT_DELAY_SEC:-30}"
KICKOFF="${SBW_KICKOFF:-1}"
HARD_KILL="${SBW_HARD_KILL:-1}"
NO_DB="${SBW_NO_DB:-0}"
DRY_RUN="${SBW_DRY_RUN:-0}"
# DB INSERT は urllib/json/os (stdlib) のみ使用ゆえ任意の python3 で可。
# third の hermes venv を既定にしつつ、無い PC では PATH の python3 に fallback (portable)。
PYTHON3_BIN="${SBW_PYTHON3_BIN:-}"
if [ -z "$PYTHON3_BIN" ]; then
  if [ -x /home/hakudoukai/.local/share/hermes-agent/venv/bin/python3 ]; then
    PYTHON3_BIN=/home/hakudoukai/.local/share/hermes-agent/venv/bin/python3
  else
    PYTHON3_BIN=python3
  fi
fi
LOG_DIR="${SBW_LOG_DIR:-$HOME/.local/share/shogun_bash_fallback_${ROLE_NAME}}"
# 既定の relaunch コマンド: doppler env 付き + --permission-mode auto (bare claude 禁)。
# 各 PC の thin wrapper が必要に応じ override (例 second_pc の bundle 版)。
# \$HOME/\$PATH は relaunch 時に pane shell が展開するよう literal で残し、$REPO_DIR は
# watchdog が今展開して typed command に埋め込む。
_SBW_DEFAULT_RELAUNCH="export PATH=\"\$HOME/.npm-global/bin:\$PATH\" && cd \"$REPO_DIR\" && doppler run --project openhands --config dev -- claude --permission-mode auto"
RELAUNCH_CMD="${SBW_RELAUNCH_CMD:-$_SBW_DEFAULT_RELAUNCH}"
KICKOFF_TEXT="${SBW_KICKOFF_TEXT:-【watchdog 再起動 directive】貴殿の Claude session は再起動された。CLAUDE.md Session Start 手順 (自己識別→memory/instructions 読込→YAML 再構築) を実行し、停滞していた task を再開せよ。}"

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y%m%d).log"
RESTART_HISTORY="$LOG_DIR/restarts.log"
INPROGRESS_FLAG="$LOG_DIR/restart_in_progress.flag"
STUCK_STATE="$LOG_DIR/stuck_state"
DISABLE_LOCAL="$LOG_DIR/DISABLE"
DISABLE_GLOBAL="$HOME/.openclaw/global_disable"

log() { printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG" >&2; }

now_epoch() { echo "${SBW_NOW_EPOCH:-$(date +%s)}"; }

# ─── Supabase INSERT (fire/escalate 時のみ。安全 heredoc) ───
db_audit_insert() {
  # $1=event_type $2=action_taken $3=result $4=detail
  [ "$NO_DB" = "1" ] && { log "[NO_DB] skip shireiko_audit_log INSERT ($2/$3)"; return 0; }
  SBW_EVENT_TYPE_PY="$1" SBW_ACTION_PY="$2" SBW_RESULT_PY="$3" SBW_DETAIL_PY="$4" \
  SBW_TARGET_PC_PY="$TARGET_PC" \
  doppler run --project openhands --config dev -- \
    "$PYTHON3_BIN" - <<'PYEOF' 2>>"$LOG" || true
import os, json, urllib.request
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/shireiko_audit_log'
payload = {
    "event_type": os.environ.get('SBW_EVENT_TYPE_PY', ''),
    "detail": os.environ.get('SBW_DETAIL_PY', ''),
    "judgment_level": 2,
    "action_taken": os.environ.get('SBW_ACTION_PY', ''),
    "result": os.environ.get('SBW_RESULT_PY', ''),
    "engine": "shogun_bash_fallback_watchdog",
    "target_pc": os.environ.get('SBW_TARGET_PC_PY', ''),
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"shireiko_audit_log INSERT rc={r.status}")
PYEOF
}

db_handshake_insert() {
  # $1=topic $2=content $3=priority
  [ "$NO_DB" = "1" ] && { log "[NO_DB] skip pc_handshake INSERT ($1)"; return 0; }
  SBW_TOPIC_PY="$1" SBW_CONTENT_PY="$2" SBW_PRIORITY_PY="$3" SBW_FROM_PC_PY="$FROM_PC" \
  doppler run --project openhands --config dev -- \
    "$PYTHON3_BIN" - <<'PYEOF' 2>>"$LOG" || true
import os, json, urllib.request, uuid
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
url = os.environ['SUPABASE_URL'] + '/rest/v1/pc_handshake'
payload = {
    "id": str(uuid.uuid4()),
    "from_pc": os.environ.get('SBW_FROM_PC_PY', ''),
    "to_pc": "fukuincho",
    "topic": os.environ.get('SBW_TOPIC_PY', ''),
    "content": os.environ.get('SBW_CONTENT_PY', ''),
    "priority": os.environ.get('SBW_PRIORITY_PY', 'low'),
    "message_type": "status_update",
}
req = urllib.request.Request(url, method='POST', data=json.dumps(payload).encode(),
    headers={'apikey':key,'Authorization':f'Bearer {key}','Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(f"pc_handshake INSERT rc={r.status}")
PYEOF
}

# ─── pane 操作 (DRY_RUN 尊重) ───
send_keys_line() {
  # $1=literal text to type, then Enter (separate, 0.3s gap = 既存 nudge 流儀)
  if [ "$DRY_RUN" = "1" ]; then log "[DRY_RUN] would send-keys: $1"; return 0; fi
  tmux send-keys -t "$PANE_TARGET" "$1" 2>>"$LOG"
  sleep 0.3
  tmux send-keys -t "$PANE_TARGET" Enter 2>>"$LOG"
}
send_key_special() {
  # $1=tmux key name (Escape / C-c)
  if [ "$DRY_RUN" = "1" ]; then log "[DRY_RUN] would send key: $1"; return 0; fi
  tmux send-keys -t "$PANE_TARGET" "$1" 2>>"$LOG"
}

# ─── classification (capture-content 主, pane_cmd 副) ───
# Claude TUI chrome (= Claude 稼働中の指標)
CHROME_RE='esc to interrupt|bypass permissions|\? for shortcuts|context (used|left)|shift\+tab|⏵⏵|tab to (cycle|expand)|❯|│[[:space:]]*>'
# stuck-retry signal
STUCK_RE='Retrying[^[:alnum:]]{0,40}attempt [0-9]+/[0-9]+|API Error.*[Rr]etry|overloaded_error|Crunching|Zigzagging|Reticulating|Hibernating|Marinating|Simmering'
# bash-fallback signal
BASH_RE='command not found|: not found|[A-Za-z0-9._-]+@[A-Za-z0-9._-]+:[^#$]*[#$][[:space:]]*$'

classify() {
  # reads $PANE_TAIL and $PANE_CMD; echoes one of: A B HEALTHY EMPTY
  local tail="$1" cmd="$2"
  if [ -z "$tail" ]; then echo "EMPTY"; return; fi
  local has_chrome=0 has_stuck=0 has_bash=0
  printf '%s' "$tail" | grep -qE "$CHROME_RE" && has_chrome=1
  printf '%s' "$tail" | grep -qE "$STUCK_RE"  && has_stuck=1
  printf '%s' "$tail" | grep -qE "$BASH_RE"   && has_bash=1
  # (A) bash-fallback: chrome 不在 + bash 兆候 (+ pane_cmd=bash で補強だが必須にしない:
  #     doppler mask の逆 = bash 落ち時は確実に bash になる)
  if [ "$has_chrome" -eq 0 ] && { [ "$has_bash" -eq 1 ] || [ "$cmd" = "bash" ]; }; then
    echo "A"; return
  fi
  # (B) stuck-retry: chrome 在り + stuck 兆候 (persistence は呼出側で判定)
  if [ "$has_chrome" -eq 1 ] && [ "$has_stuck" -eq 1 ]; then
    echo "B"; return
  fi
  echo "HEALTHY"
}

fingerprint() {
  # 直近の非空行から安定 fingerprint。spinner の「経過秒」等の可変部を除く為
  # 数字列を # に潰してから hash (= 進捗が止まれば同一 fp、進めば別 fp)。
  printf '%s' "$1" | grep -v '^[[:space:]]*$' | tail -8 | sed 's/[0-9]\+/#/g' | sha1sum | cut -d' ' -f1
}

# ════════════════════ main ════════════════════
log "=== ${ROLE_NAME} bash-fallback watchdog cycle start (pane=$PANE_TARGET) ==="

# Step 0: 手動停止 flag 尊重 (Watcher 原則 3)
if [ -f "$DISABLE_GLOBAL" ] || [ -f "$DISABLE_LOCAL" ]; then
  log "manual disable flag present (global=$([ -f "$DISABLE_GLOBAL" ] && echo 1 || echo 0) local=$([ -f "$DISABLE_LOCAL" ] && echo 1 || echo 0)) — no action"
  exit 0
fi

# capture 取得 (test override 可)
if [ -n "${SBW_CAPTURE_FILE:-}" ]; then
  PANE_TAIL=$(cat "$SBW_CAPTURE_FILE" 2>/dev/null || echo "")
  PANE_CMD="${SBW_PANE_CMD_OVERRIDE:-bash}"
else
  if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    log "WARN: tmux session '$SESSION_NAME' not found, skip"; exit 0
  fi
  if ! tmux display-message -t "$PANE_TARGET" -p '#{pane_id}' >/dev/null 2>&1; then
    log "WARN: pane '$PANE_TARGET' not found, skip"; exit 0
  fi
  PANE_CMD="${SBW_PANE_CMD_OVERRIDE:-$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_command}' 2>/dev/null || echo "")}"
  PANE_TAIL=$(tmux capture-pane -t "$PANE_TARGET" -p -S -40 2>/dev/null || echo "")
  PANE_TAIL=$(printf '%s' "$PANE_TAIL" | sed 's/\xc2\xa0/ /g')
fi

MODE=$(classify "$PANE_TAIL" "$PANE_CMD")
log "classify: mode=$MODE pane_cmd=$PANE_CMD tail_b64=$(printf '%s' "$PANE_TAIL" | tail -6 | base64 -w0)"

# テストフック: classification だけ確認して exit (persistence/relaunch を回さない)
if [ "${SBW_CLASSIFY_ONLY:-0}" = "1" ]; then
  echo "$MODE"
  exit 0
fi

# (B) persistence 判定: 同一 fingerprint が STUCK_MIN 分継続して初めて発火
if [ "$MODE" = "B" ]; then
  FP=$(fingerprint "$PANE_TAIL")
  NOW=$(now_epoch)
  if [ -f "$STUCK_STATE" ]; then
    PREV_FP=$(cut -d'|' -f1 "$STUCK_STATE" 2>/dev/null || echo "")
    PREV_TS=$(cut -d'|' -f2 "$STUCK_STATE" 2>/dev/null || echo "$NOW")
  else
    PREV_FP=""; PREV_TS="$NOW"
  fi
  if [ "$FP" = "$PREV_FP" ]; then
    ELAPSED=$(( NOW - PREV_TS ))
    log "stuck persistence: fp unchanged ${ELAPSED}s (need $((STUCK_MIN*60))s)"
    if [ "$ELAPSED" -lt $((STUCK_MIN * 60)) ]; then
      log "stuck not yet persistent enough — defer (no relaunch)"; exit 0
    fi
    # persistent enough → fall through to recovery
  else
    # 新しい fingerprint = 進捗あり or 別の stuck → タイマ reset
    printf '%s|%s\n' "$FP" "$NOW" > "$STUCK_STATE"
    log "stuck fp changed/new — reset timer, defer (no relaunch)"; exit 0
  fi
fi

if [ "$MODE" = "HEALTHY" ] || [ "$MODE" = "EMPTY" ]; then
  # 健全 = stuck timer クリア
  [ -f "$STUCK_STATE" ] && rm -f "$STUCK_STATE"
  log "no failure detected (mode=$MODE) — no action"
  exit 0
fi

# ─── ここから MODE = A or B (要復旧) ───

# Step 1: 冪等 — restart 進行中なら skip (boot 猶予)
if [ -f "$INPROGRESS_FLAG" ]; then
  FLAG_AGE=$(( $(now_epoch) - $(stat -c %Y "$INPROGRESS_FLAG" 2>/dev/null || echo 0) ))
  if [ "$FLAG_AGE" -lt "$INPROGRESS_TTL_SEC" ]; then
    log "restart in progress (flag age ${FLAG_AGE}s < ${INPROGRESS_TTL_SEC}s) — skip (idempotency)"
    exit 0
  fi
  log "stale restart flag (age ${FLAG_AGE}s) — clearing"
  rm -f "$INPROGRESS_FLAG"
fi

# Step 2: 連続再起動上限 (暴走防止)
NOW=$(now_epoch)
WINDOW_EPOCH=$(( NOW - RESTART_WINDOW_MIN * 60 ))
if [ -f "$RESTART_HISTORY" ]; then
  RECENT=$(awk -v c="$WINDOW_EPOCH" 'BEGIN{n=0}{if($1+0>=c)n++}END{print n}' "$RESTART_HISTORY" 2>/dev/null || echo 0)
else
  RECENT=0
fi
log "restart cap check: recent=${RECENT} in ${RESTART_WINDOW_MIN}min cap=${RESTART_CAP}"
if [ "$RECENT" -ge "$RESTART_CAP" ]; then
  log "★HALT★ restart cap exceeded (${RECENT} >= ${RESTART_CAP}) — escalate human_required, NO relaunch"
  db_audit_insert "shogun_bash_fallback_halt" "halted" "escalated" \
    "${ROLE_NAME} ${MODE}-mode failure but restart cap exceeded (${RECENT}>=${RESTART_CAP} in ${RESTART_WINDOW_MIN}min). human_required."
  db_handshake_insert "[human_required] ${ROLE_NAME} bash-fallback restart cap exceeded" \
    "${TARGET_PC} ${ROLE_NAME} pane=${PANE_TARGET} mode=${MODE}: 連続再起動が上限 ${RESTART_CAP}/${RESTART_WINDOW_MIN}min に到達。watchdog は自動再起動を停止。人手確認が必要 (real crash か誤検知か切り分け)。" \
    "high"
  exit 0
fi

# Step 3: @agent_id 取得 (永続、log/incident 用)
AGENT_ID="${SBW_AGENT_ID_FALLBACK:-$ROLE_NAME}"
if [ -z "${SBW_CAPTURE_FILE:-}" ]; then
  AID=$(tmux display-message -t "$PANE_TARGET" -p '#{@agent_id}' 2>/dev/null || echo "")
  [ -n "$AID" ] && AGENT_ID="$AID"
fi
log "agent_id=$AGENT_ID"

# Step 4: 冪等 flag を立てる
touch "$INPROGRESS_FLAG"

# Step 5: (B) のみ — Claude を停止し pane を解放
if [ "$MODE" = "B" ]; then
  log "MODE B: interrupt + free pane (Esc → C-c → SIGTERM child if needed)"
  send_key_special "Escape"; sleep 2
  send_key_special "C-c";    sleep 2
  send_key_special "C-c";    sleep 3
  # pane が bash に戻ったか確認
  if [ -z "${SBW_CAPTURE_FILE:-}" ]; then
    CUR=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_command}' 2>/dev/null || echo "")
    if [ "$CUR" != "bash" ] && [ "$HARD_KILL" = "1" ] && [ "$DRY_RUN" != "1" ]; then
      PANE_PID=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_pid}' 2>/dev/null || echo "")
      if [ -n "$PANE_PID" ]; then
        # pane shell の子孫 (claude/node/doppler) に SIGTERM (ローカルのみ)
        for child in $(pgrep -P "$PANE_PID" 2>/dev/null || true); do
          CNAME=$(ps -o comm= -p "$child" 2>/dev/null || echo "")
          case "$CNAME" in claude|node|doppler) log "SIGTERM child pid=$child ($CNAME)"; kill -TERM "$child" 2>>"$LOG" || true ;; esac
        done
        sleep 3
      fi
      CUR=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_command}' 2>/dev/null || echo "")
    fi
    if [ "$CUR" != "bash" ]; then
      log "WARN: pane not freed (current=$CUR) — escalate, leave flag to TTL"
      db_handshake_insert "[human_required] ${ROLE_NAME} stuck pane not freed" \
        "${TARGET_PC} ${ROLE_NAME} pane=${PANE_TARGET}: stuck-retry 停止に失敗 (current_command=${CUR})。人手介入が必要。" "high"
      exit 0
    fi
  fi
fi

# Step 6: relaunch (doppler env 付き)
log "★RELAUNCH★ mode=$MODE cmd=$RELAUNCH_CMD"
send_keys_line "$RELAUNCH_CMD"
now_epoch >> "$RESTART_HISTORY"

# Step 7: incident 記録
db_audit_insert "shogun_bash_fallback_relaunch" "relaunch_${MODE}" "success" \
  "${ROLE_NAME} (${AGENT_ID}) ${MODE}-mode failure detected on ${PANE_TARGET}; relaunched with doppler env (--permission-mode auto)."
db_handshake_insert "[watchdog] ${ROLE_NAME} relaunched (mode=${MODE})" \
  "${TARGET_PC} ${ROLE_NAME} pane=${PANE_TARGET} agent=${AGENT_ID}: ${MODE}-mode (A=bash-fallback / B=stuck-retry) 検知→doppler env 付き relaunch 実行。restart count=$((RECENT+1))/${RESTART_CAP}." \
  "normal"

# Step 8: kickoff directive (boot 待機後)
if [ "$KICKOFF" = "1" ]; then
  log "kickoff: sleep ${BOOT_DELAY_SEC}s for boot, then send directive"
  if [ "$DRY_RUN" != "1" ] && [ -z "${SBW_CAPTURE_FILE:-}" ]; then sleep "$BOOT_DELAY_SEC"; fi
  send_keys_line "$KICKOFF_TEXT"
fi

# Step 9: stuck timer クリア + 冪等 flag は次 cycle の TTL で自然消滅
[ -f "$STUCK_STATE" ] && rm -f "$STUCK_STATE"
log "=== cycle complete (mode=$MODE relaunched, restart_in_progress flag set, TTL=${INPROGRESS_TTL_SEC}s) ==="
exit 0
