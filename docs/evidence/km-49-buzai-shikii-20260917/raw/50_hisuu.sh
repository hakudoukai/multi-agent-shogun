#!/bin/bash
# 50_hisuu.sh ―― ㋓ ★閾に數でない物を食はせる★。六形 + 未設定 + ★門を外した写し★。
# 出目は三つ ⑴鳴る(rc=1) ⑵黙る(rc=0) ⑶死ぬ(rc≧2 或いは shell が倒れる)。
# usage: bash 50_hisuu.sh <砂場の根> <本器の path>
set -u
S="${1:?砂場の根}"; MON="${2:?本器}"
[ -e "$S" ] && { printf '%s\n' "★砂場が既に在る ―― 上書かぬ(fail-closed)★" >&2; exit 3; }
mkdir -p "$S" || exit 3
python3 -c 'open("'"$S"'/rei.txt","wb").write(b"")'
python3 -c 'open("'"$S"'/chiisai.txt","wb").write(b"x"*100)'
# ★差し向けの先は歩き根の外へ★ ―― 「> は走る前に file を建てる」ゆゑ根の中に置けば己を数へる(51_hisuu_taoreta.out の疵)
NUL="${S}.nul"; ESA="${S}.kage"; mkdir -p "$ESA"
find "$S" -mindepth 1 -type f -print0 > "$NUL"
say(){ printf '%s\n' "$*"; }
say "刻 = $(date '+%Y-%m-%dT%H:%M:%S')"
say "餌 = 0 byte 一本 と 100 byte 一本(★既定の閾 1048576 の下では必ず黙る餌★ ∴ 鳴つたら閾の所為)"
say ""

# ★門を外した写し★ ―― is_num の一行だけを抜いた影武者(生器には一字も触れて居らぬ)
KAGE="$ESA/kage_mon.sh"
grep -v '^is_num "\$MAXB" ||' "$MON" > "$KAGE"
say "影武者 = is_num の検めを ★一行だけ★ 抜いた写し(差 = $(diff "$MON" "$KAGE" | grep -c '^<') 行)"
say ""

kuu(){ # <札> <値の見せ方> <器> <env の建て方>
  local fuda="$1" mise="$2" ki="$3" tate="$4" rc out
  out="$(eval "$tate bash '$ki' --from0 < '$NUL'" 2>&1)"; rc=$?
  local deme
  if   [ "$rc" -eq 0 ]; then deme="⑵黙る"
  elif [ "$rc" -eq 1 ]; then deme="⑴鳴る"
  else deme="⑶死ぬ(rc=${rc})"; fi
  say "―― ${fuda} : ${mise}"
  printf '%s\n' "$out" | sed 's/^/     /'
  say "     ★出目 = ${deme}(rc=${rc})★"
  say ""
}

kuu "① 空(設定して空)"   "BUZAI_MAX_BYTES=''"        "$MON" "BUZAI_MAX_BYTES=''"
kuu "①' 未設定"          "env -u BUZAI_MAX_BYTES"     "$MON" "env -u BUZAI_MAX_BYTES"
kuu "② 全角數字"         "BUZAI_MAX_BYTES=１０４８５７６" "$MON" "BUZAI_MAX_BYTES=１０４８５７６"
kuu "③ 1e9"              "BUZAI_MAX_BYTES=1e9"        "$MON" "BUZAI_MAX_BYTES=1e9"
kuu "④ 0x10"             "BUZAI_MAX_BYTES=0x10"       "$MON" "BUZAI_MAX_BYTES=0x10"
kuu "⑤ 負"               "BUZAI_MAX_BYTES=-1"         "$MON" "BUZAI_MAX_BYTES=-1"
kuu "⑥ 零"               "BUZAI_MAX_BYTES=0"          "$MON" "BUZAI_MAX_BYTES=0"
say "════ 影武者(門を外した写し)に同じ物を食はせる ════"
kuu "④影 0x10"           "BUZAI_MAX_BYTES=0x10"       "$KAGE" "BUZAI_MAX_BYTES=0x10"
kuu "②影 全角數字"       "BUZAI_MAX_BYTES=１０４８５７６" "$KAGE" "BUZAI_MAX_BYTES=１０４８５７６"
kuu "⑤影 負"             "BUZAI_MAX_BYTES=-1"         "$KAGE" "BUZAI_MAX_BYTES=-1"

rm -f -- "$S/rei.txt" "$S/chiisai.txt" "$NUL" "$KAGE"; rmdir "$S" "$ESA" 2>/dev/null
say "砂場 = 畳んだ"
