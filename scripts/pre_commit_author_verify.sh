#!/usr/bin/env bash
# pre_commit_author_verify.sh — cmd_inbox_reform cycle 17 黒田 v2 P0#2/#3 fix
#
# 目的:
#   SessionStart hook で session 起動時に git config --local user.{name,email}
#   を agent_id 別自動設定するが、.git/config --local は repo 共有資源ゆえ
#   last-write-wins race (= 他 agent の session_start_hook が後刻 overwrite)
#   が commit 直前に発生し author 不整合 commit を作る risk が残る。
#
#   本 wrapper は commit 直前に呼び出し、現 session の agent_id と
#   現 --local user.{name,email} を個別 verify、不一致時に再設定する。
#   二重 safety = session start (hook) + commit 直前 (wrapper)。
#
# 使い方:
#   - 手動: 任意の git commit 直前に `bash scripts/pre_commit_author_verify.sh`
#   - .pre-commit-config.yaml の local hook 経由 (pre-commit install 済の場合)
#
# Exit code:
#   0 = author 整合 OK (set / verified)
#   1 = agent_id 未取得 (= TMUX_PANE 未設定 / tmux 不在) → 個人開発扱い、commit 続行可
#   2 = whitelist 外 agent_id → 設定 skip、karo 報告 path (但し commit は許可しない)
#   3 = git config 設定失敗 → karo 報告 path、commit 阻止

set -uo pipefail

GIT_CONFIG_AGENT_ID_WHITELIST="shogun karo gunshi ashigaru1 ashigaru2 ashigaru3 ashigaru4 ashigaru5 ashigaru6 ashigaru7"

AGENT_ID=""
if [ -n "${TMUX_PANE:-}" ]; then
    AGENT_ID=$(tmux display-message -t "$TMUX_PANE" -p '#{@agent_id}' 2>/dev/null || true)
fi
# env override (= 試験 / CI 兼用)
if [ -n "${PRE_COMMIT_AGENT_ID:-}" ]; then
    AGENT_ID="$PRE_COMMIT_AGENT_ID"
fi

if [ -z "$AGENT_ID" ]; then
    echo "[pre_commit_author_verify] agent_id 未取得 (= TMUX_PANE 未設定 / tmux 不在)、個人開発扱いで pass" >&2
    exit 1
fi

# REPO_ROOT 解決: env override > git rev-parse > script 位置 fallback
REPO_ROOT="${PRE_COMMIT_REPO_ROOT:-}"
if [ -z "$REPO_ROOT" ]; then
    REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
fi
if [ -z "$REPO_ROOT" ]; then
    if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
        REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    else
        REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
    fi
fi

# whitelist check
matched=0
for wl in $GIT_CONFIG_AGENT_ID_WHITELIST; do
    if [ "$AGENT_ID" = "$wl" ]; then
        matched=1
        break
    fi
done

if [ "$matched" -eq 0 ]; then
    cat <<WARN >&2
[pre_commit_author_verify] WARNING — agent_id whitelist 외、commit 阻止:
   agent_id=$AGENT_ID
   whitelist=$GIT_CONFIG_AGENT_ID_WHITELIST
   訂正 path: karo に inbox_write で「agent_id=$AGENT_ID whitelist 외、commit pre-check 阻止」報告 (= 自分で whitelist 拡張禁、F002 違反 risk 防止)
WARN
    exit 2
fi

EXPECTED_NAME="$AGENT_ID"
EXPECTED_EMAIL="${AGENT_ID}@multi-agent-shogun.local"

CURRENT_NAME=$(git -C "$REPO_ROOT" config --local --get user.name 2>/dev/null || true)
CURRENT_EMAIL=$(git -C "$REPO_ROOT" config --local --get user.email 2>/dev/null || true)

DRIFT=0
if [ "$CURRENT_NAME" != "$EXPECTED_NAME" ]; then
    DRIFT=1
fi
if [ "$CURRENT_EMAIL" != "$EXPECTED_EMAIL" ]; then
    DRIFT=1
fi

if [ "$DRIFT" -eq 0 ]; then
    echo "[pre_commit_author_verify] author 整合 verify pass (= $EXPECTED_NAME / $EXPECTED_EMAIL)" >&2
    exit 0
fi

# DRIFT 検知 → 再設定 (= last-write-wins race 補正)
cat <<DRIFT_MSG >&2
[pre_commit_author_verify] author drift detected, resetting:
   agent_id=$AGENT_ID
   expected: $EXPECTED_NAME / $EXPECTED_EMAIL
   current:  ${CURRENT_NAME:-<unset>} / ${CURRENT_EMAIL:-<unset>}
   原因 candidate: 他 agent の session_start_hook が後刻 overwrite (= last-write-wins race)
DRIFT_MSG

if ! git -C "$REPO_ROOT" config --local user.name "$EXPECTED_NAME"; then
    echo "[pre_commit_author_verify] ERROR — git config --local user.name set 失敗、commit 阻止" >&2
    exit 3
fi
if ! git -C "$REPO_ROOT" config --local user.email "$EXPECTED_EMAIL"; then
    echo "[pre_commit_author_verify] ERROR — git config --local user.email set 失敗、commit 阻止" >&2
    exit 3
fi

echo "[pre_commit_author_verify] author drift 補正完遂、commit 続行可" >&2
exit 0
