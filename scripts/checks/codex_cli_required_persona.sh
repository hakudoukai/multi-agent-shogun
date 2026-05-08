#!/usr/bin/env bash
# codex_cli_required_persona.sh — 家康 + 本多 の cli mismatch 検知 (§19 advisory hook)
#
# Phase 5 codex personas immediate cmd の 4 重防御 γ-2 (= operate-time 検知)。
# 家康 (ieyasu) と本多 (honda) が claude などの別 CLI で誤起動されたら stderr 警告。
#
# §19.3 順守: 絶対にブロックしない、exit 0、timeout 5 秒、stderr 警告のみ。
#
# Usage (PreToolUse hook):
#   bash $CLAUDE_PROJECT_DIR/scripts/checks/codex_cli_required_persona.sh || true

set +e
PATH="${PATH}:/usr/bin:/bin"

# tmux 不在環境では即座に exit 0
command -v tmux >/dev/null 2>&1 || exit 0

# tmux session が無ければ exit 0
tmux list-sessions >/dev/null 2>&1 || exit 0

REQUIRED_PERSONAS="ieyasu honda"
WARNING_COUNT=0

# codex 起動時の pane_current_command 期待値:
#   - "codex": codex CLI 直接起動時
#   - "node": codex の child process (= 実運用で最頻出、~/.npm-global/bin/codex 経由)
# どちらも codex 稼働とみなす。
is_codex_cli() {
    case "$1" in
        node|codex) return 0 ;;
        *) return 1 ;;
    esac
}

# 全 session × 全 window × 全 pane を scan
while IFS=$'\t' read -r session_window_pane agent_id current_cmd; do
    [ -z "$agent_id" ] && continue
    for required_persona in $REQUIRED_PERSONAS; do
        if [ "$agent_id" = "$required_persona" ]; then
            if ! is_codex_cli "$current_cmd"; then
                echo "[codex-cli-required-persona] WARN: ${agent_id} pane (${session_window_pane}) is running '${current_cmd}' instead of codex (node|codex)." >&2
                echo "  Phase 5 violation. Restart with codex CLI to prevent token accumulation events." >&2
                echo "  Re-launch via: tmux respawn-pane -k -t ${session_window_pane} + codex" >&2
                WARNING_COUNT=$((WARNING_COUNT + 1))
            fi
        fi
    done
done < <(
    tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index}'$'\t''#{@agent_id}'$'\t''#{pane_current_command}' 2>/dev/null
)

# §19.3 順守: 違反検出しても exit 0 (= ブロック禁止、advisory のみ)
exit 0
