set -euo pipefail
CODEX_CONTEXT_WARN=20
CODEX_CONTEXT_CRIT=10
CODEX_LIMIT_HITS_WARN=3
CODEX_WARNINGS=""
CODEX_STATUS="OK"
agent=ashigaru9
[[ -z "$ctx" ]] && ctx="?"
        if [[ "$ctx" != "?" ]]; then
            if [[ "$ctx" -lt "$CODEX_CONTEXT_CRIT" ]]; then
                CODEX_WARNINGS="${CODEX_WARNINGS} ${agent}(${ctx}%)!!"
                CODEX_STATUS="CRITICAL"
            elif [[ "$ctx" -lt "$CODEX_CONTEXT_WARN" ]]; then
                CODEX_WARNINGS="${CODEX_WARNINGS} ${agent}(${ctx}%)!"
                if [[ "$CODEX_STATUS" != "CRITICAL" ]]; then
                    CODEX_STATUS="WARNING"
                fi
            fi
        fi
printf "STATUS=%s WARN=[%s] VALUE=[%s]\n" "$CODEX_STATUS" "$CODEX_WARNINGS" "${ctx-<unset>}"
