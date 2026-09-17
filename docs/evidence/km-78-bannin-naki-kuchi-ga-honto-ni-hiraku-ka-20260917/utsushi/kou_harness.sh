#!/bin/bash
# 甲の写し(第56弾 km-78 ㋒)= scripts/stop_hook_inbox.sh の ★52-73 行 逐語★
#   + 出目を刷る末尾一行のみ。生器へは一字も書いて居らぬ(逐語 diff = utsushi/kou_diff.txt rc 0)。
# ★.first の疵★: 初走は 52-72 で切り、73 行目の fi を落とし ★構文誤りで一度も走らなんだ★。
#   rc=2 が 16 走 悉く同じだつたのが其の徴である(陽性対照も鳴らなんだ=器の壊れ)。
set -u
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
printf "OUT	INPUT_len=%s	el=%s	read_rc=%s	TMO=%s
" "${#INPUT}" "${__stdin_el:--}" "${__read_rc:--}" "$STOP_HOOK_STDIN_TIMEOUT"
