#!/bin/bash
# ★寫し★ 對象= scripts/stop_hook_inbox.sh sha16= f1b49820e234a1ee / 刻= 2026-09-17T10:30:33+0900
# 以下 「番人域」「判定行」は對象から ★逐語で写した★。枝(見る/見ぬ)のみ本器が付す(宣)。
STOP_HOOK_STDIN_TIMEOUT='10'
# ---- 番人域(逐語 58〜77) ----
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
# ---- 番人域 了 ----
echo "番人の後の閾= [${STOP_HOOK_STDIN_TIMEOUT}]"
__read_rc=1
__stdin_el=10
[ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]
echo "閾比較の素 rc=$?"
# ---- 判定行(逐語 90) ----
    if [ "$__read_rc" -gt 128 ] || [ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]; then
    echo "★時限切れを見る(then へ入つた)★"
else
    echo "★時限切れを見ぬ(else へ落ちた ―― 危険側)★"
fi
exit 0
