#!/usr/bin/env bash
# hakudokai_init_agents.sh — 指定agentに初期化プロンプトを投入
#
# Usage:
#   bash shim/hakudokai/hakudokai_init_agents.sh ashigaru2       # 単体
#   bash shim/hakudokai/hakudokai_init_agents.sh ashigaru2-7     # 範囲
#   bash shim/hakudokai/hakudokai_init_agents.sh all             # 全agent
#   bash shim/hakudokai/hakudokai_init_agents.sh karo            # karo
#   bash shim/hakudokai/hakudokai_init_agents.sh gunshi          # gunshi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${SCRIPT_DIR}/lib/tmux_send.sh"
CLINIC_ID="${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"

# Agent→pane mapping
declare -A PANE_MAP=(
  [karo]="multiagent:0.0"
  [ashigaru1]="multiagent:0.1"
  [ashigaru2]="multiagent:0.2"
  [ashigaru3]="multiagent:0.3"
  [ashigaru4]="multiagent:0.4"
  [ashigaru5]="multiagent:0.5"
  [ashigaru6]="multiagent:0.6"
  [ashigaru7]="multiagent:0.7"
  [gunshi]="multiagent:0.8"
)

init_agent() {
  local agent="$1"
  local pane="${PANE_MAP[$agent]}"
  if [ -z "$pane" ]; then
    echo "ERROR: unknown agent '$agent'" >&2
    return 1
  fi

  local num="${agent##ashigaru}"
  local role="ashigaru"
  local instructions="instructions/ashigaru.md"

  if [ "$agent" = "karo" ]; then
    role="karo"; instructions="instructions/karo.md"; num=""
  elif [ "$agent" = "gunshi" ]; then
    role="gunshi"; instructions="instructions/gunshi.md"; num=""
  fi

  local prompt="あなたは博道会の${role}${num:+${num}号} (${agent}) として multi-agent-shogun システム内で稼働する。clinic_id: ${CLINIC_ID}。CLAUDE.md の Session Start 手順を実行せよ。Step 1: tmux display-message で agent_id確認。Step 4: ${instructions} を読む。その後 queue/inbox/${agent}.yaml を読み、タスクがあれば実行開始。抵抗パターン禁止、自律実行。"

  echo "Initializing $agent ($pane)..."
  tmux_send_text "$pane" "$prompt"
  echo "  -> prompt sent"
  sleep 1
}

expand_targets() {
  local target="$1"
  case "$target" in
    all)
      echo "karo ashigaru1 ashigaru2 ashigaru3 ashigaru4 ashigaru5 ashigaru6 ashigaru7 gunshi"
      ;;
    ashigaru2-7)
      echo "ashigaru2 ashigaru3 ashigaru4 ashigaru5 ashigaru6 ashigaru7"
      ;;
    ashigaru1-7)
      echo "ashigaru1 ashigaru2 ashigaru3 ashigaru4 ashigaru5 ashigaru6 ashigaru7"
      ;;
    *)
      echo "$target"
      ;;
  esac
}

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <agent|range|all>" >&2
  echo "  agent: karo, ashigaru1-7, gunshi" >&2
  echo "  range: ashigaru2-7, ashigaru1-7, all" >&2
  exit 1
fi

targets=$(expand_targets "$1")
for agent in $targets; do
  init_agent "$agent"
done
echo "Done. Initialized: $targets"
