#!/usr/bin/env bash
#
# Deploy — Shogun Bash-Fallback Watchdog (各PC ローカル systemd --user, 60s cycle)
#
# 由来: subtask_thirdpc_shogun_bash_fallback_watchdog (副院長追命 670ffbfe(2))。
# ★各PC (main/second/third) ローカル配備が要 (cross-PC send-keys 依存を断つ)★。
# second_pc 優先。systemd --user timer で 60s 間隔、oneshot service が wrapper を起動。
#
# 使い方:
#   bash scripts/watchdogs/deploy_shogun_bash_fallback_watchdog.sh [main|second|third] [install|uninstall|status|verify]
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

# cycle6 MED T1: 生成した systemd unit 内容を install 直後に検証 (沈黙投入で壊れた unit を残さない)。
# ① service が本 PC の wrapper を正しく指すか ② oneshot か ③ timer が 60s cadence で service を起動するか
# を grep で確認し、可能なら systemd-analyze --user verify で構文検証する。1 つでも欠落で exit 4。
verify_unit() {
  local svc_path="$UNIT_DIR/$SVC" tmr_path="$UNIT_DIR/$TMR" fail=0
  echo "[deploy] verify: systemd unit 内容を検証 ..."
  if [ ! -f "$svc_path" ]; then echo "  NG: service unit 不在: $svc_path" >&2; fail=1; fi
  if [ ! -f "$tmr_path" ]; then echo "  NG: timer unit 不在: $tmr_path" >&2; fail=1; fi
  if [ "$fail" -eq 0 ]; then
    grep -q "^Type=oneshot$"                "$svc_path" || { echo "  NG: service Type=oneshot 欠落" >&2; fail=1; }
    grep -qF "ExecStart=/bin/bash $WRAPPER"  "$svc_path" || { echo "  NG: service ExecStart が wrapper [$WRAPPER] を指さない" >&2; fail=1; }
    grep -q "^OnUnitActiveSec=60s$"          "$tmr_path" || { echo "  NG: timer OnUnitActiveSec=60s 欠落 (60s cadence)" >&2; fail=1; }
    grep -qF "Unit=$SVC"                     "$tmr_path" || { echo "  NG: timer が service [$SVC] を起動しない" >&2; fail=1; }
    grep -qF "Requires=$SVC"                 "$tmr_path" || { echo "  NG: timer Requires=$SVC 欠落" >&2; fail=1; }
  fi
  # 構文検証 (best-effort: systemd-analyze 不在環境では skip するが grep 検証は必達)
  if command -v systemd-analyze >/dev/null 2>&1; then
    if systemd-analyze --user verify "$svc_path" "$tmr_path" 2>&1 | grep -q .; then
      echo "  WARN: systemd-analyze verify が警告を出力 (下記)。grep 検証は別途実施。" >&2
      systemd-analyze --user verify "$svc_path" "$tmr_path" 2>&1 | sed 's/^/    analyze| /' >&2 || true
    else
      echo "  OK: systemd-analyze --user verify 警告なし"
    fi
  else
    echo "  (systemd-analyze 不在 — 構文検証 skip、grep 検証のみ)"
  fi
  if [ "$fail" -ne 0 ]; then
    echo "[deploy] ★unit 検証 FAIL★ — 壊れた unit を投入した。手動確認せよ ($svc_path / $tmr_path)。" >&2
    exit 4
  fi
  echo "[deploy] verify: unit 内容 OK (wrapper=$WRAPPER, cadence=60s, oneshot)"
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

  verify_unit   # cycle6 MED T1: enable 前に unit 内容を検証 (壊れた unit を有効化しない)
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
  verify)    verify_unit ;;
  *) echo "ERROR: action は install|uninstall|status|verify (got: $ACTION)" >&2; exit 2 ;;
esac
