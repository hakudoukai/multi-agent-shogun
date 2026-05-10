#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# redo_loop.sh — 自動 redo loop (= ashigaru deliverable green 達成まで)
#
# 陛下御差配 (2026-05-10): 「確認しないで完結するまで行って、止まらないで繰返」
# 動作:
#   1. ashigaru report mtime 監視 (= 30 min 周期)
#   2. mtime 更新検出 → submit-async で 自動 re-audit
#   3. audit 結果 fetch、green なら該当 ashigaru 完遂
#   4. red なら karo に再度 redo 命令 inbox_write
#   5. 両 ashigaru green まで loop、最大 N iteration
#
# Usage:
#   bash scripts/redo_loop.sh <ashigaru_id> [<ashigaru_id2> ...]
#   bash scripts/redo_loop.sh ashigaru4 ashigaru6
# ════════════════════════════════════════════════════════════════
set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck source=/dev/null
source "$REPO_ROOT/lib/audit_via_supabase.sh"
_audit_load_supabase_env || { echo "ERR: SUPABASE env 不在"; exit 2; }

TARGETS=("$@")
[ ${#TARGETS[@]} -eq 0 ] && { echo "Usage: $0 <ashigaru_id> ..."; exit 1; }

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
STATE_DIR="/tmp/redo_loop_state"
mkdir -p "$STATE_DIR"

POLL_INTERVAL=600  # 10 min (= mtime 検出 interval)
MAX_ITER=10        # 最大 10 回 loop (= 安全装置)

log() { echo "[$(date -Iseconds)] $*"; }

# 各 target の状態 init (= 初回 mtime 記録)
declare -A baseline_mtime
declare -A done_status
for tgt in "${TARGETS[@]}"; do
    f="queue/reports/${tgt}_report.yaml"
    if [ -f "$f" ]; then
        baseline_mtime[$tgt]=$(stat -c %Y "$f")
    else
        baseline_mtime[$tgt]=0
    fi
    done_status[$tgt]=0
done

log "redo_loop 起動: targets=${TARGETS[*]} interval=${POLL_INTERVAL}s max_iter=$MAX_ITER"
log "baseline mtime 記録: $(for k in "${!baseline_mtime[@]}"; do echo -n "$k=${baseline_mtime[$k]} "; done)"

iter=0
while [ $iter -lt $MAX_ITER ]; do
    iter=$((iter+1))
    log "loop iter=$iter"

    # 全 target green なら exit
    all_green=1
    for tgt in "${TARGETS[@]}"; do
        [ "${done_status[$tgt]}" = "0" ] && all_green=0
    done
    if [ "$all_green" = "1" ]; then
        log "ALL GREEN — loop 完遂 (iter=$iter)"
        break
    fi

    # 各 target の更新検出 → re-audit
    for tgt in "${TARGETS[@]}"; do
        [ "${done_status[$tgt]}" = "1" ] && continue
        f="queue/reports/${tgt}_report.yaml"
        [ -f "$f" ] || continue
        cur=$(stat -c %Y "$f")
        if [ "$cur" -gt "${baseline_mtime[$tgt]}" ]; then
            log "$tgt: report 更新検出 (mtime ${baseline_mtime[$tgt]} → $cur)、re-audit 投函"
            # prompt 用 file
            prompt_file="$STATE_DIR/${tgt}_redo_audit.txt"
            cat > "$prompt_file" <<EOF
軍師・黒田官兵衛として ${tgt} の redo cycle 後 deliverable を再監査せよ。

target: ${tgt} (= 前回 verdict=fail から redo)
report: queue/reports/${tgt}_report.yaml

確認観点:
- 実装 file が報告通り存在するか (= 実体検証)
- tsc/構文 check PASS evidence あるか
- commit_hash + log_path が全 deliverable に記録されているか
- Supabase 同期完遂か
- 前回指摘事項全て解消か

200 字以内 YAML: verdict / findings (3 件以上 if fail) / persona_signature: 黒田官兵衛
EOF
            qid=$(audit_submit_async kuroda "$prompt_file" "redo:$tgt" 2>&1 | tail -1)
            log "$tgt: queue_id=$qid"
            echo "$qid" > "$STATE_DIR/${tgt}_qid.txt"
            baseline_mtime[$tgt]=$cur
        fi
    done

    # 既 submit 済 audit の結果 check (= 軽微遅延 + 結果取得)
    for tgt in "${TARGETS[@]}"; do
        [ "${done_status[$tgt]}" = "1" ] && continue
        qid_file="$STATE_DIR/${tgt}_qid.txt"
        [ -f "$qid_file" ] || continue
        qid=$(cat "$qid_file")
        # pc_handshake から audit_result_id 取得
        result_id=$(QID="$qid" python3 <<'PY'
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
        if [ -n "$result_id" ]; then
            # codex_audit_results から signal 取得
            signal=$(RID="$result_id" python3 <<'PY'
import os, json, urllib.request, urllib.parse
url = os.environ['SUPABASE_URL']; key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
qs = urllib.parse.urlencode({'select':'overall_signal','id':f'eq.{os.environ["RID"]}'})
req = urllib.request.Request(f"{url}/rest/v1/codex_audit_results?{qs}",
    headers={'apikey':key,'Authorization':f'Bearer {key}'})
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
print(data[0]['overall_signal'] if data else '')
PY
)
            log "$tgt: audit signal=$signal"
            if [ "$signal" = "green" ]; then
                done_status[$tgt]=1
                log "$tgt: ✅ GREEN 達成"
            elif [ "$signal" = "red" ]; then
                # 再 redo 命令を karo へ
                log "$tgt: 🔴 RED 継続、karo に再 redo 命令"
                bash "$REPO_ROOT/scripts/inbox_write.sh" karo \
                    "🔄 ${tgt} 再 redo: 前回 redo cycle で再度 fail (audit_id=$result_id)。実体検証を厳格化、再々 redo 仕る。loop iter=$iter" \
                    "redo_command" "shogun" 2>&1
                rm -f "$qid_file"  # 次 mtime 更新で再 submit
            fi
        fi
    done

    log "iter=$iter done、${POLL_INTERVAL}s 待機"
    sleep $POLL_INTERVAL
done

if [ $iter -ge $MAX_ITER ]; then
    log "MAX_ITER ($MAX_ITER) 到達、loop 中断 (= 手動介入要)"
fi

log "redo_loop 終了"
