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

# ─── ★出目の規律★（委員長裁 seq337507⑶疵①「usage で閉ぢ rc を分けよ」）───
#   rc=0 … 測れた（`--help` も 0）
#   rc=1 … ★使ひ方の誤★ = 呼び手の argv が誤つて居る
#           （未知の旗 / 値を取る旗に値が無い / 値が空 / 値が旗に見える /
#             session 名が当たらぬ / --panes に該当無 / tmux 外で --session 無し）
#   rc=2 … ★器の死★ = 呼び手に非は無く、機に走る物が無い
#           （tmux が機に無い / 共用 lib が読めぬ）
# ★据ゑる前の実測★(docs/evidence/karo-mac_agent-status-kizu1-usage-rc-wakatsu-20260919/raw/50_before.txt):
#   ㋓㋔㋕ 値が無いと `line 28: $2: unbound variable` が出て rc=1 ―― usage は出ぬ。
#   ㋙ 未知の旗も rc=1 ∴ ★呼び手の誤りと器の死が同じ出目に潰れて居た★。
#   ㋖ `--lang ""`      → rc=0（黙つて空の言語）
#   ㋗ `--session ""`   → rc=0（★黙つて現用 session へ倒れた★＝別の物を測る）
#   ㋘ `--lang --session` → rc=0（値を食はれ project 路へ倒れた）
readonly KM_RC_OK=0
readonly KM_RC_USAGE=1
readonly KM_RC_KIKI=2

# ★使ひ方★ ―― 誤りは stderr へ、`--help` は stdout へ（$1 = 1 か 2）
km_usage() {
    local fd="${1:-1}"
    {
        echo "Usage: agent_status.sh [--session NAME] [--panes 0,1,2] [--lang en|ja]"
        echo ""
        echo "Options:"
        echo "  --session NAME   Tmux session to scan (default: auto-detect)"
        echo "  --panes N,N,N    Comma-separated pane indices to check"
        echo "  --lang en|ja     Output language (default: ja)"
        echo ""
        echo "Without options, reads config/settings.yaml for agent definitions."
        echo ""
        echo "Exit codes:"
        echo "  0  measured"
        echo "  ${KM_RC_USAGE}  usage error: unknown flag / missing or empty value / no such session"
        echo "  ${KM_RC_KIKI}  instrument unusable: tmux absent / shared lib unreadable"
    } >&"$fd"
}

# ★値を取る旗を検める★ ―― 値が無い時に $2 を触つてはならぬ（set -u で shell が死ぬ）
#   $1=旗の名 / $2=残りの引数の数($#) / $3=次の語（無ければ空）
km_need_value() {
    local flag="$1" argc="$2" nxt="${3-}"
    if [[ "$argc" -lt 2 ]]; then
        echo "Error: ${flag} は値を要るが、値が無い" >&2
        km_usage 2
        return 1
    fi
    if [[ -z "$nxt" ]]; then
        echo "Error: ${flag} の値が空である（黙つて既定へ倒さぬ）" >&2
        km_usage 2
        return 1
    fi
    case "$nxt" in
        --*)
            echo "Error: ${flag} の値が旗に見える（'${nxt}'）―― 値を落として居らぬか" >&2
            km_usage 2
            return 1
            ;;
    esac
    return 0
}

# ─── Parse args ───
while [[ $# -gt 0 ]]; do
    case "$1" in
        --lang)
            km_need_value --lang "$#" "${2-}" || exit "$KM_RC_USAGE"
            LANG_MODE="$2"; shift 2 ;;
        --session)
            km_need_value --session "$#" "${2-}" || exit "$KM_RC_USAGE"
            SESSION_NAME="$2"; STANDALONE=true; shift 2 ;;
        --panes)
            km_need_value --panes "$#" "${2-}" || exit "$KM_RC_USAGE"
            MANUAL_PANES="$2"; STANDALONE=true; shift 2 ;;
        --help|-h)
            km_usage 1
            exit "$KM_RC_OK"
            ;;
        *)
            # ★誤りは stderr へ★（旧形は stdout へ出して居た＝出を集める器が黙つて呑む）
            echo "Error: 未知の旗: $1" >&2
            km_usage 2
            exit "$KM_RC_USAGE"
            ;;
    esac
done

# ─── ★器の死★ 其の一: tmux が機に無い（裁337507⑶疵①「器の死=2」）───
# 実測(raw/51_tmux_fuzai_project.txt ―― tmux のみを PATH から抜いた・据ゑる前):
#   ⑴ standalone 路 → rc=1「session 'multiagent-mac' は完全一致で存在せぬ」＝★偽の因★
#      （session は在る。無いのは器である。呼び手の argv を咎めて居た）
#   ⑵ project 路    → ★rc=0★ で表を刷る。表の中身は正直（Pane=不在・Status=---・
#      母數行が「的: @agent_idで解けた=0 / 寫像不能(session無)=6」と宣す）が、
#      ★何一つ測れて居らぬのに「通」を返す★。rc だけを読む呼び手は「正常」と解す。
# ∴ 門を入口に立て rc=2 で止める。★此処は 2>/dev/null で呑まぬ★。
if ! command -v tmux >/dev/null 2>&1; then
    echo "Error: tmux が機に無い ―― 本器は tmux の pane を測る物ゆゑ何も測れぬ" >&2
    echo "       （呼び手の誤りではない。rc=${KM_RC_KIKI} ＝ 器の死）" >&2
    exit "$KM_RC_KIKI"
fi

# ─── ★器の死★ 其の二: 共用 lib が読めぬ ───
# 旧形は `source` が失敗すると set -e で rc=1 ＝★使ひ方の誤と同じ顔★に成つて居た。
for _lib in "$SCRIPT_DIR/lib/agent_status.sh" "$SCRIPT_DIR/lib/_section18_roles.sh"; do
    if [[ ! -r "$_lib" ]]; then
        echo "Error: 共用 lib が読めぬ: ${_lib}" >&2
        echo "       （呼び手の誤りではない。rc=${KM_RC_KIKI} ＝ 器の死）" >&2
        exit "$KM_RC_KIKI"
    fi
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
            3) echo "AMBIG" ;;
        esac
    else
        case $rc in
            0) echo "稼働中" ;;
            1) echo "待機中" ;;
            2) echo "不在" ;;
            3) echo "曖昧" ;;
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
            exit "$KM_RC_USAGE"   # ★使ひ方の誤★（値は旧と同じ 1・振舞は変へぬ）
        fi
    fi

    # ─── ★session は完全一致で検める★（裁337507⑶疵② 同類・standalone 路）───
    # 実測(2026-09-19 当機): `--session multiagent` は当機に無い名だが tmux が
    # multiagent-mac へ★前方一致し rc=0 で他 session の四席を刷つて居た★（偽の通）。
    # `=名` は has-session では効く（list-panes では効かぬ）∴ 門は has-session で立てる。
    if ! tmux has-session -t "=${SESSION_NAME}" 2>/dev/null; then
        echo "Error: session '${SESSION_NAME}' は完全一致で存在せぬ（前方一致では当てぬ）" >&2
        exit "$KM_RC_USAGE"   # ★使ひ方の誤★（値は旧と同じ 1）
    fi

    # Determine panes — ★的は pane_id(%N)★・見出しのみ session:window.pane
    # （display-message は不在の的でも rc=0 を返し現用 pane へ倒れる ∴ 的に名は使はぬ）
    declare -a PANE_IDS=()
    declare -a PANE_LABELS=()
    while IFS="$(printf '\t')" read -r _pid _label; do
        [[ -z "$_pid" ]] && continue
        if [[ -n "$MANUAL_PANES" ]]; then
            case ",${MANUAL_PANES}," in
                *",${_label##*.},"*) ;;
                *) continue ;;
            esac
        fi
        PANE_IDS+=("$_pid"); PANE_LABELS+=("$_label")
    done < <(tmux list-panes -a -F '#{pane_id}	#{session_name}:#{window_name}.#{pane_index}	#{session_name}' 2>/dev/null \
             | awk -F'\t' -v s="$SESSION_NAME" '$3==s {print $1 "\t" $2}')

    # ★bash 3.2 は空配列の "${a[@]}" が set -u で死ぬ★
    # （実測 旧版: 無い名を与へると `PANE_TARGETS[@]: unbound variable` で rc=1・表の冠は既に出て居た）
    if [[ ${#PANE_IDS[@]} -eq 0 ]]; then
        echo "Error: session '${SESSION_NAME}' に該当する pane が無い（--panes の指定を含む）" >&2
        exit "$KM_RC_USAGE"   # ★使ひ方の誤★（値は旧と同じ 1）
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

    for _i in "${!PANE_IDS[@]}"; do
        pane_target="${PANE_IDS[$_i]}"        # ★%N★
        pane_label="${PANE_LABELS[$_i]}"
        # Try reading @agent_id from the pane
        agent_id=$(timeout 2 tmux display-message -t "$pane_target" -p '#{@agent_id}' 2>/dev/null || echo "---")
        [[ -z "$agent_id" ]] && agent_id="---"

        agent_is_busy_check "$pane_target" && rc=0 || rc=$?
        label=$(state_label "$rc")

        print_padded "$pane_label" 30
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
# ★此の 2>/dev/null は外さぬ★（命⑶ 後段・理由）―― 黙つて数を偽る類ではない。
# 下の三つ（session 名・pane 一覧・@agent_id）も同じ理由で残す。帳の parse とは別の事である。
# ★2026-09-19 追随（裁337507⑶疵①）★ ―― 旧註は「tmux が無い所（CI・素の shell）で
# 走る事が設計上の並(standalone mode)」と書いて居たが、★実装が変はつた★:
# tmux 不在は★入口の門で rc=2（器の死）として止まる★（上の km_need_value の下）。
# ∴ 此処へ到る時 tmux は★必ず在る★。此の `|| echo 0` が覆ふのは
# 「tmux は在るが pane-base-index が未設定」の場合★のみ★である。
PANE_BASE=$(tmux show-options -gv pane-base-index 2>/dev/null || echo 0)

# ─── ★的は @agent_id の完全一致で解く★（委員長裁 seq337507⑶ 疵② / 同 337482 採用形）───
# 実測(2026-09-19 当機 tmux 3.7b ―― 推さず測つた):
#   ⑴ `-t =名` は has-session では効く(rc=1)が、★list-panes では効かぬ★
#      (`list-panes -s -t =multiagent` が rc=0 で multiagent-mac の四席を返す。
#       誤りの字面が "can't find window" ゆゑ window 的と解され session 部へ掛からぬ)
#   ⑵ display-message は★不在の的でも rc=0★（`-t %99999` も rc=0）。
#      更に窓/pane が外れると★其の session の現用 pane へ黙つて倒れる★
#      (`-t multiagent:agents.4` → %7 = 別席の生席)。∴ rc で不在を判じてはならぬ。
#   ∴ 信ずるに足る形は ★pane_id(%N)★ のみ。悉皆列挙して @agent_id で一致を取る。
# 出目: 0=一件のみ(pane_id を stdout へ) / 3=★二件以上=曖昧ゆゑ当てぬ★ / 1=零件
km_pane_id_by_agent_id() {
    local want="$1" ids n
    ids=$(tmux list-panes -a -F '#{pane_id} #{@agent_id}' 2>/dev/null \
          | awk -v w="$want" '$2==w {print $1}') || true
    [[ -z "$ids" ]] && return 1
    n=$(printf '%s\n' "$ids" | awk 'END{print NR}')
    if [[ "$n" -ne 1 ]]; then
        return 3
    fi
    printf '%s' "$ids"
    return 0
}

# ─── 顔の度數 ―― ★母數 = 歩いた席の数★（委員長裁 seq336105⑷ / no-silent-failure §4）───
# 「帳が無い」「parse が通らぬ」「弾が無い」は ★別の事★ である。一つの「---」へ畳まぬ。
N_SEKI=0; N_YOMETA=0; N_NOTAMA=0; N_NOFILE=0; N_PARSE_NG=0
N_NOPY=0; N_SHAPE=0; N_READERR=0; N_PYDIE=0; N_BOX_NG=0; N_MULTI=0
# ─── 的（pane）の顔の度數 ―― ★「席が無い」と「的が曖昧」と「寫像が使へぬ」は別の事★
N_BYID=0; N_AMBIG=0; N_NOSESS=0; N_NOPANE=0

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
#       $3=強ひる出目（任意・"" なら実測する）―― ★3=曖昧★ を「不在」に畳まぬ為
print_agent_row() {
    local agent="$1"
    local pane_target="$2"
    local forced_rc="${3:-}"

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
    if [[ -n "$forced_rc" ]]; then
        rc="$forced_rc"
    elif [[ -n "$pane_target" ]]; then
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

# ─── MainPC: ★固定寫像＋前方一致を廃す★（委員長裁 seq337507⑶ 疵② ―― 最優先）───
# 旧: pane_target="multiagent:agents.${pane_idx}"
#   当機に session `multiagent` は無く `multiagent-mac` のみ在る。tmux の -t は前方一致ゆゑ
#   ★六行 悉く別レーンの生席へ当たつて居た★（実測 2026-09-19T13:07:49+0900）:
#     0→%68 家老mac / 1→%72 專任1 / 2→%7 專任2 / 3→%125 專任3 /
#     4→%7・5→%7（index 不在ゆゑ現用 pane へ倒れ、capture だけ rc=1 ∴ ★偽の待機中★）
# 新: ①@agent_id 完全一致→%N ②二件以上=★曖昧ゆゑ当てぬ★ ③零件は固定寫像へ倒れる前に
#     session の完全一致(=名 は has-session では効く)と index の実在を列挙で検め、
#     満たさねば ★不在★ で止まる(fail-closed)。★前方一致の的は一つも作らぬ。★
FIXED_SESSION="multiagent"
FIXED_SESSION_OK=false
if tmux has-session -t "=${FIXED_SESSION}" 2>/dev/null; then
    FIXED_SESSION_OK=true
fi
for i in "${!MAINPC_AGENTS[@]}"; do
    agent="${MAINPC_AGENTS[$i]}"
    pane_idx=$((PANE_BASE + i))
    pane_target=""
    forced_rc=""
    rc_res=0
    pane_target=$(km_pane_id_by_agent_id "$agent" 2>/dev/null) || rc_res=$?
    if [[ "$rc_res" -eq 0 ]]; then
        N_BYID=$((N_BYID + 1))
    elif [[ "$rc_res" -eq 3 ]]; then
        # ★二件以上★ = 当てれば別席を撃ち得る ∴ 的を作らぬ（曖昧の顔で刷る）
        N_AMBIG=$((N_AMBIG + 1)); pane_target=""; forced_rc=3
    else
        pane_target=""
        if $FIXED_SESSION_OK; then
            # session が★完全一致で在る★時のみ寫像を使ふ。index の実在も列挙で検める
            # （display-message の rc は不在を判じられぬ ―― 上の実測⑵）
            pane_target=$(tmux list-panes -a -F '#{session_name} #{window_name} #{pane_index} #{pane_id}' 2>/dev/null \
                | awk -v s="$FIXED_SESSION" -v x="$pane_idx" '$1==s && $2=="agents" && $3==x {print $4; exit}') || true
            if [[ -z "$pane_target" ]]; then
                N_NOPANE=$((N_NOPANE + 1))
            fi
        else
            N_NOSESS=$((N_NOSESS + 1))
        fi
    fi
    print_agent_row "$agent" "$pane_target" "$forced_rc"
done

# SecondPC: 別 tmux session のため pane lookup 不可。task/inbox のみ。
for agent in "${SECONDPC_AGENTS[@]}"; do
    print_agent_row "$agent" ""
done

printf "\n"

# ─── 結語 ―― ★母數と parse 不能の数を刷る★（命⑴）。表を崩さぬ為 stderr へ出す（命⑵）。
printf '[agent_status] ★母數★ 歩いた席=%d ／ 帳: 讀めた=%d 弾無=%d 帳無=%d ★parse不能=%d★ 形違=%d 讀めぬ=%d 器無=%d 器落=%d ★多鍵形=%d★ ／ 箱: 数に非ざる顔=%d ／ 的: @agent_idで解けた=%d ★曖昧=%d★ 寫像不能(session無)=%d 寫像不能(pane無)=%d\n' \
    "$N_SEKI" "$N_YOMETA" "$N_NOTAMA" "$N_NOFILE" "$N_PARSE_NG" \
    "$N_SHAPE" "$N_READERR" "$N_NOPY" "$N_PYDIE" "$N_MULTI" "$N_BOX_NG" \
    "$N_BYID" "$N_AMBIG" "$N_NOSESS" "$N_NOPANE" >&2
if [[ $((N_PARSE_NG + N_SHAPE + N_READERR + N_PYDIE + N_MULTI + N_BOX_NG)) -gt 0 ]]; then
    printf '[agent_status] ★黙らぬ★ 上の顔は「弾が無い」ではない。★帳が読めて居らぬ★。\n' >&2
fi
if [[ "$N_AMBIG" -gt 0 ]]; then
    printf '[agent_status] ★黙らぬ★ @agent_id が二席以上に在る席が %d ―― 当てれば別席を撃ち得る ∴ ★当てなかつた★。\n' "$N_AMBIG" >&2
fi
