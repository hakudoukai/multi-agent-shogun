#!/bin/bash
# ★寫し器★ otsu_hook(型=乙) ―― 生器 scripts/stop_hook_inbox.sh の逐語切片。★生器へは一字も書いて居らぬ★
#   生器 sha16=f1b49820e234a1ee / 切り出した行域=52-93 / 作つた刻=2026-09-17T11:35:17+0900
#   生器と同じ shell 宣: set -euo pipefail
set -euo pipefail
# ===== 寫し ここから(生器 逐語・一字も違へず) =====
# ★甲(裁 seq322952)★ 閾は ★後で比べる時と同じ演算子★ で検めよ ―― 旧形の glob `*[!0-9]*` は
#   20桁の十進を「數」として通すが、下の `[ "$__stdin_el" -ge "$STOP_HOOK_STDIN_TIMEOUT" ]` は
#   2^63 超で rc=2 を返し ★黙つて else(時限切れを見ぬ側)へ落つる★。
#   加へて `read -t <20桁>` は bash に ★拒まれ(invalid timeout specification)★ ―― 實測(當席 2026-09-17):
#   rc=1・★讀めた字数 0★ ∴ hook 入力 JSON を ★丸ごと落として先へ進む★。而して上の rc=2 ゆゑ ★其の事を報せぬ★。
#   裁 seq324588⑴(最重)。兄弟器 scripts/redundancy/shogun_report_watcher.sh L63-69 と同形。
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
# ===== 寫し ここまで =====
# ===== 附録(當席が書いた駆動部・寫しに非ず) =====
__uke="${STOP_HOOK_STDIN_TIMEOUT-《受け皿が立たず》}"
__kbranch=UNRUN
# 下流は寫しの内(scripts/stop_hook_inbox.sh:78・90(寫しの内)) ―― read -r -d '' -t <閾> で stdin を待ち、経過秒を閾と比べる
__kbranch="讀めた字数=${#INPUT}"
__k3="${__read_rc-―}"   # read の rc(在る器のみ)
printf "RESULT\t%s\t%s\t%s\n" "$__uke" "$__kbranch" "$__k3"
