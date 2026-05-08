#!/usr/bin/env bash
# scripts/message_delivery_v2/codex_guard.sh — Codex pane interruption guard
#
# Phase 0 反省点 c (= send-keys 連発 Codex interruption) + 反省点 w (= 長文 submit 不確定)
# + 反省点 m (= cli_adapter drift) + 反省点 x (= ESCALATION /clear 暴発) への対応。
#
# Codex pane への send-keys 直前に pre-flight check を行い、Conversation interrupted
# / sandbox 固着 / drift / TUI 空白等の危険な状態で送信を阻止する。
#
# Usage:
#   bash scripts/message_delivery_v2/codex_guard.sh <agent_id> <pane_target>
#   exit code:
#     0 = allow (= send 可能)
#     1 = queued_nudge (= cooldown 中、queue へ積む)
#     2 = blocked_interruption_risk (= Working / sandbox prompt 検知)
#     3 = pane_drift (= agent_id 不一致、絶対拒否)
#     4 = tui_empty (= TUI 空白、書面 mode フォールバック推奨)
#     5 = bash_shell (= Codex 終了、bash shell 状態、緊急介入要)
#
# 設計: docs/message_delivery_v2_design_2026-05-08.md §2.4

set -euo pipefail

AGENT_ID="${1:-}"
PANE_TARGET="${2:-}"

if [[ -z "$AGENT_ID" || -z "$PANE_TARGET" ]]; then
    echo "Usage: $0 <agent_id> <pane_target>" >&2
    exit 99
fi

_GUARD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_GUARD_PROJECT_ROOT="$(cd "${_GUARD_DIR}/../.." && pwd)"

# cooldown 状態ファイル
COOLDOWN_FILE="${_GUARD_PROJECT_ROOT}/queue/watchers/${AGENT_ID}.last_nudge"
COOLDOWN_SEC=120

# pane 存在確認
if ! tmux list-panes -a -F "#{session_name}:#{window_index}.#{pane_index}" 2>/dev/null | grep -qx "$PANE_TARGET"; then
    echo "blocked: pane $PANE_TARGET does not exist" >&2
    exit 3
fi

# pane @agent_id 一致確認 (= 反省点 n 対応)
pane_agent_id=$(tmux display-message -t "$PANE_TARGET" -p '#{@agent_id}' 2>/dev/null || echo "")
if [[ -z "$pane_agent_id" ]]; then
    echo "blocked: pane $PANE_TARGET has no @agent_id env" >&2
    exit 3
fi
if [[ "$pane_agent_id" != "$AGENT_ID" ]]; then
    echo "pane_drift: expected=$AGENT_ID actual=$pane_agent_id" >&2
    exit 3
fi

# capture-pane で現在表示確認
capture=$(tmux capture-pane -t "$PANE_TARGET" -p 2>/dev/null || echo "")
capture_tail=$(echo "$capture" | tail -20)

# TUI 空白判定 (= 反省点 d 対応)
non_empty_lines=$(echo "$capture" | grep -cE '\S' || echo "0")
if [[ "$non_empty_lines" -lt 2 ]]; then
    echo "tui_empty: capture has $non_empty_lines non-empty lines, fallback to book mode" >&2
    exit 4
fi

# bash shell 状態検知 (= 反省点 x 対応、Codex 終了状態)
if echo "$capture_tail" | grep -qE '^\S+@\S+:.*\$\s*$'; then
    echo "bash_shell: pane is at bash prompt, Codex has exited, manual intervention required" >&2
    exit 5
fi

# sandbox 確認プロンプト検知 (= 反省点 t 対応)
if echo "$capture_tail" | grep -qE 'Yes, proceed|Press enter to confirm|tell Codex what to do differently'; then
    echo "blocked_interruption_risk: sandbox prompt detected" >&2
    exit 2
fi

# Working マーカー検知 (= Codex 作業中)
if echo "$capture_tail" | grep -qE '• Working \([0-9]+[smh] • esc to interrupt\)'; then
    echo "blocked_interruption_risk: Codex Working state detected" >&2
    exit 2
fi

# cooldown 確認 (= 反省点 c 対応、120 秒)
if [[ -f "$COOLDOWN_FILE" ]]; then
    last_epoch=$(cat "$COOLDOWN_FILE" 2>/dev/null || echo 0)
    now_epoch=$(date +%s)
    elapsed=$((now_epoch - last_epoch))
    if [[ $elapsed -lt $COOLDOWN_SEC ]]; then
        echo "queued_nudge: cooldown ${elapsed}s < ${COOLDOWN_SEC}s" >&2
        exit 1
    fi
fi

# 全 check PASS
echo "allow: all guards passed for $AGENT_ID at $PANE_TARGET"
exit 0
