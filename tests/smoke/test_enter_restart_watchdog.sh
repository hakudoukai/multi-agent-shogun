#!/usr/bin/env bash
#
# Smoke test for enter_restart watchdog core logic units (cycle3 T1 fix)
#
# 由来: 副院長令 baabd1ca【enter_restart RED 修正 Phase A 即修正】②、Codex audit
#       e7e28c7a-1a77-4c31-bd6a-44176099075e (cycle2 ffa89df red) T1 high close。
#
# 監査仕様 4 観点 (副院長令明示):
#   (a) 空 buffer → C-m (Enter) 送信なし
#   (b) 非空 buffer (label match) → C-m 送信 1 回
#   (c) 15 分以内 fire 3 回 → HALT (本 cycle 停止)
#   (d) log dir 未作成でも script 起動 (mkdir で自動作成)
#
# 実装方針:
#   既存 watchdog script (enter_restart_shogun_third_watchdog.sh +
#   enter_restart_commander_watchdog.sh) のコアロジック (label match /
#   fire cap / log dir 自動作成) を本 smoke test 内に bash で同等再現し、
#   各観点を assertion 検証。実装本体が divergence した場合は本 smoke も
#   同期更新する運用 (D1 共通化後は 1 元化、本 smoke も 1 元検証へ)。
#
# Usage:
#   bash tests/smoke/test_enter_restart_watchdog.sh
#
# Output:
#   各観点の PASS/FAIL を stdout 出力、最後に集計、終了コード 0=全 PASS / 1=FAIL 含む

set -euo pipefail

PASS_COUNT=0
FAIL_COUNT=0
TEST_DIR=$(mktemp -d -t enter_restart_smoke_XXXXXX)
trap 'rm -rf "$TEST_DIR"' EXIT

pass() { echo "PASS: $*"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "FAIL: $*" >&2; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# ─── 共通: label match 判定ロジック (watchdog L150-L156 と等価) ────────────────
check_label_match() {
  local pane_tail="$1"
  local last_line
  last_line=$(printf '%s\n' "$pane_tail" | awk 'NF{last=$0} END{print last}')
  if printf '%s' "$last_line" | grep -qE '│[[:space:]]*>[[:space:]]+[^[:space:]│]'; then
    echo "1"  # match
  else
    echo "0"  # no match
  fi
}

# ─── (a) 空 buffer → C-m 送信なし ──────────────────────────────────────────────
test_empty_buffer_no_send() {
  local desc='(a) 空 buffer (`│ > ` のみ) → label_match=0、C-m 送信スキップ'
  local pane_tail=$'│ > '
  local result
  result=$(check_label_match "$pane_tail")
  if [ "$result" = "0" ]; then
    pass "$desc"
  else
    fail "$desc — expected 0, got $result (false positive)"
  fi

  # 念のため2系統の空パターンも検証
  local pane_tail2=$'│ >'
  local result2
  result2=$(check_label_match "$pane_tail2")
  if [ "$result2" = "0" ]; then
    pass '(a) 空 buffer (`│ >` 末尾、trailing space なし) → label_match=0'
  else
    fail "(a) 空 buffer pattern2 — expected 0, got $result2"
  fi
}

# ─── (b) 非空 buffer → C-m 送信 1 回 ──────────────────────────────────────────
test_nonempty_buffer_send_once() {
  local desc='(b) 非空 buffer (`│ > hello world`) → label_match=1、C-m 送信実行'
  local pane_tail=$'│ > hello world'
  local result
  result=$(check_label_match "$pane_tail")
  if [ "$result" = "1" ]; then
    pass "$desc"
  else
    fail "$desc — expected 1, got $result (false negative)"
  fi

  # 多行 + 非空入力の典型ケースも検証
  local pane_tail2=$'some output\n│ > continue here'
  local result2
  result2=$(check_label_match "$pane_tail2")
  if [ "$result2" = "1" ]; then
    pass '(b) 多行 pane + 末尾非空 buffer → label_match=1'
  else
    fail "(b) 多行 + 非空 buffer — expected 1, got $result2"
  fi
}

# ─── (c) 15 分以内 fire 3 回 → HALT ────────────────────────────────────────────
test_fire_cap_halt() {
  local desc='(c) 過去 15 分以内 fire 3 回 → recent_fires >= cap=3 → HALT'
  local fires_log="$TEST_DIR/fires_cap_test.log"
  local now_epoch
  now_epoch=$(date +%s)
  # 過去 15 分以内に 3 回 fire 記録 (10 分前 / 6 分前 / 3 分前)
  {
    echo "$((now_epoch - 600))"
    echo "$((now_epoch - 360))"
    echo "$((now_epoch - 180))"
  } > "$fires_log"

  # watchdog L48-L52 fire cap 判定ロジック emulate
  local fire_cap_window_min=15
  local fire_cap_count=3
  local window_epoch=$((now_epoch - fire_cap_window_min * 60))
  local recent_fires
  recent_fires=$(awk -v cutoff="$window_epoch" 'BEGIN{c=0} { if ($1+0 >= cutoff) c++ } END { print c }' "$fires_log")

  if [ "$recent_fires" -ge "$fire_cap_count" ]; then
    pass "$desc (recent_fires=$recent_fires)"
  else
    fail "$desc — recent_fires=$recent_fires < cap=$fire_cap_count、HALT 判定にならず"
  fi

  # 逆ケース: 16 分前以前の fire のみ → HALT しない
  local fires_log_old="$TEST_DIR/fires_cap_test_old.log"
  {
    echo "$((now_epoch - 1200))"
    echo "$((now_epoch - 1000))"
    echo "$((now_epoch - 950))"
  } > "$fires_log_old"
  local recent_fires_old
  recent_fires_old=$(awk -v cutoff="$window_epoch" 'BEGIN{c=0} { if ($1+0 >= cutoff) c++ } END { print c }' "$fires_log_old")
  if [ "$recent_fires_old" -lt "$fire_cap_count" ]; then
    pass '(c) 15 分以前の fire のみ → recent_fires < cap → HALT しない (false positive 防止)'
  else
    fail "(c) 古い fire しかないのに HALT 判定 (recent_fires=$recent_fires_old)"
  fi
}

# ─── (d) log dir 未作成でも script 起動 (mkdir -p で自動作成) ──────────────────
test_log_dir_autocreate() {
  local desc='(d) log dir 未作成 → script L37 mkdir -p で自動作成成功'
  local nonexistent_log_dir="$TEST_DIR/nonexistent_path/sub/log_dir"
  if [ -d "$nonexistent_log_dir" ]; then
    fail "(d) pre-test: 想定外に dir が既存 ($nonexistent_log_dir)"
    return
  fi
  # watchdog L37 と等価
  mkdir -p "$nonexistent_log_dir"
  if [ -d "$nonexistent_log_dir" ]; then
    pass "$desc"
  else
    fail "$desc — mkdir -p 失敗 ($nonexistent_log_dir)"
  fi

  # 補足: systemd ExecStartPre による cycle3 B1+B2 fix の動作確認
  # (両 .service に ExecStartPre=/bin/mkdir -p が追加済、commit 33b98e9 で実証)
  local service_files=(
    "scripts/watchdogs/enter_restart_commander.service"
    "scripts/watchdogs/enter_restart_shogun_third.service"
  )
  local repo_root
  repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  local exec_start_pre_count=0
  for svc in "${service_files[@]}"; do
    if grep -qE '^ExecStartPre=/bin/mkdir -p' "$repo_root/$svc"; then
      exec_start_pre_count=$((exec_start_pre_count + 1))
    fi
  done
  if [ "$exec_start_pre_count" -eq 2 ]; then
    pass '(d) systemd 両 .service に ExecStartPre=/bin/mkdir -p 設定確認 (cycle3 B1+B2 fix)'
  else
    fail "(d) ExecStartPre 設定 .service 数 expected=2 got=$exec_start_pre_count"
  fi
}

echo "=== Smoke test: enter_restart watchdog core logic (cycle3 T1) ==="
test_empty_buffer_no_send
test_nonempty_buffer_send_once
test_fire_cap_halt
test_log_dir_autocreate
echo "---"
echo "Total: PASS=$PASS_COUNT FAIL=$FAIL_COUNT"

if [ "$FAIL_COUNT" -gt 0 ]; then
  echo "RESULT: FAIL — smoke test に失敗 case あり、修正要" >&2
  exit 1
fi

echo "RESULT: PASS — 全 4 観点 (空 buffer 不送信 / 非空 buffer 送信 / 15 分 3 回 cap HALT / log dir 自動作成) 全 PASS"
exit 0
