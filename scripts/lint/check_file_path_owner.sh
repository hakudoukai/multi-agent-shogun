#!/usr/bin/env bash
# check_file_path_owner.sh — scope contamination prevention (= cmd_020 ashigaru2 v2 redesign)
#
# 設計書: docs/cmd020_scope_contamination_v2_incident_root_cause.md §4
#         docs/scope_contamination_prevention.md §3.2 (= 旧設計の置換)
#
# 旧 check_staged_residual.sh 設計欠陥 (= 直政 post-audit msg_20260513_135950):
#   pre-commit framework が staged 全件を $@ として渡す → commit_set ⊇ staged_set 常成立 →
#   residual_set = staged_set - commit_set 常空 → 元事故 (= 他 agent staged 巻取り) 検出不能。
#
# 本 hook の構造的解決:
#   1. 各 staged file の owner を file path pattern から決定 (= 集合差廃棄、path-based 帰属判定)
#   2. 現 agent ID は tmux pane @agent_id を primary、git config user.name は fallback only
#      (= 共有 git config の last-write-wins race を構造回避)
#   3. owner ≠ 現 agent + shared 未許可 → reject (= ashigaru) / warning (= karo/gunshi/shogun)
#   4. 共有 file の authorize は task manifest の shared_files_allowlist field 経由 (= karo-only 廃棄)
#
# Invocation:
#   - .git/hooks/pre-commit shim 経由 (= scripts/install_pre_commit_hook.sh で install)
#   - 直接実行可能 (= 引数不要、git diff --cached --name-only で staged 検出)
#
# Env override:
#   SCOPE_CONTAMINATION_LINT_MODE=strict|warn  (default: strict)
#     strict: shared file 未許可で reject
#     warn:   shared file 未許可は warning 出力のみ pass (= 移行期 / CI debug 用)
#   PRE_COMMIT_AGENT_ID=<agent_id>            (test fixtures override)
#
# Exit code:
#   0 = pass (= 全 staged file owner ∈ {current_agent, allowlisted_shared}、or warn-only mode)
#   1 = reject (= 外部 owner staged あり、or shared 未許可 in strict mode for ashigaru)

set -uo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [ -z "$REPO_ROOT" ]; then
    echo "[check_file_path_owner] not inside git work tree (= graceful skip)" >&2
    exit 0
fi

LINT_MODE="${SCOPE_CONTAMINATION_LINT_MODE:-strict}"

# Identity resolution: tmux @agent_id primary, git config user.name fallback (with warning)
AGENT_ID="${PRE_COMMIT_AGENT_ID:-}"
IDENTITY_SOURCE="env_override"
if [ -z "$AGENT_ID" ] && [ -n "${TMUX_PANE:-}" ]; then
    AGENT_ID=$(tmux display-message -t "$TMUX_PANE" -p '#{@agent_id}' 2>/dev/null || true)
    IDENTITY_SOURCE="tmux_pane_agent_id"
fi
if [ -z "$AGENT_ID" ]; then
    AGENT_ID=$(git -C "$REPO_ROOT" config user.name 2>/dev/null || true)
    IDENTITY_SOURCE="git_config_fallback"
    case "$AGENT_ID" in
        shogun|karo|gunshi|ashigaru[1-9]) ;;
        "") ;;
        *)
            echo "[check_file_path_owner] WARNING: git config user.name='$AGENT_ID' is not a recognized agent_id (= last-write-wins race risk, tmux @agent_id 未設定)" >&2
            ;;
    esac
fi

if [ -z "$AGENT_ID" ]; then
    echo "[check_file_path_owner] agent_id unresolved (= TMUX_PANE + git config 双方 empty)、personal-dev mode pass" >&2
    exit 0
fi

# Role classification (= shared file 未許可時の reject/warn 判定)
case "$AGENT_ID" in
    ashigaru[1-9]) AGENT_ROLE="ashigaru" ;;
    karo|gunshi|shogun) AGENT_ROLE="orchestrator" ;;
    *)
        echo "[check_file_path_owner] WARNING: agent_id='$AGENT_ID' not in known whitelist、orchestrator role assumed" >&2
        AGENT_ROLE="orchestrator"
        ;;
esac

# Task manifest resolution
TASK_POINTER="$REPO_ROOT/queue/tasks/$AGENT_ID.yaml"
TASK_FILE=""
if [ -f "$TASK_POINTER" ]; then
    TASK_FILE=$(awk '
        /^[[:space:]]*task_file:/ {
            sub(/^[[:space:]]*task_file:[[:space:]]*/, "");
            gsub(/["'\''"]/, "");
            sub(/[[:space:]]*$/, "");
            print; exit
        }
    ' "$TASK_POINTER")
fi

# Allowlist extraction: shared_files_allowlist (flat list under top-level key)
ALLOWLIST_FILE=$(mktemp)
trap 'rm -f "$ALLOWLIST_FILE"' EXIT INT TERM

extract_allowlist() {
    local src="$1"
    [ -f "$src" ] || return
    awk '
        /^shared_files_allowlist:[[:space:]]*$/ { capture=1; next }
        /^shared_files_allowlist:[[:space:]]*\[/ {
            line=$0
            sub(/^shared_files_allowlist:[[:space:]]*\[/, "", line)
            sub(/\][[:space:]]*$/, "", line)
            n = split(line, arr, ",")
            for (i=1; i<=n; i++) {
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", arr[i])
                gsub(/["'\''"]/, "", arr[i])
                if (arr[i] != "") print arr[i]
            }
            next
        }
        capture && /^[[:space:]]*-[[:space:]]+/ {
            sub(/^[[:space:]]*-[[:space:]]+/, "")
            gsub(/["'\''"]/, "")
            sub(/[[:space:]]*$/, "")
            sub(/[[:space:]]*#.*$/, "")
            if ($0 != "") print
            next
        }
        capture && /^[^[:space:]#]/ { capture=0 }
    ' "$src"
}

extract_allowlist "$TASK_POINTER" >> "$ALLOWLIST_FILE"
if [ -n "$TASK_FILE" ] && [ -f "$REPO_ROOT/$TASK_FILE" ]; then
    extract_allowlist "$REPO_ROOT/$TASK_FILE" >> "$ALLOWLIST_FILE"
fi

is_in_allowlist() {
    local path="$1"
    [ -s "$ALLOWLIST_FILE" ] || return 1
    while IFS= read -r pattern; do
        [ -z "$pattern" ] && continue
        case "$path" in
            $pattern) return 0 ;;
        esac
    done < "$ALLOWLIST_FILE"
    return 1
}

# Owner classification by file path pattern
classify_owner() {
    local path="$1"
    case "$path" in
        queue/reports/ashigaru1_*|queue/reports/ashigaru1/*) echo "ashigaru1" ;;
        queue/reports/ashigaru2_*|queue/reports/ashigaru2/*) echo "ashigaru2" ;;
        queue/reports/ashigaru3_*|queue/reports/ashigaru3/*) echo "ashigaru3" ;;
        queue/reports/ashigaru4_*|queue/reports/ashigaru4/*) echo "ashigaru4" ;;
        queue/reports/ashigaru5_*|queue/reports/ashigaru5/*) echo "ashigaru5" ;;
        queue/reports/ashigaru6_*|queue/reports/ashigaru6/*) echo "ashigaru6" ;;
        queue/reports/ashigaru7_*|queue/reports/ashigaru7/*) echo "ashigaru7" ;;
        queue/reports/gunshi_*|queue/reports/naomasa_*|queue/reports/takenaka_*) echo "gunshi" ;;
        queue/reports/karo_*|queue/reports/honda_*|queue/reports/kuroda_*|queue/reports/acha_*) echo "karo" ;;
        queue/reports/shogun_*|queue/reports/nobunaga_*) echo "shogun" ;;
        queue/inbox/ashigaru1.yaml) echo "ashigaru1" ;;
        queue/inbox/ashigaru2.yaml) echo "ashigaru2" ;;
        queue/inbox/ashigaru3.yaml) echo "ashigaru3" ;;
        queue/inbox/ashigaru4.yaml) echo "ashigaru4" ;;
        queue/inbox/ashigaru5.yaml) echo "ashigaru5" ;;
        queue/inbox/ashigaru6.yaml) echo "ashigaru6" ;;
        queue/inbox/ashigaru7.yaml) echo "ashigaru7" ;;
        queue/inbox/karo.yaml)    echo "karo" ;;
        queue/inbox/gunshi.yaml)  echo "gunshi" ;;
        queue/inbox/shogun.yaml)  echo "shogun" ;;
        queue/tasks/ashigaru1.yaml) echo "ashigaru1" ;;
        queue/tasks/ashigaru2.yaml) echo "ashigaru2" ;;
        queue/tasks/ashigaru3.yaml) echo "ashigaru3" ;;
        queue/tasks/ashigaru4.yaml) echo "ashigaru4" ;;
        queue/tasks/ashigaru5.yaml) echo "ashigaru5" ;;
        queue/tasks/ashigaru6.yaml) echo "ashigaru6" ;;
        queue/tasks/ashigaru7.yaml) echo "ashigaru7" ;;
        queue/tasks/subtask_*)    echo "karo" ;;
        scripts/test/test_subtask_*_ashigaru1_*|scripts/test/test_*_ashigaru1_*) echo "ashigaru1" ;;
        scripts/test/test_subtask_*_ashigaru2_*|scripts/test/test_*_ashigaru2_*) echo "ashigaru2" ;;
        scripts/test/test_subtask_*_ashigaru3_*|scripts/test/test_*_ashigaru3_*) echo "ashigaru3" ;;
        scripts/test/test_subtask_*_ashigaru4_*|scripts/test/test_*_ashigaru4_*) echo "ashigaru4" ;;
        scripts/test/test_subtask_*_ashigaru5_*|scripts/test/test_*_ashigaru5_*) echo "ashigaru5" ;;
        scripts/test/test_subtask_*_ashigaru6_*|scripts/test/test_*_ashigaru6_*) echo "ashigaru6" ;;
        scripts/test/test_subtask_*_ashigaru7_*|scripts/test/test_*_ashigaru7_*) echo "ashigaru7" ;;
        *) echo "shared" ;;
    esac
}

# Staged set
STAGED_FILES=()
while IFS= read -r f; do
    [ -n "$f" ] && STAGED_FILES+=("$f")
done < <(git -C "$REPO_ROOT" diff --cached --name-only --diff-filter=ACMRD 2>/dev/null || true)

if [ ${#STAGED_FILES[@]} -eq 0 ]; then
    echo "[check_file_path_owner] no staged files (= pass、agent_id=$AGENT_ID source=$IDENTITY_SOURCE)" >&2
    exit 0
fi

CROSS_OWNER=()
UNAUTHORIZED_SHARED=()

for f in "${STAGED_FILES[@]}"; do
    owner=$(classify_owner "$f")
    if [ "$owner" = "shared" ]; then
        if is_in_allowlist "$f"; then
            continue
        else
            UNAUTHORIZED_SHARED+=("$f")
        fi
    elif [ "$owner" != "$AGENT_ID" ]; then
        CROSS_OWNER+=("$f<$owner>")
    fi
done

EXIT_CODE=0

if [ ${#CROSS_OWNER[@]} -gt 0 ]; then
    echo "[check_file_path_owner] REJECT cross-owner staged files (agent_id=$AGENT_ID source=$IDENTITY_SOURCE role=$AGENT_ROLE):" >&2
    for entry in "${CROSS_OWNER[@]}"; do
        path="${entry%<*}"
        owner="${entry##*<}"
        owner="${owner%>}"
        echo "  - $path (path-owner=$owner)" >&2
    done
    echo "[check_file_path_owner] unstage 経路: git restore --staged <path>" >&2
    echo "[check_file_path_owner] reference: docs/cmd020_scope_contamination_v2_incident_root_cause.md §4" >&2
    EXIT_CODE=1
fi

if [ ${#UNAUTHORIZED_SHARED[@]} -gt 0 ]; then
    case "$AGENT_ROLE:$LINT_MODE" in
        ashigaru:strict)
            echo "[check_file_path_owner] REJECT unauthorized shared edits (agent_id=$AGENT_ID role=ashigaru mode=strict):" >&2
            for f in "${UNAUTHORIZED_SHARED[@]}"; do echo "  - $f" >&2; done
            echo "[check_file_path_owner] authorize 経路: task YAML or queue/tasks/$AGENT_ID.yaml に shared_files_allowlist field を追加" >&2
            EXIT_CODE=1
            ;;
        *)
            echo "[check_file_path_owner] WARNING shared edits not in allowlist (agent_id=$AGENT_ID role=$AGENT_ROLE mode=$LINT_MODE):" >&2
            for f in "${UNAUTHORIZED_SHARED[@]}"; do echo "  - $f" >&2; done
            echo "[check_file_path_owner] strict 化 経路: SCOPE_CONTAMINATION_LINT_MODE=strict、または task YAML に shared_files_allowlist 追記" >&2
            ;;
    esac
fi

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "[check_file_path_owner] OK (agent_id=$AGENT_ID source=$IDENTITY_SOURCE role=$AGENT_ROLE mode=$LINT_MODE files=${#STAGED_FILES[@]})" >&2
fi

exit $EXIT_CODE
