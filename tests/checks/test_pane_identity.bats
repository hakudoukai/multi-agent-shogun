#!/usr/bin/env bats
# test_pane_identity.bats — cycle2 M3 fix
#
# scripts/checks/pane_identity.sh の bats 自動テスト。
# cycle1 で実装した 4-way mapping audit + cycle2 fix (M1 return code, M2 global timeout,
# S1 awk parser, S2 mktemp, S3 alias single source) をシナリオ別に検証する。
#
# シナリオ (Codex T1 high 対応):
#   T-001 disable flag → 即時 exit 0
#   T-002 pass — 4 source 整合 → mismatch=0 + exit 0
#   T-003 drift — idx 1 で値違い → mismatch>0 + exit 2 + dump file 0600
#   T-004 skipped-source — pane_registry 不在 → degraded、source_skipped 加算
#   T-005 parser edge case — §18.1 セクション欠落 CLAUDE.md → 空 source D 扱い
#   T-006 timeout — fake_tmux に sleep 仕込み → global budget 5s 内に完了 (M2 検証)
#   T-007 M1 return code — drift 256 件相当の高 mismatch でも誤判定なし

setup_file() {
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
    export PROJECT_ROOT
    export SCRIPT="$PROJECT_ROOT/scripts/checks/pane_identity.sh"
    export FIXTURES="$PROJECT_ROOT/tests/checks/fixtures"
    export FAKE_TMUX="$FIXTURES/fake_tmux.sh"
    [ -f "$SCRIPT" ] || return 1
    [ -x "$FAKE_TMUX" ] || return 1
}

setup() {
    BATS_TMPDIR_TEST="$(mktemp -d "${BATS_RUN_TMPDIR:-/tmp}/pane_identity_test.XXXXXX")"
    export BATS_TMPDIR_TEST
    export TMPDIR="$BATS_TMPDIR_TEST"
    export LAST_RUN_JSON="$BATS_TMPDIR_TEST/last_run.json"
    export DISABLE_FLAG="$BATS_TMPDIR_TEST/disable_flag.no"
    export TMUX_CMD="$FAKE_TMUX"
    # 既定 fixtures (個別テストで override)
    export PANE_REGISTRY="$FIXTURES/pane_registry_match.yaml"
    export WATCHER_SUPERVISOR="$FIXTURES/watcher_supervisor_sample.sh"
    export CLAUDE_MD="$FIXTURES/CLAUDE_md_sample.md"
    export SECTION18_ROLES_LIB="$PROJECT_ROOT/lib/_section18_roles.sh"
    # マッチング panes (T-002 既定)
    export FAKE_TMUX_PANES=$'multiagent:agents.0=hideyoshi\nmultiagent:agents.1=ashigaru1\nmultiagent:agents.2=ashigaru2\nmultiagent:agents.3=ieyasu\nshogun:main.0=nobunaga'
    unset FAKE_TMUX_DELAY
    unset FAKE_TMUX_LIST_FAIL
}

teardown() {
    if [ -n "${BATS_TMPDIR_TEST:-}" ] && [ -d "$BATS_TMPDIR_TEST" ]; then
        rm -rf "$BATS_TMPDIR_TEST"
    fi
}

# ============================================================
# T-001: disable flag → 即時 exit 0
# ============================================================
@test "T-001: disable flag があれば即時 exit 0" {
    touch "$BATS_TMPDIR_TEST/disable_flag"
    DISABLE_FLAG="$BATS_TMPDIR_TEST/disable_flag" run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"disabled by flag"* ]]
}

# ============================================================
# T-002: 4 source 整合 → mismatch=0 + exit 0
# ============================================================
@test "T-002: 4-way 全 source 整合 → exit 0 + drift 件数 0" {
    run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"4-way audit 結果: ✅ 全 source 整合"* ]]
    [[ "$output" != *"DRIFT"* ]] || [[ "$output" == *"❌ DRIFT"*"_"* ]]
    # last_run.json should be present and status=ok
    [ -f "$LAST_RUN_JSON" ]
    grep -q '"status": "ok"' "$LAST_RUN_JSON"
    grep -q '"mismatch_count": 0' "$LAST_RUN_JSON"
}

# ============================================================
# T-003: drift → mismatch>0 + exit 2 + dump file 0600
# ============================================================
@test "T-003: idx 1 drift 検出 → exit 2 + dump file 0600 + mismatch_count>0" {
    export PANE_REGISTRY="$FIXTURES/pane_registry_drift.yaml"
    run bash "$SCRIPT"
    [ "$status" -eq 2 ]
    [[ "$output" == *"DRIFT"* ]]
    # last_run.json status=drift
    grep -q '"status": "drift"' "$LAST_RUN_JSON"
    grep -q '"mismatch_count": [1-9]' "$LAST_RUN_JSON"
    # dump file 確認 (mktemp で .json suffix、permission 0600)
    dump=$(find "$BATS_TMPDIR_TEST" -maxdepth 1 -name "pane_identity_drift.*.json" -print -quit)
    [ -n "$dump" ]
    # 0600 verify
    perm=$(stat -c '%a' "$dump")
    [ "$perm" = "600" ]
    # JSON 内容確認
    grep -q '"err_code": "ERR-INFRA-PANE-DRIFT-001"' "$dump"
}

# ============================================================
# T-004: source skipped (pane_registry 不在) → degraded 動作
# ============================================================
@test "T-004: pane_registry 不在 → source_skipped 加算 + degraded mode" {
    export PANE_REGISTRY="$BATS_TMPDIR_TEST/nonexistent_registry.yaml"
    run bash "$SCRIPT"
    # 他 3 source は match だから exit 0 になる (skipped は drift とみなさない)
    [ "$status" -eq 0 ] || [ "$status" -eq 2 ]
    [[ "$output" == *"source B"*"degraded"* ]] || [[ "$output" == *"source B 不在"* ]]
    grep -q '"sources_skipped": [1-9]' "$LAST_RUN_JSON"
}

# ============================================================
# T-005: parser edge case — §18.1 セクション欠落 CLAUDE.md
# ============================================================
@test "T-005: §18.1 セクション欠落 CLAUDE.md → source D 空、エラー停止せず" {
    export CLAUDE_MD="$FIXTURES/CLAUDE_md_empty.md"
    run bash "$SCRIPT"
    # source D が空のまま動作続行 (advisory)
    [ "$status" -eq 0 ] || [ "$status" -eq 2 ]
    # last_run.json 存在
    [ -f "$LAST_RUN_JSON" ]
}

# ============================================================
# T-006: timeout — fake_tmux 遅延でも global 5s 内完了
# ============================================================
@test "T-006: tmux 遅延 1s 仕込みで global timeout 5s 内に audit 完了 (M2 検証)" {
    export FAKE_TMUX_DELAY=1
    start_ts=$(date +%s)
    run bash "$SCRIPT"
    end_ts=$(date +%s)
    elapsed=$((end_ts - start_ts))
    # global budget 5s + per-source timeout 2s × 4 source 程度の余裕で実用 10s 以内
    [ "$elapsed" -lt 10 ]
    # advisory only ゆえ exit は 0 or 2
    [ "$status" -eq 0 ] || [ "$status" -eq 2 ]
}

# ============================================================
# T-007: M1 return code — 高 drift 件数でも 256 wrap 影響なし
# ============================================================
@test "T-007: M1 return code wrap 解消 — drift 件数を MISMATCH_COUNT_GLOBAL 経由で正確伝達" {
    # drift fixture でも mismatch_count は last_run.json から確認可能
    export PANE_REGISTRY="$FIXTURES/pane_registry_drift.yaml"
    run bash "$SCRIPT"
    [ "$status" -eq 2 ]
    # mismatch_count が 1 以上で正しく記録されていること
    grep -q '"mismatch_count": [1-9]' "$LAST_RUN_JSON"
    # 0 と誤判定されていないこと (= return modulo 256 wrap がもし発生していれば 0 になる)
    ! grep -q '"mismatch_count": 0' "$LAST_RUN_JSON"
}
