#!/usr/bin/env bash
# audit_gemini.sh — 家康がGemini(ジェミちゃん)に仕様準拠+法令監査を依頼する標準スクリプト
#
# Usage:
#   bash scripts/audit_gemini.sh <task_id> <cycle> <base_commit> <head_commit> [<repo_path>] [<spec_file>]
#
# Output:
#   - JSON 結果を /tmp/gemini_audit_<task_id>_cycle<cycle>.json に保存
#   - 標準出力に verdict (pass/fail) を返す
#   - 終了コード: 0=PASS, 1=FAIL, 2=invocation error
#
# 監査フレームワーク準拠: docs/audit-framework.md §5

set -uo pipefail

TASK_ID="${1:-}"
CYCLE="${2:-}"
BASE_COMMIT="${3:-}"
HEAD_COMMIT="${4:-}"
REPO_PATH="${5:-/mnt/c/Users/User/Documents/DentalBI}"
SPEC_FILE="${6:-/mnt/c/Users/User/projects/multi-agent-shogun/context/teriha-zero-wait.md}"

if [ -z "$TASK_ID" ] || [ -z "$CYCLE" ] || [ -z "$BASE_COMMIT" ] || [ -z "$HEAD_COMMIT" ]; then
  echo "Usage: $0 <task_id> <cycle> <base_commit> <head_commit> [<repo_path>] [<spec_file>]" >&2
  exit 2
fi

OUTPUT="/tmp/gemini_audit_${TASK_ID}_cycle${CYCLE}.json"
LOG="/tmp/gemini_audit_${TASK_ID}_cycle${CYCLE}.log"
EXCLUDE_PATTERN=':(exclude)**/node_modules/** :(exclude)**/.venv/** :(exclude)**/dist/** :(exclude)**/build/** :(exclude)**/*.lock :(exclude)**/__pycache__/** :(exclude)**/.git/**'

# --unified=2: context lines を 3→2 に削減して diff サイズを ~20% 縮小
# (Windows node.exe の 32K cmdline + WSL/Windows interop 制約対策)
DIFF=$(cd "$REPO_PATH" && git diff --unified=2 "${BASE_COMMIT}..${HEAD_COMMIT}" -- . $EXCLUDE_PATTERN 2>/dev/null)

if [ -z "$DIFF" ]; then
  echo "{\"task_id\":\"$TASK_ID\",\"cycle\":$CYCLE,\"overall_verdict\":\"fail\",\"summary\":\"empty diff\"}" > "$OUTPUT"
  echo "fail"
  exit 1
fi

CHANGED_PATHS=$(cd "$REPO_PATH" && git diff --name-only "${BASE_COMMIT}..${HEAD_COMMIT}" -- . $EXCLUDE_PATTERN 2>/dev/null | tr '\n' ' ')

# Detect PII/legal-relevant changes (broader detection for safety)
PII_KEYWORDS="patient|kanja|name|kana|dob|birth|insurance|hokensho|consent|doui|guardian|hogosha|medical|shinryo|chart|karte"
HAS_PII="false"
if echo "$DIFF" | grep -qiE "$PII_KEYWORDS"; then
  HAS_PII="true"
fi

SPEC_CONTENT=""
if [ -f "$SPEC_FILE" ]; then
  # head -300 → head -50 (16KB → ~3KB に削減、ARG_MAX 対策)
  # 仕様の核心 (会計待ちゼロ作戦の North Star + 主要 Step) は冒頭にある前提
  SPEC_CONTENT=$(head -50 "$SPEC_FILE")
fi

# PROMPT_FILE を Windows fs (/mnt/c/temp) に配置して WSL/Windows interop 問題を回避
# /mnt/c/temp が存在しない場合は /tmp に fallback
PROMPT_TMP_DIR="/mnt/c/temp"
if [ ! -d "$PROMPT_TMP_DIR" ]; then
  mkdir -p "$PROMPT_TMP_DIR" 2>/dev/null || PROMPT_TMP_DIR="/tmp"
fi
PROMPT_FILE=$(mktemp "${PROMPT_TMP_DIR}/gemini_prompt.XXXXXX.txt")
cat > "$PROMPT_FILE" <<EOF
あなたはシステム整合性審査専門のレビュアー（デコポンとは異なる俯瞰視点）。以下のdiffを審査してください。
**【役割変更 2026-05-05 理事長殿御指示】開発期間中は法令観点を行わない**。完成後の最終総合監査で別途実施。
今回は「プログラム本体や周辺との関連性チェック」を主任務とする。

タスクID: ${TASK_ID}
サイクル: ${CYCLE}
変更パス: ${CHANGED_PATHS}
PII該当検知（参考情報のみ、今回は監査対象外）: ${HAS_PII}

=== 審査観点（8観点・システム整合性版） ===
1. spec_compliance (仕様準拠): 設計書(DD-XXX, context/*.md)と乖離がないか、acceptance_criteria全充足か
2. system_relations (システム関連性): 他モジュールへの影響範囲、API契約変更時の呼出元、共有state/contextの破壊
3. side_effects (副作用・依存関係): DB トリガ/watcher/cron/hook で連鎖発動する処理、循環依存、レースコンディション
4. completeness (網羅性): エッジケース、空入力、境界値、エラーパス、並行実行、タイムアウト、リソースリーク
5. data_flow (データフロー整合): 入力→処理→保存→読出 全経路でデータが正しく流れるか、SSOT 維持
6. extensibility (拡張性): 将来の機能追加に耐える設計か。新医院/新処置/新ロール/新書類/法令改定/新デバイス/多言語化/DBスキーマ進化/API バージョニング各観点で評価
7. observability_error_handling (観察可能性・エラー処理): CLAUDE.md §Error Design & Observability Mandate の8項目チェック (構造化ログ/correlation_id/アラート発火条件/fallback/retry cap/ヘルスチェック/エラーdump/ユーザー向けエラー文言)
8. documentation (ドキュメント整合): コメント、JSDoc/docstring、README、型定義、変更履歴、設計書の同期

=== 重要 ===
- このdiffに限定して審査せよ。リポジトリ全体を走査するな（フル走査は禁止）
- 各観点のfindings は Severity (critical|high|medium|low) を必ず付与
- Critical/High が1件でもあれば該当観点は fail
- legal_compliance / 個人情報保護 / 医療情報取扱い 観点は **今回スキップ**（完成後の最終監査で実施）
- ジェミちゃんはデコポンと異なる「俯瞰視点・関連性」を重視せよ

=== 設計書抜粋（仕様準拠の判断材料） ===
${SPEC_CONTENT}

=== 出力形式（JSON のみ） ===
{
  "task_id": "${TASK_ID}",
  "cycle": ${CYCLE},
  "pii_detected_info_only": ${HAS_PII},
  "audit_phase": "development_system_integrity",
  "categories": {
    "spec_compliance": {"verdict": "pass|fail", "findings": [{"severity": "...", "id": "S1", "description": "...", "file": "...", "line": 0, "fix_suggestion": "..."}]},
    "system_relations": {"verdict": "pass|fail", "findings": []},
    "side_effects": {"verdict": "pass|fail", "findings": []},
    "completeness": {"verdict": "pass|fail", "findings": []},
    "data_flow": {"verdict": "pass|fail", "findings": []},
    "extensibility": {"verdict": "pass|fail", "findings": []},
    "observability_error_handling": {"verdict": "pass|fail", "findings": []},
    "documentation": {"verdict": "pass|fail", "findings": []}
  },
  "overall_verdict": "pass|fail",
  "summary": "総括 (1-3文)"
}

=== 差分 ===
${DIFF}
EOF

# Invoke Gemini — stdin 経由で大きい prompt を渡す (ARG_MAX 128KB 制限回避)。
# Gemini CLI 仕様 (`gemini --help`): "Appended to input on stdin (if any)" =
# `-p` 引数は stdin の後に追記される。大きい diff/spec は stdin、短いトリガは -p。
# Issue: ~50KB 超の diff で「Argument list too long」発生 (Phase 3 cycle1, QR cycle3 等で実害)。
GEMINI_OUT=$(gemini -p "上記の指示に従い、JSON のみで監査結果を返答せよ。" < "$PROMPT_FILE" 2>"$LOG")
GEMINI_EXIT=$?

rm -f "$PROMPT_FILE"

if [ $GEMINI_EXIT -ne 0 ] || [ -z "$GEMINI_OUT" ]; then
  echo "{\"task_id\":\"$TASK_ID\",\"cycle\":$CYCLE,\"overall_verdict\":\"invocation_error\",\"summary\":\"gemini invocation failed: see $LOG\"}" > "$OUTPUT"
  echo "invocation_error"
  exit 2
fi

# Extract JSON from Gemini output (Gemini may include markdown fence)
echo "$GEMINI_OUT" | python3 -c "
import sys, json, re
text = sys.stdin.read()
# Try to extract JSON block
m = re.search(r'\`\`\`(?:json)?\s*(\{.*\})\s*\`\`\`', text, re.DOTALL)
if m:
    text = m.group(1)
else:
    # Find first { to last }
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        text = text[start:end+1]
try:
    d = json.loads(text)
    print(json.dumps(d, ensure_ascii=False, indent=2))
except Exception as e:
    print(json.dumps({
        'task_id': '$TASK_ID',
        'cycle': $CYCLE,
        'overall_verdict': 'invocation_error',
        'parse_error': str(e),
        'raw_output': text[:500]
    }, ensure_ascii=False))
" > "$OUTPUT"

VERDICT=$(python3 -c "
import json
try:
  d = json.load(open('$OUTPUT'))
  print(d.get('overall_verdict', 'invocation_error'))
except Exception:
  print('invocation_error')
")

echo "$VERDICT"

case "$VERDICT" in
  pass) exit 0 ;;
  fail) exit 1 ;;
  *) exit 2 ;;
esac
