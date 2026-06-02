#!/usr/bin/env bash
#
# Smoke test for pretooluse_bash_guard.sh stdin JSON 対応 (cycle5 T1 修正版)
#
# 由来:
#   - cycle4 b3386b9 で stdin JSON 公式仕様対応 (副院長令 baabd1ca cycle4 B1)
#   - cycle5 副院長令 baabd1ca cycle4 Codex audit 02c21d67-f70c-458d-ad25-10e913692204
#     T1 high「rc=0 なら常に PASS する条件、hook が stdin JSON を読まない回帰を
#     検出できない」を構造的に解消。
#
# 解消手段 (副院長令明示):
#   pane_identity.sh を stub 化し ★実行痕跡を明示出力★、tmux command 時は発火
#   回数=1、safe command 時は発火回数=0 を ★厳密 assert★ (rc=0 のみガード禁)。
#
# 設計:
#   - $TEST_DIR/scripts/checks/ に hook script + stub pane_identity.sh をコピー配置
#   - stub pane_identity.sh は呼出ごとに $TEST_DIR/pane_identity-fires.log に追記
#   - hook script (pretooluse_bash_guard.sh L24) は同 dir の pane_identity.sh を
#     `here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; bash "$here/pane_identity.sh"`
#     で呼出 → コピー先 dir で実行すれば stub が必ず呼ばれる
#   - 各テスト前に fires.log を reset、hook 実行後に行数 (= 発火回数) を assertion
#
# 検証 5 観点 (cycle5 T1 厳密化):
#   (1) stdin JSON tool_input.command=tmux split-window → ★fires=1★ + rc=0 厳密 assert
#   (2) stdin JSON tool_input.command=ls -la (safe) → ★fires=0★ + rc=0 厳密 assert
#   (3) stdin JSON 不正 + CLAUDE_TOOL_INPUT=tmux → ★fires=1★ + rc=0 (fallback 経路)
#   (4) stdin 空 + CLAUDE_TOOL_INPUT 未設定 → ★fires=0★ + rc=0 (素通り)
#   (5) python3 抽出経路の正確性 (DD-169 と同等仕様)

set -euo pipefail

PASS_COUNT=0
FAIL_COUNT=0
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TEST_DIR=$(mktemp -d -t pretooluse_smoke_XXXXXX)
trap 'rm -rf "$TEST_DIR"' EXIT

pass() { echo "PASS: $*"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL: $*" >&2; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# ─── setup: hook + stub pane_identity を TEST_DIR に配置 ───
setup_hook_with_stub() {
  local hook_dir="$TEST_DIR/scripts/checks"
  mkdir -p "$hook_dir"

  # 本物 hook script を TEST_DIR にコピー (本体無修正で動作確認)
  cp "$REPO_ROOT/scripts/checks/pretooluse_bash_guard.sh" "$hook_dir/pretooluse_bash_guard.sh"
  chmod +x "$hook_dir/pretooluse_bash_guard.sh"

  # stub pane_identity.sh: 呼出ごとに fires.log へ追記 + 実行痕跡 stderr 出力
  cat > "$hook_dir/pane_identity.sh" <<'STUBPI'
#!/usr/bin/env bash
# Stub pane_identity.sh for smoke test (cycle5 T1 fix)
# 呼出ごとに $TEST_DIR/pane_identity-fires.log にタイムスタンプ追記
echo "fire_at=$(date -Is)" >> "${TEST_DIR}/pane_identity-fires.log"
echo "[STUB pane_identity] invoked (smoke test)" >&2
exit 0
STUBPI
  chmod +x "$hook_dir/pane_identity.sh"

  export TEST_DIR
  HOOK="$hook_dir/pretooluse_bash_guard.sh"
}

reset_fires_log() {
  : > "$TEST_DIR/pane_identity-fires.log"
}

count_fires() {
  if [ -f "$TEST_DIR/pane_identity-fires.log" ]; then
    # 空 file は wc -l で 0、各 fire 行は改行で終端
    local n
    n=$(wc -l < "$TEST_DIR/pane_identity-fires.log" | tr -d ' ')
    echo "${n:-0}"
  else
    echo 0
  fi
}

# ─── (1) stdin JSON tmux split-window → fires=1 + rc=0 ───
test_stdin_json_tmux_fires_once() {
  local desc='(1) stdin JSON tmux split-window → 発火回数=1 + rc=0 (厳密 assert)'
  reset_fires_log
  local input_json='{"tool_input":{"command":"tmux split-window -h"}}'
  local rc=0
  printf '%s' "$input_json" | bash "$HOOK" >/dev/null 2>&1 || rc=$?
  local fires
  fires=$(count_fires)

  if [ "$rc" -eq 0 ] && [ "$fires" -eq 1 ]; then
    pass "$desc (rc=$rc, fires=$fires)"
  else
    fail "$desc — rc=$rc fires=$fires (expected rc=0 fires=1)"
  fi
}

# ─── (2) stdin JSON safe command → fires=0 + rc=0 ───
test_stdin_json_safe_no_fire() {
  local desc='(2) stdin JSON safe command (ls -la) → 発火回数=0 + rc=0 (厳密 assert)'
  reset_fires_log
  local input_json='{"tool_input":{"command":"ls -la"}}'
  local rc=0
  printf '%s' "$input_json" | bash "$HOOK" >/dev/null 2>&1 || rc=$?
  local fires
  fires=$(count_fires)

  if [ "$rc" -eq 0 ] && [ "$fires" -eq 0 ]; then
    pass "$desc (rc=$rc, fires=$fires)"
  else
    fail "$desc — rc=$rc fires=$fires (expected rc=0 fires=0、false positive)"
  fi
}

# ─── (3) stdin JSON 不正 + CLAUDE_TOOL_INPUT fallback → fires=1 ───
test_stdin_invalid_fallback_fires() {
  local desc='(3) stdin JSON 不正 + CLAUDE_TOOL_INPUT=tmux split-window → fallback で発火回数=1'
  reset_fires_log
  local rc=0
  printf '%s' "{not_json_garbage}" | CLAUDE_TOOL_INPUT="tmux split-window -h" bash "$HOOK" >/dev/null 2>&1 || rc=$?
  local fires
  fires=$(count_fires)

  if [ "$rc" -eq 0 ] && [ "$fires" -eq 1 ]; then
    pass "$desc (rc=$rc, fires=$fires、fallback 経路で発火)"
  else
    fail "$desc — rc=$rc fires=$fires (expected rc=0 fires=1)"
  fi
}

# ─── (4) stdin 空 + envvar 未設定 → fires=0 ───
test_stdin_empty_no_fire() {
  local desc='(4) stdin 空 + CLAUDE_TOOL_INPUT 未設定 → 発火回数=0 + rc=0 (素通り)'
  reset_fires_log
  local rc=0
  printf '' | env -u CLAUDE_TOOL_INPUT bash "$HOOK" >/dev/null 2>&1 || rc=$?
  local fires
  fires=$(count_fires)

  if [ "$rc" -eq 0 ] && [ "$fires" -eq 0 ]; then
    pass "$desc (rc=$rc, fires=$fires)"
  else
    fail "$desc — rc=$rc fires=$fires (expected rc=0 fires=0)"
  fi
}

# ─── (5) python3 抽出経路の正確性 (DD-169 と同等仕様) ───
test_stdin_json_extraction_correctness() {
  local desc='(5) python3 抽出経路で .tool_input.command が正確に取得される (DD-169 と同等仕様)'
  local input_json='{"tool_input":{"command":"echo hello"},"other":"ignored"}'
  local extracted
  extracted=$(printf '%s' "$input_json" | python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print(d.get('tool_input', {}).get('command', ''), end='')
except Exception:
    sys.exit(1)
" 2>/dev/null)
  if [ "$extracted" = "echo hello" ]; then
    pass "$desc (extracted='$extracted')"
  else
    fail "$desc — extracted='$extracted' (expected 'echo hello')"
  fi
}

# ─── (6) ★cycle5 T1 回帰検知能力検証★: hook が stdin JSON 読まなくなった場合に fail する ───
test_regression_detection_capability() {
  local desc='(6) 回帰検知能力 verify: hook が stdin JSON 読まないと test(1) が fail に転じることを meta 検証'
  # 別 hook を temporary に作成、stdin JSON を読まず envvar のみ依存 (cycle3 以前の状態 simulate)
  local broken_hook_dir="$TEST_DIR/scripts/checks_broken"
  mkdir -p "$broken_hook_dir"
  cp "$TEST_DIR/scripts/checks/pane_identity.sh" "$broken_hook_dir/pane_identity.sh"
  cat > "$broken_hook_dir/pretooluse_bash_guard.sh" <<'BROKENHOOK'
#!/usr/bin/env bash
# Broken hook: stdin JSON を読まず CLAUDE_TOOL_INPUT のみ依存 (cycle3 以前の状態 simulate)
set +e
input="${CLAUDE_TOOL_INPUT:-}"
if printf '%s' "$input" | grep -qE '(tmux split-window|tmux kill-pane|tmux respawn-pane)'; then
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    bash "$here/pane_identity.sh" >&2 2>/dev/null || true
fi
exit 0
BROKENHOOK
  chmod +x "$broken_hook_dir/pretooluse_bash_guard.sh"

  reset_fires_log
  local input_json='{"tool_input":{"command":"tmux split-window -h"}}'
  local rc=0
  # broken hook に stdin JSON 入力 + CLAUDE_TOOL_INPUT 未設定
  printf '%s' "$input_json" | env -u CLAUDE_TOOL_INPUT bash "$broken_hook_dir/pretooluse_bash_guard.sh" >/dev/null 2>&1 || rc=$?
  local fires
  fires=$(count_fires)

  # broken hook では fires=0 (stdin 読まないので tmux 検出不能) → これを assert で fail とすれば回帰検知能力 verify
  if [ "$rc" -eq 0 ] && [ "$fires" -eq 0 ]; then
    pass "$desc (broken hook では fires=0 → 本 smoke test の (1) が正しく fail に転じる証跡)"
  else
    fail "$desc — broken hook で予期しない rc=$rc fires=$fires"
  fi
}

# ─── Main ───
setup_hook_with_stub

echo "=== Smoke test: pretooluse_bash_guard.sh stdin JSON 厳密 assert (cycle5 T1) ==="
test_stdin_json_tmux_fires_once
test_stdin_json_safe_no_fire
test_stdin_invalid_fallback_fires
test_stdin_empty_no_fire
test_stdin_json_extraction_correctness
test_regression_detection_capability
echo "---"
echo "Total: PASS=$PASS_COUNT FAIL=$FAIL_COUNT"

if [ "$FAIL_COUNT" -gt 0 ]; then
  echo "RESULT: FAIL" >&2
  exit 1
fi

echo "RESULT: PASS — 全 6 観点 (stub pane_identity + fires=1/0 厳密 assert + 回帰検知能力 verify) 全 PASS"
exit 0
