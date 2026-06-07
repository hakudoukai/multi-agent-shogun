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
DETECT_STALE_LOCK_FILE="${DETECT_STALE_LOCK_FILE:-/tmp/fukuincho_detect_stale.lock}"

# ★cycle3 fix1 (HIGH-1 cure)★: 認可境界 sender x recipient x type 許可行列 (完全一致 allowlist)
# 設計§2(2) verbatim、prefix glob (karo-*) は spoof (karo-spoof / karo-fake) を通過させるため廃止。
# 配列要素 = "sender:recipient:type" 完全一致 join、空白なし。
_DETECT_STALE_ALLOWLIST_MATRIX=(
    "commander-third:fukuincho:auto_poke"
    "shogun-third:fukuincho:auto_poke"
    "karo-third:fukuincho:auto_poke"
    "gunshi-third:fukuincho:auto_poke"
    "ashigaru-third-1:fukuincho:auto_poke"
    "ashigaru-third-2:fukuincho:auto_poke"
    "ashigaru-third-3:fukuincho:auto_poke"
    "ashigaru-third-4:fukuincho:auto_poke"
    "ashigaru-third-5:fukuincho:auto_poke"
    "fukuincho:fukuincho:auto_poke"
    "commander-third:fukuincho:handshake"
    "shogun-third:fukuincho:handshake"
    "karo-third:fukuincho:handshake"
    "gunshi-third:fukuincho:handshake"
    "ashigaru-third-1:fukuincho:handshake"
    "ashigaru-third-2:fukuincho:handshake"
    "ashigaru-third-3:fukuincho:handshake"
    "ashigaru-third-4:fukuincho:handshake"
    "ashigaru-third-5:fukuincho:handshake"
)

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
# corr_id sanitize (★cycle3 fix4 (MED-1 cure)★: basename 正規化を廃止 — reject 化)
# 許可: 英数 + underscore + hyphen のみ ([A-Za-z0-9_-]+)
# 旧 impl: basename で path component を strip 後 regex 検証 → ../../etc/passwd を passwd へ
#         「正規化受理」する collision 温床 (MED-1)
# 新 impl: raw 入力をそのまま regex 検証、不合格 = ★reject★ (skip + log)、正規化なし
# ───────────────────────────────────────────────────────────
_detect_stale_sanitize_corr_id() {
    local raw="$1"
    if [ -z "$raw" ]; then
        _detect_stale_log "DENY" "corr_id_empty"
        return 1
    fi
    # ★fix4★: raw のまま regex で完全一致検証 — basename 正規化禁
    if ! printf '%s' "$raw" | grep -qE '^[A-Za-z0-9_-]+$'; then
        _detect_stale_log "DENY" "corr_id_unsafe_reject: raw='${raw}' (regex ^[A-Za-z0-9_-]+\$ 不合格、basename 正規化廃止)"
        return 1
    fi
    printf '%s' "$raw"
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

# ★cycle3 fix2 (HIGH-2 cure)★: inflight check→mark を flock で atomic 化
# 旧 impl 欠陥: comment は flock と記すが実装ゼロ、check と mark の間に TOCTOU race。
#               並行 cron 2 発で両 enqueue → 設計 I1 (race condition 不生) 違反。
# 新 impl: flock -x で排他取得した上で check→mark を 1 トランザクション化。
# Returns:
#   0 = newly marked (proceed enqueue)
#   1 = already inflight (race で他 cron が先に mark、skip)
#   2 = unsafe corr_id (sanitize reject)
#   3 = flock acquire failed (rare、I/O error 等)
_detect_stale_inflight_check_and_mark() {
    local raw_id="$1"
    local safe_id
    safe_id=$(_detect_stale_sanitize_corr_id "$raw_id") || return 2
    mkdir -p "$DETECT_STALE_INFLIGHT_DIR" 2>/dev/null

    # flock 専用 lock file (inflight marker file とは別) — sub-shell で fd 9 を open
    (
        flock -x 9 || exit 3
        if [ -f "${DETECT_STALE_INFLIGHT_DIR}/${safe_id}.inflight" ]; then
            exit 1   # 既 marked (race 検知)
        fi
        : > "${DETECT_STALE_INFLIGHT_DIR}/${safe_id}.inflight"
        exit 0
    ) 9>"$DETECT_STALE_LOCK_FILE"
    return $?
}

# 認可境界 (設計 §2 (2)、ae8083dd §2.4 継承)
# ★cycle3 fix1 (HIGH-1 cure)★: 旧 prefix glob (karo-*) は karo-spoof / karo-fake を通過させる
# 攻撃ベクタゆえ廃止。sender x recipient x type 許可行列で完全一致 (allowlist) 化。
_detect_stale_authz_check() {
    local row_json="$1"
    local from recipient type_val
    from=$(printf '%s' "$row_json" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("from",""))
except Exception: print("")' 2>/dev/null || echo "")
    recipient=$(printf '%s' "$row_json" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("recipient","fukuincho"))
except Exception: print("fukuincho")' 2>/dev/null || echo "fukuincho")
    type_val=$(printf '%s' "$row_json" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("type","auto_poke"))
except Exception: print("auto_poke")' 2>/dev/null || echo "auto_poke")

    # 完全一致 allowlist 照合 (prefix glob 廃止、spoof reject)
    local key="${from}:${recipient}:${type_val}"
    local allowed
    for allowed in "${_DETECT_STALE_ALLOWLIST_MATRIX[@]}"; do
        if [ "$key" = "$allowed" ]; then
            return 0
        fi
    done
    _detect_stale_log "DENY" "trigger_unauthorized: matrix_miss key='${key}' (prefix 緩和廃止、完全一致 only)"
    return 1
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

    # ★cycle3 fix3 (HIGH-3 cure)★: response_by_time 厳格判定 — 設計§2(1) 整合
    # 旧 impl 欠陥: 空 / parse 不能で fall through → auto-poke (期限なし row も STALE 化)
    # 新 impl:
    #   - 空 deadline → ANOMALY (rc=2)、auto-poke 禁
    #   - parse 不能 deadline → ANOMALY (rc=2)、auto-poke 禁
    #   - 未来 deadline → FRESH (rc=1)
    #   - 過去 deadline → STALE 候補 (継続評価)
    if [ -z "$response_by_time" ]; then
        _detect_stale_log "ANOMALY" "deadline_empty: corr_id=${safe_id} (期限なし row は auto-poke 禁、§2(1))"
        return 2
    fi
    local deadline_epoch
    deadline_epoch=$(date -d "$response_by_time" +%s 2>/dev/null || echo "0")
    if [ "$deadline_epoch" -le 0 ]; then
        _detect_stale_log "ANOMALY" "deadline_malformed: corr_id=${safe_id} response_by_time='${response_by_time}' (parse 不能 = auto-poke 禁)"
        return 2
    fi
    if [ "$now" -lt "$deadline_epoch" ]; then
        _detect_stale_log "FRESH" "corr_id=${safe_id} response_by_time=${response_by_time} not yet stale"
        return 1
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
# ★cycle3 fix2 (HIGH-2 cure)★: bare mark を atomic check_and_mark に置換、
#   並行 cron 2 発 race で両 enqueue する欠陥を flock で根治。
detect_stale_enqueue() {
    local raw_id="$1"
    local recipient="${2:-fukuincho}"
    local payload="${3:-確認して}"

    local safe_id
    safe_id=$(_detect_stale_sanitize_corr_id "$raw_id") || {
        _detect_stale_log "ERROR" "unsafe_correlation_id — enqueue refused"
        return 1
    }

    # ★fix2★ atomic check-and-mark (flock 排他取得下で check→mark を 1 トランザクション化)
    _detect_stale_inflight_check_and_mark "$raw_id"
    local mark_rc=$?
    case "$mark_rc" in
        0) ;;  # newly marked、proceed
        1)
            _detect_stale_log "SKIP" "atomic_race_inflight: corr_id=${safe_id} (並行 cron が先取、設計 I1 整合)"
            return 1
            ;;
        2)
            _detect_stale_log "ERROR" "unsafe_correlation_id at atomic mark — enqueue refused"
            return 1
            ;;
        3)
            _detect_stale_log "ERROR" "flock_acquire_failed: corr_id=${safe_id}"
            return 1
            ;;
        *)
            _detect_stale_log "ERROR" "unknown_atomic_rc=${mark_rc}: corr_id=${safe_id}"
            return 1
            ;;
    esac

    # 既存 ae8083dd omni engine entrypoint = 暫定 stub (実 entrypoint は別 task)
    # 構造化ログのみ emit (payload 実値はログ出さない、§14)
    _detect_stale_log "ENQUEUE" "corr_id=${safe_id} recipient=${recipient} (payload_redacted)"
    return 0
}
