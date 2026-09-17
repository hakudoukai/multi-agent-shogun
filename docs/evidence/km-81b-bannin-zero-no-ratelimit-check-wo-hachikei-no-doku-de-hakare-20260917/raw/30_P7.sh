set -euo pipefail
LANG_MODE="ja"

# ─── Parse args ───
while [[ $# -gt 0 ]]; do
    case "$1" in
        --lang)  LANG_MODE="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: ratelimit_check.sh [--lang en|ja]"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done
printf "VALUE=[%s]\n" "$LANG_MODE"
