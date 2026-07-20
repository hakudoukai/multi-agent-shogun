#!/usr/bin/env bash
# hermes2_deaddrop_stale_detector.sh
#
# hermes2 (環境部長) legacy dead-drop YAML (queue/inbox/hermes2.yaml) の
# ★read-only★ stale 検知器。
#
# 起点: 副委員長指令 hermes2-dead-drop-route-guard-work-order-20260721.md
# item 3「旧hermes2.yamlの新規滞留をread-onlyに検知するstale detectorを
# 追加する。検知器は配送consumerにならず、本文を再送・既読化・削除しない。」
#
# ★安全核★
#   - queue/inbox/hermes2.yaml は read のみ。書込・作成・削除・既読化・
#     再送は一切行わない (ファイルが存在しなくても新規作成しない)。
#   - 検知器自身の state (前回実行時の unread 件数・連続 clean cycle 数)
#     は queue/inbox/ の外、queue/metrics/ に保持する。
#
# Usage: bash scripts/hermes2_deaddrop_stale_detector.sh
# Exit 0: 新規滞留 (unread 件数増加) なし。stderr に現況を出力。
# Exit 1: 新規滞留を検知 (前回実行時より unread 件数が増加)。
#
# 少なくとも2監視周期 (=本スクリプトの2回連続実行) で exit 0 が継続すれば
# work order item 6 の「2監視周期で新規滞留0」証跡となる。
# consecutive_clean_cycles が state に記録される。

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python3"

HERMES2_INBOX="${HERMES2_INBOX:-$SCRIPT_DIR/queue/inbox/hermes2.yaml}"
STALE_STATE_FILE="${STALE_STATE_FILE:-$SCRIPT_DIR/queue/metrics/hermes2_deaddrop_stale_state.yaml}"

mkdir -p "$(dirname "$STALE_STATE_FILE")"

TIMESTAMP=$(date "+%Y-%m-%dT%H:%M:%S")

RESULT=$("$VENV_PYTHON" - "$HERMES2_INBOX" "$STALE_STATE_FILE" "$TIMESTAMP" <<'PYEOF'
import sys, yaml, os

inbox_path, state_path, now_ts = sys.argv[1:4]

# ★read-only★: hermes2.yaml が存在しなければ new-create せず unread=0 と
# 扱う。存在すれば読むだけ (open 'r' のみ、書込は一切しない)。
if os.path.exists(inbox_path):
    with open(inbox_path) as f:
        data = yaml.safe_load(f) or {}
    messages = data.get('messages') or []
    if not isinstance(messages, list):
        messages = []
    total = len(messages)
    unread_msgs = [m for m in messages if isinstance(m, dict) and not m.get('read', False)]
    unread = len(unread_msgs)
    # ★finding H2-G1-STALE-DETECTOR-COUNT-ALIASING-002 是正★:
    # 件数だけの比較では「既読化された旧未読1件」+「新規到着の未読1件」が
    # 同一cycle内で同時発生すると差引ゼロとなり検知漏れする (同数入替)。
    # そのため未読 message ID の★集合★を state に保持し、前回 cycle の
    # 未読ID集合に存在しなかった ID が今回出現したら growth とする。
    unread_ids = sorted({
        m.get('id') for m in unread_msgs
        if isinstance(m, dict) and m.get('id')
    })
else:
    total = 0
    unread = 0
    unread_ids = []

prev_state = {}
if os.path.exists(state_path):
    with open(state_path) as f:
        prev_state = yaml.safe_load(f) or {}

prev_unread = prev_state.get('last_unread_count')
prev_clean_cycles = int(prev_state.get('consecutive_clean_cycles', 0) or 0)
prev_unread_ids = set(prev_state.get('unread_ids') or [])

if prev_unread is None:
    # 初回実行: 比較対象なし → baseline 確立、growth 扱いしない。
    # baseline 自体を「1回目の clean 観測」として数える (2周期連続 clean
    # 確認 = baseline 実行 + 次回 clean 実行の計2回、work order item 6)。
    verdict = 'baseline'
    growth = False
    consecutive_clean_cycles = 1
else:
    new_ids = set(unread_ids) - prev_unread_ids
    if new_ids:
        verdict = 'growth'
        growth = True
        consecutive_clean_cycles = 0
    else:
        verdict = 'clean'
        growth = False
        consecutive_clean_cycles = prev_clean_cycles + 1

new_state = {
    'last_checked_at': now_ts,
    'last_total_count': total,
    'last_unread_count': unread,
    'consecutive_clean_cycles': consecutive_clean_cycles,
    'unread_ids': unread_ids,
}

# state file は queue/metrics/ 配下 (対象 YAML の外) — atomic write。
import tempfile
tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(state_path), suffix='.tmp')
try:
    with os.fdopen(tmp_fd, 'w') as f:
        yaml.safe_dump(new_state, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    os.replace(tmp_path, state_path)
except Exception:
    os.unlink(tmp_path)
    raise

print(f'verdict={verdict}|total={total}|unread={unread}|prev_unread={prev_unread if prev_unread is not None else "none"}|consecutive_clean_cycles={consecutive_clean_cycles}')
PYEOF
)

VERDICT=$(echo "$RESULT" | sed -n 's/^verdict=\([a-z]*\).*/\1/p')
TOTAL=$(echo "$RESULT" | sed -n 's/.*|total=\([0-9]*\)|.*/\1/p')
UNREAD=$(echo "$RESULT" | sed -n 's/.*|unread=\([0-9]*\)|.*/\1/p')
PREV_UNREAD=$(echo "$RESULT" | sed -n 's/.*|prev_unread=\([^|]*\)|.*/\1/p')
CONSECUTIVE=$(echo "$RESULT" | sed -n 's/.*consecutive_clean_cycles=\([0-9]*\)$/\1/p')

case "$VERDICT" in
    baseline)
        echo "[hermes2_deaddrop_stale_detector] baseline established: total=${TOTAL} unread=${UNREAD} (read-only, no prior state to compare)" >&2
        exit 0
        ;;
    clean)
        echo "[hermes2_deaddrop_stale_detector] OK: no new stale accumulation (unread=${UNREAD}, prev_unread=${PREV_UNREAD}, consecutive_clean_cycles=${CONSECUTIVE})" >&2
        if [ "${CONSECUTIVE:-0}" -ge 2 ]; then
            echo "[hermes2_deaddrop_stale_detector] 2-cycle confirmation achieved: consecutive_clean_cycles=${CONSECUTIVE} >= 2" >&2
        fi
        exit 0
        ;;
    growth)
        echo "[hermes2_deaddrop_stale_detector] GROWTH DETECTED: unread increased from ${PREV_UNREAD} to ${UNREAD} (total=${TOTAL}); legacy hermes2.yaml is accumulating new stale messages" >&2
        exit 1
        ;;
    *)
        echo "[hermes2_deaddrop_stale_detector] ERROR: unexpected verdict output: ${RESULT}" >&2
        exit 2
        ;;
esac
