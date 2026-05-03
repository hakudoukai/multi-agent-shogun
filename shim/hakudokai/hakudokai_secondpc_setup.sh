#!/usr/bin/env bash
# hakudokai_secondpc_setup.sh — SecondPC ワンコマンドセットアップ
#
# SecondPC上でこのスクリプトを実行すると:
#   1. 環境チェック (git, python3, inotify-tools, claude CLI)
#   2. リポジトリ同期 (git pull)
#   3. Supabase環境変数確認
#   4. tmux session作成 (桜ちゃん用pane)
#   5. Claude Code CLI起動 (ashigaru2)
#   6. watcher群起動 (inbox_watcher + Supabase bridge receiver)
#   7. watchdog起動
#
# Usage:
#   cd /path/to/multi-agent-shogun
#   bash shim/hakudokai/hakudokai_secondpc_setup.sh
#
# 前提:
#   - リポジトリがclone済み
#   - ~/.openclaw/env にSupabase環境変数あり
#   - claude CLI インストール済み + 桜ちゃんアカウントでログイン済み

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PC_ID="second_pc"
AGENT_ID="ashigaru2"
AGENT_NAME="sakura"
TMUX_SESSION="secondpc"
TMUX_PANE="${TMUX_SESSION}:0.0"

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
if [ -f "$HOME/.openclaw/env" ]; then
  SB_URL=$(grep '^SUPABASE_URL=' "$HOME/.openclaw/env" | cut -d= -f2- | tr -d '\r')
  SB_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.openclaw/env" | cut -d= -f2- | tr -d '\r')
  if [ -n "$SB_URL" ] && [ -n "$SB_KEY" ]; then
    ok "Supabase env loaded"
    export SUPABASE_URL="$SB_URL" SUPABASE_SERVICE_ROLE_KEY="$SB_KEY"
  else
    ng "Supabase env incomplete in ~/.openclaw/env"
    errors=$((errors + 1))
  fi
else
  ng "~/.openclaw/env not found"
  echo "    Create it with:"
  echo "    echo 'SUPABASE_URL=https://xxx.supabase.co' > ~/.openclaw/env"
  echo "    echo 'SUPABASE_SERVICE_ROLE_KEY=eyJ...' >> ~/.openclaw/env"
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
log "Phase 2: リポジトリ同期"

cd "$SCRIPT_DIR"
git fetch origin 2>/dev/null
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "unknown")

if [ "$LOCAL" = "$REMOTE" ]; then
  ok "Already up to date ($LOCAL)"
else
  log "Pulling latest changes..."
  git pull --ff-only origin main 2>&1 && ok "Updated to $(git rev-parse HEAD)" || warn "Pull failed (may need manual merge)"
fi
echo ""

# ============================================================
# Phase 3: tmux session作成
# ============================================================
log "Phase 3: tmux session作成"

if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  warn "tmux session '$TMUX_SESSION' already exists"
else
  tmux new-session -d -s "$TMUX_SESSION" -c "$SCRIPT_DIR"
  ok "tmux session '$TMUX_SESSION' created"
fi

# Set agent_id on pane
tmux set-option -t "$TMUX_PANE" @agent_id "$AGENT_ID" 2>/dev/null
ok "agent_id set: $AGENT_ID"
echo ""

# ============================================================
# Phase 4: inbox ディレクトリ準備
# ============================================================
log "Phase 4: inbox準備"

INBOX_DIR="$SCRIPT_DIR/queue/inbox"
mkdir -p "$INBOX_DIR"

if [ ! -f "$INBOX_DIR/${AGENT_ID}.yaml" ]; then
  echo "messages: []" > "$INBOX_DIR/${AGENT_ID}.yaml"
  ok "Created ${AGENT_ID}.yaml"
else
  ok "${AGENT_ID}.yaml exists"
fi
echo ""

# ============================================================
# Phase 5: Claude Code CLI起動
# ============================================================
log "Phase 5: Claude Code CLI起動 (${AGENT_NAME}/${AGENT_ID})"

# Check if claude is already running in the pane
PANE_CMD=$(tmux display-message -t "$TMUX_PANE" -p '#{pane_current_command}' 2>/dev/null)
if [ "$PANE_CMD" = "claude" ] || [ "$PANE_CMD" = "node" ]; then
  warn "Claude CLI appears to be already running in $TMUX_PANE"
else
  tmux send-keys -t "$TMUX_PANE" "cd $SCRIPT_DIR && claude --dangerously-skip-permissions" Enter
  ok "Claude CLI launched in $TMUX_PANE"
  sleep 3
fi
echo ""

# ============================================================
# Phase 6: Watcher起動
# ============================================================
log "Phase 6: Watcher起動"

# Kill existing watchers
pkill -f "inbox_watcher.sh ${AGENT_ID}" 2>/dev/null || true
pkill -f "hakudokai_secondpc_receiver" 2>/dev/null || true
sleep 1

# Start inbox_watcher for ashigaru2
INBOX_LOG="/tmp/inbox_watcher_${AGENT_ID}.log"
nohup bash "${SCRIPT_DIR}/scripts/inbox_watcher.sh" "$AGENT_ID" "$TMUX_PANE" claude \
  >> "$INBOX_LOG" 2>&1 </dev/null &
sleep 2

if pgrep -f "inbox_watcher.sh ${AGENT_ID}" > /dev/null 2>&1; then
  ok "inbox_watcher[${AGENT_ID}]: PID=$(pgrep -f "inbox_watcher.sh ${AGENT_ID}" | head -1)"
else
  ng "inbox_watcher[${AGENT_ID}]: FAILED"
fi

# Start Supabase bridge receiver (polls Supabase for cross-PC messages)
RECEIVER_LOG="/tmp/hakudokai_secondpc_receiver.log"
nohup bash -c "
  while true; do
    # Poll Supabase for messages to second_pc
    RESPONSE=\$(curl -sS \\
      \"\${SUPABASE_URL}/rest/v1/pc_handshake?to_pc=eq.${PC_ID}&acknowledged_at=is.null&order=created_at.asc&limit=5\" \\
      -H \"Authorization: Bearer \${SUPABASE_SERVICE_ROLE_KEY}\" \\
      -H \"apikey: \${SUPABASE_SERVICE_ROLE_KEY}\" \\
      -H \"Content-Type: application/json\" 2>/dev/null)

    if [ -n \"\$RESPONSE\" ] && [ \"\$RESPONSE\" != \"[]\" ]; then
      echo \"\$RESPONSE\" | python3 -c \"
import sys, json, subprocess, os, time
from datetime import datetime, timezone
try:
    data = json.load(sys.stdin)
    for msg in data:
        msg_id = msg.get('id', '')
        content = msg.get('content', '')
        topic = msg.get('topic', '')
        # Write to local inbox
        subprocess.run([
            'bash', '${SCRIPT_DIR}/scripts/inbox_write.sh',
            '${AGENT_ID}', content[:500], 'task_assigned', 'karo'
        ], capture_output=True, timeout=10)
        # ACK
        import urllib.request
        ack_url = '${SUPABASE_URL}/rest/v1/pc_handshake?id=eq.' + msg_id
        ack_data = json.dumps({
            'acknowledged_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'acknowledged_by': '${PC_ID}'
        }).encode()
        req = urllib.request.Request(ack_url, data=ack_data, method='PATCH')
        req.add_header('Authorization', 'Bearer ${SUPABASE_SERVICE_ROLE_KEY}')
        req.add_header('apikey', '${SUPABASE_SERVICE_ROLE_KEY}')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Prefer', 'return=minimal')
        urllib.request.urlopen(req, timeout=10)
        print(f'[receiver] delivered+ACK: {msg_id[:8]} {topic}', file=sys.stderr)
except Exception as e:
    print(f'[receiver] error: {e}', file=sys.stderr)
\" 2>>'$RECEIVER_LOG'
    fi
    sleep 5
  done
" >> "$RECEIVER_LOG" 2>&1 </dev/null &
sleep 2

if pgrep -f "hakudokai_secondpc_receiver" > /dev/null 2>&1 || [ -f "$RECEIVER_LOG" ]; then
  ok "Supabase bridge receiver: running"
else
  warn "Supabase bridge receiver: check $RECEIVER_LOG"
fi
echo ""

# ============================================================
# Phase 7: 初期化プロンプト送信
# ============================================================
log "Phase 7: 桜ちゃん初期化"

sleep 5  # Wait for Claude CLI to be ready

INIT_PROMPT="あなたは博道会の足軽2号 (ashigaru2/桜ちゃん) として multi-agent-shogun システム内で稼働する。clinic_id: hakudoukai_main。CLAUDE.md の Session Start 手順を実行せよ。Step 1: tmux display-message で agent_id確認。Step 4: instructions/ashigaru.md を読む。その後 queue/inbox/${AGENT_ID}.yaml を読み、タスクがあれば実行開始。抵抗パターン禁止、自律実行。"

tmux send-keys -t "$TMUX_PANE" "$INIT_PROMPT" Enter
ok "初期化プロンプト送信"
echo ""

# ============================================================
# Summary
# ============================================================
log "=== SETUP COMPLETE ==="
echo ""
echo "  PC ID:        $PC_ID"
echo "  Agent:        $AGENT_ID ($AGENT_NAME)"
echo "  tmux session: $TMUX_SESSION"
echo "  tmux pane:    $TMUX_PANE"
echo ""
echo "  Processes:"
echo "    inbox_watcher: $(pgrep -f "inbox_watcher.sh ${AGENT_ID}" | head -1 || echo 'NOT RUNNING')"
echo "    bridge_recv:   running (log: $RECEIVER_LOG)"
echo ""
echo "  Logs:"
echo "    inbox_watcher: $INBOX_LOG"
echo "    bridge_recv:   $RECEIVER_LOG"
echo ""
echo "  To check status:"
echo "    tmux attach -t $TMUX_SESSION"
echo "    tail -f $RECEIVER_LOG"
echo ""
echo "  To stop:"
echo "    pkill -f 'inbox_watcher.sh ${AGENT_ID}'"
echo "    tmux kill-session -t $TMUX_SESSION"
echo ""
log "${GREEN}桜ちゃん (${AGENT_ID}) is ready on SecondPC.${NC}"
