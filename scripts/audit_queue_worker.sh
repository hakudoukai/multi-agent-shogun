#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# audit_queue_worker.sh — async audit worker daemon (= Phase C)
#
# Phase C 実装 (= 黒田 arch-01 是正後の async path):
#   pc_handshake table を queue として利用、shogun_kind='audit_request' を polling
#   pending row を claim → codex/gemini exec → *_audit_results INSERT → pc_handshake resolved
#
# Phase 5 immutable 制約は *_audit_results にのみ適用、pc_handshake は mutable ゆえ async OK。
#
# 使用想定:
#   nohup bash scripts/audit_queue_worker.sh main_pc \
#     >> logs/audit_queue_worker_main.log 2>&1 &
#   (= MainPC daemon、kuroda/takenaka 担当)
#
#   SecondPC でも同様に起動 (= naomasa/acha 担当):
#     scripts/audit_queue_worker.sh second_pc
#
# Usage:
#   bash scripts/audit_queue_worker.sh <my_pc>           # 永続 daemon (= 30s 周期)
#   bash scripts/audit_queue_worker.sh <my_pc> --once    # 1 回のみ
#   bash scripts/audit_queue_worker.sh <my_pc> --dry-run # claim/exec せず list のみ
#
# my_pc: main_pc | second_pc
# ════════════════════════════════════════════════════════════════
set -o pipefail   # set -u 外し (= Claude Code shell snapshot 競合回避)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck source=/dev/null
source "$REPO_ROOT/lib/audit_via_supabase.sh"

MY_PC="${1:-}"
case "$MY_PC" in
    main_pc|second_pc) ;;
    *) echo "Usage: $0 <main_pc|second_pc> [--once|--dry-run]"; exit 2 ;;
esac

ONCE="no"
DRY_RUN="no"
for arg in "$@"; do
    [ "$arg" = "--once" ] && ONCE="yes"
    [ "$arg" = "--dry-run" ] && DRY_RUN="yes"
done

POLL_INTERVAL=30  # seconds

_audit_load_supabase_env || { echo "ERR: SUPABASE env 不在"; exit 2; }

mkdir -p logs

worker_log() {
    echo "[$(date -Iseconds)] $*"
}

# pending audit_request 取得 (= shogun_kind=audit_request、resolved_at IS NULL、to_pc=$MY_PC)
fetch_pending() {
    MY_PC="$MY_PC" python3 <<'PY'
import os, json, urllib.request, urllib.parse, sys
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
# jsonb filter (= context_data->>'shogun_kind'='audit_request') を SQL level で適用
# (= 旧 client side filter は order=created_at.asc + limit=5 で古い question rows に埋もれて 0 件問題)
qs = urllib.parse.urlencode({
    'select': 'id,topic,content,context_data,priority,created_at',
    # 陛下御差配 2026-05-10: status_update 単一化 (= DD-107 制約 + 残 question audit_request 0 件確認済)
    'message_type': 'eq.status_update',
    'to_pc': f'eq.{os.environ["MY_PC"]}',
    'resolved_at': 'is.null',
    'context_data->>shogun_kind': 'eq.audit_request',
    'order': 'created_at.asc',
    'limit': '5',
})
req = urllib.request.Request(f"{url}/rest/v1/pc_handshake?{qs}",
    headers={'apikey': key, 'Authorization': f'Bearer {key}'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        rows = json.loads(r.read())
        print(json.dumps(rows))
except Exception as e:
    print(f'ERR: {e}', file=sys.stderr)
    print('[]')
PY
}

# claim → exec → audit_results INSERT → pc_handshake resolved
process_one() {
    local row_json="$1"
    local queue_id gunshi prompt_content topic

    queue_id=$(echo "$row_json" | python3 -c "import json, sys; print(json.load(sys.stdin)['id'])")
    gunshi=$(echo "$row_json" | python3 -c "import json, sys; print(json.load(sys.stdin)['context_data']['gunshi'])")
    prompt_content=$(echo "$row_json" | python3 -c "import json, sys; print(json.load(sys.stdin)['content'])")
    topic=$(echo "$row_json" | python3 -c "import json, sys; print(json.load(sys.stdin)['topic'])")

    worker_log "claim queue_id=$queue_id gunshi=$gunshi"

    if [ "$DRY_RUN" = "yes" ]; then
        worker_log "  [dry-run] skip claim/exec"
        return 0
    fi

    # acknowledge (= claim、UPDATE pc_handshake)
    QUEUE_ID="$queue_id" MY_PC="$MY_PC" python3 <<'PY'
import os, json, urllib.request
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
import datetime
# acknowledged_by check constraint: main_pc/second_pc/system/auto_ack 等
payload = {
    'acknowledged_at': datetime.datetime.utcnow().isoformat() + 'Z',
    'acknowledged_by': os.environ['MY_PC'],   # = main_pc | second_pc (= constraint 適合)
}
req = urllib.request.Request(
    f"{url}/rest/v1/pc_handshake?id=eq.{os.environ['QUEUE_ID']}",
    method='PATCH',
    headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
    data=json.dumps(payload).encode()
)
try:
    urllib.request.urlopen(req, timeout=10)
except Exception as e:
    # 既 ack 済等の 400 は無視 (= 旧 worker による ack を尊重、続行)
    print(f'  [warn] ack PATCH skip: {e}')
PY

    # 実行 — audit_via_supabase.sh の audit_run_local 機構を流用
    local prompt_file
    prompt_file=$(mktemp)
    echo "$prompt_content" > "$prompt_file"

    local scope="async:${topic:0:80}"
    audit_run_local "$gunshi" "$prompt_file" "$scope"
    local exit_code=$?
    rm -f "$prompt_file"

    # 直近 INSERT した audit_id 取得 (= 関連付けは created_at で近似)
    local audit_table
    case "$gunshi" in
        kuroda|naomasa) audit_table='codex_audit_results' ;;
        takenaka|acha)  audit_table='gemini_audit_results' ;;
    esac
    local audit_id
    audit_id=$(AT="$audit_table" python3 <<'PY'
import os, json, urllib.request, urllib.parse, sys
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
qs = urllib.parse.urlencode({'select':'id','order':'created_at.desc','limit':'1'})
req = urllib.request.Request(f"{url}/rest/v1/{os.environ['AT']}?{qs}",
    headers={'apikey':key,'Authorization':f'Bearer {key}'})
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read())
    print(data[0]['id'] if data else '')
PY
)

    # resolve (= UPDATE pc_handshake、context_data に audit_result_id 追加)
    QUEUE_ID="$queue_id" AUDIT_ID="$audit_id" EXIT_CODE="$exit_code" python3 <<'PY'
import os, json, urllib.request
import datetime
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
exit_code = int(os.environ['EXIT_CODE'])
# resolution_type check constraint: agreed/deferred/escalated/withdrawn/split のみ
# completed → agreed (= 合意完遂)、failed → withdrawn (= 取下げ相当)
payload = {
    'resolved_at': datetime.datetime.utcnow().isoformat() + 'Z',
    'resolution_type': 'agreed' if exit_code == 0 else 'withdrawn',
    'context_data': {'shogun_kind': 'audit_request', 'audit_result_id': os.environ['AUDIT_ID']},
}
req = urllib.request.Request(
    f"{url}/rest/v1/pc_handshake?id=eq.{os.environ['QUEUE_ID']}",
    method='PATCH',
    headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
    data=json.dumps(payload).encode()
)
try:
    urllib.request.urlopen(req, timeout=10)
except Exception as e:
    print(f'  [err] resolve PATCH failed: {e}', file=__import__('sys').stderr)
PY

    worker_log "resolved queue_id=$queue_id audit_id=$audit_id exit=$exit_code"
}

# main loop
worker_log "audit_queue_worker started: my_pc=$MY_PC poll=${POLL_INTERVAL}s once=$ONCE dry_run=$DRY_RUN"

while true; do
    pending=$(fetch_pending)
    count=$(echo "$pending" | python3 -c "import json, sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)

    if [ "$count" -gt 0 ]; then
        worker_log "pending audit requests: $count"
        echo "$pending" | python3 -c "
import json, sys
for r in json.load(sys.stdin):
    print(json.dumps(r))
" | while read -r row; do
            process_one "$row"
        done
    fi

    [ "$ONCE" = "yes" ] && break
    sleep $POLL_INTERVAL
done
