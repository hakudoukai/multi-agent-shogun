#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# test_fukuincho_detect_stale_cli.sh — 層① CLI 統合 (integration) test
# ═══════════════════════════════════════════════════════════════
# redo: subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_cycle3_003
#   - ★cycle4 fix2 (CLI integration test)★:
#     gunshi-third cycle3 governing RED-C3 (CLI L106 || true で rc 破壊) 退行捕捉用。
#     lib 単体 (test_detect_stale.sh) は GREEN でも、CLI wrapper の rc 処理が
#     退行すれば authz reject / anomaly / fresh / inflight skip が全て enqueue 化する。
#     本 test は CLI 経由で spoof / empty-deadline / future / inflight 各 row を流し、
#     ★enqueued=0★ を assert することで CLI 層の rc 処理を検証する。
#
# Usage:
#   bash scripts/tests/test_fukuincho_detect_stale_cli.sh
#
# Exit:
#   0 = all PASS
#   1 = at least one FAIL
# ═══════════════════════════════════════════════════════════════

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
CLI_PATH="$REPO_ROOT/scripts/fukuincho_detect_stale_cli.sh"

if [ ! -f "$CLI_PATH" ]; then
    echo "FATAL: CLI not found: $CLI_PATH" >&2
    exit 1
fi

PASS=0
FAIL=0
FAIL_DETAILS=()

# 各 case 独立な log / inflight dir を用意するヘルパ
_setup_env() {
    DETECT_STALE_LOG="$(mktemp -t fukuincho_cli_test.XXXXXX.log)"
    DETECT_STALE_INFLIGHT_DIR="$(mktemp -d -t fukuincho_cli_inflight.XXXXXX)"
    DETECT_STALE_LOCK_FILE="$(mktemp -t fukuincho_cli_lock.XXXXXX)"
    export DETECT_STALE_LOG DETECT_STALE_INFLIGHT_DIR DETECT_STALE_LOCK_FILE
}

_teardown_env() {
    rm -f "$DETECT_STALE_LOG" 2>/dev/null
    rm -rf "$DETECT_STALE_INFLIGHT_DIR" 2>/dev/null
    rm -f "$DETECT_STALE_LOCK_FILE" 2>/dev/null
}

# CLI を invoke して done 行から enqueued 値を抽出する
# 引数: $1=JSONL 文字列 (複数行可、改行は \n で渡す)
# stdout: enqueued の値 (見つからない時は -1)
_invoke_cli_get_enqueued() {
    local jsonl="$1"
    printf '%s\n' "$jsonl" | bash "$CLI_PATH" --detect-stale-handshake >/dev/null 2>&1
    # done 行: "<ts> [INVOKE] fukuincho_detect_stale_cli done processed=N enqueued=N skipped=N anomalies=N"
    local done_line
    done_line=$(grep -E '\[INVOKE\].*fukuincho_detect_stale_cli done' "$DETECT_STALE_LOG" | tail -n 1)
    if [ -z "$done_line" ]; then
        printf '%s' "-1"
        return 1
    fi
    # enqueued=N 抽出
    printf '%s' "$done_line" | sed -nE 's/.*enqueued=([0-9]+).*/\1/p'
}

# log 内に指定 keyword (DENY / ANOMALY / FRESH / SKIP) を含む行数を返す
_log_count() {
    local pattern="$1"
    grep -cE "\[${pattern}\]" "$DETECT_STALE_LOG" 2>/dev/null || echo 0
}

run() {
    local name="$1"; shift
    if "$@"; then
        PASS=$((PASS + 1))
        echo "PASS: $name"
    else
        FAIL=$((FAIL + 1))
        FAIL_DETAILS+=("$name")
        echo "FAIL: $name"
    fi
}

# ════════════════════════════════════════════════════════════
# CLI-1: spoof row → enqueued=0 + DENY counter ≥1
# 旧 cycle3 fix5 (|| true) 退行下では DENY ログ後も rc=0 (true) で enqueue 発火していた。
# cycle4 fix1 で rc が実 detect_stale_evaluate_row の rc (=1 skip) になるはず。
# ════════════════════════════════════════════════════════════
test_cli_spoof_row_enqueued_zero() {
    _setup_env
    local row='{"from":"karo-spoof","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"cli-spoof-1","response_by_time":"2020-01-01T00:00:00Z"}'
    local enqueued
    enqueued=$(_invoke_cli_get_enqueued "$row")
    local deny_count
    deny_count=$(_log_count "DENY")
    local result=0
    if [ "$enqueued" != "0" ]; then
        echo "  [FAIL] enqueued=${enqueued} (期待 0)" >&2
        result=1
    fi
    if [ "$deny_count" -lt 1 ]; then
        echo "  [FAIL] DENY 行数=${deny_count} (期待 ≥1)" >&2
        result=1
    fi
    _teardown_env
    return $result
}

# ════════════════════════════════════════════════════════════
# CLI-2: empty-deadline row → enqueued=0 + ANOMALY counter ≥1
# cycle3 fix3 (HIGH-3 cure) で空 deadline は rc=2 anomaly。
# 退行下では rc 破壊で case 0 enqueue 発火、cure では case 2 anomalies 計上。
# ════════════════════════════════════════════════════════════
test_cli_empty_deadline_enqueued_zero() {
    _setup_env
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"cli-empty-dl-1","response_by_time":""}'
    local enqueued
    enqueued=$(_invoke_cli_get_enqueued "$row")
    local anomaly_count
    anomaly_count=$(_log_count "ANOMALY")
    local result=0
    if [ "$enqueued" != "0" ]; then
        echo "  [FAIL] enqueued=${enqueued} (期待 0)" >&2
        result=1
    fi
    if [ "$anomaly_count" -lt 1 ]; then
        echo "  [FAIL] ANOMALY 行数=${anomaly_count} (期待 ≥1)" >&2
        result=1
    fi
    _teardown_env
    return $result
}

# ════════════════════════════════════════════════════════════
# CLI-3: future row → enqueued=0 + FRESH counter ≥1
# cycle3 fix3 で未来 deadline は rc=1 skip + FRESH ログ。
# ════════════════════════════════════════════════════════════
test_cli_future_row_enqueued_zero() {
    _setup_env
    local future
    future=$(date -d "+1 hour" --iso-8601=seconds 2>/dev/null || date -v+1H +%Y-%m-%dT%H:%M:%S 2>/dev/null)
    local row="{\"from\":\"karo-third\",\"recipient\":\"fukuincho\",\"type\":\"auto_poke\",\"status\":\"pending\",\"correlation_id\":\"cli-future-1\",\"response_by_time\":\"$future\"}"
    local enqueued
    enqueued=$(_invoke_cli_get_enqueued "$row")
    local fresh_count
    fresh_count=$(_log_count "FRESH")
    local result=0
    if [ "$enqueued" != "0" ]; then
        echo "  [FAIL] enqueued=${enqueued} (期待 0)" >&2
        result=1
    fi
    if [ "$fresh_count" -lt 1 ]; then
        echo "  [FAIL] FRESH 行数=${fresh_count} (期待 ≥1)" >&2
        result=1
    fi
    _teardown_env
    return $result
}

# ════════════════════════════════════════════════════════════
# CLI-4: inflight row → enqueued=0 + SKIP counter ≥1
# 先に inflight marker を作成しておき、その corr_id の row を流す。
# cycle3 fix2 (HIGH-2 cure) で in_flight 検出 → rc=1 skip。
# ════════════════════════════════════════════════════════════
test_cli_inflight_row_enqueued_zero() {
    _setup_env
    # inflight marker を先置 (lib の sanitize 規則に合致する safe corr_id を直接 mark)
    local cid="cli-inflight-1"
    mkdir -p "$DETECT_STALE_INFLIGHT_DIR"
    : > "${DETECT_STALE_INFLIGHT_DIR}/${cid}.inflight"
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"cli-inflight-1","response_by_time":"2020-01-01T00:00:00Z"}'
    local enqueued
    enqueued=$(_invoke_cli_get_enqueued "$row")
    local skip_count
    skip_count=$(_log_count "SKIP")
    local result=0
    if [ "$enqueued" != "0" ]; then
        echo "  [FAIL] enqueued=${enqueued} (期待 0)" >&2
        result=1
    fi
    if [ "$skip_count" -lt 1 ]; then
        echo "  [FAIL] SKIP 行数=${skip_count} (期待 ≥1、in_flight ログ)" >&2
        result=1
    fi
    _teardown_env
    return $result
}

# ════════════════════════════════════════════════════════════
# CLI-5: 正常な past-stale row → enqueued=1 (positive control、CLI rc 経路の生存確認)
# 全 case が enqueued=0 のみでは「CLI が常に 0 を返す」逆退行を捕捉できないため、
# 正常 stale row 1 件で実 enqueue 経路が動作することを confirm。
# ════════════════════════════════════════════════════════════
test_cli_normal_stale_enqueued_one() {
    _setup_env
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"cli-normal-stale-1","response_by_time":"2020-01-01T00:00:00Z"}'
    local enqueued
    enqueued=$(_invoke_cli_get_enqueued "$row")
    local enqueue_log_count
    enqueue_log_count=$(_log_count "ENQUEUE")
    local result=0
    if [ "$enqueued" != "1" ]; then
        echo "  [FAIL] enqueued=${enqueued} (期待 1、正常 stale 経路)" >&2
        result=1
    fi
    if [ "$enqueue_log_count" -lt 1 ]; then
        echo "  [FAIL] ENQUEUE 行数=${enqueue_log_count} (期待 ≥1)" >&2
        result=1
    fi
    _teardown_env
    return $result
}

# ════════════════════════════════════════════════════════════
# Test list 実行
# ════════════════════════════════════════════════════════════
echo "───────────────────────────────────────"
echo "test_fukuincho_detect_stale_cli.sh"
echo "redo: subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_cycle3_003 (cycle4 fix2)"
echo "scope: CLI rc→enqueue 判定 integration、cycle3 RED-C3 (|| true rc 破壊) 退行捕捉用"
echo "───────────────────────────────────────"

run "CLI-1 ★cycle4 fix2★ spoof row (karo-spoof) → enqueued=0 + DENY ≥1" test_cli_spoof_row_enqueued_zero
run "CLI-2 ★cycle4 fix2★ empty-deadline row → enqueued=0 + ANOMALY ≥1" test_cli_empty_deadline_enqueued_zero
run "CLI-3 ★cycle4 fix2★ future row → enqueued=0 + FRESH ≥1" test_cli_future_row_enqueued_zero
run "CLI-4 ★cycle4 fix2★ inflight row → enqueued=0 + SKIP ≥1" test_cli_inflight_row_enqueued_zero
run "CLI-5 ★cycle4 fix2★ 正常 past-stale row → enqueued=1 (positive control)" test_cli_normal_stale_enqueued_one

echo "───────────────────────────────────────"
echo "PASS=$PASS FAIL=$FAIL SKIP=0"

if [ "$FAIL" -gt 0 ]; then
    echo "───────────────────────────────────────"
    echo "FAILURE DETAILS:"
    for d in "${FAIL_DETAILS[@]}"; do
        echo "  - $d"
    done
    exit 1
fi
echo "★ALL PASS (SKIP=0、CLI rc 経路健全、cycle3 RED-C3 退行なし)★"
exit 0
