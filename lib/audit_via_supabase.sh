#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# audit_via_supabase.sh — Audit を Supabase 経由で実行 (= context 切離 + 永続化)
#
# 陛下御差配 (2026-05-10): 監査・計画書・指示文 等を Supabase 統一経由で扱う。
# context 消費抑止 + 資料保存 + 大量投稿 bug 防止 + cross-PC 透明性。
#
# 提供関数 (= 黒田 arch-01 是正後):
#   audit_run_local <gunshi> <prompt_file> [scope]
#     → codex/gemini exec を先行 → 完遂後に 1 回だけ INSERT (= Phase 5 immutable 遵守)
#     → 拙者 (信長) context への流入は wrapper 出力のみ (= prompt/log は DB+log file)
#
#   audit_get_summary <audit_id> [table]
#     → 結果 summary (overall_signal + issues_count) のみ取得 (= context 圧迫回避)
#
# 廃止 (= Phase 5 immutable と矛盾):
#   - audit_request (= INSERT pending → UPDATE 設計、UPDATE 不可で矛盾)
#   - audit_wait (= async poller 想定、現 schema では未実装)
#   将来 async 必要時は別 queue table (= pc_handshake 等) で実装予定
#
# 依存:
#   - SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY env
#   - codex (Codex CLI) / gemini (Gemini CLI) 何れか
#   - python3
# ════════════════════════════════════════════════════════════════
set -o pipefail   # set -u 外し (= Claude Code shell snapshot の ZSH_VERSION 参照と競合)

AUDIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_PROJECT_ROOT="$(cd "${AUDIT_DIR}/.." && pwd)"

# ─────────────────────────────────────────────────────────────
# Supabase env 取得 (= bridge process or 既存 env)
# ─────────────────────────────────────────────────────────────
_audit_load_supabase_env() {
    if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
        return 0
    fi
    local bridge_pid
    bridge_pid=$(pgrep -f hakudokai_realtime_bridge | head -1)
    if [ -n "$bridge_pid" ] && [ -r "/proc/$bridge_pid/environ" ]; then
        eval "$(cat /proc/$bridge_pid/environ 2>/dev/null | tr '\0' '\n' | grep -E '^SUPABASE_(URL|SERVICE_ROLE_KEY)=' | sed 's/^/export /')"
        return 0
    fi
    return 1
}

# ─────────────────────────────────────────────────────────────
# audit_request — DEPRECATED (= 黒田 arch-01 指摘で廃止)
# Phase 5 immutable 制約により INSERT pending → UPDATE 不可、本関数は使用禁。
# 将来 async 必要時は pc_handshake / 専用 queue table で再実装。
# ─────────────────────────────────────────────────────────────
audit_request() {
    echo "DEPRECATED: audit_request は Phase 5 immutable 制約と矛盾、廃止 (= 黒田 arch-01)。" >&2
    echo "  → audit_run_local を使え (= sync 1 回 INSERT、Phase 5 遵守)。" >&2
    echo "  → async 必要時は別途 queue table 設計待ち。" >&2
    return 99
}

# ─────────────────────────────────────────────────────────────
# audit_run_local <gunshi> <prompt_file> [scope]
#   INSERT pending → 同 process で codex/gemini exec → UPDATE completed
#   poller 不要、互換 path (= 軽量 / single-shot)
# ─────────────────────────────────────────────────────────────
audit_run_local() {
    # ────────────────────────────────────────────────────────
    # codex_audit_results / gemini_audit_results は Phase 5 immutable
    # (= INSERT only、UPDATE/DELETE 不可、DD-128 v2.1c §3.2 準拠)
    # ゆえに「INSERT pending → UPDATE completed」設計禁、INSERT は完遂後に 1 回のみ。
    # ────────────────────────────────────────────────────────
    local gunshi="$1"
    local prompt_file="$2"
    local scope="${3:-}"

    _audit_load_supabase_env || { echo "ERR: SUPABASE env 不在" >&2; return 2; }

    # gunshi → table mapping
    local table tool ran_pc
    case "$gunshi" in
        kuroda)   table='codex_audit_results';  tool='codex';  ran_pc='main_pc'   ;;
        takenaka) table='gemini_audit_results'; tool='gemini'; ran_pc='main_pc'   ;;
        naomasa)  table='codex_audit_results';  tool='codex';  ran_pc='second_pc' ;;
        acha)     table='gemini_audit_results'; tool='gemini'; ran_pc='second_pc' ;;
        *) echo "ERR: 未知 gunshi=$gunshi" >&2; return 1 ;;
    esac

    [ -z "$scope" ] && scope=$(head -1 "$prompt_file" | cut -c1-200)

    # 実行 (= INSERT 前に codex/gemini を先に動かす)
    local log_file
    log_file="logs/audit_$(date +%Y%m%d_%H%M%S)_${gunshi}.log"
    mkdir -p logs
    local started_at
    started_at=$(date +%s)

    local prompt_content
    prompt_content=$(cat "$prompt_file")

    echo "[audit_run_local] running $tool for $gunshi (timeout 300s, log=$log_file)"
    if [ "$tool" = "codex" ]; then
        timeout 300 codex exec "$prompt_content" > "$log_file" 2>&1
    else
        cd "$AUDIT_PROJECT_ROOT"
        NODE_OPTIONS=--dns-result-order=ipv4first timeout 300 \
            gemini -m gemini-2.5-pro -p "$prompt_content" > "$log_file" 2>&1
    fi
    local exit_code=$?
    local ended_at duration_sec
    ended_at=$(date +%s)
    duration_sec=$((ended_at - started_at))

    # 結果を 1 回 INSERT (= Phase 5 immutable 遵守)
    local result_text
    result_text=$(cat "$log_file" | tail -200)
    AUDIT_TABLE="$table" RESULT_TEXT="$result_text" DURATION="$duration_sec" \
    EXIT_CODE="$exit_code" LOG_PATH="$log_file" SCOPE="$scope" RAN_PC="$ran_pc" \
    GUNSHI="$gunshi" TOOL="$tool" python3 <<'PY'
import os, json, urllib.request, re, sys
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
table = os.environ['AUDIT_TABLE']
exit_code = int(os.environ['EXIT_CODE'])
text = os.environ['RESULT_TEXT']

# verdict 推定
verdict = 'green'
m = re.search(r'verdict:\s*(\w+)', text, re.IGNORECASE)
if m:
    v = m.group(1).lower()
    if v == 'fail': verdict = 'red'
    elif 'concern' in v: verdict = 'yellow'
if exit_code != 0: verdict = 'red'

# triaged_issues 抽出 (= "- id: kN" pattern)
issues = []
for m in re.finditer(r'(?m)^\s*-\s*id:\s*(\S+)\s*\n\s*.*?severity:\s*(\w+).*?title:\s*([^\n]+)', text, re.DOTALL):
    issues.append({'id': m.group(1).strip(), 'severity': m.group(2).strip(), 'title': m.group(3).strip()[:100]})

cnt = {'a': 0, 'b': 0, 'c': 0}
for i in issues:
    sv = i.get('severity', 'c').lower()
    if sv in ('a', 'high'): cnt['a'] += 1
    elif sv in ('b', 'medium'): cnt['b'] += 1
    else: cnt['c'] += 1

payload = {
    'audit_scope': os.environ['SCOPE'],
    'audit_summary_md': text[:8000],
    'overall_signal': verdict,
    'triaged_issues': issues,
    'issues_count_a': cnt['a'],
    'issues_count_b': cnt['b'],
    'issues_count_c': cnt['c'],
    'ran_on_pc': os.environ['RAN_PC'],
    'audit_duration_sec': int(os.environ['DURATION']),
    'audit_file_path': os.environ['LOG_PATH'],
    'task_title': f"audit:{os.environ['GUNSHI']}",
}
if os.environ['TOOL'] == 'codex':
    payload['codex_version'] = 'codex (gpt-5.5)'
else:
    payload['gemini_version'] = 'gemini-2.5-pro'

req = urllib.request.Request(
    f"{url}/rest/v1/{table}",
    method='POST',
    headers={'apikey': key, 'Authorization': f'Bearer {key}',
             'Content-Type': 'application/json',
             'Prefer': 'return=representation'},
    data=json.dumps(payload).encode()
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
        if isinstance(data, list) and data:
            aid = data[0]['id']
            print(f'[audit_run_local] INSERTED audit_id={aid} signal={verdict} issues={len(issues)} duration={os.environ["DURATION"]}s')
        else:
            print('ERR: empty INSERT response', file=sys.stderr)
            sys.exit(3)
except Exception as e:
    print(f'ERR INSERT: {e}', file=sys.stderr)
    sys.exit(4)
PY
    return $exit_code
}

# ─────────────────────────────────────────────────────────────
# audit_get_summary <audit_id> [table]
# ─────────────────────────────────────────────────────────────
audit_get_summary() {
    local audit_id="$1"
    local table="${2:-codex_audit_results}"  # default codex
    _audit_load_supabase_env || return 2

    AUDIT_ID="$audit_id" TABLE="$table" python3 <<'PY'
import os, json, urllib.request, urllib.parse
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
qs = urllib.parse.urlencode({
    'select': 'id,overall_signal,issues_count_a,issues_count_b,issues_count_c,audit_duration_sec,ran_on_pc',
    'id': f'eq.{os.environ["AUDIT_ID"]}',
})
req = urllib.request.Request(
    f"{url}/rest/v1/{os.environ['TABLE']}?{qs}",
    headers={'apikey': key, 'Authorization': f'Bearer {key}'}
)
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read())
    if data:
        x = data[0]
        print(f"audit_id={x['id']} signal={x['overall_signal']} issues_a/b/c={x['issues_count_a']}/{x['issues_count_b']}/{x['issues_count_c']} duration={x['audit_duration_sec']}s pc={x['ran_on_pc']}")
PY
}

# ════════════════════════════════════════════════════════════════
# Async path (= Phase C、pc_handshake table 利用)
# pc_handshake は mutable (acknowledged_at/resolved_at update 可)
# 提出 → worker が poll → codex/gemini exec → audit_results INSERT → pc_handshake resolved
# ════════════════════════════════════════════════════════════════

# audit_submit_async <gunshi> <prompt_file> [scope]
#   pc_handshake に audit request を INSERT、queue_id を返却
audit_submit_async() {
    local gunshi="$1"
    local prompt_file="$2"
    local scope="${3:-}"

    [ -z "$gunshi" ] && { echo "ERR: gunshi 必須" >&2; return 1; }
    [ -f "$prompt_file" ] || { echo "ERR: prompt_file 不在" >&2; return 1; }
    _audit_load_supabase_env || return 2

    local target_pc
    case "$gunshi" in
        kuroda|takenaka) target_pc='main_pc' ;;
        naomasa|acha)    target_pc='second_pc' ;;
        *) echo "ERR: 未知 gunshi=$gunshi" >&2; return 1 ;;
    esac

    [ -z "$scope" ] && scope=$(head -1 "$prompt_file" | cut -c1-150)
    local prompt_content
    prompt_content=$(cat "$prompt_file")

    PROMPT_CONTENT="$prompt_content" SCOPE="$scope" GUNSHI="$gunshi" TARGET_PC="$target_pc" python3 <<'PY'
import os, json, urllib.request, sys
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
payload = {
    'message_type': 'question',
    'from_pc': 'main_pc',
    'to_pc': os.environ['TARGET_PC'],
    'topic': f"audit_request:{os.environ['GUNSHI']}:{os.environ['SCOPE'][:80]}",
    'content': os.environ['PROMPT_CONTENT'],
    'context_data': {'shogun_kind': 'audit_request', 'gunshi': os.environ['GUNSHI']},
    'requires_response': True,
    'priority': 'normal',
    'clinic_id': 'hakudoukai_main',
}
req = urllib.request.Request(
    f"{url}/rest/v1/pc_handshake",
    method='POST',
    headers={'apikey': key, 'Authorization': f'Bearer {key}',
             'Content-Type': 'application/json',
             'Prefer': 'return=representation'},
    data=json.dumps(payload).encode()
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
        if isinstance(data, list) and data:
            print(data[0]['id'])
except Exception as e:
    print(f'ERR: {e}', file=sys.stderr)
    sys.exit(3)
PY
}

# audit_get_async <queue_id>
#   pc_handshake row + 関連 *_audit_results の状態を統合表示
audit_get_async() {
    local queue_id="$1"
    [ -z "$queue_id" ] && { echo "ERR: queue_id 必須" >&2; return 1; }
    _audit_load_supabase_env || return 2

    QUEUE_ID="$queue_id" python3 <<'PY'
import os, json, urllib.request, urllib.parse, sys
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
qs = urllib.parse.urlencode({
    'select': 'id,topic,context_data,acknowledged_at,resolved_at,resolution_type,created_at',
    'id': f'eq.{os.environ["QUEUE_ID"]}',
})
req = urllib.request.Request(f"{url}/rest/v1/pc_handshake?{qs}",
    headers={'apikey': key, 'Authorization': f'Bearer {key}'})
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read())
    if not data:
        print(f'queue_id {os.environ["QUEUE_ID"]} not found')
        sys.exit(1)
    x = data[0]
    status = 'pending'
    if x.get('resolved_at'):
        status = 'completed' if x.get('resolution_type') != 'failed' else 'failed'
    elif x.get('acknowledged_at'):
        status = 'processing'
    audit_id = (x.get('context_data') or {}).get('audit_result_id', '')
    resolved = x.get('resolved_at') or '-'
    resolved_short = resolved[:19] if resolved != '-' else '-'
    print(f"queue_id={x['id']} status={status} created={x['created_at'][:19]} resolved={resolved_short} audit_id={audit_id}")
PY
}

# ─────────────────────────────────────────────────────────────
# Self-test (= direct execution 時のみ)
# ─────────────────────────────────────────────────────────────
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    case "${1:-help}" in
        run)            audit_run_local "${@:2}" ;;
        summary)        audit_get_summary "${@:2}" ;;
        submit-async)   audit_submit_async "${@:2}" ;;
        get-async)      audit_get_async "${@:2}" ;;
        request)        audit_request "${@:2}" ;;  # DEPRECATED で error 返す
        *)
            cat <<HELP
Usage:
  $0 run          <gunshi> <prompt_file> [scope]   — sync 即実行 (= Phase 5 INSERT only)
  $0 summary      <audit_id> [table]                — 結果 summary 取得 (= context 圧迫回避)
  $0 submit-async <gunshi> <prompt_file> [scope]    — async submit、queue_id 返却
  $0 get-async    <queue_id>                        — async 結果取得 (pending|completed|failed)

gunshi: kuroda | takenaka | naomasa | acha
queue: pc_handshake table (= acknowledged_at/resolved_at で状態管理)

廃止: audit_request (= 黒田 arch-01、Phase 5 immutable と矛盾)
HELP
            ;;
    esac
fi
