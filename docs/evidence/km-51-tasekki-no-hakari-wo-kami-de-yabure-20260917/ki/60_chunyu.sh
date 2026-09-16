#!/bin/bash
# 60_chunyu.sh ―― ★專任2 の直し紙(行注入封じ)を、當席の丙(safe_show)の知見で検める★
#   當席 第50弾 丙の限界: 「表示を潰すのみ・env の生値は改行を持つ」。
#   問: 同じ限界が專任2 の直しにも在るか。加へて tr '\n\r\t' '\266\215\211' が吐く byte は何か。
# 使ひ方: 60_chunyu.sh <作業dir>
set -u
WD="$1"; mkdir -p "$WD"
V=$(printf '50\n9999')
printf '#項\t出目\t判\n'

# ⑴ 直しの tr が吐く byte(逐byte)
OUT=$(printf '%s' "$V" | tr '\n\r\t' '\266\215\211')
printf '%s' "$OUT" > "$WD/naoshi_out.bin"
BY=$(od -An -tx1 < "$WD/naoshi_out.bin" | tr -s ' \n' ' ' | sed 's/^ //; s/ $//')
printf '⑴tr の出 byte列\t%s\t%s\n' "$BY" "$(printf '%s' "$OUT" | grep -c '' >/dev/null; echo 一行)"

# ⑵ 其の byte は妥当な UTF-8 か
U=$(python3 -c "
import sys
b=open(sys.argv[1],'rb').read()
try:
    s=b.decode('utf-8'); print('妥当\t文字=%r 字数=%d'%(s,len(s)))
except UnicodeDecodeError as e:
    print('★不当UTF-8★\t%s'%e)
" "$WD/naoshi_out.bin")
printf '⑵UTF-8 妥当性\t%s\n' "$U"
printf '⑶本来の ¶(U+00B6) の byte\t%s\t★tr の \\266 は 1byte・¶ は 2byte(c2 b6)★\n' \
  "$(printf '¶' | od -An -tx1 | tr -s ' \n' ' ' | sed 's/^ //; s/ $//')"

# ⑷ 當席の書き手(errors=strict)が其の行を読めるか ―― 束の紙は悉く此の器を通る
printf '[watcher] ★閾 T を比較器が扱へぬ(「%s」) ―― 既定 30 へ倒す★\n' "$OUT" > "$WD/nari_line.txt"
K=$(python3 -c "
import io,sys
try:
    io.open(sys.argv[1],encoding='utf-8',errors='strict').read(); print('読めた')
except Exception as e: print('★読めぬ: %s: %s★'%(type(e).__name__,e))
" "$WD/nari_line.txt")
printf '⑷strict な讀手\t%s\t%s\n' "$K" "$([ "${K#★}" = "$K" ] && echo - || echo '★直しが新たな疵を生む★')"

# ⑸ grep が其の行を文字と見るか binary と見るか
G=$(LC_ALL=en_US.UTF-8 grep -c '閾' "$WD/nari_line.txt" 2>&1); g_rc=$?
GB=$(LC_ALL=en_US.UTF-8 grep '閾' "$WD/nari_line.txt" 2>&1 | head -1 | cut -c1-40)
printf '⑸grep(UTF-8 locale)\t件=%s rc=%s 出=[%s]\t-\n' "$G" "$g_rc" "$GB"

# ⑹ ★共通の限界★: 直しても env の生値は改行を持つか
export T_X="$V"
RAW=$(bash -c 'printf "%s" "$T_X"' | od -An -tx1 | tr -s ' \n' ' ' | sed 's/^ //; s/ $//')
printf '⑹直し後も env の生値\t%s\t%s\n' "$RAW" \
  "$(printf '%s' "$V" | grep -c $'\n' >/dev/null; echo '★改行は env に残る=當席 丙 と同じ限界★')"

# ⑺ 陽性/陰性対照
P=$(printf '%s' "$V" | grep -c '')            # 注入形は2行
N=$(printf '%s' '30' | tr '\n\r\t' '\266\215\211' | grep -c '')
printf '⑺陽性:注入形の行数(直し前)\t%s\t★2 行=注入成立★\n' "$P"
printf '⑺陰性:清値30 を直しに通す\t%s\t行=%s(不変)\n' "$(printf '%s' '30' | tr '\n\r\t' '\266\215\211')" "$N"
