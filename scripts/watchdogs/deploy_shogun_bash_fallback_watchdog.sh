#!/usr/bin/env bash
#
# Deploy — Shogun Bash-Fallback Watchdog (各PC ローカル systemd --user, 60s cycle)
#
# 由来: subtask_thirdpc_shogun_bash_fallback_watchdog (副院長追命 670ffbfe(2))。
# ★各PC (main/second/third) ローカル配備が要 (cross-PC send-keys 依存を断つ)★。
# second_pc 優先。systemd --user timer で 60s 間隔、oneshot service が wrapper を起動。
#
# 使い方:
#   bash scripts/watchdogs/deploy_shogun_bash_fallback_watchdog.sh [main|second|third] [install|uninstall|status]
#   引数省略時: PC は whoami で自動判定、action=install。
#
# 安全: 既存 enter_restart timer とは別 unit (shogun_bash_fallback.*) ゆえ非干渉。
#       手動停止は `touch ~/.local/share/shogun_bash_fallback_<role>/DISABLE` または
#       `systemctl --user stop shogun_bash_fallback.timer`。

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/../.." && pwd)"
WATCHDOGS_DIR="$REPO_DIR/scripts/watchdogs"

PC="${1:-auto}"
ACTION="${2:-install}"

if [ "$PC" = "auto" ]; then
  case "$(whoami)" in
    hakudoukai) PC=third ;;
    hakudokai)  PC=second ;;
    user)       PC=main ;;
    *)          echo "ERROR: PC を自動判定できず (whoami=$(whoami))。引数で main|second|third を明示せよ。" >&2; exit 2 ;;
  esac
  echo "[deploy] PC auto-detected: $PC (whoami=$(whoami))"
fi

case "$PC" in
  main)   WRAPPER="$WATCHDOGS_DIR/shogun_bash_fallback_main_watchdog.sh" ;;
  second) WRAPPER="$WATCHDOGS_DIR/shogun_bash_fallback_second_watchdog.sh" ;;
  third)  WRAPPER="$WATCHDOGS_DIR/shogun_bash_fallback_third_watchdog.sh" ;;
  *) echo "ERROR: PC は main|second|third のいずれか (got: $PC)" >&2; exit 2 ;;
esac

if [ ! -x "$WRAPPER" ]; then
  echo "ERROR: wrapper not found or not executable: $WRAPPER" >&2; exit 2
fi

UNIT_DIR="$HOME/.config/systemd/user"
SVC="shogun_bash_fallback.service"
TMR="shogun_bash_fallback.timer"
LOG_DIR="$HOME/.local/share/shogun_bash_fallback_shogun_${PC}"

uninstall() {
  echo "[deploy] uninstalling $TMR / $SVC ..."
  systemctl --user disable --now "$TMR" 2>/dev/null || true
  rm -f "$UNIT_DIR/$SVC" "$UNIT_DIR/$TMR"
  systemctl --user daemon-reload 2>/dev/null || true
  echo "[deploy] uninstalled."
}

status() {
  echo "=== timer ==="; systemctl --user status "$TMR" --no-pager 2>/dev/null | head -12 || true
  echo "=== last service run ==="; systemctl --user status "$SVC" --no-pager 2>/dev/null | head -15 || true
  echo "=== log dir ($LOG_DIR) ==="; ls -la "$LOG_DIR" 2>/dev/null || echo "(no logs yet)"
}

install() {
  if ! command -v systemctl >/dev/null 2>&1; then
    echo "ERROR: systemctl 不在。systemd --user 不可な環境では cron/常駐ループ等の代替が必要。" >&2
    exit 3
  fi
  mkdir -p "$UNIT_DIR" "$LOG_DIR"

  cat > "$UNIT_DIR/$SVC" <<EOF
[Unit]
Description=Shogun Bash-Fallback / Stuck-Retry Watchdog ($PC, 60s cycle) — relaunch crashed/stuck Claude with doppler env
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=%h
ExecStartPre=/bin/mkdir -p $LOG_DIR
ExecStart=/bin/bash $WRAPPER
StandardOutput=append:$LOG_DIR/service.log
StandardError=append:$LOG_DIR/service.err
EOF

  cat > "$UNIT_DIR/$TMR" <<EOF
[Unit]
Description=Shogun Bash-Fallback Watchdog — 60s cycle ($PC local)
Requires=$SVC

[Timer]
OnBootSec=90s
OnUnitActiveSec=60s
AccuracySec=10s
Unit=$SVC

[Install]
WantedBy=timers.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable --now "$TMR"
  echo "[deploy] installed + enabled $TMR (PC=$PC, wrapper=$WRAPPER, cadence=60s)"
  echo "[deploy] disable: systemctl --user stop $TMR  /  touch $LOG_DIR/DISABLE"
  systemctl --user list-timers "$TMR" --no-pager 2>/dev/null | head -4 || true
}

case "$ACTION" in
  install)   install ;;
  uninstall) uninstall ;;
  status)    status ;;
  *) echo "ERROR: action は install|uninstall|status (got: $ACTION)" >&2; exit 2 ;;
esac
