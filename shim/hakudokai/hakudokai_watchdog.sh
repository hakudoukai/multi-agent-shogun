#!/usr/bin/env bash
# hakudokai_watchdog.sh — プロセス死活監視 + 自動再起動 + フェイルセーフ
# (DD-142 §4.5/§7 + Phase 2 Registry-driven monitoring + §15 SH6 restart cap)
#
# 監視対象 (Phase 2 — registry 動的読込化):
#   1. hakudokai_fukuincho_watcher.sh (Supabase→shogun inbox)
#   2. hakudokai_fukuincho_reverse_watcher.sh (shogun→Supabase)
#   3. inbox_watcher.sh per agent (= queue/pane_registry.yaml driven、legacy hardcode fallback)
#
# Phase 2 (cmd_phase2_watchdog_registry_001、base=94833a6、2026-05-08):
#   - INBOX_AGENTS hardcode → queue/pane_registry.yaml 動的読込 (flock + python yaml)
#   - 旧名→新名 alias (lib/_section18_roles.sh の section18_resolve_alias)
#   - 不在 pane (multiagent:0.8 等) は pane_exists() で自動除外
#   - takenaka/maeda/ashigaru2/ashigaru3 を registry 経由で監視
#   - §15 SH6: 同一 agent 再起動 5/h cap + escalation
#   - dual-write: registry 失敗時 LEGACY_INBOX_AGENTS 配列 fallback (cycle1 段階1)
#
# DD-142 §4.5 フェイルセーフ3段階:
#   Stage 1: 死亡検出→60秒以内に自動再起動
#   Stage 2: 3回連続失敗→urgent_stop alert (手動搬送モード = MANUAL_MODE)
#   Stage 3: /tmp/hakudokai_health_dashboard.json 30秒更新
#
# DD-142 §7 自律改善ループ:
#   - 再起動失敗時にdev_lessonsへ自動記録
#   - recurrence>=3で改善提案自動dispatch
#
# §15 SH6 (Phase 2 追加 + cmd_agent_health_check_unified_001 hardening):
#   - 同一 agent 再起動 5/h cap → 超過時 ntfy 緊急発火 + 指数バックオフ復活機構
#   - state file: /tmp/watchdog_restart_count_<agent>.json (= 5/h sliding window)
#   - alert dump: /tmp/watchdog_alert_<agent>_<ts>.json (ERR-WATCHDOG-001)
#   - backoff state: /tmp/watchdog_backoff_<agent>.json (= 死亡検知後復活、ERR-WATCHDOG-002)
#   - backoff schedule: 5min → 10min → 20min → 40min → 80min → 60min cap
#     永久 dead lock を回避、復活成功時は cap state リセット (= 旧版の hard-block 廃止)。
#
# 手動停止フラグ (Watcher Design Principles 準拠):
#   - ~/.openclaw/global_disable: 全 watchdog 機能無効化
#   - ~/.openclaw/disable_watchdog: watchdog 単独停止
#   - ~/.openclaw/registry_updating: registry 更新中、本 cycle はスキップ
#   - ~/.openclaw/disable_inbox_watcher_<agent>: 個別停止
#
# Usage: bash shim/hakudokai/hakudokai_watchdog.sh [--interval 30]
# 前提: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 環境変数
#       HAKUDOKAI_PC_ROLE (= MainPC|SecondPC、未設定時 MainPC)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHECK_INTERVAL="${2:-30}"
MAX_RESTART_FAILS=3
RESTART_CAP_PER_HOUR=5  # §15 SH6 limited self-restart cap (1h sliding window)

# Source §18 alias resolver (read-only mirror of CLAUDE.md §18.1)
# shellcheck disable=SC1091
if [ -r "${SCRIPT_DIR}/lib/_section18_roles.sh" ]; then
  source "${SCRIPT_DIR}/lib/_section18_roles.sh"
fi

# Auto-source Supabase env from ~/.hakudokai/env (CR stripped)
if [ -z "${SUPABASE_URL:-}" ] && [ -f "$HOME/.hakudokai/env" ]; then
  SUPABASE_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  SUPABASE_SERVICE_ROLE_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  export SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
fi

LOG="/tmp/hakudokai_watchdog.log"
STRUCT_LOG="/tmp/hakudokai_watchdog_struct.log"
DASHBOARD="/tmp/hakudokai_health_dashboard.json"
HEALTH_FILE="/tmp/hakudokai_watchdog.health"
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"
SUPABASE_API="${SUPABASE_URL}/rest/v1"
CORR_ID="watchdog-$$-$(date +%s)"
LAST_ACTION="startup"

# §18 PC role (= MainPC | SecondPC、未設定時 MainPC)
PC_ROLE="${HAKUDOKAI_PC_ROLE:-MainPC}"

# Registry SSoT (Phase 1 で雛形作成済、Phase 2 動的読込)
REGISTRY_FILE="${SCRIPT_DIR}/queue/pane_registry.yaml"

# 手動停止フラグ (Watcher Design Principles)
REGISTRY_UPDATING="$HOME/.openclaw/registry_updating"

# Registry load status (= dashboard publishing field)
REGISTRY_LOAD_STATUS="unknown"

# Legacy hardcoded fallback (cycle1 dual-write 段階1; cycle2 で削除予定).
# Used by get_active_agents() when registry load fails / returns empty.
LEGACY_INBOX_AGENTS="karo:multiagent:0.0 ashigaru1:multiagent:0.1 gunshi:multiagent:0.8 shogun:shogun:0.0"

# Restart failure counters (associative array, lazy-initialized via init_agent_counters)
declare -A RESTART_FAIL_COUNT
declare -A MANUAL_MODE
RESTART_FAIL_COUNT[fukuincho]=0
MANUAL_MODE[fukuincho]=false
RESTART_FAIL_COUNT[fukuincho_reverse]=0
MANUAL_MODE[fukuincho_reverse]=false

# Active agent list (= registry-driven, refreshed every cycle; fallback to LEGACY)
declare -a ACTIVE_AGENTS=()

# Stats
START_TIME=$(date +%s)
TOTAL_RESTARTS=0
TOTAL_ALERTS=0

log() {
  echo "[watchdog][$(date '+%H:%M:%S')] $1" | tee -a "$LOG" >&2
}

# §Error Design 8項目 #1: 構造化ログ (JSON) → STRUCT_LOG
# Usage: log_struct LEVEL ACTION [AGENT] [EXTRA_JSON]
log_struct() {
  local level="$1" action="$2" agent="${3:-watchdog}" extra="${4:-{\}}"
  local iso
  iso=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
  printf '{"ts":"%s","level":"%s","agent":"%s","action":"%s","corr_id":"%s","ctx":%s}\n' \
    "$iso" "$level" "$agent" "$action" "${CORR_ID}" "$extra" >> "$STRUCT_LOG" 2>/dev/null || true
}

# §18 alias resolver wrapper (旧名 → 新名).
# Falls back to inline alias map if lib/_section18_roles.sh failed to load.
agent_alias_resolve() {
  if declare -f section18_resolve_alias >/dev/null 2>&1; then
    section18_resolve_alias "$1"
  else
    case "$1" in
      shogun) echo "nobunaga" ;;
      karo) echo "hideyoshi" ;;
      gunshi) echo "ieyasu" ;;
      *) echo "$1" ;;
    esac
  fi
}

# tmux pane existence check (= 不在 pane を kill 試行から除外).
# `tmux list-panes -t <target>` returns non-zero when target absent or tmux not running.
pane_exists() {
  tmux list-panes -t "$1" >/dev/null 2>&1
}

# ─── Registry loading (Phase 2 必須 1) ─────────────────────────────────────
# stdout: list of "agent_id:tmux_target" entries (one per line) for current PC_ROLE.
# Return code disambiguation (= caller maps to REGISTRY_LOAD_STATUS in parent shell):
#   0 = ok (entries printed)
#   2 = missing (REGISTRY_FILE unreadable)
#   3 = parse_error (yaml/python error)
#   4 = empty (no entries matched PC_ROLE)
# Uses flock -s -w 5 (shared, 5s timeout) on REGISTRY_FILE to coexist with writers.
# NOTE: REGISTRY_LOAD_STATUS is intentionally NOT set here because $() runs in a
# subshell — assignment would not propagate. Caller (= get_active_agents) sets it.
load_inbox_agents_from_registry() {
  if [ ! -r "$REGISTRY_FILE" ]; then
    log "registry: not readable ($REGISTRY_FILE) — fallback"
    return 2
  fi

  local script
  script=$(cat <<'PY'
import sys, yaml
path, pc_role = sys.argv[1], sys.argv[2]
try:
    with open(path) as f:
        data = yaml.safe_load(f)
    panes = ((data or {}).get('pane_registry', {}) or {}).get('panes', []) or []
    for p in panes:
        if p.get('pc') != pc_role:
            continue
        aid = p.get('agent_id'); tgt = p.get('tmux_target')
        if aid and tgt:
            print(f"{aid}:{tgt}")
except Exception as e:
    sys.stderr.write(f"registry parse error: {e}\n")
    sys.exit(2)
PY
)
  local result rc
  result=$(flock -s -w 5 "$REGISTRY_FILE" python3 -c "$script" "$REGISTRY_FILE" "$PC_ROLE" 2>>"$LOG")
  rc=$?
  if [ "$rc" -ne 0 ]; then
    log "registry: parse FAILED (rc=$rc) — fallback to legacy"
    return 3
  fi
  if [ -z "$result" ]; then
    log "registry: empty for pc=${PC_ROLE} — fallback to legacy"
    return 4
  fi
  printf '%s\n' "$result"
  return 0
}

# ─── §15 SH6: restart cap (5/h sliding window) ────────────────────────────
# State stored in /tmp/watchdog_restart_count_<agent>.json:
#   {"timestamps": [<unix_ts>, ...]}  (entries older than 1h auto-pruned)
restart_count_file() { echo "/tmp/watchdog_restart_count_$1.json"; }

# stdout: number of restart timestamps within last 3600 seconds
restart_count_window() {
  local agent="$1"
  local file
  file=$(restart_count_file "$agent")
  if [ ! -f "$file" ]; then echo 0; return 0; fi
  python3 - "$file" 2>/dev/null <<'PY' || echo 0
import json, time, sys
path = sys.argv[1]
now = int(time.time())
cutoff = now - 3600
try:
    with open(path) as f: data = json.load(f)
    ts = [t for t in data.get('timestamps', []) if t > cutoff]
    print(len(ts))
except Exception:
    print(0)
PY
}

# Append a restart timestamp + prune entries older than 1h.
restart_count_record() {
  local agent="$1"
  local file
  file=$(restart_count_file "$agent")
  python3 - "$file" 2>/dev/null <<'PY'
import json, time, sys
path = sys.argv[1]
now = int(time.time())
cutoff = now - 3600
try:
    with open(path) as f: data = json.load(f)
except Exception:
    data = {'timestamps': []}
ts = [t for t in data.get('timestamps', []) if t > cutoff]
ts.append(now)
data['timestamps'] = ts
with open(path, 'w') as f: json.dump(data, f)
PY
}

# Returns 0 (= true / cap reached) when count >= RESTART_CAP_PER_HOUR; else 1.
restart_cap_exceeded() {
  local agent="$1" count
  count=$(restart_count_window "$agent")
  [ "$count" -ge "$RESTART_CAP_PER_HOUR" ]
}

# ─── ERR-WATCHDOG-002: exponential backoff revival after cap breach ─────
# 旧版 (= cmd_phase2 cycle1) は cap 到達後 hard-block で永久 dead lock を引き起こし、
# 全 watcher が 30s 周期で死亡 → 再起動拒否を繰り返す death loop が発生 (= 信長殿
# msg_134138 R1 統合命令の CRITICAL 案件、cmd_watchdog_health_root_cause_001)。
# 本版は cap 到達後も指数バックオフ (5min → 10min → 20min → 40min → 80min → 60min cap)
# で復活を試行、復活成功時は cap state を完全リセット。
BACKOFF_BASE_SEC=300        # 5 min
BACKOFF_MAX_SEC=3600        # 60 min
backoff_state_file() { echo "/tmp/watchdog_backoff_$1.json"; }

# stdout: number of consecutive cap breaches (= 0 when no breach yet)
backoff_breach_count() {
  local agent="$1"
  local file
  file=$(backoff_state_file "$agent")
  if [ ! -f "$file" ]; then echo 0; return 0; fi
  python3 - "$file" 2>/dev/null <<'PY' || echo 0
import json, sys
try:
    with open(sys.argv[1]) as f: data = json.load(f)
    print(int(data.get('cap_breaches', 0)))
except Exception:
    print(0)
PY
}

# Returns 0 (= true / skip) when within backoff window; 1 (= allow) when expired or no breach.
# stdout: remaining seconds (informational) when skipping.
backoff_should_skip() {
  local agent="$1"
  local file
  file=$(backoff_state_file "$agent")
  [ ! -f "$file" ] && return 1
  python3 - "$file" "$BACKOFF_BASE_SEC" "$BACKOFF_MAX_SEC" 2>/dev/null <<'PY'
import json, sys, time
path, base, cap = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
try:
    with open(path) as f: d = json.load(f)
except Exception:
    sys.exit(1)
breaches = int(d.get('cap_breaches', 0))
last = int(d.get('last_attempt', 0))
if breaches <= 0:
    sys.exit(1)
backoff = min(base * (2 ** (breaches - 1)), cap)
elapsed = int(time.time()) - last
if elapsed < backoff:
    print(f"{backoff - elapsed}s remaining (breach #{breaches}, backoff={backoff}s)")
    sys.exit(0)
sys.exit(1)
PY
}

# Increment breach count + record attempt timestamp (= called at each revival attempt).
backoff_record_breach() {
  local agent="$1"
  local file
  file=$(backoff_state_file "$agent")
  python3 - "$file" 2>/dev/null <<'PY'
import json, sys, time
path = sys.argv[1]
try:
    with open(path) as f: d = json.load(f)
except Exception:
    d = {}
d['cap_breaches'] = int(d.get('cap_breaches', 0)) + 1
d['last_attempt'] = int(time.time())
with open(path, 'w') as f: json.dump(d, f)
PY
}

# Reset backoff state on successful revival (= 復活成功時の完全 reset)。
backoff_reset() {
  local agent="$1"
  rm -f "$(backoff_state_file "$agent")" 2>/dev/null || true
}

# Lazy init for dynamically-discovered agents (= registry-loaded entries).
init_agent_counters() {
  local agent="$1"
  if [ -z "${RESTART_FAIL_COUNT[$agent]+x}" ]; then
    RESTART_FAIL_COUNT[$agent]=0
    MANUAL_MODE[$agent]=false
  fi
}

# ─── Active agent resolution (Phase 2 dual-write 段階1) ───────────────────
# Populates ACTIVE_AGENTS array each cycle:
#   1. If REGISTRY_UPDATING flag present → keep previous list, return 1
#   2. Try registry read → on success use those entries
#   3. On failure → fall back to LEGACY_INBOX_AGENTS (degraded mode)
#   4. Filter by pane_exists() (= 不在 pane を kill 試行から除外)
get_active_agents() {
  if [ -f "$REGISTRY_UPDATING" ]; then
    log "registry_updating flag detected — keeping previous ACTIVE_AGENTS this cycle"
    REGISTRY_LOAD_STATUS="updating"
    return 1
  fi

  local -a candidates=()
  local registry_output reg_rc
  registry_output=$(load_inbox_agents_from_registry)
  reg_rc=$?
  case "$reg_rc" in
    0) REGISTRY_LOAD_STATUS="ok" ;;
    2) REGISTRY_LOAD_STATUS="missing" ;;
    3) REGISTRY_LOAD_STATUS="parse_error" ;;
    4) REGISTRY_LOAD_STATUS="empty" ;;
    *) REGISTRY_LOAD_STATUS="unknown_error" ;;
  esac
  if [ "$reg_rc" -eq 0 ] && [ -n "$registry_output" ]; then
    mapfile -t candidates <<< "$registry_output"
  else
    log "using LEGACY_INBOX_AGENTS fallback (= degraded mode, status=${REGISTRY_LOAD_STATUS})"
    # shellcheck disable=SC2206
    candidates=( $LEGACY_INBOX_AGENTS )
  fi

  ACTIVE_AGENTS=()
  local entry agent pane
  for entry in "${candidates[@]}"; do
    agent="${entry%%:*}"
    pane="${entry#*:}"
    if pane_exists "$pane"; then
      ACTIVE_AGENTS+=("$entry")
    else
      log "skip [$agent]: pane $pane absent (PC=${PC_ROLE})"
    fi
  done
  return 0
}

send_urgent_alert() {
  local target="$1"
  local msg="$2"
  TOTAL_ALERTS=$((TOTAL_ALERTS + 1))
  curl -sS -X POST \
    "${SUPABASE_API}/pc_handshake" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "{\"message_type\":\"urgent_stop\",\"from_pc\":\"main_pc\",\"to_pc\":\"fukuincho\",\"topic\":\"watchdog_failsafe\",\"content\":\"${msg}\",\"requires_response\":true,\"priority\":\"urgent\",\"clinic_id\":\"${CLINIC_ID}\",\"bypass_5round_limit\":false,\"is_meta_only\":false}" \
    2>/dev/null || log "ALERT SEND FAILED for ${target}"
  log "URGENT ALERT SENT: ${msg}"
}

record_dev_lesson() {
  local error_pattern="$1"
  local root_cause="$2"
  local resolution="$3"
  # Insert into dev_lessons table via Supabase
  local payload
  payload=$(cat <<EOJSON
{
  "error_pattern": "${error_pattern}",
  "root_cause": "${root_cause}",
  "resolution_attempted": "${resolution}",
  "source": "watchdog",
  "clinic_id": "${CLINIC_ID}",
  "created_at": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
}
EOJSON
)
  curl -sS -X POST \
    "${SUPABASE_API}/dev_lessons" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "$payload" 2>/dev/null \
    && log "dev_lesson recorded: ${error_pattern}" \
    || log "dev_lesson INSERT failed (table may not exist yet)"
}

start_fukuincho_watcher() {
  log "Starting fukuincho_watcher..."
  nohup env SUPABASE_URL="$SUPABASE_URL" SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
    bash "${SCRIPT_DIR}/shim/hakudokai/hakudokai_fukuincho_watcher.sh" --interval 5 \
    >> /tmp/hakudokai_fukuincho_watcher.log 2>&1 </dev/null &
  local pid=$!
  sleep 3
  if ps -p "$pid" > /dev/null 2>&1; then
    log "fukuincho_watcher STARTED (PID=$pid)"
    RESTART_FAIL_COUNT[fukuincho]=0
    TOTAL_RESTARTS=$((TOTAL_RESTARTS + 1))
    return 0
  else
    log "fukuincho_watcher FAILED TO START"
    return 1
  fi
}

start_inbox_watcher() {
  local agent="$1"
  local pane="$2"
  local logfile="/tmp/inbox_watcher_${agent}.log"
  log "Starting inbox_watcher for $agent ($pane)..."
  nohup bash "${SCRIPT_DIR}/scripts/inbox_watcher.sh" "$agent" "$pane" claude \
    >> "$logfile" 2>&1 </dev/null &
  local pid=$!
  sleep 2
  if ps -p "$pid" > /dev/null 2>&1; then
    log "inbox_watcher[$agent] STARTED (PID=$pid)"
    RESTART_FAIL_COUNT[$agent]=0
    TOTAL_RESTARTS=$((TOTAL_RESTARTS + 1))
    return 0
  else
    log "inbox_watcher[$agent] FAILED TO START"
    tail -3 "$logfile" >> "$LOG"
    return 1
  fi
}

start_fukuincho_reverse_watcher() {
  log "Starting fukuincho_reverse_watcher..."
  nohup env SUPABASE_URL="$SUPABASE_URL" SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
    bash "${SCRIPT_DIR}/shim/hakudokai/hakudokai_fukuincho_reverse_watcher.sh" --interval 5 \
    >> /tmp/hakudokai_fukuincho_reverse_watcher.log 2>&1 </dev/null &
  local pid=$!
  sleep 3
  if ps -p "$pid" > /dev/null 2>&1; then
    log "fukuincho_reverse_watcher STARTED (PID=$pid)"
    RESTART_FAIL_COUNT[fukuincho_reverse]=0
    TOTAL_RESTARTS=$((TOTAL_RESTARTS + 1))
    return 0
  else
    log "fukuincho_reverse_watcher FAILED TO START"
    return 1
  fi
}

check_and_restart_fukuincho_reverse() {
  if ! pgrep -f "hakudokai_fukuincho_reverse_watcher.sh" > /dev/null 2>&1; then
    if [ "${MANUAL_MODE[fukuincho_reverse]}" = "true" ]; then
      log "fukuincho_reverse DEAD — MANUAL MODE (skipping)"
      return 1
    fi
    if [ -f "$HOME/.openclaw/disable_fukuincho_reverse_watcher" ]; then
      log "fukuincho_reverse DEAD — DISABLED by flag (skipping restart)"
      return 1
    fi
    log "ALERT: fukuincho_reverse DEAD — restarting"
    if ! start_fukuincho_reverse_watcher; then
      RESTART_FAIL_COUNT[fukuincho_reverse]=$((RESTART_FAIL_COUNT[fukuincho_reverse] + 1))
      if [ "${RESTART_FAIL_COUNT[fukuincho_reverse]}" -ge "$MAX_RESTART_FAILS" ]; then
        MANUAL_MODE[fukuincho_reverse]=true
        send_urgent_alert "fukuincho_reverse" "fukuincho_reverse_watcher: ${MAX_RESTART_FAILS} restart failures. MANUAL MODE."
      fi
    fi
  fi
}

# DD-142 §4.5 Stage 1+2: check, restart, escalate
check_and_restart_fukuincho() {
  if ! pgrep -f "hakudokai_fukuincho_watcher.sh" > /dev/null 2>&1; then
    if [ "${MANUAL_MODE[fukuincho]}" = "true" ]; then
      log "fukuincho_watcher DEAD — MANUAL MODE (skipping restart)"
      return 1
    fi
    if [ -f "$HOME/.openclaw/disable_fukuincho_watcher" ]; then
      log "fukuincho_watcher DEAD — DISABLED by flag (skipping restart)"
      return 1
    fi
    log "ALERT: fukuincho_watcher DEAD — restarting (fail_count=${RESTART_FAIL_COUNT[fukuincho]})"
    if ! start_fukuincho_watcher; then
      RESTART_FAIL_COUNT[fukuincho]=$((RESTART_FAIL_COUNT[fukuincho] + 1))
      if [ "${RESTART_FAIL_COUNT[fukuincho]}" -ge "$MAX_RESTART_FAILS" ]; then
        MANUAL_MODE[fukuincho]=true
        send_urgent_alert "fukuincho" "fukuincho_watcher: ${MAX_RESTART_FAILS} consecutive restart failures. Entering MANUAL MODE. PID=$$ requires human intervention."
        record_dev_lesson \
          "fukuincho_watcher_restart_failure_x${MAX_RESTART_FAILS}" \
          "Process dies immediately after restart ${MAX_RESTART_FAILS} times" \
          "Escalated to urgent_stop. Manual intervention required."
      fi
    fi
  fi
}

check_and_restart_inbox() {
  local agent="$1"
  local pane="$2"
  init_agent_counters "$agent"

  if ! pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then
    if [ "${MANUAL_MODE[$agent]}" = "true" ]; then
      log "inbox_watcher[$agent] DEAD — MANUAL MODE (skipping restart)"
      return 1
    fi
    if [ -f "$HOME/.openclaw/disable_inbox_watcher_${agent}" ]; then
      log "inbox_watcher[$agent] DEAD — DISABLED by flag (skipping restart)"
      return 1
    fi
    # §15 SH6 + ERR-WATCHDOG-002: 5/h restart cap + 指数バックオフ復活機構
    # (= 旧版 hard-block 廃止、永久 dead lock を回避、cmd_watchdog_health_root_cause_001)。
    if restart_cap_exceeded "$agent"; then
      local cap_flag="/tmp/watchdog_alert_${agent}_capped"
      # 初回 cap breach 時のみ ERR-WATCHDOG-001 で urgent alert + dump (1 回限り)
      if [ ! -f "$cap_flag" ]; then
        log "RESTART CAP EXCEEDED [$agent]: ${RESTART_CAP_PER_HOUR}/h — entering exponential backoff revival"
        send_urgent_alert "$agent" "[ERR-WATCHDOG-001] inbox_watcher[${agent}] exceeded ${RESTART_CAP_PER_HOUR} restarts/hour. Backoff revival enabled (5→10→20→40→80→60min cap)."
        cat > "/tmp/watchdog_alert_${agent}_$(date +%s).json" <<EOF
{"err_code":"ERR-WATCHDOG-001","alert":"restart_cap_exceeded","agent":"${agent}","pane":"${pane}","timestamp":"$(date -u '+%Y-%m-%dT%H:%M:%SZ')","cap_per_hour":${RESTART_CAP_PER_HOUR},"window_seconds":3600,"revival":"exponential_backoff"}
EOF
        log_struct "CRITICAL" "restart_cap_exceeded" "$agent" "{\"pane\":\"${pane}\",\"cap\":${RESTART_CAP_PER_HOUR},\"revival\":\"exponential_backoff\"}"
        touch "$cap_flag"
      fi
      # 指数バックオフ判定: window 内なら skip、expired なら復活試行。
      if backoff_should_skip "$agent" >/dev/null; then
        return 1
      fi
      # Backoff window expired → 1 回だけ復活試行 (= 新 ERR-WATCHDOG-002 escalation)。
      local breach_n
      breach_n=$(backoff_breach_count "$agent")
      log "BACKOFF REVIVAL ATTEMPT [$agent] (breach #$((breach_n + 1))) — backoff expired"
      log_struct "WARN" "backoff_revival_attempt" "$agent" "{\"pane\":\"${pane}\",\"breach\":$((breach_n + 1))}"
      backoff_record_breach "$agent"
      restart_count_record "$agent"
      if start_inbox_watcher "$agent" "$pane"; then
        sleep 5
        if pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1; then
          log "BACKOFF REVIVAL SUCCESS [$agent] — resetting cap state"
          log_struct "INFO" "backoff_revival_success" "$agent" "{\"pane\":\"${pane}\"}"
          backoff_reset "$agent"
          rm -f "$(restart_count_file "$agent")" 2>/dev/null || true
          rm -f "$cap_flag" 2>/dev/null || true
        fi
      else
        # 連続失敗時のみ ERR-WATCHDOG-002 escalation (= 3 breach 以降 = 35min+ 経過)
        if [ "$((breach_n + 1))" -ge 3 ]; then
          local prolonged_flag="/tmp/watchdog_alert_${agent}_prolonged"
          if [ ! -f "$prolonged_flag" ]; then
            send_urgent_alert "$agent" "[ERR-WATCHDOG-002] inbox_watcher[${agent}] prolonged death loop (${breach_n} backoff breaches). Manual investigation required."
            cat > "/tmp/watchdog_alert_${agent}_prolonged_$(date +%s).json" <<EOF
{"err_code":"ERR-WATCHDOG-002","alert":"prolonged_death_loop","agent":"${agent}","pane":"${pane}","timestamp":"$(date -u '+%Y-%m-%dT%H:%M:%SZ')","backoff_breaches":${breach_n}}
EOF
            log_struct "CRITICAL" "prolonged_death_loop" "$agent" "{\"pane\":\"${pane}\",\"breaches\":${breach_n}}"
            touch "$prolonged_flag"
          fi
        fi
      fi
      return 0
    fi
    log "ALERT: inbox_watcher[$agent] DEAD — restarting (fail_count=${RESTART_FAIL_COUNT[$agent]}, hourly=$(restart_count_window "$agent"))"
    restart_count_record "$agent"
    if ! start_inbox_watcher "$agent" "$pane"; then
      RESTART_FAIL_COUNT[$agent]=$((RESTART_FAIL_COUNT[$agent] + 1))
      if [ "${RESTART_FAIL_COUNT[$agent]}" -ge "$MAX_RESTART_FAILS" ]; then
        MANUAL_MODE[$agent]=true
        send_urgent_alert "$agent" "inbox_watcher[${agent}]: ${MAX_RESTART_FAILS} consecutive restart failures. Entering MANUAL MODE. PID=$$ requires human intervention."
        record_dev_lesson \
          "inbox_watcher_${agent}_restart_failure_x${MAX_RESTART_FAILS}" \
          "inbox_watcher for ${agent} dies immediately after restart ${MAX_RESTART_FAILS} times" \
          "Escalated to urgent_stop. Manual intervention required."
      fi
    fi
  fi
}

# DD-142 §4.5 Stage 3: Health dashboard
update_dashboard() {
  local now
  now=$(date +%s)
  local uptime=$((now - START_TIME))

  # Build per-process status
  local fukuincho_alive="false"
  pgrep -f "hakudokai_fukuincho_watcher.sh" > /dev/null 2>&1 && fukuincho_alive="true"
  local reverse_alive="false"
  pgrep -f "hakudokai_fukuincho_reverse_watcher.sh" > /dev/null 2>&1 && reverse_alive="true"

  local processes="\"fukuincho_watcher\":{\"alive\":${fukuincho_alive},\"manual_mode\":${MANUAL_MODE[fukuincho]},\"restart_fails\":${RESTART_FAIL_COUNT[fukuincho]}},\"fukuincho_reverse\":{\"alive\":${reverse_alive},\"manual_mode\":${MANUAL_MODE[fukuincho_reverse]},\"restart_fails\":${RESTART_FAIL_COUNT[fukuincho_reverse]}}"

  local entry agent hourly
  for entry in "${ACTIVE_AGENTS[@]}"; do
    agent="${entry%%:*}"
    init_agent_counters "$agent"
    local alive="false"
    pgrep -f "inbox_watcher.sh ${agent}" > /dev/null 2>&1 && alive="true"
    hourly=$(restart_count_window "$agent")
    processes="${processes},\"inbox_watcher_${agent}\":{\"alive\":${alive},\"manual_mode\":${MANUAL_MODE[$agent]},\"restart_fails\":${RESTART_FAIL_COUNT[$agent]},\"hourly_restart_count\":${hourly}}"
  done

  local now_iso
  now_iso=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
  cat > "$DASHBOARD" <<EOJSON
{
  "timestamp": "${now_iso}",
  "uptime_seconds": ${uptime},
  "total_restarts": ${TOTAL_RESTARTS},
  "total_alerts": ${TOTAL_ALERTS},
  "check_interval": ${CHECK_INTERVAL},
  "pc_role": "${PC_ROLE}",
  "registry_load_status": "${REGISTRY_LOAD_STATUS}",
  "active_agents_count": ${#ACTIVE_AGENTS[@]},
  "restart_cap_per_hour": ${RESTART_CAP_PER_HOUR},
  "processes": {${processes}}
}
EOJSON

  # §Error Design 8項目 #6: ヘルスチェックファイル (= 5min 以上未更新で死亡判定)
  cat > "$HEALTH_FILE" <<EOJSON
{"alive":true,"uptime":${uptime},"last_action":"${LAST_ACTION}","timestamp":"${now_iso}","pc_role":"${PC_ROLE}","registry_load_status":"${REGISTRY_LOAD_STATUS}","active_agents_count":${#ACTIVE_AGENTS[@]}}
EOJSON
}

GLOBAL_DISABLE="$HOME/.openclaw/global_disable"
WATCHDOG_DISABLE="$HOME/.openclaw/disable_watchdog"

# Check disable flags before starting
if [ -f "$GLOBAL_DISABLE" ] || [ -f "$WATCHDOG_DISABLE" ]; then
  echo "[watchdog] DISABLED by flag file — refusing to start" >&2
  exit 0
fi

log "started (interval=${CHECK_INTERVAL}s, max_restart_fails=${MAX_RESTART_FAILS}, restart_cap_per_hour=${RESTART_CAP_PER_HOUR}, pc_role=${PC_ROLE})"
log_struct "INFO" "startup" "watchdog" "{\"pc_role\":\"${PC_ROLE}\",\"interval\":${CHECK_INTERVAL},\"max_restart_fails\":${MAX_RESTART_FAILS},\"restart_cap_per_hour\":${RESTART_CAP_PER_HOUR}}"

# Phase 2: registry 動的読込 → ACTIVE_AGENTS 解決 (= 旧 INBOX_AGENTS hardcode 廃止)
LAST_ACTION="get_active_agents_initial"
get_active_agents
log "initial ACTIVE_AGENTS (n=${#ACTIVE_AGENTS[@]}, registry=${REGISTRY_LOAD_STATUS}): ${ACTIVE_AGENTS[*]:-<empty>}"
log_struct "INFO" "active_agents_resolved" "watchdog" "{\"count\":${#ACTIVE_AGENTS[@]},\"registry_status\":\"${REGISTRY_LOAD_STATUS}\"}"

# Initial health check
LAST_ACTION="initial_check"
check_and_restart_fukuincho
check_and_restart_fukuincho_reverse
for entry in "${ACTIVE_AGENTS[@]}"; do
  agent="${entry%%:*}"
  pane="${entry#*:}"
  init_agent_counters "$agent"
  check_and_restart_inbox "$agent" "$pane"
done
LAST_ACTION="initial_dashboard"
update_dashboard

while true; do
  sleep "$CHECK_INTERVAL"

  # Respect manual disable flags (Watcher Design Principles)
  if [ -f "$GLOBAL_DISABLE" ] || [ -f "$WATCHDOG_DISABLE" ]; then
    log "DISABLED by flag file — exiting gracefully"
    log_struct "INFO" "shutdown_disabled" "watchdog" "{\"reason\":\"flag_file\"}"
    rm -f "$DASHBOARD" "$HEALTH_FILE"
    exit 0
  fi

  # Refresh ACTIVE_AGENTS each cycle (= registry 変更 + REGISTRY_UPDATING flag 反映)
  LAST_ACTION="get_active_agents"
  get_active_agents

  LAST_ACTION="check_fukuincho"
  check_and_restart_fukuincho
  LAST_ACTION="check_fukuincho_reverse"
  check_and_restart_fukuincho_reverse

  for entry in "${ACTIVE_AGENTS[@]}"; do
    agent="${entry%%:*}"
    pane="${entry#*:}"
    init_agent_counters "$agent"
    LAST_ACTION="check_inbox_${agent}"
    check_and_restart_inbox "$agent" "$pane"
  done

  # DD-142 §4.5 Stage 3: Update health dashboard every cycle
  LAST_ACTION="update_dashboard"
  update_dashboard

  # Heartbeat
  log "HEARTBEAT: all checks complete (active=${#ACTIVE_AGENTS[@]}, registry=${REGISTRY_LOAD_STATUS})"
done
