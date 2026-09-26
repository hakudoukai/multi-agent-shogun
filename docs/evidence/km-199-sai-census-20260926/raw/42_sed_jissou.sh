#!/bin/sh
# 旧 C（9/18 の README L27 逐語の sed）と新 C2 を、BSD sed で走らせる。入力 = raw/05 の実の送出行2件＋器 L335 の書式で組んだ親なし行1件（試料・便ではない）。
cd "$(dirname "$0")" || exit 9
date '+# 刻 %Y-%m-%dT%H:%M:%S%z'
for src in 05_sender_out/km200s3.out 05_sender_out/km200g.out 05_sender_out/km200r6k.out oyanashi; do
  if [ "$src" = oyanashi ]; then out='★karo-mac へ送出した★ seq=999001'; else out=$(cat "$src"); fi
  c=$(printf '%s\n' "$out" | sed -n 's/.*へ送出した★ seq=\([0-9]*\)（.*/\1/p')
  c2=$(printf '%s\n' "$out" | sed -n 's/.*へ送出した★ seq=\([0-9][0-9]*\).*/\1/p')
  echo "$src | 行=[$out] | C=[$c] | C2=[$c2]"
done
