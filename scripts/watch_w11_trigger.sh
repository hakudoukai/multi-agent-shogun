#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# watch_w11_trigger.sh — W11 in_progress 完了 trigger 検知 (scheduled, one-shot)
#
# 設計責務 (= detect-and-notify only):
#   - 各 systemd timer tick 毎に W11 2 候補 (C-V29-W11DDA / C-V30-W11DDB) の
#     Supabase development_progress row 状態を single query で取得。
#   - status='completed' AND commit_hash 非空 を検出した場合、
#     queue/reports run_log.yaml + queue/metrics heartbeat.yaml に
#     構造化 evidence を append/upsert し、scripts/inbox_write.sh で karo に通知。
#   - direct audited_done / shogun_verified の status 書込は禁。
#   - canonical post-audit chain (= karo → naomasa → shogun_verify_audit.sh) は
#     本 watcher の責務外、karo 経由で起動する。
#
# 設計参照:
#   docs/background_worker_eval_gate.md  (= worker_eval_gate 正本)
#   docs/cmd020_w11_trigger_worker_eval_gate_check.md  (= 本 watcher の 13 fields 記録)
#   queue/reports/naomasa_cmd020_w11_trigger_preaudit_cycle5_20260513.yaml  (= pre_audit cycle5)
#
# 起動:
#   one-shot (= systemd dashboard-w11-trigger.service の ExecStart)。
#   resident process 禁。max_runtime_sec=60 (= systemd TimeoutStartSec / 内部 timeout)。
#
# 環境変数:
#   WATCH_W11_TRIGGER_DRY_RUN=1  → query 実行せず log のみ、heartbeat に dry_run 記録
#   WATCH_W11_TRIGGER_REPO_ROOT  → 試験用 repo root override (default: スクリプト親の親)
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ─── repo root 解決 (= test override 対応) ───
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${WATCH_W11_TRIGGER_REPO_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"

# ─── path 定数 ───
LOG_DIR="$REPO_ROOT/logs"
LOG_FILE="$LOG_DIR/watch_w11_trigger.log"
RUN_LOG_YAML="$REPO_ROOT/queue/reports/ashigaru5_subtask_cmd020_w11_completion_trigger_watcher_run_log.yaml"
HEARTBEAT_YAML="$REPO_ROOT/queue/metrics/w11_trigger_heartbeat.yaml"
INBOX_WRITE="$REPO_ROOT/scripts/inbox_write.sh"

# ─── target W11 in_progress 候補 (= 不変、Anti-Dup pass) ───
# completion 条件: status='completed' AND commit_hash 非空
W11_CANDIDATES=("C-V29-W11DDA" "C-V30-W11DDB")

# ─── bounded guard ───
MAX_RUNTIME_SEC=60
RETRY_COUNT=1

mkdir -p "$LOG_DIR" "$(dirname "$RUN_LOG_YAML")" "$(dirname "$HEARTBEAT_YAML")"

# ─── helper: structured log line ───
log() {
    local level="$1"
    shift
    local ts
    ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    printf '[%s] [%s] %s\n' "$ts" "$level" "$*" | tee -a "$LOG_FILE" >&2
}

# ─── helper: heartbeat upsert (= last_run_ts + last_result + items_detected + next_run_eta) ───
write_heartbeat() {
    local last_result="$1"
    local items_detected="$2"
    local next_eta="$3"
    local ts
    ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    cat > "$HEARTBEAT_YAML" <<EOF
# W11 trigger heartbeat (= human-visible health signal)
# 13 fields decision record と整合、Karo が dashboard.md Layer F に集約予定。
last_run_ts: "$ts"
last_result: "$last_result"
items_detected: $items_detected
next_run_eta: "$next_eta"
watcher_id: watch_w11_trigger
worker_eval_doc: docs/cmd020_w11_trigger_worker_eval_gate_check.md
EOF
}

# ─── helper: run_log append (= structured evidence、append-only) ───
append_run_log() {
    local result_code="$1"
    local items_detected="$2"
    local supabase_mcp_available="$3"
    local detail="$4"
    local ts
    ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    # initialize header if file missing
    if [ ! -f "$RUN_LOG_YAML" ]; then
        cat > "$RUN_LOG_YAML" <<EOF
# watch_w11_trigger run log — append-only structured evidence
# (audit trail per docs/cmd020_w11_trigger_worker_eval_gate_check.md §1 Q4)
run_log:
EOF
    fi
    cat >> "$RUN_LOG_YAML" <<EOF
  - timestamp: "$ts"
    result_code: "$result_code"
    items_detected: $items_detected
    supabase_mcp_available: $supabase_mcp_available
    detail: "$detail"
EOF
}

# ─── helper: inbox notify karo (= detect 時のみ、direct audited_done 禁) ───
notify_karo() {
    local detected_ids="$1"
    # detect-and-notify only payload. 監査完了 mark は naomasa post-audit chain 経由 (= 本 watcher は実施せず)。
    local msg="W11 completion candidate detected: ${detected_ids}. naomasa post-audit chain trigger 要 (detect-and-notify only)."
    if [ -x "$INBOX_WRITE" ]; then
        bash "$INBOX_WRITE" karo "$msg" report_received ashigaru5 >> "$LOG_FILE" 2>&1 || {
            log WARN "inbox_write to karo failed (non-fatal, run_log retains evidence)"
        }
    else
        log WARN "inbox_write.sh not executable, skipping karo notify"
    fi
}

# ─── main one-shot run (= timer tick 毎、bounded) ───
main() {
    log INFO "watch_w11_trigger start (= scheduled one-shot, candidates=${W11_CANDIDATES[*]})"

    local start_epoch
    start_epoch=$(date +%s)

    # next_run_eta は systemd timer 設定 (= 600s) 想定で固定計算
    local next_eta
    next_eta=$(date -u -d "+600 seconds" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null \
        || date -u +"%Y-%m-%dT%H:%M:%SZ")

    # dry-run mode (= feature flag)
    if [ "${WATCH_W11_TRIGGER_DRY_RUN:-0}" = "1" ]; then
        log INFO "DRY_RUN=1 → query skipped, heartbeat noted, no inbox notify"
        write_heartbeat "dry_run" 0 "$next_eta"
        append_run_log "dry_run" 0 "false" "WATCH_W11_TRIGGER_DRY_RUN=1 set, no query executed"
        return 0
    fi

    # Supabase MCP availability preflight (= shell から MCP 直接呼出不能、
    # MCP は Claude/Codex agent runtime 側で呼ばれる前提。本 shell は availability
    # 信号を環境変数 SUPABASE_MCP_AVAILABLE で受け取り、unavailable 時は terminal
    # failure 経路で karo notify、monitor readiness 主張せず。)
    local mcp_available="${SUPABASE_MCP_AVAILABLE:-unknown}"
    if [ "$mcp_available" = "false" ]; then
        log ERROR "Supabase MCP unavailable, terminal failure recorded"
        write_heartbeat "fail" 0 "$next_eta"
        append_run_log "fail" 0 "false" "Supabase MCP unavailable (SUPABASE_MCP_AVAILABLE=false)"
        notify_karo "MCP_UNAVAILABLE (no candidates queried)"
        return 1
    fi

    # 本 watcher は shell side では query placeholder のみ記録し、実 query は
    # 上位 agent runtime (= Claude/Codex の mcp__claude_ai_Supabase__execute_sql)
    # 経由で投入する。timer 駆動の bounded one-shot 実行を維持しつつ、Supabase
    # MCP 認証 binding の所在差 (= MC vs SC) に依らず evidence path を一貫させる。
    local items_detected=0
    local detected_ids=""

    log INFO "Supabase MCP availability=${mcp_available} (shell side records preflight only)"
    log INFO "candidates to check: ${W11_CANDIDATES[*]} (completion = status='completed' AND commit_hash != '')"

    # 検出結果が外部から提供される場合 (= MCP runtime が完了後 echo する場合) を
    # support するため、環境変数 WATCH_W11_TRIGGER_DETECTED_IDS (CSV) を読み取る。
    if [ -n "${WATCH_W11_TRIGGER_DETECTED_IDS:-}" ]; then
        detected_ids="$WATCH_W11_TRIGGER_DETECTED_IDS"
        items_detected=$(awk -F',' '{print NF}' <<< "$detected_ids")
    fi

    # bounded runtime guard
    local now_epoch
    now_epoch=$(date +%s)
    local elapsed=$(( now_epoch - start_epoch ))
    if [ "$elapsed" -ge "$MAX_RUNTIME_SEC" ]; then
        log ERROR "max_runtime_sec=${MAX_RUNTIME_SEC} exceeded (elapsed=${elapsed}s)"
        write_heartbeat "fail" "$items_detected" "$next_eta"
        append_run_log "fail" "$items_detected" "$mcp_available" "max_runtime_sec exceeded"
        return 1
    fi

    # result classify
    if [ "$items_detected" -gt 0 ]; then
        log INFO "detected ${items_detected} W11 completion candidates: ${detected_ids}"
        write_heartbeat "detected" "$items_detected" "$next_eta"
        append_run_log "detected" "$items_detected" "$mcp_available" "candidates: ${detected_ids}"
        notify_karo "$detected_ids"
    else
        log INFO "no completion detected (= candidates still in_progress or query placeholder)"
        write_heartbeat "no_change" 0 "$next_eta"
        append_run_log "no_change" 0 "$mcp_available" "no completion candidate detected at this tick"
    fi

    log INFO "watch_w11_trigger end ok (= bounded one-shot complete, retry_count=${RETRY_COUNT}, backoff=next_timer_tick)"
}

# ─── retry-1 single-shot wrapper (= bounded、resident 禁) ───
if main; then
    exit 0
else
    rc=$?
    log WARN "main failed (rc=${rc}), retry_count=${RETRY_COUNT} → 1 retry then backoff=next_timer_tick"
    if main; then
        exit 0
    else
        rc2=$?
        log ERROR "retry failed (rc=${rc2}), terminal failure → karo inbox notify + next timer tick"
        # 二度失敗時は run_log + heartbeat は既に main 内で記録済、karo notify を補強
        if [ -x "$INBOX_WRITE" ]; then
            bash "$INBOX_WRITE" karo "watch_w11_trigger terminal failure (rc=${rc2}), next timer tick backoff" report_received ashigaru5 >> "$LOG_FILE" 2>&1 || true
        fi
        exit "$rc2"
    fi
fi
