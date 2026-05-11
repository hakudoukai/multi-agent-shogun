#!/usr/bin/env bash
# Phase 1-6 deliverable git-tracking 検証 (cmd_004 subtask_cmd004_phase_1_6_rollback_recovery_audit AC5)
# 設計: docs/cmd004_phase_1_6_rollback_recovery_audit.md §3
#
# 目的: 重要 deliverable file が `.gitignore` の `*`-default pattern で
#       誤って untracked にならないよう機械検査する。
#
# 使い方:
#   bash scripts/lint/check_deliverable_tracked.sh        # 通常検証
#   bash scripts/lint/check_deliverable_tracked.sh -v     # verbose
#
# 終了コード:
#   0 = 全 deliverable が tracked 可能 (= not ignored)
#   1 = 1 件以上の deliverable が `.gitignore` で ignored
#   2 = preflight 失敗 (= 想定 repo 外で起動)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || { echo "[check_deliverable] failed to cd $ROOT" >&2; exit 2; }

VERBOSE=0
[ "${1:-}" = "-v" ] && VERBOSE=1

# Phase 1-6 deliverable list (= ashigaru3 滝川一益 cmd_004 chain)
# whitelist は .gitignore 内で管理、本 script は **検査専用**
DELIVERABLES=(
  # Phase 1 (push_vapid_infra)
  "docs/cmd004_push_vapid_management.md"
  "queue/reports/ashigaru3_cmd004_push_vapid_infra_report.yaml"
  # Phase 2 (push_vapid_phase2)
  "queue/reports/ashigaru3_cmd004_push_vapid_phase2_report.yaml"
  # Phase 3 (service_worker_offline_sync)
  "docs/cmd004_patient_app_pwa_design.md"
  "queue/reports/ashigaru3_cmd004_service_worker_offline_sync_report.yaml"
  # Phase 4 (notification_facade_pattern)
  "docs/cmd004_notification_facade_design.md"
  "queue/reports/ashigaru3_cmd004_notification_facade_pattern_report.yaml"
  # Phase 5 (observability_infra)
  "docs/cmd004_observability_design.md"
  "queue/reports/ashigaru3_cmd004_observability_infra_report.yaml"
  # Phase 6 (security_hardening_infra)
  "docs/cmd004_security_hardening_design.md"
  "queue/reports/ashigaru3_cmd004_security_hardening_infra_report.yaml"
  ".pre-commit-config.yaml"
  "scripts/lint/check_secrets.sh"
  "scripts/lint/dependency_audit.sh"
  "scripts/lint/check_deliverable_tracked.sh"
  # Phase 1-6 rollback recovery audit (本 task)
  "docs/cmd004_phase_1_6_rollback_recovery_audit.md"
  "queue/reports/ashigaru3_cmd004_phase_1_6_rollback_recovery_audit_report.yaml"
  ".gitattributes"
)

missing_files=0
ignored_files=0
ok_count=0

for f in "${DELIVERABLES[@]}"; do
    if [ ! -e "$f" ]; then
        echo "[FAIL] missing file: $f"
        missing_files=$((missing_files + 1))
        continue
    fi
    # git check-ignore は ignored 時 rc=0、tracked 時 rc=1
    if git check-ignore -q "$f" 2>/dev/null; then
        echo "[FAIL] file is ignored by .gitignore: $f"
        ignored_files=$((ignored_files + 1))
        continue
    fi
    ok_count=$((ok_count + 1))
    [ "$VERBOSE" -eq 1 ] && echo "[OK]   $f"
done

total_violation=$((missing_files + ignored_files))
echo ""
echo "[check_deliverable] summary: ok=$ok_count missing=$missing_files ignored=$ignored_files total=${#DELIVERABLES[@]}"

if [ "$total_violation" -gt 0 ]; then
    echo "[check_deliverable] FAIL: $total_violation deliverable(s) not properly tracked."
    echo "[check_deliverable] hint: update .gitignore '!path' whitelist entries."
    exit 1
fi

echo "[check_deliverable] OK: all deliverables tracked."
exit 0
