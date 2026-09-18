#!/bin/bash
# ★寫し★ 對象= docs/evidence/km-81-hook-no-jigen-wo-onaji-enzanshi-de-kenme-20260917/_before/stop_hook_inbox.sh.snapshot sha16= 42c83a9ab41c0166 / 刻= 2026-09-17T10:30:33+0900
# 以下 「番人域」「判定行」は對象から ★逐語で写した★。枝(見る/見ぬ)のみ本器が付す(宣)。
STOP_HOOK_STDIN_TIMEOUT='10'
# ---- 番人域(逐語 52〜59) ----
STOP_HOOK_STDIN_TIMEOUT="${STOP_HOOK_STDIN_TIMEOUT:-10}"
case "$STOP_HOOK_STDIN_TIMEOUT" in
    ''|*[!0-9]*)
        echo "[stop_hook] ★STOP_HOOK_STDIN_TIMEOUT が數でない(「${STOP_HOOK_STDIN_TIMEOUT}」) — 既定 10 へ倒す(fail-closed)★" >&2
        STOP_HOOK_STDIN_TIMEOUT=10 ;;
esac
INPUT=""
__stdin_t0=$SECONDS
# ---- 番人域 了 ----
echo "番人の後の閾= [${STOP_HOOK_STDIN_TIMEOUT}]"
__read_rc=1
__stdin_el=10
[ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]
echo "閾比較の素 rc=$?"
# ---- 判定行(逐語 70) ----
    if [ "$__read_rc" -gt 128 ] || [ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]; then
    echo "★時限切れを見る(then へ入つた)★"
else
    echo "★時限切れを見ぬ(else へ落ちた ―― 危険側)★"
fi
exit 0
