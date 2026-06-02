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

set +e

input="${CLAUDE_TOOL_INPUT:-}"
if printf '%s' "$input" | grep -qE '(tmux split-window|tmux kill-pane|tmux respawn-pane)'; then
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    bash "$here/pane_identity.sh" >&2 2>/dev/null || true
fi

exit 0
