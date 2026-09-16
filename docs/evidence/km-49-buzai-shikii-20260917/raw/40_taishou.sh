#!/bin/bash
# 40_taishou.sh ―― ㋒ ★恒真でない事★ の證。陽性四形(鳴らねばならぬ)・陰性四形(鳴つてはならぬ)。
# ★境は手で書かぬ★ ―― 閾−1 / 閾 / 閾+1 を ★器に作らせる★(MAXB から算く)。
# 砂場は ★員外★。走り終りに己が作つた物だけを名指しで消す(既存物には一指も触れぬ)。
# usage: bash 40_taishou.sh <砂場の根> <本器の path>
set -u
S="${1:?砂場の根が要る}"; MON="${2:?本器の path が要る}"
MAXB="${BUZAI_MAX_BYTES:-1048576}"
say(){ printf '%s\n' "$*"; }
[ -e "$S" ] && { printf '%s\n' "★砂場が既に在る(「'"$S"'」) ―― 上書かぬ(fail-closed)★" >&2; exit 3; }
mkdir -p "$S" || exit 3

SHITA=$((MAXB-1)); UE=$((MAXB+1))
say "刻 = $(date '+%Y-%m-%dT%H:%M:%S') / 部材閾 MAXB = ${MAXB}"
say "★境は器が算いた★ ―― 閾−1 = ${SHITA} / 閾 = ${MAXB} / 閾+1 = ${UE}"
say ""

tsukuru(){ python3 -c 'import sys;open(sys.argv[1],"wb").write(b"x"*int(sys.argv[2]))' "$1" "$2"; }

# ―― 八形を建てる(予言は建てる前に書く)
mkdir -p "$S/you1" "$S/you2" "$S/you3" "$S/you4" "$S/in1" "$S/in2" "$S/in3" "$S/in4"
tsukuru "$S/you1/chodo.bin"  "$MAXB"                      # 陽1 境上(-ge ゆゑ鳴る)
tsukuru "$S/you2/hitotsu_ue.bin" "$UE"                    # 陽2 境上一
tsukuru "$S/you3/futoi.bin"  "$((MAXB*3))"                # 陽3 第48弾の形
i=0; while [ "$i" -lt 30 ]; do tsukuru "$S/you3/chiisai_${i}.txt" 100; i=$((i+1)); done
tsukuru "$S/you4/futsuu.txt" 10                           # 陽4 止(FIFO を混ぜる)
mkfifo "$S/you4/tomari.fifo" || exit 3
tsukuru "$S/in1/hitotsu_shita.bin" "$SHITA"               # 陰1 境下一
i=0; while [ "$i" -lt 11 ]; do tsukuru "$S/in2/tsumi_${i}.bin" "$SHITA"; i=$((i+1)); done   # 陰2 ★積★
tsukuru "$S/in3/rei.txt" 0; tsukuru "$S/in3/ichi.txt" 1   # 陰3 零と一
tsukuru "$S/in4/a b.txt" 3; tsukuru "$S/in4/乙 丙.txt" 5  # 陰4 名に空白と多バイト

hitotsu(){ # <名> <期待rc> <dir> <予言>
  local na="$1" kitai="$2" d="$3" yogen="$4" rc
  find "$d" -mindepth 1 -print0 > "$S/argv.nul"
  BUZAI_MAX_BYTES="$MAXB" bash "$MON" --from0 < "$S/argv.nul" > "$S/o.txt" 2> "$S/e.txt"
  rc=$?
  say "―― ${na}(予言 rc=${kitai} ― ${yogen})"
  sed 's/^/     /' "$S/e.txt"
  if [ "$rc" -eq "$kitai" ]; then say "     ★判 = 合(實 rc=${rc})★"
  else say "     ★判 = ★外れ★(實 rc=${rc} ― 期待 ${kitai})★"; TAORE=$((TAORE+1)); fi
  say ""
}
TAORE=0
hitotsu "陽1 境上 ―― 丁度 ${MAXB} byte 一本" 1 "$S/you1" "-ge ゆゑ境そのものが鳴る"
hitotsu "陽2 境上一 ―― ${UE} byte 一本" 1 "$S/you2" "閾を一 byte 超えれば鳴る"
hitotsu "陽3 第48弾の形 ―― $((MAXB*3)) byte 一本 + 小 30 本" 1 "$S/you3" "束の和は束級閾 10485760 未満なるに部材が鳴る"
hitotsu "陽4 止 ―― FIFO を混ぜる" 1 "$S/you4" "開かずに NOTREG と見て『測れぬ』で鳴る(黙らぬ)"
hitotsu "陰1 境下一 ―― ${SHITA} byte 一本" 0 "$S/in1" "閾に一 byte 足らねば黙る"
hitotsu "陰2 ★積★ ―― ${SHITA} byte × 11 本(和 $((SHITA*11)))" 0 "$S/in2" "和は束級閾 10485760 を超ゆるに ★部材は一本も超えぬ★ ∴ 黙る ―― 之が『和の器の化身でない』證"
hitotsu "陰3 零と一 ―― 0 byte と 1 byte" 0 "$S/in3" "小さき物に鳴いてはならぬ"
hitotsu "陰4 名 ―― 「a b.txt」と「乙 丙.txt」" 0 "$S/in4" "空白と多バイトの名でも割れず黙る(母數 2)"

say "★倒れた形 = ${TAORE} / 8★"
[ "$TAORE" -eq 0 ] && say "★陰性は一形も鳴らず、陽性は四形とも鳴つた ―― 之は騒音でなく器である。★" \
  || say "★倒れが在る ―― 走りは残す(消さぬ)。★"

# ―― 砂場を畳む(己が作つた物だけを名指しで)
rm -f -- "$S/o.txt" "$S/e.txt" "$S/argv.nul" "$S/you1/chodo.bin" "$S/you2/hitotsu_ue.bin" \
  "$S/you3/futoi.bin" "$S/you4/futsuu.txt" "$S/you4/tomari.fifo" "$S/in1/hitotsu_shita.bin" \
  "$S/in3/rei.txt" "$S/in3/ichi.txt" "$S/in4/a b.txt" "$S/in4/乙 丙.txt"
i=0; while [ "$i" -lt 30 ]; do rm -f -- "$S/you3/chiisai_${i}.txt"; i=$((i+1)); done
i=0; while [ "$i" -lt 11 ]; do rm -f -- "$S/in2/tsumi_${i}.bin"; i=$((i+1)); done
rmdir "$S/you1" "$S/you2" "$S/you3" "$S/you4" "$S/in1" "$S/in2" "$S/in3" "$S/in4" "$S" 2>/dev/null
say "砂場 = 畳んだ(残りが在れば rmdir が黙つて拒む ∴ 次走で『既に在る』と倒れる)"
