# -*- coding: utf-8 -*-
import io, hashlib
F="scripts/agent_status.sh"
s=io.open(F,encoding="utf-8").read()
print("前 sha256=%s 行=%d"%(hashlib.sha256(s.encode()).hexdigest(), s.count("\n")))
def rep(old,new,tag):
    global s
    n=s.count(old); assert n==1,"REFUSE %s hit=%d"%(tag,n)
    s=s.replace(old,new); print("  彫 %-10s hit=1"%tag)

rep('''    # Determine panes — collect all window:pane pairs across the session
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
''',
'''    # ─── ★session は完全一致で検める★（裁337507⑶疵② 同類・standalone 路）───
    # 実測(2026-09-19 当機): `--session multiagent` は当機に無い名だが tmux が
    # multiagent-mac へ★前方一致し rc=0 で他 session の四席を刷つて居た★（偽の通）。
    # `=名` は has-session では効く（list-panes では効かぬ）∴ 門は has-session で立てる。
    if ! tmux has-session -t "=${SESSION_NAME}" 2>/dev/null; then
        echo "Error: session '${SESSION_NAME}' は完全一致で存在せぬ（前方一致では当てぬ）" >&2
        exit 1
    fi

    # Determine panes — ★的は pane_id(%N)★・見出しのみ session:window.pane
    # （display-message は不在の的でも rc=0 を返し現用 pane へ倒れる ∴ 的に名は使はぬ）
    declare -a PANE_IDS=()
    declare -a PANE_LABELS=()
    while IFS="$(printf '\\t')" read -r _pid _label; do
        [[ -z "$_pid" ]] && continue
        if [[ -n "$MANUAL_PANES" ]]; then
            case ",${MANUAL_PANES}," in
                *",${_label##*.},"*) ;;
                *) continue ;;
            esac
        fi
        PANE_IDS+=("$_pid"); PANE_LABELS+=("$_label")
    done < <(tmux list-panes -a -F '#{pane_id}	#{session_name}:#{window_name}.#{pane_index}	#{session_name}' 2>/dev/null \\
             | awk -F'\\t' -v s="$SESSION_NAME" '$3==s {print $1 "\\t" $2}')

    # ★bash 3.2 は空配列の "${a[@]}" が set -u で死ぬ★
    # （実測 旧版: 無い名を与へると `PANE_TARGETS[@]: unbound variable` で rc=1・表の冠は既に出て居た）
    if [[ ${#PANE_IDS[@]} -eq 0 ]]; then
        echo "Error: session '${SESSION_NAME}' に該当する pane が無い（--panes の指定を含む）" >&2
        exit 1
    fi
''', "㋖門")

rep('''    for pane_target in "${PANE_TARGETS[@]}"; do
        # Try reading @agent_id from the pane
        agent_id=$(timeout 2 tmux display-message -t "$pane_target" -p '#{@agent_id}' 2>/dev/null || echo "---")
        [[ -z "$agent_id" ]] && agent_id="---"

        agent_is_busy_check "$pane_target" && rc=0 || rc=$?
        label=$(state_label "$rc")

        print_padded "$pane_target" 30''',
'''    for _i in "${!PANE_IDS[@]}"; do
        pane_target="${PANE_IDS[$_i]}"        # ★%N★
        pane_label="${PANE_LABELS[$_i]}"
        # Try reading @agent_id from the pane
        agent_id=$(timeout 2 tmux display-message -t "$pane_target" -p '#{@agent_id}' 2>/dev/null || echo "---")
        [[ -z "$agent_id" ]] && agent_id="---"

        agent_is_busy_check "$pane_target" && rc=0 || rc=$?
        label=$(state_label "$rc")

        print_padded "$pane_label" 30''', "㋖環")

io.open(F,"w",encoding="utf-8").write(s)
print("後 sha256=%s 行=%d byte=%d"%(hashlib.sha256(s.encode()).hexdigest(), s.count("\n"), len(s.encode())))
