set -euo pipefail
TODAY=$(date +%Y-%m-%d)
if [[ "$LANG_MODE" == "en" ]]; then
    printf "══ Rate Limit Status (%s) ══\n" "$TODAY"
else
    printf "══ レートリミット状況 (%s) ══\n" "$TODAY"
fi
printf "VALUE=[%s]\n" "${LANG_MODE-<unset>}"
