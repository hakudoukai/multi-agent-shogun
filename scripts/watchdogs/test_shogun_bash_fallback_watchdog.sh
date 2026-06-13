#!/usr/bin/env bash
#
# DoD 再現テスト — shogun_bash_fallback_watchdog.sh
#
# 由来: subtask_thirdpc_shogun_bash_fallback_watchdog (副院長追命 670ffbfe(2))。
# 偽 green 厳禁・real 証跡: 実 tmux fixture pane で (A) bash 落ち + (B) stuck 再現 →
# watchdog 検知 → relaunch → alive 実証 + 冪等 + 再起動上限 escalate を機械検証する。
#
# 実行: bash scripts/watchdogs/test_shogun_bash_fallback_watchdog.sh
# 終了コード: 0 = 全 PASS、1 = いずれか FAIL
#
# 安全: DD-169 順守で tmux kill-session を一切使わない (fixture は exit で自然終了)。
#       DB は SBW_NO_DB=1 で全 skip、relaunch は無害な stand-in command に差替。

set -uo pipefail
cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../.." || exit 1

WD=scripts/watchdogs/shogun_bash_fallback_watchdog.sh
PASS=0; FAIL=0
ok() { echo "  PASS: $1"; PASS=$((PASS+1)); }
ng() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
t_eq()    { if [ "$1" = "$2" ]; then ok "$3"; else ng "$3 (got='$1' want='$2')"; fi; }
t_grep()  { if printf '%s' "$1" | grep -q "$2"; then ok "$3"; else ng "$3"; fi; }
t_ngrep() { if printf '%s' "$1" | grep -q "$2"; then ng "$3"; else ok "$3"; fi; }

TMP=$(mktemp -d /tmp/sbw_test.XXXXXX)
trap 'rm -rf "$TMP"' EXIT

echo "════ 0. shellcheck ════"
if command -v shellcheck >/dev/null 2>&1; then
  if shellcheck "$WD" >/dev/null 2>&1; then ok "shellcheck green"; else ng "shellcheck issues"; shellcheck "$WD"; fi
else
  if bash -n "$WD"; then ok "bash -n (shellcheck absent)"; else ng "bash -n syntax error"; fi
fi

# ─── classification fixtures ───
cat > "$TMP/cap_A.txt" <<'EOF'
[大将軍標準編成] 将軍-third / claude
hakudokai@momizi-dx:~/multi-agent-shogun$ inbox3
inbox3: command not found
hakudokai@momizi-dx:~/multi-agent-shogun$
EOF
cat > "$TMP/cap_B.txt" <<'EOF'
● Calling the model...
  ⎿  API Error: 529 overloaded_error · Retrying… attempt 4/10
─────────────────────────────────────────────
 ❯
─────────────────────────────────────────────
  ⏵⏵ bypass permissions on (shift+tab to cycle)   esc to interrupt
EOF
cat > "$TMP/cap_H.txt" <<'EOF'
● I'll read the file now.
  ⎿  Read 40 lines
─────────────────────────────────────────────
 ❯ continue with the task
─────────────────────────────────────────────
  ⏵⏵ bypass permissions on   esc to interrupt   ? for shortcuts
EOF
: > "$TMP/cap_E.txt"

cls() { SBW_CLASSIFY_ONLY=1 SBW_NO_DB=1 SBW_CAPTURE_FILE="$1" SBW_PANE_CMD_OVERRIDE="$2" \
  SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t bash "$WD" 2>/dev/null; }

echo "════ 1. classification (capture-content 主, doppler mask 耐性) ════"
t_eq "$(cls "$TMP/cap_A.txt" bash)"    "A"       "A: bash-fallback"
t_eq "$(cls "$TMP/cap_B.txt" node)"    "B"       "B: stuck-retry"
t_eq "$(cls "$TMP/cap_H.txt" node)"    "HEALTHY" "HEALTHY (working)"
t_eq "$(cls "$TMP/cap_E.txt" bash)"    "EMPTY"   "EMPTY"
t_eq "$(cls "$TMP/cap_H.txt" doppler)" "HEALTHY" "doppler-mask healthy≠A"
t_eq "$(cls "$TMP/cap_B.txt" doppler)" "B"       "doppler-mask stuck=B"

echo "════ 2. (B) persistence (STUCK_MIN→300s, NOW 注入で決定的) ════"
LD="$TMP/persist"
pr() { SBW_NO_DB=1 SBW_DRY_RUN=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_CAPTURE_FILE="$TMP/cap_B.txt" SBW_PANE_CMD_OVERRIDE=node SBW_LOG_DIR="$LD" SBW_NOW_EPOCH="$1" bash "$WD" 2>&1; }
t_grep "$(pr 1000)" 'reset timer'          "run1 first-sighting defer"
t_grep "$(pr 1060)" 'not yet persistent'   "run2 +60s defer"
t_grep "$(pr 1360)" 'RELAUNCH'             "run3 +360s fires"

echo "════ 3. idempotency (MODE A 連続 run = relaunch 1 回) ════"
LD="$TMP/idem"
ir() { SBW_NO_DB=1 SBW_DRY_RUN=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_CAPTURE_FILE="$TMP/cap_A.txt" SBW_PANE_CMD_OVERRIDE=bash SBW_LOG_DIR="$LD" bash "$WD" 2>&1; }
ir >/dev/null
t_grep "$(ir)" 'idempotency' "run2 skipped (flag)"
t_eq "$(wc -l < "$LD/restarts.log")" "1" "relaunch count == 1"

echo "════ 4. restart cap → human_required escalate (relaunch 無) ════"
LD="$TMP/cap"; mkdir -p "$LD"; printf '%s\n' 5000 5010 5020 > "$LD/restarts.log"
cr=$(SBW_NO_DB=1 SBW_DRY_RUN=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_CAPTURE_FILE="$TMP/cap_A.txt" SBW_PANE_CMD_OVERRIDE=bash SBW_LOG_DIR="$LD" SBW_NOW_EPOCH=5100 \
  SBW_RESTART_CAP=3 bash "$WD" 2>&1)
t_grep  "$cr" 'HALT'     "cap exceeded → HALT"
t_grep  "$cr" 'escalate' "cap exceeded → escalate"
t_ngrep "$cr" 'RELAUNCH' "no relaunch over cap"
t_eq "$(wc -l < "$LD/restarts.log")" "3" "restarts.log unchanged (3)"

echo "════ 5. manual disable flag 尊重 ════"
LD="$TMP/disable"; mkdir -p "$LD"; touch "$LD/DISABLE"
dr=$(SBW_NO_DB=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_CAPTURE_FILE="$TMP/cap_A.txt" SBW_PANE_CMD_OVERRIDE=bash SBW_LOG_DIR="$LD" bash "$WD" 2>&1)
t_grep "$dr" 'manual disable' "DISABLE flag halts watchdog"

# ─── live tmux e2e ───
e2e_one() {
  # $1=session $2=setup-cmd $3=role $4=marker $5=mode-label
  local S="$1" setup="$2" role="$3" marker="$4" lbl="$5"
  local LD="$TMP/e2e_$S" cap
  tmux new-session -d -s "$S" -x 200 -y 50 -n f 2>/dev/null
  sleep 0.5
  tmux send-keys -t "$S":f.0 "$setup" Enter
  sleep 1
  # 2 回 run: MODE B は persistence で 2 回目に発火 (MODE A は冪等 flag で 2 回目 skip)
  for _ in 1 2; do
    SBW_NO_DB=1 SBW_BOOT_DELAY_SEC=2 SBW_STUCK_MIN=0 \
      SBW_RELAUNCH_CMD="echo $marker && cat" \
      SBW_KICKOFF_TEXT="KICK_$marker" \
      SBW_PANE_TARGET="$S":f.0 SBW_SESSION_NAME="$S" SBW_ROLE_NAME="$role" SBW_LOG_DIR="$LD" \
      bash "$WD" >/dev/null 2>&1
    sleep 1
  done
  cap=$(tmux capture-pane -t "$S":f.0 -p -S -20 2>/dev/null)
  # teardown (exit, no kill-session = DD-169 順守)
  tmux send-keys -t "$S":f.0 C-c 2>/dev/null; sleep 0.2
  tmux send-keys -t "$S":f.0 "exit" Enter 2>/dev/null; sleep 0.3
  if printf '%s' "$cap" | grep -q "$marker" && printf '%s' "$cap" | grep -q "KICK_$marker"; then
    ok "e2e $lbl: relaunch executed + kickoff delivered"
  else
    ng "e2e $lbl: relaunch/kickoff (capture tail below)"; printf '%s\n' "$cap" | tail -8
  fi
}

if command -v tmux >/dev/null 2>&1; then
  echo "════ 6. live tmux e2e (A: bash-fallback) ════"
  e2e_one sbwt_A "echo '[大将軍標準編成] 将軍-test / claude'; inbox3" t-a SBW_A_OK "MODE A"
  echo "════ 7. live tmux e2e (B: stuck-retry → interrupt+relaunch) ════"
  e2e_one sbwt_B \
    $'printf \'\\u25cf model...\\n  Retrying\\u2026 attempt 4/10\\n \\u276f\\n  esc to interrupt\\n\'; sleep 600' \
    t-b SBW_B_OK "MODE B"
else
  echo "(tmux 不在 — e2e skip)"
fi

# ─── MODE B child-TERM 証跡+検証 (cycle2 hardening, 誤TERM防止 real証跡) ───
echo "════ 8. MODE B child-TERM 証跡+検証 (誤TERM防止) ════"
SLEEP_BIN="$(command -v sleep)"
BD="$TMP/termbin"; mkdir -p "$BD/claude_stack"
# comm を制御する為 copy binary を使う (shebang script だと comm=interpreter になる)。
# args への 'claude' 注入は実行 path 経由 (claude_stack/…) で valid sleep 引数を維持。
for n in claude node doppler vite; do cp "$SLEEP_BIN" "$BD/$n"; done
cp "$SLEEP_BIN" "$BD/claude_stack/node"
cp "$SLEEP_BIN" "$BD/claude_stack/doppler"
PIDF="$TMP/term_cpids"; : > "$PIDF"
cat > "$TMP/term_parent.sh" <<EOF
#!/usr/bin/env bash
"$BD/claude" 60 &              echo "claude \$!"      >> "$PIDF"
"$BD/node" 60 &               echo "node_gen \$!"    >> "$PIDF"
"$BD/doppler" 60 &            echo "doppler_gen \$!" >> "$PIDF"
"$BD/vite" 60 &               echo "vite \$!"        >> "$PIDF"
"$BD/claude_stack/node" 60 &     echo "node_cl \$!"    >> "$PIDF"
"$BD/claude_stack/doppler" 60 &  echo "doppler_cl \$!" >> "$PIDF"
exec sleep 60
EOF
chmod +x "$TMP/term_parent.sh"
"$TMP/term_parent.sh" &
PARENT_PID=$!
sleep 0.7
gp() { awk -v k="$1" '$1==k{print $2}' "$PIDF"; }
# alive = process 存在 かつ zombie でない (親=exec sleep は子を reap せぬ為、TERM 済子は
# Z 状態で残り kill -0 を通す。stat で Z を死亡扱いにする)。
av() {
  local st
  st=$(ps -o stat= -p "$1" 2>/dev/null | tr -d ' ')
  if [ -z "$st" ]; then echo 0; return; fi
  case "$st" in Z*) echo 0 ;; *) echo 1 ;; esac
}

# (8a) DRY probe: 証跡 + 検証 decision を log で確認 (実 kill 無)
dprobe=$(SBW_NO_DB=1 SBW_DRY_RUN=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_LOG_DIR="$TMP/term_dry" SBW_MODE_B_TERM_PROBE_PID="$PARENT_PID" bash "$WD" 2>&1)
t_grep "$dprobe" 'ps-evidence'                       "8a 事前 ps 証跡 header 出力"
t_grep "$dprobe" 'ps|'                               "8a 証跡に直系子の ps 行列挙"
t_grep "$dprobe" 'would SIGTERM verified child.*ppid=' "8a 検証 decision に ppid 記録"
nterm=$(printf '%s\n' "$dprobe" | grep -c 'would SIGTERM verified child')
nskip=$(printf '%s\n' "$dprobe" | grep -c 'MODE B skip')
t_eq "$nterm" "3" "8a DRY: claude-stack 3件のみ TERM 対象 (claude+node/claude+doppler/claude)"
t_eq "$nskip" "3" "8a DRY: generic 3件 skip (node/doppler/vite 誤TERM防止)"
t_ngrep "$dprobe" '] SIGTERM verified child'   "8a DRY: 実 SIGTERM log 無 (would のみ)"

# (8b) REAL probe: 検証を通った claude-stack だけ実 TERM、generic は生存 (real証跡)
SBW_NO_DB=1 SBW_DRY_RUN=0 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_LOG_DIR="$TMP/term_real" SBW_MODE_B_TERM_PROBE_PID="$PARENT_PID" bash "$WD" >/dev/null 2>&1
sleep 1
t_eq "$(av "$(gp claude)")"      "0" "8b REAL: claude 本体 TERMed"
t_eq "$(av "$(gp node_cl)")"     "0" "8b REAL: node(claude args) TERMed"
t_eq "$(av "$(gp doppler_cl)")"  "0" "8b REAL: doppler(claude args) TERMed"
t_eq "$(av "$(gp node_gen)")"    "1" "8b REAL: generic node SURVIVED (誤TERM防止 実証)"
t_eq "$(av "$(gp doppler_gen)")" "1" "8b REAL: generic doppler SURVIVED"
t_eq "$(av "$(gp vite)")"        "1" "8b REAL: generic vite SURVIVED"
# cleanup (単一PID形 TERM、生存分のみ)
kill -TERM "$PARENT_PID" 2>/dev/null || true
for k in node_gen doppler_gen vite; do kill -TERM "$(gp "$k")" 2>/dev/null || true; done

echo
echo "════════════ RESULT: PASS=$PASS FAIL=$FAIL ════════════"
if [ "$FAIL" -eq 0 ]; then echo "ALL GREEN"; exit 0; else echo "FAILURES PRESENT"; exit 1; fi
