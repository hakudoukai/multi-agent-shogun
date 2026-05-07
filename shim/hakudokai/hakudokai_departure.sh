#!/usr/bin/env bash
# hakudokai_departure.sh — 出陣スクリプト (Phase B-2 task 1)
#
# 両 PC 共通の毎日起動 wrapper。env / role.json / disable flag を確認し、
# inbox_watcher をバックグラウンド起動。最後に動作 verbatim 出力で running 状態を表示。
#
# Usage:
#   bash scripts/hakudokai_departure.sh                  # role.json から自動判定 (--start 相当)
#   bash scripts/hakudokai_departure.sh --start          # 明示起動 (default 同等)
#   bash scripts/hakudokai_departure.sh --role ashigaru1 # role 明示指定 (§18 役名)
#   bash scripts/hakudokai_departure.sh --check          # 起動はせず確認のみ
#   bash scripts/hakudokai_departure.sh --stop           # 既存 watcher を停止
#
# 既稼働中の watcher 検知:
#   - PID file: /tmp/hakudokai_watcher_${ROLE}.pid
#   - 既起動なら起動スキップ (重複防止、race condition 抑止)
#
# 環境変数:
#   HAKUDOKAI_ROLE              role 名 (role.json 優先) — §18 役名
#   HAKUDOKAI_PC_ID             PC 識別子 (notified_by_pc に記録) — main_pc / second_pc
#   HAKUDOKAI_CLINIC_ID         clinic_id (default: hakudoukai_main)
#   SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY  必須
#   HAKUDOKAI_POLL_INTERVAL     polling 間隔秒 (default: 5)
#
# §18 PC×アカウント配置 (理事長殿御指示 2026-05-06):
#   MainPC (sasebo@sasebo.or.jp): shogun / karo / gunshi / ashigaru1 / ashigaru2 + 非常時 ashigaru3
#   SecondPC (hakudoukai@gmail.com): ashigaru5 / ashigaru6 / ashigaru7 + 非常時 ashigaru8
#   ashigaru4 = 欠番 (PC 境界の視覚的区切り)。旧体制名 (fukuincho/yama/kuro/sakura/kouchan) は廃止。
#
# Reference: shogun upstream (yohey-w/multi-agent-shogun v4.6.0, MIT) start.sh パターン
# License: MIT (shogun upstream credit 保持)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ROLE=""
ACTION="start"   # start / check / stop
WATCHER_LOG="/tmp/hakudokai_watcher.log"

while [ $# -gt 0 ]; do
  case "$1" in
    --role)   ROLE="$2"; shift 2;;
    --start)  ACTION="start"; shift;;   # default だが明示指定可
    --check)  ACTION="check"; shift;;
    --stop)   ACTION="stop"; shift;;
    -h|--help) sed -n '2,30p' "$0"; exit 0;;
    *) echo "[departure] unknown arg: $1" >&2; exit 2;;
  esac
done

# role 解決: 引数 > env > role.json
if [ -z "$ROLE" ]; then
  ROLE="${HAKUDOKAI_ROLE:-}"
fi
if [ -z "$ROLE" ] && [ -f "$HOME/.openclaw/role.json" ]; then
  ROLE=$(python3 -c "import json,sys;print(json.load(open('$HOME/.openclaw/role.json')).get('role',''))" 2>/dev/null || true)
fi
if [ -z "$ROLE" ]; then
  echo "[departure] FATAL: role unresolved. specify --role or set HAKUDOKAI_ROLE / ~/.openclaw/role.json" >&2
  exit 3
fi

case "$ROLE" in
  # §18 (理事長殿御指示 2026-05-06) MainPC: shogun/karo/gunshi/ashigaru1-3、SecondPC: ashigaru5-8。
  # ashigaru4 は欠番。旧体制名 (fukuincho/yama/kuro/sakura/kouchan) は §18 移行で廃止。
  shogun|karo|gunshi|ashigaru1|ashigaru2|ashigaru3|ashigaru5|ashigaru6|ashigaru7|ashigaru8) ;;
  *) echo "[departure] FATAL: invalid role '$ROLE' (§18 役名: shogun/karo/gunshi/ashigaru1-3/ashigaru5-8)" >&2; exit 3;;
esac

PID_FILE="/tmp/hakudokai_watcher_${ROLE}.pid"

# --- stop action ---
if [ "$ACTION" = "stop" ]; then
  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
      kill "$PID" && echo "[departure] stopped watcher PID=$PID role=$ROLE"
    else
      echo "[departure] PID file stale, removing"
    fi
    rm -f "$PID_FILE"
  else
    echo "[departure] no watcher PID file for role=$ROLE"
  fi
  exit 0
fi

# --- 必須 env 確認 ---
echo "[departure] === env 確認 ==="
if [ -z "${SUPABASE_URL:-}" ]; then
  echo "[departure] FATAL: SUPABASE_URL missing" >&2
  exit 4
fi
if [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ] && [ -z "${SUPABASE_KEY:-}" ]; then
  echo "[departure] FATAL: SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY) missing" >&2
  exit 4
fi
echo "[departure] role=$ROLE"
echo "[departure] HAKUDOKAI_PC_ID=${HAKUDOKAI_PC_ID:-(unset, will record 'unknown')}"
echo "[departure] HAKUDOKAI_CLINIC_ID=${HAKUDOKAI_CLINIC_ID:-hakudoukai_main}"

# --- role.json 確認 + 自動修復 ---
ROLE_JSON="$HOME/.openclaw/role.json"
if [ ! -f "$ROLE_JSON" ]; then
  echo "[departure] WARN $ROLE_JSON missing → auto-creating via hakudokai_role_init.py"
  python3 "$SCRIPT_DIR/hakudokai_role_init.py" --role "$ROLE"
fi

# --- disable flag 確認 ---
GLOBAL_FLAG="$HOME/.openclaw/global_disable"
ROLE_FLAG="$HOME/.openclaw/disable_auto_continue_${ROLE}"
if [ -f "$GLOBAL_FLAG" ]; then
  echo "[departure] WARN $GLOBAL_FLAG present → Stop Hook 自動継続が無効"
fi
if [ -f "$ROLE_FLAG" ]; then
  echo "[departure] WARN $ROLE_FLAG present → 当該 role のみ自動継続無効"
fi

# --- idle_flag 自動修復 (起動時 idle 状態へ) ---
IDLE_DIR=$(python3 -c "import json;print(json.load(open('$ROLE_JSON')).get('idle_flag_dir','/tmp'))" 2>/dev/null || echo /tmp)
IDLE_FLAG="$IDLE_DIR/hakudokai_idle_${ROLE}"
if [ ! -f "$IDLE_FLAG" ]; then
  touch "$IDLE_FLAG"
  echo "[departure] idle_flag created: $IDLE_FLAG"
fi

# --- check のみで終了 ---
if [ "$ACTION" = "check" ]; then
  if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "[departure] check: watcher RUNNING (PID=$(cat "$PID_FILE"))"
  else
    echo "[departure] check: watcher NOT RUNNING"
  fi
  exit 0
fi

# --- 既起動 watcher 検知 (重複防止) ---
if [ -f "$PID_FILE" ]; then
  EXISTING_PID=$(cat "$PID_FILE")
  if kill -0 "$EXISTING_PID" 2>/dev/null; then
    echo "[departure] watcher already running (PID=$EXISTING_PID), skip start"
    echo "[departure] use --stop to terminate, --check to verify"
    exit 0
  else
    echo "[departure] PID file stale (PID=$EXISTING_PID dead), cleaning"
    rm -f "$PID_FILE"
  fi
fi

# --- inbox_watcher background 起動 ---
WATCHER="$SCRIPT_DIR/hakudokai_inbox_watcher.py"
INTERVAL="${HAKUDOKAI_POLL_INTERVAL:-5}"
echo "[departure] starting inbox_watcher (interval=${INTERVAL}s, log=$WATCHER_LOG)"
HAKUDOKAI_ROLE="$ROLE" nohup python3 "$WATCHER" \
  --interval "$INTERVAL" \
  --max-events 20 \
  --respect-busy \
  > "$WATCHER_LOG" 2>&1 &
WATCHER_PID=$!
echo "$WATCHER_PID" > "$PID_FILE"

sleep 1
if kill -0 "$WATCHER_PID" 2>/dev/null; then
  echo "[departure] OK watcher started PID=$WATCHER_PID role=$ROLE"
  echo "[departure] log: $WATCHER_LOG"
  echo "[departure] stop: bash $0 --stop"
else
  echo "[departure] FATAL: watcher exited immediately, see $WATCHER_LOG" >&2
  rm -f "$PID_FILE"
  exit 5
fi
