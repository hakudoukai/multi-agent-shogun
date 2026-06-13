#!/usr/bin/env bash
#
# Shogun Bash-Fallback Watchdog — main_pc thin wrapper
# 由来: subtask_thirdpc_shogun_bash_fallback_watchdog (副院長追命 670ffbfe(2))。
set -euo pipefail

export SBW_PANE_TARGET="${SBW_PANE_TARGET:-shogun-main:0.0}"
export SBW_SESSION_NAME="${SBW_SESSION_NAME:-shogun-main}"
export SBW_ROLE_NAME="${SBW_ROLE_NAME:-shogun-main}"
export SBW_TARGET_PC="${SBW_TARGET_PC:-main_pc}"
export SBW_FROM_PC="${SBW_FROM_PC:-main_pc}"
export SBW_REPO_DIR="${SBW_REPO_DIR:-/home/user/multi-agent-shogun}"

exec /bin/bash "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/shogun_bash_fallback_watchdog.sh"
