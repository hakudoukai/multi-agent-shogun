#!/usr/bin/env bash
# audit_codex_doc.sh — ガバナンス文書 (SOUL.md 等 prose-doc) を Codex に観点A-I で監査依頼する標準スクリプト
#
# 既存 audit_codex.sh は git diff 6軸コードレビュー固定で prose-doc / 観点A-I に非対応。
# 本 wrapper は文書監査を versioned script として固定し ad-hoc 手書き prompt を排除する
# (手書き禁の趣旨 = ad-hoc 防止を script 固定で充足、副院長GO #1 / 副院長令 3b4520cf)。
#
# Usage:
#   bash scripts/audit_codex_doc.sh <task_id> <doc_file_path> [<ref_dir>]
#
#   <task_id>       監査タスクID
#   <doc_file_path> 監査対象文書 (markdown/text)。全文を prompt に埋め込む
#   <ref_dir>       (任意) 比較用 ref 資料ディレクトリ。配下の *.md / *.txt を全て併記
#
# Output:
#   - JSON 結果を /tmp/codex_doc_audit_<task_id>.json に保存
#   - 標準出力に overall_verdict (PASS|RED|CONDITIONAL|invocation_error|fallback_required) を返す
#   - 終了コード: 0=PASS, 1=RED, 2=invocation error, 3=usage limit, 4=CONDITIONAL
#
# 監査フレームワーク準拠: docs/audit-framework.md §4 (Codex 監査) の文書版

set -uo pipefail

TASK_ID="${1:-}"
DOC_FILE="${2:-}"
REF_DIR="${3:-}"

if [ -z "$TASK_ID" ] || [ -z "$DOC_FILE" ]; then
  echo "Usage: $0 <task_id> <doc_file_path> [<ref_dir>]" >&2
  echo "Example: $0 subtask_soulmd_v32 /tmp/soulmd_v32_audit/soul_v32.md /tmp/soulmd_v32_audit_ref" >&2
  exit 2
fi

if [ ! -f "$DOC_FILE" ]; then
  echo "{\"task_id\":\"$TASK_ID\",\"overall_verdict\":\"invocation_error\",\"summary\":\"doc_file not found: $DOC_FILE\"}"
  exit 2
fi

OUTPUT="/tmp/codex_doc_audit_${TASK_ID}.json"
LOG="/tmp/codex_doc_audit_${TASK_ID}.log"

DOC_CONTENT=$(cat "$DOC_FILE")
DOC_CHARS=${#DOC_CONTENT}

# ref 資料 (任意) — 配下の *.md / *.txt を連結
REF_CONTENT=""
if [ -n "$REF_DIR" ] && [ -d "$REF_DIR" ]; then
  while IFS= read -r f; do
    REF_CONTENT="${REF_CONTENT}

===== 参照資料: $(basename "$f") =====
$(cat "$f")"
  done < <(find "$REF_DIR" -maxdepth 1 -type f \( -name '*.md' -o -name '*.txt' \) | sort)
fi

# Build prompt (heredoc to temp file to avoid shell escaping)
PROMPT_FILE=$(mktemp)
cat > "$PROMPT_FILE" <<EOF
あなたはガバナンス文書監査専門家。以下の文書を観点A-Iで監査せよ。
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
H. 文章の冗長性・装飾文字混入・Confusable Unicode リスク: 冗長表現・過剰装飾文字 (★等の濫用)・Confusable Unicode (見た目が似た別コードポイント) による誤読/なりすましリスクがないか
I. 全体の論理一貫性: 文書全体で前後矛盾・循環参照・優先順位の衝突がなく論理的に一貫しているか

=== 重要 ===
- この文書 (+ ref資料) に限定して監査せよ。リポジトリ全体を走査するな
- 各観点の findings は Severity (critical|high|medium|low) を必ず付与
- 各観点の verdict は "PASS" | "RED" | "CONDITIONAL" のいずれか
- overall_verdict 判定規則:
    * critical/high の finding が1件でもあれば該当観点=RED
    * 観点に RED が1件でもあれば overall=RED
    * RED は無いが CONDITIONAL (条件付き合格) が1件以上 → overall=CONDITIONAL
    * 全観点 PASS のみ → overall=PASS
- fix_proposals は具体的な差分形式 (before/after または unified diff 風) で記述せよ
- conditional_requirements は CONDITIONAL 合格に必要な必須条件を列挙せよ

=== 出力形式 (JSON のみ。前後説明文不要) ===
{
  "task_id": "${TASK_ID}",
  "overall_verdict": "PASS|RED|CONDITIONAL",
  "observations": {
    "A": {"verdict": "PASS|RED|CONDITIONAL", "findings": [{"severity": "critical|high|medium|low", "description": "...", "location": "..."}]},
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

# ── Codex 呼出し (retry / usage limit / EROFS-resilient HOME) ──
# EROFS handling: 既定 HOME (~/.codex の auth/state) で実行するが、HOME が read-only で
# codex の state 書込が EROFS で失敗する場合に備え、writable HOME へ ~/.codex を複製して再試行する
# (memory: codex-state-db-repair / gemini-audit-erofs-writable-home-repair と同方向)。
run_codex() {
  local home_override="$1"
  if [ -n "$home_override" ]; then
    HOME="$home_override" npx @openai/codex exec --json --output-last-message "$OUTPUT" < "$PROMPT_FILE" 2>"$LOG"
  else
    npx @openai/codex exec --json --output-last-message "$OUTPUT" < "$PROMPT_FILE" 2>"$LOG"
  fi
}

RETRY=0
MAX_RETRY=3
HOME_OVERRIDE=""
while [ $RETRY -lt $MAX_RETRY ]; do
  run_codex "$HOME_OVERRIDE"
  CODEX_EXIT=$?

  # usage limit 検出 → fallback_required で離脱 (audit_codex.sh と同形)
  if grep -qE "usage limit|rate.?limit|429|quota" "$LOG" 2>/dev/null; then
    rm -f "$PROMPT_FILE"
    echo "{\"task_id\":\"$TASK_ID\",\"overall_verdict\":\"fallback_required\",\"fallback_reason\":\"codex usage limit\",\"summary\":\"see $LOG\"}" > "$OUTPUT"
    echo "fallback_required"
    exit 3
  fi

  # EROFS 検出 → writable HOME へ ~/.codex 複製して1回だけ切替再試行
  if [ -z "$HOME_OVERRIDE" ] && grep -qiE "EROFS|read-only file system" "$LOG" 2>/dev/null; then
    TMP_HOME=$(mktemp -d /tmp/codex-doc-home.XXXXXX)
    if [ -d "$HOME/.codex" ]; then
      cp -a "$HOME/.codex" "$TMP_HOME/.codex" 2>/dev/null || true
    fi
    HOME_OVERRIDE="$TMP_HOME"
    continue  # RETRY を消費せず HOME 切替で再試行
  fi

  if [ $CODEX_EXIT -eq 0 ] && [ -s "$OUTPUT" ]; then
    break
  fi

  RETRY=$((RETRY + 1))
  sleep 5
done

rm -f "$PROMPT_FILE"
[ -n "$HOME_OVERRIDE" ] && rm -rf "$HOME_OVERRIDE" 2>/dev/null || true

if [ ! -s "$OUTPUT" ]; then
  echo "{\"task_id\":\"$TASK_ID\",\"overall_verdict\":\"invocation_error\",\"summary\":\"codex did not produce output after $MAX_RETRY retries\"}" > "$OUTPUT"
  echo "invocation_error"
  exit 2
fi

# Extract verdict (env 経由で python に渡し literal interpolation を断つ)
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
