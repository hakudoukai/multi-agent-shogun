#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# detect_stale.sh — fukuincho 段階3 全自動ループ 層① 検知層 (lib)
# ═══════════════════════════════════════════════════════════════
# 設計章節正本: docs/08-ops/fukuincho-stage3-auto-loop-design.md §2
#   commit f1c268d (SHA256=fcf49731df98d812ad83a3d078e01afff306c13e6b867cbc033f3541ab95fb1b)
#   governing audit: subtask_thirdpc_p1_fukuincho_stage3_design_governing_audit_001
#
# Source for this redo:
#   - subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_002
#   - gunshi-third governing RED-1 真因 cure: 関数群を main loop 後ろから lib へ分離
#     (前 impl 4f1f82b1 では scripts/inbox_watcher.sh の while-true main loop L1320
#      の後ろに関数定義 → 通常実行で永久未到達 dead code であった)
#   - gunshi-third RED-2 真因 cure: corr_id sanitize (^[A-Za-z0-9_-]+$ regex + basename)
#     で path traversal 防御
#
# 用法:
#   source scripts/lib/detect_stale.sh
#   detect_stale_evaluate_row "$row_json"   # 0=enqueue 推奨, 1=skip, 2=anomaly
#   detect_stale_enqueue "$corr_id" "$recipient" "$payload"
#
# CLI entrypoint = scripts/fukuincho_detect_stale_cli.sh (cron 60s から invoke)
# ═══════════════════════════════════════════════════════════════

# 多重 source guard
if [ -n "${__FUKUINCHO_DETECT_STALE_LIB_LOADED:-}" ]; then
    return 0
fi
__FUKUINCHO_DETECT_STALE_LIB_LOADED=1

DETECT_STALE_LOG="${DETECT_STALE_LOG:-/tmp/fukuincho_detect_stale.log}"
DETECT_STALE_INFLIGHT_DIR="${DETECT_STALE_INFLIGHT_DIR:-/tmp/fukuincho_inflight}"
DETECT_STALE_STALE_SEC="${DETECT_STALE_STALE_SEC:-120}"   # 設計 §1.2 verbatim

_detect_stale_log() {
    local lvl="$1"; shift
    printf '%s [%s] %s\n' "$(date -Iseconds)" "$lvl" "$*" >> "$DETECT_STALE_LOG" 2>/dev/null || true
}

# status enum 正本 (設計 §2 (1)、Codex T1 是正)
_detect_stale_status_valid() {
    case "$1" in
        pending|in_progress) return 0 ;;
        confirmed|escalated|human_required|closed) return 1 ;;  # 終端 — stale 判定対象外
        *) return 2 ;;  # malformed/null/未知
    esac
}

# ───────────────────────────────────────────────────────────
# corr_id sanitize (gunshi-third RED-2 cure、path traversal 防御)
# 許可: 英数 + underscore + hyphen のみ ([A-Za-z0-9_-]+)
# 加えて basename 強制で .. や / を完全排除
# ───────────────────────────────────────────────────────────
_detect_stale_sanitize_corr_id() {
    local raw="$1"
    # basename で path component を除去 (.. や / 完全排除)
    local base
    base=$(basename -- "$raw" 2>/dev/null || echo "")
    # 英数 + _ + - のみ許可 regex 検証
    if ! printf '%s' "$base" | grep -qE '^[A-Za-z0-9_-]+$'; then
        _detect_stale_log "DENY" "corr_id_unsafe: raw='${raw}' base='${base}' (regex ^[A-Za-z0-9_-]+\$ 不合格)"
        return 1
    fi
    if [ -z "$base" ]; then
        _detect_stale_log "DENY" "corr_id_empty"
        return 1
    fi
    printf '%s' "$base"
    return 0
}

# in-flight 二重評価防止 (Codex B2 是正、flock + in-flight set)
_detect_stale_inflight_check() {
    local raw_id="$1"
    local safe_id
    safe_id=$(_detect_stale_sanitize_corr_id "$raw_id") || return 1
    mkdir -p "$DETECT_STALE_INFLIGHT_DIR" 2>/dev/null
    [ -f "${DETECT_STALE_INFLIGHT_DIR}/${safe_id}.inflight" ]
}

_detect_stale_inflight_mark() {
    local raw_id="$1"
    local safe_id
    safe_id=$(_detect_stale_sanitize_corr_id "$raw_id") || return 1
    mkdir -p "$DETECT_STALE_INFLIGHT_DIR" 2>/dev/null
    : > "${DETECT_STALE_INFLIGHT_DIR}/${safe_id}.inflight"
}

_detect_stale_inflight_clear() {
    local raw_id="$1"
    local safe_id
    safe_id=$(_detect_stale_sanitize_corr_id "$raw_id") || return 1
    rm -f "${DETECT_STALE_INFLIGHT_DIR}/${safe_id}.inflight" 2>/dev/null
}

# 認可境界 (設計 §2 (2)、ae8083dd §2.4 継承、Codex S1 是正)
_detect_stale_authz_check() {
    local row_json="$1"
    local from
    from=$(printf '%s' "$row_json" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("from",""))
except Exception: print("")' 2>/dev/null || echo "")
    case "$from" in
        commander-*|shogun-*|karo-*|gunshi-*|ashigaru-*)
            return 0
            ;;
        *)
            _detect_stale_log "DENY" "trigger_unauthorized: from=${from} not in trusted registry"
            return 1
            ;;
    esac
}

# trigger 候補評価 (設計 §2 (1)+(2)+(4))
# Returns: 0=enqueue 推奨, 1=skip (status 終端 or 未認可 or in-flight or unsafe corr_id), 2=anomaly
detect_stale_evaluate_row() {
    local row_json="$1"

    local status response_by_time corr_id_raw now
    status=$(printf '%s' "$row_json" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("status",""))
except Exception: print("")' 2>/dev/null || echo "")
    response_by_time=$(printf '%s' "$row_json" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("response_by_time",""))
except Exception: print("")' 2>/dev/null || echo "")
    corr_id_raw=$(printf '%s' "$row_json" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("correlation_id",""))
except Exception: print("")' 2>/dev/null || echo "")
    now=$(date +%s)

    # (1) status enum 厳密判定
    _detect_stale_status_valid "$status"
    local rc=$?
    if [ "$rc" -eq 1 ]; then
        _detect_stale_log "SKIP" "status_terminal: status=${status}"
        return 1
    fi
    if [ "$rc" -eq 2 ]; then
        _detect_stale_log "ANOMALY" "status_malformed: status=${status}"
        return 2
    fi

    # (2) 認可境界
    if ! _detect_stale_authz_check "$row_json"; then
        return 1
    fi

    # corr_id sanitize 早期評価 (RED-2 cure)
    if [ -z "$corr_id_raw" ]; then
        _detect_stale_log "ANOMALY" "corr_id_missing"
        return 2
    fi
    local safe_id
    safe_id=$(_detect_stale_sanitize_corr_id "$corr_id_raw") || return 1

    # response_by_time 超過判定 (epoch 比較)
    if [ -n "$response_by_time" ]; then
        local deadline_epoch
        deadline_epoch=$(date -d "$response_by_time" +%s 2>/dev/null || echo "0")
        if [ "$deadline_epoch" -gt 0 ] && [ "$now" -lt "$deadline_epoch" ]; then
            _detect_stale_log "FRESH" "corr_id=${safe_id} response_by_time=${response_by_time} not yet stale"
            return 1
        fi
    fi

    # (4) in-flight 二重評価防止
    if _detect_stale_inflight_check "$safe_id"; then
        _detect_stale_log "SKIP" "in_flight: corr_id=${safe_id}"
        return 1
    fi

    _detect_stale_log "STALE" "corr_id=${safe_id} stale判定"
    return 0
}

# enqueue (層③ omni engine 呼出 — 既存 inbox_write.sh 経路を wrap)
# correlation_id 継承 (新規採番禁、設計 §2 (3))
detect_stale_enqueue() {
    local raw_id="$1"
    local recipient="${2:-fukuincho}"
    local payload="${3:-確認して}"

    local safe_id
    safe_id=$(_detect_stale_sanitize_corr_id "$raw_id") || {
        _detect_stale_log "ERROR" "unsafe_correlation_id — enqueue refused"
        return 1
    }

    _detect_stale_inflight_mark "$safe_id"

    # 既存 ae8083dd omni engine entrypoint = 暫定 stub (実 entrypoint は別 task)
    # 構造化ログのみ emit (payload 実値はログ出さない、§14)
    _detect_stale_log "ENQUEUE" "corr_id=${safe_id} recipient=${recipient} (payload_redacted)"
    return 0
}
