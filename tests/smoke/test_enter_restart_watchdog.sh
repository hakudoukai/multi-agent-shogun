#!/usr/bin/env bash
#
# Smoke test for enter_restart watchdog (cycle4 Q1 修正、本体 stub 化全面書換)
#
# 由来: 副院長令 baabd1ca【enter_restart RED 修正 Phase A 即修正】①、Codex audit
#       40c0d3d2-0639-4f6d-bb32-3302c7d634d5 (cycle3 6845567 red) Q1 high close
#       — 旧 smoke test は watchdog logic を bash で再実装、production script の
#       breakage を捕捉できない欠陥を構造的に解消。本書は ★実 wrapper
#       (enter_restart_commander_watchdog.sh / enter_restart_shogun_third_watchdog.sh)
#       を stubbed tmux/doppler/python3 環境で実行★ し、watchdog 中核仕様を assertion。
#
# 検証 4 観点 (副院長令 + Codex Q1 fix_suggestion):
#   (a) 空 buffer (label mismatch) → send-keys Enter 呼出 0 回
#   (b) 非空 buffer (label match + idle 超過) → send-keys Enter 呼出 1 回
#   (c) 15 分以内 fire 3 回 → cap halt (send-keys 呼出 0 回)
#   (d) ER_LOG_DIR 未作成 → script 起動成功 (mkdir -p で自動作成)
#
# 追加検証 (wrapper env 契約):
#   (e) 必須 envvar 欠落 → common watchdog が exit 2 で拒否
#   (f) wrapper 経由で common watchdog が ER_* envvar を正常受領
#
# 設計:
#   - $TEST_DIR/bin/{tmux,doppler,fake_python3} で stub bin (PATH 前置)
#   - ER_PYTHON3_BIN=$TEST_DIR/bin/fake_python3 で python3 path override (cycle4 Q1 envvar 化)
#   - ER_LOG_DIR=$TEST_DIR/log_<role> で isolated log
#   - 実 wrapper 起動 (enter_restart_commander_watchdog.sh / enter_restart_shogun_third_watchdog.sh)
#   - send-keys 呼出は $TEST_DIR/send-keys.log に記録、assertion で行数検証

set -euo pipefail

PASS_COUNT=0
FAIL_COUNT=0
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_DIR=$(mktemp -d -t enter_restart_smoke_XXXXXX)
trap 'rm -rf "$TEST_DIR"' EXIT

pass() { echo "PASS: $*"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL: $*" >&2; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# ─── stub bin setup ───
setup_stub_bin() {
  mkdir -p "$TEST_DIR/bin"

  # fake tmux: argv に応じて mock
  cat > "$TEST_DIR/bin/tmux" <<'STUBTMUX'
#!/usr/bin/env bash
# Stub tmux for enter_restart smoke test
# 呼出ごとに $TEST_DIR/tmux-calls.log に argv を記録、send-keys は別 log にも記録
LOG="${TEST_DIR}/tmux-calls.log"
echo "$@" >> "$LOG"
case "$1" in
  has-session)
    exit 0  # session 常に存在
    ;;
  display-message)
    # -p '#{...}' format → dummy 値返答
    echo "/dummy|stub|claude"
    ;;
  capture-pane)
    # -p -S -3 で pane tail 出力
    printf '%s\n' "${FAKE_PANE_TAIL:-}"
    ;;
  send-keys)
    # send-keys 呼出を専用 log へ追記 (assertion 対象)
    echo "$@" >> "${TEST_DIR}/send-keys.log"
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
STUBTMUX
  chmod +x "$TEST_DIR/bin/tmux"

  # fake doppler: shift 5 で `run --project openhands --config dev --` 食い、残りを exec
  cat > "$TEST_DIR/bin/doppler" <<'STUBDOPPLER'
#!/usr/bin/env bash
# Stub doppler: `doppler run --project openhands --config dev -- <cmd> <args>` から
# 先頭 5 token (`run --project openhands --config dev --`) を食い、残りを exec
LOG="${TEST_DIR}/doppler-calls.log"
echo "$@" >> "$LOG"
shift 5
# SUPABASE_* env を fake で注入 (本体 script 内 os.environ['SUPABASE_*'] 参照対応)
export SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-stub_role_key}"
export SUPABASE_URL="${SUPABASE_URL:-http://stub.invalid}"
exec "$@"
STUBDOPPLER
  chmod +x "$TEST_DIR/bin/doppler"

  # fake python3: stdin 食って FAKE_PYTHON3_RESPONSE 出力 (default: NO_DATA)
  cat > "$TEST_DIR/bin/fake_python3" <<'STUBPYTHON'
#!/usr/bin/env bash
# Stub python3: stdin (heredoc PYEOF) を捨て、FAKE_PYTHON3_RESPONSE を出力
# default: NO_DATA (idle 判定 step で WARN: no ... handshake data → exit 0)
LOG="${TEST_DIR}/python3-calls.log"
echo "[$(date -Is)] fake_python3 invoked" >> "$LOG"
cat > /dev/null  # discard heredoc
echo "${FAKE_PYTHON3_RESPONSE:-NO_DATA}"
STUBPYTHON
  chmod +x "$TEST_DIR/bin/fake_python3"

  export PATH="$TEST_DIR/bin:$PATH"
  export TEST_DIR
}

reset_logs() {
  : > "$TEST_DIR/tmux-calls.log"
  : > "$TEST_DIR/doppler-calls.log"
  : > "$TEST_DIR/python3-calls.log"
  : > "$TEST_DIR/send-keys.log"
}

count_send_keys_enter() {
  if [ ! -f "$TEST_DIR/send-keys.log" ]; then
    echo 0
    return
  fi
  # grep -c は 0 match 時 rc=1 → `|| true` で suppress、出力は grep の数値のみ
  local n
  n=$(grep -c '^send-keys.*Enter' "$TEST_DIR/send-keys.log" 2>/dev/null || true)
  echo "${n:-0}"
}

# ─── (a) 空 buffer (label mismatch) → send-keys Enter 呼出 0 回 ───
test_empty_buffer_no_send() {
  local desc='(a) 空 buffer (`│ > `) → send-keys Enter 呼出 0 回 (実 wrapper 実走、commander 版)'
  reset_logs
  rm -rf "$TEST_DIR/log_commander"

  FAKE_PANE_TAIL=$'│ > ' \
  FAKE_PYTHON3_RESPONSE="15.0|2026-06-02T20:00:00Z|test_topic" \
  ER_PYTHON3_BIN="$TEST_DIR/bin/fake_python3" \
  ER_LOG_DIR="$TEST_DIR/log_commander" \
    bash "$REPO_ROOT/scripts/watchdogs/enter_restart_commander_watchdog.sh" >/dev/null 2>&1 || true

  local enter_count
  enter_count=$(count_send_keys_enter)
  if [ "$enter_count" -eq 0 ]; then
    pass "$desc (send-keys Enter count=$enter_count)"
  else
    fail "$desc — Enter count=$enter_count (expected 0、false positive)"
  fi
}

# ─── (b) 非空 buffer (label match + idle 超過) → send-keys Enter 呼出 1 回 ───
test_nonempty_buffer_send_once() {
  local desc='(b) 非空 buffer (`│ > hello`) + idle 15min → send-keys Enter 1 回 (実 wrapper 実走)'
  reset_logs
  rm -rf "$TEST_DIR/log_commander"

  FAKE_PANE_TAIL=$'│ > hello world' \
  FAKE_PYTHON3_RESPONSE="15.0|2026-06-02T20:00:00Z|test_topic" \
  ER_PYTHON3_BIN="$TEST_DIR/bin/fake_python3" \
  ER_LOG_DIR="$TEST_DIR/log_commander" \
    bash "$REPO_ROOT/scripts/watchdogs/enter_restart_commander_watchdog.sh" >/dev/null 2>&1 || true

  local enter_count
  enter_count=$(count_send_keys_enter)
  if [ "$enter_count" -eq 1 ]; then
    pass "$desc (send-keys Enter count=$enter_count)"
  else
    fail "$desc — Enter count=$enter_count (expected 1)"
  fi
}

# ─── (c) 15 分以内 fire 3 回 → cap halt (send-keys 呼出 0 回) ───
test_fire_cap_halt() {
  local desc='(c) 過去 15 分以内 fires.log 3 行 → cap halt、send-keys Enter 呼出 0 回'
  reset_logs
  rm -rf "$TEST_DIR/log_shogun_third"
  mkdir -p "$TEST_DIR/log_shogun_third"
  local now_epoch
  now_epoch=$(date +%s)
  # 過去 15 分以内に 3 回 fire 記録 (10/6/3 分前)
  {
    echo "$((now_epoch - 600))"
    echo "$((now_epoch - 360))"
    echo "$((now_epoch - 180))"
  } > "$TEST_DIR/log_shogun_third/fires.log"

  FAKE_PANE_TAIL=$'│ > hello world' \
  FAKE_PYTHON3_RESPONSE="15.0|2026-06-02T20:00:00Z|test_topic" \
  ER_PYTHON3_BIN="$TEST_DIR/bin/fake_python3" \
  ER_LOG_DIR="$TEST_DIR/log_shogun_third" \
    bash "$REPO_ROOT/scripts/watchdogs/enter_restart_shogun_third_watchdog.sh" >/dev/null 2>&1 || true

  local enter_count
  enter_count=$(count_send_keys_enter)
  if [ "$enter_count" -eq 0 ]; then
    pass "$desc (send-keys Enter count=$enter_count、cap halt 発動)"
  else
    fail "$desc — Enter count=$enter_count (expected 0、cap halt 未発動)"
  fi
}

# ─── (d) ER_LOG_DIR 未作成 → script 起動成功 (mkdir で自動作成) ───
test_log_dir_autocreate() {
  local desc='(d) ER_LOG_DIR 未作成 → script L51 mkdir で自動作成、起動成功'
  reset_logs
  local nonexistent_log_dir="$TEST_DIR/nonexistent_sub/log_dir_$$"
  rm -rf "$nonexistent_log_dir"
  if [ -d "$nonexistent_log_dir" ]; then
    fail "$desc — pre-test pollution"
    return
  fi

  FAKE_PANE_TAIL=$'│ > ' \
  FAKE_PYTHON3_RESPONSE="5.0|2026-06-02T20:00:00Z|test_topic" \
  ER_PYTHON3_BIN="$TEST_DIR/bin/fake_python3" \
  ER_LOG_DIR="$nonexistent_log_dir" \
    bash "$REPO_ROOT/scripts/watchdogs/enter_restart_commander_watchdog.sh" >/dev/null 2>&1 || true

  if [ -d "$nonexistent_log_dir" ]; then
    pass "$desc (dir 作成済 $nonexistent_log_dir)"
  else
    fail "$desc — dir 未作成 ($nonexistent_log_dir)"
  fi
}

# ─── (e) 必須 envvar 欠落 → common watchdog が exit 2 で拒否 ───
test_required_envvar_missing_rejected() {
  local desc='(e) wrapper 経由せず common watchdog 直接 + 必須 envvar 欠落 → exit 2 拒否'
  reset_logs
  local rc=0
  # ER_PANE_TARGET 未設定で common watchdog 直接呼出
  env -u ER_PANE_TARGET \
    bash "$REPO_ROOT/scripts/watchdogs/enter_restart_common_watchdog.sh" >/dev/null 2>&1 || rc=$?
  if [ "$rc" -eq 2 ]; then
    pass "$desc (rc=$rc)"
  else
    fail "$desc — rc=$rc (expected 2)"
  fi
}

# ─── (f) wrapper 経由で common watchdog が ER_* envvar を正常受領 ───
test_wrapper_env_contract() {
  local desc='(f) commander wrapper 起動で ER_PANE_TARGET=commander-third:0.0 等が common に渡る'
  reset_logs
  rm -rf "$TEST_DIR/log_commander"

  # wrapper 起動、common watchdog が呼出時 envvar 設定済か (log 内文字列で間接検証)
  FAKE_PANE_TAIL=$'│ > ' \
  FAKE_PYTHON3_RESPONSE="5.0|2026-06-02T20:00:00Z|test_topic" \
  ER_PYTHON3_BIN="$TEST_DIR/bin/fake_python3" \
  ER_LOG_DIR="$TEST_DIR/log_commander" \
    bash "$REPO_ROOT/scripts/watchdogs/enter_restart_commander_watchdog.sh" >/dev/null 2>&1 || true

  # common watchdog の log 内に "Commander" role name が出ているか
  local log_file
  log_file=$(find "$TEST_DIR/log_commander" -name '*.log' -type f 2>/dev/null | head -1)
  if [ -n "$log_file" ] && grep -q "Commander alive\|Commander last handshake\|enter_restart_commander cycle" "$log_file" 2>/dev/null; then
    pass "$desc (log: $(basename "$log_file"))"
  else
    fail "$desc — log file no Commander envvar trace (log=$log_file)"
  fi
}

# ─── Main ───
setup_stub_bin

echo "=== Smoke test: enter_restart watchdog 本体 stub 実行 (cycle4 Q1) ==="
test_empty_buffer_no_send
test_nonempty_buffer_send_once
test_fire_cap_halt
test_log_dir_autocreate
test_required_envvar_missing_rejected
test_wrapper_env_contract
echo "---"
echo "Total: PASS=$PASS_COUNT FAIL=$FAIL_COUNT"

if [ "$FAIL_COUNT" -gt 0 ]; then
  echo "RESULT: FAIL — smoke test 失敗 case あり、修正要" >&2
  exit 1
fi

echo "RESULT: PASS — 全 6 観点 (空/非空 buffer / cap halt / log dir auto / envvar contract) 全 PASS、実 wrapper 実行で本体 breakage を捕捉可能"
exit 0
