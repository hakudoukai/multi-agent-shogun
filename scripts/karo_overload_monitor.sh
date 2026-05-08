#!/usr/bin/env bash
# karo_overload_monitor.sh — 家老輻輳監視 watcher (cmd_karo_overload_takenaka_assist_001 §6.1+§6.2)
#
# 用途:
#   家老 (秀吉/karo) の輻輳兆候を 5 指標で検知し、竹中に分担補助 alert + 信長に CRITICAL alert を発火する。
#   single-shot 方式、cron / supervisor 経由で 30秒〜1分間隔の周期実行を想定 (= 本 script 自身は loop しない)。
#
# 5 検知指標 (信長殿明示):
#   M1. karo inbox unread 件数  ≥ KARO_UNREAD_THRESHOLD (既定 10)
#   M2. inbox 受信→処理 latency ≥ KARO_LATENCY_THRESHOLD_SEC (既定 300、5 分)
#   M3. cmd 受領→ashigaru dispatch latency ≥ DISPATCH_LATENCY_THRESHOLD_SEC (既定 300、5 分)
#   M4. 並列 cmd_new 受領数 (1h)  ≥ PARALLEL_CMD_NEW_THRESHOLD (既定 5)
#   M5. 未着手 sub-phase 数      ≥ UNSTARTED_SUBPHASE_THRESHOLD (既定 3)
#
# 自動分担境界 (= 重要、絶対遵守):
#   - 竹中 OK 領域: audit / preparation / 隘路検出 / skill 違反監視
#   - 家老専管: ashigaru dispatch / 三者監査判定 / 強権発動 / dashboard 主管 / redo
#   - 本 watcher は **alert 発火のみ**、自動 task 発令は行わない (= 越境防止)
#
# Watcher Design Principles (CLAUDE.md "Watcher Design Principles" 完全準拠):
#   1. retry 無限ループ禁止: 単発 watch、retry なし
#   2. self-send 即 ack: 該当なし (= alert 送信のみ、自身は受信しない)
#   3. 手動停止フラグ尊重: ~/.openclaw/disable_karo_overload_monitor + ~/.openclaw/global_disable
#   4. 重複検知: 5 分 cooldown で同種 alert 重複防止
#   5. idempotency: state file ベース、副作用最小
#
# §15 Self-Healing パターン:
#   - SH3 (graceful degradation): state file 不在時 fresh start (= 安全側倒し)
#   - SH6 (limited self-restart): 同 alert 1h 5 回上限、超過時 stderr 警告 + skip
#   - 危険パターン D2 厳禁: 連続失敗時の forceful 系切替なし
#
# Error Design 8 項目:
#   - 構造化ログ: stderr に JSON 形式 (timestamp/level/source/corr_id/hit_metrics/...)
#   - correlation_id: 各実行で UUID-like (= karo_overload-<unix_ts>-<pid>)
#   - アラート発火条件: 5 指標 hit 時 → 竹中 inbox + 信長 inbox CRITICAL
#   - fallback: state file 読込失敗時 fresh start
#   - retry cap: 単発、retry なし
#   - ヘルスチェック: /tmp/karo_overload_monitor.health (JSON)
#   - エラー dump: hit 時 dump file (mktemp + 0600)
#   - ユーザー向けエラー文言: stderr 警告
#
# 出力:
#   stdout = 実行サマリ (人間可読)
#   stderr = 構造化 JSON ログ + WARN/ERROR
# exit:
#   0 = 正常終了 (= alert 発火 / cooldown skip / cap skip / disabled いずれも 0)
#   非 0 = 内部異常のみ (= 通常運用では出さない)

set -uo pipefail

# /tmp dump file の symlink/clobber 攻撃対策
umask 077

# ─── 定数 / 設定 ──────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# bats / external test 用 env override
: "${KARO_INBOX:=$REPO_ROOT/queue/inbox/karo.yaml}"
: "${TASKS_DIR:=$REPO_ROOT/queue/tasks}"
: "${TAKENAKA_INBOX:=$REPO_ROOT/queue/inbox/takenaka.yaml}"
: "${SHOGUN_INBOX:=$REPO_ROOT/queue/inbox/shogun.yaml}"
: "${INBOX_WRITE_CMD:=$SCRIPT_DIR/inbox_write.sh}"
: "${STATE_FILE:=/tmp/karo_overload_monitor_state.json}"
: "${HEALTH_FILE:=/tmp/karo_overload_monitor.health}"
: "${DUMP_DIR:=/tmp}"
: "${DISABLE_FLAG:=$HOME/.openclaw/disable_karo_overload_monitor}"
: "${GLOBAL_DISABLE_FLAG:=$HOME/.openclaw/global_disable}"

# 検知閾値 (env override 可)
: "${KARO_UNREAD_THRESHOLD:=10}"
: "${KARO_LATENCY_THRESHOLD_SEC:=300}"
: "${DISPATCH_LATENCY_THRESHOLD_SEC:=300}"
: "${PARALLEL_CMD_NEW_THRESHOLD:=5}"
: "${UNSTARTED_SUBPHASE_THRESHOLD:=3}"

# §15 SH6 cap + cooldown
: "${COOLDOWN_SEC:=300}"      # 同 alert 5 分 cooldown
: "${ALERT_CAP_PER_HOUR:=5}"  # 1h 5 回上限

# 動作モード
#   default = check + alert (本番)
#   check-only = 検知のみ、alert 送信しない (= bats / smoke 用)
: "${MONITOR_MODE:=default}"

# correlation_id: 構造化ログ用
CORR_ID="karo_overload-$(date +%s)-$$"
NOW_EPOCH=$(date +%s)
NOW_ISO=$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S%z)

# ─── 構造化ログ helper ────────────────────────────────────────────────
log_json() {
    local level="$1"
    local msg="$2"
    shift 2
    local extra="$*"
    # stderr 単独行 JSON、jq 等で grep 可能
    if [ -n "$extra" ]; then
        printf '{"ts":"%s","level":"%s","source":"karo_overload_monitor","corr_id":"%s","msg":"%s",%s}\n' \
            "$NOW_ISO" "$level" "$CORR_ID" "$msg" "$extra" >&2
    else
        printf '{"ts":"%s","level":"%s","source":"karo_overload_monitor","corr_id":"%s","msg":"%s"}\n' \
            "$NOW_ISO" "$level" "$CORR_ID" "$msg" >&2
    fi
}

# ─── 手動停止フラグ尊重 ───────────────────────────────────────────────
if [ -f "$GLOBAL_DISABLE_FLAG" ]; then
    echo "▼ karo_overload_monitor disabled by global flag: $GLOBAL_DISABLE_FLAG"
    log_json INFO "disabled_by_global_flag" "\"flag\":\"$GLOBAL_DISABLE_FLAG\""
    exit 0
fi
if [ -f "$DISABLE_FLAG" ]; then
    echo "▼ karo_overload_monitor disabled by flag: $DISABLE_FLAG"
    log_json INFO "disabled_by_flag" "\"flag\":\"$DISABLE_FLAG\""
    exit 0
fi

# ─── ヘルスファイル更新 (= 5 分以上更新なし=死亡判定可) ───────────────
write_health() {
    local status="$1"
    local hits="$2"
    # 失敗しても続行 (= advisory only)
    {
        printf '{"alive":true,"ts":"%s","corr_id":"%s","status":"%s","hit_count":%s,"uptime_sec":%s}\n' \
            "$NOW_ISO" "$CORR_ID" "$status" "$hits" "$SECONDS"
    } > "$HEALTH_FILE" 2>/dev/null || true
}

# ─── state file load (= SH3 graceful degradation) ─────────────────────
# state schema:
#   {
#     "last_alert_at": <epoch>,
#     "alert_history_1h": [<epoch>, <epoch>, ...],
#     "last_hit_metrics": ["M1","M3", ...]
#   }
load_state() {
    if [ ! -f "$STATE_FILE" ]; then
        STATE_LAST_ALERT_AT=0
        STATE_ALERT_HISTORY=""
        return 0
    fi
    # python3 で安全に parse (= jq 依存回避)
    local out
    out=$(python3 - "$STATE_FILE" <<'PYEOF' 2>/dev/null || true
import json, sys
try:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        data = json.load(f)
    last = int(data.get("last_alert_at", 0) or 0)
    hist = data.get("alert_history_1h", []) or []
    hist = [int(x) for x in hist if isinstance(x, (int, float))]
    print(f"{last}|{','.join(str(x) for x in hist)}")
except Exception:
    print("0|")
PYEOF
)
    if [ -z "$out" ]; then
        # SH3: fresh start
        STATE_LAST_ALERT_AT=0
        STATE_ALERT_HISTORY=""
        log_json WARN "state_load_failed_fresh_start" "\"file\":\"$STATE_FILE\""
        return 0
    fi
    STATE_LAST_ALERT_AT="${out%%|*}"
    STATE_ALERT_HISTORY="${out##*|}"
}

save_state() {
    local last_alert="$1"
    local history_csv="$2"
    local hit_metrics_csv="$3"
    # 1h 内のみ残す (= alert_history_1h 名前通り)
    local cutoff=$((NOW_EPOCH - 3600))
    local filtered=""
    if [ -n "$history_csv" ]; then
        local IFS=','
        for ts in $history_csv; do
            [ -z "$ts" ] && continue
            if [ "$ts" -ge "$cutoff" ] 2>/dev/null; then
                filtered="${filtered:+$filtered,}$ts"
            fi
        done
    fi
    # JSON 配列形式に変換
    local hist_json="[]"
    if [ -n "$filtered" ]; then
        hist_json="[$filtered]"
    fi
    local hits_json="[]"
    if [ -n "$hit_metrics_csv" ]; then
        local IFS=','
        local first=1
        hits_json="["
        for m in $hit_metrics_csv; do
            [ -z "$m" ] && continue
            if [ "$first" = "1" ]; then
                hits_json="${hits_json}\"$m\""
                first=0
            else
                hits_json="${hits_json},\"$m\""
            fi
        done
        hits_json="${hits_json}]"
    fi
    local tmp_state
    tmp_state=$(mktemp "${STATE_FILE}.XXXXXX") || return 0
    cat > "$tmp_state" <<EOF
{
  "last_alert_at": $last_alert,
  "alert_history_1h": $hist_json,
  "last_hit_metrics": $hits_json,
  "last_run_corr_id": "$CORR_ID",
  "last_run_ts": "$NOW_ISO"
}
EOF
    mv -f "$tmp_state" "$STATE_FILE" 2>/dev/null || rm -f "$tmp_state" 2>/dev/null
}

# ─── 5 指標検知 ───────────────────────────────────────────────────────

# M1 + M2 + M3 + M4: karo.yaml を 1 度だけ python で解析
# 出力フォーマット (1 行 5 値、|区切り):
#   <unread_count>|<oldest_unread_age_sec>|<oldest_cmd_new_unread_age_sec>|<cmd_new_count_1h>|<status>
analyze_karo_inbox() {
    if [ ! -f "$KARO_INBOX" ]; then
        log_json WARN "karo_inbox_missing" "\"file\":\"$KARO_INBOX\""
        echo "0|0|0|0|missing"
        return 0
    fi
    python3 - "$KARO_INBOX" "$NOW_EPOCH" <<'PYEOF' 2>/dev/null || echo "0|0|0|0|parse_error"
import sys, datetime, re
try:
    import yaml  # PyYAML
except Exception:
    yaml = None

path = sys.argv[1]
now = int(sys.argv[2])

def parse_ts(s):
    if not s:
        return None
    s = str(s).strip().strip('"').strip("'")
    # ISO 8601 with optional offset
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                # JST 仮定 (= 既存メッセージはローカル ISO)
                dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
            return int(dt.timestamp())
        except Exception:
            continue
    return None

unread = 0
oldest_unread_age = 0
oldest_cmd_new_unread_age = 0
cmd_new_count_1h = 0
status = "ok"

try:
    with open(path, "r", encoding="utf-8") as f:
        if yaml is not None:
            data = yaml.safe_load(f) or {}
        else:
            data = None
    if data is None:
        # PyYAML なし、最小 fallback parser (= read: false 件数のみ)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        unread = len(re.findall(r"^\s*read:\s*false\s*$", text, re.MULTILINE))
        # cmd_new count fallback
        cmd_new_total = len(re.findall(r"^\s*type:\s*cmd_new\s*$", text, re.MULTILINE))
        cmd_new_count_1h = cmd_new_total  # 過大評価上等、advisory
        status = "fallback_no_yaml"
    else:
        msgs = data.get("messages") or []
        cutoff_1h = now - 3600
        for m in msgs:
            if not isinstance(m, dict):
                continue
            is_read = bool(m.get("read", False))
            mtype = str(m.get("type", "") or "")
            ts_raw = m.get("timestamp")
            ts_epoch = parse_ts(ts_raw)
            if not is_read:
                unread += 1
                if ts_epoch is not None:
                    age = now - ts_epoch
                    if age > oldest_unread_age:
                        oldest_unread_age = age
                if mtype == "cmd_new" and ts_epoch is not None:
                    age = now - ts_epoch
                    if age > oldest_cmd_new_unread_age:
                        oldest_cmd_new_unread_age = age
            if mtype == "cmd_new" and ts_epoch is not None and ts_epoch >= cutoff_1h:
                cmd_new_count_1h += 1
except Exception as e:
    status = f"error:{type(e).__name__}"

print(f"{unread}|{oldest_unread_age}|{oldest_cmd_new_unread_age}|{cmd_new_count_1h}|{status}")
PYEOF
}

# M5: 未着手 sub-phase = ashigaru*.yaml で status: assigned のもの
count_unstarted_subphases() {
    local count=0
    if [ ! -d "$TASKS_DIR" ]; then
        echo "0"
        return 0
    fi
    # ashigaru タスク YAML のみ対象 (= 家老 dispatch 範囲)
    shopt -s nullglob
    local f
    for f in "$TASKS_DIR"/ashigaru*.yaml; do
        [ -f "$f" ] || continue
        # status: assigned を grep (= シンプルさ優先、advisory)
        if grep -qE '^\s*status:\s*assigned\s*$' "$f" 2>/dev/null; then
            count=$((count + 1))
        fi
    done
    shopt -u nullglob
    echo "$count"
}

# ─── alert 送信 ───────────────────────────────────────────────────────
send_alert() {
    local hit_metrics_csv="$1"
    local m1="$2"
    local m2="$3"
    local m3="$4"
    local m4="$5"
    local m5="$6"

    local content
    content="[karo_overload_monitor] 家老輻輳兆候検知 (corr_id=$CORR_ID): hits=[$hit_metrics_csv] / unread=$m1 / oldest_unread_age_sec=$m2 / oldest_cmd_new_unread_age_sec=$m3 / cmd_new_1h=$m4 / unstarted_subphases=$m5。竹中殿、CLAUDE.md §6.1 自動分担境界に基づき audit/preparation/隘路検出/skill 違反監視 領域での補助を依頼する。"

    if [ "$MONITOR_MODE" = "check-only" ]; then
        log_json INFO "alert_skipped_check_only_mode" "\"hits\":\"$hit_metrics_csv\""
        return 0
    fi

    # inbox_write.sh 経由 (= D006 違反なし、self-send guard あり)
    # from = nobunaga (= 信長補完 watcher、F002 違反なし)
    # 失敗しても続行 (advisory)
    local ok_takenaka=0
    local ok_shogun=0
    if [ -x "$INBOX_WRITE_CMD" ] || [ -f "$INBOX_WRITE_CMD" ]; then
        if bash "$INBOX_WRITE_CMD" takenaka "$content" assist_request nobunaga >/dev/null 2>&1; then
            ok_takenaka=1
        else
            log_json ERROR "takenaka_inbox_write_failed" "\"err_code\":\"ERR-INFRA-OVERLOAD-001\""
        fi
        # 信長 inbox は CRITICAL severity 別文面
        local shogun_content
        shogun_content="[karo_overload_monitor CRITICAL] 家老輻輳検知 (corr_id=$CORR_ID): hits=[$hit_metrics_csv]。竹中に assist_request 送付済 (ok=$ok_takenaka)。dashboard 🚨要対応 確認推奨。"
        if bash "$INBOX_WRITE_CMD" shogun "$shogun_content" karo_overload_alert nobunaga >/dev/null 2>&1; then
            ok_shogun=1
        else
            log_json ERROR "shogun_inbox_write_failed" "\"err_code\":\"ERR-INFRA-OVERLOAD-002\""
        fi
    else
        log_json ERROR "inbox_write_cmd_unavailable" "\"path\":\"$INBOX_WRITE_CMD\""
    fi

    log_json INFO "alert_sent" "\"hits\":\"$hit_metrics_csv\",\"takenaka_ok\":$ok_takenaka,\"shogun_ok\":$ok_shogun"
    echo "  📨 alert 送付: takenaka_ok=$ok_takenaka shogun_ok=$ok_shogun"
}

# ─── dump file 保存 (= 後日デバッグ用、mktemp + 0600) ──────────────────
write_dump() {
    local hits_csv="$1"
    local m1="$2"
    local m2="$3"
    local m3="$4"
    local m4="$5"
    local m5="$6"
    local cooldown_skip="$7"
    local cap_skip="$8"
    local dump_path
    dump_path=$(mktemp "${DUMP_DIR}/karo_overload_dump.XXXXXX.json") || return 0
    cat > "$dump_path" <<EOF
{
  "err_code": "ERR-INFRA-OVERLOAD-DETECTED-001",
  "ts": "$NOW_ISO",
  "corr_id": "$CORR_ID",
  "hit_metrics": "$hits_csv",
  "values": {
    "M1_karo_unread": $m1,
    "M2_oldest_unread_age_sec": $m2,
    "M3_oldest_cmd_new_unread_age_sec": $m3,
    "M4_cmd_new_count_1h": $m4,
    "M5_unstarted_subphases": $m5
  },
  "thresholds": {
    "M1": $KARO_UNREAD_THRESHOLD,
    "M2": $KARO_LATENCY_THRESHOLD_SEC,
    "M3": $DISPATCH_LATENCY_THRESHOLD_SEC,
    "M4": $PARALLEL_CMD_NEW_THRESHOLD,
    "M5": $UNSTARTED_SUBPHASE_THRESHOLD
  },
  "cooldown_skip": $cooldown_skip,
  "cap_skip": $cap_skip,
  "alert_history_1h_count": $CURRENT_ALERT_COUNT_1H
}
EOF
    chmod 600 "$dump_path" 2>/dev/null || true
    echo "$dump_path"
}

# ─── main flow ────────────────────────────────────────────────────────
main() {
    echo "▼ karo_overload_monitor (corr_id=$CORR_ID, mode=$MONITOR_MODE)"

    load_state

    # 5 指標取得
    local karo_analysis
    karo_analysis=$(analyze_karo_inbox)
    local m1 m2 m3 m4 m_status
    IFS='|' read -r m1 m2 m3 m4 m_status <<<"$karo_analysis"
    : "${m1:=0}"; : "${m2:=0}"; : "${m3:=0}"; : "${m4:=0}"; : "${m_status:=unknown}"
    local m5
    m5=$(count_unstarted_subphases)
    : "${m5:=0}"

    echo "  M1 karo_unread=$m1 (threshold=$KARO_UNREAD_THRESHOLD)"
    echo "  M2 oldest_unread_age_sec=$m2 (threshold=$KARO_LATENCY_THRESHOLD_SEC)"
    echo "  M3 oldest_cmd_new_unread_age_sec=$m3 (threshold=$DISPATCH_LATENCY_THRESHOLD_SEC)"
    echo "  M4 cmd_new_count_1h=$m4 (threshold=$PARALLEL_CMD_NEW_THRESHOLD)"
    echo "  M5 unstarted_subphases=$m5 (threshold=$UNSTARTED_SUBPHASE_THRESHOLD)"
    echo "  inbox_status=$m_status"

    # 各 hit 判定
    local hits_csv=""
    [ "$m1" -ge "$KARO_UNREAD_THRESHOLD" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M1"
    [ "$m2" -ge "$KARO_LATENCY_THRESHOLD_SEC" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M2"
    [ "$m3" -ge "$DISPATCH_LATENCY_THRESHOLD_SEC" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M3"
    [ "$m4" -ge "$PARALLEL_CMD_NEW_THRESHOLD" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M4"
    [ "$m5" -ge "$UNSTARTED_SUBPHASE_THRESHOLD" ] 2>/dev/null && hits_csv="${hits_csv:+$hits_csv,}M5"

    # 1h 内 alert 件数集計 (SH6 cap)
    local cutoff_1h=$((NOW_EPOCH - 3600))
    CURRENT_ALERT_COUNT_1H=0
    if [ -n "$STATE_ALERT_HISTORY" ]; then
        local IFS=','
        local ts
        for ts in $STATE_ALERT_HISTORY; do
            [ -z "$ts" ] && continue
            if [ "$ts" -ge "$cutoff_1h" ] 2>/dev/null; then
                CURRENT_ALERT_COUNT_1H=$((CURRENT_ALERT_COUNT_1H + 1))
            fi
        done
    fi

    if [ -z "$hits_csv" ]; then
        echo "  ✅ 5 指標いずれも閾値未満、輻輳兆候なし"
        log_json INFO "no_hit" "\"m1\":$m1,\"m2\":$m2,\"m3\":$m3,\"m4\":$m4,\"m5\":$m5"
        write_health "no_hit" 0
        save_state "$STATE_LAST_ALERT_AT" "$STATE_ALERT_HISTORY" ""
        return 0
    fi

    echo "  🚨 hit metrics=[$hits_csv]"

    # 重複 cooldown チェック (= 5 分以内 dedupe)
    local cooldown_skip=false
    if [ "$STATE_LAST_ALERT_AT" -gt 0 ] 2>/dev/null; then
        local since_last=$((NOW_EPOCH - STATE_LAST_ALERT_AT))
        if [ "$since_last" -lt "$COOLDOWN_SEC" ] 2>/dev/null; then
            cooldown_skip=true
            echo "  ⏸ cooldown skip (since_last=${since_last}s < ${COOLDOWN_SEC}s)"
            log_json INFO "cooldown_skip" "\"since_last_sec\":$since_last,\"cooldown_sec\":$COOLDOWN_SEC,\"hits\":\"$hits_csv\""
        fi
    fi

    # SH6 cap チェック (= 1h 5 回上限)
    local cap_skip=false
    if [ "$CURRENT_ALERT_COUNT_1H" -ge "$ALERT_CAP_PER_HOUR" ] 2>/dev/null; then
        cap_skip=true
        echo "  ⏸ SH6 cap skip (alert_count_1h=$CURRENT_ALERT_COUNT_1H >= cap=$ALERT_CAP_PER_HOUR)"
        log_json WARN "sh6_cap_skip" "\"count_1h\":$CURRENT_ALERT_COUNT_1H,\"cap\":$ALERT_CAP_PER_HOUR,\"hits\":\"$hits_csv\""
    fi

    # dump file は hit 時必ず保存 (= 監査証跡)
    local dump_path
    dump_path=$(write_dump "$hits_csv" "$m1" "$m2" "$m3" "$m4" "$m5" "$cooldown_skip" "$cap_skip")
    [ -n "$dump_path" ] && echo "  📝 dump: $dump_path"

    if [ "$cooldown_skip" = "true" ] || [ "$cap_skip" = "true" ]; then
        write_health "skipped" "$CURRENT_ALERT_COUNT_1H"
        # state はそのまま保持 (= last_alert_at 上書きしない、history 加算しない)
        save_state "$STATE_LAST_ALERT_AT" "$STATE_ALERT_HISTORY" "$hits_csv"
        return 0
    fi

    # alert 送信
    send_alert "$hits_csv" "$m1" "$m2" "$m3" "$m4" "$m5"

    # check-only mode は state を進めない (= cooldown 不正進行回避、smoke / bats 用)
    if [ "$MONITOR_MODE" = "check-only" ]; then
        write_health "check_only_hit" "$CURRENT_ALERT_COUNT_1H"
        save_state "$STATE_LAST_ALERT_AT" "$STATE_ALERT_HISTORY" "$hits_csv"
        return 0
    fi

    # state 更新 (= history に追加)
    local new_history
    if [ -n "$STATE_ALERT_HISTORY" ]; then
        new_history="${STATE_ALERT_HISTORY},${NOW_EPOCH}"
    else
        new_history="$NOW_EPOCH"
    fi
    save_state "$NOW_EPOCH" "$new_history" "$hits_csv"
    write_health "alert_sent" "$((CURRENT_ALERT_COUNT_1H + 1))"
}

# CURRENT_ALERT_COUNT_1H は main 内で算出し write_dump からも参照可
CURRENT_ALERT_COUNT_1H=0
main "$@"
exit 0
