#!/bin/bash
# ㋒ ★恒真でない證★ ―― 陽性(鳴るべき)・陰性(鳴らぬべき)を各3形以上、★悉く器を通す★。
#   ★手前で折り返す抜け道を作らぬ★: 對照は本文と ★同じ函★(raw/05_ki.sh)と ★同じ生門★ を通る。
#   ★零長の比較は偽の通過である★ ゆゑ、通した物の ★byte 数★ を悉く併せ書く。
#   砂場は ★員外★。己が作つた物だけを名指しで畳む。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"     # repo 根
. "$HERE/05_ki.sh"
S="$HERE/../sunaba"
MON="$ROOT/scripts/checks/karo_mac_dasumae_gate.sh"

[ -e "$S" ] && { printf '★砂場が既に在る ―― 上書かぬ(fail-closed)★\n' >&2; exit 3; }
mkdir -p "$S" || exit 3
[ -f "$MON" ] || { printf '★生門が無い: %s★\n' "$MON" >&2; exit 3; }

printf '刻 = %s\n' "$(date '+%Y-%m-%dT%H:%M:%S')"
printf '生門 = %s (%s byte)\n' "$MON" "$(wc -c < "$MON" | tr -d ' ')"
TAORE=0
KEI=0; YOU=0; INN=0; DOKU=0; HOKA=0   # ★母數は器が数へる(手で書かぬ)★

# ═══ 一 器A(tai_wake) ―― 陽性4形・陰性3形 ═══════════════════════
printf '\n═══ 一 器A tai_wake(㋐) ―― 陽性4形(鳴るべき)・陰性3形(鳴らぬべき) ═══\n'
a_hitotsu(){ # <名> <期待rc> <設定の仕方>  ※設定は eval で当てる
  local na="$1" kitai="$2" how="$3" o rc b
  eval "$how"
  o=$(tai_wake Z); rc=$?
  b=$(printf '%s' "$o" | cut -f2)
  printf '  %-34s 通した byte=%-3s 期待rc=%s 實rc=%s 態=%s  ' "$na" "$b" "$kitai" "${rc}" "${o%%	*}"
  KEI=$((KEI+1))
  case "$na" in (陽*) YOU=$((YOU+1)) ;; (陰*) INN=$((INN+1)) ;; (毒*) DOKU=$((DOKU+1)) ;; (*) HOKA=$((HOKA+1)) ;; esac
  if [ "$rc" -eq "$kitai" ]; then printf '★合★\n'; else printf '★外れ★\n'; TAORE=$((TAORE+1)); fi
}
printf ' ―― 陽性(is_num へ屆いて鳴るべき物)\n'
a_hitotsu '陽1 未設定'            4 'unset Z || true'
a_hitotsu '陽2 空文字'            3 'Z=""'
a_hitotsu '陽3 空白のみ(SP)'      2 'Z=" "'
a_hitotsu '陽4 數でない(abc)'     1 'Z="abc"'
printf ' ―― 陰性(黙つて通るべき物)\n'
a_hitotsu '陰1 數(4096)'          0 'Z="4096"'
a_hitotsu '陰2 數(0) ★零も數ゆゑ通る★' 0 'Z="0"'
a_hitotsu '陰3 數(10485760)'      0 'Z="10485760"'

# ═══ 二 器B(shikii_yuui) ―― 陽性4形・陰性3形 ════════════════════
printf '\n═══ 二 器B shikii_yuui(㋑) ―― 陽性4形(拒むべき)・陰性3形(通すべき) ═══\n'
b_hitotsu(){ # <名> <期待rc> <値>
  local na="$1" kitai="$2" v="$3" o rc b
  o=$(shikii_yuui "$v"); rc=$?
  b=$(printf '%s' "$v" | wc -c | tr -d ' ')
  printf '  %-30s 値「%s」 通した byte=%-3s 期待rc=%s 實rc=%s  ' "$na" "$v" "$b" "$kitai" "${rc}"
  KEI=$((KEI+1))
  case "$na" in (陽*) YOU=$((YOU+1)) ;; (陰*) INN=$((INN+1)) ;; (毒*) DOKU=$((DOKU+1)) ;; (*) HOKA=$((HOKA+1)) ;; esac
  if [ "$rc" -eq "$kitai" ]; then printf '★合★\n'; else printf '★外れ★\n'; TAORE=$((TAORE+1)); fi
}
printf ' ―― 陽性(拒むべき物)\n'
b_hitotsu '陽1 零'           2 '0'
b_hitotsu '陽2 負'           1 '-5'
b_hitotsu '陽3 極大(2^63)'   3 '9223372036854775808'
b_hitotsu '陽4 空文字'       1 ''
printf ' ―― 陰性(通すべき物)\n'
b_hitotsu '陰1 二'           0 '2'
b_hitotsu '陰2 現行閾'       0 '10485760'
b_hitotsu '陰3 2^63-1'       0 '9223372036854775807'

# ═══ 三 ★生門へ屆かせる★ ―― 紙の對照 陽性3形・陰性3形 ═══════
printf '\n═══ 三 ★生門 karo_mac_dasumae_gate.sh へ屆かせる★ ―― 紙 陽性3形・陰性3形 ═══\n'
printf '  ★此処が第49弾で落ちた穴である(對照が門に屆かぬ儘「9/9通つた」)。本弾は悉く門を通す。★\n'
printf '%b' '見出し行 \n本文行(末尾空白)   \n最終行。\n' > "$S/p1_matsubi.md"
printf '%b' '見出し行\r\n本文行\r\n最終行。\r\n'           > "$S/p2_cr.md"
printf '%b' '見出し行\n本文行\n最終行。\n\n\n'             > "$S/p3_eof.md"
printf '%b' '見出し行\n本文行\n最終行。\n'                 > "$S/n1_kiyoi.md"
printf '%b' '見出し行\n乙丙丁の行\n最終行。\n'             > "$S/n2_tabyte.md"
printf '%b' '見出し行\n本文行\n最終行。\n'                 > "$S/n3 na ni kuuhaku.md"

m_hitotsu(){ # <名> <期待rc> <file> <環境>
  local na="$1" kitai="$2" f="$3" env="$4" rc b out
  b=$(wc -c < "$f" | tr -d ' ')
  out=$(env $env bash "$MON" -- "$f" 2>&1); rc=$?
  printf '  %-40s 通した byte=%-4s 期待rc=%s 實rc=%s  ' "$na" "$b" "$kitai" "${rc}"
  KEI=$((KEI+1))
  case "$na" in (陽*) YOU=$((YOU+1)) ;; (陰*) INN=$((INN+1)) ;; (毒*) DOKU=$((DOKU+1)) ;; (*) HOKA=$((HOKA+1)) ;; esac
  if [ "$rc" -eq "$kitai" ]; then printf '★合★\n'; else printf '★外れ★\n'; TAORE=$((TAORE+1)); fi
  printf '%s\n' "$out" | sed 's/^/       │ /'
}
printf ' ―― 陽性(門が鳴るべき紙)\n'
m_hitotsu '陽1 末尾空白'   1 "$S/p1_matsubi.md" 'X=1'
m_hitotsu '陽2 CR混入'     1 "$S/p2_cr.md"      'X=1'
m_hitotsu '陽3 EOF空行'    1 "$S/p3_eof.md"     'X=1'
printf ' ―― 陰性(門が黙るべき紙)\n'
m_hitotsu '陰1 清い紙'     0 "$S/n1_kiyoi.md"   'X=1'
m_hitotsu '陰2 多バイト'   0 "$S/n2_tabyte.md"  'X=1'
m_hitotsu '陰3 名に空白'   0 "$S/n3 na ni kuuhaku.md" 'X=1'

# ═══ 四 ★閾の毒★ ―― 同じ清い紙へ、閾だけを変へて當てる ══════
printf '\n═══ 四 ★閾の毒★ ―― 陰1(清い紙・%s byte)は変へず、★閾だけ★を変へる ═══\n' "$(wc -c < "$S/n1_kiyoi.md" | tr -d ' ')"
printf '  ★此の段の「期待rc」は ★現行の器がかう出ると予言した値★ であつて ★あるべき値ではない★。★\n'
printf '  ★合 は「予言が當たつた」の意である。★健かである の意ではない。★ 二つを下に分けて書く。\n'
doku(){ # <名> <予言rc> <あるべきrc> <健否 ka|hi> <環境> <言>
  m_hitotsu "$1" "$2" "$S/n1_kiyoi.md" "$5"
  if [ "$4" = ka ]; then printf '       └ あるべきrc=%s ―― ★健か★。%s\n' "$3" "$6"
  elif [ "$2" -ne "$3" ]; then printf '       └ あるべきrc=%s なるに現行は rc=%s ―― ★疵(fail-open)★。%s\n' "$3" "$2" "$6"
  else printf '       └ あるべきrc=%s で rc は合ふ ―― ★然し健かではない(rc では表せぬ疵)★。%s\n' "$3" "$6"; fi
}
doku '毒1 閾=0(恒真)'              1 1 ka 'DASUMAE_MAX_BYTES=0'                   '閾0 は恒真ゆゑ鳴るのが正しい(但し閾其の物が無意味 ―― 器Bが rc=2 で拒む)。'
doku '毒2 閾=2^63(★算が届かぬ★)'  0 1 hi 'DASUMAE_MAX_BYTES=9223372036854775808' '[ -ge ] が rc=2 で落ち、if が偽を受け ★「閾未満」と刷つて通した★。'
doku '毒3 閾=abc(★止血済★)'       0 0 ka 'DASUMAE_MAX_BYTES=abc'                 '既定へ倒し ★倒した事を言つた★ ―― 之が正しき形。'
doku '毒4 閾=空文字(★:- が食ふ★)' 0 0 hi 'DASUMAE_MAX_BYTES='                    '既定へ倒れたが ★一言も言はぬ★。値は正しいが ★出目が「検めて通した」と同じ顔をする★ ―― ★㋐の穴の生器版★。'

# ★疵 50-F の直し ―― 走一は母數「21」を ★手で書いて★ 居た。實は 24 形。
# ★本弾が咎めて居る当の病(器の通らぬ數)を、己の器が持つて居た。★
# ★走一の出目は 31_taishou.tesho.out に残す ―― 消さぬ。★
printf '\n★形の數(★器が数へた★) 陽性=%s 陰性=%s 毒=%s 他=%s ―― 計 %s 形★\n' \
  "${YOU}" "${INN}" "${DOKU}" "${HOKA}" "${KEI}"
printf '★倒れた形 = %s / %s★\n' "${TAORE}" "${KEI}"
if [ "$TAORE" -eq 0 ]; then printf '★陽性は悉く鳴り、陰性は一形も鳴らなんだ ―― 之は騒音でなく器である。★\n'
else printf '★倒れが在る ―― 走りは残す(消さぬ)。★\n'; fi

rm -f -- "$S/p1_matsubi.md" "$S/p2_cr.md" "$S/p3_eof.md" "$S/n1_kiyoi.md" "$S/n2_tabyte.md" "$S/n3 na ni kuuhaku.md"
rmdir "$S" 2>/dev/null
if [ -e "$S" ]; then printf '★砂場が畳めなんだ(残りが在る) ―― 次走は「既に在る」で倒れる★\n'; else printf '砂場 = 畳んだ\n'; fi
