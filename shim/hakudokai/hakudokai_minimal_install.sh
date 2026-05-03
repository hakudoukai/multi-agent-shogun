#!/usr/bin/env bash
# hakudokai_minimal_install.sh — 博道会 shogun-base minimal patch installer
#
# 両 PC 共通 (main_pc / second_pc)、WSL2 Ubuntu 22.04+ / git-bash 想定。
# shogun (yohey-w v4.6.0) first_setup.sh の minimal 版 (tmux 廃止、Supabase 追加)。
#
# Usage:
#   bash scripts/hakudokai_minimal_install.sh --role kouchan
#   bash scripts/hakudokai_minimal_install.sh --role sakura --idle-dir /tmp
#
# 処理:
#   1. python3 / pip / supabase-py install
#   2. ~/.openclaw/role.json 作成 (role 設定)
#   3. ~/.openclaw/disable_auto_continue_${ROLE} 不在確認 (有効化)
#   4. ~/.openclaw/global_disable 不在確認
#   5. .claude/hooks/stop_hook_inbox.sh 配置 (実行権限付与)
#   6. .claude/settings.json snippet 提示 (手動マージ案内)
#   7. 動作テスト (--once で notify を試行)
#
# Reference: shogun upstream commit 20af6b53, first_setup.sh (42KB → 100行に圧縮)
# License: MIT

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ROLE=""
IDLE_DIR="/tmp"
SKIP_PIP=0
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --role)        ROLE="$2"; shift 2;;
    --idle-dir)    IDLE_DIR="$2"; shift 2;;
    --skip-pip)    SKIP_PIP=1; shift;;
    --dry-run)     DRY_RUN=1; shift;;
    -h|--help)
      sed -n '2,30p' "$0"
      exit 0;;
    *)
      echo "[install] unknown arg: $1" >&2
      exit 2;;
  esac
done

if [ -z "$ROLE" ]; then
  echo "[install] --role <fukuincho|kuro|yama|sakura|kouchan> required" >&2
  exit 2
fi

case "$ROLE" in
  fukuincho|yama|kuro|sakura|kouchan) ;;
  *)
    echo "[install] invalid role '$ROLE'" >&2
    exit 2;;
esac

echo "[install] role=$ROLE idle_dir=$IDLE_DIR repo_root=$REPO_ROOT dry_run=$DRY_RUN"

# 1. python3 + pip + supabase-py
if [ "$SKIP_PIP" -eq 0 ]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "[install] python3 not found. install: sudo apt install python3 python3-pip" >&2
    exit 3
  fi
  if [ "$DRY_RUN" -eq 0 ]; then
    # Codex audit fix #4: pip 失敗を致命的エラーとして扱う (silent skip しない)
    if ! python3 -m pip install --quiet --user --upgrade "supabase>=2.0.0" 2>&1 | tail -3; then
      echo "[install] FATAL: pip install failed." >&2
      echo "[install] hint: pip install --break-system-packages 'supabase>=2.0.0' (PEP 668 envs)" >&2
      exit 4
    fi
  else
    echo "[install] (dry-run) would: python3 -m pip install --user 'supabase>=2.0.0'"
  fi
else
  echo "[install] --skip-pip given, skipping pip install"
fi

# 2. ~/.openclaw/role.json
mkdir -p "$HOME/.openclaw"
ROLE_JSON="$HOME/.openclaw/role.json"
if [ "$DRY_RUN" -eq 0 ]; then
  cat > "$ROLE_JSON" <<JSON
{
  "role": "$ROLE",
  "idle_flag_dir": "$IDLE_DIR",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "shogun_version": "v4.6.0",
  "minimal_patch_version": "v0.1"
}
JSON
  chmod 600 "$ROLE_JSON"
  echo "[install] wrote $ROLE_JSON"
else
  echo "[install] (dry-run) would write $ROLE_JSON with role=$ROLE"
fi

# 3-4. disable flag precheck (warn if exists)
for FLAG in "$HOME/.openclaw/global_disable" "$HOME/.openclaw/disable_auto_continue_${ROLE}"; do
  if [ -f "$FLAG" ]; then
    echo "[install] WARN disable flag exists: $FLAG (Stop Hook will exit early)"
  fi
done

# 5. stop hook 配置 (chmod +x)
HOOK_SRC="$REPO_ROOT/.claude/hooks/stop_hook_inbox.sh"
if [ -f "$HOOK_SRC" ]; then
  chmod +x "$HOOK_SRC"
  echo "[install] stop_hook_inbox.sh executable: $HOOK_SRC"
else
  echo "[install] WARN $HOOK_SRC missing"
fi

# 6. settings.json snippet (手動マージ)
SNIPPET=$(cat <<'JSON'
{
  "env": {
    "HAKUDOKAI_ROLE": "<role>",
    "IDLE_FLAG_DIR": "/tmp"
  },
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "<repo_root>/.claude/hooks/stop_hook_inbox.sh" }
        ]
      }
    ]
  }
}
JSON
)
echo ""
echo "[install] === .claude/settings.json snippet (手動マージ案内) ==="
echo "$SNIPPET" | sed "s|<role>|$ROLE|g" | sed "s|<repo_root>|$REPO_ROOT|g"
echo ""

# 7. 動作テスト (require SUPABASE_URL/KEY)
if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-${SUPABASE_KEY:-}}" ]; then
  echo "[install] running watcher --once (smoke test)"
  HAKUDOKAI_ROLE="$ROLE" python3 "$REPO_ROOT/scripts/hakudokai_inbox_watcher.py" --once --quiet \
    || echo "[install] watcher smoke test exited non-zero (acceptable if no unread)"
else
  echo "[install] skipping smoke test (SUPABASE_URL / KEY not set)"
fi

echo ""
echo "[install] DONE. Next:"
echo "  - Merge the settings.json snippet into ~/.claude/settings.json (or project local)"
echo "  - Verify ~/.openclaw/role.json"
echo "  - Run: HAKUDOKAI_ROLE=$ROLE python3 $REPO_ROOT/scripts/hakudokai_inbox_watcher.py --once"
echo "  - 緊急停止 flag: touch ~/.openclaw/disable_auto_continue_${ROLE}"
