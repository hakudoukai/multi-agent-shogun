#!/usr/bin/env bash
# audit_codex.sh — 家康がCodex(デコポン)に6軸監査を依頼する標準スクリプト
#
# Usage:
#   bash scripts/audit_codex.sh <task_id> <cycle> <base_commit> <head_commit> [<repo_path>]
#
# Output:
#   - JSON 結果を /tmp/codex_audit_<task_id>_cycle<cycle>.json に保存
#   - 標準出力に verdict (pass/fail) を返す
#   - 終了コード: 0=PASS, 1=FAIL, 2=invocation error, 3=usage limit
#
# 監査フレームワーク準拠: docs/audit-framework.md §4

set -uo pipefail

TASK_ID="${1:-}"
CYCLE="${2:-}"
BASE_COMMIT="${3:-}"
HEAD_COMMIT="${4:-}"
REPO_PATH="${5:-/mnt/c/Users/User/Documents/DentalBI}"

if [ -z "$TASK_ID" ] || [ -z "$CYCLE" ] || [ -z "$BASE_COMMIT" ] || [ -z "$HEAD_COMMIT" ]; then
  echo "Usage: $0 <task_id> <cycle> <base_commit> <head_commit> [<repo_path>]" >&2
  echo "Example: $0 subtask_t13_qr_003b2 1 abc123 def456 /mnt/c/Projects/hakudokai-dev" >&2
  exit 2
fi

OUTPUT="/tmp/codex_audit_${TASK_ID}_cycle${CYCLE}.json"
LOG="/tmp/codex_audit_${TASK_ID}_cycle${CYCLE}.log"
EXCLUDE_PATTERN=':(exclude)**/node_modules/** :(exclude)**/.venv/** :(exclude)**/dist/** :(exclude)**/build/** :(exclude)**/*.lock :(exclude)**/__pycache__/** :(exclude)**/.git/**'

# Get diff (with exclude patterns)
DIFF=$(cd "$REPO_PATH" && git diff "${BASE_COMMIT}..${HEAD_COMMIT}" -- . $EXCLUDE_PATTERN 2>/dev/null)

if [ -z "$DIFF" ]; then
  echo "{\"task_id\":\"$TASK_ID\",\"cycle\":$CYCLE,\"overall_verdict\":\"fail\",\"summary\":\"empty diff between $BASE_COMMIT..$HEAD_COMMIT\"}" > "$OUTPUT"
  echo "fail"
  exit 1
fi

CHANGED_PATHS=$(cd "$REPO_PATH" && git diff --name-only "${BASE_COMMIT}..${HEAD_COMMIT}" -- . $EXCLUDE_PATTERN 2>/dev/null | tr '\n' ' ')
DIFF_LINES_ADDED=$(echo "$DIFF" | grep -c '^+[^+]' || echo 0)
DIFF_LINES_REMOVED=$(echo "$DIFF" | grep -c '^-[^-]' || echo 0)

# Build prompt (heredoc to temp file to avoid shell escaping)
PROMPT_FILE=$(mktemp)
cat > "$PROMPT_FILE" <<EOF
あなたはコードレビュー専門家。以下の git diff を6軸監査してください。

タスクID: ${TASK_ID}
サイクル: ${CYCLE}
変更パス: ${CHANGED_PATHS}
追加行数: ${DIFF_LINES_ADDED}
削除行数: ${DIFF_LINES_REMOVED}

=== 監査軸（6軸固定。順守せよ） ===
Axis 1 (security): セキュリティ脆弱性 — OWASP Top 10、認証・認可、SQLi/XSS/CSRF、機密漏洩、暗号化、CORS、入力検証
Axis 2 (bugs): バグ・エラーハンドリング — 例外処理、null/undefined、境界値、リソースリーク、レースコンディション
Axis 3 (types): 型整合性・契約 — TypeScript/Python型、関数シグネチャ、暗黙キャスト、any濫用、Optional処理
Axis 4 (tests): テスト網羅性 — 新規テストの妥当性、SKIP=0、境界・異常系カバレッジ、モック適切性、回帰テスト
Axis 5 (duplication): 既存コードとの重複 — Anti-Duplication Rule準拠、再利用妥当性、共通化候補、命名衝突
Axis 6 (git): Git Persistence・コミット粒度 — atomic commits、commitメッセージ品質、不要ファイル混入なし

=== 重要 ===
- このdiffに限定して監査せよ。リポジトリ全体を走査するな（フル走査は禁止）
- 各axisのfindingsは Severity (critical|high|medium|low) を必ず付与
- Critical/High が1件でもあれば該当axisは fail、6軸全てが pass の時のみ overall_verdict=pass

=== 出力形式（JSON のみ。前後説明文不要） ===
{
  "task_id": "${TASK_ID}",
  "cycle": ${CYCLE},
  "axes": {
    "axis1_security": {"verdict": "pass|fail", "findings": [{"severity": "...", "id": "S1", "description": "...", "file": "...", "line": 0, "fix_suggestion": "..."}]},
    "axis2_bugs": {"verdict": "pass|fail", "findings": []},
    "axis3_types": {"verdict": "pass|fail", "findings": []},
    "axis4_tests": {"verdict": "pass|fail", "findings": []},
    "axis5_duplication": {"verdict": "pass|fail", "findings": []},
    "axis6_git": {"verdict": "pass|fail", "findings": []}
  },
  "overall_verdict": "pass|fail",
  "summary": "総括 (1-3文)"
}

=== 差分 ===
${DIFF}
EOF

# Invoke Codex with retry logic
RETRY=0
MAX_RETRY=3
while [ $RETRY -lt $MAX_RETRY ]; do
  CODEX_RAW=$(npx @openai/codex exec --json --output-last-message "$OUTPUT" < "$PROMPT_FILE" 2>"$LOG")
  CODEX_EXIT=$?

  # Detect usage limit
  if grep -qE "usage limit|rate.?limit|429|quota" "$LOG" 2>/dev/null; then
    rm -f "$PROMPT_FILE"
    echo "{\"task_id\":\"$TASK_ID\",\"cycle\":$CYCLE,\"overall_verdict\":\"fallback_required\",\"fallback_reason\":\"codex usage limit\",\"summary\":\"see $LOG\"}" > "$OUTPUT"
    echo "fallback_required"
    exit 3
  fi

  if [ $CODEX_EXIT -eq 0 ] && [ -s "$OUTPUT" ]; then
    break
  fi

  RETRY=$((RETRY + 1))
  sleep 5
done

rm -f "$PROMPT_FILE"

if [ ! -s "$OUTPUT" ]; then
  echo "{\"task_id\":\"$TASK_ID\",\"cycle\":$CYCLE,\"overall_verdict\":\"invocation_error\",\"summary\":\"codex did not produce output after $MAX_RETRY retries\"}" > "$OUTPUT"
  echo "invocation_error"
  exit 2
fi

# Extract verdict
VERDICT=$(python3 -c "
import json
try:
  d = json.load(open('$OUTPUT'))
  print(d.get('overall_verdict', 'invocation_error'))
except Exception as e:
  print('invocation_error')
")

echo "$VERDICT"

case "$VERDICT" in
  pass) exit 0 ;;
  fail) exit 1 ;;
  *) exit 2 ;;
esac
