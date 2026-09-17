#!/bin/bash
# ★寫し★ 對象= scripts/stop_hook_inbox.sh sha16= f1b49820e234a1ee / 刻= 2026-09-17T10:31:08+0900
# 番人域・判定行は對象から ★逐語で写した★。枝のみ本器が付す(宣)。
MASS_UNREAD_THRESHOLD='99999999999999999999'
UNREAD_COUNT='7'
# ---- 番人域(逐語 197〜213) ----
MASS_UNREAD_THRESHOLD=${MASS_UNREAD_THRESHOLD:-5}
# ★2026-09-16 非數の閾を塞ぐ(専任3 第39弾 の指摘・家老mac が code を讀んで確かめた)★
#   旧: 閾が數でないと `[ n -gt 非數 ]` は rc=2 を返し、`if` は之を「偽」と讀む。
#       `set -e` は if の條件には掛からぬ ∴ ★器は死なず、番人だけが黙る★。
#       結果 塞ぐ帯が [1,5] から ★[1,∞)★ へ開き、5/7 の自己増殖ループの防ぎが消える。
#       ―― 之は「赤が青に成る」でなく「番人が居らぬ事に誰も気付かぬ」形の疵である。
#   本形: 閾も數も先に検め、數でなければ ★既定へ倒して其の旨を言ふ(fail-closed・黙らぬ)★。
case "$MASS_UNREAD_THRESHOLD" in
    ''|*[!0-9]*)
        echo "[stop_hook] ★MASS_UNREAD_THRESHOLD が數でない(「${MASS_UNREAD_THRESHOLD}」) — 既定 5 へ倒す(fail-closed)★" >&2
        MASS_UNREAD_THRESHOLD=5 ;;
esac
case "${UNREAD_COUNT:-0}" in
    ''|*[!0-9]*)
        echo "[stop_hook] ★UNREAD_COUNT が數でない(「${UNREAD_COUNT:-}」) — 0 へ倒す(fail-closed)★" >&2
        UNREAD_COUNT=0 ;;
esac
# ---- 番人域 了 ----
echo "番人の後: MASS_UNREAD_THRESHOLD=[${MASS_UNREAD_THRESHOLD}] UNREAD_COUNT=[${UNREAD_COUNT}]"
[ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]
echo "閾比較の素 rc=$?"
# ---- 判定行(逐語 214) ----
if [ "${UNREAD_COUNT:-0}" -gt "$MASS_UNREAD_THRESHOLD" ]; then
    echo "★閾を越えたと見る(then へ入つた)★"
else
    echo "★閾を越えたと見ぬ(else へ落ちた)★"
fi
exit 0
