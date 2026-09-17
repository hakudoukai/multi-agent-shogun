#!/usr/bin/env bash
# safe_nudge 当ての試し台 ── repo の mock(tests/test_helper/mock_tmux_pane.bash) と同じ仕掛を素の bash で。
# bats は当機に入つて居らぬ ∴ 同じ mock 手法を手で組む。器は触らず、mock の tmux を PATH で挿し替へる丈。
set -uo pipefail
BASE=/tmp/snh; rm -rf "$BASE"; mkdir -p "$BASE"

run_case() {  # tag script agent pane_agent pane_cmd cli make_watchers
  local tag="$1" script="$2" agent="$3" pane_agent="$4" pane_cmd="$5" cli="$6" mkw="$7"
  local S="$BASE/$tag"
  mkdir -p "$S/scripts/message_delivery_v2" "$S/queue/session_health" "$S/logs/message_delivery_v2" "$S/home/.openclaw" "$S/bin"
  [ "$mkw" = "yes" ] && mkdir -p "$S/queue/watchers"
  cp "$script" "$S/scripts/message_delivery_v2/safe_nudge.sh"
  export MOCK_LOG="$S/tmux_calls.log"; : > "$MOCK_LOG"
  export MOCK_PANE_AGENT_ID="$pane_agent" MOCK_PANE_CMD="$pane_cmd" MOCK_PANE_LIST="test:0.0" MOCK_CAPTURE_PANE="" MOCK_SENDKEYS_RC=0
  cat > "$S/bin/tmux" <<'TM'
#!/usr/bin/env bash
printf 'tmux %s\n' "$*" >> "${MOCK_LOG}"
cmd="${1:-}"; shift || true
case "$cmd" in
  list-panes) [[ -n "${MOCK_PANE_LIST:-}" ]] && printf '%s\n' "$MOCK_PANE_LIST"; exit 0;;
  display-message) fmt=""; while [[ $# -gt 0 ]]; do case "$1" in -p) shift; fmt="${1:-}";; esac; shift || true; done
    case "$fmt" in "#{@agent_id}") printf '%s\n' "${MOCK_PANE_AGENT_ID:-}";; "#{pane_current_command}") printf '%s\n' "${MOCK_PANE_CMD:-claude}";; *) printf '\n';; esac; exit 0;;
  capture-pane) [[ -n "${MOCK_CAPTURE_PANE:-}" ]] && printf '%s\n' "$MOCK_CAPTURE_PANE"; exit 0;;
  send-keys) exit "${MOCK_SENDKEYS_RC:-0}";;
  *) exit 0;;
esac
TM
  chmod +x "$S/bin/tmux"
  local out rc sent
  out=$(PATH="$S/bin:$PATH" HOME="$S/home" bash "$S/scripts/message_delivery_v2/safe_nudge.sh" "$agent" test:0.0 "$cli" "PROBE_NUDGE" "corr-$tag" 2>&1); rc=$?
  sent=$(command grep -c 'send-keys' "$MOCK_LOG" 2>/dev/null); sent=${sent:-0}
  local reason; reason=$(command grep -o '"extra":"[^"]*"' "$S/logs/message_delivery_v2/"*.log 2>/dev/null | tail -1)
  printf '%-4s | %-5s | cli=%-7s pane_agent=%-11s pane_cmd=%-7s | rc=%s | send-keys=%s | %s\n' \
     "$tag" "$8" "$cli" "$pane_agent" "$pane_cmd" "$rc" "$sent" "${reason:-<log無し>}"
}

C=/tmp/sn_canon.sh   # origin/main の正本
F=/tmp/sn_fix2.sh    # 本枝の当て(2行)
echo "script_canon_sha=$(sha256sum $C|cut -d' ' -f1)"
echo "script_fix2_sha =$(sha256sum $F|cut -d' ' -f1)"
echo
echo "tag  | 器    | 条件                                                    | rc   | send-keys | log の extra"
echo "-----+-------+---------------------------------------------------------+------+-----------+--------------"
run_case s1o "$C" test_agent test_agent  doppler doppler yes 旧
run_case s1n "$F" test_agent test_agent  doppler doppler yes 新
run_case s2o "$C" test_agent other_agent doppler doppler yes 旧
run_case s2n "$F" test_agent other_agent doppler doppler yes 新
run_case s3o "$C" test_agent test_agent  doppler claude  yes 旧
run_case s3n "$F" test_agent test_agent  doppler claude  yes 新
run_case s4o "$C" test_agent test_agent  claude  claude  yes 旧
run_case s4n "$F" test_agent test_agent  claude  claude  yes 新
run_case s5o "$C" test_agent other_agent claude  claude  yes 旧
run_case s5n "$F" test_agent other_agent claude  claude  yes 新
echo "-----+-------+---------------------------------------------------------+------+-----------+--------------"
echo "S6 ── 冷めの置き場が無い時(根がずれた場合の再現): queue/watchers を作らぬ"
run_case s6n "$F" test_agent test_agent  doppler doppler no  新
