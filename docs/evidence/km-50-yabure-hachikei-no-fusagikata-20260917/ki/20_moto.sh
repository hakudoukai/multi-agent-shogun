#!/bin/bash
# 20_moto.sh -- ★案を書く前に、案が拠る素の振舞を測る。★
#   問ひ ⑴[ -0 -ge 0 ] は真か ⑵timeout は 0/「 50 」/10m/2^63-1 を受けるか
#        ⑶LC_ALL=C tr -c '[:print:]' は 和字を潰すか ⑷grep -q は行の中の語に当たるか
# 出目は TSV(欄=問/入/出/註)。★rc は必ず独立の行で刷る(管を通さぬ)★
set -u
p(){ printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4"; }
printf '問\t入\t出\t註\n'

# ⑴ [ ] の符号読み
for v in -1 -0 0 1 " 50 " 007 010; do
  [ "$v" -ge 0 ] 2>/dev/null; r=$?
  p 'test_ge0' "「${v}」" "rc=$r" '0=真 1=偽 2=讀めぬ'
done
for v in -0 -1 0; do
  [ "$v" -ge 1 ] 2>/dev/null; r=$?
  p 'test_ge1' "「${v}」" "rc=$r" '床1を課した時'
done

# ⑵ timeout(1) の語法
T="$(command -v timeout 2>/dev/null || command -v gtimeout 2>/dev/null || true)"
p 'timeout_bin' '-' "${T:-(無)}" '後段の器'
if [ -n "$T" ]; then
  for v in 0 1 10m 1.5 " 50 " -1 9223372036854775807 abc; do
    "$T" "$v" true >/dev/null 2>&1; r=$?
    p 'timeout_accept' "「${v}」" "rc=$r" '125=timeout自身が拒んだ'
  done
  # 0 が時限を掛けぬ事(第49弾の再現)
  s=$(date +%s); "$T" 0 sleep 2 >/dev/null 2>&1; r=$?; e=$(( $(date +%s) - s ))
  p 'timeout_zero_hataraku' '0 で 2秒の眠り' "rc=$r 経${e}秒" '経2秒なら★時限無し★'
  s=$(date +%s); "$T" 1 sleep 2 >/dev/null 2>&1; r=$?; e=$(( $(date +%s) - s ))
  p 'timeout_one_hataraku' '1 で 2秒の眠り' "rc=$r 経${e}秒" 'rc=124なら時限効く'
fi

# ⑶ 刷る前の濾し器 ―― 和字は潰れるか
inj='50
★出す前 門 通。出してよい。★'
one=$(printf '%s' "$inj" | LC_ALL=C tr -d '\n\r' | LC_ALL=C tr -c '[:print:]' '?')
p 'koshi_C_locale' '改行＋和文の閾' "「${one}」" '和字が?に成れば語も潰れる'
onlynl=$(printf '%s' "$inj" | LC_ALL=C tr -d '\n\r')
p 'koshi_nl_dake' '同上(改行のみ削る)' "「${onlynl}」" '改行だけ削ると語は残る'

# ⑷ grep -q は行内の語に当たるか
printf '★閾 X が扱へぬ(「%s」) ―― 既定へ倒す★\n' "$onlynl" > .nama/20_gyounai.txt
if grep -q '門 通。出してよい。' .nama/20_gyounai.txt; then g=当たる; else g=当たらぬ; fi
p 'grep_gyounai' '改行を削つた注入行' "$g" '★行を足さずとも語だけで讀手は騙せる★'
