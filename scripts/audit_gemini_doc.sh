#!/usr/bin/env bash
# audit_gemini_doc.sh — ガバナンス文書 (SOUL.md 等 prose-doc) を Gemini に観点A-I で監査依頼する標準スクリプト
#
# audit_codex_doc.sh の Gemini 版 (俯瞰視点)。観点A-I は同一。
# 注: 現状 Gemini CLI は IneligibleTier (UNSUPPORTED_CLIENT / free-tier client廃止) 等で
# invocation_error になりうる。その場合は ≠RED・記録のみ・復帰後再走機会確保
# (memory: gemini-audit-invocation-error-can-be-ineligible-tier-not-erofs)。
#
# Usage:
#   bash scripts/audit_gemini_doc.sh <task_id> <doc_file_path> [<ref_dir>]
#
# Output:
#   - JSON 結果を /tmp/gemini_doc_audit_<task_id>.json に保存
#   - 標準出力に overall_verdict を返す
#   - 終了コード: 0=PASS, 1=RED, 2=invocation error, 4=CONDITIONAL
#
# 監査フレームワーク準拠: docs/audit-framework.md §5 (Gemini 監査) の文書版

set -uo pipefail

TASK_ID="${1:-}"
DOC_FILE="${2:-}"
REF_DIR="${3:-}"

if [ -z "$TASK_ID" ] || [ -z "$DOC_FILE" ]; then
  echo "Usage: $0 <task_id> <doc_file_path> [<ref_dir>]" >&2
  exit 2
fi

if [ ! -f "$DOC_FILE" ]; then
  echo "{\"task_id\":\"$TASK_ID\",\"overall_verdict\":\"invocation_error\",\"summary\":\"doc_file not found: $DOC_FILE\"}"
  exit 2
fi

OUTPUT="/tmp/gemini_doc_audit_${TASK_ID}.json"
LOG="/tmp/gemini_doc_audit_${TASK_ID}.log"

DOC_CONTENT=$(cat "$DOC_FILE")
DOC_CHARS=${#DOC_CONTENT}

REF_CONTENT=""
if [ -n "$REF_DIR" ] && [ -d "$REF_DIR" ]; then
  while IFS= read -r f; do
    REF_CONTENT="${REF_CONTENT}

===== 参照資料: $(basename "$f") =====
$(cat "$f")"
  done < <(find "$REF_DIR" -maxdepth 1 -type f \( -name '*.md' -o -name '*.txt' \) | sort)
fi

# PROMPT_FILE — writable tmp に配置 (EROFS 回避)
PROMPT_TMP_DIR="${PROMPT_TMP_DIR:-/tmp}"
[ -d "$PROMPT_TMP_DIR" ] || PROMPT_TMP_DIR="/tmp"
PROMPT_FILE=$(mktemp "${PROMPT_TMP_DIR}/gemini_doc_prompt.XXXXXX.txt")
cat > "$PROMPT_FILE" <<EOF
あなたはガバナンス文書監査専門家 (デコポンとは異なる俯瞰視点)。以下の文書を観点A-Iで監査せよ。
これは git diff のコードレビューではなく、ガバナンス文書 (システムプロンプト / 規程 / 設計憲章 class) の prose 監査である。

監査タスクID: ${TASK_ID}
監査対象文書: $(basename "$DOC_FILE")
文書文字数: ${DOC_CHARS}

=== 監査観点 (A-I 固定。順守せよ) ===
A. v3.1既存条項の完全継承確認: 旧版 (ref 資料) の既存条項・規範・禁則が新版で漏れなく継承されているか。意図せぬ削除・弱化がないか
B. 10教訓組込位置の妥当性: 本日インシデント由来の教訓が文書内の適切な位置・粒度・文脈で組み込まれているか。重複・矛盾・場違いがないか
C. DD-170〜173 (視覚監査基準) 整合: 視覚監査 (human-eye / 偽green禁 / 実画面検収) に関する基準と整合しているか
D. PERMS-02 / FKI-HERMES-UPSTREAM-RELAY-01 / DD-HERMES-CODEX-PIVOT-01 整合: secret物理境界 / Hermes上り経路一本化 (hermes_relay経由) / Hermes-Codex pivot 規約と整合しているか
E. 副院長平時規範整合: 副院長の平時 (非緊急時) の権限境界・責務規範と整合しているか
F. 緊急時拡張の発動条件・自動失効条件の明確性: 緊急時の役務拡張について、発動条件と自動失効 (期間終了で平時復帰) の条件が曖昧さなく明記されているか
G. 物理ファイル書換+Hermes再起動で実装可能か: 本文書をシステムプロンプトとして物理ファイルに反映し Hermes を再起動するだけで実装可能か。外部依存・未定義参照・実装不能な記述がないか
H. 文章の冗長性・装飾文字混入・Confusable Unicode リスク: 冗長表現・過剰装飾文字 (★等の濫用)・Confusable Unicode による誤読/なりすましリスクがないか
I. 全体の論理一貫性: 文書全体で前後矛盾・循環参照・優先順位の衝突がなく論理的に一貫しているか

=== 重要 ===
- この文書 (+ ref資料) に限定して監査せよ。リポジトリ全体を走査するな
- 各観点の findings は Severity (critical|high|medium|low) を必ず付与
- 各観点の verdict は "PASS" | "RED" | "CONDITIONAL" のいずれか
- overall_verdict: 観点に RED が1件でもあれば RED / RED無し+CONDITIONAL有り → CONDITIONAL / 全PASS → PASS
- fix_proposals は具体的な差分形式で、conditional_requirements は必須条件を列挙せよ

=== 出力形式 (JSON のみ) ===
{
  "task_id": "${TASK_ID}",
  "overall_verdict": "PASS|RED|CONDITIONAL",
  "observations": {
    "A": {"verdict": "PASS|RED|CONDITIONAL", "findings": [{"severity": "...", "description": "...", "location": "..."}]},
    "B": {"verdict": "...", "findings": []},
    "C": {"verdict": "...", "findings": []},
    "D": {"verdict": "...", "findings": []},
    "E": {"verdict": "...", "findings": []},
    "F": {"verdict": "...", "findings": []},
    "G": {"verdict": "...", "findings": []},
    "H": {"verdict": "...", "findings": []},
    "I": {"verdict": "...", "findings": []}
  },
  "fix_proposals": [{"observation": "A|B|...|I", "diff": "before: ...\\nafter: ..."}],
  "conditional_requirements": [],
  "summary": "総括 (1-3文)"
}

=== 監査対象文書 (全文) ===
${DOC_CONTENT}
${REF_CONTENT}
EOF

# Invoke Gemini (大きい prompt は stdin 経由・短いトリガは -p)
GEMINI_OUT=$(gemini -p "上記の指示に従い、JSON のみで監査結果を返答せよ。" < "$PROMPT_FILE" 2>"$LOG")
GEMINI_EXIT=$?

rm -f "$PROMPT_FILE"

if [ $GEMINI_EXIT -ne 0 ] || [ -z "$GEMINI_OUT" ]; then
  # IneligibleTier / EROFS / その他 invocation 失敗。≠RED・記録のみ。
  echo "{\"task_id\":\"$TASK_ID\",\"overall_verdict\":\"invocation_error\",\"summary\":\"gemini invocation failed (IneligibleTier/EROFS 等想定): see $LOG\"}" > "$OUTPUT"
  echo "invocation_error"
  exit 2
fi

# Extract JSON from Gemini output (markdown fence 除去・env 経由で interpolation 断つ)
GEMINI_OUT="$GEMINI_OUT" AUDIT_TASK_ID="$TASK_ID" \
python3 - <<'PYEOF' > "$OUTPUT"
import json, re, os
text = os.environ.get('GEMINI_OUT', '')
task_id = os.environ.get('AUDIT_TASK_ID', '')
m = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, re.DOTALL)
if m:
    text = m.group(1)
else:
    start = text.find('{'); end = text.rfind('}')
    if start >= 0 and end > start:
        text = text[start:end+1]
try:
    d = json.loads(text)
    print(json.dumps(d, ensure_ascii=False, indent=2))
except Exception as e:
    print(json.dumps({
        'task_id': task_id,
        'overall_verdict': 'invocation_error',
        'parse_error': str(e),
        'raw_output': text[:500]
    }, ensure_ascii=False))
PYEOF

VERDICT=$(AUDIT_OUTPUT_PATH="$OUTPUT" python3 - <<'PYEOF'
import json, os
try:
    d = json.load(open(os.environ['AUDIT_OUTPUT_PATH']))
    print(d.get('overall_verdict', 'invocation_error'))
except Exception:
    print('invocation_error')
PYEOF
)

echo "$VERDICT"

case "$VERDICT" in
  PASS) exit 0 ;;
  RED) exit 1 ;;
  CONDITIONAL) exit 4 ;;
  *) exit 2 ;;
esac
