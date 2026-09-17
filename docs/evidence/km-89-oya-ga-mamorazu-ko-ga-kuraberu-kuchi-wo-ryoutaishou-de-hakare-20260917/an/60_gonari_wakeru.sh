#!/usr/bin/env bash
# ★門 條④★ 出目を file へ落す時は必ず尾の空白を落とせ(printf の詰め物が尾に残る):
#   bash <此の器> | sed $'s/[ \t]*$//' > <raw/…>
# ★案 v2 の鳴りを分類する器★ ―― 「弾いた」と「鳴つた(log)」は別の数である。
set -uo pipefail
. "$(dirname "$0")/kazu_no_bannin_v2.sh"
MIN=1; MAX=86400
n_h=0; n_t=0; n_nari=0; n_shizuka=0
printf '%-18s %-9s %-7s %-9s %s\n' '組' '出目' 'log鳴' '採つた値' '誤鳴りか(當席の断)'
while IFS=$'\t' read -r label val kind; do
    # ★疵④★ IFS=$'\t' は TAB も「IFS 空白」ゆゑ ★連続 TAB の空欄を潰す★。
    #   空欄を素で置くと次の欄(註の字)が val へ入り、「空」の組に別の毒を食はせて居た(実測)。
    #   ∴ 空は札 <空> で表し、此処で実の空へ戻す。
    v=$(printf '%b#' "$val"); v=${v%#}
    case "$val" in '<未設定>'|'<空>') v='';; esac
    err=$(kazu_no_bannin STALE_SEC "$v" 300 "$MIN" "$MAX" 2>&1 >/dev/null)
    got=$(kazu_no_bannin STALE_SEC "$v" 300 "$MIN" "$MAX" 2>/dev/null); rc=$?
    if [ "$rc" -eq 0 ]; then deme='通した'; n_t=$((n_t+1)); else deme='★弾いた'; n_h=$((n_h+1)); fi
    if [ -n "$err" ]; then nari='鳴'; n_nari=$((n_nari+1)); else nari='黙'; n_shizuka=$((n_shizuka+1)); fi
    printf '%-18s %-9s %-7s %-9s %s\n' "$label" "$deme" "$nari" "$got" "$kind"
done <<'TSV'
陰性_正常300_10	300	否 ―― 正しく通つた
陰性_未設定	<未設定>	否 ―― 宣された既定の路(v2 で黙つた)
陽性_空	<空>	否 ―― 同上(親の :- と同じ出目)
陽性_空白のみ	 	否 ―― 現行は子が落ちて死 loop、案は倒して生かす
陽性_0	0	否 ―― ★現行は 1 秒で Enter 発火(誤爆)★
陽性_-1	-1	否 ―― 同上
陽性_abc	abc	否 ―― 現行は死 loop
陽性_300abc	300abc	否 ―― 現行は死 loop
陽性_010	010	否 ―― 現行は黙つて 10(人の読み 8 と食ひ違ふ)
陽性_+10	+10	★是が誤鳴り★ ―― 人の意図 10 が 300 へ倒れる(現行は 10 で通る)
陽性_4294967295	4294967295	★是が誤鳴り候★ ―― 巨大値で「事実上無効化」して居た運用を 300 へ戻す
陽性_4294967296	4294967296	★同上★
陽性_2p63m1	9223372036854775807	★同上★(但し現行も POLL では OSError で落ちる)
陽性_改行尾	300\n	否 ―― 現行は黙つて 300(見えぬ字が通る)
追加_改行中	3\n0	否 ―― 現行は死 loop
追加_前後空白	 300 	否 ―― 現行は黙つて 300(見えぬ字が通る)
追加_下線	1_0	否 ―― 現行は黙つて 10(人は數と読まぬ)
追加_0x10	0x10	否 ―― 現行は死 loop
追加_全角300	３００	否 ―― 現行は黙つて 300(全角が通る)
TSV
printf '\n―― 案 v2 の数: ★弾いた=%d / 通した=%d / log 鳴つた=%d / 黙つた=%d / 計=%d★\n' \
    "$n_h" "$n_t" "$n_nari" "$n_shizuka" $((n_h+n_t))
printf '―― ★誤鳴り(當席の断)= 1 確 (+10) + 3 候 (巨大値 3 組) / 19 組★\n'
