#!/usr/bin/env bash
# bulk_ack.sh — 安全な bulk ack (重要 type 除外) — 2026-05-07 制定
#
# 目的: 拙者が 5/7 18:00 頃の自己増殖ループ事件で全 inbox bulk ack した結果、
#       家康→ashigaru7 cycle2 qc_fail も ack で消失 → ashigaru7 指示見失い、
#       という事故を恒久防止。type 別フィルタで「処理が必要な指示」を保護。
#
# Usage:
#   bash scripts/bulk_ack.sh <agent_id> [--exclude-types ...] [--dry-run]
#   bash scripts/bulk_ack.sh --all       # 全 agent (重要 type 除外)
#   bash scripts/bulk_ack.sh <agent_id> --force  # 重要 type も含めて強制 ack (危険)
#
# Default exclude types (= 保護対象、ack されない):
#   task_assigned, qc_fail, cmd_new, directive, redo, urgent_stop, request_permission
#
# Default include types (= ack OK):
#   notification, report_received, status_update, audit_missing, idle_alert, info

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ─── default exclude types (= 保護される、ack しない) ───
DEFAULT_EXCLUDE="task_assigned,qc_fail,cmd_new,directive,redo,urgent_stop,request_permission"

EXCLUDE_TYPES="$DEFAULT_EXCLUDE"
DRY_RUN=false
FORCE=false
ALL_AGENTS=false
TARGET_AGENT=""

# ─── parse args ───
while [ $# -gt 0 ]; do
    case "$1" in
        --exclude-types)
            EXCLUDE_TYPES="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            EXCLUDE_TYPES=""  # force 時は exclude 無効
            shift
            ;;
        --all)
            ALL_AGENTS=true
            shift
            ;;
        -h|--help)
            grep "^#" "$0" | head -25
            exit 0
            ;;
        *)
            TARGET_AGENT="$1"
            shift
            ;;
    esac
done

if [ -z "$TARGET_AGENT" ] && [ "$ALL_AGENTS" != "true" ]; then
    echo "Usage: bulk_ack.sh <agent_id> [--exclude-types t1,t2,...] [--dry-run] [--force]" >&2
    echo "       bulk_ack.sh --all" >&2
    exit 1
fi

# ─── agent 一覧 ───
if [ "$ALL_AGENTS" = "true" ]; then
    AGENTS="shogun karo gunshi ashigaru1 ashigaru2 ashigaru3 ashigaru5 ashigaru6 ashigaru7 ashigaru8"
else
    AGENTS="$TARGET_AGENT"
fi

# ─── 各 agent inbox を処理 ───
TOTAL_ACKED=0
TOTAL_PROTECTED=0

for AGENT in $AGENTS; do
    INBOX="$SCRIPT_DIR/queue/inbox/${AGENT}.yaml"
    if [ ! -f "$INBOX" ]; then
        continue
    fi

    # backup
    if [ "$DRY_RUN" != "true" ]; then
        cp "$INBOX" "${INBOX}.bak.$(date '+%Y%m%d_%H%M%S')_bulkack"
    fi

    # process via python (yaml safe)
    EXCLUDE="$EXCLUDE_TYPES" DRY_RUN="$DRY_RUN" \
    python3 - "$INBOX" "$AGENT" <<'PYEOF'
import yaml, sys, os
inbox_path, agent_id = sys.argv[1], sys.argv[2]
exclude_types = set(t.strip() for t in os.environ.get('EXCLUDE','').split(',') if t.strip())
dry_run = os.environ.get('DRY_RUN','') == 'true'

with open(inbox_path) as f:
    data = yaml.safe_load(f) or {}
msgs = data.get('messages', []) or []

acked = 0
protected = 0
for m in msgs:
    if m.get('read', True):
        continue
    msg_type = m.get('type', '')
    if msg_type in exclude_types:
        protected += 1
        continue
    if not dry_run:
        m['read'] = True
    acked += 1

if not dry_run and acked > 0:
    with open(inbox_path, 'w') as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

prefix = "[DRY-RUN] " if dry_run else ""
print(f"  {prefix}{agent_id}: acked={acked}, protected={protected} (exclude={','.join(sorted(exclude_types)) or '(none = force)'})")
PYEOF
done

echo ""
echo "完了。重要 type は保護されました (= ack されず、agent が処理する必要)"
echo "ack 対象を細かく指定したい場合: --exclude-types <comma-separated>"
echo "完全強制 ack (= 旧来の挙動、危険): --force"
