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
_DETECT_STALE_STALE_SEC_DEFAULT=120   # 設計 §1.2 verbatim (stale 閾値 = response_by_time 超過 120s)
# ★km-92 (2026-09-17)★ `:-` → `-`: 未設定のみ既定へ。空 / 空白 / 非數 は _detect_stale_stale_sec が名指して倒す (裁 seq323062⑷ 乙)。
DETECT_STALE_STALE_SEC="${DETECT_STALE_STALE_SEC-$_DETECT_STALE_STALE_SEC_DEFAULT}"
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

# ★km-92 (2026-09-17) 閾を讀む★: DETECT_STALE_STALE_SEC (設計 §1.2 verbatim 120s) は宣のみで讀手 0 であつた
#   (repo 全体 `git grep` 1 行 = 宣其の物、閾を 999999 / abc にしても出目が変はらぬ = km-92 raw/30_kansu.txt)。
#   本函数が閾を ★比較に使ふのと同じ演算子 `[ -ge 0 ]` で検め★ (裁 seq323062⑷ 甲)、空 / 空白のみ / 非數 / 負 /
#   桁溢れ を ★名指して★ 既定へ倒す (同 乙)。stdout に有効値 (數字のみ) を刷る。rc は常に 0 (倒す事は失敗ではない、log に残す)。
_detect_stale_stale_sec() {
    local raw="${DETECT_STALE_STALE_SEC-}"
    local default="${_DETECT_STALE_STALE_SEC_DEFAULT:-120}"
    case "$raw" in
        '')
            _detect_stale_log "WARN" "stale_sec_empty: DETECT_STALE_STALE_SEC='' → 既定 ${default} へ倒す"
            printf '%s' "$default"; return 0 ;;
        *[![:space:]]*) ;;
        *)
            _detect_stale_log "WARN" "stale_sec_blank: DETECT_STALE_STALE_SEC='${raw}' (空白のみ) → 既定 ${default} へ倒す"
            printf '%s' "$default"; return 0 ;;
    esac
    case "$raw" in
        *[!0-9]*)
            _detect_stale_log "WARN" "stale_sec_malformed: DETECT_STALE_STALE_SEC='${raw}' (數字のみを受ける) → 既定 ${default} へ倒す"
            printf '%s' "$default"; return 0 ;;
    esac
    # 甲: 比較器そのもので検む (桁溢れ 2^63 は bash の [ が rc=2 で拒む = 30_kansu 実測)
    if ! [ "$raw" -ge 0 ] 2>/dev/null; then
        _detect_stale_log "WARN" "stale_sec_out_of_range: DETECT_STALE_STALE_SEC='${raw}' (比較器 [ -ge 0 ] rc≠0) → 既定 ${default} へ倒す"
        printf '%s' "$default"; return 0
    fi
    printf '%s' "$raw"; return 0
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
    # ★km-92 (2026-09-17) 方言と番人★
    #   旧: `date -d` は GNU 語法 ── BSD (macOS) では `illegal option -- d` rc=1 → `|| echo "0"` → ★正しい時刻も悉く
    #       deadline_malformed★ (km-92 raw/20_date.txt / 30_kansu 姿B)。且つ `[ "$deadline_epoch" -le 0 ]` は非數
    #       (abc / 空 / 1e3 / 2^63 / 改行入り) で rc=2 → if 偽 → 次の `[ now -lt … ]` も rc=2 → 偽 → ★STALE 候補へ
    #       落ちて auto-poke★ (30_kansu 姿S: abc / 空 / 2^63 / 1e3 が悉く enqueued=1)。註「parse 不能 → ANOMALY」は嘘であつた。
    #   新: python3 (本 lib が既に json で 5 箇所依る) の fromisoformat で方言無しに epoch へ (Z / ±hh:mm / ±hhmm /
    #       naive を受ける、enter_restart_common_watchdog.sh の `fromisoformat(….replace('Z','+00:00'))` と同 idiom)。
    #       出目は ★數字のみ★ を受け、其の上で比較器そのもの `[ -gt 0 ]` で検む (桁溢れは bash の [ が rc=2 で拒む)。
    #       何れも外れれば ANOMALY (fail-closed)。python3 が無ければ rc 127 → 空 → ANOMALY。
    local deadline_epoch
    deadline_epoch=$(printf '%s' "$response_by_time" | python3 -c 'import sys, re
from datetime import datetime
s = sys.stdin.read().strip()
if s.endswith("Z") or s.endswith("z"): s = s[:-1] + "+00:00"
s = re.sub(r"([+-]\d\d)(\d\d)$", r"\1:\2", s)
try: print(int(datetime.fromisoformat(s).timestamp()))
except Exception: sys.exit(1)' 2>/dev/null) || deadline_epoch=""
    case "$deadline_epoch" in
        ''|*[!0-9]*)
            _detect_stale_log "ANOMALY" "deadline_malformed: corr_id=${safe_id} response_by_time='${response_by_time}' epoch='${deadline_epoch}' (parse 不能 or 非數 = auto-poke 禁)"
            return 2 ;;
    esac
    #   上限 253402300799 = 9999-12-31T23:59:59Z (fromisoformat の上限)。parser が壊れて 2^63-1 を刷つても
    #   ★永久 FRESH★ に成らぬ様、比較器そのもの [ -gt 0 ] と [ -le 上限 ] の両側で検む (41 二走 S2_max_int が FRESH であつた疵)。
    if ! [ "$deadline_epoch" -gt 0 ] 2>/dev/null || ! [ "$deadline_epoch" -le 253402300799 ] 2>/dev/null; then
        _detect_stale_log "ANOMALY" "deadline_out_of_range: corr_id=${safe_id} response_by_time='${response_by_time}' epoch='${deadline_epoch}' (比較器 [ -gt 0 ] && [ -le 253402300799 ] rc≠0 = auto-poke 禁)"
        return 2
    fi
    # ★閾を讀む★: stale = now ≥ deadline + DETECT_STALE_STALE_SEC (設計 §1.2「response_by_time 超過 120s」)。
    #   `now - sec < deadline` の形で比較する (deadline + sec の桁溢れを避ける)。
    local stale_sec
    stale_sec=$(_detect_stale_stale_sec)
    if [ $((now - stale_sec)) -lt "$deadline_epoch" ]; then
        _detect_stale_log "FRESH" "corr_id=${safe_id} response_by_time=${response_by_time} not yet stale (deadline_epoch=${deadline_epoch} stale_sec=${stale_sec} now=${now})"
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
    local payload="${3:-確認依頼、コマンダーより}"

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
