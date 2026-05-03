#!/usr/bin/env bash
# hakudokai_audit_scheduler.sh — デコポン+ジェミちゃん定期監査ディスパッチ
#
# Usage:
#   bash hakudokai_audit_scheduler.sh daily    # 日次軽量チェック
#   bash hakudokai_audit_scheduler.sh weekly   # 週次フル監査
#   bash hakudokai_audit_scheduler.sh on-commit # commit hook用 (変更ファイルのみ)
#
# 副医院長(fukuincho)から呼ばれる。結果はdocs/codex_audits/に保存。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUDIT_DIR="${SCRIPT_DIR}/docs/codex_audits"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Auto-source env
if [ -z "${SUPABASE_URL:-}" ] && [ -f "$HOME/.openclaw/env" ]; then
  SUPABASE_URL=$(grep '^SUPABASE_URL=' "$HOME/.openclaw/env" | cut -d= -f2- | tr -d '\r')
  SUPABASE_SERVICE_ROLE_KEY=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.openclaw/env" | cut -d= -f2- | tr -d '\r')
  export SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
fi

mkdir -p "$AUDIT_DIR"

log() {
  echo "[audit_scheduler][$(date '+%H:%M:%S')] $1" >&2
}

notify() {
  local level="$1"
  local summary="$2"
  python3 "${SCRIPT_DIR}/shim/hakudokai/hakudokai_escalation.py" notify \
    --level "$level" --summary "$summary" 2>/dev/null
}

# --- Daily lightweight check ---
run_daily() {
  log "Starting daily check..."
  local report="${AUDIT_DIR}/daily_check_${TIMESTAMP}.txt"
  local issues=0

  {
    echo "=== Daily Audit Check: $(date) ==="
    echo ""

    # 1. Shell script syntax check
    echo "--- Shell syntax check ---"
    for f in "${SCRIPT_DIR}"/shim/hakudokai/*.sh; do
      if ! bash -n "$f" 2>/dev/null; then
        echo "FAIL: $f"
        issues=$((issues + 1))
      fi
    done
    echo "Shell check done."
    echo ""

    # 2. Python syntax check
    echo "--- Python syntax check ---"
    for f in "${SCRIPT_DIR}"/shim/hakudokai/*.py; do
      if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "FAIL: $f"
        issues=$((issues + 1))
      fi
    done
    echo "Python check done."
    echo ""

    # 3. FKI directive validation
    echo "--- FKI validation ---"
    python3 "${SCRIPT_DIR}/shim/hakudokai/hakudokai_resistance_guard.py" validate 2>&1
    echo ""

    # 4. Watcher health check
    echo "--- Watcher health ---"
    for hf in /tmp/hakudokai_*_health.json; do
      if [ -f "$hf" ]; then
        echo "$hf: $(cat "$hf")"
      fi
    done
    echo ""

    # 5. Git unpushed check
    echo "--- Git status ---"
    cd "$SCRIPT_DIR"
    local unpushed
    unpushed=$(git log --oneline origin/main..HEAD 2>/dev/null | wc -l)
    echo "Unpushed commits: $unpushed"
    if [ "$unpushed" -gt 0 ]; then
      git log --oneline origin/main..HEAD 2>/dev/null
      issues=$((issues + 1))
    fi
    echo ""

    echo "=== Summary: ${issues} issue(s) found ==="
  } > "$report" 2>&1

  log "Daily check complete: ${issues} issues. Report: $report"

  if [ "$issues" -gt 0 ]; then
    notify "L3a" "日次チェック: ${issues}件の問題検出 — $report"
  fi
}

# --- Weekly full audit ---
run_weekly() {
  log "Starting weekly full audit..."

  local codex_out="${AUDIT_DIR}/weekly_codex_${TIMESTAMP}.txt"
  local gemini_out="${AUDIT_DIR}/weekly_gemini_${TIMESTAMP}.txt"

  # Get diff since last weekly audit
  local last_audit
  last_audit=$(ls -t "${AUDIT_DIR}"/weekly_codex_*.txt 2>/dev/null | head -1)

  local diff_summary=""
  if [ -n "$last_audit" ]; then
    local last_date
    last_date=$(echo "$last_audit" | grep -oP '\d{8}')
    diff_summary=$(cd "$SCRIPT_DIR" && git log --oneline --since="${last_date:0:4}-${last_date:4:2}-${last_date:6:2}" 2>/dev/null | head -20)
  fi

  # Codex dispatch
  log "Dispatching Codex 6-axis audit..."
  local codex_prompt="Weekly automated audit. Review all files under shim/hakudokai/ for: (1) code quality, (2) watcher reliability, (3) security/deny list completeness, (4) self-improvement loop integrity, (5) multi-tenant isolation, (6) git automation status. Recent changes: ${diff_summary:-none}. Rate each axis GREEN/YELLOW/RED with specific file:line references."

  npx @openai/codex exec -o "$codex_out" --ephemeral "$codex_prompt" 2>/dev/null
  log "Codex audit saved: $codex_out"

  # Gemini dispatch
  log "Dispatching Gemini audit..."
  local gemini_prompt="Weekly automated audit for hakudokai dental clinic system. Focus on: medical data safety, PII handling, Japanese medical regulations compliance, patient consent management, cross-clinic data isolation. Review shim/hakudokai/ files. Recent changes: ${diff_summary:-none}. Rate each area GREEN/YELLOW/RED."

  gemini -p "$gemini_prompt" > "$gemini_out" 2>/dev/null
  log "Gemini audit saved: $gemini_out"

  # Determine overall result
  local has_red=false
  local has_yellow=false
  if grep -qi "RED" "$codex_out" 2>/dev/null || grep -qi "RED" "$gemini_out" 2>/dev/null; then
    has_red=true
  fi
  if grep -qi "YELLOW" "$codex_out" 2>/dev/null || grep -qi "YELLOW" "$gemini_out" 2>/dev/null; then
    has_yellow=true
  fi

  if [ "$has_red" = true ]; then
    notify "L4" "週次監査: RED検出 — 理事長確認要。Codex: $codex_out, Gemini: $gemini_out"
    log "Weekly audit: RED detected. L4 escalation sent."
  elif [ "$has_yellow" = true ]; then
    notify "L3a" "週次監査: YELLOW — 改善タスク起票推奨。$codex_out"
    log "Weekly audit: YELLOW. Improvement tasks recommended."
  else
    log "Weekly audit: ALL GREEN."
  fi
}

# --- On-commit audit (triggered by git hook) ---
run_on_commit() {
  log "Starting on-commit audit..."

  # Get changed files
  local changed
  changed=$(cd "$SCRIPT_DIR" && git diff --name-only HEAD~1 2>/dev/null)

  # Only audit if relevant files changed
  local needs_audit=false
  echo "$changed" | grep -qE '^(shim/hakudokai/|instructions/|\.claude/settings\.json|CLAUDE\.md)' && needs_audit=true

  if [ "$needs_audit" = false ]; then
    log "No relevant files changed. Skipping audit."
    return 0
  fi

  local out="${AUDIT_DIR}/commit_audit_${TIMESTAMP}.txt"
  local prompt="On-commit audit. Changed files: ${changed}. Check for: syntax errors, security issues, FKI directive consistency, deny list gaps. Brief report, RED/YELLOW/GREEN per file."

  npx @openai/codex exec -o "$out" --ephemeral "$prompt" 2>/dev/null
  log "Commit audit saved: $out"

  if grep -qi "RED" "$out" 2>/dev/null; then
    notify "L3b" "コミット監査RED: 確認要 — $out"
  fi
}

# --- Main ---
case "${1:-}" in
  daily)  run_daily ;;
  weekly) run_weekly ;;
  on-commit) run_on_commit ;;
  *)
    echo "Usage: $0 {daily|weekly|on-commit}" >&2
    exit 1
    ;;
esac
