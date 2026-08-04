#!/usr/bin/env bash
# inbox_write.sh — メールボックスへのメッセージ書き込み（排他ロック付き）
# Usage:
#   通常 (argv 経由): bash scripts/inbox_write.sh <target_agent> <content> <type> <from>
#   ★stdin 経由 (cycle2 S2 cure)★:
#       INBOX_WRITE_CONTENT_STDIN=1 bash scripts/inbox_write.sh <target> __VIA_STDIN__ <type> <from> < <(echo "$CONTENT")
#       env INBOX_WRITE_CONTENT_STDIN=1 が立っている時は $2 を無視して stdin から content を読む。
#       process inspection (ps/argv leak) で機密内容が見えるのを防ぐ用途 (fukuincho_report_poke_bundle.py で利用)。
#   ★correlation_id 任意指定 (ae8083dd 着火ackリトライ再送エンジン対応)★:
#       INBOX_WRITE_CORRELATION_ID=<id> bash scripts/inbox_write.sh <target> <content> <type> <from>
#       未指定時は自動採番 (charset ^[A-Za-z0-9_-]+$ のみ許可、既存4位置引数APIは不変)。
#       成功時 stdout に "MSG_ID=... CORRELATION_ID=..." を出力 (既存 caller は非捕捉、確認済)。
# Example: bash scripts/inbox_write.sh karo "足軽5号、任務完了" report_received ashigaru5

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SB_AUTH_LIB="$SCRIPT_DIR/shim/hakudokai/lib/sb_auth.sh"
COMPACT_DELIVERY_LEASE_LIB="$SCRIPT_DIR/scripts/lib/compact_delivery_lease_lib.sh"
# shellcheck disable=SC1090
source "$SB_AUTH_LIB"
if [ ! -r "$COMPACT_DELIVERY_LEASE_LIB" ]; then
    echo "[inbox_write] FAIL-CLOSED: missing compact delivery lease library: $COMPACT_DELIVERY_LEASE_LIB" >&2
    exit 70
fi
# shellcheck disable=SC1090
source "$COMPACT_DELIVERY_LEASE_LIB"
TARGET="$1"
CONTENT="$2"
TYPE="$3"
FROM="$4"

# ★cycle2 S2 cure (med)★: stdin 経由 content 受領 (argv 露出 cure)
# 既存 caller (positional argv) は env 未設定で従来動作、backward compatible
if [ "${INBOX_WRITE_CONTENT_STDIN:-}" = "1" ]; then
    CONTENT="$(cat)"
fi

# ★ae8083dd 着火ackリトライ再送エンジン対応★: correlation_id 任意 env 受領。
# INBOX_WRITE_CONTENT_STDIN と同じ env-var 拡張パターン (既存 4 位置引数 API
# は不変・後方互換維持)。未指定時は下で自動採番 (§2.5 "correlation_id 非
# null" 要件充足)。既存 pc_handshake.correlation_id と同一意味論を再利用
# (家老裁定 msg_20220722_103826_d5452e76 の拘束— 新規 namespace 禁)。
CORRELATION_ID="${INBOX_WRITE_CORRELATION_ID:-}"

INBOX="$SCRIPT_DIR/queue/inbox/${TARGET}.yaml"
LOCKFILE="${INBOX}.lock"

# Validate arguments
if [ -z "$TARGET" ] || [ -z "$CONTENT" ] || [ -z "$TYPE" ] || [ -z "$FROM" ]; then
    echo "Usage: inbox_write.sh <target_agent> <content> <type> <from>" >&2
    exit 1
fi

# Self-send guard: reject messages where sender == target
if [ "$FROM" = "$TARGET" ]; then
    echo "[inbox_write] REJECTED: self-send detected (from=$FROM, target=$TARGET)" >&2
    exit 1
fi

# correlation_id charset guard (detect_stale.sh:_detect_stale_sanitize_corr_id
# 踏襲— path-traversal/python文字列注入回避のため正規化せず即reject、MED-1
# 教訓再利用)。空文字列は許可 (下で自動採番)。
if [ -n "$CORRELATION_ID" ] && ! echo "$CORRELATION_ID" | grep -qE '^[A-Za-z0-9_-]+$'; then
    echo "[inbox_write] REJECTED: unsafe correlation_id charset (must match ^[A-Za-z0-9_-]+\$): $CORRELATION_ID" >&2
    exit 1
fi

# Amplification guard (2026-05-07 真因対策):
# stop_hook block + claude bash 経由の自己増殖ループ防止。
# content に「[<from>→<target>][<type>]」パターンが 3 回以上含まれていたら、
# 既に増幅された content の再送信と判定して reject。
_AMP_PATTERN_COUNT=$(echo "$CONTENT" | grep -oE '\[[a-zA-Z_0-9]+→[a-zA-Z_0-9]+\]\[[a-zA-Z_0-9]+\]' | wc -l)
if [ "${_AMP_PATTERN_COUNT:-0}" -ge 3 ]; then
    echo "[inbox_write] REJECTED: amplification loop detected (${_AMP_PATTERN_COUNT} embedded headers in content, threshold=3) target=$TARGET from=$FROM" >&2
    exit 1
fi

# Compact delivery fence (race cure, 2026-07-24):
# Every delivery path takes the same per-target coordination lock used by
# compact_delivery_lease.sh. The lease is checked while holding that lock,
# before hermes2 routing, cross-PC bridge launch, or local inbox mutation.
# This makes "lease publish" and "delivery permission" mutually exclusive.
DELIVERY_COORDINATION_LOCKFILE="$(compact_delivery_lock_path "$SCRIPT_DIR" "$TARGET")" || {
    echo "[inbox_write] FAIL-CLOSED: unable to derive compact delivery lock path target=$TARGET" >&2
    exit 70
}
DELIVERY_COORDINATION_LEASEFILE="$(compact_delivery_lease_path "$SCRIPT_DIR" "$TARGET")" || {
    echo "[inbox_write] FAIL-CLOSED: unable to derive compact delivery lease path target=$TARGET" >&2
    exit 70
}
DELIVERY_COORDINATION_FALLBACK_DIR=""
DELIVERY_COORDINATION_LOCK_HELD=0

_acquire_delivery_coordination_lock() {
    # Default is deliberately unbounded. A writer queued before a compact
    # reservation must finish first; a writer queued after publication must
    # observe the lease. An arbitrary timeout would silently drop valid work.
    local timeout_seconds="${COMPACT_DELIVERY_LOCK_TIMEOUT_SECONDS:-}"
    mkdir -p "$(dirname "$DELIVERY_COORDINATION_LOCKFILE")"

    if command -v flock >/dev/null 2>&1; then
        exec 199>"$DELIVERY_COORDINATION_LOCKFILE"
        if [ -n "$timeout_seconds" ]; then
            flock -w "$timeout_seconds" 199 || return 1
        else
            flock -x 199 || return 1
        fi
    else
        DELIVERY_COORDINATION_FALLBACK_DIR="${DELIVERY_COORDINATION_LOCKFILE}.d"
        local attempts=0
        while ! mkdir "$DELIVERY_COORDINATION_FALLBACK_DIR" 2>/dev/null; do
            attempts=$((attempts + 1))
            if [ -n "$timeout_seconds" ] && [ "$attempts" -ge "$((timeout_seconds * 10))" ]; then
                return 1
            fi
            sleep 0.1
        done
    fi
    DELIVERY_COORDINATION_LOCK_HELD=1
}

_release_delivery_coordination_lock() {
    [ "$DELIVERY_COORDINATION_LOCK_HELD" -eq 1 ] || return 0
    if command -v flock >/dev/null 2>&1; then
        flock -u 199 2>/dev/null || true
        exec 199>&-
    elif [ -n "$DELIVERY_COORDINATION_FALLBACK_DIR" ]; then
        rmdir "$DELIVERY_COORDINATION_FALLBACK_DIR" 2>/dev/null || true
        DELIVERY_COORDINATION_FALLBACK_DIR=""
    fi
    DELIVERY_COORDINATION_LOCK_HELD=0
}

# ★anti-dup fix (HERMES-AUTH-93727ABE-S1-HELPER-NOT-SOURCED-001 followup、
# 軍師 Option B 設計回答 msg_20260721_140010_d713651b 採用)★
#
# local_pc (自 PC の pc_id) + target_pc (宛先 PC、target agent 指定時のみ)
# 解決の単一責務 helper。従来 _cross_pc_bridge() と _hermes2_deaddrop_guard()
# がそれぞれ独立に同一の pc_mapping lookup パターンを実装していた (重複)。
# さらにその後の anti-dup 是正で local_pc/target_pc を★別々の python
# invocation★に分割した結果、cycle6 Codex 監査 (S1/B1) で指摘された通り
# (a) 2回の config 読込間の TOCTOU、(b) 一方だけが独立に失敗し得る部分障害
# モード、が新たに生じていた (家老裁定 msg_20260721_160326_83ff7c4b、A案)。
#
# 本 helper は target_pc/local_pc を★単一 python invocation・単一 config
# 読込 snapshot★から同時に解決することで、上記2種の不整合を構造的に排除する。
# 両 caller はこれのみを呼ぶ (_cross_pc_bridge / _hermes2_deaddrop_guard の
# 直接相互呼出しは行わない)。
#
# 引数: $1 = target agent 名 (省略可)。省略時は target_pc 部分は常に空。
# stdout: "local_pc|target_pc" (pipe 区切り、常に1行)。
#   - local_pc: 解決できた自 PC の pc_id。解決不可時は空文字列。
#   - target_pc: target 指定時のみ、bridge 対象 PC の pc_id。対象外/未指定/
#     解決不可時は空文字列。
#   - 例外発生時は両方とも空 ("|") — 一方だけが成功した状態は返さない
#     (cycle6 B1 の根絶: 部分成功を許さない)。
# fail-closed 判定 (空文字列時にどう振る舞うか) は呼出し側の責務 — 両 caller
# で contract が異なる (_cross_pc_bridge は "${local_pc:-main_pc}" フォール
# バックで非 fail-closed、_hermes2_deaddrop_guard は fail-closed) ため、本
# helper 自体はどちらの契約も強制しない (既存契約は変更しない、家老裁定)。
_resolve_local_pc() {
    local target="${1:-}"
    "$SCRIPT_DIR/.venv/bin/python3" -c "
import yaml, os
try:
    local_path = '$SCRIPT_DIR/config/settings_local.yaml'
    main_path = '$SCRIPT_DIR/config/settings.yaml'
    if os.path.exists(local_path):
        with open(local_path) as f:
            local_cfg = yaml.safe_load(f) or {}
        pc_map = local_cfg.get('pc_mapping', {})
    else:
        pc_map = {}
    if not pc_map:
        with open(main_path) as f:
            cfg = yaml.safe_load(f) or {}
        pc_map = cfg.get('pc_mapping', {})
    local_id = ''
    target_pc = ''
    for pc_name, pc_cfg in pc_map.items():
        if pc_cfg.get('is_local'):
            local_id = pc_cfg.get('pc_id', pc_name)
            continue
        agents = pc_cfg.get('agents', [])
        if '$target' and '$target' in agents and pc_cfg.get('supabase_bridge'):
            target_pc = pc_cfg.get('pc_id', pc_name)
    print(f'{local_id}|{target_pc}')
except Exception:
    print('|')
" 2>/dev/null
}

# Cross-PC bridge: if target agent is on a different PC, also INSERT to Supabase
_cross_pc_bridge() {
    local target="$1"
    local content="$2"
    local msg_type="$3"
    local from="$4"

    # target_pc + local_pc を単一 snapshot から同時解決 (anti-dup 維持 +
    # cycle6 TOCTOU/B1 是正、共有 helper _resolve_local_pc に一本化)。
    local resolved local_pc target_pc
    resolved=$(_resolve_local_pc "$target")
    local_pc="${resolved%%|*}"
    target_pc="${resolved#*|}"

    if [ -z "$target_pc" ]; then
        return 0  # Local agent, no bridge needed
    fi

    # Load Supabase env
    local sb_url sb_key
    if [ -f "$HOME/.hakudokai/env" ]; then
        sb_url=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
        sb_key=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
    fi
    sb_url="${SUPABASE_URL:-$sb_url}"
    sb_key="${SUPABASE_SERVICE_ROLE_KEY:-$sb_key}"

    if [ -z "$sb_url" ] || [ -z "$sb_key" ]; then
        echo "[inbox_write] WARN: cross-PC bridge skipped (no Supabase env)" >&2
        return 0
    fi

    # Truncate content for Supabase (max 2000 chars)
    local truncated="${content:0:2000}"

    # JSON encode via python3 (heredoc + argv) — bash 文字列補間では改行/特殊文字が
    # JSON に直接埋め込まれて Supabase が「0x0a must be escaped」で reject していた。
    # ★ae8083dd 着火ackリトライ再送エンジン (item⑤) 対応★: pc_handshake は
    # 既存 correlation_id column を持つ (fukuincho_handshake_overdue_feeder.sh
    # 参照実績あり) が本 bridge の INSERT payload は従来これを埋めていなかった
    # ため、cross-PC Stage A/B 確認の grounding が不可能だった。$CORRELATION_ID
    # (行37でresolve済、ack-retry engine 自身の呼出は必ず
    # INBOX_WRITE_CORRELATION_ID を明示付与するため _cross_pc_bridge 起動時点
    # (行391、autogen 前) でも値確定済) を追加するのみの最小加算的変更
    # (既存 caller は corr未指定→null、挙動不変)。
    local payload
    payload=$(python3 - "$truncated" "${local_pc:-main_pc}" "$target_pc" "$target" "$from" "$msg_type" "$CORRELATION_ID" <<'PYEOF'
import json, sys
content_truncated, local_pc, target_pc, target_agent, from_agent, msg_type, corr_id = sys.argv[1:8]
out = {
    "message_type": msg_type,
    "from_pc": local_pc,
    "to_pc": target_pc,
    "topic": f"cross_pc_inbox_{target_agent}",
    "content": f"[{from_agent}→{target_agent}][{msg_type}] {content_truncated}",
    "requires_response": False,
    "priority": "normal",
    "clinic_id": "hakudoukai_main",
    "bypass_5round_limit": False,
    "is_meta_only": False
}
if corr_id:
    out["correlation_id"] = corr_id
print(json.dumps(out, ensure_ascii=False))
PYEOF
)

    # INSERT to Supabase for cross-PC delivery
    SUPABASE_SERVICE_ROLE_KEY="$sb_key" sb_curl -sS \
        --connect-timeout "${COMPACT_DELIVERY_BRIDGE_CONNECT_TIMEOUT_SECONDS:-5}" \
        --max-time "${COMPACT_DELIVERY_BRIDGE_MAX_SECONDS:-20}" \
        -X POST \
        "${sb_url}/rest/v1/pc_handshake" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=minimal" \
        --data-binary "$payload" \
        2>/dev/null \
        && echo "[inbox_write] cross-PC bridge: ${target} → ${target_pc} via Supabase" >&2 \
        || echo "[inbox_write] WARN: cross-PC bridge INSERT failed for ${target}" >&2
}

# ★hermes2 (環境部長) dead-drop producer guard★ (副委員長指令
# hermes2-dead-drop-route-guard-work-order-20260721.md 起点 pc_handshake
# seq131730/seq131740)。
#
# 真因: hermes2 は config/settings.yaml の全 pc_mapping[*].agents に不在
# のため _cross_pc_bridge() は hermes2 宛では構造的に絶対起動しない。結果、
# legacy queue/inbox/hermes2.yaml (consumer 不在) への無条件書込のみが常に
# 成功し、未読が無期限蓄積していた (実績: 未読7件)。
#
# 対策: TARGET が "hermes2" に完全一致する場合のみ、legacy YAML 書込に
# 進む前でこの関数が同期的に正規 pc_handshake へ INSERT する。成功時は
# legacy 書込を完全 skip、失敗時は fail-closed (legacy へフォールバック
# しない・明示エラーで exit 1) とする。相談役 (hermes / hermes-main) は
# 完全一致でないため対象外 (誤変換防止、work order item 4)。
_hermes2_deaddrop_guard() {
    local content="$1"
    local msg_type="$2"
    local from="$3"

    # 緊急停止フラグ: cross_pc_bridge 同様、hermes2 guard も無効化可能。
    # フラグ存在時は curl を一切呼ばず fail-closed (legacy へは絶対に進まない)。
    if [ -f "$HOME/.openclaw/disable_cross_pc_bridge" ]; then
        echo "[inbox_write] FAIL-CLOSED: hermes2 dead-drop guard disabled via disable_cross_pc_bridge flag; refusing legacy fallback for hermes2" >&2
        return 1
    fi

    # local_pc 解決は共有 helper _resolve_local_pc() に委譲 (anti-dup fix、
    # HERMES-AUTH-93727ABE-S1-HELPER-NOT-SOURCED-001 followup、軍師 Option B
    # msg_20260721_140010_d713651b)。_cross_pc_bridge との直接相互呼出しは
    # しない — 両者ともこの共有 helper のみを呼ぶ。target 未指定呼出しのため
    # 常に "local_pc|" 形式で返る ("%%|*" で bare local_pc を取り出す。既存
    # fail-closed 契約自体は不変更、cycle6 是正で戻り値の形式のみ適応)。
    local local_pc
    local_pc=$(_resolve_local_pc)
    local_pc="${local_pc%%|*}"

    if [ -z "$local_pc" ]; then
        echo "[inbox_write] FAIL-CLOSED: hermes2 dead-drop guard could not resolve local_pc from pc_mapping; refusing legacy fallback for hermes2" >&2
        return 1
    fi

    # Supabase 資格情報
    local sb_url sb_key
    if [ -f "$HOME/.hakudokai/env" ]; then
        sb_url=$(grep '^SUPABASE_URL=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
        sb_key=$(grep '^SUPABASE_SERVICE_ROLE_KEY=' "$HOME/.hakudokai/env" | cut -d= -f2- | tr -d '\r')
    fi
    sb_url="${SUPABASE_URL:-$sb_url}"
    sb_key="${SUPABASE_SERVICE_ROLE_KEY:-$sb_key}"

    if [ -z "$sb_url" ] || [ -z "$sb_key" ]; then
        echo "[inbox_write] FAIL-CLOSED: hermes2 dead-drop guard has no Supabase credentials; refusing legacy fallback for hermes2" >&2
        return 1
    fi

    local truncated="${content:0:2000}"

    # message_type を pc_handshake の CHECK allowlist へ正規化
    # (request_permission grant_permission decline_permission status_update
    #  urgent_stop question answer ack file_sync)。allowlist 外は
    # status_update へ fallback、元の $TYPE は content prefix に保持する。
    local payload
    payload=$(python3 - "$truncated" "$local_pc" "hermes2" "$from" "$msg_type" <<'PYEOF'
import json, sys
content_truncated, local_pc, target_agent, from_agent, orig_type = sys.argv[1:6]
ALLOWED = {"request_permission", "grant_permission", "decline_permission",
           "status_update", "urgent_stop", "question", "answer", "ack", "file_sync"}
normalized_type = orig_type if orig_type in ALLOWED else "status_update"
print(json.dumps({
    "message_type": normalized_type,
    "from_pc": local_pc,
    "to_pc": "hermes2",
    "topic": f"hermes2_deaddrop_guard_{target_agent}",
    "content": f"[{from_agent}→hermes2][{orig_type}] {content_truncated}",
    "requires_response": False,
    "priority": "normal",
    "clinic_id": "hakudoukai_main",
    "bypass_5round_limit": False,
    "is_meta_only": False
}, ensure_ascii=False))
PYEOF
)

    # 同期 (非 background) INSERT。curl 自体の exit code だけでなく実
    # HTTP status も検査する (_cross_pc_bridge より厳格・fail-closed 要件)。
    local resp_file http_status curl_status
    resp_file=$(mktemp)
    # set -e 下では http_status=$(...) 単体の代入失敗が即シェル終了を招き
    # FAIL-CLOSED 分岐へ到達しない (Codex監査 cycle1 B1)。if の条件式内で
    # 代入することで curl の非0終了を確実に捕捉する。
    if http_status=$(SUPABASE_SERVICE_ROLE_KEY="$sb_key" sb_curl -sS \
        --connect-timeout "${COMPACT_DELIVERY_BRIDGE_CONNECT_TIMEOUT_SECONDS:-5}" \
        --max-time "${COMPACT_DELIVERY_BRIDGE_MAX_SECONDS:-20}" \
        -o "$resp_file" -w '%{http_code}' -X POST \
        "${sb_url}/rest/v1/pc_handshake" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=minimal" \
        --data-binary "$payload" \
        2>/dev/null); then
        curl_status=0
    else
        curl_status=$?
        http_status=""
    fi

    if [ "$curl_status" -eq 0 ] && echo "$http_status" | grep -qE '^2[0-9][0-9]$'; then
        echo "[inbox_write] hermes2 dead-drop guard: canonical pc_handshake INSERT succeeded (http=${http_status}); legacy hermes2.yaml write skipped" >&2
        rm -f "$resp_file"
        return 0
    else
        # S1是正: レスポンス本文はstderrへ出力しない (内部詳細の漏洩懸念)。
        # 判定に必要な curl_status/http_status のみ記録する。
        echo "[inbox_write] FAIL-CLOSED: hermes2 dead-drop guard canonical pc_handshake INSERT failed (curl_status=${curl_status}, http=${http_status}); refusing legacy fallback for hermes2" >&2
        rm -f "$resp_file"
        return 1
    fi
}

# ★hermes2 (環境部長) alias/表示名 正規化 (G1 REDO cycle2 finding
# H2-G1-ROLE-ALIAS-GUARD-MISSING-001 是正)★
#
# 正本: shim/hakudokai/hakudokai_fukuincho_reverse_poll.py の
# _format_codex_sender() が唯一の技術ID↔表示名マッピング正本。そこでは
# hermes2 → 環境部長 が確定しており、hermes / hermes-main → 相談役 は
# 構造的に別エントリ (末尾に数字 "2" を含まない)。config/hermes-departments-registry.json
# は department-head 専用サブセッション registry で hermes2 に一切言及が
# なく対象外と確認済 (route matrix report 参照、anti-duplication rule 順守)。
#
# 分類は3段:
#   (a) canonical  — "hermes2" / "環境部長" の完全一致、または大小文字・
#       区切り文字 (-, _, space) のみが異なる ASCII 変種 (例: hermes-2,
#       HERMES2, Hermes_2 等)。正規化は必ず「hermes」+ 区切り記号除去 +
#       数字「2」」に厳密一致させる。相談役 (hermes/hermes-main) は数字
#       "2" を含まないため、この正規化では絶対に一致しない (誤変換防止、
#       work order item 4 / T-105・T-106 既存 negative test と整合)。
#   (b) none       — 上記いずれにも該当しない、hermes2 と無関係な target。
#       通常の legacy ルートへそのまま進む (挙動変更なし)。
#   (c) near_miss  — "hermes" と "2" の両方を含むが (a) の完全一致セット
#       に含まれない未知の類似名、または "環境部長" を部分文字列として
#       含むが完全一致ではない名前。fail-closed (legacy へ絶対に進まない
#       ・明示エラーで exit 1)。誤って新しい legacy alias ファイルが
#       生成される事故を防ぐ。
_hermes2_alias_kind() {
    local raw="$1"
    case "$raw" in
        hermes2|環境部長|hermes-2|hermes_2|"hermes 2"|HERMES2|Hermes2|HERMES-2|Hermes-2|Hermes_2|"Hermes 2")
            echo "canonical"
            return 0
            ;;
    esac
    local norm
    norm=$(printf '%s' "$raw" | tr '[:upper:]' '[:lower:]' | tr -d ' _-')
    if [ "$norm" = "hermes2" ]; then
        echo "canonical"
        return 0
    fi
    case "$norm" in
        *hermes*2*)
            echo "near_miss"
            return 0
            ;;
    esac
    case "$raw" in
        *環境部長*)
            echo "near_miss"
            return 0
            ;;
    esac
    echo "none"
    return 0
}

# hermes2 (canonical alias/表示名含む) は legacy YAML dead-drop 経路から
# 完全除外。正規 pc_handshake が成功すればここで exit 0 (legacy 書込に
# 一切進まない)、失敗すれば exit 1 (fail-closed、legacy へのフォール
# バックは絶対にしない)。near_miss は canonical guard を経由せず即
# fail-closed (curl すら呼ばない、legacy 書込より前で確実に止める)。
if ! _acquire_delivery_coordination_lock; then
    echo "[inbox_write] FAIL-CLOSED: compact delivery coordination lock timeout target=$TARGET" >&2
    exit 75
fi
trap _release_delivery_coordination_lock EXIT

if [ -f "$DELIVERY_COORDINATION_LEASEFILE" ]; then
    echo "DELIVERY_BLOCKED_COMPACT_LEASE target=$TARGET lease=$DELIVERY_COORDINATION_LEASEFILE" >&2
    exit 75
fi

_H2_ALIAS_KIND=$(_hermes2_alias_kind "$TARGET")
case "$_H2_ALIAS_KIND" in
    canonical)
        if _hermes2_deaddrop_guard "$CONTENT" "$TYPE" "$FROM"; then
            exit 0
        else
            exit 1
        fi
        ;;
    near_miss)
        echo "[inbox_write] FAIL-CLOSED: TARGET='$TARGET' resembles hermes2/環境部長 but is not a recognized canonical alias; refusing legacy fallback (unknown near-miss, work order item 4 H2-G1-ROLE-ALIAS-GUARD-MISSING-001)" >&2
        exit 1
        ;;
esac

# Trigger cross-PC bridge synchronously while the compact coordination lock is
# held. A background bridge could POST after a lease had already published.
# 緊急停止 2026-05-07 18:23: 連続 INSERT loop 発生中、source 不明
# ~/.openclaw/disable_cross_pc_bridge flag 存在時は cross_pc_bridge を起動しない
if [ ! -f "$HOME/.openclaw/disable_cross_pc_bridge" ]; then
    _cross_pc_bridge "$TARGET" "$CONTENT" "$TYPE" "$FROM"
fi

# Initialize inbox if not exists
if [ ! -f "$INBOX" ]; then
    mkdir -p "$(dirname "$INBOX")"
    echo "messages: []" > "$INBOX"
fi

# Generate unique message ID (timestamp + 4 random bytes).
# Use `od` instead of `xxd` because `od` is available on both GNU/Linux and macOS runners by default.
MSG_ID="msg_$(date +%Y%m%d_%H%M%S)_$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
TIMESTAMP=$(date "+%Y-%m-%dT%H:%M:%S")

# 未指定時の自動採番は opt-in 限定 (fb66b73b境界: G1受入前は既存無関係呼出への
# 本番影響を回避、karo-third是正指示 msg_20260722_110357_7024877b 対応)。
# ack-retry engine 自身の呼出のみ INBOX_WRITE_ENABLE_CORRELATION_AUTOGEN=1 を
# 明示付与し auto採番を有効化する。無指定の既存呼出 (stop_hook_inbox.sh 等) は
# 旧挙動 (correlation_id なし) を維持する。§2.5 correlation_id 非null要件は
# G1受入・engine本番化後に auto-gen をデフォルト化して満たす想定 (暫定措置)。
if [ -z "$CORRELATION_ID" ] && [ "${INBOX_WRITE_ENABLE_CORRELATION_AUTOGEN:-}" = "1" ]; then
    CORRELATION_ID="corr_$(date +%Y%m%d_%H%M%S)_$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')"
fi

# Cross-platform lock: flock (Linux) or mkdir (macOS fallback)
LOCK_DIR="${LOCKFILE}.d"

_acquire_lock() {
    if command -v flock &>/dev/null; then
        exec 200>"$LOCKFILE"
        flock -w 5 200 || return 1
    else
        local i=0
        while ! mkdir "$LOCK_DIR" 2>/dev/null; do
            sleep 0.1
            i=$((i + 1))
            [ $i -ge 50 ] && return 1  # 5s timeout
        done
    fi
    return 0
}

_release_lock() {
    if command -v flock &>/dev/null; then
        exec 200>&-
    else
        rmdir "$LOCK_DIR" 2>/dev/null
    fi
}

# Atomic write with lock (3 retries)
attempt=0
max_attempts=3

while [ $attempt -lt $max_attempts ]; do
    if _acquire_lock; then
        INBOX_CONTENT="$CONTENT" "$SCRIPT_DIR/.venv/bin/python3" -c "
import yaml, sys, os

try:
    # Load existing inbox
    with open('$INBOX') as f:
        documents = list(yaml.safe_load_all(f))

    # Repair legacy/orphan multi-document inboxes under the same write lock.
    # Preserve the exact pre-repair bytes once, then normalize every document
    # into the canonical top-level messages array before appending the new row.
    if len(documents) > 1:
        import datetime
        import shutil
        backup_suffix = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        shutil.copy2('$INBOX', f'$INBOX.automerge_{backup_suffix}')
        normalized_messages = []
        for document in documents:
            if not isinstance(document, dict):
                continue
            if isinstance(document.get('messages'), list):
                normalized_messages.extend(document['messages'])
                continue
            orphan = dict(document)
            orphan_content = orphan.pop('content', None)
            if orphan_content is None:
                body = orphan.pop('body', '')
                subject = orphan.pop('subject', '')
                orphan_content = body or subject
            normalized_messages.append({
                'id': orphan.get('id') or f'orphan_{len(normalized_messages) + 1}',
                'from': orphan.get('from', 'unknown'),
                'timestamp': orphan.get('timestamp', ''),
                'type': orphan.get('type', 'legacy_orphan'),
                'content': orphan_content,
                'read': bool(orphan.get('read', False)),
            })
        data = {'messages': normalized_messages}
    elif documents:
        data = documents[0]
    else:
        data = None

    # Initialize if needed
    if not data:
        data = {}
    if not data.get('messages'):
        data['messages'] = []

    # Add new message (content via env var to avoid quote injection)
    new_msg = {
        'id': '$MSG_ID',
        'from': '$FROM',
        'timestamp': '$TIMESTAMP',
        'type': '$TYPE',
        'content': os.environ.get('INBOX_CONTENT', ''),
        'read': False,
    }
    corr_val = '$CORRELATION_ID'
    if corr_val:
        new_msg['correlation_id'] = corr_val
    data['messages'].append(new_msg)

    # Overflow rotation (2026-08-03 委員長hotfix 裁定seq137748/137769):
    # 旧仕様は50便超で既読便を黙って恒久破壊していた(同日17+19便消失の実害)。
    # 破壊→回転: 溢れた既読便はper-agent archiveへ全量退避し、発動をstderrへlogする。
    if len(data['messages']) > 50:
        msgs = data['messages']
        unread = [m for m in msgs if not m.get('read', False)]
        read = [m for m in msgs if m.get('read', False)]
        dropped = read[:-30]
        if dropped:
            _adir = os.path.join(os.path.dirname(os.path.realpath('$INBOX')), '_archive')  # realpath: alias/実体のarchive二重化防止(a6指摘)
            os.makedirs(_adir, exist_ok=True)
            _abase = os.path.basename(os.path.realpath('$INBOX'))
            if _abase.endswith('.yaml'):
                _abase = _abase[:-5]
            _apath = os.path.join(_adir, _abase + '_pruned.yaml')
            with open(_apath, 'a', encoding='utf-8') as _af:
                yaml.safe_dump({'pruned_at': '$TIMESTAMP', 'count': len(dropped), 'messages': dropped}, _af, allow_unicode=True, default_flow_style=False)
                _af.write('---\n')
            print('[inbox_write] CAP_ROTATED: ' + str(len(dropped)) + ' read messages moved to ' + _apath, file=sys.stderr)
            # 永続log (2026-08-03 W67・a6提起「stderrのみで一過性」を受け、append-only・cap無し・既存archiveと同一realpath配下)
            _logpath = os.path.join(_adir, '_prune_events.log')
            with open(_logpath, 'a', encoding='utf-8') as _lf:
                _lf.write(f'$TIMESTAMP agent={_abase} pruned={len(dropped)} archive={_apath}\n')
        data['messages'] = unread + read[-30:]

    # Atomic write: tmp file + rename (prevents partial reads)
    # CRITICAL: dereference symlinks BEFORE atomic replace.
    # 2026-05-08 incident: queue/inbox/ split-brain. When INBOX was a symlink
    # (e.g. karo.yaml -> hideyoshi.yaml), os.replace replaced the SYMLINK ITSELF
    # with the tmp file, severing the alias and causing dual orphan files.
    # Fix: resolve to canonical path so writes always land on the real file
    # while symlink aliases remain intact.
    import tempfile, os
    inbox_canonical = os.path.realpath('$INBOX')
    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(inbox_canonical), suffix='.tmp')
    try:
        with os.fdopen(tmp_fd, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, indent=2, sort_keys=False)
        os.replace(tmp_path, inbox_canonical)
    except:
        os.unlink(tmp_path)
        raise

except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
"
        STATUS=$?
        _release_lock
        if [ $STATUS -eq 0 ]; then
            # ★ae8083dd★: 既存 caller は stdout 非捕捉確認済 (grep -rn "\$(.*inbox_write\.sh"
            # = 0件、27参照ファイル全て fire-and-forget 呼出し)。ack-retry engine の
            # Stage A 確認用グラウンディング値として MSG_ID/CORRELATION_ID を出力。
            echo "MSG_ID=$MSG_ID CORRELATION_ID=$CORRELATION_ID"
            exit 0
        fi
        attempt=$((attempt + 1))
        [ $attempt -lt $max_attempts ] && sleep 1
    else
        # Lock timeout
        attempt=$((attempt + 1))
        if [ $attempt -lt $max_attempts ]; then
            echo "[inbox_write] Lock timeout for $INBOX (attempt $attempt/$max_attempts), retrying..." >&2
            sleep 1
        else
            echo "[inbox_write] Failed to acquire lock after $max_attempts attempts for $INBOX" >&2
            exit 1
        fi
    fi
done
