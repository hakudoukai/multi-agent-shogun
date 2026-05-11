#!/usr/bin/env bash
# auto_git_sync.sh — 両PC ↔ origin の git 自動 pull (= pull-only mode)
# 信長 (shogun) 直接装備、2026-05-11、F007 遵守改修版
#
# 設計原則:
#   - F007 遵守 = git push は agent workflow + 陛下御差配が trust gate (= auto-push 禁)
#   - drift 構造防止 = fast-forward pull のみ auto 化、remote 先行を即取り込み
#   - 不整合起きない = divergent 検出時 HALT、auto-merge 厳禁
#   - 効率的 = 5min interval、flock 排他
#   - 安定 = bounded retry、両 PC 対称
#
# 動作:
#   1. flock で二重起動禁
#   2. PC_ID + remote 自動判定 (= MC=newbuild、SC=origin)
#   3. git fetch
#   4. fast-forward 可能なら pull、divergent なら HALT + notify (= 人間介入 trigger)
#   5. local change 検出のみ (= warn log、commit/push は手動規範)
#   6. log + 連続 HALT 3 回で shogun escalation
#
# 旧版で実装していた auto-commit + auto-push は F007 違反ゆえ削除。
# commit + push は ashigaru workflow + F007 (陛下御差配) 規範下で別途実行。

set -uo pipefail

# === Constants ===
REPO_ROOT="$HOME/projects/multi-agent-shogun-newbuild"
LOG_FILE="$REPO_ROOT/queue/reports/auto_sync_log.yaml"
HALT_COUNTER_FILE="$REPO_ROOT/queue/reports/.auto_sync_halt_counter"
LOCK_FILE="/run/user/$(id -u)/auto_git_sync.lock"
NOTIFY_SCRIPT="$REPO_ROOT/scripts/inbox_write.sh"
BRANCH="${AUTO_GIT_SYNC_BRANCH:-main}"
CONSECUTIVE_HALT_ESCALATION=3

# === PC_ID 自動判定 ===
if [ -z "${PC_ID:-}" ]; then
  case "$(hostname)" in
    USER-0T4SR8MIQA) PC_ID=main_pc ;;
    USER-O6AK917NTU) PC_ID=second_pc ;;
    *) PC_ID="unknown_$(hostname)" ;;
  esac
fi

# === Remote 名自動判定 (= MC は newbuild、SC は origin) ===
if [ -z "${AUTO_GIT_SYNC_REMOTE:-}" ]; then
  case "$PC_ID" in
    main_pc)   REMOTE_NAME="newbuild" ;;
    second_pc) REMOTE_NAME="origin" ;;
    *)         REMOTE_NAME="origin" ;;
  esac
else
  REMOTE_NAME="$AUTO_GIT_SYNC_REMOTE"
fi

# === Options ===
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --help|-h)
      cat <<EOF
Usage: $0 [--dry-run]

Auto-pulls FF-only from <PC>'s remote into local main.
NEVER commits or pushes (= F007 遵守).

Environment:
  AUTO_GIT_SYNC_REMOTE  (default: PC_ID 依存、MC=newbuild、SC=origin)
  AUTO_GIT_SYNC_BRANCH  (default: main)
  PC_ID                 (auto-detected from hostname)
EOF
      exit 0
      ;;
  esac
done

# === Functions ===
ts_now() { date -Iseconds; }

log_event() {
  local op="$1" reason="${2:-}" extra="${3:-}"
  if [ ! -f "$LOG_FILE" ]; then
    mkdir -p "$(dirname "$LOG_FILE")"
    printf 'generated_at: "%s"\nevents: []\n' "$(ts_now)" > "$LOG_FILE"
  fi
  {
    flock -x 200
    if grep -q '^events: \[\]' "$LOG_FILE"; then
      sed -i 's|^events: \[\]|events:|' "$LOG_FILE"
    fi
    cat >> "$LOG_FILE" <<YAML
  - ts: "$(ts_now)"
    pc_id: "$PC_ID"
    operation: "$op"
    halt_reason: "$reason"
    extra: "$extra"
YAML
  } 200>"${LOG_FILE}.lock"
}

bump_halt_counter() {
  local count=0
  if [ -f "$HALT_COUNTER_FILE" ]; then
    count=$(cat "$HALT_COUNTER_FILE" 2>/dev/null || echo 0)
  fi
  count=$((count + 1))
  echo "$count" > "$HALT_COUNTER_FILE"
  echo "$count"
}

reset_halt_counter() {
  echo 0 > "$HALT_COUNTER_FILE"
}

notify_karo() {
  local reason="$1"
  if [ -x "$NOTIFY_SCRIPT" ]; then
    bash "$NOTIFY_SCRIPT" karo "auto_git_sync HALT ($PC_ID): $reason" status_update auto_git_sync 2>&1 | head -3 || true
  fi
}

notify_shogun_escalation() {
  local reason="$1" halt_count="$2"
  if [ -x "$NOTIFY_SCRIPT" ]; then
    bash "$NOTIFY_SCRIPT" shogun "auto_git_sync ESCALATION ($PC_ID): ${halt_count} consecutive HALTs. Last reason: $reason" status_update auto_git_sync 2>&1 | head -3 || true
  fi
}

halt() {
  local reason="$1"
  log_event "halt" "$reason"
  notify_karo "$reason"
  local halt_count
  halt_count=$(bump_halt_counter)
  if [ "$halt_count" -ge "$CONSECUTIVE_HALT_ESCALATION" ]; then
    notify_shogun_escalation "$reason" "$halt_count"
  fi
  echo "[$(ts_now)] HALT: $reason (consecutive=${halt_count})" >&2
  exit 1
}

# === Lock (二重起動禁) ===
mkdir -p "$(dirname "$LOCK_FILE")"
exec 9>"$LOCK_FILE" || { echo "FATAL: lock open failed" >&2; exit 1; }
flock -n 9 || { echo "[$(ts_now)] SKIPPED: lock held by another instance" >&2; exit 0; }

# === Step 1: Preflight ===
cd "$REPO_ROOT" || halt "repo_root_not_found"

if [ $DRY_RUN -eq 1 ]; then echo "[DRY_RUN] cd $REPO_ROOT (remote=$REMOTE_NAME)"; fi

# === Step 2: Fetch ===
if [ $DRY_RUN -eq 1 ]; then
  echo "[DRY_RUN] would: git fetch $REMOTE_NAME $BRANCH"
else
  git fetch "$REMOTE_NAME" "$BRANCH" >/dev/null 2>&1 || halt "fetch_failed"
fi

# === Step 3: FF Pull or HALT on divergent ===
local_head=$(git rev-parse HEAD 2>/dev/null || echo "")
remote_head=$(git rev-parse "$REMOTE_NAME/$BRANCH" 2>/dev/null || echo "")

if [ -z "$local_head" ] || [ -z "$remote_head" ]; then
  halt "missing_head local=${local_head:-empty} remote=${remote_head:-empty}"
fi

pulled_count=0
status="up_to_date"

if [ "$local_head" != "$remote_head" ]; then
  if git merge-base --is-ancestor "$local_head" "$remote_head" 2>/dev/null; then
    # FF pull 可能
    pulled_count=$(git rev-list --count "${local_head}..${remote_head}" 2>/dev/null || echo 0)
    if [ $DRY_RUN -eq 1 ]; then
      echo "[DRY_RUN] would: git pull --ff-only $REMOTE_NAME $BRANCH (would fetch $pulled_count commits)"
      status="dry_run_ff_pull"
    else
      # working tree dirty なら stash → pull → stash pop (safe)
      dirty_count=$(git status --porcelain 2>/dev/null | wc -l)
      stashed=0
      if [ "$dirty_count" -gt 0 ]; then
        if git stash push -u -m "auto_git_sync_stash_$(ts_now)" >/dev/null 2>&1; then
          stashed=1
        else
          halt "stash_failed_${dirty_count}files"
        fi
      fi
      if git pull --ff-only "$REMOTE_NAME" "$BRANCH" >/dev/null 2>&1; then
        status="ff_pulled"
      else
        # rollback stash
        if [ $stashed -eq 1 ]; then git stash pop >/dev/null 2>&1 || true; fi
        halt "ff_pull_failed"
      fi
      if [ $stashed -eq 1 ]; then
        git stash pop >/dev/null 2>&1 || halt "stash_pop_failed"
      fi
    fi
  elif git merge-base --is-ancestor "$remote_head" "$local_head" 2>/dev/null; then
    # local ahead = agent workflow で push 待ち (= F007 規範下手動 push 期待)
    status="local_ahead_awaiting_manual_push"
  else
    # divergent
    halt "non_ff_divergent local=${local_head:0:8} remote=${remote_head:0:8}"
  fi
fi

# === Step 4: Local change 検出 (= 情報 only、commit/push せず) ===
dirty_count=$(git status --porcelain 2>/dev/null | wc -l)

# === Step 5: Success log + reset halt counter (= dry-run 時は触らず) ===
if [ $DRY_RUN -eq 0 ]; then
  log_event "pull_cycle" "" "status=${status} pulled=${pulled_count} local_dirty=${dirty_count}"
  reset_halt_counter
fi

if [ $DRY_RUN -eq 1 ]; then
  echo "[DRY_RUN] complete. status=$status pulled=$pulled_count local_dirty=$dirty_count"
fi

exit 0
