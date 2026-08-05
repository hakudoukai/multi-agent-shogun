#!/usr/bin/env bash
# inbox_write.sh — メールボックスへのメッセージ書き込み（排他ロック付き）
# Usage:
#   通常 (argv 経由): bash scripts/inbox_write.sh <target_agent> <content> <type> <from>
#   ★stdin 経由 (cycle2 S2 cure)★:
#       INBOX_WRITE_CONTENT_STDIN=1 bash scripts/inbox_write.sh <target> __VIA_STDIN__ <type> <from> < <(echo "$CONTENT")
#       env INBOX_WRITE_CONTENT_STDIN=1 が立っている時は $2 を無視して stdin から content を読む。
#       process inspection (ps/argv leak) で機密内容が見えるのを防ぐ用途 (fukuincho_report_poke_bundle.py で利用)。
# Example: bash scripts/inbox_write.sh karo "足軽5号、任務完了" report_received ashigaru5
#
# ★canon fail-closed gate (leg B, subtask_shadow_failclosed_legB_a2_20260805)★:
#   TARGET が queue/pane_registry.yaml (トップレベル pane_registry: 直下の panes[].agent_id
#   ★一段★、flat panes[] ではない) に無い canon 外の宛名なら、
#   受理せず (queue/inbox/<TARGET>.yaml は書かない)、FROM が canon 内なら FROM 自身の
#   inbox へ delivery_failed 返送便を、FROM も canon 外なら queue/dead_letter/_unroutable/
#   へ記録を残す。registry 自体が読めぬ時は fail-closed (allow ではなく reject) し
#   stderr に DETECTOR_UNAVAILABLE を出す。env INBOX_WRITE_CANON_REGISTRY で registry
#   path を上書き可能 (detector-dead 疑似用)。

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$1"
CONTENT="$2"
TYPE="$3"
FROM="$4"

# ★cycle2 S2 cure (med)★: stdin 経由 content 受領 (argv 露出 cure)
# 既存 caller (positional argv) は env 未設定で従来動作、backward compatible
if [ "${INBOX_WRITE_CONTENT_STDIN:-}" = "1" ]; then
    CONTENT="$(cat)"
fi

# Validate arguments
if [ -z "$TARGET" ] || [ -z "$CONTENT" ] || [ -z "$TYPE" ] || [ -z "$FROM" ]; then
    echo "Usage: inbox_write.sh <target_agent> <content> <type> <from>" >&2
    exit 1
fi

# Cross-platform lock: flock (Linux) or mkdir (macOS fallback). Parameterized
# (lockfile/lock_dir passed in) because leg B fail-closed notices/dead-letter
# writes need their own inbox+lock, independent of the primary TARGET's inbox.
_acquire_lock() {
    local lockfile="$1"
    local lock_dir="$2"
    if command -v flock &>/dev/null; then
        exec 200>"$lockfile"
        flock -w 5 200 || return 1
    else
        local i=0
        while ! mkdir "$lock_dir" 2>/dev/null; do
            sleep 0.1
            i=$((i + 1))
            [ $i -ge 50 ] && return 1  # 5s timeout
        done
    fi
    return 0
}

_release_lock() {
    local lockfile="$1"
    local lock_dir="$2"
    if command -v flock &>/dev/null; then
        exec 200>&-
    else
        rmdir "$lock_dir" 2>/dev/null
    fi
}

# ★第二の lock (FD 201・第一の門)★: _notify_pc_dispatcher_of_unroutable() が
# 保持する pending-notice buffer の lock は、flush 時に _write_message() を
# 呼ぶ (= FD 200 を内部で再取得する)。同一 FD 200 を使い回すと `exec 200>newfile`
# で古い lock が黙って解放され (fd の再オープンで advisory lock が切れる)、
# 「buffer lock を持ったまま _write_message を呼ぶ」つもりが実は無施錠区間に
# なる。∴ 専用 FD 201 に分離し、_acquire_lock (FD200) とは独立に動く。
_acquire_lock2() {
    local lockfile="$1"
    local lock_dir="$2"
    if command -v flock &>/dev/null; then
        exec 201>"$lockfile"
        flock -w 5 201 || return 1
    else
        local i=0
        while ! mkdir "$lock_dir" 2>/dev/null; do
            sleep 0.1
            i=$((i + 1))
            [ $i -ge 50 ] && return 1
        done
    fi
    return 0
}

_release_lock2() {
    local lockfile="$1"
    local lock_dir="$2"
    if command -v flock &>/dev/null; then
        exec 201>&-
    else
        rmdir "$lock_dir" 2>/dev/null
    fi
}

# Atomic locked append of a single message to <target>'s inbox. Used both for
# the primary write (TARGET) and for internally-generated notices (e.g. the
# delivery_failed return to a canon FROM when TARGET is rejected). expires/
# supersedes are optional (5th/6th args) — notices never inherit the original
# message's expiry/supersession.
_write_message() {
    local target="$1"
    local content="$2"
    local type="$3"
    local from="$4"
    local expires="${5:-}"
    local supersedes="${6:-}"

    local inbox="$SCRIPT_DIR/queue/inbox/${target}.yaml"
    local lockfile="${inbox}.lock"
    local lock_dir="${lockfile}.d"
    local msg_id
    msg_id="msg_$(date +%Y%m%d_%H%M%S)_$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
    local timestamp
    timestamp=$(date "+%Y-%m-%dT%H:%M:%S")

    if [ ! -f "$inbox" ]; then
        mkdir -p "$(dirname "$inbox")"
        echo "messages: []" > "$inbox"
    fi

    local attempt=0
    local max_attempts=3

    while [ $attempt -lt $max_attempts ]; do
        if _acquire_lock "$lockfile" "$lock_dir"; then
            INBOX_CONTENT="$content" INBOX_EXPIRES_AT="$expires" INBOX_SUPERSEDES_ID="$supersedes" "$SCRIPT_DIR/.venv/bin/python3" -c "
import yaml, sys, os

try:
    # Load existing inbox
    with open('$inbox') as f:
        data = yaml.safe_load(f)

    # Initialize if needed
    if not data:
        data = {}
    if not data.get('messages'):
        data['messages'] = []

    # Add new message (content via env var to avoid quote injection)
    # expires_at/supersedes: optional expiry/supersession schema fields, also
    # routed via env var (not shell interpolation) to avoid injection. Absent
    # by default (None) = fully backward compatible with existing readers,
    # which never assumed these keys were present.
    new_msg = {
        'id': '$msg_id',
        'from': '$from',
        'timestamp': '$timestamp',
        'type': '$type',
        'content': os.environ.get('INBOX_CONTENT', ''),
        'read': False,
        'expires_at': os.environ.get('INBOX_EXPIRES_AT') or None,
        'supersedes': os.environ.get('INBOX_SUPERSEDES_ID') or None
    }
    data['messages'].append(new_msg)

    # Overflow rotation (2026-08-03 委員長hotfix 裁定seq137748/137769):
    # 旧仕様は50便超で既読便を黙って恒久破壊していた(同日17+19便消失の実害)。
    # 破壊→回転: 溢れた既読便はper-agent archiveへ全量退避し、発動をstderrへlogする。
    if len(data['messages']) > 50:
        msgs = data['messages']
        unread = [m for m in msgs if not m.get('read', False)]
        read = [m for m in msgs if m.get('read', False)]
        dropped = read[:-30]
        if dropped:
            _adir = os.path.join(os.path.dirname(os.path.realpath('$inbox')), '_archive')  # realpath: alias/実体のarchive二重化防止(a6指摘)
            os.makedirs(_adir, exist_ok=True)
            _abase = os.path.basename(os.path.realpath('$inbox'))
            if _abase.endswith('.yaml'):
                _abase = _abase[:-5]
            _apath = os.path.join(_adir, _abase + '_pruned.yaml')
            with open(_apath, 'a', encoding='utf-8') as _af:
                _af.write('# multi-document YAML -- use yaml.safe_load_all(), not safe_load() (see scripts/read_pruned_archive.sh)\n')
                yaml.safe_dump({'pruned_at': '$timestamp', 'count': len(dropped), 'messages': dropped}, _af, allow_unicode=True, default_flow_style=False)
                _af.write('---\n')
            print('[inbox_write] CAP_ROTATED: ' + str(len(dropped)) + ' read messages moved to ' + _apath, file=sys.stderr)
            # 永続log (2026-08-03 W67・a6提起「stderrのみで一過性」を受け、append-only・cap無し・既存archiveと同一realpath配下)
            _logpath = os.path.join(_adir, '_prune_events.log')
            with open(_logpath, 'a', encoding='utf-8') as _lf:
                _lf.write(f'$timestamp agent={_abase} pruned={len(dropped)} archive={_apath}' + chr(10))
        data['messages'] = unread + read[-30:]

    # Atomic write: tmp file + rename (prevents partial reads)
    # CRITICAL: dereference symlinks BEFORE atomic replace.
    # 2026-05-08 incident: queue/inbox/ split-brain. When INBOX was a symlink
    # (e.g. karo.yaml -> hideyoshi.yaml), os.replace replaced the SYMLINK ITSELF
    # with the tmp file, severing the alias and causing dual orphan files.
    # Fix: resolve to canonical path so writes always land on the real file
    # while symlink aliases remain intact.
    import tempfile, os
    inbox_canonical = os.path.realpath('$inbox')
    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(inbox_canonical), suffix='.tmp')
    try:
        with os.fdopen(tmp_fd, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        os.replace(tmp_path, inbox_canonical)
    except:
        os.unlink(tmp_path)
        raise

except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
"
            local status=$?
            _release_lock "$lockfile" "$lock_dir"
            [ $status -eq 0 ] && return 0
            attempt=$((attempt + 1))
            [ $attempt -lt $max_attempts ] && sleep 1
        else
            attempt=$((attempt + 1))
            if [ $attempt -lt $max_attempts ]; then
                echo "[inbox_write] Lock timeout for $inbox (attempt $attempt/$max_attempts), retrying..." >&2
                sleep 1
            else
                echo "[inbox_write] Failed to acquire lock after $max_attempts attempts for $inbox" >&2
                return 1
            fi
        fi
    done
    return 1
}

# Escalate an unroutable message (canon-外 TARGET, canon-外/unresolvable FROM)
# to a dead-letter record instead of silently dropping it or fabricating a new
# shadow inbox file for a nonexistent FROM. reason (5th arg) distinguishes why
# the return path was judged unresolvable (2026-08-05 是正三点目: canon 帰属だけ
# では「読む者が居る」を証さぬ — file 不在/stale も同じ escalate 経路を通す).
_write_dead_letter() {
    local target="$1"
    local content="$2"
    local type="$3"
    local from="$4"
    local reason="${5:-unroutable_target_and_unresolvable_from}"

    local dir="$SCRIPT_DIR/queue/dead_letter/_unroutable"
    mkdir -p "$dir"
    local id
    id="unroutable_$(date +%Y%m%d_%H%M%S)_$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
    local path="$dir/${id}.yaml"
    local timestamp
    timestamp=$(date "+%Y-%m-%dT%H:%M:%S")

    DL_CONTENT="$content" "$SCRIPT_DIR/.venv/bin/python3" -c "
import yaml, os
record = {
    'escalated_at': '$timestamp',
    'reason': '''$reason''',
    'target': '''$target''',
    'from': '''$from''',
    'type': '''$type''',
    'content': os.environ.get('DL_CONTENT', ''),
}
with open('$path', 'w') as f:
    yaml.dump(record, f, default_flow_style=False, allow_unicode=True, indent=2)
"
    echo "$path"
}

# ★第一の門 (lane=delivery-route-stabilization、委員長裁定 msg_20260805_140505_f11b5ad2
# ・訂正版 msg_20260805_141246_06125769)★: FROM が解けず _write_dead_letter() で
# 墓場落ちした便を、そのPCの差配者 (既定=shogun-second、env
# INBOX_WRITE_DISPATCH_NOTICE_TARGET で上書き可・足軽4号 registry scope 欄実装後は
# そちらへ委譲予定) の実箱へ★必ず★1行報せる。
#
# ★1件ごとに即送しない理由 (委員長裁定訂正版の危険を踏まえた設計)★: 実箱は
# 50件超で既読分を _archive/<agent>_pruned.yaml へ CAP_ROTATED 退避する
# (このファイル上部 _write_message() 132-155行)。通知1件=1便で即送すると、
# 通知が積もるほど既読の実便が早く退避され、退避先は標準 safe_load では読めぬ
# (safe_load_all が要る) — 「消える」ではないが「在るのに読めぬ」を誘発する。
# ∴ n件を1便に束ねる (専用 file 分離は不採用 — 委員長裁定「最も読まれる箱へ」の
# 理由=「未来の読者に依存する段を増やさぬ」に反するため)。
#
# ★束ねの間隔・上限 (数字を選んだ理由)★:
#   cap=5   … 束ね無しなら9件の canon 外 dead-letter (本日実測) が実便9通を消費する所、
#             5件毎の束ねなら最大2通に圧縮できる (量を有意に抑える最小限の値)。
#   interval=300s(5分) … 既存 codebase の cooldown 慣例 (activity_monitor 監査間隔=120s 等)
#             と同系統の桁。単発イベントが長時間 未束ねのまま孤立するのを5分で打ち切る。
#
# ★この修正が新たに開ける穴 (受入条件⑴)★: 束ね判定は「dead-letter 事象が起きた瞬間」
# にしか評価されない (新規常駐 process は増やさぬ設計ゆえ)。∴ ある1件が★最後の★
# dead-letter 事象のまま以後二度と起きなければ、その1件の通知は pending buffer に
# 溜まったまま flush されず、差配者へ★永久に届かぬ★ (cap/interval のどちらの条件も、
# 次の dead-letter 事象が来て初めて再評価されるため)。これは「和名で名乗る者は
# 不達を永久に知り得ない」を「差配者への通知そのものが同じ病に罹り得る」形で
# 再生産する余地であり、根絶はしていない — 単発かつ稀な最終イベントについては
# 残存する。止める者 = env INBOX_WRITE_DISPATCH_NOTICE_DISABLE (既定=1=無効・下記参照)
# を明示 0 にする迄は誰も有効化せぬ。1に戻す/据え置くのみなら委員長/karo-second 権限を
# 問わず誰でも安全側。
#
# ★測る側 (flush 判定=count/age) と 書く側 (_write_message 呼出) は本関数内で対を成す★。
#
# ★既定=無効 (2026-08-05T14:2x karo-second 令 msg_20260805_142047_b4a254cf・至急停止)★:
# 足軽3号の【第五】出口の門 設計 (docs/incident_logs/2026-08-05_exit_gate_design_delivery_route_stabilization_a3.md
# §4-4) が「alt-signal の記録先を inbox.yaml 自身にするな」との核心禁則を立て、本機構の
# 書込先 (queue/inbox/shogun-second.yaml) と正面衝突した。実測: shogun-second.yaml は
# 本機構と無関係な既存トラフィックのみで既に平均約37分周期で cap(50件)到達・退避を
# 繰り返しており (queue/inbox/_archive/_prune_events.log 実測)、追加書込は退避頻度を
# 早める。決着 (委員長裁定) まで既定を無効化し、以後の生産物 (dead-letter 発生) に対して
# 本機構が実際に発火しないようにする。有効化は INBOX_WRITE_DISPATCH_NOTICE_DISABLE=0
# を明示指定した時のみ (裁定が下り、既定を戻す判断が出るまでこの向きを保つ)。
_notify_pc_dispatcher_of_unroutable() {
    local dl_path="$1" target="$2" from="$3" reason="$4"

    if [ "${INBOX_WRITE_DISPATCH_NOTICE_DISABLE:-1}" != "0" ]; then
        echo "[inbox_write] DISPATCH_NOTICE_DISABLED: skipping dispatcher notice for $dl_path (default-disabled pending karo-second/委員長 decision on the ashigaru3 exit-gate conflict; set INBOX_WRITE_DISPATCH_NOTICE_DISABLE=0 to re-enable)" >&2
        return 0
    fi

    local dispatcher="${INBOX_WRITE_DISPATCH_NOTICE_TARGET:-shogun-second}"
    local notice_dir="${INBOX_WRITE_DISPATCH_NOTICE_DIR:-$SCRIPT_DIR/queue/dead_letter/_pending_notice}"
    mkdir -p "$notice_dir"
    local buffer="$notice_dir/${dispatcher}.log"
    local lockfile="${buffer}.lock"
    local lock_dir="${lockfile}.d"

    if ! _acquire_lock2 "$lockfile" "$lock_dir"; then
        echo "[inbox_write] WARNING: could not acquire dispatch-notice buffer lock for $buffer — notice for $dl_path NOT recorded (best-effort, does not block caller)" >&2
        return 1
    fi

    local now_epoch now_human
    now_epoch=$(date +%s)
    now_human=$(date "+%Y-%m-%dT%H:%M:%S")
    printf '%s %s FROM不明の便を墓場へ落とした / %s (target=%s from=%s reason=%s)\n' \
        "$now_epoch" "$now_human" "$dl_path" "$target" "$from" "$reason" >> "$buffer"

    local count oldest_epoch age
    count=$(wc -l < "$buffer" 2>/dev/null || echo 0)
    oldest_epoch=$(head -1 "$buffer" 2>/dev/null | awk '{print $1}')
    age=0
    [ -n "$oldest_epoch" ] && age=$(( now_epoch - oldest_epoch ))

    local cap="${INBOX_WRITE_DISPATCH_NOTICE_CAP:-5}"
    local interval="${INBOX_WRITE_DISPATCH_NOTICE_INTERVAL_SECONDS:-300}"

    local flush_content=""
    local should_flush=0
    if [ "$count" -ge "$cap" ] || [ "$age" -ge "$interval" ]; then
        should_flush=1
        flush_content="$(cat "$buffer")"
        : > "$buffer"
    fi
    _release_lock2 "$lockfile" "$lock_dir"

    if [ "$should_flush" -eq 1 ] && [ -n "$flush_content" ]; then
        local bundle_body
        bundle_body=$(printf '%s\n' "$flush_content" | sed -E 's/^[0-9]+ //')
        local notice_msg
        notice_msg="[inbox_write] FROM不明・墓場落ち通知 束ね (${count}件、interval=${interval}s/cap=${cap})
${bundle_body}"
        set +e
        _write_message "$dispatcher" "$notice_msg" "unroutable_notice_bundle" "inbox_write" "" ""
        local wstatus=$?
        set -e
        if [ $wstatus -ne 0 ]; then
            echo "[inbox_write] WARNING: dispatch-notice flush to '$dispatcher' failed (rc=$wstatus) — buffer was already cleared, this bundle's notice is best-effort lost (see 【この修正が新たに開ける穴】 comment above _notify_pc_dispatcher_of_unroutable)" >&2
        else
            echo "[inbox_write] DISPATCH_NOTICE_FLUSHED: ${count} pending unroutable notice(s) sent to '$dispatcher'" >&2
        fi
    fi
    return 0
}

# ★resolvable FROM (2026-08-05 軍師second 再監査 FAIL 是正・mtime 撤回)★:
# 「canon 帰属」だけでは「読む者が居る」を証さぬ (実測: registry 全16名中5名が
# canon でありながら実質配送不能 — 箱 file 不在/長期停滞)。
# ★mtime は代理に成らぬ★ — mtime は write で進み read では進まぬ。かつ
# fail-closed の返送そのものが mtime を更新し得るため「書かれた事」を
# 「読まれた事」と取り違える循環を開く。∴ 判定材料を mtime → message の
# read:true + その timestamp へ差し替える:
#   戻り値 0 = resolvable — read:true の便が1件以上あり、その最新 timestamp が閾値内
#   戻り値 1 = unresolvable — 箱が一度も作られておらぬ/messages が空/read:true が一件も無い
#   戻り値 2 = unresolvable — read:true 履歴は在るが、最新 timestamp が閾値超 (長期停滞)
# read:false の便 (delivery_failed 返送含む) は一切この判定に寄与しない —
# 新着の未読がいくら積もっても「読まれた証」にはならぬ (循環を断つ核心)。
# 閾値既定 86400秒(24h): 台帳実測 (07-02/07-08/05-09 起点の月単位 stale) は
# 明確に「日」を超える停滞ゆえ、24h は「今日 活動した箱」と「長期停滞箱」を
# 分ける保守的な既定値と判断 (根拠不十分ゆえ env での上書きを常時許す)。
_from_resolvable() {
    local from="$1"
    local inbox="$SCRIPT_DIR/queue/inbox/${from}.yaml"
    local threshold="${INBOX_WRITE_STALE_READER_SECONDS:-86400}"
    if [ ! -f "$inbox" ]; then
        return 1
    fi
    "$SCRIPT_DIR/.venv/bin/python3" -c "
import yaml, sys
from datetime import datetime

threshold = $threshold
try:
    with open('''$inbox''') as f:
        data = yaml.safe_load(f)
except Exception:
    sys.exit(1)

msgs = (data or {}).get('messages') or []
read_true = [m for m in msgs if isinstance(m, dict) and m.get('read') is True]
if not read_true:
    sys.exit(1)

def parse_ts(m):
    try:
        return datetime.strptime(m.get('timestamp', ''), '%Y-%m-%dT%H:%M:%S')
    except Exception:
        return None

timestamps = [t for t in (parse_ts(m) for m in read_true) if t is not None]
if not timestamps:
    sys.exit(1)

age = (datetime.now() - max(timestamps)).total_seconds()
sys.exit(2 if age > threshold else 0)
"
}

# ── canon fail-closed gate ──
# canon 宛先集合 = registry (queue/pane_registry.yaml, env で上書き可) の
# ★pane_registry.panes[].agent_id★ (top-level に pane_registry: が一段挟まる。
# flat panes[] は不可 — SMFC-SCHEMA1 が機械固定)。
# registry が読めぬ/壊れておる時は fail-closed (allow ではなく reject)。
CANON_REGISTRY="${INBOX_WRITE_CANON_REGISTRY:-$SCRIPT_DIR/queue/pane_registry.yaml}"

_canon_lookup() {
    "$SCRIPT_DIR/.venv/bin/python3" -c "
import yaml, sys
path = '''$CANON_REGISTRY'''
target = '''$TARGET'''
frm = '''$FROM'''
try:
    with open(path) as f:
        data = yaml.safe_load(f)
    if not data:
        raise ValueError('empty registry: ' + path)

    # ★形状も機械固定 (軍師second 監査是正)★: canon 出所は必ず厳密な
    # pane_registry.panes[].agent_id の一段。似て非なる形 (例: panes: が
    # トップレベル直下) を「近いから通す」事はせぬ — fail-closed。
    panes = None
    if isinstance(data, dict):
        _pr = data.get('pane_registry')
        if isinstance(_pr, dict) and isinstance(_pr.get('panes'), list):
            panes = _pr['panes']
    if panes is None:
        raise ValueError('pane_registry.panes[] not found at the required exact path in registry: ' + path)
    canon = {p.get('agent_id') for p in panes if isinstance(p, dict) and p.get('agent_id')}
    if not canon:
        raise ValueError('empty canon agent_id set in registry: ' + path)
    print('TARGET_OK' if target in canon else 'TARGET_BAD')
    print('FROM_OK' if frm in canon else 'FROM_BAD')
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(2)
"
}

set +e
_CANON_OUT="$(_canon_lookup)"
_CANON_RC=$?
set -e

if [ $_CANON_RC -ne 0 ]; then
    echo "[inbox_write] DETECTOR_UNAVAILABLE: canon registry check failed (registry=$CANON_REGISTRY, detail follows) — target=$TARGET write rejected fail-closed" >&2
    exit 1
fi

_TARGET_STATUS="$(printf '%s\n' "$_CANON_OUT" | sed -n '1p')"
_FROM_STATUS="$(printf '%s\n' "$_CANON_OUT" | sed -n '2p')"

if [ "$_TARGET_STATUS" = "TARGET_BAD" ]; then
    _FROM_RESOLVABLE_RC=1
    if [ "$_FROM_STATUS" = "FROM_OK" ]; then
        set +e
        _from_resolvable "$FROM"
        _FROM_RESOLVABLE_RC=$?
        set -e
    fi

    if [ "$_FROM_STATUS" = "FROM_OK" ] && [ "$_FROM_RESOLVABLE_RC" -eq 0 ]; then
        _NOTICE="宛先不明: ${TARGET} ／ 名簿に在る有効な宛先の一例: ashigaru1 (registry=$CANON_REGISTRY)"
        set +e
        _write_message "$FROM" "$_NOTICE" "delivery_failed" "inbox_write" "" ""
        set -e
        echo "[inbox_write] REJECTED: target '$TARGET' is not a canon agent_id (registry=$CANON_REGISTRY) — delivery_failed notice returned to from='$FROM'" >&2
        exit 1
    else
        _DL_REASON="unroutable_target_and_unresolvable_from"
        if [ "$_FROM_STATUS" = "FROM_OK" ]; then
            case "$_FROM_RESOLVABLE_RC" in
                1) _DL_REASON="target_non_canon_from_canon_but_inbox_never_created" ;;
                2) _DL_REASON="target_non_canon_from_canon_but_inbox_stale" ;;
            esac
        fi
        set +e
        _DL_PATH="$(_write_dead_letter "$TARGET" "$CONTENT" "$TYPE" "$FROM" "$_DL_REASON")"
        set -e
        # ★主契約 (load-bearing)★: 呼び手への戻り値 (non-zero exit + stderr の
        # 明示印) — file と違い墓場に成り得ぬ唯一の終端。dead_letter への記録は
        # 補助的な法医学記録に格下げ (単体で読み手を保証すると主張せぬ)。
        echo "[inbox_write] UNROUTABLE_ESCALATED: target=$TARGET from=$FROM (reason=$_DL_REASON) dead_letter=$_DL_PATH — not silently dropped, caller must handle" >&2
        # ★第一の門 (lane=delivery-route-stabilization)★: FROM が解けない墓場落ちを
        # そのPCの差配者へ束ねて報せる。best-effort — 失敗しても主契約 (上記
        # non-zero exit) を巻き込まぬよう set +e/-e で隔離する。
        set +e
        _notify_pc_dispatcher_of_unroutable "$_DL_PATH" "$TARGET" "$FROM" "$_DL_REASON"
        set -e
        exit 1
    fi
fi

echo "[inbox_write] canon_check: OK (target=$TARGET, registry=$CANON_REGISTRY)" >&2

# Self-send guard: reject messages where sender == target
if [ "$FROM" = "$TARGET" ]; then
    echo "[inbox_write] REJECTED: self-send detected (from=$FROM, target=$TARGET)" >&2
    exit 1
fi

# Amplification guard (2026-05-07 真因対策):
# stop_hook block + claude bash 経由の自己増殖ループ防止。
# content に「[<from>→<target>][<type>]」パターンが 3 回以上含まれていたら、
# 既に増幅された content の再送信と判定して reject。
_AMP_PATTERN_COUNT=$(echo "$CONTENT" | grep -oE '\[[a-zA-Z_0-9]+→[a-zA-Z_0-9]+\]\[[a-zA-Z_0-9]+\]' | wc -l)
if [ "${_AMP_PATTERN_COUNT:-0}" -ge 3 ]; then
    echo "[inbox_write] REJECTED: amplification loop detected (${_AMP_PATTERN_COUNT} embedded headers in content, threshold=3) target=$TARGET from=$FROM" >&2
    exit 1
fi

# Cross-PC bridge: if target agent is on a different PC, also INSERT to Supabase
_cross_pc_bridge() {
    local target="$1"
    local content="$2"
    local msg_type="$3"
    local from="$4"

    # Check if cross-PC delivery is needed via settings.yaml
    # settings_local.yaml overrides pc_mapping (SecondPC uses different is_local)
    # ★三値化 (lane=delivery-route-stabilization, karo-second 裁定 msg_20260805_143302_c8641467)★:
    # 旧実装は「真に local (事態A)」と「canon 通過済だが pc_mapping のどの pc の agents[] にも
    # 見当たらぬ (事態B = registry/pc_mapping 二正本の乖離)」を同じ空文字で潰し、呼び手が
    # 区別できなんだ (L440-441 相当の旧欠陥)。以後 LOCAL / BRIDGED|<local>|<target> / UNROUTABLE
    # の三値で返す。事態Bの既知の実例 = registry にのみ在り pc_mapping に無い名 (takenaka/honda/sanada)。
    local bridge_info local_pc target_pc
    bridge_info=$("$SCRIPT_DIR/.venv/bin/python3" -c "
import yaml, sys, os
try:
    local_path = '$SCRIPT_DIR/config/settings_local.yaml'
    main_path = '$SCRIPT_DIR/config/settings.yaml'
    if os.path.exists(local_path):
        with open(local_path) as f:
            local_cfg = yaml.safe_load(f) or {}
        pc_map = local_cfg.get('pc_mapping', {})
    else:
        pc_map = {}
    if not pc_map:
        with open(main_path) as f:
            cfg = yaml.safe_load(f) or {}
        pc_map = cfg.get('pc_mapping', {})
    local_id = ''
    local_agents = []
    for pc_name, pc_cfg in pc_map.items():
        if pc_cfg.get('is_local'):
            local_id = pc_cfg.get('pc_id', pc_name)
            local_agents = pc_cfg.get('agents', []) or []
    # local-first (R0 seq96053/96064): target が local PC の agents に在れば bridge せず local 書込。
    # 3PC 均等編成で同一 agent_id (例 ashigaru1-7) が複数 PC に併存しても、各 PC 内で local 解決される。
    # remote-only agent (local に無い) の bridge 意味論は不変。
    if '$target' in local_agents:
        print('LOCAL')
        sys.exit(0)
    for pc_name, pc_cfg in pc_map.items():
        if pc_cfg.get('is_local'):
            continue
        agents = pc_cfg.get('agents', [])
        if '$target' in agents and pc_cfg.get('supabase_bridge'):
            print(f'BRIDGED|{local_id}|{pc_cfg.get(\"pc_id\", pc_name)}')
            sys.exit(0)
    # 事態B: target はどの pc_cfg.agents[] にも無い (local にも bridge 先にも見当たらぬ)。
    print('UNROUTABLE')
except Exception:
    print('UNROUTABLE')
" 2>/dev/null)

    local _bridge_status _bridge_f2 _bridge_f3
    IFS='|' read -r _bridge_status _bridge_f2 _bridge_f3 <<< "$bridge_info"

    if [ "$_bridge_status" = "LOCAL" ]; then
        return 0  # Local agent, no bridge needed
    fi

    if [ "$_bridge_status" != "BRIDGED" ]; then
        # UNROUTABLE (事態B: canon gate は通過済だが pc_mapping のどの pc の agents[] にも
        # 見当たらぬ)、または想定外の出力 (python 側例外/形式不一致) — 旧実装は空文字→
        # 事態A(真にlocal)と同じ扱いで local write へ静かに fall through していたが、それは
        # 「消える」より質が悪い『在ると思うて開けねば諦める』死蔵を生む (前段実測=
        # takenaka/honda/sanada 宛)。∴ _canon_lookup の TARGET_BAD 分岐 (L479-518) と同型に
        # 揃え、local write はさせず dead_letter へ記録 + PC 差配者通知 + fail-closed (71) で
        # 呼び手へ返す (新規 exit code は増やさぬ — 既存 71 を再利用)。
        set +e
        _DL_PATH="$(_write_dead_letter "$target" "$content" "$msg_type" "$from" "cross_pc_bridge_unroutable")"
        _notify_pc_dispatcher_of_unroutable "$_DL_PATH" "$target" "$from" "cross_pc_bridge_unroutable"
        set -e
        echo "[inbox_write] UNROUTABLE: target=$target is canon (registry) but pc_mapping has no local/bridge routing entry for it (bridge_info='${bridge_info}') — not silently written to local inbox, dead_letter=$_DL_PATH" >&2
        return 71
    fi

    local_pc="$_bridge_f2"
    target_pc="$_bridge_f3"

    # Load Supabase env
    local sb_url sb_key
    if [ -f "$HOME/.hakudokai/env" ]; then
        sb_url=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
        sb_key=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
    fi
    sb_url="${SUPABASE_URL:-$sb_url}"
    sb_key="${SUPABASE_SERVICE_ROLE_KEY:-$sb_key}"

    if [ -z "$sb_url" ] || [ -z "$sb_key" ]; then
        echo "[inbox_write] WARN: cross-PC bridge skipped (no Supabase env)" >&2
        return 0
    fi

    # Truncate content for Supabase (max 2000 chars)
    local truncated="${content:0:2000}"

    # JSON encode via python3 (heredoc + argv) — bash 文字列補間では改行/特殊文字が
    # JSON に直接埋め込まれて Supabase が「0x0a must be escaped」で reject していた。
    local payload
    payload=$(python3 - "$truncated" "${local_pc:-main_pc}" "$target_pc" "$target" "$from" "$msg_type" <<'PYEOF'
import json, sys
content_truncated, local_pc, target_pc, target_agent, from_agent, msg_type = sys.argv[1:7]
print(json.dumps({
    "message_type": msg_type,
    "from_pc": local_pc,
    "to_pc": target_pc,
    "topic": f"cross_pc_inbox_{target_agent}",
    "content": f"[{from_agent}→{target_agent}][{msg_type}] {content_truncated}",
    "requires_response": False,
    "priority": "normal",
    "clinic_id": "hakudoukai_main",
    "bypass_5round_limit": False,
    "is_meta_only": False
}, ensure_ascii=False))
PYEOF
)

    # INSERT to Supabase for cross-PC delivery. curl itself exits 0 for HTTP
    # 4xx/5xx unless --fail is used, so require both curl success and an
    # explicit 2xx response. Discard the response body to avoid logging it.
    local http_status curl_rc
    http_status=$(curl --fail-with-body -sS -o /dev/null -w '%{http_code}' -X POST \
        --connect-timeout 10 --max-time 15 \
        "${sb_url}/rest/v1/pc_handshake" \
        -H "Authorization: Bearer ${sb_key}" \
        -H "apikey: ${sb_key}" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=minimal" \
        --data-binary "$payload" \
        2>/dev/null)
    curl_rc=$?
    if [ "$curl_rc" -eq 0 ] && [[ "$http_status" =~ ^2[0-9][0-9]$ ]]; then
        echo "[inbox_write] cross-PC bridge: ${target} → ${target_pc} via Supabase" >&2
        return 70
    fi
    echo "[inbox_write] WARN: cross-PC bridge INSERT failed for ${target} (http_status=${http_status:-000}, curl_rc=$curl_rc)" >&2
    return 71
}

# Trigger cross-PC bridge. If a cross-PC insert succeeds, do not also write a
# local dead-letter inbox file. If insert fails, or the target is UNROUTABLE
# (canon per registry but no pc_mapping routing entry — 三値化 lane=delivery-route-
# stabilization), fail closed instead of silently creating an unread local queue
# that no remote recipient reads.
if [ ! -f "$HOME/.openclaw/disable_cross_pc_bridge" ]; then
    set +e
    _cross_pc_bridge "$TARGET" "$CONTENT" "$TYPE" "$FROM"
    _BRIDGE_RC=$?
    set -e
    if [ "$_BRIDGE_RC" -eq 70 ]; then
        exit 0
    fi
    if [ "$_BRIDGE_RC" -eq 71 ]; then
        exit 71
    fi
fi

_write_message "$TARGET" "$CONTENT" "$TYPE" "$FROM" "${INBOX_EXPIRES_AT:-}" "${INBOX_SUPERSEDES_ID:-}"
exit $?
