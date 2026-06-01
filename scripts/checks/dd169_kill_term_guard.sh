#!/usr/bin/env bash
#
# DD-169 D006 conditional exception — PreToolUse hook regex guard
# 副院長令 9cb98a5d+4f7d549e+1b7452cd (P2 副院長裁定 cycle3)
#
# 目的:
#   - Bash(kill -TERM:*) wildcard を「数値 PID 1 個」制約の代替として扱わない
#   - 厳格 regex `^kill -TERM ([0-9]+)$` のみ通す
#   - 通過時: ps -o pid,ppid,pgid,sid,stat,etime,comm,args -p <PID> 証跡を /tmp/dd169_audit_log/ に記録
#   - blocked 時: exit 2 (PreToolUse hook 中断) + 副院長 escalate handshake INSERT
#
# Codex cycle2 修正提案 (5) 反映 + Codex cycle3 残課題対応
#
set -uo pipefail

LOG_DIR="/tmp/dd169_audit_log"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date +%Y%m%d).log"

log() { printf '[%s] %s\n' "$(date -Is)" "$*" >> "$LOG_FILE"; }

# CLAUDE_TOOL_INPUT が kill 系コマンドでなければスルー
# (kill 単独 + pkill + killall + tmux kill-* 全件 catch、単語境界 \b は pkill 内 kill にマッチしないため別途列挙)
INPUT="${CLAUDE_TOOL_INPUT:-}"
if ! echo "$INPUT" | grep -qE '(^|[[:space:]])(kill|pkill|killall)([[:space:]]|$)|tmux[[:space:]]+kill-'; then
    exit 0
fi

# pkill / killall / tmux kill-server / tmux kill-session は例外対象外 deny
if echo "$INPUT" | grep -qE '(^|[[:space:]])(pkill|killall)([[:space:]]|$)|tmux[[:space:]]+kill-(server|session|pane)'; then
    log "BLOCKED non-graceful kill: $INPUT"
    echo '[DD-169 guard] BLOCKED: pkill/killall/tmux kill-server/tmux kill-session は例外対象外' >&2
    exit 2
fi

# kill -9 (= SIGKILL) も deny
if echo "$INPUT" | grep -qE '(^|[[:space:]])kill[[:space:]]+-9([[:space:]]|$)|(^|[[:space:]])kill[[:space:]]+-SIGKILL'; then
    log "BLOCKED kill -9 (SIGKILL): $INPUT"
    echo '[DD-169 guard] BLOCKED: kill -9 (SIGKILL) は例外対象外、graceful TERM のみ' >&2
    exit 2
fi

# kill -TERM <数値PID> 厳格 regex で通す
if echo "$INPUT" | grep -qE '^kill[[:space:]]+-TERM[[:space:]]+[0-9]+$'; then
    PID=$(echo "$INPUT" | grep -oE '[0-9]+$')
    if [ -z "$PID" ]; then
        log "PARSE_FAIL: PID 抽出失敗 input=$INPUT"
        exit 2
    fi
    PS_EVIDENCE=$(ps -o pid,ppid,pgid,sid,stat,etime,comm,args -p "$PID" 2>/dev/null)
    if [ -z "$PS_EVIDENCE" ]; then
        log "PID_NOT_FOUND: PID=$PID input=$INPUT"
        echo "[DD-169 guard] PID $PID not found, allowing graceful no-op" >&2
        exit 0
    fi
    log "ALLOWED kill -TERM PID=$PID"
    log "  ps_evidence: $(echo "$PS_EVIDENCE" | tail -n +2)"
    echo "[DD-169 guard] kill -TERM $PID allowed (証跡 /tmp/dd169_audit_log/)" >&2
    exit 0
fi

# kill コマンドだが上記 regex に該当しない (= wildcard・パターン kill・複数 PID 等)
log "BLOCKED non-conforming kill: $INPUT"
echo '[DD-169 guard] BLOCKED: kill コマンドは DD-169 例外条件 (^kill -TERM [0-9]+$ で 数値PID 1個) のみ許可' >&2
echo "[DD-169 guard]   入力: $INPUT" >&2
exit 2
