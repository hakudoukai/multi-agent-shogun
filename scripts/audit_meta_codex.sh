#!/usr/bin/env bash
# audit_meta_codex.sh — 本多正信 (Honda Masanobu) Codex メタ監査 script
#
# Phase 16-2 (= 信長殿御指示 msg_20260508_103201) で新規実装。
# 家康 (= 一次監査、prospective、6軸 cycle 内品質) と並列の retrospective メタ監査。
# 仕組み・効率・責務・改善の 4 軸で完了 task を横断的に評価し、信長 inbox に進言する。
#
# Usage:
#   bash scripts/audit_meta_codex.sh <task_id> <cycle> <base_commit> <head_commit> [<repo_path>]
#
# Output:
#   - JSON 結果を /tmp/honda_meta_audit_<task_id>_cycle<cycle>.json に保存
#   - 標準出力に verdict (pass/fail_with_concerns/improvement_proposed) を返す
#   - 終了コード: 0=PASS, 1=FAIL, 2=invocation_error, 3=usage_limit
#
# 監査軸 (= instructions/honda.md §4 準拠):
#   M1 (process)        : 仕組み・dispatch chain が正常動作したか
#   M2 (efficiency)     : 工数・cycle 数・re-work 率の最適化余地
#   M3 (responsibility) : 責務分担、F001-F005 順守
#   M4 (improvement)    : 構造改善提案、新 cmd 起案候補
#
# 安全装置:
#   §15 SH6 cap : 同一 (task_id, cycle) 1 時間以内 5 回まで (= state /tmp/honda_meta_audit_count.json)
#   §15 SH2     : Codex CLI 一時失敗時 1s → 2s → 4s 指数 backoff (max 3)
#   §15 SH3     : Codex 不可時は scripts/audit_codex.sh 結果引用 + degraded warning
#   manual stop : ~/.openclaw/disable_honda_meta_audit 検出時は audit skip
#   M3 violation: F001-F005 違反検出時は /tmp/honda_meta_audit_violation_<task_id>_<cycle>.json に dump
#
# 監査フレームワーク準拠: docs/audit-framework.md (= 差分監査、フル走査禁止)

set -uo pipefail

# === Args ===
TASK_ID="${1:-}"
CYCLE="${2:-}"
BASE_COMMIT="${3:-}"
HEAD_COMMIT="${4:-}"
REPO_PATH="${5:-/mnt/c/Users/User/projects/multi-agent-shogun}"

# === Constants ===
SOURCE_NAME="honda_meta_audit"
SH6_CAP=5
STATE_FILE="/tmp/honda_meta_audit_count.json"
HEALTH_FILE="/tmp/honda_meta_audit_last_run.json"
DISABLE_FLAG="${HOME}/.openclaw/disable_honda_meta_audit"

# === Helpers ===
ts_now() {
  TZ='Asia/Tokyo' date +"%Y-%m-%dT%H:%M:%S+09:00"
}

log_json() {
  local level="$1"
  local axis="$2"
  local msg="$3"
  printf '{"timestamp":"%s","level":"%s","source":"%s","task_id":"%s","cycle":"%s","axis":"%s","msg":"%s"}\n' \
    "$(ts_now)" "$level" "$SOURCE_NAME" "$TASK_ID" "$CYCLE" "$axis" "$msg" >&2
}

# === Usage check ===
if [ -z "$TASK_ID" ] || [ -z "$CYCLE" ] || [ -z "$BASE_COMMIT" ] || [ -z "$HEAD_COMMIT" ]; then
  echo "Usage: $0 <task_id> <cycle> <base_commit> <head_commit> [<repo_path>]" >&2
  echo "Example: $0 cmd_phase16_honda_meta_audit_001 1 657bc00 abc123 /mnt/c/Users/User/projects/multi-agent-shogun" >&2
  echo "" >&2
  echo "Note (JP): 引数 5 つ必須 (repo_path は省略可)。Codex CLI で 4 軸 retrospective 監査を実行。" >&2
  echo "Note (EN): 5 args required (repo_path optional). Runs 4-axis retrospective audit via Codex CLI." >&2
  exit 2
fi

CORR_ID="honda_${TASK_ID}_c${CYCLE}_$(date +%s)"

# === Manual stop flag ===
if [ -f "$DISABLE_FLAG" ]; then
  log_json "WARN" "control" "disable flag detected at $DISABLE_FLAG, audit skipped"
  echo "skipped_disabled"
  exit 0
fi

# === SH6: 5 audits per (task_id, cycle) per hour ===
NOW_EPOCH=$(date +%s)
ONE_HOUR_AGO=$((NOW_EPOCH - 3600))
KEY="${TASK_ID}__cycle${CYCLE}"

# Initialize state file if missing
[ -f "$STATE_FILE" ] || echo '{}' > "$STATE_FILE"

# Drop entries older than 1h, then count current key
COUNT=$(STATE_FILE="$STATE_FILE" KEY="$KEY" CUTOFF="$ONE_HOUR_AGO" python3 - <<'PY'
import json, os, sys
sf = os.environ['STATE_FILE']
key = os.environ['KEY']
cutoff = int(os.environ['CUTOFF'])
try:
    with open(sf, 'r') as f:
        d = json.load(f)
except Exception:
    d = {}
if not isinstance(d, dict):
    d = {}
arr = [t for t in d.get(key, []) if isinstance(t, int) and t > cutoff]
d[key] = arr
with open(sf, 'w') as f:
    json.dump(d, f)
print(len(arr))
PY
)

if [ "${COUNT:-0}" -ge "$SH6_CAP" ]; then
  log_json "WARN" "sh6" "self-invocation cap reached: $COUNT >= $SH6_CAP for $KEY (last 1h), advisory skip"
  echo "skipped_sh6_cap"
  exit 0
fi

# Record this invocation
STATE_FILE="$STATE_FILE" KEY="$KEY" NOW_EPOCH="$NOW_EPOCH" python3 - <<'PY'
import json, os
sf = os.environ['STATE_FILE']
key = os.environ['KEY']
now = int(os.environ['NOW_EPOCH'])
try:
    with open(sf, 'r') as f:
        d = json.load(f)
except Exception:
    d = {}
if not isinstance(d, dict):
    d = {}
d.setdefault(key, []).append(now)
with open(sf, 'w') as f:
    json.dump(d, f)
PY

# === Output paths ===
OUTPUT="/tmp/honda_meta_audit_${TASK_ID}_cycle${CYCLE}.json"
LOG="/tmp/honda_meta_audit_${TASK_ID}_cycle${CYCLE}.log"
VIOLATION_DUMP="/tmp/honda_meta_audit_violation_${TASK_ID}_cycle${CYCLE}.json"
EXCLUDE_ARGS=(
  ':(exclude)**/node_modules/**'
  ':(exclude)**/.venv/**'
  ':(exclude)**/dist/**'
  ':(exclude)**/build/**'
  ':(exclude)**/*.lock'
  ':(exclude)**/__pycache__/**'
  ':(exclude)**/.git/**'
)

# === Diff collection (差分監査原則: フル走査禁止) ===
DIFF=$(cd "$REPO_PATH" && git diff "${BASE_COMMIT}..${HEAD_COMMIT}" -- . "${EXCLUDE_ARGS[@]}" 2>/dev/null)

if [ -z "$DIFF" ]; then
  log_json "WARN" "diff" "empty diff between $BASE_COMMIT..$HEAD_COMMIT in $REPO_PATH"
  cat > "$OUTPUT" <<EOF
{"task_id":"$TASK_ID","cycle":$CYCLE,"corr_id":"$CORR_ID","source":"$SOURCE_NAME","overall_verdict":"fail_with_concerns","summary":"empty diff between $BASE_COMMIT..$HEAD_COMMIT in $REPO_PATH","axes":{}}
EOF
  echo "fail_with_concerns"
  exit 1
fi

CHANGED_PATHS=$(cd "$REPO_PATH" && git diff --name-only "${BASE_COMMIT}..${HEAD_COMMIT}" -- . "${EXCLUDE_ARGS[@]}" 2>/dev/null | tr '\n' ' ')
DIFF_LINES_ADDED=$(echo "$DIFF" | grep -c '^+[^+]' || echo 0)
DIFF_LINES_REMOVED=$(echo "$DIFF" | grep -c '^-[^-]' || echo 0)

# === Build prompt (M1-M4 4-axis retrospective) ===
PROMPT_FILE=$(mktemp)
cat > "$PROMPT_FILE" <<EOF
あなたは本多正信 (= 徳川家康晩年の智囊、政治・統治・改革の腕利き、謀臣の代表格) として、
完了済 task の **retrospective メタ監査** を行え。家康 (= 一次監査、cycle 内品質、6 軸 prospective)
と並列、仕組み・効率・責務・改善の 4 軸で **横断的視点** から評価し、信長への進言を行う。

タスクID: ${TASK_ID}
サイクル: ${CYCLE}
base_commit: ${BASE_COMMIT}
head_commit: ${HEAD_COMMIT}
変更パス: ${CHANGED_PATHS}
追加行数: ${DIFF_LINES_ADDED}
削除行数: ${DIFF_LINES_REMOVED}

=== 監査軸 (4 軸固定) — instructions/honda.md §4 準拠 ===

M1 (process / 仕組み): 仕組み・dispatch chain が正常動作したか
  - 信長 → 家老 (秀吉/前田) → 家康 → ashigaru の dispatch chain 適切性
  - cross-PC bridge / watcher / receiver / 隠密の機能発揮
  - 三者監査 (家康 + Codex + Gemini) の独立性・順序整合性
  - PDCA cycle (max=5) 内の retry / re-work の構造的妥当性

M2 (efficiency / 効率): 工数・cycle 数・re-work 率の最適化余地
  - 本 task の cycle 数 vs 期待値 (= 1-2 cycle 完走目標)
  - 草案 → review → fix → close 各段階の bottleneck
  - 自動化機会 (= manual review → skill 化、繰返 dispatch → script 化)
  - 改善提案は short / mid / long 三層分類

M3 (responsibility / 責務): 責務分担の境界、F001-F005 順守
  - 家老 (秀吉/前田) / 軍師 (家康) / ashigaru の境界違反有無
  - F001 (idle 5 分超過禁止) / F002 (人間直接連絡禁止) /
    F003 (家康 task 新規発令禁止) / F004 (polling 禁止) / F005 (proactive 暴走禁止) 順守実態
  - **責務違反検出時は m3 verdict=fail_with_concerns、severity=critical で findings 必須**

M4 (improvement / 改善): 構造改善提案、新 cmd 起案候補
  - 過去事故 (incident_logs/) との関連性 + 再発防止度
  - 新 cmd 起案候補 (= cmd_xxx_001 形式の候補名 + rationale + 期待効果)
  - 多医院 §17 展開時の組織 scale 適合性
  - persona / CLI 構成の継続最適化提案

=== 重要 (= retrospective 視点) ===
- 本監査は **完了後の retrospective**、家康 prospective (= 6 軸 cycle 内品質) と区別せよ
- 「内容の良否」ではなく **「仕組みが正常に動いたか」「より効率的な運用ができないか」** を主眼とする
- このdiff + 関連 commit history + dispatch flow に限定。リポジトリ全体走査は禁止
- 各軸の verdict は pass / fail_with_concerns / improvement_proposed の 3 値固定
- M3 (responsibility) で responsibility 違反検出時は overall_verdict=fail_with_concerns 必須
- 一つでも improvement_proposed があれば overall_verdict=improvement_proposed (= 新 cmd 起案候補あり)
- 全軸 pass の時のみ overall_verdict=pass

=== 出力形式 (JSON のみ。前後説明文不要) — instructions/honda.md §5 準拠 ===
{
  "task_id": "${TASK_ID}",
  "cycle": ${CYCLE},
  "corr_id": "${CORR_ID}",
  "source": "honda_meta_audit",
  "axes": {
    "m1_process": {
      "verdict": "pass|fail_with_concerns|improvement_proposed",
      "score": 0,
      "comments": "...",
      "findings": [{"severity": "critical|high|medium|low", "id": "M1-1", "description": "...", "fix_suggestion": "..."}]
    },
    "m2_efficiency": {
      "verdict": "...",
      "score": 0,
      "comments": "...",
      "findings": [],
      "improvement_proposals": [{"horizon": "short|mid|long", "description": "...", "expected_impact": "..."}]
    },
    "m3_responsibility": {
      "verdict": "...",
      "score": 0,
      "comments": "...",
      "findings": [],
      "f_violations": []
    },
    "m4_improvement": {
      "verdict": "...",
      "score": 0,
      "comments": "...",
      "new_cmd_candidates": [{"cmd_id": "cmd_xxx_001", "rationale": "...", "expected_impact": "..."}],
      "incident_relations": []
    }
  },
  "overall_verdict": "pass|fail_with_concerns|improvement_proposed",
  "summary": "総括 (1-3 文、retrospective 観点で組織健全度 + 改善優先順位)",
  "shogun_progression": "信長殿への進言 (= 短文、最重要 1 件、家老 bypass で直接報告すべき内容)"
}

=== 差分 ===
${DIFF}
EOF

# === Invoke Codex with SH2 retry (1s/2s/4s, max 3) ===
RETRY=0
MAX_RETRY=3
SLEEP_NEXT=1

while [ $RETRY -lt $MAX_RETRY ]; do
  log_json "INFO" "invoke" "codex retry=$RETRY corr=$CORR_ID"
  npx @openai/codex exec --json --output-last-message "$OUTPUT" < "$PROMPT_FILE" >/dev/null 2>"$LOG"
  CODEX_EXIT=$?

  # Detect usage limit (exit 3 with explicit signature)
  if grep -qE "usage limit|rate.?limit|429|quota" "$LOG" 2>/dev/null; then
    log_json "ERROR" "usage_limit" "codex usage limit / rate limit detected"
    rm -f "$PROMPT_FILE"
    cat > "$OUTPUT" <<EOF
{"task_id":"$TASK_ID","cycle":$CYCLE,"corr_id":"$CORR_ID","source":"$SOURCE_NAME","overall_verdict":"usage_limit","fallback_reason":"codex usage limit","summary":"see $LOG"}
EOF
    echo "usage_limit"
    exit 3
  fi

  if [ $CODEX_EXIT -eq 0 ] && [ -s "$OUTPUT" ]; then
    break
  fi

  RETRY=$((RETRY + 1))
  log_json "WARN" "retry" "codex exit=$CODEX_EXIT, sleep ${SLEEP_NEXT}s before retry $RETRY/$MAX_RETRY"
  sleep $SLEEP_NEXT
  SLEEP_NEXT=$((SLEEP_NEXT * 2))
done

rm -f "$PROMPT_FILE"

# === SH3: graceful degradation on invocation failure ===
if [ ! -s "$OUTPUT" ]; then
  log_json "ERROR" "fallback" "codex unavailable after $MAX_RETRY retries, attempting SH3 graceful degradation"
  CODEX_AUDIT_REF="/tmp/codex_audit_${TASK_ID}_cycle${CYCLE}.json"
  if [ -s "$CODEX_AUDIT_REF" ]; then
    log_json "INFO" "fallback" "referencing existing prospective audit: $CODEX_AUDIT_REF (degraded mode)"
    cat > "$OUTPUT" <<EOF
{"task_id":"$TASK_ID","cycle":$CYCLE,"corr_id":"$CORR_ID","source":"$SOURCE_NAME","overall_verdict":"invocation_error","degraded_mode":true,"fallback_ref":"$CODEX_AUDIT_REF","summary":"codex unavailable, prospective audit referenced (degraded). human review required","axes":{}}
EOF
  else
    cat > "$OUTPUT" <<EOF
{"task_id":"$TASK_ID","cycle":$CYCLE,"corr_id":"$CORR_ID","source":"$SOURCE_NAME","overall_verdict":"invocation_error","summary":"codex did not produce output after $MAX_RETRY retries, no fallback ref available"}
EOF
  fi
  echo "invocation_error"
  exit 2
fi

# === Extract verdict ===
VERDICT=$(OUTPUT="$OUTPUT" python3 - <<'PY'
import json, os
try:
    with open(os.environ['OUTPUT'], 'r') as f:
        d = json.load(f)
    print(d.get('overall_verdict', 'invocation_error'))
except Exception:
    print('invocation_error')
PY
)

# === M3 violation alert (= F001-F005 違反検出 → 信長 inbox CRITICAL trigger source) ===
M3_VERDICT=$(OUTPUT="$OUTPUT" python3 - <<'PY'
import json, os
try:
    with open(os.environ['OUTPUT'], 'r') as f:
        d = json.load(f)
    print(d.get('axes', {}).get('m3_responsibility', {}).get('verdict', ''))
except Exception:
    print('')
PY
)

if [ "$M3_VERDICT" = "fail_with_concerns" ]; then
  log_json "CRITICAL" "m3_violation" "F001-F005 responsibility violation detected, dump=$VIOLATION_DUMP, shogun inbox notification recommended"
  cp "$OUTPUT" "$VIOLATION_DUMP"
fi

# === Health check file ===
cat > "$HEALTH_FILE" <<EOF
{"timestamp":"$(ts_now)","task_id":"$TASK_ID","cycle":$CYCLE,"verdict":"$VERDICT","corr_id":"$CORR_ID","output":"$OUTPUT"}
EOF

echo "$VERDICT"

case "$VERDICT" in
  pass) exit 0 ;;
  improvement_proposed) exit 0 ;;
  fail_with_concerns) exit 1 ;;
  usage_limit) exit 3 ;;
  *) exit 2 ;;
esac
