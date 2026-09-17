set -euo pipefail
CLAUDE_STATUS="OK"
CLAUDE_5H_RESET=""
CLAUDE_7D_RESET=""
CLAUDE_7D_UTIL=10.0
    if [[ -n "$CLAUDE_5H_UTIL" && "$CLAUDE_5H_UTIL" != "?" ]]; then
        printf "  ── Quota ──\n"
        # 5-hour window
        fh_int=${CLAUDE_5H_UTIL%.*}
        if [[ "$fh_int" -ge 80 ]]; then
            printf "  5h window:  %s%% used ⚠️  (resets %s)\n" "$CLAUDE_5H_UTIL" "$CLAUDE_5H_RESET"
            CLAUDE_STATUS="WARNING (5h: ${CLAUDE_5H_UTIL}%)"
        else
            printf "  5h window:  %s%% used  (resets %s)\n" "$CLAUDE_5H_UTIL" "$CLAUDE_5H_RESET"
        fi
        # 7-day window
        sd_int=${CLAUDE_7D_UTIL%.*}
        if [[ "$sd_int" -ge 80 ]]; then
            printf "  7d window:  %s%% used ⚠️  (resets %s)\n" "$CLAUDE_7D_UTIL" "$CLAUDE_7D_RESET"
            CLAUDE_STATUS="WARNING (7d: ${CLAUDE_7D_UTIL}%)"
        else
            printf "  7d window:  %s%% used  (resets %s)\n" "$CLAUDE_7D_UTIL" "$CLAUDE_7D_RESET"
        fi
fi
printf "STATUS=%s VALUE=[%s]\n" "$CLAUDE_STATUS" "${CLAUDE_5H_UTIL-<unset>}"
