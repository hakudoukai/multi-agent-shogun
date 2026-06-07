#!/usr/bin/env bash
# context_usage_warn.sh — Claude Code UserPromptSubmit hook (STEP1-C 副院長令)
#
# 目的 (context 衛生機構):
#   Claude Code 2.x の /compact は (a) 自動 (context limit 接近時) + (b) 手動 (/compact 入力)
#   の二系統で発火するが、★閾値到達「前」に proactive に notice する公的 API は存在しない★。
#   本 hook は session jsonl ファイル size を heuristic に観測し、危険水域に近づいた際
#   stderr へ警告を吐く。Claude Code が会話と共に stderr を表示するため、ユーザーへ
#   早期 /compact 入力を促す機構となる。
#
# 配線:
#   .claude/settings.json の "UserPromptSubmit" hook へ登録 (timeout 5、|| true 必須)。
#   絶対にブロックしない (DD-169 設計原則と整合、PreToolUse の hook 設計と同一)。
#
# 仕組み:
#   1. 現セッションの jsonl 経路を CLAUDE_CODE_SESSION_ID env から導出
#   2. file size (bytes) を観測
#   3. 既定閾値:
#      - WARN_BYTES (=1.6MB / 約 80%): stderr "★context_warn★ jsonl=XKB ≒ 80% — /compact 推奨"
#      - DANGER_BYTES (=2.0MB / 約 95%): stderr "★context_danger★ jsonl=XKB ≒ 95% — /compact 即実行"
#   4. 閾値は env で上書き可 (CONTEXT_WARN_BYTES / CONTEXT_DANGER_BYTES)
#
# 注意:
#   - jsonl は immutable log で live in-memory context とは厳密一致しない (auto-compact 後も
#     jsonl は append され続けるため過大推定気味)。あくまで heuristic な早期警告として運用。
#   - 厳密な context % は /context slash command (対話的に Claude へ入力) でのみ取得可能。
#   - 本 hook は ★絶対にブロックしない★ (exit 0 強制)。

set -u

WARN_BYTES="${CONTEXT_WARN_BYTES:-1600000}"   # ~1.6 MB ≒ 80% (heuristic)
DANGER_BYTES="${CONTEXT_DANGER_BYTES:-2000000}" # ~2.0 MB ≒ 95% (heuristic)

SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$HOME/multi-agent-shogun}"

# project_dir を Claude Code 流に slug 化 (`/` → `-` 接頭辞)
PROJECT_SLUG="-$(echo "$PROJECT_DIR" | sed 's|^/||; s|/|-|g')"
JSONL_PATH="$HOME/.claude/projects/$PROJECT_SLUG/$SESSION_ID.jsonl"

if [ -z "$SESSION_ID" ] || [ ! -f "$JSONL_PATH" ]; then
    # session 情報取得不能 → silently exit (絶対 block 禁)
    exit 0
fi

SZ=$(stat -c '%s' "$JSONL_PATH" 2>/dev/null || echo 0)
KB=$((SZ / 1024))

if [ "$SZ" -ge "$DANGER_BYTES" ]; then
    echo "★context_danger★ session jsonl=${KB}KB (>=$(($DANGER_BYTES / 1024))KB ≒ 95% heuristic) — ★即 /compact 入力推奨★" >&2
elif [ "$SZ" -ge "$WARN_BYTES" ]; then
    echo "★context_warn★ session jsonl=${KB}KB (>=$(($WARN_BYTES / 1024))KB ≒ 80% heuristic) — /compact 入力を検討" >&2
fi

exit 0
