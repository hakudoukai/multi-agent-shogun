#!/usr/bin/env bash
# scripts/lib/inbox_path.sh — inbox path SSoT 解決ライブラリ
#
# Phase 0 反省点 u (= bulk_ack/inbox_write/inbox_watcher 三者間の path 想定不一致) への対応。
# 全 script で本ライブラリ経由で path 解決すること。
#
# Usage:
#   source scripts/lib/inbox_path.sh
#   inbox_path=$(get_inbox_path "hideyoshi")
#
# 設計:
#   - v1 path: queue/inbox/<agent>.yaml (旧、symlink risk あり)
#   - v2 path: queue/inbox_v2/<agent>.yaml (新、workspace 内固定、symlink 廃止)
#   - migration 期間: v1 + v2 両方の存在を確認、INBOX_VERSION 環境変数で切替
#
# 改訂責務:
#   docs/message_delivery_v2_design_2026-05-08.md §2.6 と同期。
#   Phase 4 cutover 完遂後に v1 path 解決ロジックを削除する。

set -euo pipefail

# project root 解決 (本ライブラリは scripts/lib/ に配置)
_INBOX_PATH_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_INBOX_PATH_PROJECT_ROOT="$(cd "${_INBOX_PATH_LIB_DIR}/../.." && pwd)"

# inbox version 切替 (default: v1 = 旧 path、Phase 4 cutover で v2 へ)
INBOX_VERSION="${INBOX_VERSION:-v1}"

# get_inbox_path <agent_id>
# returns: inbox YAML の絶対 path
get_inbox_path() {
    local agent="$1"
    if [[ -z "$agent" ]]; then
        echo "[inbox_path.sh] ERROR: agent_id required" >&2
        return 1
    fi
    case "$INBOX_VERSION" in
        v1)
            echo "${_INBOX_PATH_PROJECT_ROOT}/queue/inbox/${agent}.yaml"
            ;;
        v2)
            echo "${_INBOX_PATH_PROJECT_ROOT}/queue/inbox_v2/${agent}.yaml"
            ;;
        *)
            echo "[inbox_path.sh] ERROR: unknown INBOX_VERSION=$INBOX_VERSION" >&2
            return 1
            ;;
    esac
}

# get_inbox_dir
# returns: inbox ディレクトリ
get_inbox_dir() {
    case "$INBOX_VERSION" in
        v1)
            echo "${_INBOX_PATH_PROJECT_ROOT}/queue/inbox"
            ;;
        v2)
            echo "${_INBOX_PATH_PROJECT_ROOT}/queue/inbox_v2"
            ;;
    esac
}

# get_health_path <agent_id>
# returns: heartbeat health file path
get_health_path() {
    local agent="$1"
    echo "${_INBOX_PATH_PROJECT_ROOT}/queue/watchers/${agent}.health"
}

# get_dead_letter_dir <agent_id>
# returns: dead-letter ディレクトリ
get_dead_letter_dir() {
    local agent="$1"
    echo "${_INBOX_PATH_PROJECT_ROOT}/queue/dead_letter/${agent}"
}

# get_session_health_path <agent_id>
# returns: session health YAML path
get_session_health_path() {
    local agent="$1"
    echo "${_INBOX_PATH_PROJECT_ROOT}/queue/session_health/${agent}.yaml"
}

# is_within_workspace <path>
# returns: 0 if path is within workspace (writable), 1 otherwise
# Phase 0 反省点 t (= symlink + Codex sandbox writable_root 整合) 対応
is_within_workspace() {
    local target="$1"
    local resolved
    resolved=$(realpath -m "$target" 2>/dev/null || echo "$target")
    case "$resolved" in
        "${_INBOX_PATH_PROJECT_ROOT}"*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# verify_inbox_writable <agent_id>
# returns: 0 if inbox path is workspace-writable, 1 otherwise
verify_inbox_writable() {
    local agent="$1"
    local path
    path=$(get_inbox_path "$agent")
    if is_within_workspace "$path"; then
        return 0
    else
        echo "[inbox_path.sh] WARN: $path not within workspace, Codex sandbox may block" >&2
        return 1
    fi
}
