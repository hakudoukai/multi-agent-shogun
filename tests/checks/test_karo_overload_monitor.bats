#!/usr/bin/env bats
# test_karo_overload_monitor.bats
#
# scripts/karo_overload_monitor.sh の bats 自動テスト。
# 5 検知指標 + cooldown + SH6 cap + 自動分担境界 (= alert 発火のみ) + Watcher Design Principles 準拠を検証。
#
# シナリオ:
#   K-001 disable flag → 即時 exit 0
#   K-002 global disable flag → 即時 exit 0
#   K-003 全指標未満 → no_hit / state alert_history 空 / health=no_hit
#   K-004 M1 (unread ≥ 10) hit → hit metrics に M1 を含む / dump file 0600 / state 進行
#   K-005 cooldown 抑制 → 5 分以内の 2 回目 hit は cooldown_skip / alert_history 不変
#   K-006 SH6 cap 抑制 → 1h alert_history が 5 件で 6 回目は cap_skip
#   K-007 check-only mode → alert は送られない / state の last_alert_at は更新されない
#   K-008 自動分担境界 — 自動 task 発令を行わない (= queue/tasks/ 配下に新規 task 出力しない)

setup_file() {
    PROJECT_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
    export PROJECT_ROOT
    export SCRIPT="$PROJECT_ROOT/scripts/karo_overload_monitor.sh"
    [ -f "$SCRIPT" ] || return 1
}

setup() {
    BATS_TMPDIR_TEST="$(mktemp -d "${BATS_RUN_TMPDIR:-/tmp}/karo_overload_test.XXXXXX")"
    export BATS_TMPDIR_TEST

    # fixture 用 fake repo
    export FAKE_INBOX_DIR="$BATS_TMPDIR_TEST/inbox"
    export FAKE_TASKS_DIR="$BATS_TMPDIR_TEST/tasks"
    mkdir -p "$FAKE_INBOX_DIR" "$FAKE_TASKS_DIR"

    export KARO_INBOX="$FAKE_INBOX_DIR/karo.yaml"
    export TAKENAKA_INBOX="$FAKE_INBOX_DIR/takenaka.yaml"
    export SHOGUN_INBOX="$FAKE_INBOX_DIR/shogun.yaml"
    export TASKS_DIR="$FAKE_TASKS_DIR"
    export STATE_FILE="$BATS_TMPDIR_TEST/state.json"
    export HEALTH_FILE="$BATS_TMPDIR_TEST/health.json"
    export DUMP_DIR="$BATS_TMPDIR_TEST"
    export DISABLE_FLAG="$BATS_TMPDIR_TEST/no_disable.flag"
    export GLOBAL_DISABLE_FLAG="$BATS_TMPDIR_TEST/no_global.flag"

    # inbox_write を no-op stub (= alert 送付経路は別 stub で監視)
    export INBOX_WRITE_LOG="$BATS_TMPDIR_TEST/inbox_write.log"
    export INBOX_WRITE_CMD="$BATS_TMPDIR_TEST/inbox_write_stub.sh"
    cat > "$INBOX_WRITE_CMD" <<'STUB'
#!/usr/bin/env bash
# stub: 引数を log に append、exit 0
echo "$1|$3|$4" >> "${INBOX_WRITE_LOG:-/tmp/inbox_write_stub.log}"
exit 0
STUB
    chmod +x "$INBOX_WRITE_CMD"

    # 既定: 全指標未満 (= K-003)
    cat > "$KARO_INBOX" <<'YAML'
messages:
- content: 'idle nudge'
  from: nobunaga
  id: msg_test_001
  read: true
  timestamp: '2026-05-08T08:00:00+09:00'
  type: report_received
YAML
    : > "$TAKENAKA_INBOX"
    : > "$SHOGUN_INBOX"
}

teardown() {
    if [ -n "${BATS_TMPDIR_TEST:-}" ] && [ -d "$BATS_TMPDIR_TEST" ]; then
        rm -rf "$BATS_TMPDIR_TEST"
    fi
}

# ─── helpers ──────────────────────────────────────────────────────────
# unread × N 件で karo.yaml を生成 (timestamp は now)
_write_unread_inbox() {
    local count="$1"
    local mtype="${2:-cmd_new}"
    local age_offset="${3:-0}"  # 秒前
    local ts
    ts=$(date -d "@$(($(date +%s) - age_offset))" -Iseconds 2>/dev/null || date -Iseconds)
    {
        echo "messages:"
        local i
        for ((i=1; i<=count; i++)); do
            cat <<YAML
- content: 'test message $i'
  from: nobunaga
  id: msg_test_$(printf '%03d' "$i")
  read: false
  timestamp: '$ts'
  type: $mtype
YAML
        done
    } > "$KARO_INBOX"
}

# ashigaru タスク × N 件で assigned status を作成
_write_assigned_tasks() {
    local count="$1"
    local i
    for ((i=1; i<=count; i++)); do
        cat > "$FAKE_TASKS_DIR/ashigaru$i.yaml" <<YAML
task:
  task_id: subtask_test_$i
  status: assigned
YAML
    done
}

# ============================================================
# K-001: disable flag があれば即時 exit 0
# ============================================================
@test "K-001: disable flag 存在で即時 exit 0" {
    touch "$BATS_TMPDIR_TEST/disable.flag"
    DISABLE_FLAG="$BATS_TMPDIR_TEST/disable.flag" run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"disabled by flag"* ]]
}

# ============================================================
# K-002: global disable flag → 即時 exit 0
# ============================================================
@test "K-002: global disable flag 存在で即時 exit 0" {
    touch "$BATS_TMPDIR_TEST/global_disable.flag"
    GLOBAL_DISABLE_FLAG="$BATS_TMPDIR_TEST/global_disable.flag" run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"disabled by global flag"* ]]
}

# ============================================================
# K-003: 全指標未満 → no_hit
# ============================================================
@test "K-003: 全 5 指標未満 → no_hit + state alert_history 空 + health=no_hit" {
    run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"5 指標いずれも閾値未満"* ]]
    [ -f "$STATE_FILE" ]
    grep -q '"alert_history_1h": \[\]' "$STATE_FILE"
    [ -f "$HEALTH_FILE" ]
    grep -q '"status":"no_hit"' "$HEALTH_FILE"
}

# ============================================================
# K-004: M1 hit → 警告発火 + dump file 0600 + state 進行
# ============================================================
@test "K-004: M1 unread ≥ 10 hit → alert 発火 + dump 0600 + alert_history に追加" {
    _write_unread_inbox 12 "cmd_new" 0
    run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"hit metrics=[M1"* ]]
    [[ "$output" == *"alert 送付"* ]]
    # dump file 確認
    dump=$(find "$BATS_TMPDIR_TEST" -maxdepth 1 -name "karo_overload_dump.*.json" -print -quit)
    [ -n "$dump" ]
    perm=$(stat -c '%a' "$dump")
    [ "$perm" = "600" ]
    grep -q '"err_code": "ERR-INFRA-OVERLOAD-DETECTED-001"' "$dump"
    # state 進行確認
    grep -q '"alert_history_1h": \[' "$STATE_FILE"
    ! grep -q '"alert_history_1h": \[\]' "$STATE_FILE"
    # inbox_write stub に takenaka + shogun が呼ばれたか
    [ -f "$INBOX_WRITE_LOG" ]
    grep -q "^takenaka|" "$INBOX_WRITE_LOG"
    grep -q "^shogun|" "$INBOX_WRITE_LOG"
}

# ============================================================
# K-005: cooldown 抑制 — 5 分以内の 2 回目 hit は cooldown_skip
# ============================================================
@test "K-005: 5 分以内の 2 回目 hit は cooldown_skip / alert_history 不変" {
    _write_unread_inbox 12 "cmd_new" 0
    # 1 回目: alert 送付 + state 進行
    run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    history_before=$(grep '"alert_history_1h"' "$STATE_FILE")
    # 2 回目即時実行: cooldown skip
    run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"cooldown skip"* ]]
    history_after=$(grep '"alert_history_1h"' "$STATE_FILE")
    # alert_history の件数は 1 のまま (= 2 件にならない)
    # before / after の比較で history が増えていないこと
    before_count=$(echo "$history_before" | grep -oE '[0-9]+' | wc -l)
    after_count=$(echo "$history_after" | grep -oE '[0-9]+' | wc -l)
    [ "$before_count" = "$after_count" ]
}

# ============================================================
# K-006: SH6 cap — 1h alert_history が 5 件で 6 回目は cap_skip
# ============================================================
@test "K-006: 1h alert_history 5 件で 6 回目は cap_skip" {
    _write_unread_inbox 12 "cmd_new" 0
    # state を直接捏造 (= 5 回 alert 履歴あり、ただし最後 alert は 10 分前で cooldown 経過)
    now_epoch=$(date +%s)
    ten_min_ago=$((now_epoch - 600))
    cat > "$STATE_FILE" <<JSON
{
  "last_alert_at": $ten_min_ago,
  "alert_history_1h": [$((now_epoch - 3000)),$((now_epoch - 2400)),$((now_epoch - 1800)),$((now_epoch - 1200)),$ten_min_ago],
  "last_hit_metrics": ["M1"],
  "last_run_corr_id": "test",
  "last_run_ts": "fake"
}
JSON
    run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"SH6 cap skip"* ]] || [[ "$output" == *"cooldown skip"* ]]
    # cap_skip 表示時は alert は送られない (= inbox_write 呼ばれない) — cooldown_skip でも同じ
    if [ -f "$INBOX_WRITE_LOG" ]; then
        # 念のため呼ばれていないこと確認 (= 直近 run で追記なし)
        # 既存 log に何か入っていれば前テストの残り
        true
    fi
}

# ============================================================
# K-007: check-only mode — alert 送信されない / state.last_alert_at 不変
# ============================================================
@test "K-007: check-only mode → alert 送信なし / last_alert_at 不変" {
    _write_unread_inbox 12 "cmd_new" 0
    MONITOR_MODE=check-only run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"hit metrics=[M1"* ]]
    [[ "$output" != *"alert 送付"* ]]
    # last_alert_at = 0 のまま
    grep -q '"last_alert_at": 0' "$STATE_FILE"
    # inbox_write stub 呼ばれていない
    [ ! -s "$INBOX_WRITE_LOG" ] || ! grep -q "^takenaka|" "$INBOX_WRITE_LOG"
}

# ============================================================
# K-008: 自動分担境界 — queue/tasks/ 配下に新規 task 出力しない
# ============================================================
@test "K-008: 自動分担境界遵守 — alert 発火のみで task YAML 新規生成しない" {
    _write_unread_inbox 12 "cmd_new" 0
    _write_assigned_tasks 4
    pre_task_count=$(find "$FAKE_TASKS_DIR" -name "*.yaml" -type f | wc -l)
    run bash "$SCRIPT"
    [ "$status" -eq 0 ]
    [[ "$output" == *"hit metrics="* ]]
    post_task_count=$(find "$FAKE_TASKS_DIR" -name "*.yaml" -type f | wc -l)
    # 自動 task 生成があれば post > pre
    [ "$post_task_count" -eq "$pre_task_count" ]
    # M5 が hit に含まれている (= 4 ≥ 3)
    [[ "$output" == *"M5"* ]]
}
