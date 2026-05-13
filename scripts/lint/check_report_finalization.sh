#!/usr/bin/env bash
# check_report_finalization.sh — completion-claim sections に未確定 token 残存があれば exit 1
#
# 設計書: docs/report_finalization_norm.md
# 関連: queue/tasks/subtask_cmd020_scope_contamination_prevention_v2.yaml AC5
#
# Scope (= 完遂主張部のみ):
#   ^commit_history:
#   ^push_plan:
#   ^acceptance_criteria:
#   ^next_actions:
#
# Forbidden tokens (= 完遂主張部に出現したら未確定):
#   TBD, TBD_SHA, pending, 予定, planned, in_progress
#
# Allowlist (= status taxonomy enum / 履歴 / 引用は exempt):
#   scripts/lint/report_finalization_allowlist.txt の substring 列、line 内に出現すれば skip
#
# Invocation:
#   bash scripts/lint/check_report_finalization.sh <report.yaml> [<report2.yaml> ...]
#
# Exit code:
#   0 = pass (= 全 report で完遂主張部 clean)
#   1 = fail (= 1 件以上で flagged)
#   2 = usage error

set -uo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
ALLOWLIST="${REPORT_FINALIZATION_ALLOWLIST:-${REPO_ROOT}/scripts/lint/report_finalization_allowlist.txt}"

if [ $# -lt 1 ]; then
    echo "[check_report_finalization] usage: $0 <report.yaml> [...]" >&2
    exit 2
fi

SCOPED_SECTIONS_REGEX='^(commit_history|push_plan|acceptance_criteria|next_actions):'
# 部分一致: TBD/pending は接尾辞 (= _SHA_3, _audit, _user_sashihai 等) 込みで検出
FORBIDDEN_REGEX='(TBD[A-Z0-9_]*|pending[a-z_]*|\bplanned\b|\bin_progress\b|予定)'
# Semantic stale state guard (= push_plan.status が将来 push 待ち状態のまま commit_history に確定 SHA
# が存在 → 完遂主張と矛盾、d1a2ff1 post-audit findings[0] root cause)。
# 既 forbidden token regex (pending[a-z_]*) では捕捉できない `ready_for_bounded_push` 等を補足。
SEMANTIC_STALE_STATES_REGEX='\b(ready_for_bounded_push|awaiting_bounded_push|awaiting_push|requires_sha_backfill|requires_backfill|ready_for_push)\b'
# commit_history 内 resolved SHA = 7-40 桁 hex (= short / full SHA 両対応)
RESOLVED_SHA_REGEX='\bsha:[[:space:]]*[0-9a-f]{7,40}\b'

load_allowlist_into_var() {
    local file="$1"
    [ -f "$file" ] || return
    awk '
        /^[[:space:]]*#/ { next }
        /^[[:space:]]*$/ { next }
        { print }
    ' "$file"
}

ALLOWLIST_PATTERNS=()
while IFS= read -r line; do
    [ -n "$line" ] && ALLOWLIST_PATTERNS+=("$line")
done < <(load_allowlist_into_var "$ALLOWLIST")

is_allowlisted() {
    local line="$1"
    for pat in "${ALLOWLIST_PATTERNS[@]}"; do
        if echo "$line" | grep -Eq -- "$pat"; then
            return 0
        fi
    done
    return 1
}

scan_report() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "[check_report_finalization] file not found: $file" >&2
        return 1
    fi
    local in_scope=0
    local current_section=""
    local lineno=0
    local found=0
    # Semantic stale guard state (= 2-pass artifact: collect during scan, evaluate at end)
    local has_resolved_sha=0
    local stale_status_line=""
    local stale_status_lineno=0
    while IFS= read -r line; do
        lineno=$((lineno+1))
        # New top-level section
        if [[ "$line" =~ ^[a-z_][a-z0-9_]*: ]]; then
            if [[ "$line" =~ $SCOPED_SECTIONS_REGEX ]]; then
                in_scope=1
                current_section="${line%%:*}"
            else
                in_scope=0
                current_section=""
            fi
            continue
        fi
        if [ "$in_scope" -eq 0 ]; then
            continue
        fi
        # Strip inline comments
        local clean
        clean=$(echo "$line" | sed 's/[[:space:]]*#.*$//')
        # Semantic stale guard: collect commit_history resolved SHA + push_plan.status stale-state
        if [ "$current_section" = "commit_history" ]; then
            if echo "$clean" | grep -Eq -- "$RESOLVED_SHA_REGEX"; then
                has_resolved_sha=1
            fi
        elif [ "$current_section" = "push_plan" ]; then
            if echo "$clean" | grep -Eq -- '^[[:space:]]*status:[[:space:]]*'"$SEMANTIC_STALE_STATES_REGEX"; then
                if ! is_allowlisted "$clean"; then
                    stale_status_line="$line"
                    stale_status_lineno="$lineno"
                fi
            fi
        fi
        # Forbidden token check (= existing path)
        if echo "$clean" | grep -Eq -- "$FORBIDDEN_REGEX"; then
            if is_allowlisted "$clean"; then
                continue
            fi
            echo "[check_report_finalization] FAIL $file:$lineno [$current_section] $line" >&2
            found=1
        fi
    done < "$file"
    # Semantic stale guard evaluate (= 確定 SHA 存在時に stale state 残存 → fail)
    if [ "$has_resolved_sha" -eq 1 ] && [ -n "$stale_status_line" ]; then
        echo "[check_report_finalization] FAIL $file:$stale_status_lineno [push_plan semantic_stale_guard] $stale_status_line" >&2
        echo "[check_report_finalization]   reason: push_plan.status remains a future-push state while commit_history contains resolved SHAs (= post-push completion-claim stale)" >&2
        found=1
    fi
    return "$found"
}

EXIT_CODE=0
for f in "$@"; do
    if ! scan_report "$f"; then
        EXIT_CODE=1
    fi
done

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "[check_report_finalization] OK — completion-claim sections clean for $# file(s)"
fi

exit "$EXIT_CODE"
