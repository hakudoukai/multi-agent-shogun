#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# fukuincho_detect_stale_cli.sh — 層① 検知 CLI entrypoint
# ═══════════════════════════════════════════════════════════════
# 設計章節正本: docs/08-ops/fukuincho-stage3-auto-loop-design.md §2
#   commit f1c268d (SHA256=fcf49731df98d812ad83a3d078e01afff306c13e6b867cbc033f3541ab95fb1b)
#   redo: subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_002
#         (gunshi-third RED-1 cure: 関数群 lib 化 + 本 CLI で arg dispatch 実 code 化)
#
# 用法:
#   bash scripts/fukuincho_detect_stale_cli.sh --detect-stale-handshake [--input <file>]
#   echo '<json_row>' | bash scripts/fukuincho_detect_stale_cli.sh --detect-stale-handshake
#
# 呼出経路: cron 60s polling から本 CLI を invoke。
#   crontab 例: */1 * * * * /path/to/scripts/fukuincho_detect_stale_cli.sh \
#                            --detect-stale-handshake --input /tmp/pc_handshake_pending.jsonl
#
# 入力フォーマット: 1 行 1 row の JSONL (pc_handshake row 表現)
#   各 row = { "correlation_id": "...", "status": "pending|in_progress|...",
#              "response_by_time": "ISO8601 or empty", "from": "...", ... }
# ═══════════════════════════════════════════════════════════════

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# lib を source (関数群を runtime に読込、RED-1 cure)
LIB_PATH="$SCRIPT_DIR/scripts/lib/detect_stale.sh"
if [ ! -f "$LIB_PATH" ]; then
    echo "[fukuincho_detect_stale_cli] FATAL: lib not found at $LIB_PATH" >&2
    exit 2
fi
# shellcheck disable=SC1090
source "$LIB_PATH"

# ─── arg dispatch (RED-1 cure: comment でなく実 code) ───
ACTION=""
INPUT_FILE=""
while [ $# -gt 0 ]; do
    case "$1" in
        --detect-stale-handshake)
            ACTION="detect_stale_handshake"
            shift
            ;;
        --input)
            INPUT_FILE="${2:-}"
            shift 2
            ;;
        --help|-h)
            cat <<EOF
fukuincho_detect_stale_cli.sh — 層① 検知 CLI

Usage:
  $0 --detect-stale-handshake [--input <file>]   # 標準入力 or file から JSONL 受領
  $0 --help                                       # 本 help を表示

Source for redo: subtask_thirdpc_p1_fukuincho_stage3_actual_impl_apply_redo_002
EOF
            exit 0
            ;;
        *)
            echo "[fukuincho_detect_stale_cli] unknown arg: $1" >&2
            exit 2
            ;;
    esac
done

if [ -z "$ACTION" ]; then
    echo "[fukuincho_detect_stale_cli] no action specified — use --detect-stale-handshake" >&2
    exit 2
fi

# ─── detect-stale-handshake dispatch ───
if [ "$ACTION" = "detect_stale_handshake" ]; then
    _detect_stale_log "INVOKE" "fukuincho_detect_stale_cli detect-stale-handshake start (pid=$$)"

    INPUT_CONTENT=""
    if [ -n "$INPUT_FILE" ]; then
        if [ ! -r "$INPUT_FILE" ]; then
            _detect_stale_log "ERROR" "input_file_not_readable: $INPUT_FILE"
            exit 2
        fi
        INPUT_CONTENT="$(cat "$INPUT_FILE")"
    else
        # stdin から
        INPUT_CONTENT="$(cat)"
    fi

    if [ -z "$INPUT_CONTENT" ]; then
        _detect_stale_log "WARN" "empty input — exit 0"
        exit 0
    fi

    # 1 行 1 row の JSONL 想定、各 row を評価
    PROCESSED=0
    ENQUEUED=0
    SKIPPED=0
    ANOMALIES=0

    while IFS= read -r row; do
        [ -z "$row" ] && continue
        PROCESSED=$((PROCESSED + 1))
        # detect_stale_evaluate_row: 0=enqueue 推奨, 1=skip, 2=anomaly
        # ★cycle4 fix1 (RED-C3 cure / CLI rc 破壊根治)★:
        #   script 冒頭 set -uo pipefail (★-e 未設定★) ゆえ command 失敗で exit せず、
        #   `|| true` は rc を常に 0 (true の rc) で上書きし case 0 enqueue 分岐を
        #   全 row に発火させる退行を生む (cycle3 fix5 で誤導入)。
        #   set -e 未設定下では `|| true` 不要、rc=$? で実 rc を直接捕捉する。
        detect_stale_evaluate_row "$row"
        rc=$?
        case "$rc" in
            0)
                # enqueue 推奨 — correlation_id + recipient を抽出して enqueue 呼出
                corr_raw=$(printf '%s' "$row" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("correlation_id",""))
except Exception: print("")' 2>/dev/null || echo "")
                recip=$(printf '%s' "$row" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("recipient","fukuincho"))
except Exception: print("fukuincho")' 2>/dev/null || echo "fukuincho")
                if detect_stale_enqueue "$corr_raw" "$recip" "確認依頼、コマンダーより"; then
                    ENQUEUED=$((ENQUEUED + 1))
                fi
                ;;
            1)
                SKIPPED=$((SKIPPED + 1))
                ;;
            2)
                ANOMALIES=$((ANOMALIES + 1))
                ;;
        esac
    done <<< "$INPUT_CONTENT"

    _detect_stale_log "INVOKE" "fukuincho_detect_stale_cli done processed=${PROCESSED} enqueued=${ENQUEUED} skipped=${SKIPPED} anomalies=${ANOMALIES}"
    exit 0
fi
