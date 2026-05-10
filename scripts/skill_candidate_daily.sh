#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# skill_candidate_daily.sh — 日次 skill candidate scan (= cron 推奨)
#
# 黒田 debt-04 是正 (= 2026-05-10): session_start_hook から分離。
# 旧: SessionStart hook 内で background 起動 → 復旧 hook の副作用累積、deterministic 性 劣化
# 新: 本 script を cron で 1 日 1 回起動 (= 復旧 hook は persona 復元のみ)
#
# 推奨 cron 設定 (= crontab -e):
#   0 9 * * * cd /home/user/projects/multi-agent-shogun-newbuild && \
#     bash scripts/skill_candidate_daily.sh \
#     >> logs/skill_candidate_daily.log 2>&1
#
# 旧経路の rate-limit stamp (/tmp/.skill_candidate_scan_stamp) は廃止、
# cron 自体が重複防止 + scheduling を担う。
# ════════════════════════════════════════════════════════════════
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

echo "═══════════════════════════════════════════════════════════"
echo "  Daily skill candidate scan — $(date -Iseconds)"
echo "═══════════════════════════════════════════════════════════"

# Stage 1: skill candidate scan
SKILL_SCAN_SCRIPT="skills/shogun-trouble-auto-skill/scripts/skill_candidate_scan.sh"
if [ -x "$SKILL_SCAN_SCRIPT" ]; then
    echo ""
    echo "─── skill_candidate_scan ───"
    bash "$SKILL_SCAN_SCRIPT" scan
fi

# Stage 2: dashboard 24h 残留 scan
DASH_SCAN="skills/shogun-trouble-auto-skill/scripts/dashboard_scan.sh"
if [ -x "$DASH_SCAN" ]; then
    echo ""
    echo "─── dashboard_scan ───"
    bash "$DASH_SCAN"
fi

echo ""
echo "═══ Daily scan 完遂 — $(date -Iseconds) ═══"
