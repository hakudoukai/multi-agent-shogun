#!/usr/bin/env bash
# shutsujin_departure_secondpc.sh — SecondPC 出陣スクリプト
#
# Phase 1 (2026-05-07): SecondPC tmux multiagent session を以下の構成で起動:
#   pane 0 = karo-second (SecondPC 家老) — 新設
#   pane 1 = ashigaru5
#   pane 2 = ashigaru6
#   pane 3 = ashigaru7
#   pane 4 = gunshi-second (SecondPC 軍師、Opus) — staged recovery seq95958 で新設
#   pane 5-8 = ashigaru1-4 : HOLD (agent_id 衝突ブロッカーで未実装、owner 裁定待ち)
#   pane (末尾) = ashigaru8 (registered standby、~/.openclaw/enable_ashigaru8 フラグで起動)
#
# 前提:
#   - WSL2 + Ubuntu 上で実行
#   - claude CLI がインストール済み (= /home/hakudokai/.local/share/claude/code)
#   - hakudoukai@gmail.com (Claude Max 20x) でログイン済
#   - shim/hakudokai/hakudokai_secondpc_receiver.sh が cron / systemd で起動可能
#
# 既存 session があれば warning + abort (= 慎重に kill して再構築するため)。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PERMISSION_FLAG=""  # D4: no bypass for SecondPC worker agents
SESSION="multiagent-second"
WINDOW="agents"

log_info() { echo "  [shutsujin-secondpc] $*"; }
log_war() { echo ""; echo "⚔️  $*"; echo ""; }

# ─── 既存 session 確認 ───
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo ""
    echo "  ╔════════════════════════════════════════════════════════════╗"
    echo "  ║  [WARN] 既存の '$SESSION' tmux session が存在する          ║"
    echo "  ║  本スクリプトは新規構築用。既存を破棄するなら:              ║"
    echo "  ║    tmux kill-session -t $SESSION                            ║"
    echo "  ║  実行後、本スクリプトを再実行。                             ║"
    echo "  ╚════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

log_war "🏯 SecondPC 出陣 — karo-second + gunshi-second + ashigaru5/6/7 を構築中..."

# ─── tmux session + window 作成 ───
tmux new-session -d -s "$SESSION" -n "$WINDOW"

# pane 0 = karo-second (= 初期 pane)
PANE0=$(tmux display-message -t "$SESSION:$WINDOW" -p '#{pane_id}')

# pane 1, 2, 3 = ashigaru5, 6, 7 を順次 split
PANE1=$(tmux split-window -v -t "$PANE0" -P -F '#{pane_id}')
PANE2=$(tmux split-window -v -t "$PANE1" -P -F '#{pane_id}')
PANE3=$(tmux split-window -v -t "$PANE2" -P -F '#{pane_id}')

# pane 4 = gunshi-second (SecondPC 軍師、Opus) — staged recovery seq95958
PANE4=$(tmux split-window -v -t "$PANE3" -P -F '#{pane_id}')

# HOLD: ashigaru1-4 (pane 5-8) は agent_id 衝突ブロッカーにより本スクリプトへ未追加。
#   owner (shogun-second) の id namespacing 裁定後に個別 split で追加する。

# registered standby (ashigaru8) フラグチェック — 末尾 pane
ENABLE_A8=""
if [[ -f "$HOME/.openclaw/enable_ashigaru8" ]]; then
    PANE_A8=$(tmux split-window -v -t "$PANE4" -P -F '#{pane_id}')
    ENABLE_A8="yes"
    log_info "standby フラグ検知 → ashigaru8 を末尾 pane に追加"
fi

# layout を均等 vertical に
tmux select-layout -t "$SESSION:$WINDOW" even-vertical

# ─── pane 識別属性設定 ───
declare -A PANE_AGENT
PANE_AGENT["$PANE0"]="karo-second"
PANE_AGENT["$PANE1"]="ashigaru5"
PANE_AGENT["$PANE2"]="ashigaru6"
PANE_AGENT["$PANE3"]="ashigaru7"
PANE_AGENT["$PANE4"]="gunshi-second"
[[ -n "$ENABLE_A8" ]] && PANE_AGENT["$PANE_A8"]="ashigaru8"

for pid in "${!PANE_AGENT[@]}"; do
    agent="${PANE_AGENT[$pid]}"
    tmux set-option -p -t "$pid" @agent_id "$agent"
    tmux set-option -p -t "$pid" @agent_cli "claude"
    case "$agent" in
        karo-second) tmux set-option -p -t "$pid" @model_name "Fable5" 2>/dev/null || true ;;
        gunshi-second) tmux set-option -p -t "$pid" @model_name "Opus" 2>/dev/null || true ;;
        ashigaru*) tmux set-option -p -t "$pid" @model_name "Sonnet5" 2>/dev/null || true ;;
        *) tmux set-option -p -t "$pid" @model_name "Sonnet5" 2>/dev/null || true ;;
    esac
    log_info "  set @agent_id=$agent → $pid"
done

# ─── claude 起動 ───
for pid in "${!PANE_AGENT[@]}"; do
    agent="${PANE_AGENT[$pid]}"
    case "$agent" in
        karo-second)
            CMD="bash -lc 'claude --model claude-fable-5; rc=\$?; echo CLAUDE_EXIT:\$rc; exec bash'"
            ;;
        gunshi-second)
            # 所見(v4.4編成時記録): 軍師は本令対象外ゆえ現状維持。現行運用のCodex化とは乖離あり(是正は別途裁可事項)。
            CMD="bash -lc 'claude --model opus; rc=\$?; echo CLAUDE_EXIT:\$rc; exec bash'"
            ;;
        ashigaru*)
            CMD="bash -lc 'claude --model claude-sonnet-5; rc=\$?; echo CLAUDE_EXIT:\$rc; exec bash'"
            ;;
        *)
            CMD="bash -lc 'claude --model claude-sonnet-5; rc=\$?; echo CLAUDE_EXIT:\$rc; exec bash'"
            ;;
    esac
    tmux send-keys -t "$pid" "$CMD" Enter
    log_info "  claude 起動: $agent ($pid)"
done

# 12 秒待機 (= claude 起動完了)
log_info "claude 起動完了を待機中 (12 秒)..."
sleep 12

# ─── 各 pane に Session Start 指示 ───
for pid in "${!PANE_AGENT[@]}"; do
    agent="${PANE_AGENT[$pid]}"
    case "$agent" in
        karo-second)
            prompt='拙者SecondPC 家老として召喚さる。Session Start: ①tmux display-message で自己識別 → karo-second ②instructions/karo-second.md + instructions/karo.md + queue/pane_registry.yaml を必読 ③persona/禁止事項/SecondPC専属境界を確認 ④queue/inbox/karo-second.yaml + queue/tasks/karo-second.yaml + queue/reports/karo-second_report.yaml 確認 ⑤配下 ashigaru5/6/7 の @agent_id と各自 task/inbox 状態確認 ⑥未割当なら勝手に同一作業を重複発令せず、役割分担を明示してから発令。本丸越境禁止。'
            ;;
        gunshi-second)
            prompt='拙者SecondPC 軍師として召喚さる。Session Start: ①tmux display-message で自己識別 → gunshi-second ②instructions/gunshi-second.md + instructions/gunshi.md + queue/pane_registry.yaml を必読 ③persona/禁止事項/SecondPC専属境界を確認 ④queue/inbox/gunshi-second.yaml + queue/tasks/gunshi-second.yaml 確認 ⑤役割=SecondPC の品質監査役 (足軽成果物の QC・PDCA)、新規タスク発令は禁 (F003)。報告先=shogun-second/karo-second。本丸越境禁止。'
            ;;
        ashigaru*)
            prompt="拙者${agent}、SecondPC で召喚さる。Session Start: ①tmux display-message → ${agent} ②instructions/ashigaru.md + instructions/roles/ashigaru_role.md を必読 ③自分専用 queue/tasks/${agent}.yaml + queue/inbox/${agent}.yaml のみ確認 ④他足軽taskを読まない/同一作業を勝手に重複しない ⑤assign があれば自分の担当分だけ着手、なければ karo-second 指示待ち。報告先は karo-second。"
            ;;
    esac
    tmux send-keys -t "$pid" "$prompt"
    sleep 0.3
    tmux send-keys -t "$pid" Enter
done

# ─── inbox_watcher 起動 ───
log_info "inbox_watcher 起動中..."
for pid in "${!PANE_AGENT[@]}"; do
    agent="${PANE_AGENT[$pid]}"
    pane_target="$SESSION:$WINDOW.$(tmux display-message -t "$pid" -p '#{pane_index}')"
    nohup bash "$SCRIPT_DIR/scripts/inbox_watcher.sh" "$agent" "$pane_target" "claude" \
        > "/tmp/inbox_watcher_${agent}.log" 2>&1 &
    log_info "  watcher: $agent → $pane_target (PID $!)"
done

# ─── receiver.sh 起動 (= MainPC からの cross_pc 配信を受信) ───
if ! ps -ef | grep -q "[s]econdpc_receiver"; then
    log_info "SecondPC receiver.sh を起動中..."
    nohup bash "$SCRIPT_DIR/shim/hakudokai/hakudokai_secondpc_receiver.sh" \
        > /tmp/secondpc_receiver.log 2>&1 &
    log_info "  receiver: PID $!"
fi

# ─── 結果 ───
echo ""
log_war "🏯 SecondPC 出陣完了"
tmux list-panes -t "$SESSION:$WINDOW" -F '  agents.#{pane_index}  @agent_id=#{@agent_id}  pid=#{pane_pid}'
echo ""
log_info "tmux attach -t $SESSION で確認可能"
log_info "新体制 (= karo-second + gunshi-second + a5/a6/a7 [+a8 standby]) で運用開始"
