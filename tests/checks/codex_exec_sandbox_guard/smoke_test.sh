#!/usr/bin/env bash
#
# codex_exec_sandbox_guard.sh — 弾く側 (rejection side) 負テスト
#
# 発令: 家老second → 足軽3号 (msg_20260806_065625_de110cbd)
# 対象: scripts/checks/codex_exec_sandbox_guard.sh (59行・3719 bytes・git 追跡済)
#
# ★境・限界 (冒頭に記す・末尾に置けば読み手が読み落とすゆえ)★
#
#   本ガード は 3 段の直列判定を持つ:
#     (0) halt gate  — GO_RECORD file (/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record)
#         の実在 + marker 内容を検証。無ければ即 exit 1 (BLOCK)。
#     (1) live-repo cwd 判定  — INTENDED_CWD が repo/newbuild パターンに glob マッチすれば exit 1。
#     (2) sandbox 種別判定    — CODEX_SANDBOX_KIND 未設定なら exit 2 (判定不能)。
#
#   ★現環境で GO_RECORD は実在せぬ (本テスト実行前に ls で確認済・当スクリプトも re-confirm する)★。
#   ∴ (0) が常に先着で exit 1 を返し、(1)(2) には ★到達し得ぬ★。
#
#   ★(1)(2) を実行で検証するには GO_RECORD を実在させる必要が在るが、
#   guard 本体のコメント (L27) が明記する通り
#   「GO記録file は理事長GO発令後に上位のみが配置する。agent自己配置/自己設定 = D-lane違反」
#   ゆえ、★本テストは GO_RECORD を一切 作成/書換せぬ★ (絶対境界・本工区の禁則を守る為)。
#
#   ∴ 本テストが実測できるのは ★halt gate (段0) の弾く側のみ★。
#   段(1)(2) の弾く側 (live-repo cwd 拒否・絶対path・相対path ../ 脱出・sandbox種別判定) は
#   ★試しておらぬ★ (試せぬ、ではなく「試すには禁則に触れるゆえ 試しておらぬ」)。
#
#   ★試した形★ = halt gate 拒否 (GO_RECORD 不在) を、intended_cwd の 6 変化
#                 (無引数/live repo 直下/live repo 配下/newbuild/安全な cwd/相対 ../ 脱出) +
#                 CODEX_SANDBOX_KIND 設定有無 の組合せで確認。
#                 ★いずれも段0 で止まる事を示すのみで、段1/2 の条件分岐そのものは検証せぬ★。
#
#   ★未測 (design-level observation・実行未確認)★ = guard コメント L43 が自ら認める通り、
#   段(1) の cwd 判定は文字列 glob マッチであり realpath 解決を行わぬ。
#   ゆえに「相対 path の ../ が文字列上 repo パターンに一致せぬ形」で live repo へ実際には
#   入り込む入力が在れば、段(1) は理論上 素通りし得る (guard 自身のコメントに拠る認識であり、
#   ★当職が実行して確かめた事実ではない★。段0 に阻まれ 実行では到達不能ゆえ)。
#
#   ★網羅を主張せず★。上記以外の未試形が在り得る事を排除せぬ。
#
# 実行: bash tests/checks/codex_exec_sandbox_guard/smoke_test.sh
# 期待: 全ケース PASS、最終行 "ALL PASS (N/N)"
#

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
GUARD="$REPO_ROOT/scripts/checks/codex_exec_sandbox_guard.sh"
GO_RECORD="/home/hakudokai/.config/dentalbi/codex_exec_sandbox_go.record"

if [ ! -f "$GUARD" ]; then
    echo "ERROR: guard not found: $GUARD" >&2
    exit 1
fi

# --- 前提の再確認 (本テスト自体が GO_RECORD を作らぬ事の保証・実行毎に検める) ---
if [ -e "$GO_RECORD" ]; then
    echo "ERROR: GO_RECORD が実在する ($GO_RECORD)。本テストは『GO_RECORD 不在』を前提に段0の弾く側のみを検証する設計ゆえ、実在する環境では前提が崩れ結果が無意味になる。中断する。" >&2
    exit 2
fi

PASS=0
FAIL=0
FAILED_CASES=()

run_case() {
    local case_id="$1"
    local description="$2"
    local expected_rc="$3"
    local expected_stderr_grep="$4"
    shift 4
    # 残余引数 = guard へ渡す引数 (0 個 or 1 個の intended_cwd)

    local actual_rc actual_stderr
    actual_stderr=$(bash "$GUARD" "$@" 2>&1 1>/dev/null)
    actual_rc=$?

    local ok=1
    if [ "$actual_rc" != "$expected_rc" ]; then
        ok=0
    fi
    if [ -n "$expected_stderr_grep" ] && ! printf '%s' "$actual_stderr" | grep -qi "$expected_stderr_grep"; then
        ok=0
    fi

    if [ "$ok" = 1 ]; then
        printf '[PASS] %-6s rc=%s (expected=%s) — %s\n' "$case_id" "$actual_rc" "$expected_rc" "$description"
        PASS=$((PASS + 1))
    else
        printf '[FAIL] %-6s rc=%s (expected=%s) stderr_grep=%q — %s\n' "$case_id" "$actual_rc" "$expected_rc" "$expected_stderr_grep" "$description" >&2
        printf '       stderr=%s\n' "$actual_stderr" >&2
        FAIL=$((FAIL + 1))
        FAILED_CASES+=("$case_id")
    fi
}

echo "=== codex_exec_sandbox_guard.sh 弾く側 負テスト (halt gate のみ実測可) ==="
echo "guard: $GUARD"
echo "GO_RECORD (不在を前提): $GO_RECORD"
echo "----"

# C01: 無引数 (= $PWD 既定・repo 内で実行しても) → halt で弾かれる
run_case "C01" \
    "無引数 (\$PWD 既定) → GO_RECORD 不在ゆえ exit 1 (halt)" \
    1 "GO記録file不在"

# C02: intended_cwd = live repo root
run_case "C02" \
    "intended_cwd=live repo 直下 → halt が先着 (cwd 判定には未到達)" \
    1 "GO記録file不在" \
    "$REPO_ROOT"

# C03: intended_cwd = live repo 配下 (サブpath)
run_case "C03" \
    "intended_cwd=live repo 配下 → halt が先着" \
    1 "GO記録file不在" \
    "$REPO_ROOT/scripts/checks"

# C04: intended_cwd = newbuild パターン
run_case "C04" \
    "intended_cwd=newbuild パターン → halt が先着" \
    1 "GO記録file不在" \
    "/home/hakudokai/projects/multi-agent-shogun-newbuild-test"

# C05: intended_cwd = 明らかに安全な cwd (repo 外・/tmp) → それでも弾かれる
run_case "C05" \
    "intended_cwd=/tmp (安全に見える cwd) でも halt が弾く (cwd の安全性は無関係)" \
    1 "GO記録file不在" \
    "/tmp/codex_exec_sandbox_guard_test_safe_dir"

# C06: intended_cwd = 相対 path による ../ 脱出試行 (文字列上は live repo パターンに非一致)
run_case "C06" \
    "intended_cwd に相対 ../ を含む脱出試行文字列 → それでも halt が先着し弾く" \
    1 "GO記録file不在" \
    "../../../home/hakudokai/projects/multi-agent-shogun"

# C07: CODEX_SANDBOX_KIND を設定しても halt には無関係 (halt が最優先)
#      run_case は env var 注入に非対応ゆえ、本ケースのみ手で組む (run_case 呼出は行わぬ)。
CODEX_SANDBOX_KIND=docker
export CODEX_SANDBOX_KIND
actual_stderr=$(bash "$GUARD" "/tmp/codex_exec_sandbox_guard_test_safe_dir_2" 2>&1 1>/dev/null)
actual_rc=$?
unset CODEX_SANDBOX_KIND
if [ "$actual_rc" = "1" ] && printf '%s' "$actual_stderr" | grep -qi "GO記録file不在"; then
    printf '[PASS] %-6s rc=%s (expected=1) — CODEX_SANDBOX_KIND=docker 設定下でも halt が先着 (sandbox種別設定はhaltを迂回せぬ)\n' "C07" "$actual_rc"
    PASS=$((PASS + 1))
else
    printf '[FAIL] %-6s rc=%s (expected=1) — CODEX_SANDBOX_KIND=docker 設定下でも halt が先着\n' "C07" "$actual_rc" >&2
    printf '       stderr=%s\n' "$actual_stderr" >&2
    FAIL=$((FAIL + 1))
    FAILED_CASES+=("C07")
fi

echo "----"
TOTAL=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
    echo "ALL PASS ($PASS/$TOTAL)"
    echo "★注記★: 全ケースは段0 (halt gate) の弾く側のみを実測。段1(cwd判定)/段2(sandbox種別判定) の弾く側は本テストでは未測 (理由=冒頭参照)。"
    exit 0
else
    echo "FAILED ($FAIL/$TOTAL): ${FAILED_CASES[*]}" >&2
    exit 1
fi
