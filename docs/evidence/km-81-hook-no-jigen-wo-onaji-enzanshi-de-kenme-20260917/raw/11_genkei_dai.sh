#!/usr/bin/env bash
# ★寫し★ 10_slice.py が docs/evidence/km-81-hook-no-jigen-wo-onaji-enzanshi-de-kenme-20260917/_before/stop_hook_inbox.sh.snapshot から切り出した(手で書いて居らぬ)
set -euo pipefail
STOP_HOOK_STDIN_TIMEOUT="${STOP_HOOK_STDIN_TIMEOUT:-10}"
case "$STOP_HOOK_STDIN_TIMEOUT" in
    ''|*[!0-9]*)
        echo "[stop_hook] ★STOP_HOOK_STDIN_TIMEOUT が數でない(「${STOP_HOOK_STDIN_TIMEOUT}」) — 既定 10 へ倒す(fail-closed)★" >&2
        STOP_HOOK_STDIN_TIMEOUT=10 ;;
esac
INPUT=""
__stdin_t0=$SECONDS
if IFS= read -r -d '' -t "$STOP_HOOK_STDIN_TIMEOUT" INPUT; then
    :
else
    __read_rc=$?
    __stdin_el=$(( SECONDS - __stdin_t0 ))
    # ★実測(家老mac 2026-09-16)★: 此の Mac の /bin/bash は 3.2 ゆゑ
    #   `read -t` は★時限切れでも rc=1★ を返す(EOF と同じ出目)。
    #   rc>128 は bash 4 以降の形であり、shebang は env bash(=brew bash 5)だが
    #   呼び手が `/bin/bash <script>` なら 3.2 で走る ―― ★両方在り得る★。
    #   ∴ rc だけに頼らず、★経過秒★ でも分ける。
    if [ "$__read_rc" -gt 128 ] || [ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]; then
        echo "[stop_hook] ★stdin 時限切れ(${STOP_HOOK_STDIN_TIMEOUT}秒経過・rc=${__read_rc}) — 讀めた ${#INPUT} 字で続行★" >&2
    fi
fi
printf "THRESHOLD=%s\n" "$STOP_HOOK_STDIN_TIMEOUT"
printf "INPUT_LEN=%s\n" "${#INPUT}"
