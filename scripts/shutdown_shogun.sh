#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# shutdown_shogun.sh — Shogun システム graceful shutdown (= 両 PC)
#
# 陛下御差配 (2026-05-10): 終了手順の不整が stale 累積 + 次回汚染の真因。
# Lord が「終了」発話 → 拙者 (信長) が本 script 起動、両 PC を逆順 graceful 停止。
#
# 順序 (= 起動の逆):
#   1. SecondPC bridge process stop
#   2. SecondPC tmux sessions kill (shogun, multiagent, bridge)
#   3. SecondPC stale watcher process kill
#   4. MainPC bridge process stop
#   5. MainPC stale watcher process kill
#   6. MainPC tmux sessions kill (shogun は最後、自分自身)
#
# 副次効果: 次回起動時 stale 0 化、coherence 即 10/10
#
# Usage:
#   bash scripts/shutdown_shogun.sh           # 通常終了 (= 確認なし)
#   bash scripts/shutdown_shogun.sh --dry-run # 何も kill せず list のみ
#   bash scripts/shutdown_shogun.sh --confirm # 1 段毎に確認
# ════════════════════════════════════════════════════════════════
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck source=/dev/null
source "$REPO_ROOT/lib/agent_pane_mapping.sh" 2>/dev/null || true

DRY_RUN="no"
CONFIRM="yes"   # 既定 confirm 必須 (= 黒田 kl3 是正、shogun.md confirm_required:true と整合)
for arg in "$@"; do
    [ "$arg" = "--dry-run" ] && DRY_RUN="yes"
    [ "$arg" = "--no-confirm" ] && CONFIRM="no"   # 明示で skip 可 (= 自動化用)
done

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/shutdown_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "═══════════════════════════════════════════════════════════"
echo "  Shogun System Graceful Shutdown — $(date -Iseconds)"
echo "  dry_run=$DRY_RUN confirm=$CONFIRM"
echo "═══════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────
# Helper: confirm / dry-run aware kill
# ─────────────────────────────────────────────────────────────
safe_kill() {
    local pid="$1"
    local desc="$2"
    if [ -z "$pid" ]; then
        echo "  [skip] $desc — PID 不在"
        return 0
    fi
    if [ "$DRY_RUN" = "yes" ]; then
        echo "  [dry-run] kill $pid ($desc)"
        return 0
    fi
    if [ "$CONFIRM" = "yes" ]; then
        read -r -p "  kill $pid ($desc)? [y/N] " ans
        [ "$ans" != "y" ] && return 0
    fi
    kill "$pid" 2>&1 && echo "  [killed] $pid $desc" || echo "  [fail] $pid $desc"
}

safe_tmux_kill() {
    local target="$1"
    local where="$2"  # local | secondpc
    if [ "$DRY_RUN" = "yes" ]; then
        echo "  [dry-run] tmux kill-session $target ($where)"
        return 0
    fi
    if [ "$where" = "local" ]; then
        tmux kill-session -t "$target" 2>&1 || echo "  [skip] $target 不在"
    else
        ssh -o BatchMode=yes -p 2222 User@192.168.11.47 "wsl -- bash -lc \"tmux kill-session -t $target 2>&1\"" 2>&1 || echo "  [skip] $target 不在 SecondPC"
    fi
}

# ─────────────────────────────────────────────────────────────
# Step 1-3: SecondPC 停止 (= 起動順の逆)
# ─────────────────────────────────────────────────────────────
echo ""
echo "═══ Step 1-3: SecondPC graceful shutdown ═══"

if [ "$DRY_RUN" = "yes" ]; then
    echo "  [dry-run] SecondPC SSH connection skipped"
else
    # 1. SecondPC bridge process stop
    echo "[1] SecondPC bridge process stop"
    SECONDPC_BRIDGE=$(ssh -o BatchMode=yes -p 2222 User@192.168.11.47 \
        'wsl -- bash -lc "pgrep -f hakudokai_realtime_bridge"' 2>/dev/null | head -1)
    if [ -n "$SECONDPC_BRIDGE" ]; then
        ssh -o BatchMode=yes -p 2222 User@192.168.11.47 \
            "wsl -- bash -lc \"kill $SECONDPC_BRIDGE\"" 2>&1
        echo "  [killed] SecondPC bridge PID $SECONDPC_BRIDGE"
    else
        echo "  [skip] SecondPC bridge 不在"
    fi

    # 2. SecondPC stale watchers kill
    echo "[2] SecondPC inbox_watcher daemon kill"
    ssh -o BatchMode=yes -p 2222 User@192.168.11.47 \
        'wsl -- bash -lc "for pid in \$(pgrep -f scripts/inbox_watcher.sh); do kill \$pid; done; pgrep -f scripts/watcher_supervisor.sh | xargs -r kill"' 2>&1

    # 3. SecondPC tmux sessions kill (= bridge → multiagent → shogun)
    echo "[3] SecondPC tmux sessions kill"
    for sess in bridge multiagent shogun; do
        safe_tmux_kill "$sess" secondpc
    done
fi

# ─────────────────────────────────────────────────────────────
# Step 4-6: MainPC 停止
# ─────────────────────────────────────────────────────────────
echo ""
echo "═══ Step 4-6: MainPC graceful shutdown ═══"

# 4. MainPC bridge process stop
echo "[4] MainPC bridge process stop"
MAINPC_BRIDGE=$(pgrep -f hakudokai_realtime_bridge | head -1)
safe_kill "$MAINPC_BRIDGE" "MainPC bridge"

# 5. MainPC stale watchers kill (= 信長 P002 specific PID)
echo "[5] MainPC inbox_watcher + supervisor daemon kill"
for pid in $(pgrep -f "scripts/inbox_watcher.sh"); do
    safe_kill "$pid" "inbox_watcher PID=$pid"
done
for pid in $(pgrep -f "scripts/watcher_supervisor.sh"); do
    safe_kill "$pid" "watcher_supervisor PID=$pid"
done

# 6. MainPC tmux sessions kill (= 自分自身 shogun は最後)
echo "[6] MainPC tmux sessions kill"
# multiagent 先 (= karo + ashigaru + 軍師 全停止)
safe_tmux_kill multiagent local
# bridge session (もしあれば)
safe_tmux_kill bridge local
# shogun は最後 (= 自分自身ゆえ kill すると本 script も死ぬ)
echo "  [note] shogun session は本 script の親、kill すると本 script も終了"
if [ "$DRY_RUN" != "yes" ]; then
    echo "  → tmux kill-session shogun は最後、本 script の最終 line で実行"
fi

echo ""
echo "═══ Shutdown 完遂 — $(date -Iseconds) ═══"
echo "log: $LOG_FILE"
echo ""

if [ "$DRY_RUN" != "yes" ]; then
    echo "[Final] tmux kill-session shogun (= 本 script 終了と同時)"
    sleep 2
    tmux kill-session -t shogun 2>&1 || echo "shogun session 既不在"
fi
