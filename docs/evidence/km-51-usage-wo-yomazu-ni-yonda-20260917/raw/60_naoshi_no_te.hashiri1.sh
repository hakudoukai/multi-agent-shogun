#!/bin/bash
# ★㋔★ 甲(2^63 の fail-open)／乙(空の閾の黙り)の改めを ★束の中の写しへ★ 当てて実演する。
#   ★生器(scripts/checks/karo_mac_dasumae_gate.sh)へは一字も書かぬ。★ 写しを作り、写しを直し、写しを走らす。
#   出す物: 61_mon_saki.sh(前の写し・逐語) / 62_mon_ato.sh(後) / 63_naoshi.diff / 本 out
set -u
REPO=/Users/momizimac/multi-agent-shogun
NAMA="$REPO/scripts/checks/karo_mac_dasumae_gate.sh"
HERE="$(cd "$(dirname "$0")" && pwd)"
SAKI="$HERE/61_mon_saki.sh"; ATO="$HERE/62_mon_ato.sh"; DIF="$HERE/63_naoshi.diff"

echo "=== 0. 基点と生器 ==="
echo "  生器 = $NAMA"
echo "  生器 sha256 = $(shasum -a 256 "$NAMA" | cut -d' ' -f1)"
echo "  生器 行数   = $(grep -c '' "$NAMA")"
cp "$NAMA" "$SAKI"
echo "  写し(前) = raw/61_mon_saki.sh  sha256 = $(shasum -a 256 "$SAKI" | cut -d' ' -f1)"
echo "  ★写した直後の sha が生器と一致するか★ = $( [ "$(shasum -a 256 "$NAMA"|cut -d' ' -f1)" = "$(shasum -a 256 "$SAKI"|cut -d' ' -f1)" ] && echo 一致 || echo ★不一致★ )"

echo
echo "=== 1. 改めを写しへ当てる(python・見つからねば落とす) ==="
/opt/homebrew/bin/python3 - "$SAKI" "$ATO" <<'PY'
import sys
saki, ato = sys.argv[1], sys.argv[2]
s = open(saki, encoding="utf-8").read()

# ---- 改め 乙 ---- 既定へ倒した事を「言ふ」(毒3 と同じ形)。MAXB の値は一切変へぬ。
otsu_saki = 'is_num "$MAXB" || { printf \'%s\\n\' "★閾 DASUMAE_MAX_BYTES が數でない(「${MAXB}」) ―― 既定 10485760 へ倒す(fail-closed)★" >&2; MAXB=10485760; }\n'
otsu_ato = otsu_saki + '''# ★改め 乙(第50弾 提案 → 第51弾 で現物化)★ ―― ★倒した事を言へ★
#   由来: L20 `${DASUMAE_MAX_BYTES:-10485760}` は ★未設定★ も ★空文字★ も黙つて食ふ。
#         値は正しく既定へ倒れる。★然し一言も言はぬ★ ―― 「検めて通した」と同じ顔をする(第50弾 毒4)。
#   本形は ★言葉だけを足す★。MAXB の値には一指も触れて居らぬ(∴ 閾の意味は不変)。
#   可逆: 下の if 一塊(5行)を消せば旧挙動。
if [ -z "${DASUMAE_MAX_BYTES+SET}" ]; then
  say "條⑤ 閾 = 既定 ${MAXB}(DASUMAE_MAX_BYTES ★未設定★)"
elif [ -z "${DASUMAE_MAX_BYTES-}" ]; then
  say "★閾 DASUMAE_MAX_BYTES が ★空文字★(設定は在るが値が無い) ―― 既定 ${MAXB} を用ゐる(fail-closed)★"
fi
'''
assert s.count(otsu_saki) == 1, "乙: 当て先が %d 箇所" % s.count(otsu_saki)
s = s.replace(otsu_saki, otsu_ato)

# ---- 改め 甲 ---- 比べる前に ★同じ演算子で★ 閾を検める。rc=2(器の誤り)だけを捕へる。
kou_saki = '  if [ "$total" -ge "$MAXB" ]; then\n'
kou_ato = '''  # ★改め 甲(第50弾 提案 → 第51弾 で現物化)★ ―― 比べる前に ★同じ `[ ]` で★ 閾を検める
  #   由来: MAXB が 2^63 以上だと `[ -ge ]` が ★rc=2(器の誤り)★ で落ち、if が其れを ★偽★ と受けて ★通した★。
  #         (第50弾 毒2: `line 194: [: 9223372036854775808: integer expression expected` を刷りつつ ★門 通 rc=0★)
  #   ★rc=1(偽)は捕へぬ★ ―― 負の閾は旧来通り「總て鳴る」(fail-closed)の儘。捕へるのは ★rc>=2 だけ★。
  #   ∴ 出目が変るのは ★旧版が器の誤りを刷つて居た態★ に限られる(下の㋔-⑷ 不変表)。
  #   可逆: 下の 6 行を `if [ "$total" -ge "$MAXB" ]; then` 一行へ戻せば旧挙動。
  local maxb_rc
  [ "$MAXB" -ge 0 ] 2>/dev/null; maxb_rc=$?
  if [ "$maxb_rc" -ge 2 ]; then
    say "★閾 DASUMAE_MAX_BYTES が 「[ ]」 で比べられぬ(「${MAXB}」・rc=${maxb_rc}) ―― 既定 10485760 へ倒す(fail-closed)★"
    MAXB=10485760
  fi
  if [ "$total" -ge "$MAXB" ]; then
'''
assert s.count(kou_saki) == 1, "甲: 当て先が %d 箇所" % s.count(kou_saki)
s = s.replace(kou_saki, kou_ato)
open(ato, "w", encoding="utf-8").write(s)
print("  当て終り: raw/62_mon_ato.sh を書いた")
PY
rc=$?; echo "  python rc=$rc"; [ $rc -eq 0 ] || exit 1
chmod +x "$ATO"
echo "  写し(後) sha256 = $(shasum -a 256 "$ATO" | cut -d' ' -f1)  行数 = $(grep -c '' "$ATO")"
echo "  ★生器は触れて居らぬか★ 生器 sha256(再測) = $(shasum -a 256 "$NAMA" | cut -d' ' -f1)"

echo
echo "=== 2. ⑴ 逐語 前/後(diff -u) ==="
diff -u "$SAKI" "$ATO" > "$DIF"; echo "  diff rc=$?(1=差在り が正)  → raw/63_naoshi.diff  行数 = $(grep -c '' "$DIF")"
cat "$DIF"

echo
echo "=== 3. ⑵ bash -n(構文検め) ==="
for f in "$SAKI" "$ATO" "$NAMA"; do
  o=$(bash -n "$f" 2>&1); r=$?
  echo "  bash -n $(basename "$f")  rc=$r  出目=「${o:-(空)}」"
done

echo
echo "=== 4. 對照の前拵へ(束の中に 36byte の紙を作る) ==="
FX="$HERE/.taishou_36.txt"
printf 'ashigaru-mac-2 km-51 taishou fixture\n' > "$FX"
echo "  $FX  寸法=$(stat -f %z "$FX") byte  末尾=$(tail -c1 "$FX"|xxd -p)"

# hashiru <札> <閾の態> <器> <file...>  ―― 門を一度走らせ、rc と 條⑤ の行を刷る
hashiru(){
  local fuda="$1" tai="$2" ki="$3"; shift 3
  local out rc jou5
  case "$tai" in
    (MISET) out=$(env -u DASUMAE_MAX_BYTES bash "$ki" -- "$@" 2>&1); rc=$? ;;
    (*)     out=$(DASUMAE_MAX_BYTES="$tai" bash "$ki" -- "$@" 2>&1); rc=$? ;;
  esac
  jou5=$(printf '%s\n' "$out" | grep '條⑤ 寸法' | head -1)
  local koe; koe=$(printf '%s\n' "$out" | grep -c '倒す\|用ゐる\|integer expression\|閾 = 既定')
  printf '  [%s] %s rc=%s\n' "$fuda" "$(basename "$ki")" "$rc"
  printf '      條⑤ 行 = 「%s」\n' "${jou5:-(條⑤ の行が出ぬ)}"
  printf '      閾に就いて口を利いた行 = %s 行\n' "$koe"
  printf '%s\n' "$out" | grep '倒す\|用ゐる\|integer expression\|閾 = 既定\|門 通\|門が落ちた' | sed 's/^/      ／ /'
}

echo
echo "=== 5. ⑶ 對照 甲 ―― 閾 2^63(第50弾 毒2 の形)／紙 36byte ==="
echo "  ★陽性(誤形)★ 閾=9223372036854775808"
hashiru 陽性前 9223372036854775808 "$SAKI" "$FX"
hashiru 陽性後 9223372036854775808 "$ATO"  "$FX"
echo "  ★陰性(正形)★ 閾=10485760(既定と同値)"
hashiru 陰性前 10485760 "$SAKI" "$FX"
hashiru 陰性後 10485760 "$ATO"  "$FX"

echo
echo "=== 6. ⑶ 對照 甲(現物で ★鳴らす★) ―― byte和 が閾を超える紙で、fail-open を目に見せる ==="
BIG="$HERE/.taishou_10mb.txt"
yes 'x' 2>/dev/null | head -c 10485761 > "$BIG"
printf '\n' >> "$BIG"
echo "  拵へた紙 $BIG 寸法=$(stat -f %z "$BIG") byte(閾 10485760 を超える)"
echo "  ★之が要である★: 閾=2^63 の時 前の門は ★byte和が幾らでも鳴かぬ★。後の門は既定へ倒れて ★鳴る★。"
hashiru 陽性前・大 9223372036854775808 "$SAKI" "$BIG"
hashiru 陽性後・大 9223372036854775808 "$ATO"  "$BIG"
echo "  ★陰性(正形・大)★ 閾=10485760 ―― 前も後も同じく鳴らねばならぬ"
hashiru 陰性前・大 10485760 "$SAKI" "$BIG"
hashiru 陰性後・大 10485760 "$ATO"  "$BIG"
rm -f "$BIG"; echo "  (10MB の紙は消した ―― 束へ残さぬ。拵へ方は本 script の中に在る)"

echo
echo "=== 7. ⑶ 對照 乙 ―― 空の閾の黙り(第50弾 毒4 の形)／紙 36byte ==="
echo "  ★陽性(空文字)★"
hashiru 陽性前 "" "$SAKI" "$FX"
hashiru 陽性後 "" "$ATO"  "$FX"
echo "  ★陽性(未設定)★"
hashiru 陽性前 MISET "$SAKI" "$FX"
hashiru 陽性後 MISET "$ATO"  "$FX"
echo "  ★陰性(値在り 4096)★ ―― 新しい行が出ては ならぬ"
hashiru 陰性前 4096 "$SAKI" "$FX"
hashiru 陰性後 4096 "$ATO"  "$FX"

echo
echo "=== 8. ⑷ ★閾の意味が変つて居らぬ★ 證 ―― 態 十通を前後で当て、出目を並べる ==="
printf '  %-22s | %-4s | %-4s | %-38s | %s\n' 態 前rc 後rc 前の條⑤ 後の條⑤
printf '  %s\n' "-----------------------+------+------+----------------------------------------+---------------------------"
kurabe(){
  local na="$1" tai="$2" o1 r1 o2 r2 j1 j2
  case "$tai" in
    (MISET) o1=$(env -u DASUMAE_MAX_BYTES bash "$SAKI" -- "$FX" 2>&1); r1=$?
            o2=$(env -u DASUMAE_MAX_BYTES bash "$ATO"  -- "$FX" 2>&1); r2=$? ;;
    (*)     o1=$(DASUMAE_MAX_BYTES="$tai" bash "$SAKI" -- "$FX" 2>&1); r1=$?
            o2=$(DASUMAE_MAX_BYTES="$tai" bash "$ATO"  -- "$FX" 2>&1); r2=$? ;;
  esac
  j1=$(printf '%s\n' "$o1" | grep -o '閾 [^)]*[)）超]' | head -1)
  j2=$(printf '%s\n' "$o2" | grep -o '閾 [^)]*[)）超]' | head -1)
  printf '  %-22s | %-4s | %-4s | %-38s | %s\n' "$na" "$r1" "$r2" "${j1:-(無)}" "${j2:-(無)}"
}
kurabe "一 未設定"        MISET
kurabe "二 空文字"        ""
kurabe "三 空白のみ SP"   " "
kurabe "四 空白のみ TAB"  "$(printf '\t')"
kurabe "五 全角空白"      "　"
kurabe "六 4096"          4096
kurabe "七 abc"           abc
kurabe "八 0"             0
kurabe "九 2^63-1"        9223372036854775807
kurabe "十 2^63"          9223372036854775808
echo
echo "  ★讀み★ 六〜九(=「[ ]」 が比べられる値)の rc と 條⑤ の字は ★前後で同じ★。"
echo "        一二(未設定・空文字)は rc も條⑤も同じで、★増えたのは言葉だけ★(乙)。"
echo "        三四五七(數でない)は L49 の旧来の枝が先に食ふ ∴ 不変。"
echo "        ★変つたのは 十(2^63) だけ★ ―― 其処だけが旧版で ★器の誤りを刷りつつ通して居た★ 態である。"

echo
echo "=== 9. ⑸ 一行で戻す ==="
echo "  甲: sed -i '' -e '/★改め 甲(第50弾 提案 → 第51弾 で現物化)★/,/^  fi$/d' <gate> ―― は ★勧めぬ★(範囲が脆い)。"
echo "  ★勧める一行★(甲乙とも一度に戻す・控から): cp docs/evidence/km-51-usage-wo-yomazu-ni-yonda-20260917/raw/61_mon_saki.sh scripts/checks/karo_mac_dasumae_gate.sh"
echo "  ―― 61_mon_saki.sh は ★据ゑる前の生器の逐語の写し★(上 sha256 一致を示した)。之が最も短く、最も確かな戻し方である。"
rm -f "$FX"
echo
echo "=== 10. 終 ―― 生器 sha256(最終再測) ==="
echo "  $(shasum -a 256 "$NAMA")"
