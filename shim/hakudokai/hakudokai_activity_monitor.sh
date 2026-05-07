#!/usr/bin/env bash
# hakudokai_activity_monitor.sh — エージェント稼働監視デーモン
#
# 「プロセスが生きているか」ではなく「実際に仕事をしているか」を監視する。
# pane出力のハッシュを定期比較し、一定時間変化がなければ将軍に報告。
#
# 監視対象 (§18 PC×アカウント配置 — 理事長殿御指示 2026-05-06):
#   - MainPC multiagent session: karo, ashigaru1-3, gunshi (5 panes)
#   - SecondPC secondpc session: ashigaru5-8 (4 panes) ※存在時のみ
#   ※ ashigaru4 は欠番 (PC 境界の視覚的区切り)
#
# 報告方法:
#   - 将軍の inbox に idle_alert を書き込み（inbox_write.sh 経由）
#   - /tmp/hakudokai_activity_dashboard.json に最新状態を常時出力
#
# 監査コンプライアンス監視:
#   - タスク完了(done)なのに軍師の監査報告がない → audit_missing アラート
#   - 監査報告にCodex/Geminiが欠けている → audit_incomplete アラート
#   - 監査FAILなのに修正が進んでいない → pdca_stalled アラート
#   - 監査ログをダッシュボードJSONに含めて常時可視化
#
# Usage: bash shim/hakudokai/hakudokai_activity_monitor.sh [--idle-threshold 300] [--interval 30]
# idle-threshold: 秒（デフォルト300 = 5分）
# interval: チェック間隔秒（デフォルト30）

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IDLE_THRESHOLD="${IDLE_THRESHOLD:-300}"
CHECK_INTERVAL="${CHECK_INTERVAL:-30}"
DASHBOARD="/tmp/hakudokai_activity_dashboard.json"
LOG="/tmp/hakudokai_activity_monitor.log"
HASH_DIR="/tmp/hakudokai_activity_hashes"

# Cooldown: 同じエージェントへの重複アラートを防止（秒）
ALERT_COOLDOWN=600  # 10分間は同一エージェントの再アラートを抑制

# Parse args
while [ $# -gt 0 ]; do
  case "$1" in
    --idle-threshold) IDLE_THRESHOLD="$2"; shift 2 ;;
    --interval) CHECK_INTERVAL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

mkdir -p "$HASH_DIR"

log() {
  echo "[activity_monitor][$(date '+%H:%M:%S')] $1" | tee -a "$LOG" >&2
}

# タスクが割り当てられているか確認（assignedまたはin_progress）
has_active_task() {
  local agent="$1"
  local task_file="${SCRIPT_DIR}/queue/tasks/${agent}.yaml"
  if [ ! -f "$task_file" ]; then
    return 1  # タスクファイルなし = 監視不要
  fi
  local status
  status=$(grep '^\s*status:' "$task_file" | head -1 | sed 's/.*status:\s*//' | tr -d "' \"" | tr -d $'\r')
  case "$status" in
    assigned|work|in_progress) return 0 ;;
    *) return 1 ;;
  esac
}

# pane出力のハッシュを取得
get_pane_hash() {
  local pane="$1"
  tmux capture-pane -t "$pane" -p 2>/dev/null | md5sum | cut -d' ' -f1
}

# 前回ハッシュと比較し、変化があったかを判定
check_activity() {
  local agent="$1"
  local pane="$2"
  local hash_file="${HASH_DIR}/${agent}.hash"
  local time_file="${HASH_DIR}/${agent}.last_change"
  local now
  now=$(date +%s)

  # paneが存在するか確認
  local current_hash
  current_hash=$(get_pane_hash "$pane")
  if [ -z "$current_hash" ]; then
    # paneが存在しない（SecondPC未接続など）
    echo "unreachable"
    return
  fi

  # 前回ハッシュとの比較
  local prev_hash=""
  [ -f "$hash_file" ] && prev_hash=$(cat "$hash_file")

  if [ "$current_hash" != "$prev_hash" ]; then
    # 変化あり — ハッシュ更新、最終変化時刻を記録
    echo "$current_hash" > "$hash_file"
    echo "$now" > "$time_file"
    echo "active"
  else
    # 変化なし — 最終変化時刻からの経過を計算
    local last_change=0
    [ -f "$time_file" ] && last_change=$(cat "$time_file")
    if [ "$last_change" -eq 0 ]; then
      # 初回は「今」をセット
      echo "$now" > "$time_file"
      echo "$current_hash" > "$hash_file"
      echo "active"
    else
      local idle_seconds=$((now - last_change))
      if [ "$idle_seconds" -ge "$IDLE_THRESHOLD" ]; then
        echo "idle:${idle_seconds}"
      else
        echo "waiting:${idle_seconds}"
      fi
    fi
  fi
}

# アラート送信（cooldown付き）
send_idle_alert() {
  local agent="$1"
  local idle_seconds="$2"
  local cooldown_file="${HASH_DIR}/${agent}.last_alert"
  local now
  now=$(date +%s)

  # Cooldownチェック
  if [ -f "$cooldown_file" ]; then
    local last_alert
    last_alert=$(cat "$cooldown_file")
    local elapsed=$((now - last_alert))
    if [ "$elapsed" -lt "$ALERT_COOLDOWN" ]; then
      return  # クールダウン中、送らない
    fi
  fi

  local idle_min=$((idle_seconds / 60))

  # タスクが割り当てられているエージェントのみアラート
  if has_active_task "$agent"; then
    local task_id
    task_id=$(grep '^\s*task_id:' "${SCRIPT_DIR}/queue/tasks/${agent}.yaml" 2>/dev/null | head -1 | sed 's/.*task_id:\s*//' | tr -d "' \"" | tr -d $'\r')
    log "IDLE ALERT: ${agent} idle ${idle_min}min (task: ${task_id})"
    bash "${SCRIPT_DIR}/scripts/inbox_write.sh" shogun \
      "${agent}が${idle_min}分以上停止中。タスク: ${task_id}。確認が必要。" \
      idle_alert activity_monitor 2>/dev/null
    echo "$now" > "$cooldown_file"
  fi
}

# =============================================================
# 監査コンプライアンスチェック（三者監査: 軍師Claude→Codex→Gemini）
# =============================================================

AUDIT_CHECK_INTERVAL="${AUDIT_CHECK_INTERVAL:-120}"  # 監査チェックは2分ごと（軽くするため毎回ではない）
LAST_AUDIT_CHECK=0

# cooldown付きアラート送信（汎用）
send_alert_with_cooldown() {
  local alert_type="$1"
  local alert_key="$2"
  local message="$3"
  local cooldown_file="${HASH_DIR}/audit_${alert_key}.last_alert"
  local now
  now=$(date +%s)

  if [ -f "$cooldown_file" ]; then
    local last
    last=$(cat "$cooldown_file")
    local elapsed=$((now - last))
    if [ "$elapsed" -lt "$ALERT_COOLDOWN" ]; then
      return
    fi
  fi

  log "AUDIT ALERT [${alert_type}]: ${message}"
  bash "${SCRIPT_DIR}/scripts/inbox_write.sh" shogun \
    "${message}" \
    "${alert_type}" activity_monitor 2>/dev/null
  echo "$now" > "$cooldown_file"
}

# 各足軽のタスク完了→監査状況をチェック
check_audit_compliance() {
  local now
  now=$(date +%s)

  # 頻度制限
  if [ $((now - LAST_AUDIT_CHECK)) -lt "$AUDIT_CHECK_INTERVAL" ]; then
    return
  fi
  LAST_AUDIT_CHECK=$now

  local audit_entries=""
  local audit_first=true

  # §18: ashigaru4 は欠番。ashigaru1-3 = MainPC、ashigaru5-8 = SecondPC。
  for agent in ashigaru1 ashigaru2 ashigaru3 ashigaru5 ashigaru6 ashigaru7 ashigaru8; do
    local task_file="${SCRIPT_DIR}/queue/tasks/${agent}.yaml"
    [ ! -f "$task_file" ] && continue

    local task_status
    task_status=$(grep '^\s*status:' "$task_file" 2>/dev/null | head -1 | sed 's/.*status:\s*//' | tr -d "' \"" | tr -d $'\r')
    [ "$task_status" != "done" ] && continue

    local task_id
    task_id=$(grep '^\s*task_id:' "$task_file" 2>/dev/null | head -1 | sed 's/.*task_id:\s*//' | tr -d "' \"" | tr -d $'\r')

    # 足軽の完了報告があるか
    local report_file="${SCRIPT_DIR}/queue/reports/${agent}_report.yaml"
    if [ ! -f "$report_file" ]; then
      # 完了報告自体がない（異常だが監査以前の問題）
      if [ "$audit_first" = true ]; then audit_first=false; else audit_entries="${audit_entries},"; fi
      audit_entries="${audit_entries}\"${agent}\":{\"task_id\":\"${task_id}\",\"status\":\"no_report\"}"
      continue
    fi

    # 軍師の監査報告があるか
    local gunshi_report="${SCRIPT_DIR}/queue/reports/gunshi_report.yaml"
    if [ ! -f "$gunshi_report" ]; then
      send_alert_with_cooldown "audit_missing" "${agent}_no_gunshi" \
        "[監査未実施] ${agent}(${task_id})が完了済みだが軍師の監査報告なし。三者監査が必要。"
      if [ "$audit_first" = true ]; then audit_first=false; else audit_entries="${audit_entries},"; fi
      audit_entries="${audit_entries}\"${agent}\":{\"task_id\":\"${task_id}\",\"status\":\"audit_missing\"}"
      continue
    fi

    # 軍師報告の内容を解析
    local qa_decision
    qa_decision=$(grep '^\s*qa_decision:' "$gunshi_report" 2>/dev/null | head -1 | sed 's/.*qa_decision:\s*//' | tr -d "' \"" | tr -d $'\r')

    # 対象タスクの監査か確認
    local audited_task
    audited_task=$(grep '^\s*ashigaru_task_id:' "$gunshi_report" 2>/dev/null | head -1 | sed 's/.*ashigaru_task_id:\s*//' | tr -d "' \"" | tr -d $'\r')

    if [ "$audited_task" != "$task_id" ]; then
      # 軍師報告はあるが、このタスクの監査ではない
      send_alert_with_cooldown "audit_missing" "${agent}_wrong_task" \
        "[監査未実施] ${agent}(${task_id})の監査が未完了。軍師報告は別タスク(${audited_task})のもの。"
      if [ "$audit_first" = true ]; then audit_first=false; else audit_entries="${audit_entries},"; fi
      audit_entries="${audit_entries}\"${agent}\":{\"task_id\":\"${task_id}\",\"status\":\"audit_missing_for_task\"}"
      continue
    fi

    # Codex/Geminiの監査結果を確認
    local has_codex="false"
    local has_gemini="false"
    local codex_verdict="missing"
    local gemini_verdict="missing"

    grep -q 'codex:' "$gunshi_report" 2>/dev/null && has_codex="true"
    grep -q 'gemini:' "$gunshi_report" 2>/dev/null && has_gemini="true"

    if [ "$has_codex" = "true" ]; then
      codex_verdict=$(grep -A2 'codex:' "$gunshi_report" 2>/dev/null | grep 'verdict:' | head -1 | sed 's/.*verdict:\s*//' | tr -d "' \"" | tr -d $'\r')
    fi
    if [ "$has_gemini" = "true" ]; then
      gemini_verdict=$(grep -A2 'gemini:' "$gunshi_report" 2>/dev/null | grep 'verdict:' | head -1 | sed 's/.*verdict:\s*//' | tr -d "' \"" | tr -d $'\r')
    fi

    # 三者揃っているか
    if [ "$has_codex" = "false" ] || [ "$has_gemini" = "false" ]; then
      local missing=""
      [ "$has_codex" = "false" ] && missing="Codex"
      [ "$has_gemini" = "false" ] && missing="${missing:+$missing, }Gemini"
      send_alert_with_cooldown "audit_incomplete" "${agent}_incomplete" \
        "[三者監査不完全] ${agent}(${task_id})の監査で${missing}が未実施。三者全員のPASSが必須。"
      if [ "$audit_first" = true ]; then audit_first=false; else audit_entries="${audit_entries},"; fi
      audit_entries="${audit_entries}\"${agent}\":{\"task_id\":\"${task_id}\",\"status\":\"audit_incomplete\",\"missing\":\"${missing}\"}"
      continue
    fi

    # FAIL判定のチェック
    if [ "$qa_decision" = "fail" ]; then
      # FAILなのに足軽のタスクがdoneのまま → PDCAが回っていない
      # 修正タスク(redo)が割り当てられているか確認
      local redo_exists=false
      # §18: ashigaru4 は欠番。
      for redo_agent in ashigaru1 ashigaru2 ashigaru3 ashigaru5 ashigaru6 ashigaru7 ashigaru8; do
        local redo_file="${SCRIPT_DIR}/queue/tasks/${redo_agent}.yaml"
        [ ! -f "$redo_file" ] && continue
        if grep -q "redo_of:" "$redo_file" 2>/dev/null; then
          local redo_status
          redo_status=$(grep '^\s*status:' "$redo_file" 2>/dev/null | head -1 | sed 's/.*status:\s*//' | tr -d "' \"" | tr -d $'\r')
          if [ "$redo_status" = "assigned" ] || [ "$redo_status" = "work" ] || [ "$redo_status" = "in_progress" ]; then
            redo_exists=true
            break
          fi
        fi
      done

      if [ "$redo_exists" = false ]; then
        send_alert_with_cooldown "pdca_stalled" "${agent}_pdca" \
          "[PDCA停滞] ${agent}(${task_id})が監査FAIL(Codex:${codex_verdict}/Gemini:${gemini_verdict})だが修正タスクが未割当。家老に修正指示を出させよ。"
      fi

      if [ "$audit_first" = true ]; then audit_first=false; else audit_entries="${audit_entries},"; fi
      audit_entries="${audit_entries}\"${agent}\":{\"task_id\":\"${task_id}\",\"status\":\"fail_pending_fix\",\"qa_decision\":\"${qa_decision}\",\"codex\":\"${codex_verdict}\",\"gemini\":\"${gemini_verdict}\"}"
    else
      # PASS
      if [ "$audit_first" = true ]; then audit_first=false; else audit_entries="${audit_entries},"; fi
      audit_entries="${audit_entries}\"${agent}\":{\"task_id\":\"${task_id}\",\"status\":\"pass\",\"qa_decision\":\"${qa_decision}\",\"codex\":\"${codex_verdict}\",\"gemini\":\"${gemini_verdict}\"}"
    fi
  done

  # ダッシュボードに監査状況を保存
  echo "{${audit_entries}}" > "${HASH_DIR}/audit_compliance.json"
}

# ダッシュボード出力
update_activity_dashboard() {
  local now
  now=$(date +%s)
  local entries=""
  local first=true

  # multiagent session (§18 MainPC: karo + ashigaru1-3 + gunshi = 5 panes)
  local pane_index=0
  for agent in karo ashigaru1 ashigaru2 ashigaru3 gunshi; do
    local pane="multiagent:0.${pane_index}"
    local status_file="${HASH_DIR}/${agent}.status"
    local status="unknown"
    [ -f "$status_file" ] && status=$(tr -d '\r' < "$status_file")

    local task_status="none"
    local task_id="none"
    if [ -f "${SCRIPT_DIR}/queue/tasks/${agent}.yaml" ]; then
      task_status=$(grep '^\s*status:' "${SCRIPT_DIR}/queue/tasks/${agent}.yaml" 2>/dev/null | head -1 | sed 's/.*status:\s*//' | tr -d "' \"" | tr -d $'\r')
      task_id=$(grep '^\s*task_id:' "${SCRIPT_DIR}/queue/tasks/${agent}.yaml" 2>/dev/null | head -1 | sed 's/.*task_id:\s*//' | tr -d "' \"" | tr -d $'\r')
    fi

    local idle_sec=0
    local time_file="${HASH_DIR}/${agent}.last_change"
    if [ -f "$time_file" ]; then
      local lc
      lc=$(cat "$time_file")
      idle_sec=$((now - lc))
    fi

    if [ "$first" = true ]; then first=false; else entries="${entries},"; fi
    entries="${entries}\"${agent}\":{\"status\":\"${status}\",\"idle_seconds\":${idle_sec},\"task_id\":\"${task_id}\",\"task_status\":\"${task_status}\"}"
    pane_index=$((pane_index + 1))
  done

  # secondpc session (§18 SecondPC: ashigaru5-8 = 4 panes、存在時のみ)
  if tmux has-session -t secondpc 2>/dev/null; then
    for sp_entry in "ashigaru5:secondpc:0.0" "ashigaru6:secondpc:0.1" "ashigaru7:secondpc:0.2" "ashigaru8:secondpc:0.3"; do
      local sp_agent="${sp_entry%%:*}"
      local sp_pane="${sp_entry#*:}"
      local sp_status="unknown"
      [ -f "${HASH_DIR}/${sp_agent}.status" ] && sp_status=$(tr -d '\r' < "${HASH_DIR}/${sp_agent}.status")
      local sp_idle=0
      [ -f "${HASH_DIR}/${sp_agent}.last_change" ] && sp_idle=$((now - $(cat "${HASH_DIR}/${sp_agent}.last_change")))
      entries="${entries},\"${sp_agent}\":{\"status\":\"${sp_status}\",\"idle_seconds\":${sp_idle}}"
    done
  fi

  # 監査コンプライアンス情報
  local audit_json="{}"
  [ -f "${HASH_DIR}/audit_compliance.json" ] && audit_json=$(cat "${HASH_DIR}/audit_compliance.json")

  cat > "$DASHBOARD" <<EOJSON
{
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "idle_threshold_seconds": ${IDLE_THRESHOLD},
  "check_interval_seconds": ${CHECK_INTERVAL},
  "agents": {${entries}},
  "audit_compliance": ${audit_json}
}
EOJSON
}

# --- Main loop ---

log "started (idle_threshold=${IDLE_THRESHOLD}s, check_interval=${CHECK_INTERVAL}s)"

while true; do
  # multiagent session (§18 MainPC: karo + ashigaru1-3 + gunshi = 5 panes)
  pane_index=0
  for agent in karo ashigaru1 ashigaru2 ashigaru3 gunshi; do
    pane="multiagent:0.${pane_index}"
    result=$(check_activity "$agent" "$pane")
    echo "$result" > "${HASH_DIR}/${agent}.status"

    case "$result" in
      idle:*)
        idle_sec="${result#idle:}"
        send_idle_alert "$agent" "$idle_sec"
        ;;
    esac
    pane_index=$((pane_index + 1))
  done

  # secondpc session (§18 SecondPC: ashigaru5-8 = 4 panes、存在時のみ)
  if tmux has-session -t secondpc 2>/dev/null; then
    for sp_entry in "ashigaru5:secondpc:0.0" "ashigaru6:secondpc:0.1" "ashigaru7:secondpc:0.2" "ashigaru8:secondpc:0.3"; do
      sp_agent="${sp_entry%%:*}"
      sp_pane="${sp_entry#*:}"
      result=$(check_activity "$sp_agent" "$sp_pane")
      echo "$result" > "${HASH_DIR}/${sp_agent}.status"
      case "$result" in
        idle:*)
          idle_sec="${result#idle:}"
          # §18: agent 名が role 名と直接一致 (旧 sakura/kuro alias は廃止)
          [ -f "${SCRIPT_DIR}/queue/tasks/${sp_agent}.yaml" ] && send_idle_alert "$sp_agent" "$idle_sec"
          ;;
      esac
    done
  fi

  # 監査コンプライアンスチェック（2分ごと）
  check_audit_compliance

  update_activity_dashboard
  sleep "$CHECK_INTERVAL"
done
