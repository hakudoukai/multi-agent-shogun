#!/bin/bash
# ★事変★ ―― 本弾の ㋔ を書いて居る最中に、★生器が他の手で直つた★。
#   實測: 5d… 己が写しを取つた 05:04:24 の生器 sha256 = 3eaa5cc6…
#         本 script を書く時の生器 sha256 = e11f0d01…(mtime 2026-09-17 05:09:42)
#         新しい生器の中に 「★甲(裁 seq322952)★」「★乙(裁 seq322952)★」 の註が在る。
#   ∴ 己の ㋔ は ★已に据ゑられた物への提案★ に成つた。取下げるのではなく ★他人の手を己の対照で検める★。
#   ★生器へは一字も書かぬ。讀んで写すのみ。★
set -u
REPO=/Users/momizimac/multi-agent-shogun
NAMA="$REPO/scripts/checks/karo_mac_dasumae_gate.sh"
HERE="$(cd "$(dirname "$0")" && pwd)"
SAKI="$HERE/61_mon_saki.sh"          # 05:04:24 の生器(旧)
IMA="$HERE/65_mon_ima.sh"            # 05:09:42 の生器(今)
ATO="$HERE/62_mon_ato.sh"            # 己の案を当てた写し

echo "=== 0. 刻と sha ==="
echo "  今の刻     = $(date '+%Y-%m-%d %H:%M:%S')"
echo "  生器 mtime = $(stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "$NAMA")"
echo "  生器 sha256(今) = $(shasum -a 256 "$NAMA" | cut -d' ' -f1)"
echo "  写し sha256(旧・05:04:24) = $(shasum -a 256 "$SAKI" | cut -d' ' -f1)"
cp "$NAMA" "$IMA"
echo "  写し(今) = raw/65_mon_ima.sh sha256 = $(shasum -a 256 "$IMA" | cut -d' ' -f1)"
echo "  一致するか(生器 vs 65) = $( [ "$(shasum -a 256 "$NAMA"|cut -d' ' -f1)" = "$(shasum -a 256 "$IMA"|cut -d' ' -f1)" ] && echo 一致 || echo ★不一致★ )"
echo "  行数 旧=$(grep -c '' "$SAKI") 今=$(grep -c '' "$IMA") 己の案=$(grep -c '' "$ATO")"

echo
echo "=== 1. 旧 → 今 の差(他人の手・逐語) ==="
diff -u "$SAKI" "$IMA" > "$HERE/66_ima.diff"; echo "  差の行数 = $(grep -c '' "$HERE/66_ima.diff")  (raw/66_ima.diff)"
echo "  ★裁★ の印を数へる = $(grep -c 'seq322952' "$IMA") 箇所"

echo
echo "=== 2. bash -n(三つとも) ==="
for f in "$SAKI" "$IMA" "$ATO"; do
  o=$(bash -n "$f" 2>&1); r=$?
  printf '  %-16s rc=%s 出目=「%s」\n' "$(basename "$f")" "$r" "${o:-(空)}"
done

echo
echo "=== 3. 小さき紙を拵へる ==="
FX="$HERE/.taishou_fixture.txt"
printf '一二三\n' > "$FX"; printf 'あいうえお\n' >> "$FX"
echo "  紙 = $FX 寸法=$(stat -f %z "$FX") byte"

hashiru(){
  local fuda="$1" maxb="$2" ki="$3" kami="$4" out rc
  case "$maxb" in
    (MISET) out=$(env -u DASUMAE_MAX_BYTES bash "$ki" -- "$kami" 2>&1); rc=$? ;;
    (*)     out=$(DASUMAE_MAX_BYTES="$maxb" bash "$ki" -- "$kami" 2>&1); rc=$? ;;
  esac
  local jou5; jou5=$(printf '%s\n' "$out" | grep '條⑤ 寸法' | head -1)
  local koe; koe=$(printf '%s\n' "$out" | grep -c '倒す\|用ゐる\|integer expression\|閾 = 既定\|扱へぬ')
  printf '  [%s] %s rc=%s 告げ=%s行\n' "$fuda" "$(basename "$ki")" "$rc" "$koe"
  printf '      條⑤ = 「%s」\n' "${jou5:-(條⑤ の行が出ぬ)}"
  printf '%s\n' "$out" | grep '倒す\|用ゐる\|integer expression\|閾 = 既定\|扱へぬ\|門 通\|門が落ちた' | sed 's/^/      ／ /'
}

echo
echo "=== 4. ⑶ 甲 ―― 閾 2^63 / 小さき紙 ==="
for k in "$SAKI:旧" "$IMA:今" "$ATO:己の案"; do
  hashiru "陽性・${k#*:}" 9223372036854775808 "${k%%:*}" "$FX"
done

echo
echo "=== 5. ★要★ 閾 2^63 / byte和が閾を超える紙(10485762 byte) ==="
BIG="$HERE/.taishou_10mb.txt"
yes 'x' 2>/dev/null | head -c 10485761 > "$BIG"; printf '\n' >> "$BIG"
echo "  拵へた紙 寸法=$(stat -f %z "$BIG") byte(既定閾 10485760 を超える)"
for k in "$SAKI:旧" "$IMA:今" "$ATO:己の案"; do
  hashiru "陽性大・${k#*:}" 9223372036854775808 "${k%%:*}" "$BIG"
done
echo "  ★陰性(正形・大)★ 閾=10485760 ―― 三つとも鳴らねばならぬ"
for k in "$SAKI:旧" "$IMA:今" "$ATO:己の案"; do
  hashiru "陰性大・${k#*:}" 10485760 "${k%%:*}" "$BIG"
done
rm -f "$BIG"; echo "  (10MB の紙は消した)"

echo
echo "=== 6. ⑶ 乙 ―― 空の閾 ==="
for t in "MISET:未設定" ":空文字" " :空白のみSP" "4096:陰性4096"; do
  v="${t%%:*}"; na="${t#*:}"
  echo "  ―― 態 $na"
  for k in "$SAKI:旧" "$IMA:今" "$ATO:己の案"; do
    hashiru "$na・${k#*:}" "$v" "${k%%:*}" "$FX"
  done
done

echo
echo "=== 7. ⑷ 態 十通 ―― 旧 / 今 / 己の案 の三列 ==="
printf '  %-18s | %-14s | %-14s | %-14s\n' 態 '旧 rc/告げ' '今 rc/告げ' '己の案 rc/告げ'
printf '  %s\n' "-------------------+----------------+----------------+----------------"
hitotsu(){
  local ki="$1" tai="$2" o r
  case "$tai" in
    (MISET) o=$(env -u DASUMAE_MAX_BYTES bash "$ki" -- "$FX" 2>&1); r=$? ;;
    (*)     o=$(DASUMAE_MAX_BYTES="$tai" bash "$ki" -- "$FX" 2>&1); r=$? ;;
  esac
  printf '%s/%s' "$r" "$(printf '%s\n' "$o" | grep -c '倒す\|用ゐる\|閾 = 既定\|扱へぬ')"
}
kurabe3(){
  printf '  %-18s | %-14s | %-14s | %-14s\n' "$1" "$(hitotsu "$SAKI" "$2")" "$(hitotsu "$IMA" "$2")" "$(hitotsu "$ATO" "$2")"
}
kurabe3 "一 未設定"       MISET
kurabe3 "二 空文字"       ""
kurabe3 "三 空白のみ SP"  " "
kurabe3 "四 空白のみ TAB" "$(printf '\t')"
kurabe3 "五 全角空白"     "　"
kurabe3 "六 4096"         4096
kurabe3 "七 abc"          abc
kurabe3 "八 0"            0
kurabe3 "九 2^63-1"       9223372036854775807
kurabe3 "十 2^63"         9223372036854775808
rm -f "$FX"

echo
echo "=== 8. 走り終へて生器を測り直す(己が一字も書いて居らぬ證) ==="
echo "  生器 sha256 = $(shasum -a 256 "$NAMA" | cut -d' ' -f1)"
echo "  生器 mtime  = $(stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "$NAMA")"
