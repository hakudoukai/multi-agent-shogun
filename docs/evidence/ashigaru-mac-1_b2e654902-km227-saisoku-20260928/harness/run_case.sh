#!/usr/bin/env bash
# b2e654902 (km-227 再測) sandbox driver — km-227b の run_case.sh(1288610b) を元に mock の在処と試料を引数へ出した版。tmux は mock のみ(PATH 先頭)。
# 実 tmux を一切呼ばぬ事は argv=0 の "tmux" 解決先を実行前後で明示する。
set -uo pipefail
VER_DIR="$1"        # sbx/ver_main または sbx/ver_karo (絶対path)
CLI_TYPE_ARG="$2"   # claude | codex
MOCK_KIND="$3"      # absent | negctrl
OUT_DIR="$4"        # 結果を書く場所(絶対path)
HARNESS="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$OUT_DIR"

case "$MOCK_KIND" in
  absent)   MOCK_SRC="$HARNESS/mock_tmux_absent" ;;
  negctrl)  MOCK_SRC="$HARNESS/mock_tmux_negctrl" ;;
  idle)     MOCK_SRC="$HARNESS/mock_tmux_idle" ;;
  *) echo "unknown MOCK_KIND=$MOCK_KIND" >&2; exit 9 ;;
esac

MOCK_BIN_DIR="$OUT_DIR/bin"; mkdir -p "$MOCK_BIN_DIR"; cp "$MOCK_SRC" "$MOCK_BIN_DIR/tmux"; chmod +x "$MOCK_BIN_DIR/tmux"
# 試料の受信箱を毎 case 新たに置く(前 case の既読化を持ち越さぬ)
cp "$HARNESS/fixture_testagent.yaml" "$VER_DIR/queue/inbox/testagent.yaml"; rm -f "$VER_DIR/queue/inbox/testagent.yaml.lock"
export MOCK_TMUX_LOG="$OUT_DIR/mock_tmux.log"
: > "$MOCK_TMUX_LOG"
export IDLE_FLAG_DIR="$OUT_DIR/flags"
rm -rf "$IDLE_FLAG_DIR"; mkdir -p "$IDLE_FLAG_DIR"
export PATH="$MOCK_BIN_DIR:$PATH"

# ★汚染対策★: 本体は既定で /tmp/inbox_watcher_nudge_fingerprint_<AGENT_ID> という
# 固定pathへ書く(script行135・実測)。AGENT_ID="testagent"を全caseで共有する為、
# 隔離せねば case間・session間(前回実行の残留)で状態が漏れる(実測: km-227b 追而1で発見)。
# 此処で毎回 OUT_DIR 配下の専用fileへ export し、実行前に必ず削除する。
export NUDGE_FINGERPRINT_FILE="$OUT_DIR/nudge_fingerprint"
rm -f "$NUDGE_FINGERPRINT_FILE"

# ASW_PHASE 既定値(script行150="2")を明示化する。既定はunsetのままにする
# (=本番既定を其の儘測る)が、何が効いたかを env_check.txt に記録する。
{
  echo "which_tmux=$(command -v tmux)"
  echo "mock_bin_dir=$MOCK_BIN_DIR"
  echo "ASW_PHASE(caller_env)=${ASW_PHASE:-<unset,script_default_is_2>}"
  echo "ASW_DISABLE_NORMAL_NUDGE(caller_env)=${ASW_DISABLE_NORMAL_NUDGE:-<unset,script_default_depends_on_ASW_PHASE>}"
  echo "NUDGE_FINGERPRINT_FILE=$NUDGE_FINGERPRINT_FILE (isolated, not /tmp)"
} > "$OUT_DIR/env_check.txt"

export __INBOX_WATCHER_TESTING__=1
SCRIPT_DIR="$VER_DIR"
AGENT_ID="testagent"
PANE_TARGET="%999999"
CLI_TYPE="$CLI_TYPE_ARG"
INBOX="$VER_DIR/queue/inbox/${AGENT_ID}.yaml"
LOCKFILE="${INBOX}.lock"

# ★追而2★: $5 は任意の「未読からの経過秒」override。process_unread()の
# age=(now-FIRST_UNREAD_SEEN) 分岐(120s=ESCALATE_PHASE1 / 240s=ESCALATE_PHASE2)を
# 一回の process_unread_once 呼出で直接検査する為、FIRST_UNREAD_SEEN を事前に
# 過去へ動かす(script行122 `FIRST_UNREAD_SEEN=${FIRST_UNREAD_SEEN:-0}` は
# 既に export 済の値を尊重するので、此処での事前export が効く)。
AGE_OVERRIDE_SEC="${5:-}"
if [ -n "$AGE_OVERRIDE_SEC" ]; then
    export FIRST_UNREAD_SEEN=$(( $(date +%s) - AGE_OVERRIDE_SEC ))
fi

# 本番の起動順を testing-guard の外で自ら再現する (production L57-58 相当):
# CLI_TYPE=claude の時のみ idle flag を touch する。此処を飛ばすとtesting modeが
# 本番と違ふ初期状態から出発してしまふ。
if [[ "$CLI_TYPE" == "claude" ]]; then
    touch "${IDLE_FLAG_DIR}/shogun_idle_${AGENT_ID}"
fi

echo "argv_cwd=$(pwd)" > "$OUT_DIR/argv.txt"
echo "VER_DIR=$VER_DIR CLI_TYPE=$CLI_TYPE PANE_TARGET=$PANE_TARGET MOCK_KIND=$MOCK_KIND AGE_OVERRIDE_SEC=${AGE_OVERRIDE_SEC:-<none,age=~0s>} FIRST_UNREAD_SEEN=${FIRST_UNREAD_SEEN:-<unset>}" >> "$OUT_DIR/argv.txt"

source "$VER_DIR/scripts/inbox_watcher.sh" > "$OUT_DIR/source.stdout" 2> "$OUT_DIR/source.stderr"
src_rc=$?
echo "$src_rc" > "$OUT_DIR/source.rc"

# source後の実効値(script内部でASW_PHASE等が計算済の状態)を記録する。
{
  echo "post_source_ASW_PHASE=${ASW_PHASE:-<still_unset>}"
  echo "post_source_ASW_DISABLE_NORMAL_NUDGE=${ASW_DISABLE_NORMAL_NUDGE:-<still_unset>}"
} >> "$OUT_DIR/env_check.txt"

process_unread_once > "$OUT_DIR/process_unread.stdout" 2> "$OUT_DIR/process_unread.stderr"
pu_rc=$?
echo "$pu_rc" > "$OUT_DIR/process_unread.rc"

# agent_is_busy() 自体の戻り値も直接測る(呼出側の解釈と切り離して観測する為)
agent_is_busy > "$OUT_DIR/agent_is_busy_direct.stdout" 2> "$OUT_DIR/agent_is_busy_direct.stderr"
echo "$?" > "$OUT_DIR/agent_is_busy_direct.rc"

sendkeys_count=$(grep -c '^MOCK_TMUX_SENDKEYS\|^MOCK_TMUX_NEGCTRL_SENDKEYS\|^MOCK_TMUX_IDLE_SENDKEYS' "$MOCK_TMUX_LOG" 2>/dev/null || true)
sendkeys_count="${sendkeys_count:-0}"
echo "$sendkeys_count" > "$OUT_DIR/sendkeys_count.txt"
echo "mock_tmux_log_lines=$(wc -l < "$MOCK_TMUX_LOG")" >> "$OUT_DIR/sendkeys_count.txt"
