#!/bin/bash
# 乙の写しを source し、evaluate_row を一度だけ呼ぶ。
# ★生器には一切触れぬ★ ―― source するのは _utsushi/otsu_detect_stale.sh のみ。
# 内(器の報せ) = rc と log の最終行。外 = stderr。
BA="$(cd "$(dirname "$0")/otsu_ba" && pwd)"
: "${DETECT_STALE_LOG:=$BA/probe.log}"
: "${DETECT_STALE_INFLIGHT_DIR:=$BA/inflight}"
export DETECT_STALE_LOG DETECT_STALE_INFLIGHT_DIR
mkdir -p "$BA" 2>/dev/null
# shellcheck disable=SC1090
. "$(dirname "$0")/../_utsushi/otsu_detect_stale.sh"
ROW='{"status":"pending","from":"ashigaru-third-2","recipient":"fukuincho","type":"handshake","response_by_time":"2020-01-01T00:00:00+09:00","correlation_id":"km83probe"}'
detect_stale_evaluate_row "$ROW"
rc=$?
echo "rc=$rc"
echo "log末=$(tail -1 "$DETECT_STALE_LOG" 2>/dev/null || echo '(log読めず)')"
echo "STALE_SEC実値=${DETECT_STALE_STALE_SEC}"
exit $rc
