#!/bin/bash
# karo_mac_dasumae_gate_negative_test.sh
#   出す前門(karo_mac_dasumae_gate.sh)の ★負テスト★ ―― 裁 seq330497 +
#   軍師mac REVISE PR#27(seq330291「LF/CR/TAB等 threshold sanitization の自動試験なし。
#   各値の単一診断/非注入/fallback試験要」)への答。
#
# ★紙を repo へ commit せぬ★: 疵の紙(末尾不可視字・CRLF・0byte)を追跡下に置けば
#   其の紙が他の門を鳴らす。∴ 全ての紙を ★codepoint から走る時に組み立てる★。
#   之は同時に「形で数へる目録は閉ぢぬ」への手当でもある ―― 形は此処に明記され、増やせる。
#
# usage: bash scripts/checks/tests/karo_mac_dasumae_gate_negative_test.sh
#   rc=0: 期待と實測が悉く一致 / rc=1: 食ひ違ひ在り / rc=2: 器が走れぬ
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
#   ★門の path は env で差せる★ ―― 之が無いと「此の負テスト自身が器か」を
#   疵の在る旧版に当てて実演できぬ(器は己の陽性対照を持たねばならぬ)。
GATE="${DASUMAE_GATE:-$HERE/../karo_mac_dasumae_gate.sh}"
[ -f "$GATE" ] || { printf '★門が無い: %s★\n' "$GATE" >&2; exit 2; }

T="$(mktemp -d)" || { printf '★mktemp 失敗★\n' >&2; exit 2; }
trap 'rm -rf "$T"' EXIT

PASS=0; FAIL=0
ok(){ PASS=$((PASS+1)); printf '  通 %s\n' "$1"; }
ng(){ FAIL=$((FAIL+1)); printf '★落 %s ―― %s★\n' "$1" "$2"; }

# 紙を組み立てる ―― $1=名 $2=末尾に置く byte 列(printf の escape)
mk_tail(){ printf '見出し\n本文\n最終行'"$2"'\n' > "$T/$1"; }

# ―― 條② 十形(名・UTF-8 byte 列・codepoint) ――
#    U+0020 U+0009 U+00A0 U+2003 U+2007 U+202F U+3000 U+007F U+200B U+FEFF
JOU2_NAMES="a_sp b_tab c_nbsp d_emsp e_figsp f_nnbsp g_ideo h_del i_zwsp j_bom"
jou2_bytes(){
  case "$1" in
    a_sp)   printf ' ' ;;
    b_tab)  printf '\011' ;;
    c_nbsp) printf '\302\240' ;;
    d_emsp) printf '\342\200\203' ;;
    e_figsp)printf '\342\200\207' ;;
    f_nnbsp)printf '\342\200\257' ;;
    g_ideo) printf '\343\200\200' ;;
    h_del)  printf '\177' ;;
    i_zwsp) printf '\342\200\213' ;;
    j_bom)  printf '\357\273\277' ;;
  esac
}

printf '=== 其一 條② 末尾不可視字 十形(★悉く鳴るべし★) ===\n'
for n in $JOU2_NAMES; do
  f="$T/jou2_$n.md"
  { printf '見出し\n本文\n最終行'; jou2_bytes "$n"; printf '\n'; } > "$f"
  e=$(bash "$GATE" -- "$f" 2>&1 >/dev/null); rc=$?
  if [ "$rc" -eq 0 ]; then ng "條②/$n" "rc=0 で通つた(★偽の青★)"
  elif printf '%s\n' "$e" | grep -q '末尾不可視字'; then ok "條②/$n rc=$rc"
  else ng "條②/$n" "rc=$rc だが條②の報せが無い"; fi
done

printf '=== 其二 條③ CR混入 ===\n'
printf '見出し\r\n本文\r\n最終行\n' > "$T/jou3_crlf.md"
e=$(bash "$GATE" -- "$T/jou3_crlf.md" 2>&1 >/dev/null); rc=$?
{ [ "$rc" -ne 0 ] && printf '%s\n' "$e" | grep -q 'CR混入'; } && ok "條③/crlf rc=$rc" || ng "條③/crlf" "rc=$rc"

printf '=== 其三 條④ 末尾行 四形 ===\n'
printf '見出し\n本文\n最終行' > "$T/jou4_noeol.md"            # EOF改行無
printf '見出し\n本文\n最終行\n\n' > "$T/jou4_twoeol.md"        # 空行
printf '見出し\n本文\n最終行\n\r\n' > "$T/jou4_crlf_twoeol.md" # CRLF 空行(舊版は黙つた)
: > "$T/jou4_zero.md"                                          # 0byte
for pair in "jou4_noeol.md:EOF改行が無い" "jou4_twoeol.md:末尾行が不可視のみ" \
            "jou4_crlf_twoeol.md:末尾行が不可視のみ" "jou4_zero.md:空file"; do
  f="${pair%%:*}"; want="${pair##*:}"
  e=$(bash "$GATE" -- "$T/$f" 2>&1 >/dev/null); rc=$?
  { [ "$rc" -ne 0 ] && printf '%s\n' "$e" | grep -q "$want"; } && ok "條④/$f rc=$rc" || ng "條④/$f" "rc=$rc ―― 「${want}」が無い"
done

printf '=== 其四 ★重畳=完全な偽の青★(條②の全角盲 + 條④の0a0a限定が重なつた形) ===\n'
#   舊版(2b652d9b)實測: 此の二紙は ★rc=0「出してよい」★ であつた。
{ printf '見出し\n本文\n最終行\n'; jou2_bytes g_ideo; printf '\n'; } > "$T/kasane_k.md"
{ printf '見出し\n本文\n最終行\n'; jou2_bytes a_sp;  printf '\n'; } > "$T/kasane_l.md"
for f in kasane_k.md kasane_l.md; do
  e=$(bash "$GATE" -- "$T/$f" 2>&1 >/dev/null); rc=$?
  n2=$(printf '%s\n' "$e" | grep -c '末尾不可視字'); n4=$(printf '%s\n' "$e" | grep -c '末尾行が不可視のみ')
  { [ "$rc" -ne 0 ] && [ "$n2" -ge 1 ] && [ "$n4" -ge 1 ]; } \
    && ok "重畳/$f rc=$rc 條②=$n2 條④=$n4(★両方鳴る★)" \
    || ng "重畳/$f" "rc=$rc 條②=$n2 條④=$n4 ―― 舊版の偽の青が残る"
done

printf '=== 其五 NUL 四形(濡れ衣を作らぬ事も見る) ===\n'
printf '見出し\n本\000文\n最終行\n' > "$T/nul_m.md"                        # 清い尾 → 鳴らぬべし
{ printf '見出し\n本\000文\n最終行'; jou2_bytes a_sp; printf '\n'; } > "$T/nul_n.md"
{ printf '見出し\n最終行\000'; jou2_bytes a_sp; printf '\n'; } > "$T/nul_o.md"
{ printf '見出し\n最終行'; jou2_bytes a_sp; printf '\000\n'; } > "$T/nul_p.md"
e=$(bash "$GATE" -- "$T/nul_m.md" 2>&1 >/dev/null); rc=$?
[ "$rc" -eq 0 ] && ok "NUL/清い尾 rc=0(濡れ衣無し)" || ng "NUL/清い尾" "rc=$rc ―― 濡れ衣"
for f in nul_n.md nul_o.md nul_p.md; do
  e=$(bash "$GATE" -- "$T/$f" 2>&1 >/dev/null); rc=$?
  { [ "$rc" -ne 0 ] && printf '%s\n' "$e" | grep -q '末尾不可視字'; } && ok "NUL/$f rc=$rc" || ng "NUL/$f" "rc=$rc"
done

printf '=== 其六 負対照(清い紙は鳴らぬ) ===\n'
printf '見出し\n本文\n最終行。\n' > "$T/clean.md"
e=$(bash "$GATE" -- "$T/clean.md" 2>&1 >/dev/null); rc=$?
[ "$rc" -eq 0 ] && ok "負対照 rc=0" || ng "負対照" "rc=$rc ―― 誤検知: $e"

printf '=== 其七 閾(軍師mac REVISE seq330291 ―― 各値の単一診断/非注入/fallback) ===\n'
#   ★2026-09-18 裁 seq330497★ 閾が非數/空/空白のみ/2^63以上 は ★既定へ倒さず rc=2 で止める★。
#   ★行数を定数で縛るな★: 當席は初め「stderr は 2 行」と期待して 8 件を落としたが、
#   第三行は ★もう一方の閾(DASUMAE_READ_TIMEOUT)が既定へ倒つた事を刷る正しい行★ であつた。
#   ∴ 縛りは「全ての行が ★門の語彙で説明が付く★ か」= 身元の判る行だけか、で置く。
thr_case(){ # $1=札 $2=値
  local tag="$1" val="$2" e rc n_thr n_all n_acct n_inj n_ctrl
  e=$(DASUMAE_MAX_BYTES="$val" bash "$GATE" -- "$T/clean.md" 2>&1 >/dev/null); rc=$?
  n_thr=$(printf '%s\n' "$e" | grep -c '閾 DASUMAE_MAX_BYTES')        # 単一診断
  n_all=$(printf '%s\n' "$e" | grep -c '')
  n_acct=$(printf '%s\n' "$e" | grep -c '閾 DASUMAE_\|門 止まる')    # 身元の判る行
  n_inj=$(printf '%s\n' "$e" | grep -c '^★偽の報せ行★')              # 行頭に立つたら★注入★
  # 生の制御字が stderr へ素通りして居らぬか(逃がして刷る筈: ␊ ␍ ␉)
  n_ctrl=$(printf '%s' "$e" | tr -d '\n' | LC_ALL=C tr -cd '\001-\010\011\013-\037' | wc -c | tr -d ' ')
  if [ "$rc" -ne 2 ]; then ng "閾/$tag" "rc=$rc(要 2 ―― 既定へ倒れて居る)"
  elif [ "$n_thr" -ne 1 ]; then ng "閾/$tag" "閾の診断が ${n_thr} 行(要 ★1行=単一診断★)"
  elif [ "$n_inj" -ne 0 ]; then ng "閾/$tag" "★行注入★ ―― 値の中身が独立した行に成つた(${n_inj} 行)"
  elif [ "$n_acct" -ne "$n_all" ]; then ng "閾/$tag" "身元不明の行 $((n_all - n_acct)) 本(全 ${n_all} 行)"
  elif [ "$n_ctrl" -ne 0 ]; then ng "閾/$tag" "生の制御字 ${n_ctrl} 個が素通り(逃がして刷る筈)"
  else ok "閾/$tag rc=2 単一診断=1 注入=0 身元不明=0 生制御字=0(全 ${n_all} 行)"; fi
}
thr_case 空文字 ''
thr_case 空白のみ '   '
thr_case 全角空白のみ "$(jou2_bytes g_ideo)"
thr_case 非數 'abc'
thr_case 2^63以上 '99999999999999999999'
thr_case LF注入 "$(printf '10\n★偽の報せ行★')"
thr_case CR注入 "$(printf '10\r★偽の報せ行★')"
thr_case TAB注入 "$(printf '10\t★偽の報せ行★')"

printf '=== 其八 fallback と「以上」の境目 ===\n'
e=$(unset DASUMAE_MAX_BYTES; bash "$GATE" -- "$T/clean.md" 2>&1 >/dev/null); rc=$?
{ [ "$rc" -eq 0 ] && printf '%s\n' "$e" | grep -q '未設定 ―― 既定 10485760'; } \
  && ok "fallback/未設定 rc=0 かつ倒した事を刷る" || ng "fallback/未設定" "rc=$rc"
SZ=$(wc -c < "$T/clean.md" | tr -d ' ')
for d in -1 0 1; do
  th=$((SZ + d))
  [ "$th" -le 0 ] && continue
  e=$(DASUMAE_MAX_BYTES="$th" bash "$GATE" -- "$T/clean.md" 2>&1 >/dev/null); rc=$?
  case "$d" in
    -1|0) # 和 >= 閾 ―― 鳴るべし。かつ語は「以上」
      { [ "$rc" -ne 0 ] && printf '%s\n' "$e" | grep -q '以上'; } \
        && ok "境目/和=${SZ} 閾=${th}(和≧閾) rc=$rc 語=以上" \
        || ng "境目/和=${SZ} 閾=${th}" "rc=$rc ―― 鳴らぬか語が「超」の儘" ;;
    1)  [ "$rc" -eq 0 ] && ok "境目/和=${SZ} 閾=${th}(和<閾) rc=0" || ng "境目/和=${SZ} 閾=${th}" "rc=$rc" ;;
  esac
done

printf '\n=== 締め ===\n'
printf '通=%d 落=%d\n' "$PASS" "$FAIL"
if [ "$FAIL" -eq 0 ]; then printf '★負テスト 悉く一致。★\n'; exit 0; fi
printf '★負テストに食ひ違ひ %d 件。門を直せ。数を出すな。★\n' "$FAIL"; exit 1
