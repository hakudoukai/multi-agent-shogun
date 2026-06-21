#!/bin/bash
# setup_shogun_third.sh — サードPC 9 agent tmux session 起動
# 副医院長殿 directive a2a9ce8f / 403c3b7b 整合
# Session: shogun-third (= shogun-{pc} pane 0) + multiagent-third (= 9 agent pane)

set -e
PC=mc
SHOGUN_SESSION="shogun-${PC}"
MULTI_SESSION="multiagent-${PC}"

# kill existing sessions if present
tmux kill-session -t "$SHOGUN_SESSION" 2>/dev/null || true
tmux kill-session -t "$MULTI_SESSION" 2>/dev/null || true

# === shogun-third session (= pane 0、本職 Shogun) ===
tmux new-session -d -s "$SHOGUN_SESSION" -x 200 -y 50 -n shogun
tmux send-keys -t "$SHOGUN_SESSION":shogun "echo 'shogun-${PC} ready (= pane 0)'" Enter

# === multiagent-third session (= pane 1-9 = karo + 7 ashigaru + gunshi) ===
tmux new-session -d -s "$MULTI_SESSION" -x 200 -y 50 -n agents
# pane 0 already exists (= karo)
tmux send-keys -t "$MULTI_SESSION":agents.0 "echo 'karo-${PC} ready (= pane 1)'" Enter

# split 8 more panes (= pane 1-8 = ashigaru 1-7 + gunshi)
for i in 1 2 3 4 5 6 7 8; do
  tmux split-window -t "$MULTI_SESSION":agents -v 2>/dev/null || tmux split-window -t "$MULTI_SESSION":agents -h
  case $i in
    1) lbl="ashigaru-${PC}-1 (= 企画 / pane 2)" ;;
    2) lbl="ashigaru-${PC}-2 (= 設計 / pane 3)" ;;
    3) lbl="ashigaru-${PC}-3 (= 実装FE / pane 4)" ;;
    4) lbl="ashigaru-${PC}-4 (= 実装BE / pane 5)" ;;
    5) lbl="ashigaru-${PC}-5 (= テスト / pane 6)" ;;
    6) lbl="ashigaru-${PC}-6 (= 監査 Codex / pane 7)" ;;
    7) lbl="ashigaru-${PC}-7 (= 運用 / pane 8)" ;;
    8) lbl="gunshi-${PC} (= 軍師 Codex / pane 9)" ;;
  esac
  tmux send-keys -t "$MULTI_SESSION":agents "echo '$lbl ready'" Enter
  tmux select-layout -t "$MULTI_SESSION":agents tiled 2>/dev/null
done

tmux select-layout -t "$MULTI_SESSION":agents tiled

# agent_id pane property 装着 (= F002 識別用)
tmux set -t "$SHOGUN_SESSION":shogun.0 -p @agent_id "shogun-${PC}" 2>/dev/null
tmux set -t "$MULTI_SESSION":agents.0 -p @agent_id "karo-${PC}" 2>/dev/null
for i in 1 2 3 4 5 6 7; do
  tmux set -t "$MULTI_SESSION":agents.$i -p @agent_id "ashigaru-${PC}-${i}" 2>/dev/null
done
tmux set -t "$MULTI_SESSION":agents.8 -p @agent_id "gunshi-${PC}" 2>/dev/null

echo "=== セッション作成完遂 ==="
tmux list-sessions
echo "--- panes (= shogun-${PC}) ---"
tmux list-panes -t "$SHOGUN_SESSION":shogun -F '#{session_name}:#{window_index}.#{pane_index} #{@agent_id}'
echo "--- panes (= multiagent-${PC}) ---"
tmux list-panes -t "$MULTI_SESSION":agents -F '#{session_name}:#{window_index}.#{pane_index} #{@agent_id}'
