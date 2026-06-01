#!/usr/bin/env bash
# Commander 自動 Enter watcher supervisor (副院長令 889ee02c [P1])
#
# 機能:
#   - commander-third pane が在る間だけ pane_enter_watcher.py を生かす
#   - pane 消滅で watcher も停止
#   - 二重起動防止 (flock)
#   - watcher 異常終了で 5秒後 自動再起動
#
# 環境変数:
#   LIVE=1 -> 実 Enter 送出 (本番)
#   LIVE=0 or 不在 -> DRY-RUN (誤爆ゼロ実証用)
#   STALE_SEC=300 (既定 5分)
#   POLL_SEC=10 (既定 10秒)
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WATCHER_PY="$SCRIPT_DIR/pane_enter_watcher.py"
TARGET_PANE="commander-third:0.0"
LOCKFILE="/tmp/pane_enter_watcher_supervisor.lock"
LOGFILE="/tmp/pane_enter_watcher_supervisor.log"

log() { printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOGFILE" >&2; }

# 二重起動防止
exec 200>"$LOCKFILE"
flock -n 200 || { log "another supervisor instance running, exit"; exit 0; }

log "=== supervisor start (LIVE=${LIVE:-0}) ==="

# 対象 pane 存在判定
pane_exists() {
    tmux display-message -t "$TARGET_PANE" -p '#{pane_id}' >/dev/null 2>&1
}

# 起動 loop
while true; do
    if ! pane_exists; then
        log "target pane $TARGET_PANE not found, exit"
        exit 0
    fi

    log "starting watcher (LIVE=${LIVE:-0} STALE_SEC=${STALE_SEC:-300} POLL_SEC=${POLL_SEC:-10})"
    LIVE="${LIVE:-0}" STALE_SEC="${STALE_SEC:-300}" POLL_SEC="${POLL_SEC:-10}" \
        /usr/bin/python3 "$WATCHER_PY" --target "$TARGET_PANE" \
            >>"$LOGFILE" 2>&1
    rc=$?
    log "watcher exited rc=$rc"

    if ! pane_exists; then
        log "target pane vanished, supervisor exit"
        exit 0
    fi

    log "watcher restart in 5s"
    sleep 5
done
