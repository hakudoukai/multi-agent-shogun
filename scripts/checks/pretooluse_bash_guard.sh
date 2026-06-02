#!/usr/bin/env bash
# pretooluse_bash_guard.sh — Claude Code PreToolUse Bash hook
#
# 旧 inline (.claude/settings.json) は `if ... then ... fi; exit 0` の一行式で、
# Windows 上の Claude Code hook executor が `bash <hook_command>` を `bash -c`
# に渡す際、コマンド先頭が `if` だと `bash if ...` となり構文崩壊した
# (2026-06-02 Commander 診断 seq30274)。
#
# 対策:
#   (1) ロジックをスクリプトファイルへ退避し settings.json は単一パス呼出のみ
#   (2) settings.json の command は先頭 `bash ` を付けない (executor 側で
#       prepend されるため重複させない)
#
# 役割: tmux split-window / kill-pane / respawn-pane が呼ばれる時のみ
#       pane identity 整合チェックを走らせ、警告は stderr に出すだけ
#       (絶対にブロックしない: §19 観点・hook はブロック禁)。
# 失敗時も exit 0 で素通り。
#
# ★cycle4 B1 修正 (副院長令 baabd1ca / Codex audit 40c0d3d2 B1 high close)★:
#   Claude Code PreToolUse hook 公式仕様 = stdin JSON 入力 (DD-169 cycle4 + 公式
#   ドキュメント準拠)。env var CLAUDE_TOOL_INPUT のみ依存の旧実装は stdin JSON
#   無視で pane_identity check が実質不発の疑いゆえ、stdin JSON `.tool_input.command`
#   抽出を一次経路化、CLAUDE_TOOL_INPUT は fallback として残置 (後方互換)。
#   実 hook 発火テスト (tests/checks/pretooluse_stdin_json/) で stdin JSON 経路を
#   検証する。

set +e

# 公式仕様: stdin JSON `.tool_input.command` 抽出 (一次経路)
INPUT_JSON=$(cat 2>/dev/null)
COMMAND=$(printf '%s' "$INPUT_JSON" | python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print(d.get('tool_input', {}).get('command', ''), end='')
except Exception:
    sys.exit(1)
" 2>/dev/null)
PYTHON_RC=$?

# fallback: 旧 CLAUDE_TOOL_INPUT envvar (公式仕様抽出失敗時 or stdin 空時)
if [ "$PYTHON_RC" -ne 0 ] || [ -z "$COMMAND" ]; then
    COMMAND="${CLAUDE_TOOL_INPUT:-}"
fi

# tmux 危険系操作の検出 → pane identity check 発動
if printf '%s' "$COMMAND" | grep -qE '(tmux split-window|tmux kill-pane|tmux respawn-pane)'; then
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    bash "$here/pane_identity.sh" >&2 2>/dev/null || true
fi

# §19 観点・hook はブロック禁: 必ず exit 0
exit 0
