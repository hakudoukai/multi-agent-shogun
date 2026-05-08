#!/usr/bin/env bash
# agent_health_check.sh — multi-agent-shogun 健康診断 + 異常時 ntfy/shogun-inbox 通知
#
# 用途: 5分毎に systemd user timer で実行、異常検知時に理事長殿/信長に通知
# Created: 2026-05-07 (理事長殿御指示「対話依存タイマー脱却、機械的仕組みへ」)
# Hardened: 2026-05-08 cmd_health_check_secret_hardening_001 (ashigaru3)
#   - SUPABASE_SERVICE_ROLE_KEY を env var 必須化 (= ~/.hakudokai/env file 読みを廃止)
#   - curl Authorization/apikey header を --config - 経由 stdin で渡す
#     (= ps aux 経由の secret 漏洩防止、家康殿 audit msg_20260507_223206)
#   - 全 SSH に -o StrictHostKeyChecking=yes 強制 (= MITM 解消、要 known_hosts 事前登録)
# Unified: 2026-05-08 cmd_agent_health_check_unified_001 (ashigaru2)
#   - Phase 5 γ-3: codex persona pane (家康/本多) の CLI mismatch 検知
#     = ERR-PERSONA-CLI-001
#   - Phase F: 会話 token 上限接近検知 (200k WARN / 240k CRITICAL)
#     = ERR-TOKEN-WARN-001 / ERR-TOKEN-CRITICAL-001
#   - 5min cooldown (連投防止) + Supabase error_log INSERT + 信長 inbox alert
#
# Check 項目:
#   1. Supabase 増殖ループ予兆 (1分間 5件超 INSERT)
#   2. claude プロセスの稼働状況 (= 各 pane で claude が動いているか)
#   3. inbox 滞留 (= 未読 10件超 = block loop の前兆)
#   4. SecondPC SSH 接続性
#   5. SecondPC inbox 滞留
#   6. codex persona CLI 整合性 (= 家康/本多 pane が codex CLI で稼働中か)
#   7. 会話 token 上限接近 (= 200k+ WARN / 240k+ CRITICAL escalation)
#
# Usage:
#   SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... bash scripts/agent_health_check.sh [--quiet]
# Output: /tmp/agent_health_check.log + ntfy (異常時のみ) + shogun inbox (Phase F/γ-3 のみ)
# Exit:
#   0: OK
#   1: alerts fired
#   2: required env var missing (= 安全側倒し、無 key 動作禁止)
#
# Pre-requirement: scripts/setup_known_hosts.sh で SecondPC fingerprint を事前登録すること。
#
# Manual disable flags (Watcher Design Principles):
#   ~/.openclaw/global_disable: 全機能無効
#   ~/.openclaw/disable_health_check: 本 script 無効
#   ~/.openclaw/disable_persona_check: codex persona 検知のみ無効
#   ~/.openclaw/disable_token_check: token 検知のみ無効

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Test-friendly overrides (= bats fixtures から差し替え可、未設定時は既定 path)。
LOG="${HEALTH_CHECK_LOG:-/tmp/agent_health_check.log}"
QUIET=false
[ "${1:-}" = "--quiet" ] && QUIET=true

# correlation_id (= 監査ログ追跡用、§10 Error Design 準拠)
CORR_ID="hc-$(date '+%Y%m%dT%H%M%S')-$$"

# ─── env var 必須化 (= 引数経由廃止 + ~/.hakudokai/env file 読み廃止) ───
# secret 値は **絶対 log しない** (key 名のみ stderr/log に出す)
if [ -z "${SUPABASE_URL:-}" ]; then
    echo "[health_check][${CORR_ID}] FATAL: SUPABASE_URL env var が未設定です。~/.hakudokai/env 等で export してから本スクリプトを呼び出してください。" >&2
    echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')][${CORR_ID}] err_code=ERR-INFRA-002 missing_env=SUPABASE_URL" >> "$LOG"
    exit 2
fi
if [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
    echo "[health_check][${CORR_ID}] FATAL: SUPABASE_SERVICE_ROLE_KEY env var が未設定です。~/.hakudokai/env 等で export してから本スクリプトを呼び出してください。" >&2
    echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')][${CORR_ID}] err_code=ERR-INFRA-002 missing_env=SUPABASE_SERVICE_ROLE_KEY" >> "$LOG"
    exit 2
fi

# 全機能無効化フラグ (Watcher Design Principles)
GLOBAL_DISABLE="$HOME/.openclaw/global_disable"
HEALTH_CHECK_DISABLE="$HOME/.openclaw/disable_health_check"
if [ -f "$GLOBAL_DISABLE" ] || [ -f "$HEALTH_CHECK_DISABLE" ]; then
    echo "[health_check][${CORR_ID}] DISABLED by flag file — exiting 0" >&2
    exit 0
fi

# ─── 共通 helper: cooldown / shogun inbox / Supabase error_log ───
ALERT_COOLDOWN_DIR="${HEALTH_CHECK_COOLDOWN_DIR:-/tmp/agent_health_check_cooldown}"
mkdir -p "$ALERT_COOLDOWN_DIR" 2>/dev/null || true
ALERT_COOLDOWN_SEC="${HEALTH_CHECK_COOLDOWN_SEC:-300}"  # 5 min (= task spec)

ALERTS=()

# Cooldown: 同一 alert key の 5min 以内連投を抑止する。
# Returns 0 (= ok to fire) when cooldown expired or first time, 1 (= skip) within window.
should_fire_alert() {
    local key="$1"
    local cf="${ALERT_COOLDOWN_DIR}/${key}.last"
    local now last elapsed
    now=$(date +%s)
    last=$(cat "$cf" 2>/dev/null || echo 0)
    last=${last%%[^0-9]*}
    last=${last:-0}
    elapsed=$((now - last))
    if [ "$elapsed" -lt "$ALERT_COOLDOWN_SEC" ]; then
        return 1
    fi
    echo "$now" > "$cf" 2>/dev/null || true
    return 0
}

# Supabase error_log への構造化 INSERT (= secret は --config - で stdin 経由)。
# 失敗時は log に記録するのみで health_check 全体は止めない (best effort)。
insert_error_log() {
    local err_code="$1" severity="$2" message="$3" ctx_json="${4:-{\}}"
    local now_iso
    now_iso=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    local payload
    payload=$(python3 - "$err_code" "$severity" "$message" "$ctx_json" "$CORR_ID" "$now_iso" <<'PY' 2>/dev/null || echo '{}'
import json, sys
err_code, severity, message, ctx_json, corr_id, ts = sys.argv[1:7]
try:
    ctx = json.loads(ctx_json) if ctx_json else {}
except Exception:
    ctx = {"raw": ctx_json}
print(json.dumps({
    "err_code": err_code,
    "severity": severity,
    "message": message,
    "corr_id": corr_id,
    "agent": "health_check",
    "ctx": ctx,
    "created_at": ts,
}))
PY
)
    [ -z "$payload" ] || [ "$payload" = '{}' ] && return 0
    curl --max-time 5 -sS -X POST \
        --config - \
        "${SUPABASE_URL}/rest/v1/error_log" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=minimal" \
        -d "$payload" 2>>"$LOG" <<EOF >/dev/null || echo "[health_check][${CORR_ID}] error_log INSERT failed (table may not exist)" >> "$LOG"
header = "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}"
header = "apikey: ${SUPABASE_SERVICE_ROLE_KEY}"
EOF
}

# 信長 inbox への alert 配信 (= scripts/inbox_write.sh 経由、self-send/amplification guard 通過)。
# 失敗時は log に記録するのみで health_check 全体は止めない。
send_shogun_inbox_alert() {
    local content="$1" type="${2:-task_assigned}"
    [ -x "$SCRIPT_DIR/scripts/inbox_write.sh" ] || return 0
    bash "$SCRIPT_DIR/scripts/inbox_write.sh" shogun "$content" "$type" health_check 2>>"$LOG" || \
        echo "[health_check][${CORR_ID}] shogun inbox_write failed" >> "$LOG"
}

# 構造化 log (JSON) → /tmp/agent_health_check_struct.log (or HEALTH_CHECK_STRUCT_LOG)
STRUCT_LOG="${HEALTH_CHECK_STRUCT_LOG:-/tmp/agent_health_check_struct.log}"
log_struct() {
    local level="$1" event="$2" extra_json="${3:-{\}}"
    local iso
    iso=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    printf '{"ts":"%s","level":"%s","corr_id":"%s","event":"%s","ctx":%s}\n' \
        "$iso" "$level" "$CORR_ID" "$event" "$extra_json" >> "$STRUCT_LOG" 2>/dev/null || true
}

# ─── 1. Supabase 増殖ループ予兆検知 ───
# curl Authorization/apikey header を --config - で stdin 経由渡し、
# ps aux で `-H "Authorization: Bearer <key>"` が見えないようにする (= secret hardening)。
NOW1_JST=$(date -d '1 minute ago' '+%Y-%m-%dT%H:%M:%S')
INSERT_COUNT=$(curl --max-time 10 -sS \
    --config - \
    "${SUPABASE_URL}/rest/v1/pc_handshake?topic=like.cross_pc_inbox_*&created_at=gte.${NOW1_JST}&select=created_at" \
    2>/dev/null <<EOF | python3 -c "import sys,json;print(len(json.loads(sys.stdin.read())))" 2>/dev/null || echo 0
header = "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}"
header = "apikey: ${SUPABASE_SERVICE_ROLE_KEY}"
EOF
)
INSERT_COUNT=${INSERT_COUNT%%[^0-9]*}
INSERT_COUNT=${INSERT_COUNT:-0}
if [ "${INSERT_COUNT:-0}" -gt 5 ]; then
    ALERTS+=("ERR-INFRA-LOOP: Supabase ${INSERT_COUNT} INSERTs/1min (=loop suspect, threshold=5)")
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

# ─── 4. SecondPC 接続性 (StrictHostKeyChecking=yes 強制 = MITM 解消) ───
SECONDPC_SSH_OPTS=(-o ConnectTimeout=5 -o StrictHostKeyChecking=yes -o BatchMode=yes)
if ! ssh "${SECONDPC_SSH_OPTS[@]}" hakudokai@192.168.11.47 'true' 2>/dev/null; then
    ALERTS+=("ERR-SECONDPC-DOWN: SSH unreachable to 192.168.11.47 (StrictHostKeyChecking=yes、要 known_hosts 事前登録 — scripts/setup_known_hosts.sh)")
fi

# ─── 5. SecondPC inbox 滞留 ───
if ssh "${SECONDPC_SSH_OPTS[@]}" hakudokai@192.168.11.47 'true' 2>/dev/null; then
    for a in ashigaru5 ashigaru6 ashigaru7; do
        n=$(ssh "${SECONDPC_SSH_OPTS[@]}" hakudokai@192.168.11.47 \
            "grep -c 'read: false' ~/projects/multi-agent-shogun/queue/inbox/${a}.yaml 2>/dev/null || echo 0" 2>/dev/null)
        n=${n%%[^0-9]*}
        if [ "${n:-0}" -gt 10 ]; then
            ALERTS+=("ERR-INBOX-OVERFLOW: SecondPC ${a} unread=${n}")
        fi
    done
fi

# ─── 6. Phase 5 γ-3: codex persona CLI 整合性検知 ───
# 家康 (multiagent:0.3) + 本多 (multiagent:1.0) は codex CLI 専属 pane (= ChatGPT Pro 認証)。
# 何らかの理由で claude CLI が起動した場合、persona 取り違え事故 (msg_134138 の R1 統合命令、
# Phase 5 γ-3) — codex 以外検出時 → ERR-PERSONA-CLI-001 alert + 5min cooldown。
# 注: pane 配置は CLAUDE.md §18.1 + queue/pane_registry.yaml に追従、ここは codex 専属 pane の集約。
PERSONA_CHECK_DISABLE="$HOME/.openclaw/disable_persona_check"
if [ ! -f "$PERSONA_CHECK_DISABLE" ]; then
    # entry format: "tmux_target:agent_label" — 配置改訂時はこの配列のみ更新する。
    # bats fixture は HEALTH_CHECK_CODEX_PANES env (= space-separated) で差し替え可。
    if [ -n "${HEALTH_CHECK_CODEX_PANES:-}" ]; then
        # shellcheck disable=SC2206
        CODEX_PERSONA_PANES=( $HEALTH_CHECK_CODEX_PANES )
    else
        CODEX_PERSONA_PANES=(
            "multiagent:0.3:ieyasu"   # 家康 (R1 統合命令)
            "multiagent:1.0:honda"    # 本多 (R1 統合命令)
        )
    fi
    for entry in "${CODEX_PERSONA_PANES[@]}"; do
        target="${entry%:*}"
        label="${entry##*:}"
        # pane 不在は skip (= 配置変動時の noise 防止、advisory のみ)。
        if ! tmux list-panes -t "$target" >/dev/null 2>&1; then
            log_struct "INFO" "persona_pane_absent" "{\"pane\":\"${target}\",\"label\":\"${label}\"}"
            continue
        fi
        pane_pid=$(tmux display-message -t "$target" -p '#{pane_pid}' 2>/dev/null || echo "")
        [ -z "$pane_pid" ] && continue

        # pstree で descendant CLI を判定 (codex は bash → node → codex の階層、
        # claude は bash → claude あるいは bash → node の階層になる)。
        tree_out=$(pstree -p "$pane_pid" 2>/dev/null || echo "")
        cli_kind="other"
        if echo "$tree_out" | grep -qE '\bcodex\(|\bcodex\b|---codex'; then
            cli_kind="codex"
        elif echo "$tree_out" | grep -qE '\bclaude\(|\bclaude\b|---claude'; then
            cli_kind="claude"
        fi
        log_struct "INFO" "persona_cli_detected" "{\"pane\":\"${target}\",\"label\":\"${label}\",\"cli\":\"${cli_kind}\"}"
        if [ "$cli_kind" != "codex" ]; then
            cool_key="persona_${label}"
            if should_fire_alert "$cool_key"; then
                msg="ERR-PERSONA-CLI-001: ${label} (${target}) running ${cli_kind} instead of codex CLI (pane_pid=${pane_pid})"
                ALERTS+=("$msg")
                ctx_json=$(printf '{"pane":"%s","label":"%s","cli_kind":"%s","pane_pid":"%s"}' \
                    "$target" "$label" "$cli_kind" "$pane_pid")
                insert_error_log "ERR-PERSONA-CLI-001" "ERROR" "$msg" "$ctx_json"
                send_shogun_inbox_alert \
                    "🚨 ERR-PERSONA-CLI-001: ${label} (${target}) で codex 以外の CLI (${cli_kind}) を検出。persona 取り違え事故防止のため即時確認要。corr_id=${CORR_ID}" \
                    task_assigned
                log_struct "ERROR" "persona_cli_mismatch" "$ctx_json"
            fi
        fi
    done
fi

# ─── 7. Phase F: 会話 token 上限接近 (auto-clear escalation) ───
# 約 200k+ で WARN / 240k+ で CRITICAL、5min cooldown で連投防止。
# 検知方式: ~/.claude/projects/<proj>/<sessionId>.jsonl の最近 (10min 以内) 更新ファイルを
# scan、最終 entry の usage (input + cache_creation + cache_read) を合算して判定。
# 注: 1 conversation = 1 jsonl ゆえ複数足軽が同 project dir を共有する場合は session 単位で
# 別個に判定する (= signal 過多にならぬよう cooldown は session_id 単位)。
TOKEN_CHECK_DISABLE="$HOME/.openclaw/disable_token_check"
TOKEN_WARN_THRESHOLD="${HEALTH_CHECK_TOKEN_WARN:-200000}"
TOKEN_CRIT_THRESHOLD="${HEALTH_CHECK_TOKEN_CRIT:-240000}"
TOKEN_PROJECT_DIR="${HEALTH_CHECK_TOKEN_PROJECT_DIR:-$HOME/.claude/projects/-mnt-c-Users-User-projects-multi-agent-shogun}"
if [ ! -f "$TOKEN_CHECK_DISABLE" ] && [ -d "$TOKEN_PROJECT_DIR" ]; then
    while IFS= read -r jsonl_path; do
        [ -z "$jsonl_path" ] && continue
        sid=$(basename "$jsonl_path" .jsonl)
        sid_short="${sid:0:8}"
        max_tokens=$(tail -20 "$jsonl_path" 2>/dev/null | python3 -c '
import json, sys
mx = 0
for line in sys.stdin:
    try:
        d = json.loads(line)
        u = ((d.get("message") or {}).get("usage") or {})
        t = int(u.get("input_tokens", 0) or 0) + int(u.get("cache_creation_input_tokens", 0) or 0) + int(u.get("cache_read_input_tokens", 0) or 0)
        if t > mx:
            mx = t
    except Exception:
        pass
print(mx)
' 2>/dev/null || echo 0)
        max_tokens=${max_tokens%%[^0-9]*}
        max_tokens=${max_tokens:-0}
        if [ "$max_tokens" -ge "$TOKEN_CRIT_THRESHOLD" ]; then
            cool_key="token_crit_${sid_short}"
            if should_fire_alert "$cool_key"; then
                msg="ERR-TOKEN-CRITICAL-001: session=${sid_short} tokens=${max_tokens} (>=${TOKEN_CRIT_THRESHOLD}, auto-clear escalation)"
                ALERTS+=("$msg")
                ctx_json=$(printf '{"session":"%s","tokens":%d,"threshold":%d}' \
                    "$sid_short" "$max_tokens" "$TOKEN_CRIT_THRESHOLD")
                insert_error_log "ERR-TOKEN-CRITICAL-001" "CRITICAL" "$msg" "$ctx_json"
                send_shogun_inbox_alert \
                    "🚨 ERR-TOKEN-CRITICAL-001: session=${sid_short} tokens=${max_tokens} (>=240k)、auto-clear escalation 即時要。corr_id=${CORR_ID}" \
                    task_assigned
                log_struct "CRITICAL" "token_critical" "$ctx_json"
            fi
        elif [ "$max_tokens" -ge "$TOKEN_WARN_THRESHOLD" ]; then
            cool_key="token_warn_${sid_short}"
            if should_fire_alert "$cool_key"; then
                msg="ERR-TOKEN-WARN-001: session=${sid_short} tokens=${max_tokens} (>=${TOKEN_WARN_THRESHOLD})"
                ALERTS+=("$msg")
                ctx_json=$(printf '{"session":"%s","tokens":%d,"threshold":%d}' \
                    "$sid_short" "$max_tokens" "$TOKEN_WARN_THRESHOLD")
                insert_error_log "ERR-TOKEN-WARN-001" "WARN" "$msg" "$ctx_json"
                send_shogun_inbox_alert \
                    "⚠ ERR-TOKEN-WARN-001: session=${sid_short} tokens=${max_tokens} (>=200k)、近く auto-clear 要。corr_id=${CORR_ID}" \
                    task_assigned
                log_struct "WARN" "token_warn" "$ctx_json"
            fi
        fi
    done < <(find "$TOKEN_PROJECT_DIR" -maxdepth 1 -name '*.jsonl' -mmin -10 2>/dev/null)
fi

# ─── 結果記録 ───
{
    echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')][${CORR_ID}] health_check"
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

[ "$QUIET" = "false" ] && echo "[health_check][${CORR_ID}] OK (insert_count_1min=${INSERT_COUNT}, alerts=0)"
exit 0
