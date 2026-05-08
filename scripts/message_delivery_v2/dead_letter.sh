#!/usr/bin/env bash
# scripts/message_delivery_v2/dead_letter.sh — dead-letter queue handler
#
# Phase 0 反省点 h (= retry 無限ループ) + 反省点 o (= dead-letter queue 不在) への対応。
# retry cap 5 を超過した msg を queue/dead_letter/<agent>/<msg_id>.yaml へ移動、
# escalation alert を信長 inbox + dashboard へ送る。
#
# Usage:
#   source scripts/message_delivery_v2/dead_letter.sh
#   move_to_dead_letter <agent_id> <msg_id> <reason> [<retry_history_json>]
#   get_retry_count <agent_id> <msg_id>
#   increment_retry <agent_id> <msg_id>
#
# 設計: docs/message_delivery_v2_design_2026-05-08.md §3.3

set -euo pipefail

_DLQ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_DLQ_PROJECT_ROOT="$(cd "${_DLQ_DIR}/../.." && pwd)"

DLQ_BASE="${_DLQ_PROJECT_ROOT}/queue/dead_letter"
RETRY_STATE_DIR="${_DLQ_PROJECT_ROOT}/queue/watchers"
RETRY_CAP=5

# get_retry_count <agent_id> <msg_id>
# returns: integer retry count (default 0)
get_retry_count() {
    local agent="$1"
    local msg_id="$2"
    local retry_file="${RETRY_STATE_DIR}/${agent}.retry.${msg_id}"
    if [[ -f "$retry_file" ]]; then
        cat "$retry_file"
    else
        echo 0
    fi
}

# increment_retry <agent_id> <msg_id>
# returns: new retry count
increment_retry() {
    local agent="$1"
    local msg_id="$2"
    local retry_file="${RETRY_STATE_DIR}/${agent}.retry.${msg_id}"
    local current
    current=$(get_retry_count "$agent" "$msg_id")
    local new=$((current + 1))
    echo "$new" > "$retry_file"
    echo "$new"
}

# is_over_retry_cap <agent_id> <msg_id>
# returns: 0 if over cap (= should be dead-lettered), 1 otherwise
is_over_retry_cap() {
    local agent="$1"
    local msg_id="$2"
    local count
    count=$(get_retry_count "$agent" "$msg_id")
    if [[ $count -ge $RETRY_CAP ]]; then
        return 0
    else
        return 1
    fi
}

# move_to_dead_letter <agent_id> <msg_id> <reason> [<original_content>]
# Moves a msg to dead_letter queue with metadata.
move_to_dead_letter() {
    local agent="$1"
    local msg_id="$2"
    local reason="$3"
    local original_content="${4:-}"

    local dlq_dir="${DLQ_BASE}/${agent}"
    mkdir -p "$dlq_dir"

    local dlq_file="${dlq_dir}/${msg_id}.yaml"
    local retry_count
    retry_count=$(get_retry_count "$agent" "$msg_id")
    local now
    now=$(date -Iseconds)

    cat > "$dlq_file" <<EOF
msg_id: ${msg_id}
agent_id: ${agent}
moved_at: "${now}"
reason: ${reason}
retry_count: ${retry_count}
retry_cap: ${RETRY_CAP}
escalation_sent: false
original_content: |
$(echo "${original_content}" | sed 's/^/  /')
EOF

    # retry state cleanup
    rm -f "${RETRY_STATE_DIR}/${agent}.retry.${msg_id}"

    # escalation を信長 inbox に送信 (= reason が dedup_skip / self_send 等の安全 reason は除外)
    case "$reason" in
        dedup_skip|self_send|expired_ttl)
            # benign reason、escalation 不要
            ;;
        *)
            _escalate_to_shogun "$agent" "$msg_id" "$reason"
            ;;
    esac

    echo "moved: $dlq_file"
}

# _escalate_to_shogun <agent> <msg_id> <reason>
# 信長 inbox に dead-letter 通知を送る (= 既存 inbox_write.sh 経由)
_escalate_to_shogun() {
    local agent="$1"
    local msg_id="$2"
    local reason="$3"
    local content
    content="🚨 ERR-WATCHER-DLQ-001: ${agent} msg ${msg_id} dead-lettered. reason=${reason}, retry_cap=${RETRY_CAP} 超過。queue/dead_letter/${agent}/${msg_id}.yaml 確認要。"

    if [[ -x "${_DLQ_PROJECT_ROOT}/scripts/inbox_write.sh" ]]; then
        bash "${_DLQ_PROJECT_ROOT}/scripts/inbox_write.sh" shogun "$content" critical_alert dead_letter_handler 2>/dev/null || true
    fi

    # mark escalation_sent
    local dlq_file="${DLQ_BASE}/${agent}/${msg_id}.yaml"
    if [[ -f "$dlq_file" ]]; then
        sed -i 's/^escalation_sent: false$/escalation_sent: true/' "$dlq_file" 2>/dev/null || true
    fi
}

# dlq_count <agent_id>
# returns: number of dead-lettered messages for an agent
dlq_count() {
    local agent="$1"
    local dlq_dir="${DLQ_BASE}/${agent}"
    if [[ -d "$dlq_dir" ]]; then
        find "$dlq_dir" -maxdepth 1 -name '*.yaml' 2>/dev/null | wc -l
    else
        echo 0
    fi
}
