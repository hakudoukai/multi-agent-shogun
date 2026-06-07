#!/usr/bin/env bash
#
# Enter Restart — shogun-second Watchdog (cycle3 D1 統合後の thin wrapper、横展開 second_pc)
#
# 由来: 副院長令 baabd1ca【enter_restart RED 修正 Phase A 即修正】 + 横展開 (2026-06-03)
#       cycle3 で commander 版+shogun_third 版重複ロジックを共通実装
#       (enter_restart_common_watchdog.sh) に統合、本書は envvar 設定のみ
#       担当する thin wrapper として再構成。second_pc は本 wrapper を配備。
#
# 役割: second_pc shogun-second:0.0 pane の Claude TUI を 10min idle 時に
#       C-m only で Enter restart する (横展開 2 号 second_pc)。
#
# 安全契約 (副院長令 e6b027a6 / docs/runbooks/enter_restart_shogun_reference.md):
#   - 新規コマンド送信絶対禁、send-keys -l 不使用、C-m (Enter) のみ 1 回送信
#   - label 照合 strict (false positive 防止)
#   - 連続発火上限 (15min 内 3 回で HALT)
#   - これらは共通実装 enter_restart_common_watchdog.sh に集約済

set -euo pipefail

# shogun-second 固有の envvar 設定 (差異は本 wrapper のみで完結)
# ★second_pc 配備: tmux session=shogun-second, pane=shogun-second:0.0★
export ER_PANE_TARGET="${ER_PANE_TARGET:-shogun-second:0.0}"
export ER_SESSION_NAME="${ER_SESSION_NAME:-shogun-second}"
export ER_FROM_PC_FILTER="${ER_FROM_PC_FILTER:-second_pc}"
export ER_LOG_DIR="${ER_LOG_DIR:-/home/hakudokai/.local/share/enter_restart_shogun_second}"
export ER_EVENT_TYPE="${ER_EVENT_TYPE:-enter_restart_shogun_second_fire}"
export ER_ROLE_NAME="${ER_ROLE_NAME:-shogun-second}"
export ER_HEARTBEAT_FROM_PC="${ER_HEARTBEAT_FROM_PC:-second_pc}"
export ER_HEARTBEAT_TOPIC_PREFIX="${ER_HEARTBEAT_TOPIC_PREFIX:-[enter_restart] shogun_second alive}"
export ER_CYCLE_LOG_PREFIX="${ER_CYCLE_LOG_PREFIX:-enter_restart_shogun_second}"
# ★横展開 patch (副院長令 baabd1ca, 2026-06-03)★: target_pc envvar 化
export ER_TARGET_PC="${ER_TARGET_PC:-second_pc}"
# python3 binary: second_pc も /usr/bin/python3 + site-packages supabase 利用
export ER_PYTHON3_BIN="${ER_PYTHON3_BIN:-/usr/bin/python3}"
# オプション (default 使用):
#   ER_THRESHOLD_MIN=10  ER_FIRE_CAP_COUNT=3  ER_FIRE_CAP_WINDOW_MIN=15

exec /bin/bash "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/enter_restart_common_watchdog.sh"
