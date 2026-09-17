#!/bin/bash
# ★8形の負テスト ―― 台を8通の環境で走らせ rc/出値/報せ行/偽行/注入痕 を出す★
#   ★己の檢出子の疵(一度目に踏んだ)★: 「偽行=『★閾』で起らぬ行」と数へると、
#   注入する側が「★閾…」を騙つた時に ★偽行=0★ と出る。∴ 偽行は ★字面でなく期待行数の差★ で数へる。
#     期待 = 倒す形は1行・通る形(⑤)は0行。偽行 = 実際の行数 − 期待。
#   注入痕 = 値に埋めた合言葉 KM79_INJECTED を含む stderr 行の数(0 が正)。
set -u
H="$1"
run(){ # $1=形名 $2=set/unset $3=値 $4=期待報せ行
  local name="$1" mode="$2" val="${3-}" exp="$4" o e rc n_all n_inj n_false
  o="$(mktemp)"; e="$(mktemp)"
  if [ "$mode" = unset ]; then env -u KM79_PROBE bash "$H" >"$o" 2>"$e"; rc=$?
  else KM79_PROBE="$val" bash "$H" >"$o" 2>"$e"; rc=$?; fi
  n_all=$(grep -c '' "$e"); n_inj=$(grep -c 'KM79_INJECTED' "$e"); n_false=$((n_all - exp))
  printf '%s\trc=%s\t出値=%s\t報せ行=%s(期待%s)\t偽行=%s\t注入痕=%s\n' \
    "$name" "$rc" "$(tr '\n' '/' <"$o")" "$n_all" "$exp" "$n_false" "$n_inj"
  sed 's/^/    stderr| /' "$e"
  rm -f "$o" "$e"
}
run "①未設定"       unset ""                        1
run "②空文字"       set   ""                        1
run "③空白のみ"     set   "   "                     1
run "④全角空白"     set   "　"                      1
run "⑤正の數(77)"   set   "77"                      0
run "⑥20桁(2^63超)" set   "99999999999999999999"    1
run "⑦改行注入"     set   "$(printf '50\n★閾 KM79_INJECTED ―― 偽の行である★')" 1
run "⑧印を既に含む" set   "5␊0"                     1
