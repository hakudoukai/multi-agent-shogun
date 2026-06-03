#!/usr/bin/env bash
#
# enter_restart_common_watchdog.sh β改修 footer 耐性 smoke test
# (CANON-SHOGUN-COMMS-RESTORE-01 残 regression #1 = footer 常時 last_line 占有問題への最小 patch 検証)
#
# 検証対象 (Step 5 抜粋, 改修箇所):
#   FOOTER_PATTERN='⏵⏵ bypass permissions|esc to interrupt|shift\+tab to cycle|⏵ Plan mode|tab to expand|ctrl\+o to expand|? for shortcuts'
#   LAST_NON_FOOTER_LINE=$(printf '%s\n' "$PANE_TAIL" | grep -vE "$FOOTER_PATTERN" | awk 'NF{last=$0} END{print last}')
#   if printf '%s' "$LAST_NON_FOOTER_LINE" | grep -qE '│[[:space:]]*>[[:space:]]+[^[:space:]│]'; then LABEL_MATCH=1; fi
#
# 実行: bash tests/checks/enter_restart_footer_immune/smoke_test.sh
# 期待: 全 8 ケース PASS、最終行 "ALL PASS (8/8)"
#

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
WATCHDOG="$REPO_ROOT/scripts/watchdogs/enter_restart_common_watchdog.sh"

if [ ! -r "$WATCHDOG" ]; then
    echo "ERROR: watchdog not readable: $WATCHDOG" >&2
    exit 1
fi

# FOOTER_PATTERN / 照合 regex を watchdog 本体から抽出 (= 単一情報源、drift 防止)
FOOTER_PATTERN=$(grep -E "^FOOTER_PATTERN=" "$WATCHDOG" | head -1 | sed -E "s/^FOOTER_PATTERN='([^']+)'/\\1/")
if [ -z "$FOOTER_PATTERN" ]; then
    echo "ERROR: FOOTER_PATTERN extract failed (watchdog 本体に定義無し or 形式変更)" >&2
    exit 1
fi
NONEMPTY_RE='│[[:space:]]*>[[:space:]]+[^[:space:]│]'
EMPTY_RE='│[[:space:]]*>[[:space:]]*│?[[:space:]]*$'

PASS=0
FAIL=0
FAILED_CASES=()

# label 判定ロジックを watchdog 本体と同一手順で再現
classify() {
    local pane_tail="$1"
    local last_non_footer
    last_non_footer=$(printf '%s\n' "$pane_tail" | grep -vE "$FOOTER_PATTERN" | awk 'NF{last=$0} END{print last}')
    if printf '%s' "$last_non_footer" | grep -qE "$NONEMPTY_RE"; then
        echo "match_nonempty"
    elif printf '%s' "$last_non_footer" | grep -qE "$EMPTY_RE"; then
        echo "match_empty"
    elif [ -z "$last_non_footer" ]; then
        echo "no_content"
    else
        echo "no_match"
    fi
}

run_case() {
    local case_id="$1"
    local description="$2"
    local pane_tail="$3"
    local expected="$4"
    local actual
    actual=$(classify "$pane_tail")
    if [ "$actual" = "$expected" ]; then
        printf '[PASS] %-4s actual=%-14s expected=%-14s — %s\n' "$case_id" "$actual" "$expected" "$description"
        PASS=$((PASS + 1))
    else
        printf '[FAIL] %-4s actual=%-14s expected=%-14s — %s\n' "$case_id" "$actual" "$expected" "$description" >&2
        printf '       pane_tail (base64): %s\n' "$(printf '%s' "$pane_tail" | base64 -w0)" >&2
        FAIL=$((FAIL + 1))
        FAILED_CASES+=("$case_id")
    fi
}

echo "=== enter_restart footer 耐性 smoke test ==="
echo "watchdog : $WATCHDOG"
echo "FOOTER_PATTERN extracted: $FOOTER_PATTERN"
echo "----"

# C01: footer のみ last_line + 直近に非空 input buffer → match_nonempty 期待 (= β改修核心)
run_case "C01" \
    "footer 1 行 last + 直前に非空 input buffer (regression 再現本丸)" \
    "│ > hello world │
⏵⏵ bypass permissions on (shift+tab to cycle)" \
    "match_nonempty"

# C02: 旧形式 = 末尾が非空 input buffer (footer 出現前の Claude TUI) → 既存ロジックでも通る
run_case "C02" \
    "旧形式: last_line 自体が非空 input buffer (β改修前から通っていたケース)" \
    "│ > legacy input │" \
    "match_nonempty"

# C03: footer + 空 input buffer → match_empty 期待 (LABEL_MATCH=0 維持、false fire 防止)
run_case "C03" \
    "footer last + 直前 空 input buffer → empty 判定 (fire しない)" \
    "│ > │
⏵⏵ bypass permissions on (shift+tab to cycle)" \
    "match_empty"

# C04: footer 単独 + claude UI prompt 無し → no_match 期待
run_case "C04" \
    "footer のみ + UI prompt 無し → no_match" \
    "some random output line
another line
⏵⏵ bypass permissions on (shift+tab to cycle)" \
    "no_match"

# C05: 多種 footer 行 (esc to interrupt + shift+tab to cycle 等) を除外しつつ非空 buffer 検出
run_case "C05" \
    "multi-line footer + 非空 input buffer" \
    "│ > deep work │
esc to interrupt
shift+tab to cycle
⏵⏵ bypass permissions on" \
    "match_nonempty"

# C06: Plan mode footer
run_case "C06" \
    "Plan mode footer + 非空 input buffer" \
    "│ > planning │
⏵ Plan mode (shift+tab to cycle)" \
    "match_nonempty"

# C07: tab to expand / ctrl+o to expand footer
run_case "C07" \
    "tab to expand + ctrl+o to expand footer + 非空 input buffer" \
    "│ > expanding │
tab to expand
ctrl+o to expand" \
    "match_nonempty"

# C08: 全行 footer のみ (= 直近 N 行が footer で埋め尽くされている異常状態) → no_content
run_case "C08" \
    "全行 footer (footer 過密) → no_content (fire しない)" \
    "⏵⏵ bypass permissions on (shift+tab to cycle)
esc to interrupt
shift+tab to cycle" \
    "no_content"

echo "----"
echo "RESULT: PASS=$PASS FAIL=$FAIL TOTAL=$((PASS + FAIL))"
if [ "$FAIL" -gt 0 ]; then
    printf 'FAILED CASES: %s\n' "${FAILED_CASES[*]}" >&2
    echo "ALL PASS NOT REACHED" >&2
    exit 1
fi
echo "ALL PASS ($PASS/$((PASS + FAIL)))"
exit 0
