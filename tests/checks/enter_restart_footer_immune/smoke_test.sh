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
# β改修 cycle3 (CANON 残 regression #1 Layer B):
#   Claude Code TUI prompt 形式 旧 `│ > xxx │` + 新 `❯ xxx` (上下 ──── ボーダー間) を OR 受理。
NONEMPTY_RE='│[[:space:]]*>[[:space:]]+[^[:space:]│]|^[[:space:]]*❯[[:space:]]+[^[:space:]]'
EMPTY_RE='│[[:space:]]*>[[:space:]]*│?[[:space:]]*$|^[[:space:]]*❯[[:space:]]*$'

PASS=0
FAIL=0
FAILED_CASES=()

# label 判定ロジックを watchdog 本体と同一手順で再現
# β改修 cycle4: NBSP (U+00A0) → ASCII space 正規化
# β改修 cycle5: last_non_footer_line → PROMPT_LINE 直接探索 (α 堅牢版)
PROMPT_LINE_PATTERN='^[[:space:]]*❯|│[[:space:]]*>'
classify() {
    local pane_tail="$1"
    local prompt_line
    pane_tail=$(printf '%s' "$pane_tail" | sed 's/\xc2\xa0/ /g')
    # ★cycle5 Codex T1 fix: grep no-match (rc=1) を pipefail 下で正常終了として扱う (|| true)★
    prompt_line=$(printf '%s\n' "$pane_tail" | { grep -E "$PROMPT_LINE_PATTERN" || true; } | tail -1)
    if [ -z "$prompt_line" ]; then
        # PANE_TAIL に prompt 行不在
        if [ -z "$(printf '%s\n' "$pane_tail" | { grep -vE "$FOOTER_PATTERN" || true; } | awk 'NF')" ]; then
            echo "no_content"
        else
            echo "no_match"
        fi
        return
    fi
    if printf '%s' "$prompt_line" | grep -qE "$NONEMPTY_RE"; then
        echo "match_nonempty"
    elif printf '%s' "$prompt_line" | grep -qE "$EMPTY_RE"; then
        echo "match_empty"
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

# === β改修 cycle3 追加 (CANON 残 regression #1 Layer B): 新 Claude TUI 形式 ❯ + context status 行 ===

# C09: 新形式 (上下 ──── ボーダー + 中央 ❯ 非空) + 末尾 context status footer → match_nonempty
#      = 現実観測した commander pane の状況 (cycle3 patch 後 fire 期待)
run_case "C09" \
    "新形式 ❯ 非空 buffer + 上下 ──── + 末尾 100% context used → match_nonempty (cycle3 核心)" \
    "────────────────────────────────────────────────
❯ hello world
────────────────────────────────────────────────
                                             100% context used" \
    "match_nonempty"

# C10: 新形式 (上下 ──── ボーダー + 中央 ❯ 空) + 末尾 context status → match_empty (fire しない)
run_case "C10" \
    "新形式 ❯ 空 buffer + 末尾 99% context used → match_empty" \
    "────────────────────────────────────────────────
❯
────────────────────────────────────────────────
                                             99% context used" \
    "match_empty"

# C11: 新形式と旧形式 mixed (実環境では発生しないが OR ロジック健全性確認)
run_case "C11" \
    "新+旧 mixed (旧 last_non_footer) → 旧 regex で match_nonempty" \
    "❯ early input
│ > later legacy input │
⏵⏵ bypass permissions on" \
    "match_nonempty"

# C12: context status 行のみ + 直前に非空 input buffer (footer 漏れ verify)
run_case "C12" \
    "末尾 [N]% context used 単独 footer + 直前新形式 ❯ 非空 → match_nonempty (status 行除外確認)" \
    "❯ ok
                                             87% context used" \
    "match_nonempty"

# === β改修 cycle4 追加 (CANON 残 regression #1 Layer C): NBSP 正規化 ===

# C13: 新形式 ❯ <NBSP> nonempty (= Claude Code TUI 実観察形式) → match_nonempty
#      実環境 (shogun-third pane) で実測した 23:52:25 cycle log の last_non_footer_line = `❯\xc2\xa0fire_test_8a8179d`
run_case "C13" \
    "新形式 ❯<NBSP>非空 (Claude Code TUI 実観察形式) → match_nonempty (cycle4 核心)" \
    "$(printf '\xe2\x9d\xaf\xc2\xa0hello_world')" \
    "match_nonempty"

# C14: 新形式 ❯ <NBSP> のみ (空 buffer 実観察形式) → match_empty
run_case "C14" \
    "新形式 ❯<NBSP> 空 buffer (実観察形式) → match_empty" \
    "$(printf '\xe2\x9d\xaf\xc2\xa0')" \
    "match_empty"

# C15: 旧形式 + NBSP separator → 旧 regex でも NBSP 正規化後 match
run_case "C15" \
    "旧形式 │<NBSP>><NBSP>非空 (理論上の NBSP 混入) → match_nonempty" \
    "$(printf '\xe2\x94\x82\xc2\xa0>\xc2\xa0legacy_with_nbsp')" \
    "match_nonempty"

# === β改修 cycle5 追加 (CANON 残 regression #1 Layer D, α 堅牢版): output 流入 race 吸収 ===

# C16: output 流入で ❯ 非空 行が中間に位置 (実観察 race case) → match_nonempty (cycle5 核心)
run_case "C16" \
    "output 流入 + ❯ 非空 + 末尾 output (PROMPT 行探索で捕捉) → match_nonempty (cycle5 核心)" \
    "────────────────────────────────────────────────
❯ user_typed_text
────────────────────────────────────────────────
100% context used

● Bash(some long output line 1)
● Bash(some long output line 2)
● Bash(some long output line 3)
some final tool output text" \
    "match_nonempty"

# C17: output 流入で ❯ 空 行が中間 → match_empty (誤発火防止維持)
run_case "C17" \
    "output 流入 + ❯ 空 + 末尾 output → match_empty (誤発火防止維持)" \
    "────────────────────────────────────────────────
❯
────────────────────────────────────────────────
100% context used

● Bash(continuing output)
final output line" \
    "match_empty"

# C18: PANE_TAIL 全体に prompt 行が一切ない (= pane の bottom 50 行に input 行が含まれない pathological case) → no_match
run_case "C18" \
    "PANE_TAIL に prompt 行なし → no_match" \
    "some output line 1
some output line 2
some output line 3" \
    "no_match"

# C19: 複数 prompt 行 (= 履歴に過去 prompt が残るケース) → tail -1 で最下位を取る
run_case "C19" \
    "複数 prompt 行混在 → tail -1 で最下位 (= 現在の) prompt 行を取る" \
    "❯ old_prompt_with_text
some output
❯ current_input
output continues" \
    "match_nonempty"

echo "----"
echo "RESULT: PASS=$PASS FAIL=$FAIL TOTAL=$((PASS + FAIL))"
if [ "$FAIL" -gt 0 ]; then
    printf 'FAILED CASES: %s\n' "${FAILED_CASES[*]}" >&2
    echo "ALL PASS NOT REACHED" >&2
    exit 1
fi
echo "ALL PASS ($PASS/$((PASS + FAIL)))"
exit 0
