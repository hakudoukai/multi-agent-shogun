#!/usr/bin/env bash
# ★便を出す前に「己の弾が何を運ぶか」を測る器★(km-79→km-81 で二度踏んだ疵の直し)。
#   「据ゑた」と「commit した」は別物 ―― 控が main より進んで居れば、
#   己の弾の commit は ★前の round の未commit分を一緒に運ぶ★。
# 使ひ方: 70_zen_commit_kenme.sh <repo> <追跡path> <控path>
#   rc=0 : main⇔控 の差 0 行(己の弾のみを運ぶ)
#   rc=1 : ★差が在る★ ―― 紙と commit 文と便に ★断り★ を書かねばならぬ
set -u
R="$1"; P="$2"; H="$3"
M=$(mktemp); git -C "$R" show "main:$P" > "$M" 2>/dev/null || { echo "★main に $P が無い★" >&2; rm -f "$M"; exit 2; }
mm=$(grep -c '' "$M"); hh=$(grep -c '' "$H"); ii=$(grep -c '' "$R/$P")
d1=$(diff "$M" "$H" | grep -c '^[<>]'); d2=$(diff "$H" "$R/$P" | grep -c '^[<>]')
printf 'main=%s行 / 控=%s行 / 今=%s行\n' "$mm" "$hh" "$ii"
printf 'main⇔控 の相違行=%s(★前round の未commit分★) / 控⇔今 の相違行=%s(★本弾★)\n' "$d1" "$d2"
rm -f "$M"
[ "$d1" -eq 0 ] || { echo "★断り要★ 本弾の commit は前round の分も運ぶ" >&2; exit 1; }
echo "★清い★ 本弾のみを運ぶ"
