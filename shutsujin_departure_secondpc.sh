#!/usr/bin/env bash
# shutsujin_departure_secondpc.sh — SecondPC 出陣スクリプト
#
# Phase 1 (2026-05-07): SecondPC tmux multiagent session を以下の構成で起動:
#   pane 0 = maeda (前田利家、SecondPC 家老) — 新設
#   pane 1 = ashigaru5
#   pane 2 = ashigaru6
#   pane 3 = ashigaru7
#   pane 4 = ashigaru8 (非常時 +1、~/.openclaw/enable_ashigaru8 フラグで起動)
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

PERMISSION_FLAG="--dangerously-skip-permissions"
SESSION="multiagent"
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

log_war "🏯 SecondPC 出陣 — 前田利家 + ashigaru5/6/7 を構築中..."

# ─── tmux session + window 作成 ───
tmux new-session -d -s "$SESSION" -n "$WINDOW"

# pane 0 = maeda (= 初期 pane)
PANE0=$(tmux display-message -t "$SESSION:$WINDOW" -p '#{pane_id}')

# pane 1, 2, 3 = ashigaru5, 6, 7 を順次 split
PANE1=$(tmux split-window -v -t "$PANE0" -P -F '#{pane_id}')
PANE2=$(tmux split-window -v -t "$PANE1" -P -F '#{pane_id}')
PANE3=$(tmux split-window -v -t "$PANE2" -P -F '#{pane_id}')

# 非常時 +1 (ashigaru8) フラグチェック
ENABLE_A8=""
if [[ -f "$HOME/.openclaw/enable_ashigaru8" ]]; then
    PANE4=$(tmux split-window -v -t "$PANE3" -P -F '#{pane_id}')
    ENABLE_A8="yes"
    log_info "非常時フラグ検知 → ashigaru8 を pane 4 に追加"
fi

# layout を均等 vertical に
tmux select-layout -t "$SESSION:$WINDOW" even-vertical

# ─── pane 識別属性設定 ───
declare -A PANE_AGENT
PANE_AGENT["$PANE0"]="maeda"
PANE_AGENT["$PANE1"]="ashigaru5"
PANE_AGENT["$PANE2"]="ashigaru6"
PANE_AGENT["$PANE3"]="ashigaru7"
[[ -n "$ENABLE_A8" ]] && PANE_AGENT["$PANE4"]="ashigaru8"

for pid in "${!PANE_AGENT[@]}"; do
    agent="${PANE_AGENT[$pid]}"
    tmux set-option -p -t "$pid" @agent_id "$agent"
    tmux set-option -p -t "$pid" @agent_cli "claude"
    tmux set-option -p -t "$pid" @model_name "Opus" 2>/dev/null || true
    log_info "  set @agent_id=$agent → $pid"
done

# ─── claude 起動 ───
CMD="claude --model opus $PERMISSION_FLAG"
for pid in "${!PANE_AGENT[@]}"; do
    agent="${PANE_AGENT[$pid]}"
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
        maeda)
            prompt='拙者前田利家、SecondPC 家老として召喚さる。Session Start: ①tmux display-message で自己識別 → maeda ②mcp__memory__read_graph (失敗時 skip) ③instructions/maeda.md と instructions/karo.md (家老共通) を必読、persona と禁止事項を完全把握 ④queue/inbox/maeda.yaml + queue/tasks/maeda.yaml + queue/reports/maeda_report.yaml 確認 ⑤信長から SecondPC 配下 cmd が届いてれば即着手 ⑥配下 ashigaru5/6/7 の状態確認、idle なら次タスク発令 (= 自走 mandate)。本日 Phase 1 で新設の体制、SecondPC 専属、本丸越境禁止。'
            ;;
        ashigaru*)
            prompt="拙者${agent}、SecondPC で召喚さる。Session Start: ①tmux display-message → ${agent} ②instructions/ashigaru.md 必読 ③queue/tasks/${agent}.yaml + queue/inbox/${agent}.yaml 確認 ④tasks に assign があれば即着手、なければ家老 maeda の指示待ち。報告先は maeda (= SecondPC 家老 前田利家、Phase 1 新設)。"
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
log_info "新体制 (= maeda + a5/a6/a7) で運用開始"
