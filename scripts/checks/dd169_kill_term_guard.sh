#!/usr/bin/env bash
#
# DD-169 D006 conditional exception — PreToolUse hook regex guard
# 副院長令 9cb98a5d+4f7d549e+1b7452cd (P2 副院長裁定 cycle3)
# + Commander 副院長令 db560a15 + 9ad453ae §4 (P0 cycle4 stdin JSON 公式仕様準拠化)
#
# 目的:
#   - Bash(kill -TERM:*) wildcard を「数値 PID 1 個」制約の代替として扱わない
#   - 厳格 regex `^kill -TERM ([0-9]+)$` のみ通す
#   - 通過時: ps -o pid,ppid,pgid,sid,stat,etime,comm,args -p <PID> 証跡を /tmp/dd169_audit_log/ に記録
#   - blocked 時: exit 2 (PreToolUse hook 中断) + 副院長 escalate handshake INSERT
#
# cycle4 修正 (stdin JSON 公式仕様準拠 + 対称 fail-secure):
#   - Claude Code 公式 PreToolUse hook 仕様 = stdin JSON 入力 (= env var CLAUDE_TOOL_INPUT 依存禁)
#   - 不明入力 (parse fail / command 空) は ALLOW せず exit 2 (= 対称 fail-secure 原則)
#   - jq missing env (本家 SC) のため python3 で JSON parse (= 同等性能、本家標準 retain)
#
# Codex cycle2 修正提案 (5) 反映 + Codex cycle3 残課題対応 + cycle4 fail-open 真因解消
#
set -uo pipefail

LOG_DIR="/tmp/dd169_audit_log"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date +%Y%m%d).log"

log() { printf '[%s] %s\n' "$(date -Is)" "$*" >> "$LOG_FILE"; }

# 公式 PreToolUse hook 仕様: stdin JSON 入力 retain (= env var 依存禁、cycle3 fail-open 真因解消)
# JSON 構造: {"tool_input": {"command": "..."}} ほか. .tool_input.command を抽出。
INPUT_JSON=$(cat)
COMMAND=$(printf '%s' "$INPUT_JSON" | python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print(d.get('tool_input', {}).get('command', ''), end='')
except Exception:
    sys.exit(1)
" 2>/dev/null)
PYTHON_RC=$?

# JSON parse 失敗 or command 空 = 不明入力 → fail-secure (exit 2)、ALLOW 不可
if [ "$PYTHON_RC" -ne 0 ] || [ -z "$COMMAND" ]; then
    log "PARSE_FAIL: stdin JSON parse 失敗 or command 空 (python_rc=$PYTHON_RC) input=$INPUT_JSON"
    echo '[DD-169 guard] BLOCKED: stdin JSON parse 失敗 or .tool_input.command 空 (対称 fail-secure)' >&2
    exit 2
fi

# kill 系コマンドでなければスルー
# (kill 単独 + pkill + killall + tmux kill-* 全件 catch、単語境界 \b は pkill 内 kill にマッチしないため別途列挙)
if ! echo "$COMMAND" | grep -qE '(^|[[:space:]])(kill|pkill|killall)([[:space:]]|$)|tmux[[:space:]]+kill-'; then
    exit 0
fi

# pkill / killall / tmux kill-server / tmux kill-session / tmux kill-pane は例外対象外 deny
if echo "$COMMAND" | grep -qE '(^|[[:space:]])(pkill|killall)([[:space:]]|$)|tmux[[:space:]]+kill-(server|session|pane)'; then
    log "BLOCKED non-graceful kill: $COMMAND"
    echo '[DD-169 guard] BLOCKED: pkill/killall/tmux kill-server/tmux kill-session は例外対象外' >&2
    exit 2
fi

# kill -9 (= SIGKILL) も deny
if echo "$COMMAND" | grep -qE '(^|[[:space:]])kill[[:space:]]+-9([[:space:]]|$)|(^|[[:space:]])kill[[:space:]]+-SIGKILL'; then
    log "BLOCKED kill -9 (SIGKILL): $COMMAND"
    echo '[DD-169 guard] BLOCKED: kill -9 (SIGKILL) は例外対象外、graceful TERM のみ' >&2
    exit 2
fi

# kill -TERM <数値PID> 厳格 regex で通す
if echo "$COMMAND" | grep -qE '^kill[[:space:]]+-TERM[[:space:]]+[0-9]+$'; then
    PID=$(echo "$COMMAND" | grep -oE '[0-9]+$')
    if [ -z "$PID" ]; then
        log "PARSE_FAIL: PID 抽出失敗 input=$COMMAND"
        exit 2
    fi
    PS_EVIDENCE=$(ps -o pid,ppid,pgid,sid,stat,etime,comm,args -p "$PID" 2>/dev/null)
    if [ -z "$PS_EVIDENCE" ]; then
        log "PID_NOT_FOUND: PID=$PID input=$COMMAND"
        echo "[DD-169 guard] PID $PID not found, allowing graceful no-op" >&2
        exit 0
    fi
    log "ALLOWED kill -TERM PID=$PID"
    log "  ps_evidence: $(echo "$PS_EVIDENCE" | tail -n +2)"
    echo "[DD-169 guard] kill -TERM $PID allowed (証跡 /tmp/dd169_audit_log/)" >&2
    exit 0
fi

# kill コマンドだが上記 regex に該当しない (= wildcard・パターン kill・複数 PID 等)
log "BLOCKED non-conforming kill: $COMMAND"
echo '[DD-169 guard] BLOCKED: kill コマンドは DD-169 例外条件 (^kill -TERM [0-9]+$ で 数値PID 1個) のみ許可' >&2
echo "[DD-169 guard]   入力: $COMMAND" >&2
exit 2
