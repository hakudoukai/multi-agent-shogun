#!/usr/bin/env bash
# scripts/test_shogun_verify_preflight.sh — shogun_verify_audit.sh --preflight の 6 種 return code 検査
#
# cmd_012 P0-2 完了条件: 6/6 PASS SKIP=0、bash -n PASS、shellcheck warning 0 件。
# 各 case ごとに mock REPO_ROOT を mktemp で作成し、env で REPO_ROOT を差替えてから
# scripts/shogun_verify_audit.sh --preflight <id> を実行、exit code を比較する。

set -uo pipefail  # set -e は外す (= 期待 exit 非 0 を case ごとに評価する都合)

REAL_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$REAL_REPO/scripts/shogun_verify_audit.sh"

pass=0
fail=0
total=0
failures=()

run_case() {
    local name="$1" expected="$2" actual="$3"
    total=$((total + 1))
    if [ "$expected" = "$actual" ]; then
        pass=$((pass + 1))
        echo "PASS: $name (exit=$actual)"
    else
        fail=$((fail + 1))
        failures+=("$name: expected=$expected actual=$actual")
        echo "FAIL: $name (expected=$expected actual=$actual)"
    fi
}

# Test 1: ready_to_verify (exit 0)
# mainpc, verdict=pass, commit_hash 有, log_path 実在 → 全条件クリア
t1_dir="$(mktemp -d)"
mkdir -p "$t1_dir/queue/reports"
: >"$t1_dir/queue/reports/dummy_log.yaml"
cat >"$t1_dir/queue/reports/kuroda_mainpc_report.yaml" <<'YAML'
reports:
  - audit_id: t1_ready_id
    target_pc: mainpc
    verdict: pass
    commit_hash: deadbeefcafe1234
    log_path: queue/reports/dummy_log.yaml
YAML
REPO_ROOT="$t1_dir" bash "$SCRIPT" --preflight t1_ready_id >/dev/null 2>&1
run_case "1-ready_to_verify" 0 $?

# Test 2: missing_audit_entry (exit 1)
# 該当 audit_id がどの report にも index にも存在しない
t2_dir="$(mktemp -d)"
mkdir -p "$t2_dir/queue/reports"
REPO_ROOT="$t2_dir" bash "$SCRIPT" --preflight nonexistent_audit_id_xyz >/dev/null 2>&1
run_case "2-missing_audit_entry" 1 $?

# Test 3: missing_cross_pc_report (exit 2)
# audit_report_index.yaml に target_pc=secondpc 記載、但し SC report file 未到達
t3_dir="$(mktemp -d)"
mkdir -p "$t3_dir/queue/reports"
: >"$t3_dir/queue/reports/dummy_log.yaml"
cat >"$t3_dir/queue/reports/audit_report_index.yaml" <<'YAML'
entries:
  - audit_id: t3_sc_missing_id
    target_pc: secondpc
    section: reports
    auditor_who: naomasa_secondpc
    verdict: pass
    commit_hash: feedface5678
    log_path: queue/reports/dummy_log.yaml
YAML
REPO_ROOT="$t3_dir" bash "$SCRIPT" --preflight t3_sc_missing_id >/dev/null 2>&1
run_case "3-missing_cross_pc_report" 2 $?

# Test 4: unsupported_report_schema (exit 3)
# 未知 section に audit_id がある → schema 認識不能
t4_dir="$(mktemp -d)"
mkdir -p "$t4_dir/queue/reports"
cat >"$t4_dir/queue/reports/kuroda_mainpc_report.yaml" <<'YAML'
weird_unrecognized_block:
  - audit_id: t4_unsupported_id
    target_pc: mainpc
    verdict: pass
YAML
REPO_ROOT="$t4_dir" bash "$SCRIPT" --preflight t4_unsupported_id >/dev/null 2>&1
run_case "4-unsupported_report_schema" 3 $?

# Test 5: partial_verdict_blocked (exit 4)
# verdict=partial → completion gate block
t5_dir="$(mktemp -d)"
mkdir -p "$t5_dir/queue/reports"
: >"$t5_dir/queue/reports/dummy_log.yaml"
cat >"$t5_dir/queue/reports/kuroda_mainpc_report.yaml" <<'YAML'
reports:
  - audit_id: t5_partial_id
    target_pc: mainpc
    verdict: partial
    commit_hash: abcdef123456
    log_path: queue/reports/dummy_log.yaml
YAML
REPO_ROOT="$t5_dir" bash "$SCRIPT" --preflight t5_partial_id >/dev/null 2>&1
run_case "5-partial_verdict_blocked" 4 $?

# Test 6: missing_log_or_commit (exit 5)
# commit_hash 空 + log_path 存在せず
t6_dir="$(mktemp -d)"
mkdir -p "$t6_dir/queue/reports"
cat >"$t6_dir/queue/reports/kuroda_mainpc_report.yaml" <<'YAML'
reports:
  - audit_id: t6_no_evidence_id
    target_pc: mainpc
    verdict: pass
    commit_hash: ""
    log_path: queue/reports/nonexistent_log.yaml
YAML
REPO_ROOT="$t6_dir" bash "$SCRIPT" --preflight t6_no_evidence_id >/dev/null 2>&1
run_case "6-missing_log_or_commit" 5 $?

# Test 7: full verify → audit_report_index.yaml 経由で entry 取得 (NOT_FOUND 解消)
# naomasa_new_001 類似: index-only entry を full verify が見つけること
t7_dir="$(mktemp -d)"
mkdir -p "$t7_dir/queue/reports"
cat >"$t7_dir/queue/reports/audit_report_index.yaml" <<'YAML'
reports:
  - audit_id: t7_index_only_id
    target_id: t7_target
    verdict: fail
    evidence_state: blocked_env
    completion_gate: blocked
    log_path: ''
    commit_hash: ''
    related_files: []
    audited_at: null
YAML
t7_out=$(PC_ID=mainpc REPO_ROOT="$t7_dir" bash "$SCRIPT" t7_index_only_id 2>/dev/null)
if echo "$t7_out" | grep -q '"NOT_FOUND"'; then
    t7_result=1
else
    t7_result=0
fi
run_case "7-full_verify_via_index_not_found_resolved" 0 "$t7_result"

# Test 8: preflight + full verify — 共通 resolver で同一 audit_id の lookup 結果が一致
t8_dir="$(mktemp -d)"
mkdir -p "$t8_dir/queue/reports"
: >"$t8_dir/queue/reports/dummy_log.yaml"
cat >"$t8_dir/queue/reports/audit_report_index.yaml" <<'YAML'
reports:
  - audit_id: t8_shared_id
    target_pc: mainpc
    verdict: pass
    evidence_state: complete
    completion_gate: open
    log_path: queue/reports/dummy_log.yaml
    commit_hash: deadbeef0102abcd
    related_files: []
    audited_at: '2026-05-11T12:00:00+09:00'
YAML
REPO_ROOT="$t8_dir" bash "$SCRIPT" --preflight t8_shared_id >/dev/null 2>&1
t8_preflight=$?
t8_verify=$(PC_ID=mainpc REPO_ROOT="$t8_dir" bash "$SCRIPT" t8_shared_id 2>/dev/null)
if echo "$t8_verify" | grep -q '"NOT_FOUND"'; then
    t8_verify_ok=1
else
    t8_verify_ok=0
fi
if [ "$t8_preflight" = "0" ] && [ "$t8_verify_ok" = "0" ]; then
    t8_result=0
else
    t8_result=1
fi
run_case "8-preflight_full_verify_common_resolver" 0 "$t8_result"

# Test 9: --pc-id 未指定 → mainpc log file が生成される (AC4 default)
t9_dir="$(mktemp -d)"
mkdir -p "$t9_dir/queue/reports"
cat >"$t9_dir/queue/reports/audit_report_index.yaml" <<'YAML'
reports:
  - audit_id: t9_test_id
    verdict: pass
    evidence_state: complete
    completion_gate: open
    log_path: ''
    commit_hash: ''
    related_files: []
    audited_at: null
YAML
REPO_ROOT="$t9_dir" bash "$SCRIPT" t9_test_id >/dev/null 2>&1
if [ -f "$t9_dir/queue/reports/shogun_verification_mainpc_log.yaml" ]; then
    t9_result=0
else
    t9_result=1
fi
run_case "9-default_mainpc_log" 0 "$t9_result"

echo "============================================================"
echo "Total: $total | Pass: $pass | Fail: $fail | SKIP: 0"
if [ "$fail" -ne 0 ]; then
    echo "--- failures ---"
    printf ' - %s\n' "${failures[@]}"
fi
# tmp dir は system /tmp cleanup に委ねる (= D002 安全規律: project tree 外 rm-rf 禁)
[ "$fail" -eq 0 ]
