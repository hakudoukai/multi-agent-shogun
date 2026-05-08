#!/usr/bin/env bash
# scripts/message_delivery_v2/dedup.sh — message dedup table
#
# Phase 0 反省点 g (= dedup 不在で同一 message_id 二度処理 risk) への対応。
# queue/message_dedup.yaml で processed_message_ids を保持、同一 msg_id の重複処理を抑止。
# TTL 24h で auto-cleanup。
#
# Usage:
#   source scripts/message_delivery_v2/dedup.sh
#   if dedup_already_processed "$msg_id"; then ... fi
#   dedup_record "$msg_id" "delivered"
#   dedup_cleanup
#
# 設計: docs/message_delivery_v2_design_2026-05-08.md §3.2

set -euo pipefail

_DEDUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_DEDUP_PROJECT_ROOT="$(cd "${_DEDUP_DIR}/../.." && pwd)"

DEDUP_TABLE="${_DEDUP_PROJECT_ROOT}/queue/message_dedup.yaml"
DEDUP_TTL_SEC=86400  # 24h

# init dedup table
_dedup_init() {
    if [[ ! -f "$DEDUP_TABLE" ]]; then
        printf 'processed: []\n' > "$DEDUP_TABLE"
    fi
}

# dedup_already_processed <msg_id>
# returns: 0 if already processed (= duplicate), 1 if not
dedup_already_processed() {
    local msg_id="$1"
    _dedup_init
    if grep -qE "^\s*- msg_id:\s+${msg_id}\s*$" "$DEDUP_TABLE" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# dedup_record <msg_id> <ack_by>
# Records a processed message with TTL-based expiration.
dedup_record() {
    local msg_id="$1"
    local ack_by="${2:-delivered}"
    _dedup_init

    local now
    now=$(date -Iseconds)
    local expires
    expires=$(date -Iseconds -d "+24 hours" 2>/dev/null || date -v+1d -Iseconds 2>/dev/null || echo "")

    # append entry (= idempotent)
    if dedup_already_processed "$msg_id"; then
        return 0
    fi

    cat >> "$DEDUP_TABLE" <<EOF
  - msg_id: ${msg_id}
    processed_at: "${now}"
    ack_by: ${ack_by}
    expires_at: "${expires}"
EOF
}

# dedup_cleanup
# Removes entries with expires_at < now.
dedup_cleanup() {
    _dedup_init
    local now_epoch
    now_epoch=$(date +%s)
    local tmp
    tmp=$(mktemp)
    python3 <<PYEOF > "$tmp"
import yaml, sys
from datetime import datetime
try:
    with open("${DEDUP_TABLE}") as f:
        d = yaml.safe_load(f) or {}
    now = datetime.now().astimezone()
    kept = []
    for e in d.get('processed', []):
        exp = e.get('expires_at')
        if not exp:
            kept.append(e)
            continue
        try:
            exp_dt = datetime.fromisoformat(exp.replace('Z', '+00:00'))
            if exp_dt > now:
                kept.append(e)
        except Exception:
            kept.append(e)
    out = {'processed': kept}
    print(yaml.safe_dump(out, allow_unicode=True, sort_keys=False))
except Exception as e:
    sys.stderr.write(f"dedup_cleanup error: {e}\n")
    sys.exit(1)
PYEOF
    if [[ -s "$tmp" ]]; then
        mv -f "$tmp" "$DEDUP_TABLE"
    else
        rm -f "$tmp"
    fi
}

# dedup_count
# returns: number of currently tracked entries
dedup_count() {
    _dedup_init
    grep -cE '^\s*- msg_id:' "$DEDUP_TABLE" 2>/dev/null || echo 0
}
