#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# audit_via_supabase.sh — Audit を Supabase 経由で実行 (= context 切離 + 永続化)
#
# 陛下御差配 (2026-05-10): 監査・計画書・指示文 等を Supabase 統一経由で扱う。
# context 消費抑止 + 資料保存 + 大量投稿 bug 防止 + cross-PC 透明性。
#
# 提供関数:
#   audit_request <gunshi> <prompt_file> [scope] [task_id]
#     → audit_id (UUID) を出力、prompt は Supabase に INSERT
#     → 軍師 pane の poller が pending row を処理
#
#   audit_wait <audit_id> [timeout=300]
#     → status=completed まで polling、result_yaml を出力
#
#   audit_get_summary <audit_id>
#     → 結果 summary (overall_signal + issues_count) のみ取得
#
#   audit_run_local <gunshi> <prompt_file> [scope]
#     → INSERT pending → 同 process で codex/gemini exec → UPDATE completed
#     → poller 不要、即時実行 (= 互換 path)
#
# 依存:
#   - SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY env
#   - codex (Codex CLI) / gemini (Gemini CLI) 何れか
#   - python3
# ════════════════════════════════════════════════════════════════
set -uo pipefail

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
# audit_request <gunshi> <prompt_file> [scope] [task_id]
#   gunshi: kuroda | takenaka | naomasa | acha
#   prompt_file: prompt 全文 file path
#   scope: audit_scope text (省略時 prompt 1 行目)
#   task_id: 任意の uuid (省略時 NULL)
#
# 出力: audit_id (UUID) を stdout
# ─────────────────────────────────────────────────────────────
audit_request() {
    local gunshi="$1"
    local prompt_file="$2"
    local scope="${3:-}"
    local task_id="${4:-}"

    [ -z "$gunshi" ] && { echo "ERR: gunshi 必須" >&2; return 1; }
    [ -f "$prompt_file" ] || { echo "ERR: prompt_file 不在: $prompt_file" >&2; return 1; }

    _audit_load_supabase_env || { echo "ERR: SUPABASE env 不在" >&2; return 2; }

    # gunshi → table mapping
    local table tool ran_pc
    case "$gunshi" in
        kuroda)   table='codex_audit_results';  tool='codex';  ran_pc='main_pc' ;;
        takenaka) table='gemini_audit_results'; tool='gemini'; ran_pc='main_pc' ;;
        naomasa)  table='codex_audit_results';  tool='codex';  ran_pc='second_pc' ;;
        acha)     table='gemini_audit_results'; tool='gemini'; ran_pc='second_pc' ;;
        *) echo "ERR: 未知 gunshi=$gunshi (valid: kuroda/takenaka/naomasa/acha)" >&2; return 1 ;;
    esac

    [ -z "$scope" ] && scope=$(head -1 "$prompt_file" | cut -c1-200)
    local prompt_content
    prompt_content=$(cat "$prompt_file")

    # INSERT pending row (audit_summary_md=prompt 全文、status は signal で表現:
    # 'pending' → audit 投函済、未実行 (= overall_signal 制約上 green/yellow/red のみ可ゆえ
    # 'pending' は別 col もしくは task_title で表現)
    # 既存 schema は status field 無し、audit_summary_md に prompt 入れて
    # overall_signal='yellow' (= pending 相当) で投函、worker が green/red に UPDATE
    PROMPT_CONTENT="$prompt_content" SCOPE="$scope" TABLE="$table" RAN_PC="$ran_pc" GUNSHI="$gunshi" TASK_ID="$task_id" python3 <<'PY'
import os, json, urllib.request, urllib.parse
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
table = os.environ['TABLE']

payload = {
    'audit_scope': os.environ['SCOPE'],
    'audit_summary_md': f"## PROMPT (= worker が処理する audit query)\n\n{os.environ['PROMPT_CONTENT']}",
    'overall_signal': 'yellow',  # pending 相当 (= 未実行/処理中、worker が完遂時 green/red に UPDATE)
    'triaged_issues': [],
    'ran_on_pc': os.environ['RAN_PC'],
    'task_title': f"audit_request:{os.environ['GUNSHI']}",
}
task_id = os.environ.get('TASK_ID', '')
if task_id: payload['task_id'] = task_id

req = urllib.request.Request(
    f"{url}/rest/v1/{table}",
    method='POST',
    headers={
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    },
    data=json.dumps(payload).encode()
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
        if isinstance(data, list) and data:
            print(data[0]['id'])
        else:
            print('ERR: empty response', file=__import__('sys').stderr)
            __import__('sys').exit(3)
except Exception as e:
    print(f'ERR: {e}', file=__import__('sys').stderr)
    __import__('sys').exit(4)
PY
}

# ─────────────────────────────────────────────────────────────
# audit_run_local <gunshi> <prompt_file> [scope]
#   INSERT pending → 同 process で codex/gemini exec → UPDATE completed
#   poller 不要、互換 path (= 軽量 / single-shot)
# ─────────────────────────────────────────────────────────────
audit_run_local() {
    local gunshi="$1"
    local prompt_file="$2"
    local scope="${3:-}"

    local audit_id
    audit_id=$(audit_request "$gunshi" "$prompt_file" "$scope") || return $?
    [ -z "$audit_id" ] && { echo "ERR: audit_id 取得失敗" >&2; return 5; }
    echo "[audit_run_local] audit_id=$audit_id"

    # 実行
    local table tool
    case "$gunshi" in
        kuroda|naomasa) table='codex_audit_results';  tool='codex'  ;;
        takenaka|acha)  table='gemini_audit_results'; tool='gemini' ;;
    esac

    local log_file="logs/audit_${audit_id}.log"
    mkdir -p logs
    local started_at
    started_at=$(date +%s)

    local prompt_content
    prompt_content=$(cat "$prompt_file")

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

    # 結果 UPDATE
    local result_text
    result_text=$(cat "$log_file" | tail -100)
    AUDIT_ID="$audit_id" TABLE="$table" RESULT_TEXT="$result_text" DURATION="$duration_sec" \
    EXIT_CODE="$exit_code" LOG_PATH="$log_file" python3 <<'PY'
import os, json, urllib.request
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
table = os.environ['TABLE']
audit_id = os.environ['AUDIT_ID']
exit_code = int(os.environ['EXIT_CODE'])

# verdict 推定 (= result_text 内に verdict: pass / fail / pass_with_concerns あれば抽出)
import re
text = os.environ['RESULT_TEXT']
verdict = 'green'  # default
m = re.search(r'verdict:\s*(\w+)', text, re.IGNORECASE)
if m:
    v = m.group(1).lower()
    if v == 'fail': verdict = 'red'
    elif 'concern' in v: verdict = 'yellow'
if exit_code != 0: verdict = 'red'

payload = {
    'overall_signal': verdict,
    'audit_summary_md': text[:8000],  # truncate to 8KB safe
    'audit_duration_sec': int(os.environ['DURATION']),
    'audit_file_path': os.environ['LOG_PATH'],
}
req = urllib.request.Request(
    f"{url}/rest/v1/{table}?id=eq.{audit_id}",
    method='PATCH',
    headers={
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    },
    data=json.dumps(payload).encode()
)
try:
    urllib.request.urlopen(req, timeout=15)
    print(f'[audit_run_local] UPDATED audit_id={audit_id} signal={verdict} duration={os.environ["DURATION"]}s')
except Exception as e:
    print(f'ERR UPDATE: {e}', file=__import__('sys').stderr)
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

# ─────────────────────────────────────────────────────────────
# Self-test (= direct execution 時のみ)
# ─────────────────────────────────────────────────────────────
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    case "${1:-help}" in
        request)  audit_request "${@:2}" ;;
        run)      audit_run_local "${@:2}" ;;
        summary)  audit_get_summary "${@:2}" ;;
        *)
            cat <<HELP
Usage:
  $0 request <gunshi> <prompt_file> [scope] [task_id]  — INSERT pending only
  $0 run     <gunshi> <prompt_file> [scope]            — INSERT + exec + UPDATE
  $0 summary <audit_id> [table]                         — fetch summary

gunshi: kuroda | takenaka | naomasa | acha
table:  codex_audit_results | gemini_audit_results
HELP
            ;;
    esac
fi
