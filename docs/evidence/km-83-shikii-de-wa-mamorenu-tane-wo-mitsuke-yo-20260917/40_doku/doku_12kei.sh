#!/bin/bash
# doku_12kei.sh ―― 十二形の毒を一つの口へ当て、内/外を分けて刷る共通器。
# 用法: doku_12kei.sh <口名> <走らせる命令...>   (命令は毒を env で受ける)
set -u
VAR="$1"; shift
D=40_doku/_cell; mkdir -p "$D"
nm(){ case "$1" in 1)echo 未設定;;2)echo 空文字;;3)echo 空白のみ;;4)echo 0;;5)echo 1;;6)echo 2;;
 7)echo 01;;8)echo +1;;9)echo -1;;10)echo 20桁;;11)echo 非數;;12)echo 改行入り;; esac; }
printf '%-8s %-5s %-38s %s\n' 毒形 rc "内(器の報せ・一行目)" "外(interpreter の悲鳴・一行目)"
printf '%s\n' "----------------------------------------------------------------------------------------------"
for i in $(seq 1 12); do
  f="$D/${VAR}_$(printf '%02d' "$i")"
  case "$i" in
    1) env -u "$VAR" "$@" >"$f.out" 2>"$f.err";;
    2) env "$VAR=" "$@" >"$f.out" 2>"$f.err";;
    3) env "$VAR= " "$@" >"$f.out" 2>"$f.err";;
    4) env "$VAR=0" "$@" >"$f.out" 2>"$f.err";;
    5) env "$VAR=1" "$@" >"$f.out" 2>"$f.err";;
    6) env "$VAR=2" "$@" >"$f.out" 2>"$f.err";;
    7) env "$VAR=01" "$@" >"$f.out" 2>"$f.err";;
    8) env "$VAR=+1" "$@" >"$f.out" 2>"$f.err";;
    9) env "$VAR=-1" "$@" >"$f.out" 2>"$f.err";;
    10) env "$VAR=99999999999999999999" "$@" >"$f.out" 2>"$f.err";;
    11) env "$VAR=abc" "$@" >"$f.out" 2>"$f.err";;
    12) _v=$'1\n'; env "$VAR=$_v" "$@" >"$f.out" 2>"$f.err";;   # ★代入で ANSI-C 展開してから渡す★
  esac
  rc=$?
  uchi=$(head -1 "$f.out" 2>/dev/null); [ -z "$uchi" ] && uchi="(無)"
  soto=$(grep -E '^[A-Za-z_.]*(Error|Exception)' "$f.err" 2>/dev/null | head -1)
  [ -z "$soto" ] && soto=$(head -1 "$f.err" 2>/dev/null)
  [ -z "$soto" ] && soto="(無)"
  printf '%-8s %-5s %-38s %s\n' "$(nm $i)" "$rc" "$uchi" "$soto"
done
