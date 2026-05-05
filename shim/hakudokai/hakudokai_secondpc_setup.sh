#!/usr/bin/env bash
# hakudokai_secondpc_setup.sh — SecondPC ワンコマンドセットアップ (2エージェント版)
#
# SecondPC上でこのスクリプトを実行すると:
#   1. 環境チェック (git, python3, inotify-tools, claude CLI)
#   2. リポジトリ同期 (git pull)
#   3. Supabase環境変数確認
#   4. tmux session作成 (2pane: 桜ちゃん + クロちゃん)
#   5. Claude Code CLI起動 (ashigaru2 + ashigaru8)
#   6. watcher群起動 (inbox_watcher x2 + Supabase bridge receiver)
#   7. 初期化プロンプト送信
#
# Usage:
#   cd /path/to/multi-agent-shogun
#   bash shim/hakudokai/hakudokai_secondpc_setup.sh
#
# 前提:
#   - リポジトリがclone済み
#   - ~/.hakudokai/env にSupabase環境変数あり
#   - claude CLI インストール済み + 桜ちゃんアカウントでログイン済み

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PC_ID="second_pc"
TMUX_SESSION="secondpc"

# エージェント定義 (2名体制)
AGENT1_ID="ashigaru2"
AGENT1_NAME="sakura"
AGENT1_PANE="${TMUX_SESSION}:0.0"

AGENT2_ID="ashigaru8"
AGENT2_NAME="kuro"
AGENT2_PANE="${TMUX_SESSION}:0.1"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "[setup] $1"; }
ok()  { echo -e "  ${GREEN}OK${NC}: $1"; }
ng()  { echo -e "  ${RED}NG${NC}: $1"; }
warn(){ echo -e "  ${YELLOW}WARN${NC}: $1"; }

errors=0

# ============================================================
# Phase 1: 環境チェック
# ============================================================
log "Phase 1: 環境チェック"

# git
if command -v git &>/dev/null; then
  ok "git $(git --version | head -1)"
else
  ng "git not found"
  errors=$((errors + 1))
fi

# python3
if command -v python3 &>/dev/null; then
  ok "python3 $(python3 --version 2>&1)"
else
  ng "python3 not found"
  errors=$((errors + 1))
fi

# inotifywait
if command -v inotifywait &>/dev/null; then
  ok "inotifywait available"
else
  ng "inotifywait not found. Install: sudo apt install inotify-tools"
  errors=$((errors + 1))
fi

# claude CLI
if command -v claude &>/dev/null; then
  ok "claude CLI available"
else
  ng "claude CLI not found. Install from https://claude.ai/download"
  errors=$((errors + 1))
fi

# tmux
if command -v tmux &>/dev/null; then
  ok "tmux available"
else
  ng "tmux not found. Install: sudo apt install tmux"
  errors=$((errors + 1))
fi

# Supabase env
if [ -f "$HOME/.hakudokai/env" ]; then
  SB_URL=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  SB_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
  if [ -n "$SB_URL" ] && [ -n "$SB_KEY" ]; then
    ok "Supabase env loaded"
    export SUPABASE_URL="$SB_URL" SUPABASE_SERVICE_ROLE_KEY="$SB_KEY"
  else
    ng "Supabase env incomplete in ~/.hakudokai/env"
    errors=$((errors + 1))
  fi
else
  ng "~/.hakudokai/env not found"
  echo "    Create it with:"
  echo "    echo 'SUPABASE_URL=https://xxx.supabase.co' > ~/.hakudokai/env"
  echo "    echo 'SUPABASE_SERVICE_ROLE_KEY=eyJ...' >> ~/.hakudokai/env"
  errors=$((errors + 1))
fi

if [ $errors -gt 0 ]; then
  log "${RED}${errors} error(s) found. Fix them and re-run.${NC}"
  exit 1
fi

log "環境チェック: ALL OK"
echo ""

# ============================================================
# Phase 2: リポジトリ同期
# ============================================================
log "Phase 2a: git credential helper セットアップ"

# WSL から Windows Git Credential Manager を使えるようにする
GCM_EXE="/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe"
GCM_LINK="$HOME/bin/git-credential-manager.exe"

if [ -f "$GCM_EXE" ]; then
  CURRENT_HELPER=$(git config --global credential.helper 2>/dev/null || true)
  if [ "$CURRENT_HELPER" != "$GCM_LINK" ]; then
    mkdir -p "$HOME/bin"
    ln -sf "$GCM_EXE" "$GCM_LINK"
    git config --global credential.helper "$GCM_LINK"
    ok "credential helper → $GCM_LINK (symlink to Windows GCM)"
  else
    ok "credential helper already configured"
  fi
else
  warn "Windows Git not found at $GCM_EXE — git push/pull may fail"
fi

log "Phase 2b: multi-agent-shogun リポジトリ同期"

cd "$SCRIPT_DIR"
git fetch origin 2>/dev/null
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "unknown")

if [ "$LOCAL" = "$REMOTE" ]; then
  ok "multi-agent-shogun: up to date ($LOCAL)"
else
  log "Pulling latest changes..."
  git pull --ff-only origin main 2>&1 && ok "Updated to $(git rev-parse HEAD)" || warn "Pull failed (may need manual merge)"
fi

log "Phase 2c: DentalBI リポジトリ同期"

# DentalBI のパスを検出（MainPC と SecondPC で異なる）
DENTALBI_CANDIDATES=(
  "/mnt/c/Users/User/Documents/DentalBI"
  "/mnt/c/Projects/hakudokai-dev"
  "$HOME/Documents/DentalBI"
)
DENTALBI_DIR=""
for d in "${DENTALBI_CANDIDATES[@]}"; do
  if [ -d "$d/.git" ]; then
    DENTALBI_DIR="$d"
    break
  fi
done

if [ -n "$DENTALBI_DIR" ]; then
  log "  DentalBI found at: $DENTALBI_DIR"
  cd "$DENTALBI_DIR"

  # git hooks の CRLF 修正（WSL で実行不可になる問題の防止）
  for hook in .git/hooks/*; do
    if [ -f "$hook" ] && file "$hook" 2>/dev/null | grep -q "CRLF"; then
      sed -i 's/\r$//' "$hook"
      chmod +x "$hook"
      ok "  fixed CRLF in $(basename "$hook")"
    fi
  done

  # デフォルトブランチを検出して同期
  DENTALBI_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo "master")
  CURRENT_BRANCH=$(git branch --show-current)

  git fetch origin 2>/dev/null
  DB_LOCAL=$(git rev-parse HEAD)
  DB_REMOTE=$(git rev-parse "origin/$DENTALBI_BRANCH" 2>/dev/null || echo "unknown")

  if [ "$DB_LOCAL" = "$DB_REMOTE" ]; then
    ok "DentalBI: up to date ($DB_LOCAL)"
  else
    # 作業中のブランチでない場合のみ自動マージ
    if [ "$CURRENT_BRANCH" = "$DENTALBI_BRANCH" ]; then
      git pull --ff-only origin "$DENTALBI_BRANCH" 2>&1 && ok "DentalBI: updated to $(git rev-parse HEAD)" || warn "DentalBI: pull failed (may need manual merge)"
    else
      warn "DentalBI: on branch '$CURRENT_BRANCH' (not '$DENTALBI_BRANCH'), skipping auto-pull"
    fi
  fi

  # git hooks インストール（リポジトリ管理のhooksを .git/hooks/ に配置）
  if [ -f "scripts/git-hooks/install.sh" ]; then
    bash scripts/git-hooks/install.sh
    ok "DentalBI: git hooks installed"
  fi

  # npm install（package-lock.json が更新されている場合のみ）
  if [ -d "frontend" ]; then
    cd frontend
    if git diff "$DB_LOCAL" "$DB_REMOTE" --name-only 2>/dev/null | grep -q "frontend/package"; then
      log "  package.json changed — running npm install..."
      npm install --no-audit --no-fund 2>&1 | tail -3
      ok "DentalBI frontend: npm install done"
    else
      ok "DentalBI frontend: packages unchanged"
    fi
  fi

  cd "$SCRIPT_DIR"
else
  warn "DentalBI repo not found. Expected locations:"
  for d in "${DENTALBI_CANDIDATES[@]}"; do
    echo "    - $d"
  done
fi

log "Phase 2d: Claude Code MCP設定同期"

# agentation MCP が未設定なら追加
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
if [ -f "$CLAUDE_SETTINGS" ]; then
  if grep -q "agentation" "$CLAUDE_SETTINGS"; then
    ok "Claude Code MCP: agentation already configured"
  else
    # jq があれば使う、なければ python3 で追加
    if command -v jq &>/dev/null; then
      jq '.mcpServers.agentation = {"command": "npx", "args": ["-y", "agentation-mcp@latest"]}' "$CLAUDE_SETTINGS" > "${CLAUDE_SETTINGS}.tmp" \
        && mv "${CLAUDE_SETTINGS}.tmp" "$CLAUDE_SETTINGS"
    else
      python3 -c "
import json, pathlib
p = pathlib.Path('$CLAUDE_SETTINGS')
d = json.loads(p.read_text())
d.setdefault('mcpServers', {})['agentation'] = {'command': 'npx', 'args': ['-y', 'agentation-mcp@latest']}
p.write_text(json.dumps(d, indent=2) + '\n')
"
    fi
    ok "Claude Code MCP: agentation added"
  fi
else
  mkdir -p "$HOME/.claude"
  cat > "$CLAUDE_SETTINGS" << 'SETTINGS_EOF'
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "agentation": {
      "command": "npx",
      "args": ["-y", "agentation-mcp@latest"]
    }
  }
}
SETTINGS_EOF
  ok "Claude Code MCP: settings.json created"
fi

# design-feedback フォルダ作成
FEEDBACK_DIR="/mnt/c/Users/User/Desktop/design-feedback"
mkdir -p "$FEEDBACK_DIR" 2>/dev/null && ok "design-feedback folder: $FEEDBACK_DIR" || true
echo ""

# ============================================================
# Phase 3: tmux session作成 (2pane構成)
# ============================================================
log "Phase 3: tmux session作成 (2pane: ${AGENT1_NAME} + ${AGENT2_NAME})"

if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  warn "tmux session '$TMUX_SESSION' already exists — killing and recreating"
  tmux kill-session -t "$TMUX_SESSION" 2>/dev/null
  sleep 1
fi

# 常に新規作成（既存セッションのpane構成が壊れている可能性を排除）
tmux new-session -d -s "$TMUX_SESSION" -c "$SCRIPT_DIR"
# 2つ目のpaneを作成 (水平分割)
tmux split-window -h -t "${TMUX_SESSION}:0" -c "$SCRIPT_DIR"
ok "tmux session '$TMUX_SESSION' created (2 panes)"

# pane数を確認
PANE_COUNT=$(tmux list-panes -t "${TMUX_SESSION}:0" 2>/dev/null | wc -l)
if [ "$PANE_COUNT" -ne 2 ]; then
  ng "Expected 2 panes, got $PANE_COUNT — aborting"
  exit 1
fi

# Set agent_id on each pane（-p = pane-level option, not window-level）
tmux set-option -p -t "$AGENT1_PANE" @agent_id "$AGENT1_ID" 2>/dev/null
ok "pane 0: agent_id=${AGENT1_ID} (${AGENT1_NAME})"

tmux set-option -p -t "$AGENT2_PANE" @agent_id "$AGENT2_ID" 2>/dev/null
ok "pane 1: agent_id=${AGENT2_ID} (${AGENT2_NAME})"

# 設定後に検証
VERIFY1=$(tmux display-message -t "$AGENT1_PANE" -p '#{@agent_id}' 2>/dev/null)
VERIFY2=$(tmux display-message -t "$AGENT2_PANE" -p '#{@agent_id}' 2>/dev/null)
if [ "$VERIFY1" != "$AGENT1_ID" ] || [ "$VERIFY2" != "$AGENT2_ID" ]; then
  ng "agent_id verification failed: pane0=$VERIFY1 (expected $AGENT1_ID), pane1=$VERIFY2 (expected $AGENT2_ID)"
  exit 1
fi
ok "agent_id verified: pane0=$VERIFY1, pane1=$VERIFY2"
echo ""

# ============================================================
# Phase 4: inbox ディレクトリ準備
# ============================================================
log "Phase 4: inbox準備"

INBOX_DIR="$SCRIPT_DIR/queue/inbox"
mkdir -p "$INBOX_DIR"

for AGENT_ID in "$AGENT1_ID" "$AGENT2_ID"; do
  if [ ! -f "$INBOX_DIR/${AGENT_ID}.yaml" ]; then
    echo "messages: []" > "$INBOX_DIR/${AGENT_ID}.yaml"
    ok "Created ${AGENT_ID}.yaml"
  else
    ok "${AGENT_ID}.yaml exists"
  fi
done
echo ""

# ============================================================
# Phase 5: Claude Code CLI起動 (2エージェント)
# ============================================================
log "Phase 5: Claude Code CLI起動"

source "${SCRIPT_DIR}/lib/tmux_send.sh"

launch_claude() {
  local pane="$1"
  local agent_name="$2"

  PANE_CMD=$(tmux display-message -t "$pane" -p '#{pane_current_command}' 2>/dev/null)
  if [ "$PANE_CMD" = "claude" ] || [ "$PANE_CMD" = "node" ]; then
    warn "${agent_name}: Claude CLI already running in $pane"
  else
    tmux_send_text "$pane" "cd $SCRIPT_DIR && claude --dangerously-skip-permissions"
    ok "${agent_name}: Claude CLI launched in $pane"
  fi
}

launch_claude "$AGENT1_PANE" "$AGENT1_NAME"
launch_claude "$AGENT2_PANE" "$AGENT2_NAME"
sleep 5
echo ""

# ============================================================
# Phase 6: Watcher起動
# ============================================================
log "Phase 6: Watcher起動"

# Kill existing watchers
pkill -f "inbox_watcher.sh ${AGENT1_ID}" 2>/dev/null || true
pkill -f "inbox_watcher.sh ${AGENT2_ID}" 2>/dev/null || true
pkill -f "hakudokai_secondpc_receiver" 2>/dev/null || true
sleep 1

# Start inbox_watcher for each agent
start_inbox_watcher() {
  local agent_id="$1"
  local pane="$2"
  local log_file="/tmp/inbox_watcher_${agent_id}.log"

  nohup bash "${SCRIPT_DIR}/scripts/inbox_watcher.sh" "$agent_id" "$pane" claude \
    >> "$log_file" 2>&1 </dev/null &
  sleep 2

  if pgrep -f "inbox_watcher.sh ${agent_id}" > /dev/null 2>&1; then
    ok "inbox_watcher[${agent_id}]: PID=$(pgrep -f "inbox_watcher.sh ${agent_id}" | head -1)"
  else
    ng "inbox_watcher[${agent_id}]: FAILED (check $log_file)"
  fi
}

start_inbox_watcher "$AGENT1_ID" "$AGENT1_PANE"
start_inbox_watcher "$AGENT2_ID" "$AGENT2_PANE"

# Start Supabase bridge receiver (v2: separate script with anti-duplicate + safe nudge)
RECEIVER_LOG="/tmp/hakudokai_secondpc_receiver.log"
pkill -f "hakudokai_secondpc_receiver" 2>/dev/null || true
sleep 1

nohup bash "${SCRIPT_DIR}/shim/hakudokai/hakudokai_secondpc_receiver.sh" --interval 5 \
  >> "$RECEIVER_LOG" 2>&1 </dev/null &
sleep 2

if pgrep -f "hakudokai_secondpc_receiver" > /dev/null 2>&1; then
  ok "Supabase bridge receiver v2: PID=$(pgrep -f 'hakudokai_secondpc_receiver' | head -1)"
else
  warn "Supabase bridge receiver: check $RECEIVER_LOG"
fi

# Start reports_sync (SecondPC → MainPC reverse file sync)
# SR2 fix: use pidfile instead of broad pkill -f
REPORTS_SYNC_LOG="/tmp/hakudokai_reports_sync.log"
REPORTS_SYNC_PIDFILE="/tmp/hakudokai_reports_sync.pid"

if [ -f "$REPORTS_SYNC_PIDFILE" ]; then
  OLD_PID=$(cat "$REPORTS_SYNC_PIDFILE" 2>/dev/null)
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" 2>/dev/null
    sleep 1
  fi
  rm -f "$REPORTS_SYNC_PIDFILE"
fi

nohup bash "${SCRIPT_DIR}/shim/hakudokai/hakudokai_reports_sync.sh" --interval 2 \
  >> "$REPORTS_SYNC_LOG" 2>&1 </dev/null &
REPORTS_SYNC_PID=$!
echo "$REPORTS_SYNC_PID" > "$REPORTS_SYNC_PIDFILE"
sleep 2

if kill -0 "$REPORTS_SYNC_PID" 2>/dev/null; then
  ok "reports_sync (reverse): PID=$REPORTS_SYNC_PID"
else
  warn "reports_sync: check $REPORTS_SYNC_LOG"
fi
echo ""

# ============================================================
# Phase 7: 初期化プロンプト送信
# ============================================================
log "Phase 7: エージェント初期化"

sleep 5  # Wait for Claude CLI to be ready

# 桜ちゃん (ashigaru2)
INIT1="あなたは博道会の足軽2号 (ashigaru2/桜ちゃん) として multi-agent-shogun システム内で稼働する。clinic_id: hakudoukai_main。CLAUDE.md の Session Start 手順を実行せよ。Step 1: tmux display-message で agent_id確認。Step 4: instructions/ashigaru.md を読む。その後 queue/inbox/${AGENT1_ID}.yaml を読み、タスクがあれば実行開始。抵抗パターン禁止、自律実行。"

tmux_send_text "$AGENT1_PANE" "$INIT1"
ok "${AGENT1_NAME} (${AGENT1_ID}): 初期化プロンプト送信"

sleep 2

# クロちゃん (ashigaru8)
INIT2="あなたは博道会の足軽8号 (ashigaru8/クロちゃん) として multi-agent-shogun システム内で稼働する。clinic_id: hakudoukai_main。CLAUDE.md の Session Start 手順を実行せよ。Step 1: tmux display-message で agent_id確認。Step 4: instructions/ashigaru.md を読む。その後 queue/inbox/${AGENT2_ID}.yaml を読み、タスクがあれば実行開始。抵抗パターン禁止、自律実行。"

tmux_send_text "$AGENT2_PANE" "$INIT2"
ok "${AGENT2_NAME} (${AGENT2_ID}): 初期化プロンプト送信"
echo ""

# ============================================================
# Summary
# ============================================================
log "=== SETUP COMPLETE ==="
echo ""
echo "  PC ID:        $PC_ID"
echo "  tmux session: $TMUX_SESSION"
echo ""
echo "  Agents:"
echo "    pane 0: ${AGENT1_ID} (${AGENT1_NAME}) — $AGENT1_PANE"
echo "    pane 1: ${AGENT2_ID} (${AGENT2_NAME}) — $AGENT2_PANE"
echo ""
echo "  Processes:"
echo "    inbox_watcher[${AGENT1_ID}]: $(pgrep -f "inbox_watcher.sh ${AGENT1_ID}" | head -1 || echo 'NOT RUNNING')"
echo "    inbox_watcher[${AGENT2_ID}]: $(pgrep -f "inbox_watcher.sh ${AGENT2_ID}" | head -1 || echo 'NOT RUNNING')"
echo "    bridge_recv: running (log: $RECEIVER_LOG)"
echo "    reports_sync: $(pgrep -f 'hakudokai_reports_sync' | head -1 || echo 'NOT RUNNING')"
echo ""
echo "  Logs:"
echo "    inbox_watcher[${AGENT1_ID}]: /tmp/inbox_watcher_${AGENT1_ID}.log"
echo "    inbox_watcher[${AGENT2_ID}]: /tmp/inbox_watcher_${AGENT2_ID}.log"
echo "    bridge_recv: $RECEIVER_LOG"
echo "    reports_sync: $REPORTS_SYNC_LOG"
echo ""
echo "  To check status:"
echo "    tmux attach -t $TMUX_SESSION"
echo "    tail -f $RECEIVER_LOG"
echo ""
echo "  To stop:"
echo "    pkill -f 'inbox_watcher.sh ${AGENT1_ID}'"
echo "    pkill -f 'inbox_watcher.sh ${AGENT2_ID}'"
echo "    tmux kill-session -t $TMUX_SESSION"
echo ""
log "${GREEN}${AGENT1_NAME} (${AGENT1_ID}) + ${AGENT2_NAME} (${AGENT2_ID}) are ready on SecondPC.${NC}"
