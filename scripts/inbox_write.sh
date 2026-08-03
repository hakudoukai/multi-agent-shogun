#!/usr/bin/env bash
# inbox_write.sh — メールボックスへのメッセージ書き込み（排他ロック付き）
# Usage:
#   通常 (argv 経由): bash scripts/inbox_write.sh <target_agent> <content> <type> <from>
#   ★stdin 経由 (cycle2 S2 cure)★:
#       INBOX_WRITE_CONTENT_STDIN=1 bash scripts/inbox_write.sh <target> __VIA_STDIN__ <type> <from> < <(echo "$CONTENT")
#       env INBOX_WRITE_CONTENT_STDIN=1 が立っている時は $2 を無視して stdin から content を読む。
#       process inspection (ps/argv leak) で機密内容が見えるのを防ぐ用途 (fukuincho_report_poke_bundle.py で利用)。
# Example: bash scripts/inbox_write.sh karo "足軽5号、任務完了" report_received ashigaru5

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$1"
CONTENT="$2"
TYPE="$3"
FROM="$4"

# ★cycle2 S2 cure (med)★: stdin 経由 content 受領 (argv 露出 cure)
# 既存 caller (positional argv) は env 未設定で従来動作、backward compatible
if [ "${INBOX_WRITE_CONTENT_STDIN:-}" = "1" ]; then
    CONTENT="$(cat)"
fi

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
    local_agents = []
    for pc_name, pc_cfg in pc_map.items():
        if pc_cfg.get('is_local'):
            local_id = pc_cfg.get('pc_id', pc_name)
            local_agents = pc_cfg.get('agents', []) or []
    # local-first (R0 seq96053/96064): target が local PC の agents に在れば bridge せず local 書込。
    # 3PC 均等編成で同一 agent_id (例 ashigaru1-7) が複数 PC に併存しても、各 PC 内で local 解決される。
    # remote-only agent (local に無い) の bridge 意味論は不変。
    if '$target' in local_agents:
        print('')
        sys.exit(0)
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
    "message_type": msg_type,
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

    # INSERT to Supabase for cross-PC delivery. curl itself exits 0 for HTTP
    # 4xx/5xx unless --fail is used, so require both curl success and an
    # explicit 2xx response. Discard the response body to avoid logging it.
    local http_status curl_rc
    http_status=$(curl --fail-with-body -sS -o /dev/null -w '%{http_code}' -X POST \
        --connect-timeout 10 --max-time 15 \
        "${sb_url}/rest/v1/pc_handshake" \
        -H "Authorization: Bearer ${sb_key}" \
        -H "apikey: ${sb_key}" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=minimal" \
        --data-binary "$payload" \
        2>/dev/null)
    curl_rc=$?
    if [ "$curl_rc" -eq 0 ] && [[ "$http_status" =~ ^2[0-9][0-9]$ ]]; then
        echo "[inbox_write] cross-PC bridge: ${target} → ${target_pc} via Supabase" >&2
        return 70
    fi
    echo "[inbox_write] WARN: cross-PC bridge INSERT failed for ${target} (http_status=${http_status:-000}, curl_rc=$curl_rc)" >&2
    return 71
}

# Trigger cross-PC bridge. If a cross-PC insert succeeds, do not also write a
# local dead-letter inbox file. If insert fails, fail closed instead of silently
# creating an unread local queue that no remote recipient reads.
if [ ! -f "$HOME/.openclaw/disable_cross_pc_bridge" ]; then
    set +e
    _cross_pc_bridge "$TARGET" "$CONTENT" "$TYPE" "$FROM"
    _BRIDGE_RC=$?
    set -e
    if [ "$_BRIDGE_RC" -eq 70 ]; then
        exit 0
    fi
    if [ "$_BRIDGE_RC" -eq 71 ]; then
        exit 71
    fi
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
        INBOX_CONTENT="$CONTENT" INBOX_EXPIRES_AT="${INBOX_EXPIRES_AT:-}" INBOX_SUPERSEDES_ID="${INBOX_SUPERSEDES_ID:-}" "$SCRIPT_DIR/.venv/bin/python3" -c "
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
    # expires_at/supersedes: optional expiry/supersession schema fields, also
    # routed via env var (not shell interpolation) to avoid injection. Absent
    # by default (None) = fully backward compatible with existing readers,
    # which never assumed these keys were present.
    new_msg = {
        'id': '$MSG_ID',
        'from': '$FROM',
        'timestamp': '$TIMESTAMP',
        'type': '$TYPE',
        'content': os.environ.get('INBOX_CONTENT', ''),
        'read': False,
        'expires_at': os.environ.get('INBOX_EXPIRES_AT') or None,
        'supersedes': os.environ.get('INBOX_SUPERSEDES_ID') or None
    }
    data['messages'].append(new_msg)

    # Overflow rotation (2026-08-03 委員長hotfix 裁定seq137748/137769):
    # 旧仕様は50便超で既読便を黙って恒久破壊していた(同日17+19便消失の実害)。
    # 破壊→回転: 溢れた既読便はper-agent archiveへ全量退避し、発動をstderrへlogする。
    if len(data['messages']) > 50:
        msgs = data['messages']
        unread = [m for m in msgs if not m.get('read', False)]
        read = [m for m in msgs if m.get('read', False)]
        dropped = read[:-30]
        if dropped:
            _adir = os.path.join(os.path.dirname('$INBOX'), '_archive')
            os.makedirs(_adir, exist_ok=True)
            _abase = os.path.basename('$INBOX')
            if _abase.endswith('.yaml'):
                _abase = _abase[:-5]
            _apath = os.path.join(_adir, _abase + '_pruned.yaml')
            with open(_apath, 'a', encoding='utf-8') as _af:
                yaml.safe_dump({'pruned_at': '$TIMESTAMP', 'count': len(dropped), 'messages': dropped}, _af, allow_unicode=True, default_flow_style=False)
                _af.write('---\n')
            print('[inbox_write] CAP_ROTATED: ' + str(len(dropped)) + ' read messages moved to ' + _apath, file=sys.stderr)
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
