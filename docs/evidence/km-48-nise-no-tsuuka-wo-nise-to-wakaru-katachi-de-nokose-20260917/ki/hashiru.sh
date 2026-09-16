#!/bin/bash
# hashiru.sh -- ★走らせ方を一本に据ゑる★(第48弾)。束の中の器。
#
# 何故:
#   ⑴ rc は ★管を通すと消える★ ―― `cmd | kaki` では $? が kaki の物に成る。
#      ∴ 先に file へ落し、rc を掴んでから kaki を通す。
#   ⑵ stderr を stdout へ混ぜぬ ―― 数へる file に混ぜれば行數が汚れる。
#   ⑶ 生の捕獲(素の `>`)は ★正規化を通らぬ★ ゆゑ、必ず 80_kaki.py を通してから殘す。
#   ⑷ 途中の生は ★束の中★ の .nama/ へ置き、kaki を通した後に消す(/tmp へは置かぬ)。
#
# 使ひ方: hashiru.sh <札名> <器…>
#   出す物: an/<札名>.out  an/<札名>.err  ―― rc は an/<札名>.out の末尾へ器が書く
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"
NA="$1"; shift
NAMA="$B/.nama"; mkdir -p "$NAMA"
"$@" >"$NAMA/o" 2>"$NAMA/e"
rc=$?
printf '\n★走の rc★ %d\n★走らせた★ %s\n' "$rc" "$*" >>"$NAMA/o"
/opt/homebrew/bin/python3 -B "$B/ki/80_kaki.py" "$B/an/$NA.out" --nushi "hashiru.sh:$NA" <"$NAMA/o"
/opt/homebrew/bin/python3 -B "$B/ki/80_kaki.py" "$B/an/$NA.err" --nushi "hashiru.sh:$NA" <"$NAMA/e"
rm -f "$NAMA/o" "$NAMA/e"; rmdir "$NAMA" 2>/dev/null
echo "== $NA rc=$rc"
exit "$rc"
