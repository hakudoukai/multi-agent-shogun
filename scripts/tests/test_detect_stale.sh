#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# test_detect_stale.sh — unit test for scripts/lib/detect_stale.sh
# ═══════════════════════════════════════════════════════════════
# redo: subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_002
#   - gunshi-third RED-3 cure: 本 commit diff 内に test 同梱
#   - gunshi-third RED-2 cure verify: corr_id sanitize (path traversal 防御)
#
# Usage:
#   bash scripts/tests/test_detect_stale.sh
#
# Exit:
#   0 = all PASS
#   1 = at least one FAIL
# ═══════════════════════════════════════════════════════════════

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_PATH="$HERE/../lib/detect_stale.sh"

if [ ! -f "$LIB_PATH" ]; then
    echo "FATAL: lib not found: $LIB_PATH" >&2
    exit 1
fi

# 専用 inflight dir / log (テストごとに reset)
export DETECT_STALE_INFLIGHT_DIR="$(mktemp -d -t fukuincho_inflight_test.XXXXXX)"
export DETECT_STALE_LOG="$(mktemp -t fukuincho_detect_stale_test.XXXXXX.log)"

# shellcheck disable=SC1090
source "$LIB_PATH"

PASS=0
FAIL=0
FAIL_DETAILS=()

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
# 1. status enum 厳密判定 (Codex T1 是正)
# ════════════════════════════════════════════════════════════
test_status_pending_valid() {
    _detect_stale_status_valid "pending"
    [ "$?" -eq 0 ]
}
test_status_in_progress_valid() {
    _detect_stale_status_valid "in_progress"
    [ "$?" -eq 0 ]
}
test_status_confirmed_terminal() {
    _detect_stale_status_valid "confirmed"
    [ "$?" -eq 1 ]
}
test_status_escalated_terminal() {
    _detect_stale_status_valid "escalated"
    [ "$?" -eq 1 ]
}
test_status_human_required_terminal() {
    _detect_stale_status_valid "human_required"
    [ "$?" -eq 1 ]
}
test_status_closed_terminal() {
    _detect_stale_status_valid "closed"
    [ "$?" -eq 1 ]
}
test_status_unknown_anomaly() {
    _detect_stale_status_valid "garbage_status"
    [ "$?" -eq 2 ]
}
test_status_empty_anomaly() {
    _detect_stale_status_valid ""
    [ "$?" -eq 2 ]
}

# ════════════════════════════════════════════════════════════
# 2. corr_id sanitize (★fix2 / RED-2 cure: path traversal 防御★)
# ════════════════════════════════════════════════════════════
test_corr_id_alphanumeric_pass() {
    local out
    out=$(_detect_stale_sanitize_corr_id "poke-abc123")
    [ "$out" = "poke-abc123" ]
}
test_corr_id_underscore_pass() {
    local out
    out=$(_detect_stale_sanitize_corr_id "poke_abc_123")
    [ "$out" = "poke_abc_123" ]
}
test_corr_id_path_traversal_reject() {
    # ★cycle3 fix4 (MED-1 cure)★: basename 正規化廃止、raw 入力をそのまま reject
    # 旧 impl は basename("../../etc/passwd") = "passwd" として「正規化受理」していた
    # 新 impl は raw に "/" や "." を含む時点で regex 不合格 → reject
    if _detect_stale_sanitize_corr_id "../../etc/passwd" > /dev/null 2>&1; then
        return 1   # accept = NG (cycle3 fix4 で reject 必須)
    fi
    return 0
}
test_corr_id_slash_reject() {
    # ★cycle3 fix4 (MED-1 cure)★: スラッシュ含む raw は regex 不合格で reject
    if _detect_stale_sanitize_corr_id "/etc/passwd" > /dev/null 2>&1; then
        return 1   # accept = NG
    fi
    return 0
}
test_corr_id_dotdot_only_reject() {
    # ".." 単独 → basename("..") = ".." → regex ^[A-Za-z0-9_-]+$ 不合格 (. はマッチしない) → reject
    if _detect_stale_sanitize_corr_id ".." > /dev/null 2>&1; then
        return 1  # 通った = NG
    fi
    return 0  # reject された = OK
}
test_corr_id_dollar_injection_reject() {
    if _detect_stale_sanitize_corr_id "abc;rm -rf /" > /dev/null 2>&1; then
        return 1  # 通った = NG
    fi
    return 0
}
test_corr_id_space_reject() {
    if _detect_stale_sanitize_corr_id "abc def" > /dev/null 2>&1; then
        return 1
    fi
    return 0
}
test_corr_id_empty_reject() {
    if _detect_stale_sanitize_corr_id "" > /dev/null 2>&1; then
        return 1
    fi
    return 0
}
test_corr_id_unicode_reject() {
    # 日本語などの Unicode 文字は [A-Za-z0-9_-] 不合格 → reject
    if _detect_stale_sanitize_corr_id "ポーク" > /dev/null 2>&1; then
        return 1
    fi
    return 0
}

# ════════════════════════════════════════════════════════════
# 3. in-flight mark/check/clear
# ════════════════════════════════════════════════════════════
test_inflight_initially_not_marked() {
    if _detect_stale_inflight_check "test-corr-1"; then
        return 1  # 初期 marked = NG
    fi
    return 0
}
test_inflight_mark_then_check() {
    _detect_stale_inflight_mark "test-corr-2"
    if _detect_stale_inflight_check "test-corr-2"; then
        return 0
    fi
    return 1
}
test_inflight_clear() {
    _detect_stale_inflight_mark "test-corr-3"
    _detect_stale_inflight_clear "test-corr-3"
    if _detect_stale_inflight_check "test-corr-3"; then
        return 1  # 残ってる = NG
    fi
    return 0
}
test_inflight_unsafe_corr_id_rejected() {
    # 不正 corr_id で mark 試行 → reject (file 作成されない)
    _detect_stale_inflight_mark ".." 2>/dev/null
    # 直後に check (不正 corr_id ゆえ check も reject)
    if _detect_stale_inflight_check ".." 2>/dev/null; then
        return 1
    fi
    # 念のため inflight dir に "..inflight" or 似た file が作成されていないか
    if find "$DETECT_STALE_INFLIGHT_DIR" -name "*passwd*" -o -name "..*" 2>/dev/null | grep -q '.'; then
        return 1
    fi
    return 0
}

# ════════════════════════════════════════════════════════════
# 4. authz_check (S1 cure + ★cycle3 fix1 HIGH-1 cure★: sender x recipient x type 完全一致 allowlist)
# ════════════════════════════════════════════════════════════
test_authz_trusted_from_pass() {
    # ★cycle3 fix1★: recipient + type 明示 (allowlist 完全一致経路)
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"abc"}'
    _detect_stale_authz_check "$row"
    [ "$?" -eq 0 ]
}
test_authz_unknown_from_reject() {
    local row='{"from":"intruder-bot","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"abc"}'
    if _detect_stale_authz_check "$row" 2>/dev/null; then
        return 1
    fi
    return 0
}
test_authz_all_5_layers() {
    for from in "commander-third" "shogun-third" "karo-third" "gunshi-third" "ashigaru-third-3"; do
        local row="{\"from\":\"$from\",\"recipient\":\"fukuincho\",\"type\":\"auto_poke\",\"status\":\"pending\",\"correlation_id\":\"abc\"}"
        if ! _detect_stale_authz_check "$row"; then
            return 1
        fi
    done
    return 0
}

# ★cycle3 fix1 HIGH-1 cure★ — spoof attack reject (prefix glob 廃止検証)
test_authz_karo_spoof_reject() {
    # 旧 prefix glob (karo-*) では karo-spoof / karo-fake / karo-third-evil が通過していた
    # 新 allowlist 完全一致では reject 必達
    for spoof in "karo-spoof" "karo-fake" "karo-third-evil" "karo-third-2" "shogun-fake" "ashigaru-third-999"; do
        local row="{\"from\":\"$spoof\",\"recipient\":\"fukuincho\",\"type\":\"auto_poke\",\"status\":\"pending\",\"correlation_id\":\"abc\"}"
        if _detect_stale_authz_check "$row" 2>/dev/null; then
            echo "  spoof '$spoof' should be rejected but was accepted" >&2
            return 1
        fi
    done
    return 0
}
test_authz_unknown_recipient_reject() {
    # recipient=不明 → allowlist miss
    local row='{"from":"karo-third","recipient":"unknown-target","type":"auto_poke","status":"pending","correlation_id":"abc"}'
    if _detect_stale_authz_check "$row" 2>/dev/null; then
        return 1
    fi
    return 0
}
test_authz_unknown_type_reject() {
    # type=不明 → allowlist miss
    local row='{"from":"karo-third","recipient":"fukuincho","type":"malicious_action","status":"pending","correlation_id":"abc"}'
    if _detect_stale_authz_check "$row" 2>/dev/null; then
        return 1
    fi
    return 0
}
test_authz_handshake_type_pass() {
    # type=handshake は allowlist に含む
    local row='{"from":"karo-third","recipient":"fukuincho","type":"handshake","status":"pending","correlation_id":"abc"}'
    _detect_stale_authz_check "$row"
    [ "$?" -eq 0 ]
}

# ════════════════════════════════════════════════════════════
# 5. detect_stale_evaluate_row 統合 (status + authz + corr_id + in-flight)
# ════════════════════════════════════════════════════════════
test_evaluate_row_normal_stale() {
    # ★cycle3 fix3 cure★: 過去 deadline で STALE 判定 (空 deadline は anomaly になるため)
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"eval-norm-1","response_by_time":"2020-01-01T00:00:00Z"}'
    detect_stale_evaluate_row "$row"
    [ "$?" -eq 0 ]
}
test_evaluate_row_confirmed_skip() {
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"confirmed","correlation_id":"eval-conf-1","response_by_time":"2020-01-01T00:00:00Z"}'
    detect_stale_evaluate_row "$row"
    [ "$?" -eq 1 ]
}
test_evaluate_row_malformed_status_anomaly() {
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"garbage","correlation_id":"eval-mal-1","response_by_time":"2020-01-01T00:00:00Z"}'
    detect_stale_evaluate_row "$row"
    [ "$?" -eq 2 ]
}
test_evaluate_row_unauthorized_reject() {
    local row='{"from":"intruder","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"eval-unauth-1","response_by_time":"2020-01-01T00:00:00Z"}'
    detect_stale_evaluate_row "$row"
    [ "$?" -eq 1 ]
}
test_evaluate_row_unsafe_corr_id_reject() {
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"..","response_by_time":"2020-01-01T00:00:00Z"}'
    detect_stale_evaluate_row "$row"
    [ "$?" -eq 1 ]
}
test_evaluate_row_inflight_skip() {
    _detect_stale_inflight_mark "eval-inflight-1"
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"eval-inflight-1","response_by_time":"2020-01-01T00:00:00Z"}'
    detect_stale_evaluate_row "$row"
    local rc=$?
    _detect_stale_inflight_clear "eval-inflight-1"
    [ "$rc" -eq 1 ]
}

# ════════════════════════════════════════════════════════════
# 6. ★cycle3 fix3 (HIGH-3 cure)★ — deadline 境界 (empty/malformed/future/past)
# ════════════════════════════════════════════════════════════
test_evaluate_deadline_empty_anomaly() {
    # 空 deadline → ANOMALY (rc=2)、auto-poke 禁
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"dl-empty-1","response_by_time":""}'
    detect_stale_evaluate_row "$row"
    [ "$?" -eq 2 ]
}
test_evaluate_deadline_malformed_anomaly() {
    # parse 不能 deadline → ANOMALY (rc=2)
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"dl-mal-1","response_by_time":"not-a-date-garbage"}'
    detect_stale_evaluate_row "$row"
    [ "$?" -eq 2 ]
}
test_evaluate_deadline_future_fresh() {
    # 未来 deadline → FRESH (rc=1)
    local future
    future=$(date -d "+1 hour" --iso-8601=seconds 2>/dev/null || date -v+1H +%Y-%m-%dT%H:%M:%S 2>/dev/null)
    local row="{\"from\":\"karo-third\",\"recipient\":\"fukuincho\",\"type\":\"auto_poke\",\"status\":\"pending\",\"correlation_id\":\"dl-fut-1\",\"response_by_time\":\"$future\"}"
    detect_stale_evaluate_row "$row"
    [ "$?" -eq 1 ]
}
test_evaluate_deadline_past_stale() {
    # 過去 deadline → STALE (rc=0、enqueue 推奨)
    local row='{"from":"karo-third","recipient":"fukuincho","type":"auto_poke","status":"pending","correlation_id":"dl-past-1","response_by_time":"2020-01-01T00:00:00Z"}'
    detect_stale_evaluate_row "$row"
    [ "$?" -eq 0 ]
}

# ════════════════════════════════════════════════════════════
# 7. ★cycle3 fix2 (HIGH-2 cure)★ — flock atomic check-and-mark race test
# ════════════════════════════════════════════════════════════
test_atomic_check_and_mark_first_wins() {
    # 1st call → 0 (newly marked), 2nd call → 1 (already inflight)
    local cid="race-${RANDOM}-${RANDOM}"
    _detect_stale_inflight_check_and_mark "$cid"
    local rc1=$?
    _detect_stale_inflight_check_and_mark "$cid"
    local rc2=$?
    _detect_stale_inflight_clear "$cid"
    [ "$rc1" -eq 0 ] && [ "$rc2" -eq 1 ]
}

test_atomic_parallel_race_single_winner() {
    # 並行 cron 2 発を模す: bg で 2 process が同時 check_and_mark、勝者 1 + 敗者 1 を verify
    local cid="parallel-${RANDOM}-${RANDOM}"
    local tmpdir
    tmpdir=$(mktemp -d)
    (
        _detect_stale_inflight_check_and_mark "$cid"
        echo $? > "$tmpdir/rc1"
    ) &
    local pid1=$!
    (
        _detect_stale_inflight_check_and_mark "$cid"
        echo $? > "$tmpdir/rc2"
    ) &
    local pid2=$!
    wait $pid1
    wait $pid2
    local rc1 rc2
    rc1=$(cat "$tmpdir/rc1" 2>/dev/null)
    rc2=$(cat "$tmpdir/rc2" 2>/dev/null)
    _detect_stale_inflight_clear "$cid"
    rm -rf "$tmpdir"
    # 排他制御により 0 と 1 が 1 件ずつ (両 0 も両 1 も race 違反)
    if { [ "$rc1" = "0" ] && [ "$rc2" = "1" ]; } || { [ "$rc1" = "1" ] && [ "$rc2" = "0" ]; }; then
        return 0
    fi
    echo "  race outcome: rc1=$rc1 rc2=$rc2 (期待 = 一方が 0、他方が 1)" >&2
    return 1
}

test_atomic_unsafe_corr_id_rejected() {
    # 不正 corr_id → rc=2 (unsafe)
    _detect_stale_inflight_check_and_mark ".." 2>/dev/null
    local rc=$?
    [ "$rc" -eq 2 ]
}

# ════════════════════════════════════════════════════════════
# 8. ★cycle3 fix4 (MED-1 cure)★ — 危険 ID reject (basename 廃止)
# ════════════════════════════════════════════════════════════
test_sanitize_dangerous_traversal_reject() {
    # ../../etc/passwd は新 impl で reject 必達 (旧 basename impl は passwd へ正規化受理)
    if _detect_stale_sanitize_corr_id "../../etc/passwd" > /dev/null 2>&1; then
        return 1   # accept = NG
    fi
    return 0
}
test_sanitize_absolute_path_reject() {
    if _detect_stale_sanitize_corr_id "/var/log/syslog" > /dev/null 2>&1; then
        return 1
    fi
    return 0
}
test_sanitize_collision_input_reject() {
    # 異なる raw が basename で同じ ID へ正規化される collision attack
    # 旧 impl: "evil/passwd" と "passwd" が両方 passwd へ → mark 衝突温床
    # 新 impl: 前者は "/" 含有で reject
    if _detect_stale_sanitize_corr_id "evil/passwd" > /dev/null 2>&1; then
        return 1   # collision input accept = NG
    fi
    # clean な passwd は依然受理可
    local out
    out=$(_detect_stale_sanitize_corr_id "passwd")
    [ "$out" = "passwd" ]
}

# ════════════════════════════════════════════════════════════
# Test list 実行
# ════════════════════════════════════════════════════════════
echo "───────────────────────────────────────"
echo "test_detect_stale.sh"
echo "redo: subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_002"
echo "───────────────────────────────────────"

# status enum
run "1.1 status pending = valid" test_status_pending_valid
run "1.2 status in_progress = valid" test_status_in_progress_valid
run "1.3 status confirmed = terminal (skip)" test_status_confirmed_terminal
run "1.4 status escalated = terminal (skip)" test_status_escalated_terminal
run "1.5 status human_required = terminal (skip)" test_status_human_required_terminal
run "1.6 status closed = terminal (skip)" test_status_closed_terminal
run "1.7 status unknown = anomaly" test_status_unknown_anomaly
run "1.8 status empty = anomaly" test_status_empty_anomaly

# corr_id sanitize (★fix2 / RED-2 cure★)
run "2.1 ★fix2★ alphanumeric corr_id pass" test_corr_id_alphanumeric_pass
run "2.2 ★fix2★ underscore corr_id pass" test_corr_id_underscore_pass
run "2.3 ★fix2★ '..' 単独 → reject" test_corr_id_dotdot_only_reject
run "2.4 ★fix2★ shell injection ';rm -rf' → reject" test_corr_id_dollar_injection_reject
run "2.5 ★fix2★ space 含む → reject" test_corr_id_space_reject
run "2.6 ★fix2★ empty → reject" test_corr_id_empty_reject
run "2.7 ★fix2★ unicode (日本語) → reject" test_corr_id_unicode_reject

# in-flight
run "3.1 in-flight initially not marked" test_inflight_initially_not_marked
run "3.2 in-flight mark→check" test_inflight_mark_then_check
run "3.3 in-flight clear" test_inflight_clear
run "3.4 ★fix2★ unsafe corr_id で in-flight mark/check 拒否" test_inflight_unsafe_corr_id_rejected

# authz
run "4.1 trusted from pass (karo-third)" test_authz_trusted_from_pass
run "4.2 unknown from reject" test_authz_unknown_from_reject
run "4.3 全 5 layer (commander/shogun/karo/gunshi/ashigaru) pass" test_authz_all_5_layers
run "4.4 ★cycle3 fix1 HIGH-1★ karo-spoof / karo-fake / evil prefix attack reject" test_authz_karo_spoof_reject
run "4.5 ★cycle3 fix1 HIGH-1★ unknown recipient reject (matrix miss)" test_authz_unknown_recipient_reject
run "4.6 ★cycle3 fix1 HIGH-1★ unknown type reject (matrix miss)" test_authz_unknown_type_reject
run "4.7 ★cycle3 fix1 HIGH-1★ type=handshake matrix pass" test_authz_handshake_type_pass

# 統合
run "5.1 evaluate_row normal stale → enqueue 推奨" test_evaluate_row_normal_stale
run "5.2 evaluate_row confirmed → skip" test_evaluate_row_confirmed_skip
run "5.3 evaluate_row malformed status → anomaly" test_evaluate_row_malformed_status_anomaly
run "5.4 evaluate_row unauthorized → skip" test_evaluate_row_unauthorized_reject
run "5.5 ★fix2★ evaluate_row unsafe corr_id → skip" test_evaluate_row_unsafe_corr_id_reject
run "5.6 evaluate_row in-flight → skip" test_evaluate_row_inflight_skip

# deadline 境界 (★cycle3 fix3 HIGH-3 cure★)
run "6.1 ★cycle3 fix3 HIGH-3★ empty deadline → anomaly (auto-poke 禁)" test_evaluate_deadline_empty_anomaly
run "6.2 ★cycle3 fix3 HIGH-3★ malformed deadline → anomaly (auto-poke 禁)" test_evaluate_deadline_malformed_anomaly
run "6.3 ★cycle3 fix3 HIGH-3★ future deadline → fresh (skip)" test_evaluate_deadline_future_fresh
run "6.4 ★cycle3 fix3 HIGH-3★ past deadline → stale (enqueue 推奨)" test_evaluate_deadline_past_stale

# flock atomic check_and_mark (★cycle3 fix2 HIGH-2 cure★)
run "7.1 ★cycle3 fix2 HIGH-2★ atomic first wins、second skipped" test_atomic_check_and_mark_first_wins
run "7.2 ★cycle3 fix2 HIGH-2★ parallel race: 一方のみが winner (race test)" test_atomic_parallel_race_single_winner
run "7.3 ★cycle3 fix2 HIGH-2★ atomic with unsafe corr_id → unsafe rc=2" test_atomic_unsafe_corr_id_rejected

# 危険 ID reject (★cycle3 fix4 MED-1 cure★、basename 廃止検証)
run "8.1 ★cycle3 fix4 MED-1★ traversal '../../etc/passwd' → reject" test_sanitize_dangerous_traversal_reject
run "8.2 ★cycle3 fix4 MED-1★ absolute '/var/log/syslog' → reject" test_sanitize_absolute_path_reject
run "8.3 ★cycle3 fix4 MED-1★ collision input 'evil/passwd' → reject、clean 'passwd' → pass" test_sanitize_collision_input_reject

echo "───────────────────────────────────────"
echo "PASS=$PASS FAIL=$FAIL SKIP=0"

# cleanup
rm -rf "$DETECT_STALE_INFLIGHT_DIR" 2>/dev/null
rm -f "$DETECT_STALE_LOG" 2>/dev/null

if [ "$FAIL" -gt 0 ]; then
    echo "───────────────────────────────────────"
    echo "FAILURE DETAILS:"
    for d in "${FAIL_DETAILS[@]}"; do
        echo "  - $d"
    done
    exit 1
fi
echo "★ALL PASS (SKIP=0、FKI-AUDIT-GREEN-TRUTH-01 順守)★"
exit 0
