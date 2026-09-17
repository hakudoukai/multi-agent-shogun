#!/bin/bash
# 50_mon_jissou.sh ―― 門(inbox_write.sh)の実走。IW_NAME_TEST_ONLY=1 ゆゑ門を通つた所で止まり箱を書かぬ(L75)。
# 五対照: ①読点名 ②空白名 ③未知名 ④生 pane 名(karo-mac) ⑤pane 無だが箱有の名(karo) ⑥IW_ALLOW_NAME 迂回
OUT="$1"; IW=scripts/inbox_write.sh
before=$(ls -1 queue/inbox/*.yaml | shasum -a 256 | cut -c1-16); before_n=$(ls -1 queue/inbox/*.yaml | wc -l | tr -d ' ')
run(){ tag="$1"; shift; env IW_NAME_TEST_ONLY=1 "$@" bash $IW 2>"$OUT/50_${tag}.err" >"$OUT/50_${tag}.out"; rc=$?; echo "$rc" > "$OUT/50_${tag}.rc"; printf '%s rc=%s out=%s err1=%s\n' "$tag" "$rc" "$(head -1 "$OUT/50_${tag}.out")" "$(head -1 "$OUT/50_${tag}.err" | cut -c1-90)"; }
# 引数は run の後ろに env 指定を置けぬ形なので個別に
IW_NAME_TEST_ONLY=1 bash $IW "karo-mac,gunshi-mac" x t f >"$OUT/50_1_touten.out" 2>"$OUT/50_1_touten.err"; echo $? > "$OUT/50_1_touten.rc"
IW_NAME_TEST_ONLY=1 bash $IW "karo mac" x t f >"$OUT/50_2_kuuhaku.out" 2>"$OUT/50_2_kuuhaku.err"; echo $? > "$OUT/50_2_kuuhaku.rc"
IW_NAME_TEST_ONLY=1 bash $IW "km97-michinai-na" x t f >"$OUT/50_3_michi.out" 2>"$OUT/50_3_michi.err"; echo $? > "$OUT/50_3_michi.rc"
IW_NAME_TEST_ONLY=1 bash $IW "karo-mac" x t f >"$OUT/50_4_pane.out" 2>"$OUT/50_4_pane.err"; echo $? > "$OUT/50_4_pane.rc"
IW_NAME_TEST_ONLY=1 bash $IW "karo" x t f >"$OUT/50_5_hako_nomi.out" 2>"$OUT/50_5_hako_nomi.err"; echo $? > "$OUT/50_5_hako_nomi.rc"
IW_NAME_TEST_ONLY=1 IW_ALLOW_NAME="km97 実走対照・箱は書かぬ" bash $IW "km97-michinai-na" x t f >"$OUT/50_6_allow.out" 2>"$OUT/50_6_allow.err"; echo $? > "$OUT/50_6_allow.rc"
IW_NAME_TEST_ONLY=1 bash $IW "gunshi-mac" x t f >"$OUT/50_7_shibako.out" 2>"$OUT/50_7_shibako.err"; echo $? > "$OUT/50_7_shibako.rc"
after=$(ls -1 queue/inbox/*.yaml | shasum -a 256 | cut -c1-16); after_n=$(ls -1 queue/inbox/*.yaml | wc -l | tr -d ' ')
{ for t in 1_touten 2_kuuhaku 3_michi 4_pane 5_hako_nomi 6_allow 7_shibako; do printf '%s\trc=%s\tstdout=%s\tstderr1=%s\n' "$t" "$(cat $OUT/50_$t.rc)" "$(head -1 $OUT/50_$t.out)" "$(head -1 $OUT/50_$t.err | cut -c1-100)"; done
  printf '箱の名列 sha16 前=%s(%s本) 後=%s(%s本) 同=%s\n' "$before" "$before_n" "$after" "$after_n" "$([ "$before" = "$after" ] && echo yes || echo NO)"
  printf '刻=%s 門sha=%s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$(shasum -a 256 $IW | cut -c1-16)"; } | tee "$OUT/50_summary.txt"
