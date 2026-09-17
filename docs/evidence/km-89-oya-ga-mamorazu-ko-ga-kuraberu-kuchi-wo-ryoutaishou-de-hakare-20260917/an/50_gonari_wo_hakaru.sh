#!/usr/bin/env bash
# ★門 條④★ 出目を file へ落す時は必ず尾の空白を落とせ(printf の詰め物が尾に残る):
#   bash <此の器> | sed $'s/[ \t]*$//' > <raw/…>
# ★案の誤鳴りを実測する器★ ―― 同じ 19 組を案に通し、
#   正しい値を誤つて弾いた数(誤鳴り=false reject)と、毒を正しく弾いた数を分けて数へる。
set -uo pipefail
. "$(dirname "$0")/kazu_no_bannin.sh"

MIN=1; MAX=86400   # 1秒〜1日 ―― stale/poll の常識的な幅(案の値・議論の余地在り)
printf '%-18s %-24s %-10s %-9s %s\n' '組' '注いだ値(od 抜粋)' '案の出目' '採つた値' '案の言つた理由'
n_hajiku=0; n_toru=0
while IFS=$'\t' read -r label val; do
    # ★命令置換は尾の改行を食ふ★(疵③ 実測: 300\n が素通りし「通した」と出た)
    #   ∴ 番人を付けて後で剥ぐ ―― 之で尾の改行が案に当たる
    v=$(printf '%b#' "$val"); v=${v%#}
    [ "$val" = '<未設定>' ] && v=''
    err=$(kazu_no_bannin STALE_SEC "$v" 300 "$MIN" "$MAX" 2>&1 >/dev/null); rc_b=$?
    got=$(kazu_no_bannin STALE_SEC "$v" 300 "$MIN" "$MAX" 2>/dev/null); rc_g=$?
    if [ "$rc_g" -ne 0 ]; then deme='★弾いた'; n_hajiku=$((n_hajiku+1)); else deme='通した'; n_toru=$((n_toru+1)); fi
    printf '%-18s %-24s %-10s %-9s %s\n' "$label" "$(printf '%s' "$v" | od -An -c | head -1 | sed 's/^ *//; s/  */ /g')" \
        "$deme" "$got" "$(printf '%s' "$err" | sed 's/.*理由= //; s/★$//')"
done <<'TSV'
陰性_正常300_10	300
陰性_未設定	<未設定>
陽性_空
陽性_空白のみ
陽性_0	0
陽性_-1	-1
陽性_abc	abc
陽性_300abc	300abc
陽性_010	010
陽性_+10	+10
陽性_4294967295	4294967295
陽性_4294967296	4294967296
陽性_2p63m1	9223372036854775807
陽性_改行尾	300\n
追加_改行中	3\n0
追加_前後空白	 300
追加_下線	1_0
追加_0x10	0x10
追加_全角300	３００
TSV
printf '\n―― 案の数: ★弾いた=%d / 通した=%d / 計=%d★ (min=%s max=%s)\n' "$n_hajiku" "$n_toru" $((n_hajiku+n_toru)) "$MIN" "$MAX"
