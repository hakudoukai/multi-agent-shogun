#!/bin/bash
# ★送る器★(第55弾 ㋒ ―― 疵⑸ の直し)
# 作法⑷の順の ★⑤のみ★ を行ふ。★測らぬ・門を走らせぬ。★
#
# 呼ぶ器の usage(逐語・scripts/inbox_write.sh L3-L4 より):
#   bash scripts/inbox_write.sh <target_agent> <content> <type> <from>
#   ∴ 宛先=argv[1] 胴=argv[2] 型=argv[3] 差出=argv[4] ―― ★位置で受ける器★。名で渡すな。
#
# 使ひ方: bash ki/02_okuru.sh <型> <胴の紙...>
# ★門★: 呼ぶ前に ki/01_hakaru.sh が同じ紙へ通つて居る事を要求する(合図の札が要る)。
#   合図 = 環境変数 KM55_HAKATTA=1。立つて居らねば ★送らず rc=5★(fail-closed)。
#   ∴ 「測らずに送る」は器の側で塞がる ―― 第54弾で「人である」と書いた穴を、一枚だけ塞ぐ。
set -u
R=/Users/momizimac/multi-agent-shogun
PY=/opt/homebrew/bin/python3
if [ "${KM55_HAKATTA:-}" != "1" ]; then
  echo "★測りの合図が無い(KM55_HAKATTA≠1) ―― 送らぬ★" >&2; exit 5
fi
TYPE="$1"; shift
for f in "$@"; do
  body=$("$PY" -c 'import sys;print(open(sys.argv[1],encoding="utf-8").read().rstrip("\n"),end="")' "$f")
  bash "$R/scripts/inbox_write.sh" karo-mac "$body" "$TYPE" ashigaru-mac-2
  rc=$?
  echo "rc=$rc $f"
  [ "$rc" -eq 0 ] || exit "$rc"
done
