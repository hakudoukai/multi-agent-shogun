#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# pdca_orchestrator.sh — PDCA 強制執行 main orchestrator
#
# 動作:
#   各 target で 5 iter loop (鉄則 3)
#   各 iter: health check → submit audit → wait + force → verdict 判定 → redo or done
#   green 達成 or iter=5 reached で exit
#
# 状態永続化: queue/pdca_state.yaml
# 起動: nohup setsid で daemon 化推奨
# Usage: pdca_orchestrator.sh <target> [<target2> ...]
# target: ashigaru1-6 | cmd_NNN | <gunshi>:<prompt_file>
# ════════════════════════════════════════════════════════════════
set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

# shellcheck source=/dev/null
source "$REPO_ROOT/lib/audit_via_supabase.sh"
_audit_load_supabase_env || { echo "ERR: SUPABASE env"; exit 2; }

TARGETS=("$@")
[ ${#TARGETS[@]} -eq 0 ] && { echo "Usage: $0 <target> [...]"; exit 1; }

LOG_DIR="logs"; mkdir -p "$LOG_DIR"
STATE_FILE="queue/pdca_state.yaml"
[ -f "$STATE_FILE" ] || echo 'pdca_targets: {}' > "$STATE_FILE"

MAX_ITER=5
WAIT_BETWEEN_ITER=300   # 5 min (= ashigaru redo cycle 想定)
AUDIT_TIMEOUT=1800      # 30 min (= 1 audit max)

log() { echo "[$(date -Iseconds)] [pdca] $*"; }

# target → audit prompt 生成
build_prompt_for_target() {
    local tgt="$1"
    local out_file="$2"
    case "$tgt" in
        ashigaru[1-6])
            cat > "$out_file" <<EOF
軍師として ${tgt} の Phase δ deliverable を 9 観点監査せよ。
report: queue/reports/${tgt}_report.yaml
実体検証必須 (= report 上の path に実 file あるか、tsc/構文 PASS 根拠、commit_hash、Supabase 同期)。
200字以内 YAML: verdict / findings (3件以上 if fail)
EOF
            # 直政 pdca_4 是正: SecondPC ashigaru も含む routing (= MainPC ashigaru1-6 は kuroda、
            # SecondPC ashigaru*_sp は naomasa)
            case "$tgt" in
                *_sp) echo "naomasa" ;;
                *)    echo "kuroda" ;;
            esac
            ;;
        cmd_*)
            cat > "$out_file" <<EOF
軍師・竹中半兵衛として ${tgt} plan (= queue/shogun_to_karo.yaml) を 9 観点監査せよ。
domain: plan / strategy / acceptance_criteria
200字以内 YAML: verdict / findings (3件以上 if fail) / persona_signature: 竹中半兵衛
EOF
            echo "takenaka"
            ;;
        *)
            echo "ERR: 未知 target $tgt" >&2
            return 1
            ;;
    esac
}

# state 更新 (= flock 化、直政 pdca_3 是正)
state_set() {
    local tgt="$1" key="$2" val="$3"
    local lock_file="queue/pdca_state.yaml.lock"
    (
        flock -w 10 200 || { echo "ERR: state_set flock timeout"; return 1; }
        TGT="$tgt" KEY="$key" VAL="$val" python3 <<'PY'
import os, yaml
path = 'queue/pdca_state.yaml'
if not os.path.exists(path):
    with open(path, 'w') as f:
        f.write('pdca_targets: {}\n')
with open(path) as f:
    d = yaml.safe_load(f) or {'pdca_targets': {}}
t = d['pdca_targets'].setdefault(os.environ['TGT'], {})
v = os.environ['VAL']
try: v = int(v)
except ValueError: pass
t[os.environ['KEY']] = v
with open(path, 'w') as f:
    yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False)
PY
    ) 200>"$lock_file"
}

state_get() {
    local tgt="$1" key="$2"
    TGT="$tgt" KEY="$key" python3 <<'PY'
import os, yaml, sys
path = 'queue/pdca_state.yaml'
with open(path) as f:
    d = yaml.safe_load(f) or {'pdca_targets': {}}
t = d['pdca_targets'].get(os.environ['TGT'], {})
print(t.get(os.environ['KEY'], ''))
PY
}

# 1 target を 5 iter で処理
process_target() {
    local tgt="$1"
    local prompt_file="/tmp/pdca_${tgt}.txt"
    local gunshi
    gunshi=$(build_prompt_for_target "$tgt" "$prompt_file") || return 1

    state_set "$tgt" "started_at" "$(date -Iseconds)"

    local iter
    iter=$(state_get "$tgt" "iter")
    [ -z "$iter" ] && iter=0

    while [ "$iter" -lt "$MAX_ITER" ]; do
        iter=$((iter+1))
        log "$tgt iter=$iter/$MAX_ITER"
        state_set "$tgt" "iter" "$iter"

        # Step 1: health check (= 鉄則 1)
        bash "$REPO_ROOT/skills/shogun-pdca-enforcer/scripts/agent_health_check.sh" 2>&1 | sed "s/^/  [$tgt] /"

        # Step 2: submit audit
        local qid
        qid=$(audit_submit_async "$gunshi" "$prompt_file" "pdca:${tgt}:iter${iter}" 2>&1 | tail -1)
        log "$tgt submitted queue_id=$qid"
        state_set "$tgt" "last_queue_id" "$qid"

        # Step 3: wait for resolve (max 30 min)
        local elapsed=0
        local audit_id=""
        while [ "$elapsed" -lt "$AUDIT_TIMEOUT" ]; do
            audit_id=$(QID="$qid" python3 <<'PY'
import os, json, urllib.request, urllib.parse
url = os.environ['SUPABASE_URL']; key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
qs = urllib.parse.urlencode({'select':'context_data,resolved_at','id':f'eq.{os.environ["QID"]}'})
req = urllib.request.Request(f"{url}/rest/v1/pc_handshake?{qs}",
    headers={'apikey':key,'Authorization':f'Bearer {key}'})
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
if data and data[0].get('resolved_at'):
    print((data[0].get('context_data') or {}).get('audit_result_id', ''))
PY
)
            [ -n "$audit_id" ] && break
            sleep 60
            elapsed=$((elapsed+60))
        done

        if [ -z "$audit_id" ]; then
            log "$tgt audit stuck (>30min)、karo に nudge + force codex exec"
            bash "$REPO_ROOT/scripts/inbox_write.sh" karo \
                "🚨 ${tgt} pdca iter=$iter audit stuck、即時処理せよ (= queue_id=$qid)" \
                "redo_command" "shogun" 2>&1 | tail -2
            continue   # 次 iter で再 submit
        fi

        # Step 4: verdict 取得
        local signal
        signal=$(RID="$audit_id" python3 <<'PY'
import os, json, urllib.request, urllib.parse
url = os.environ['SUPABASE_URL']; key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
for tbl in ['codex_audit_results','gemini_audit_results']:
    qs = urllib.parse.urlencode({'select':'overall_signal','id':f'eq.{os.environ["RID"]}'})
    req = urllib.request.Request(f"{url}/rest/v1/{tbl}?{qs}",
        headers={'apikey':key,'Authorization':f'Bearer {key}'})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        if data: print(data[0]['overall_signal']); break
    except Exception: pass
PY
)
        log "$tgt audit_id=$audit_id signal=$signal"
        state_set "$tgt" "last_audit_id" "$audit_id"
        state_set "$tgt" "last_verdict" "$signal"
        state_set "$tgt" "last_attempt_at" "$(date -Iseconds)"

        if [ "$signal" = "green" ] || [ "$signal" = "yellow" ]; then
            log "$tgt ✅ DONE (signal=$signal、iter=$iter)"
            state_set "$tgt" "status" "done"
            return 0
        fi

        # red → karo に redo + 待機
        log "$tgt 🔴 RED、karo に redo 命令 + ${WAIT_BETWEEN_ITER}s 待機 (= ashigaru cycle)"
        bash "$REPO_ROOT/scripts/inbox_write.sh" karo \
            "🔄 ${tgt} pdca iter=$iter red、即時 redo 命令 (= 信長強制執行)" \
            "redo_command" "shogun" 2>&1 | tail -2
        sleep "$WAIT_BETWEEN_ITER"
    done

    log "$tgt MAX_ITER ($MAX_ITER) 到達、人間介入要"
    state_set "$tgt" "status" "max_iter_reached"
    return 2
}

log "pdca_orchestrator 起動: targets=${TARGETS[*]} max_iter=$MAX_ITER"

# 各 target 並列処理 (= bash subshell で & 起動、xargs より)
for tgt in "${TARGETS[@]}"; do
    process_target "$tgt" &
done

wait
log "pdca_orchestrator 全 target 完遂 or max_iter"
