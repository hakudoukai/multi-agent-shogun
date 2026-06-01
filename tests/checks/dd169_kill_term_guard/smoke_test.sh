#!/usr/bin/env bash
#
# DD-169 kill -TERM guard smoke test (cycle4 stdin JSON 形式)
#
# Claude Code 公式 PreToolUse hook 仕様 = stdin JSON 入力に準拠した 10 ケース smoke。
# (cycle3 retain 段階の env var 形式は廃止、stdin JSON 形式に全件差替+新規 6 ケース追加=計 10)
#
# 実行: bash tests/checks/dd169_kill_term_guard/smoke_test.sh
# 期待: 全 10 ケース PASS、最終行 "ALL PASS (10/10)"
# 失敗時: rc=1 + どの case が fail したか stderr 表示
#

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
HOOK="$REPO_ROOT/scripts/checks/dd169_kill_term_guard.sh"

if [ ! -x "$HOOK" ]; then
    echo "ERROR: hook not found or not executable: $HOOK" >&2
    exit 1
fi

PASS=0
FAIL=0
FAILED_CASES=()

run_case() {
    local case_id="$1"
    local description="$2"
    local stdin_input="$3"
    local expected_rc="$4"

    local actual_rc
    # subshell exit code 捕捉: pipe rc を $? で取得後 printf で stdout に retain
    actual_rc=$(printf '%s' "$stdin_input" | bash "$HOOK" >/dev/null 2>&1; printf '%d' $?)

    if [ "$actual_rc" = "$expected_rc" ]; then
        printf '[PASS] %-6s rc=%s (expected=%s) — %s\n' "$case_id" "$actual_rc" "$expected_rc" "$description"
        PASS=$((PASS + 1))
    else
        printf '[FAIL] %-6s rc=%s (expected=%s) — %s\n' "$case_id" "$actual_rc" "$expected_rc" "$description" >&2
        printf '       stdin=%s\n' "$stdin_input" >&2
        FAIL=$((FAIL + 1))
        FAILED_CASES+=("$case_id")
    fi
}

echo "=== DD-169 kill -TERM guard smoke test (cycle4 stdin JSON) ==="
echo "hook: $HOOK"
echo "----"

# === fail-secure cases (parse fail / empty input) ===
run_case "C01" \
    "stdin JSON empty {} → fail-secure deny (command 空)" \
    '{}' \
    2

run_case "C02" \
    "stdin JSON parse fail (not json) → fail-secure deny" \
    'not json at all' \
    2

run_case "C03" \
    "stdin JSON command 空文字 → fail-secure deny" \
    '{"tool_input":{"command":""}}' \
    2

# === valid allow case (kill -TERM <numeric PID>) ===
run_case "C04" \
    "kill -TERM 999999 (PID 不在) → allow no-op (exit 0)" \
    '{"tool_input":{"command":"kill -TERM 999999"}}' \
    0

# === explicit deny cases (非対象例外) ===
run_case "C05" \
    "pkill foo → deny (例外対象外)" \
    '{"tool_input":{"command":"pkill foo"}}' \
    2

run_case "C06" \
    "kill -9 12345 → deny (SIGKILL は例外対象外)" \
    '{"tool_input":{"command":"kill -9 12345"}}' \
    2

run_case "C07" \
    "killall bash → deny (例外対象外)" \
    '{"tool_input":{"command":"killall bash"}}' \
    2

run_case "C08" \
    "tmux kill-server → deny (例外対象外)" \
    '{"tool_input":{"command":"tmux kill-server"}}' \
    2

# === non-kill commands (slip through) ===
run_case "C09" \
    "ls -la (kill 系外コマンド) → allow (exit 0、guard 対象外)" \
    '{"tool_input":{"command":"ls -la /tmp"}}' \
    0

# === pattern kill (non-conforming regex) ===
run_case "C10" \
    "kill -TERM \$(pgrep foo) → deny (パターン kill、厳格 regex 不通過)" \
    '{"tool_input":{"command":"kill -TERM $(pgrep foo)"}}' \
    2

# === optional extra cases (= cycle4 補強、計 12 case retain) ===
run_case "C11" \
    "kill -SIGKILL 12345 → deny (SIGKILL 別表記 retain)" \
    '{"tool_input":{"command":"kill -SIGKILL 12345"}}' \
    2

run_case "C12" \
    "kill -TERM 1 2 3 (複数 PID) → deny (1 個ずつ明示違反)" \
    '{"tool_input":{"command":"kill -TERM 1 2 3"}}' \
    2

echo "----"
TOTAL=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
    echo "ALL PASS ($PASS/$TOTAL)"
    exit 0
else
    echo "FAILED ($FAIL/$TOTAL): ${FAILED_CASES[*]}" >&2
    exit 1
fi
