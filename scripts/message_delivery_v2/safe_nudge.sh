#!/usr/bin/env bash
# scripts/message_delivery_v2/safe_nudge.sh — 安全 send-keys wrapper
#
# Phase 0 反省点 c (= send-keys 連発) + 反省点 e (= clear_command 強引 retry) +
# 反省点 f (= post-reset Session Start 衝突) + 反省点 n (= pane drift 誤配) +
# 反省点 w (= Codex 長文 submit 不確定) + 反省点 x (= ESCALATION 暴発) への対応。
#
# 全 send-keys は本 wrapper 経由で実行、direct tmux send-keys は禁止
# (除く supervisor + 信長緊急介入)。
#
# Usage:
#   bash scripts/message_delivery_v2/safe_nudge.sh <agent_id> <pane_target> <cli_type> <nudge_text> [<correlation_id>]
#   exit code:
#     0 = delivered (= send-keys 成功)
#     1 = queued (= cooldown / drift で延期、再試行は 60s 後)
#     2 = blocked (= Working / sandbox prompt、人手介入要)
#     3 = pane_drift (= agent_id 不一致、絶対拒否)
#     4 = book_mode_fallback (= TUI 空白、書面 mode に切替)
#     5 = bash_shell (= Codex 終了、緊急介入要)
#
# 設計: docs/message_delivery_v2_design_2026-05-08.md §2.3
# 本多 HND-MDV2-004 反映: SSoT を本ファイルに固定、root scripts/ に二重実装残さず

set -euo pipefail

AGENT_ID="${1:-}"
PANE_TARGET="${2:-}"
CLI_TYPE="${3:-}"
NUDGE_TEXT="${4:-}"
CORRELATION_ID="${5:-}"

if [[ -z "$AGENT_ID" || -z "$PANE_TARGET" || -z "$CLI_TYPE" || -z "$NUDGE_TEXT" ]]; then
    echo "Usage: $0 <agent_id> <pane_target> <cli_type> <nudge_text> [<correlation_id>]" >&2
    exit 99
fi

_NUDGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_NUDGE_PROJECT_ROOT="$(cd "${_NUDGE_DIR}/../.." && pwd)"

LOG_DIR="${_NUDGE_PROJECT_ROOT}/logs/message_delivery_v2"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/safe_nudge_$(date +%Y%m%d).log"

COOLDOWN_FILE="${_NUDGE_PROJECT_ROOT}/queue/watchers/${AGENT_ID}.last_nudge"
SESSION_HEALTH_DIR="${_NUDGE_PROJECT_ROOT}/queue/session_health"
mkdir -p "$SESSION_HEALTH_DIR"

log_event() {
    local level="$1"
    local result="$2"
    shift 2
    local extra="${*:-}"
    local ts
    ts=$(date -Iseconds)
    printf '{"ts":"%s","level":"%s","component":"safe_nudge","agent":"%s","pane":"%s","cli":"%s","result":"%s","corr_id":"%s","extra":"%s"}\n' \
        "$ts" "$level" "$AGENT_ID" "$PANE_TARGET" "$CLI_TYPE" "$result" "${CORRELATION_ID:-}" "$extra" >> "$LOG_FILE"
}

# 1. global_disable check
if [[ -f "$HOME/.openclaw/global_disable" ]]; then
    log_event INFO blocked "reason=global_disable"
    exit 2
fi

# 2. Codex pane の場合 codex_guard で pre-flight check
if [[ "$CLI_TYPE" == "codex" || "$CLI_TYPE" == "node" ]]; then
    set +e
    "${_NUDGE_DIR}/codex_guard.sh" "$AGENT_ID" "$PANE_TARGET" >/dev/null 2>&1
    guard_rc=$?
    set -e
    case $guard_rc in
        0) ;;  # allow
        1) log_event WARN queued "reason=codex_guard_cooldown"; exit 1 ;;
        2) log_event WARN blocked "reason=codex_working_or_sandbox_prompt"; exit 2 ;;
        3) log_event ERROR pane_drift "reason=agent_id_mismatch"; exit 3 ;;
        4) log_event WARN book_mode "reason=tui_empty"; exit 4 ;;
        5) log_event ERROR bash_shell "reason=codex_exited"; exit 5 ;;
        *) log_event ERROR blocked "reason=codex_guard_unknown_rc_${guard_rc}"; exit 2 ;;
    esac
fi

# 3. Claude pane の場合の pane identity verify (= 反省点 n)
if [[ "$CLI_TYPE" == "claude" ]]; then
    pane_agent_id=$(tmux display-message -t "$PANE_TARGET" -p '#{@agent_id}' 2>/dev/null || echo "")
    if [[ "$pane_agent_id" != "$AGENT_ID" ]]; then
        log_event ERROR pane_drift "expected=${AGENT_ID} actual=${pane_agent_id}"
        exit 3
    fi
    pane_cmd=$(tmux display-message -t "$PANE_TARGET" -p '#{pane_current_command}' 2>/dev/null || echo "")
    if [[ "$pane_cmd" != "claude" ]]; then
        log_event ERROR pane_drift "expected_cmd=claude actual_cmd=${pane_cmd}"
        exit 3
    fi
fi

# 4. cooldown check (= 同一 agent への直前 send-keys から 120s 未満は queued)
COOLDOWN_SEC=120
if [[ -f "$COOLDOWN_FILE" ]]; then
    last_epoch=$(cat "$COOLDOWN_FILE" 2>/dev/null || echo 0)
    now_epoch=$(date +%s)
    elapsed=$((now_epoch - last_epoch))
    if [[ $elapsed -lt $COOLDOWN_SEC ]]; then
        log_event WARN queued "cooldown_remaining=$((COOLDOWN_SEC - elapsed))"
        exit 1
    fi
fi

# 5. nudge text 長さ確認 (= 反省点 w 対応、Codex 100 文字超は書面 mode 推奨)
nudge_len=${#NUDGE_TEXT}
if [[ "$CLI_TYPE" == "codex" || "$CLI_TYPE" == "node" ]]; then
    if [[ $nudge_len -gt 100 ]]; then
        log_event WARN book_mode "reason=long_nudge_${nudge_len}chars_codex"
        # 書面 mode へ fallback (= session_health に entry)
        echo "{\"agent\":\"${AGENT_ID}\",\"book_entry_at\":\"$(date -Iseconds)\",\"reason\":\"long_nudge_codex\",\"nudge\":\"${NUDGE_TEXT//\"/\\\"}\",\"corr_id\":\"${CORRELATION_ID}\"}" \
            >> "${SESSION_HEALTH_DIR}/${AGENT_ID}.book_mode.jsonl"
        exit 4
    fi
fi

# 6. send-keys 実施
set +e
tmux send-keys -t "$PANE_TARGET" "$NUDGE_TEXT" Enter
send_rc=$?
set -e

if [[ $send_rc -ne 0 ]]; then
    log_event ERROR blocked "tmux_send_keys_rc=${send_rc}"
    exit 2
fi

# 7. cooldown 更新
date +%s > "$COOLDOWN_FILE"

# 8. 成功 log
log_event INFO delivered "nudge_len=${nudge_len}"
echo "delivered: $AGENT_ID at $PANE_TARGET"
exit 0
