#!/usr/bin/env bash
# km-232 新束の driver。km-227b 01_instrument/run_case.sh（harness/run_case.orig_km227b.sh）と
# 同じ順・同じ redirect で走る。違ひは一つのみ: mock の dir を $5 で受ける（原は a1-km227b/sbx/bin を焼き込む）。
# $6 = 未読からの経過秒 override（原の $5 と同義）。
set -uo pipefail
VER_DIR="$1"; CLI_TYPE_ARG="$2"; MOCK_KIND="$3"; OUT_DIR="$4"; MOCK_BIN_DIR="$5"; AGE_OVERRIDE_SEC="${6:-}"
mkdir -p "$OUT_DIR"
export MOCK_TMUX_LOG="$OUT_DIR/mock_tmux.log"
: > "$MOCK_TMUX_LOG"
export IDLE_FLAG_DIR="$OUT_DIR/flags"
rm -rf "$IDLE_FLAG_DIR"; mkdir -p "$IDLE_FLAG_DIR"
export PATH="$MOCK_BIN_DIR:$PATH"
export NUDGE_FINGERPRINT_FILE="$OUT_DIR/nudge_fingerprint"
rm -f "$NUDGE_FINGERPRINT_FILE"
echo "which_tmux=$(command -v tmux)" > "$OUT_DIR/env_check.txt"
export __INBOX_WATCHER_TESTING__=1
SCRIPT_DIR="$VER_DIR"
AGENT_ID="testagent"
PANE_TARGET="%999999"
CLI_TYPE="$CLI_TYPE_ARG"
INBOX="$VER_DIR/queue/inbox/${AGENT_ID}.yaml"
LOCKFILE="${INBOX}.lock"
if [ -n "$AGE_OVERRIDE_SEC" ]; then
    export FIRST_UNREAD_SEEN=$(( $(date +%s) - AGE_OVERRIDE_SEC ))
fi
if [[ "$CLI_TYPE" == "claude" ]]; then
    touch "${IDLE_FLAG_DIR}/shogun_idle_${AGENT_ID}"
fi
echo "VER_DIR=$VER_DIR CLI_TYPE=$CLI_TYPE PANE_TARGET=$PANE_TARGET MOCK_KIND=$MOCK_KIND AGE_OVERRIDE_SEC=${AGE_OVERRIDE_SEC:-<none>}" > "$OUT_DIR/argv.txt"
source "$VER_DIR/scripts/inbox_watcher.sh" > "$OUT_DIR/source.stdout" 2> "$OUT_DIR/source.stderr"
echo "$?" > "$OUT_DIR/source.rc"
process_unread_once > "$OUT_DIR/process_unread.stdout" 2> "$OUT_DIR/process_unread.stderr"
echo "$?" > "$OUT_DIR/process_unread.rc"
agent_is_busy > "$OUT_DIR/agent_is_busy_direct.stdout" 2> "$OUT_DIR/agent_is_busy_direct.stderr"
echo "$?" > "$OUT_DIR/agent_is_busy_direct.rc"
