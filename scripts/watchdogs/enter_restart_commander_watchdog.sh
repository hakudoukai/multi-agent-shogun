#!/usr/bin/env bash
#
# Enter Restart — Commander Watchdog (cycle3 D1 統合後の thin wrapper)
#
# 由来: 副院長令 baabd1ca【enter_restart RED 修正 Phase A 即修正】③、Codex audit
#       e7e28c7a-1a77-4c31-bd6a-44176099075e (cycle2 ffa89df red) D1 high 順守。
#       cycle3 で commander 版+shogun_third 版重複ロジックを共通実装
#       (enter_restart_common_watchdog.sh) に統合、本書は envvar 設定のみ
#       担当する thin wrapper として再構成。
#
# 役割: third_pc commander-third:0.0 pane の Commander TUI を 10min idle 時に
#       C-m only で Enter restart する (Phase 2 (β) third_pc local 番人)。
#
# 安全契約 (副院長令 e6b027a6 / docs/runbooks/enter_restart_shogun_reference.md):
#   - 新規コマンド送信絶対禁、send-keys -l 不使用、C-m (Enter) のみ 1 回送信
#   - label 照合 strict (false positive 防止)
#   - 連続発火上限 (15min 内 3 回で HALT)
#   - これらは共通実装 enter_restart_common_watchdog.sh に集約済

set -euo pipefail

# Commander 固有の envvar 設定 (差異は本 wrapper のみで完結)
# ★cycle4 Q1 fix: ${VAR:-default} 形で外部 override 可能化 (smoke test stub 用)★
export ER_PANE_TARGET="${ER_PANE_TARGET:-commander-third:0.0}"
export ER_SESSION_NAME="${ER_SESSION_NAME:-commander-third}"
export ER_FROM_PC_FILTER="${ER_FROM_PC_FILTER:-commander}"
export ER_LOG_DIR="${ER_LOG_DIR:-/home/hakudoukai/.local/share/enter_restart_commander}"
export ER_EVENT_TYPE="${ER_EVENT_TYPE:-enter_restart_commander_fire}"
export ER_ROLE_NAME="${ER_ROLE_NAME:-Commander}"
export ER_HEARTBEAT_FROM_PC="${ER_HEARTBEAT_FROM_PC:-commander}"
export ER_HEARTBEAT_TOPIC_PREFIX="${ER_HEARTBEAT_TOPIC_PREFIX:-[enter_restart] commander alive}"
export ER_CYCLE_LOG_PREFIX="${ER_CYCLE_LOG_PREFIX:-enter_restart_commander}"
# オプション (default 使用):
#   ER_THRESHOLD_MIN=10  ER_FIRE_CAP_COUNT=3  ER_FIRE_CAP_WINDOW_MIN=15

exec /bin/bash "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/enter_restart_common_watchdog.sh"
