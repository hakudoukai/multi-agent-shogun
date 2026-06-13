#!/usr/bin/env bash
#
# Shogun Bash-Fallback Watchdog — second_pc thin wrapper (★配備優先★)
# 由来: subtask_thirdpc_shogun_bash_fallback_watchdog (副院長追命 670ffbfe(2))。
# second_pc が本 watchdog の主対象 (inbox808 堆積・API retry 滞留の実事故元)。
#
# ★relaunch 方針 (重要)★: 既定は doppler env 付き (--permission-mode auto)。
# task 根因分析どおり「bare claude 再起動 = env-gap で API retry 滞留」を避けるため
# doppler 経由を厳守する (memory: second-pc bundle の bare claude は env-gap の原因)。
# 万一 second_pc で doppler が PATH 不在なら relaunch は失敗し、連続上限で
# human_required escalate される (= bare claude で誤魔化すより安全)。その場合のみ
# 運用者が SBW_RELAUNCH_CMD を明示 override すること (独断で bare claude にしない)。
set -euo pipefail

export SBW_PANE_TARGET="${SBW_PANE_TARGET:-shogun-second:0.0}"
export SBW_SESSION_NAME="${SBW_SESSION_NAME:-shogun-second}"
export SBW_ROLE_NAME="${SBW_ROLE_NAME:-shogun-second}"
export SBW_TARGET_PC="${SBW_TARGET_PC:-second_pc}"
export SBW_FROM_PC="${SBW_FROM_PC:-second_pc}"
export SBW_REPO_DIR="${SBW_REPO_DIR:-/home/hakudokai/multi-agent-shogun}"

exec /bin/bash "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/shogun_bash_fallback_watchdog.sh"
