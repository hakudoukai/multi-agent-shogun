#!/bin/bash
# 50_nul.sh ―― ★「測れぬ1(㋐22 NUL=execve死)」を別路から測る★
#   專任2 の宣: 「番人の前で execve(2) が死ぬ ∴ 番人は見て居らぬ・測れぬ」。
#   問: env 以外の路(file / stdin / 命令置換)なら同じ値が番人へ届くか。届くなら何に化けるか。
# 使ひ方: 50_nul.sh <番人片path> <作業dir>
set -u
KATA="$1"; WD="$2"; mkdir -p "$WD"
. "$KATA"
printf '#路\t入れた物(byte列)\t番人へ届いた値(byte列)\t長さ_byte\trc\t判\n'

sho(){ printf '%s' "$1" | od -An -tx1 | tr -d '\n' | sed 's/  */ /g; s/^ //; s/ $//'; }

# ―― 路① env(execve 直) ―― python から NUL 入りの値を渡せるか
p1=$(python3 - <<'PY' 2>&1
import os
try:
    os.execve('/bin/sh', ['/bin/sh','-c','echo reached'], {'V':'50\x009999'})
except Exception as e:
    print('%s: %s' % (type(e).__name__, e))
PY
); r1=$?
printf '①env(execve直)\t35 30 00 39 39 39 39\t―(到達せず)\t―\t%s\t★%s★\n' "$r1" "$p1"

# ―― 路② file → 命令置換 ――
printf '50\x009999' > "$WD/nul.bin"; ir=$?
v2=$(cat "$WD/nul.bin" 2>/dev/null); r2=$?
printf '②file→$(cat)\t35 30 00 39 39 39 39\t%s\t%s\t%s\t%s\n' "$(sho "$v2")" "${#v2}" "$r2" \
  "$([ "$v2" = '509999' ] && echo '★NUL が黙つて消え 50 と 9999 が連結★' || echo "受=[$v2]")"

# ―― 路③ file → read ――
IFS= read -r v3 < "$WD/nul.bin"; r3=$?
printf '③file→read\t35 30 00 39 39 39 39\t%s\t%s\t%s\t%s\n' "$(sho "$v3")" "${#v3}" "$r3" \
  "$([ "$v3" = '509999' ] && echo '★NUL が黙つて消え連結★' || echo "受=[$v3]")"

# ―― 路④ 番人へ実際に通す(路②の値で) ――
export T_NUL="$v2"
fix_threshold T_NUL 30 T_NUL 2>"$WD/nul_nari.txt"; r4=$?
nari=$(grep -c '' "$WD/nul_nari.txt")
printf '④番人へ通す(②の値)\t―\t%s\t%s\t%s\t%s\n' "$(sho "$T_NUL")" "${#T_NUL}" "$r4" \
  "$([ "$nari" -eq 0 ] && echo "★黙つて通つた=受[$T_NUL]★" || echo "鳴=$nari 行 受[$T_NUL]")"

# ―― 陽性対照: NUL 無しの同じ二数 ――
printf '509999' > "$WD/plain.bin"; v5=$(cat "$WD/plain.bin")
printf '陽性:NUL無 509999\t35 30 39 39 39 39\t%s\t%s\t0\t%s\n' "$(sho "$v5")" "${#v5}" \
  "$([ "$v5" = "$v2" ] && echo '★路②の値と byte 一致=NUL は痕跡を残さぬ★' || echo 不一致)"
# ―― 陰性対照: 清い値 ――
v6=$(printf '30'); export T_OK="$v6"; fix_threshold T_OK 30 T_OK 2>"$WD/ok_nari.txt"
printf '陰性:清値30\t33 30\t%s\t%s\t0\t鳴=%s 受=%s\n' "$(sho "$T_OK")" "${#T_OK}" "$(grep -c '' "$WD/ok_nari.txt")" "$T_OK"
