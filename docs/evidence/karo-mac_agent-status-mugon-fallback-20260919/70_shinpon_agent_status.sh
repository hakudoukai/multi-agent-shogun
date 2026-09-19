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
# ★此の 2>/dev/null は外さぬ★（命⑶ 後段・理由）―― tmux が無い所（CI・素の shell）で
# 走る事が設計上の並(standalone mode)であり、其の時の「tmux 無し」は ★既に別の顔★
# （不在 / 0）を持つ。黙つて数を偽る類ではない。下の三つ（session 名・pane 一覧・
# @agent_id）も同じ理由で残す。帳の parse とは別の事である。
PANE_BASE=$(tmux show-options -gv pane-base-index 2>/dev/null || echo 0)

# ─── 顔の度數 ―― ★母數 = 歩いた席の数★（委員長裁 seq336105⑷ / no-silent-failure §4）───
# 「帳が無い」「parse が通らぬ」「弾が無い」は ★別の事★ である。一つの「---」へ畳まぬ。
N_SEKI=0; N_YOMETA=0; N_NOTAMA=0; N_NOFILE=0; N_PARSE_NG=0
N_NOPY=0; N_SHAPE=0; N_READERR=0; N_PYDIE=0; N_BOX_NG=0; N_MULTI=0

# ─── Helper: task info from YAML ───
# ★出目は常に二欄（task_id / status）★。顔は悉く ASCII で書く ―― printf の %-42s は
# 和字を byte で数へる為、和字の顔は表の桁組みを崩す（命⑵「出目の路を崩すな」）。
#   (no-file)    帳が無い
#   (parse-fail) 帳は在るが yaml として読めぬ   ← 之を「無」に混ぜて居たのが本弾の疵
#   (bad-shape)  読めたが頂が写像に非ず
#   (read-err)   開けぬ（権限・I/O）
#   (no-python)  器（.venv の python3）が無い
#   (py-die)     python が非零で落ちた
#   (multi:A/N)  帳は読めたが頂に task 鍵が無い ★多鍵形★（assigned=A本 / 弾鍵=N本）
#                ← 旧弾は之を黙つて頂の旧形 task_id へ倒し、★古い一組を今の弾と偽つて居た★
#   --- ---      ★帳は在り parse も通り、其の上で弾が無い★
get_task_info() {
    local agent_id="$1"
    local yaml_file="$SCRIPT_DIR/queue/tasks/${agent_id}.yaml"
    if ! $PYTHON_AVAILABLE; then
        echo "(no-python) ---"
        return
    fi
    if [[ ! -f "$yaml_file" ]]; then
        echo "(no-file) ---"
        return
    fi
    # ★2>/dev/null を外した★（命⑶）―― 鳴りは stderr へ。表（stdout）は一字も変へぬ。
    "$PYTHON" -c "
import sys, yaml
p = '${yaml_file}'
try:
    with open(p) as f:
        data = yaml.safe_load(f)
except yaml.YAMLError as e:
    sys.stderr.write('[agent_status] parse-fail %s: %s\n' % (p, str(e).replace('\n', ' ')[:200]))
    print('(parse-fail) !'); sys.exit(0)
except OSError as e:
    sys.stderr.write('[agent_status] read-err %s: %s\n' % (p, e))
    print('(read-err) !'); sys.exit(0)
if data is None:
    print('--- ---'); sys.exit(0)
if not isinstance(data, dict):
    sys.stderr.write('[agent_status] bad-shape %s: top is %s\n' % (p, type(data).__name__))
    print('(bad-shape) !'); sys.exit(0)
if 'task' in data:
    task = data['task']
else:
    # ★無言の代入を止めた★（委員長裁 seq337393⑴ / 「意味が変はる fallback を無言で行ふな」）
    # 旧: task = data.get('task', data)
    # 実測 2026-09-19（両対照）―― 此の fallback が刷つて居たのは「弾無 --- ---」ではない。
    # 帳の頂には旧形の欄（task_id / status / priority / assigned_at）が居坐つて居り、
    # ★其の古い一組を「今の弾」として刷つて居た★。
    #   席2: 頂=km-117…/done ―― 其の時 弾鍵25本中 ★assigned が3本★ 走つて居た
    #   席3: 頂=km-113…/done ―― 同 29本中 ★assigned が2本★
    # ∴ 症は「読めぬ」ではなく ★尤もらしい偽値★ であり、之が最も悪い顔である。
    # 何れの弾を「今の弾」と選ぶかは ★政策★ ゆゑ器が選んではならぬ。器は ★測つた数★ を出す。
    tamakagi = [k for k, v in data.items() if isinstance(v, dict) and 'task_id' in v]
    asg = [k for k in tamakagi if data[k].get('status') == 'assigned']
    sys.stderr.write('[agent_status] multi-key %s: 頂に task 鍵無し・多鍵形（頂の鍵=%d本 弾鍵=%d本 assigned=%d本）―― ★頂の旧形 task_id=%r status=%r は今の弾に非ず・用ゐぬ★\n' % (p, len(data), len(tamakagi), len(asg), data.get('task_id'), data.get('status')))
    print('(multi:%d/%d) !' % (len(asg), len(tamakagi))); sys.exit(0)
if not isinstance(task, dict):
    sys.stderr.write('[agent_status] bad-shape %s: task is %s\n' % (p, type(task).__name__))
    print('(bad-shape) !'); sys.exit(0)
print('%s %s' % (task.get('task_id', '---'), task.get('status', '---')))
" || echo "(py-die) !"
}

# ─── Helper: unread inbox count ───
get_unread_count() {
    local agent_id="$1"
    local inbox_file="$SCRIPT_DIR/queue/inbox/${agent_id}.yaml"
    if ! $PYTHON_AVAILABLE; then
        echo "P"
        return
    fi
    if [[ ! -f "$inbox_file" ]]; then
        echo "-"
        return
    fi
    # ★2>/dev/null を外した★（命⑶）。箱の顔: -=箱無 !=parse不能 S=形違 E=讀めぬ P=器無 X=器落
    "$PYTHON" -c "
import sys, yaml
p = '${inbox_file}'
try:
    with open(p) as f:
        data = yaml.safe_load(f)
except yaml.YAMLError as e:
    sys.stderr.write('[agent_status] parse-fail %s: %s\n' % (p, str(e).replace('\n', ' ')[:200]))
    print('!'); sys.exit(0)
except OSError as e:
    sys.stderr.write('[agent_status] read-err %s: %s\n' % (p, e))
    print('E'); sys.exit(0)
if data is None:
    print(0); sys.exit(0)
if not isinstance(data, dict):
    sys.stderr.write('[agent_status] bad-shape %s: top is %s\n' % (p, type(data).__name__))
    print('S'); sys.exit(0)
msgs = data.get('messages', [])
if not isinstance(msgs, list):
    sys.stderr.write('[agent_status] bad-shape %s: messages is %s\n' % (p, type(msgs).__name__))
    print('S'); sys.exit(0)
print(sum(1 for m in msgs if isinstance(m, dict) and not m.get('read', False)))
" || echo "X"
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
        # ★2>/dev/null を外した★（命⑶）―― 黙つて「?」に成るのを止める。
        cli_type=$(get_cli_type "$agent" || echo "?")
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

    # ─── 顔の度數を刻む（母數は歩いた席の数）───
    # ★$(...) は子の殻ゆゑ get_task_info の中では数へられぬ★ ∴ 呼んだ側で数へる。
    # ★x=$((x+1)) と書く★ ―― ((x++)) は結果が 0 の時 rc=1 を返し set -e で死ぬ。
    N_SEKI=$((N_SEKI + 1))
    case "$task_id" in
        "(parse-fail)") N_PARSE_NG=$((N_PARSE_NG + 1)) ;;
        "(no-file)")    N_NOFILE=$((N_NOFILE + 1)) ;;
        "(no-python)")  N_NOPY=$((N_NOPY + 1)) ;;
        "(bad-shape)")  N_SHAPE=$((N_SHAPE + 1)) ;;
        "(read-err)")   N_READERR=$((N_READERR + 1)) ;;
        "(py-die)")     N_PYDIE=$((N_PYDIE + 1)) ;;
        "(multi:"*)     N_MULTI=$((N_MULTI + 1)) ;;
        "---")          N_NOTAMA=$((N_NOTAMA + 1)) ;;
        *)              N_YOMETA=$((N_YOMETA + 1)) ;;
    esac

    # Unread inbox
    local unread
    unread=$(get_unread_count "$agent")
    case "$unread" in
        "!"|"S"|"E"|"P"|"X") N_BOX_NG=$((N_BOX_NG + 1)) ;;
    esac

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

# ─── 結語 ―― ★母數と parse 不能の数を刷る★（命⑴）。表を崩さぬ為 stderr へ出す（命⑵）。
printf '[agent_status] ★母數★ 歩いた席=%d ／ 帳: 讀めた=%d 弾無=%d 帳無=%d ★parse不能=%d★ 形違=%d 讀めぬ=%d 器無=%d 器落=%d ★多鍵形=%d★ ／ 箱: 数に非ざる顔=%d\n' \
    "$N_SEKI" "$N_YOMETA" "$N_NOTAMA" "$N_NOFILE" "$N_PARSE_NG" \
    "$N_SHAPE" "$N_READERR" "$N_NOPY" "$N_PYDIE" "$N_MULTI" "$N_BOX_NG" >&2
if [[ $((N_PARSE_NG + N_SHAPE + N_READERR + N_PYDIE + N_MULTI + N_BOX_NG)) -gt 0 ]]; then
    printf '[agent_status] ★黙らぬ★ 上の顔は「弾が無い」ではない。★帳が読めて居らぬ★。\n' >&2
fi
