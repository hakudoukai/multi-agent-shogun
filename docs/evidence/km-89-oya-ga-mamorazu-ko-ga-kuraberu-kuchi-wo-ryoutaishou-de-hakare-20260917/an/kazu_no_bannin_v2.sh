#!/usr/bin/env bash
# ★km-89 直し案の写し v2★ (v1 + 未設定/空は log を鳴らさぬ) ―― ★生器へは一字も据ゑて居らぬ(scope_in⑸「紙にのみ」)★
# 親(pane_enter_watcher_supervisor.sh)の L50/L52 の手前に置く番人。
#
# 條:
#   ⑴ 十進の數字のみ(先頭 + - 全角 空白 改行 下線 0x を悉く弾く)
#   ⑵ ★桁で先に弾く★ ―― [ -lt ] は 2^63 以上で rc=2 を返し ★else 側へ落ちて fail-open する★
#      (memory: 「[ ] reads 010 as decimal」「Falling to a default can create a fail-open」)
#   ⑶ 先頭 0 (010 等) は ★人が八進と読み得る★ ゆゑ弾く ―― 意図の食ひ違ひを黙つて飲まぬ
#   ⑷ 範囲 [min,max] の外は既定へ倒す
#   ⑸ 倒した時は必ず ★log へ理由を記す(no-silent-failure)★
set -uo pipefail

kazu_no_bannin() {   # $1=名 $2=生値 $3=既定 $4=最小 $5=最大  → stdout に採つた値
    local na="$1" v="$2" kitei="$3" min="$4" max="$5" riyuu=''
    if [ -z "$v" ]; then
        # ★v2 の差★: 未設定/空 は生器が己の註(L13/L14)で宣する既定の路である。
        #   之に log を鳴らすと ★正常起動毎に警が出る= 狼少年★ ゆゑ黙つて倒す。
        #   (v1 実測: 19 組の内 2 組が此の口 ―― 是が案自身の誤鳴りであつた)
        printf '%s' "$kitei"; return 2
    elif case "$v" in *[!0-9]*) true;; *) false;; esac; then
        riyuu='十進の數字以外の字を含む'
    elif [ "${#v}" -gt "${#max}" ]; then
        riyuu="桁が最大値 $max より多い(★[ -lt ] は 2^63 以上で rc=2 ∴ 桁で先に弾く★)"
    elif [ "${#v}" -gt 1 ] && [ "${v#0}" != "$v" ]; then
        riyuu='先頭 0(人が八進と読み得る)'
    elif [ "$v" -lt "$min" ]; then
        riyuu="最小 $min 未満"
    elif [ "$v" -gt "$max" ]; then
        riyuu="最大 $max 超"
    fi
    if [ -n "$riyuu" ]; then
        printf '[BANNIN] ★閾 %s=%s を採らず既定 %s へ倒す ―― 理由= %s★\n' \
            "$na" "$(printf '%s' "$v" | od -c -A n | tr -s ' ' | head -3 | tr '\n' ' ')" \
            "$kitei" "$riyuu" >&2
        printf '%s' "$kitei"; return 1
    fi
    printf '%s' "$v"; return 0
}
