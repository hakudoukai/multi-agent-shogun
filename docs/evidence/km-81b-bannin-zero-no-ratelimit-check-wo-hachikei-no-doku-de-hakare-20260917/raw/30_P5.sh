set -euo pipefail
TODAY=$(date +%Y-%m-%d)
CLAUDE_DATA_DATE=""
CLAUDE_TODAY_DETAIL=""
CLAUDE_SESSIONS=""
CLAUDE_MESSAGES=""
    if [[ "$CLAUDE_TODAY_TOTAL" -gt 0 ]]; then
        printf "  ── Tokens ──\n"
        if [[ "${CLAUDE_DATA_DATE:-$TODAY}" != "$TODAY" ]]; then
            printf "  Latest (%s): %'d tokens\n" "$CLAUDE_DATA_DATE" "$CLAUDE_TODAY_TOTAL"
        else
            printf "  Today: %'d tokens\n" "$CLAUDE_TODAY_TOTAL"
        fi
        if [[ -n "$CLAUDE_TODAY_DETAIL" ]]; then
            printf "    %s\n" "$CLAUDE_TODAY_DETAIL"
        fi
        printf "  Sessions: %s | Messages: %s\n" "$CLAUDE_SESSIONS" "$CLAUDE_MESSAGES"
    fi
printf "VALUE=[%s]\n" "${CLAUDE_TODAY_TOTAL-<unset>}"
