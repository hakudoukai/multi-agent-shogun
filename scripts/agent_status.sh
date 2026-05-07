#!/usr/bin/env bash
# scripts/agent_status.sh — Show busy/idle status of all agents in tmux panes
#
# Usage:
#   bash scripts/agent_status.sh                    # Auto-detect from config
#   bash scripts/agent_status.sh --session myses    # Specify tmux session
#   bash scripts/agent_status.sh --panes 0,1,2,3    # Specify pane indices
#   bash scripts/agent_status.sh --lang en          # English labels
#
# Works in two modes:
#   1. Project mode (default): Reads agent list from config/settings.yaml
#      and shows task YAML + inbox status alongside pane state.
#   2. Standalone mode (--session/--panes): Just shows tmux pane busy/idle
#      state without project-specific data. Works anywhere.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ─── Defaults ───
LANG_MODE="ja"
SESSION_NAME=""
MANUAL_PANES=""
STANDALONE=false

# ─── Parse args ───
while [[ $# -gt 0 ]]; do
    case "$1" in
        --lang)    LANG_MODE="$2"; shift 2 ;;
        --session) SESSION_NAME="$2"; STANDALONE=true; shift 2 ;;
        --panes)   MANUAL_PANES="$2"; STANDALONE=true; shift 2 ;;
        --help|-h)
            echo "Usage: agent_status.sh [--session NAME] [--panes 0,1,2] [--lang en|ja]"
            echo ""
            echo "Options:"
            echo "  --session NAME   Tmux session to scan (default: auto-detect)"
            echo "  --panes N,N,N    Comma-separated pane indices to check"
            echo "  --lang en|ja     Output language (default: ja)"
            echo ""
            echo "Without options, reads config/settings.yaml for agent definitions."
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ─── Load shared library ───
source "$SCRIPT_DIR/lib/agent_status.sh"
source "$SCRIPT_DIR/lib/_section18_roles.sh"

# ─── Label functions ───
state_label() {
    local rc="$1"
    if [[ "$LANG_MODE" == "en" ]]; then
        case $rc in
            0) echo "BUSY" ;;
            1) echo "IDLE" ;;
            2) echo "N/A" ;;
        esac
    else
        case $rc in
            0) echo "稼働中" ;;
            1) echo "待機中" ;;
            2) echo "不在" ;;
        esac
    fi
}

# ─── CJK-aware padding ───
# printf doesn't account for double-width CJK characters.
# This function prints a field with correct visual alignment.
print_padded() {
    local text="$1" width="$2"
    # Calculate display width: byte length minus char count gives extra bytes from multibyte chars
    local byte_len char_len extra_bytes display_width pad
    byte_len=$(echo -n "$text" | wc -c)
    char_len=${#text}
    # Each CJK char is 3 bytes in UTF-8 and 2 display columns.
    # extra_bytes = byte_len - char_len = (3-1)*cjk_count = 2*cjk_count
    # display_width = char_len + cjk_count = char_len + extra_bytes/2
    extra_bytes=$((byte_len - char_len))
    display_width=$((char_len + extra_bytes / 2))
    pad=$((width - display_width))
    if (( pad < 0 )); then pad=0; fi
    printf "%s%*s" "$text" "$pad" ""
}

# ═══════════════════════════════════════════
# Standalone mode: just scan tmux panes
# ═══════════════════════════════════════════
if $STANDALONE; then
    # Determine session
    if [[ -z "$SESSION_NAME" ]]; then
        SESSION_NAME=$(tmux display-message -p '#{session_name}' 2>/dev/null || echo "")
        if [[ -z "$SESSION_NAME" ]]; then
            echo "Error: not inside a tmux session and --session not specified" >&2
            exit 1
        fi
    fi

    # Determine panes — collect all window:pane pairs across the session
    declare -a PANE_TARGETS=()
    if [[ -n "$MANUAL_PANES" ]]; then
        IFS=',' read -ra _indices <<< "$MANUAL_PANES"
        for pidx in "${_indices[@]}"; do
            PANE_TARGETS+=("${SESSION_NAME}:${pidx}")
        done
    else
        # List all panes across all windows in the session
        while IFS= read -r line; do PANE_TARGETS+=("$line"); done < <(tmux list-panes -s -t "$SESSION_NAME" -F '#{session_name}:#{window_name}.#{pane_index}' 2>/dev/null)
    fi

    # Header
    printf "\n"
    if [[ "$LANG_MODE" == "en" ]]; then
        printf "%-30s %-10s %s\n" "Pane" "State" "Agent ID"
        printf "%-30s %-10s %s\n" "------------------------------" "----------" "----------"
    else
        printf "%-30s %-10s %s\n" "Pane" "状態" "Agent ID"
        printf "%-30s %-10s %s\n" "------------------------------" "----------" "----------"
    fi

    for pane_target in "${PANE_TARGETS[@]}"; do
        # Try reading @agent_id from the pane
        agent_id=$(timeout 2 tmux display-message -t "$pane_target" -p '#{@agent_id}' 2>/dev/null || echo "---")
        [[ -z "$agent_id" ]] && agent_id="---"

        agent_is_busy_check "$pane_target" && rc=0 || rc=$?
        label=$(state_label "$rc")

        print_padded "$pane_target" 30
        printf " "
        print_padded "$label" 10
        printf " %s\n" "$agent_id"
    done
    printf "\n"
    exit 0
fi

# ═══════════════════════════════════════════
# Project mode: full status with task/inbox
# ═══════════════════════════════════════════
cd "$SCRIPT_DIR"

# Load cli_adapter if available (for get_cli_type)
CLI_ADAPTER_AVAILABLE=false
if [[ -f "$SCRIPT_DIR/lib/cli_adapter.sh" ]]; then
    source "$SCRIPT_DIR/lib/cli_adapter.sh"
    CLI_ADAPTER_AVAILABLE=true
fi

# Python (PyYAML)
PYTHON="${SCRIPT_DIR}/.venv/bin/python3"
PYTHON_AVAILABLE=false
if [[ -x "$PYTHON" ]]; then
    PYTHON_AVAILABLE=true
fi

# Agent definitions (§18 PC×アカウント配置 — CLAUDE.md §18.1)
#
# cycle1 三者監査 B1/R1 fix: gunshi の index 不整合 (旧実装は AGENTS 末尾に gunshi
# を置き pane_idx=8 で lookup していた。実 MainPC tmux 配置では gunshi は pane
# index 4) を解消するため、_section18_roles.sh からpane順序を参照する。
#
# - MainPC pane 0..4: karo / ashigaru1 / ashigaru2 / ashigaru3 / gunshi
#   (SECTION18_MAINPC_PANE_ORDER の定義順)
# - SecondPC (ashigaru5-8) は別 tmux session のため pane lookup 対象外。
#   task YAML / inbox status のみ表示する。
MAINPC_AGENTS=("${SECTION18_MAINPC_PANE_ORDER[@]}")
SECONDPC_AGENTS=("${SECTION18_SECONDPC_AGENTS[@]}")

# pane-base-index
PANE_BASE=$(tmux show-options -gv pane-base-index 2>/dev/null || echo 0)

# ─── Helper: task info from YAML ───
get_task_info() {
    local agent_id="$1"
    local yaml_file="$SCRIPT_DIR/queue/tasks/${agent_id}.yaml"
    if [[ ! -f "$yaml_file" ]] || ! $PYTHON_AVAILABLE; then
        echo "--- ---"
        return
    fi
    "$PYTHON" -c "
import yaml, sys
try:
    with open('${yaml_file}') as f:
        data = yaml.safe_load(f) or {}
    task = data.get('task', data)
    tid = task.get('task_id', '---')
    status = task.get('status', '---')
    print(f'{tid} {status}')
except Exception:
    print('--- ---')
" 2>/dev/null || echo "--- ---"
}

# ─── Helper: unread inbox count ───
get_unread_count() {
    local agent_id="$1"
    local inbox_file="$SCRIPT_DIR/queue/inbox/${agent_id}.yaml"
    if [[ ! -f "$inbox_file" ]] || ! $PYTHON_AVAILABLE; then
        echo "-"
        return
    fi
    "$PYTHON" -c "
import yaml, sys
try:
    with open('${inbox_file}') as f:
        data = yaml.safe_load(f) or {}
    msgs = data.get('messages', [])
    unread = sum(1 for m in msgs if not m.get('read', False))
    print(unread)
except Exception:
    print('?')
" 2>/dev/null || echo "?"
}

# ─── Output ───
printf "\n"
if [[ "$LANG_MODE" == "en" ]]; then
    printf "%-10s %-7s %-9s %-42s %-10s %s\n" "Agent" "CLI" "State" "Task ID" "Status" "Inbox"
    printf "%-10s %-7s %-9s %-42s %-10s %s\n" "----------" "-------" "---------" "------------------------------------------" "----------" "-----"
else
    printf "%-10s %-7s %-9s %-42s %-10s %s\n" "Agent" "CLI" "Pane" "Task ID" "Status" "Inbox"
    printf "%-10s %-7s %-9s %-42s %-10s %s\n" "----------" "-------" "---------" "------------------------------------------" "----------" "-----"
fi

# ─── Print one agent row (with optional pane lookup) ───
# Args: $1=agent, $2=pane_target ("" → pane state を 不在 で表示)
print_agent_row() {
    local agent="$1"
    local pane_target="$2"

    # CLI type
    local cli_type
    if $CLI_ADAPTER_AVAILABLE; then
        cli_type=$(get_cli_type "$agent" 2>/dev/null || echo "?")
    else
        cli_type="?"
    fi

    # Pane state — SecondPC は別 tmux のため lookup 不可 (rc=2 = 不在)
    local rc pane_state
    if [[ -n "$pane_target" ]]; then
        agent_is_busy_check "$pane_target" && rc=0 || rc=$?
    else
        rc=2
    fi
    pane_state=$(state_label "$rc")

    # Task info
    local task_info task_id task_status
    task_info=$(get_task_info "$agent")
    task_id=$(echo "$task_info" | awk '{print $1}')
    task_status=$(echo "$task_info" | awk '{$1=""; print $0}' | sed 's/^ //')

    # Unread inbox
    local unread
    unread=$(get_unread_count "$agent")

    # Print with CJK padding
    printf "%-10s %-7s " "$agent" "$cli_type"
    print_padded "$pane_state" 9
    printf " %-42s %-10s %s\n" "$task_id" "$task_status" "$unread"
}

# MainPC: pane lookup 有り (multiagent:agents.0..4)
for i in "${!MAINPC_AGENTS[@]}"; do
    agent="${MAINPC_AGENTS[$i]}"
    pane_idx=$((PANE_BASE + i))
    pane_target="multiagent:agents.${pane_idx}"
    print_agent_row "$agent" "$pane_target"
done

# SecondPC: 別 tmux session のため pane lookup 不可。task/inbox のみ。
for agent in "${SECONDPC_AGENTS[@]}"; do
    print_agent_row "$agent" ""
done

printf "\n"
