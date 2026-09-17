#!/usr/bin/env bash
# ★寫し★ 10_slice.py が scripts/stop_hook_inbox.sh から切り出した(手で書いて居らぬ)
set -euo pipefail
num_same_op() { [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }
# ★空文字は `:-` が黙つて呑む★ ―― 裁 seq322952 乙「未設定/空文字/空白のみを分け、既定へ倒す時は必ず刷る」
#   に依り、`:-` の前で「在るが空」を分けて刷る(未設定のみ黙る = 裁 seq323687⑵ 乙′・高頻度器の許し)。
if [ -n "${STOP_HOOK_STDIN_TIMEOUT+x}" ] && [ -z "$STOP_HOOK_STDIN_TIMEOUT" ]; then
    echo "[stop_hook] ★STOP_HOOK_STDIN_TIMEOUT が空文字 — 既定 10 へ倒す(fail-closed)★" >&2
fi
STOP_HOOK_STDIN_TIMEOUT="${STOP_HOOK_STDIN_TIMEOUT:-10}"
if ! num_same_op "$STOP_HOOK_STDIN_TIMEOUT"; then
    # ★乙(裁 seq323980⑵)★ 値を己の判定路へ刷る時、改行で ★偽の報せ行★ を生やさせぬ
    case "$STOP_HOOK_STDIN_TIMEOUT" in
        *␊*|*␍*|*␉*)
            echo "[stop_hook] ★STOP_HOOK_STDIN_TIMEOUT が可視印(␊␍␉)を既に含む — 値を刷らず既定 10 へ倒す(fail-closed・裁 seq323980⑵)★" >&2 ;;
        *)
            __th_vp="${STOP_HOOK_STDIN_TIMEOUT//$'\n'/␊}"; __th_vp="${__th_vp//$'\r'/␍}"; __th_vp="${__th_vp//$'\t'/␉}"
            echo "[stop_hook] ★STOP_HOOK_STDIN_TIMEOUT を比較器が扱へぬ(「${__th_vp}」) — 既定 10 へ倒す(fail-closed)★" >&2 ;;
    esac
    STOP_HOOK_STDIN_TIMEOUT=10
fi
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
#   ★訂(當席 2026-09-17 實測)★: 此の Mac に bash 5 は ★無い★(command -v bash=/bin/bash 3.2.57・
#   /opt/homebrew/bin/bash 不在) ∴ `env bash` も 3.2 へ解ける。上の「brew bash 5」は此の機では偽。
    #   ∴ rc だけに頼らず、★経過秒★ でも分ける。
    if [ "$__read_rc" -gt 128 ] || [ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]; then
        echo "[stop_hook] ★stdin 時限切れ(${STOP_HOOK_STDIN_TIMEOUT}秒経過・rc=${__read_rc}) — 讀めた ${#INPUT} 字で続行★" >&2
    fi
fi
printf "THRESHOLD=%s\n" "$STOP_HOOK_STDIN_TIMEOUT"
printf "INPUT_LEN=%s\n" "${#INPUT}"
