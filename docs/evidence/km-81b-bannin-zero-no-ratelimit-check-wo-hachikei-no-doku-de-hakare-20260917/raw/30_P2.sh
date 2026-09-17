set -euo pipefail
CODEX_CONTEXT_WARN=20
CODEX_CONTEXT_CRIT=10
CODEX_LIMIT_HITS_WARN=3
CODEX_WARNINGS=""
CODEX_STATUS="OK"
    CODEX_LIMIT_HITS="${CODEX_LIMIT_HITS:-0}"
    # Sanitize: strip whitespace, ensure integer
    CODEX_LIMIT_HITS=$(echo "$CODEX_LIMIT_HITS" | tr -d '[:space:]')
    [[ "$CODEX_LIMIT_HITS" =~ ^[0-9]+$ ]] || CODEX_LIMIT_HITS=0

    if [[ "$CODEX_LIMIT_HITS" -ge "$CODEX_LIMIT_HITS_WARN" ]]; then
        if [[ "$CODEX_STATUS" == "OK" ]]; then
            CODEX_STATUS="WARNING"
        fi
        CODEX_WARNINGS="${CODEX_WARNINGS} limit_hits=${CODEX_LIMIT_HITS}/h"
    fi
printf "STATUS=%s WARN=[%s] VALUE=[%s]\n" "$CODEX_STATUS" "$CODEX_WARNINGS" "${CODEX_LIMIT_HITS-<unset>}"
