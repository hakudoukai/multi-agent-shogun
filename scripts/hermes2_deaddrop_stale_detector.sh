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

# B3是正: state file の read-modify-write を flock で排他制御し、
# 検知器の並行実行によるレースを防ぐ (lock は state file 専用の別ファイル)。
STALE_LOCK_FILE="${STALE_STATE_FILE}.lock"

# ★lock待ちtimeout方針 (fix-cycle3 追補、finding H2-G1-CODEX-B3-CONCURRENCY-TEST-MISSING-002)★:
# `flock -x 200` に `-w <sec>` を付けず★無期限待機★とする。critical section は
# 小さな state YAML の read+compute+atomic write のみで一瞬 (ms オーダー) で終わる
# ため、timeout を設けて lock 取得を諦める設計は「更新消失を防ぐ」という B3 是正の
# 目的そのものに反する (timeout 発火時に検知結果を欠測させるくらいなら、待つ方が
# read-only 監視ツールとしての正確性を優先できる)。デッドロックの恐れは無い
# (lock 保持者は必ず同一 critical section を抜けて自発的に解放する)。
TIMESTAMP=$(date "+%Y-%m-%dT%H:%M:%S")

# ★fix-cycle3 追補★ (TC4 が実地で検出した実挙動不具合):
# `RESULT=$( flock -x 200; ... ) 200>"$STALE_LOCK_FILE"` は誤り —
# `$( )` command substitution は word expansion の一部として先に評価され、
# 末尾の `200>"$STALE_LOCK_FILE"` redirection は substitution 実行後にしか
# 適用されないため、substitution 内部の `flock -x 200` 実行時点では fd 200 が
# 未オープンで `flock: 200: Bad file descriptor` となり、lock は事実上
# no-op だった (並行起動で更新消失、consecutive_clean_cycles が期待値より
# 少なくなる実害を TC4 で確認)。正しくは fd を★親 shell 側で先に開いて
# flock してから★ command substitution を実行する。
exec 200>"$STALE_LOCK_FILE"
flock -x 200

RESULT=$(
    "$VENV_PYTHON" - "$HERMES2_INBOX" "$STALE_STATE_FILE" "$TIMESTAMP" <<'PYEOF'
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

# T1是正 (fix-cycle3 追補): state file の値は書換・破損・旧形式混入の可能性が
# あるため、型を検証してから使う (不正値は安全側=baseline相当へフォールバック)。
# ★bool は Python では int のサブクラス★のため isinstance(x, int) だけでは
# True/False を誤って整数として受理してしまう。bool を明示的に除外し、かつ
# 負数も不正値として弾く (契約=非負整数のみ受理)。
prev_unread_raw = prev_state.get('last_unread_count')
if (
    isinstance(prev_unread_raw, int)
    and not isinstance(prev_unread_raw, bool)
    and prev_unread_raw >= 0
):
    prev_unread = prev_unread_raw
else:
    prev_unread = None

prev_clean_cycles_raw = prev_state.get('consecutive_clean_cycles', 0)
if isinstance(prev_clean_cycles_raw, bool):
    prev_clean_cycles = 0
else:
    try:
        _prev_clean_cycles = int(prev_clean_cycles_raw)
        prev_clean_cycles = _prev_clean_cycles if _prev_clean_cycles >= 0 else 0
    except (TypeError, ValueError):
        prev_clean_cycles = 0

prev_unread_ids_raw = prev_state.get('unread_ids')
if isinstance(prev_unread_ids_raw, list):
    prev_unread_ids = {x for x in prev_unread_ids_raw if isinstance(x, str)}
else:
    prev_unread_ids = set()

if prev_unread is None:
    # 初回実行 (または state 破損によるフォールバック): 比較対象なし →
    # baseline 確立、growth 扱いしない。baseline 自体を「1回目の clean
    # 観測」として数える (2周期連続 clean 確認 = baseline 実行 + 次回
    # clean 実行の計2回、work order item 6)。
    verdict = 'baseline'
    growth = False
    consecutive_clean_cycles = 1
else:
    new_ids = set(unread_ids) - prev_unread_ids
    # B2是正 finding H2-CODEX-B2-UNREAD-COUNT-GROWTH-001:
    # ID 集合差分だけでは、ID を持たない未読メッセージの増加 (unread 総数
    # が増えているのに unread_ids には現れない) を検知できない。ID 差分に
    # 加え、unread 総数そのものの増加も growth 条件とする。
    count_growth = unread > prev_unread
    if new_ids or count_growth:
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

# critical section 終了 → fd 200 を close して flock を解放。
exec 200>&-

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
