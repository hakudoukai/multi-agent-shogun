#!/bin/bash
# 05_ki.sh ―― ★本弾の器の本体(唯一の写し)★。10/20/30 は悉く此れを source する。
# ★手前で折り返す抜け道を作らぬ為に、器を二度書かぬ。★ 對照も本文も同じ此の函を通る。
# ★束の中の器である ―― 生器(scripts/ ・~/bin ・hook ・settings)へは一字も据ゑて居らぬ。★

# ── is_num ―― ★生器の字句そのものの写し★(50 番の器が sha16 で突き合はせる)
is_num(){ case "${1:-}" in (''|*[!0-9]*) return 1 ;; (*) return 0 ;; esac }

# ── 器A ―― 三態を分ける(㋐)
#   ${X+SET} は ★設定の有無★ のみ見る(値を見ぬ)。${X-} は ★未設定でも落ちぬ★。
#   ∴ 此の二つで 未設定 / 空文字 / 空白のみ / 中身在り を分けられる。
#   rc: 0=中身在りで數 / 1=中身在りだが數でない / 2=空白のみ / 3=空文字 / 4=未設定
#   出目(stdout): "<態>\t<生値の byte>\t<分かれた所>"
tai_wake(){
  local n="$1" sonzai raw tai wakare b
  eval "sonzai=\${$n+SET}"
  eval "raw=\${$n-}"
  b=$(printf '%s' "$raw" | wc -c | tr -d ' ')
  if [ -z "${sonzai:-}" ]; then
    tai=未設定;   wakare='${X+SET} が空'
    printf '%s\t%s\t%s' "$tai" "$b" "$wakare"; return 4
  fi
  if [ -z "$raw" ]; then
    tai=空文字;   wakare='${X+SET}=SET 且つ ${X-} が零長'
    printf '%s\t%s\t%s' "$tai" "$b" "$wakare"; return 3
  fi
  case "$raw" in
    (*[!' 	']*) tai=中身在り; wakare='空白以外の字を含む' ;;
    (*)           tai=空白のみ; wakare='字は在るが悉く ASCII 空白(SP/TAB)'
                  printf '%s\t%s\t%s' "$tai" "$b" "$wakare"; return 2 ;;
  esac
  # ★空を既定で埋めずに is_num へ ★届かせる★
  if is_num "$raw"; then printf '%s\t%s\t%s' "$tai" "$b" "$wakare"; return 0; fi
  printf '%s\t%s\t%s' "$tai" "$b" "$wakare"; return 1
}

# ── 器B ―― 閾が「數であるが無意味」でないかを判ずる(㋑)
#   rc: 0=有意 / 1=數でない(is_num が拒む) / 2=★恒真★ゆゑ拒む / 3=★算が届かぬ★ / 4=実質恒真(警)
shikii_yuui(){
  local v="${1-}"
  if ! is_num "$v"; then printf '數でない'; return 1; fi
  if [ "$v" -eq 0 ] 2>/dev/null; then printf '★恒真★(-ge の下で 0 は全ての byte和 を鳴らす)'; return 2; fi
  if ! [ "$v" -ge 0 ] 2>/dev/null; then printf '★算が届かぬ★(is_num は通したが [ -ge ] が落ちた)'; return 3; fi
  if [ "$v" -le 1 ] 2>/dev/null; then printf '★実質恒真★(1 は 0byte 以外の悉くを鳴らす)'; return 4; fi
  printf '有意'; return 0
}

# ── 生器 karo_mac_dasumae_gate.sh:196 の判の写し(㋑ の陽性対照に使ふ)
jou5(){ if [ "$1" -ge "$2" ] 2>/dev/null; then printf '鳴'; else printf '通'; fi; }
