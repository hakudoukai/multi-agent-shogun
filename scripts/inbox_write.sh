#!/usr/bin/env bash
# inbox_write.sh — メールボックスへのメッセージ書き込み（排他ロック付き）
# Usage: bash scripts/inbox_write.sh <target_agent> <content> <type> <from>
# Example: bash scripts/inbox_write.sh karo "足軽5号、任務完了" report_received ashigaru5

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$1"
CONTENT="$2"
TYPE="$3"
FROM="$4"

INBOX="$SCRIPT_DIR/queue/inbox/${TARGET}.yaml"
LOCKFILE="${INBOX}.lock"

# Validate arguments
if [ -z "$TARGET" ] || [ -z "$CONTENT" ] || [ -z "$TYPE" ] || [ -z "$FROM" ]; then
    echo "Usage: inbox_write.sh <target_agent> <content> <type> <from>" >&2
    exit 1
fi

# Self-send guard: reject messages where sender == target
if [ "$FROM" = "$TARGET" ]; then
    echo "[inbox_write] REJECTED: self-send detected (from=$FROM, target=$TARGET)" >&2
    exit 1
fi

# Amplification guard (2026-05-07 真因対策):
# stop_hook block + claude bash 経由の自己増殖ループ防止。
# content に「[<from>→<target>][<type>]」パターンが 3 回以上含まれていたら、
# 既に増幅された content の再送信と判定して reject。
_AMP_PATTERN_COUNT=$(echo "$CONTENT" | grep -oE '\[[a-zA-Z_0-9]+→[a-zA-Z_0-9]+\]\[[a-zA-Z_0-9]+\]' | wc -l)
if [ "${_AMP_PATTERN_COUNT:-0}" -ge 3 ]; then
    echo "[inbox_write] REJECTED: amplification loop detected (${_AMP_PATTERN_COUNT} embedded headers in content, threshold=3) target=$TARGET from=$FROM" >&2
    exit 1
fi

# Cross-PC bridge: if target agent is on a different PC, also INSERT to Supabase
_cross_pc_bridge() {
    local target="$1"
    local content="$2"
    local msg_type="$3"
    local from="$4"

    # Check if cross-PC delivery is needed via settings.yaml
    # settings_local.yaml overrides pc_mapping (SecondPC uses different is_local)
    # Returns: "local_pc_id|target_pc_id" or empty if no bridge needed
    local bridge_info local_pc target_pc
    bridge_info=$("$SCRIPT_DIR/.venv/bin/python3" -c "
import yaml, sys, os
try:
    local_path = '$SCRIPT_DIR/config/settings_local.yaml'
    main_path = '$SCRIPT_DIR/config/settings.yaml'
    if os.path.exists(local_path):
        with open(local_path) as f:
            local_cfg = yaml.safe_load(f) or {}
        pc_map = local_cfg.get('pc_mapping', {})
    else:
        pc_map = {}
    if not pc_map:
        with open(main_path) as f:
            cfg = yaml.safe_load(f) or {}
        pc_map = cfg.get('pc_mapping', {})
    local_id = ''
    for pc_name, pc_cfg in pc_map.items():
        if pc_cfg.get('is_local'):
            local_id = pc_cfg.get('pc_id', pc_name)
    for pc_name, pc_cfg in pc_map.items():
        if pc_cfg.get('is_local'):
            continue
        agents = pc_cfg.get('agents', [])
        if '$target' in agents and pc_cfg.get('supabase_bridge'):
            print(f'{local_id}|{pc_cfg.get(\"pc_id\", pc_name)}')
            sys.exit(0)
    print('')
except Exception:
    print('')
" 2>/dev/null)

    if [ -z "$bridge_info" ]; then
        return 0  # Local agent, no bridge needed
    fi

    local_pc="${bridge_info%%|*}"
    target_pc="${bridge_info##*|}"

    # Load Supabase env
    local sb_url sb_key
    if [ -f "$HOME/.hakudokai/env" ]; then
        sb_url=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
        sb_key=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
    fi
    sb_url="${SUPABASE_URL:-$sb_url}"
    sb_key="${SUPABASE_SERVICE_ROLE_KEY:-$sb_key}"

    if [ -z "$sb_url" ] || [ -z "$sb_key" ]; then
        echo "[inbox_write] WARN: cross-PC bridge skipped (no Supabase env)" >&2
        return 0
    fi

    # Truncate content for Supabase (max 2000 chars)
    local truncated="${content:0:2000}"

    # JSON encode via python3 (heredoc + argv) — bash 文字列補間では改行/特殊文字が
    # JSON に直接埋め込まれて Supabase が「0x0a must be escaped」で reject していた。
    local payload
    payload=$(python3 - "$truncated" "${local_pc:-main_pc}" "$target_pc" "$target" "$from" "$msg_type" <<'PYEOF'
import json, sys
content_truncated, local_pc, target_pc, target_agent, from_agent, msg_type = sys.argv[1:7]
print(json.dumps({
    "message_type": "status_update",
    "from_pc": local_pc,
    "to_pc": target_pc,
    "topic": f"cross_pc_inbox_{target_agent}",
    "content": f"[{from_agent}→{target_agent}][{msg_type}] {content_truncated}",
    "requires_response": False,
    "priority": "normal",
    "clinic_id": "hakudoukai_main",
    "bypass_5round_limit": False,
    "is_meta_only": False
}, ensure_ascii=False))
PYEOF
)

    # INSERT to Supabase for cross-PC delivery
    curl -sS -X POST \
        "${sb_url}/rest/v1/pc_handshake" \
        -H "Authorization: Bearer ${sb_key}" \
        -H "apikey: ${sb_key}" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=minimal" \
        --data-binary "$payload" \
        2>/dev/null \
        && echo "[inbox_write] cross-PC bridge: ${target} → ${target_pc} via Supabase" >&2 \
        || echo "[inbox_write] WARN: cross-PC bridge INSERT failed for ${target}" >&2
}

# Trigger cross-PC bridge (non-blocking, runs in background)
# 緊急停止 2026-05-07 18:23: 連続 INSERT loop 発生中、source 不明
# ~/.openclaw/disable_cross_pc_bridge flag 存在時は cross_pc_bridge を起動しない
if [ ! -f "$HOME/.openclaw/disable_cross_pc_bridge" ]; then
    _cross_pc_bridge "$TARGET" "$CONTENT" "$TYPE" "$FROM" &
fi

# Initialize inbox if not exists
if [ ! -f "$INBOX" ]; then
    mkdir -p "$(dirname "$INBOX")"
    echo "messages: []" > "$INBOX"
fi

# Generate unique message ID (timestamp + 4 random bytes).
# Use `od` instead of `xxd` because `od` is available on both GNU/Linux and macOS runners by default.
MSG_ID="msg_$(date +%Y%m%d_%H%M%S)_$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
TIMESTAMP=$(date "+%Y-%m-%dT%H:%M:%S")

# Cross-platform lock: flock (Linux) or mkdir (macOS fallback)
LOCK_DIR="${LOCKFILE}.d"

_acquire_lock() {
    if command -v flock &>/dev/null; then
        exec 200>"$LOCKFILE"
        flock -w 5 200 || return 1
    else
        local i=0
        while ! mkdir "$LOCK_DIR" 2>/dev/null; do
            sleep 0.1
            i=$((i + 1))
            [ $i -ge 50 ] && return 1  # 5s timeout
        done
    fi
    return 0
}

_release_lock() {
    if command -v flock &>/dev/null; then
        exec 200>&-
    else
        rmdir "$LOCK_DIR" 2>/dev/null
    fi
}

# Atomic write with lock (3 retries)
attempt=0
max_attempts=3

while [ $attempt -lt $max_attempts ]; do
    if _acquire_lock; then
        INBOX_CONTENT="$CONTENT" "$SCRIPT_DIR/.venv/bin/python3" -c "
import yaml, sys, os

try:
    # Load existing inbox
    with open('$INBOX') as f:
        data = yaml.safe_load(f)

    # Initialize if needed
    if not data:
        data = {}
    if not data.get('messages'):
        data['messages'] = []

    # Add new message (content via env var to avoid quote injection)
    new_msg = {
        'id': '$MSG_ID',
        'from': '$FROM',
        'timestamp': '$TIMESTAMP',
        'type': '$TYPE',
        'content': os.environ.get('INBOX_CONTENT', ''),
        'read': False
    }
    data['messages'].append(new_msg)

    # Overflow protection: keep max 50 messages
    if len(data['messages']) > 50:
        msgs = data['messages']
        unread = [m for m in msgs if not m.get('read', False)]
        read = [m for m in msgs if m.get('read', False)]
        # Keep all unread + newest 30 read messages
        data['messages'] = unread + read[-30:]

    # Atomic write: tmp file + rename (prevents partial reads)
    # CRITICAL: dereference symlinks BEFORE atomic replace.
    # 2026-05-08 incident: queue/inbox/ split-brain. When INBOX was a symlink
    # (e.g. karo.yaml -> hideyoshi.yaml), os.replace replaced the SYMLINK ITSELF
    # with the tmp file, severing the alias and causing dual orphan files.
    # Fix: resolve to canonical path so writes always land on the real file
    # while symlink aliases remain intact.
    import tempfile, os
    inbox_canonical = os.path.realpath('$INBOX')
    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(inbox_canonical), suffix='.tmp')
    try:
        with os.fdopen(tmp_fd, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        os.replace(tmp_path, inbox_canonical)
    except:
        os.unlink(tmp_path)
        raise

except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
"
        STATUS=$?
        _release_lock
        [ $STATUS -eq 0 ] && exit 0
        attempt=$((attempt + 1))
        [ $attempt -lt $max_attempts ] && sleep 1
    else
        # Lock timeout
        attempt=$((attempt + 1))
        if [ $attempt -lt $max_attempts ]; then
            echo "[inbox_write] Lock timeout for $INBOX (attempt $attempt/$max_attempts), retrying..." >&2
            sleep 1
        else
            echo "[inbox_write] Failed to acquire lock after $max_attempts attempts for $INBOX" >&2
            exit 1
        fi
    fi
done
