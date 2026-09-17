#!/bin/bash
# ★測る器★(第55弾 ㋒ ―― 疵⑸ の直し)
# 作法⑷の順「①便の胴 ②字数 ③凍結 ④門 ⑤送」の ★②のみ★ を行ふ。
# ★送らぬ。★ 呼んでも便は一通も出ぬ ―― 之が疵⑸(測ると送るが一つの呼び)の直しである。
#
# 使ひ方: bash ki/01_hakaru.sh <胴の紙...>
#   出: 一行毎に "<字数>\t<紙>" を stdout へ。300 超が一本でも在れば rc=3。
#   字は ★字(codepoint)★ で数へる ―― byte ではない(memory: macOS awk length() は byte を返す)。
set -u
PY=/opt/homebrew/bin/python3
rc=0
for f in "$@"; do
  if [ ! -f "$f" ]; then printf '★紙が無い★\t%s\n' "$f"; rc=4; continue; fi
  n=$("$PY" -c 'import sys;print(len(open(sys.argv[1],encoding="utf-8").read().rstrip("\n")))' "$f")
  printf '%s\t%s' "$n" "$f"
  if [ "$n" -gt 300 ]; then printf '\t★300超★'; rc=3; fi
  printf '\n'
done
exit "$rc"
