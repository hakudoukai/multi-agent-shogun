#!/usr/bin/env bash
#
# Shogun Bash-Fallback Watchdog — third_pc thin wrapper
# 由来: subtask_thirdpc_shogun_bash_fallback_watchdog (副院長追命 670ffbfe(2))。
# 共通実装 shogun_bash_fallback_watchdog.sh に third_pc 固有 envvar を渡すだけ。
set -euo pipefail

export SBW_PANE_TARGET="${SBW_PANE_TARGET:-shogun-third:0.0}"
export SBW_SESSION_NAME="${SBW_SESSION_NAME:-shogun-third}"
export SBW_ROLE_NAME="${SBW_ROLE_NAME:-shogun-third}"
export SBW_TARGET_PC="${SBW_TARGET_PC:-third_pc}"
export SBW_FROM_PC="${SBW_FROM_PC:-third_pc}"
export SBW_REPO_DIR="${SBW_REPO_DIR:-/home/hakudoukai/multi-agent-shogun}"
# relaunch は既定 (doppler env + --permission-mode auto)。bare claude 禁。

exec /bin/bash "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/shogun_bash_fallback_watchdog.sh"
