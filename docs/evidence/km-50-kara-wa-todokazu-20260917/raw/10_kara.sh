#!/bin/bash
# ㋐ ★空を検めへ届かせよ★ ―― 未設定・空文字・空白のみ を区別して is_num へ渡す。
# 器の本体は raw/05_ki.sh に一つだけ在る(此処には写さぬ)。
set -u
cd "$(dirname "$0")" || exit 2
. ./05_ki.sh

DEF=10485760   # 生器 karo_mac_dasumae_gate.sh:49 の既定値の写し

# 甲 = ★現行の形★  V="${X:-DEF}" ; is_num "$V"   ―― 空は :- に食はれ is_num へ屆かぬ
kou(){
  local n="$1" v rc
  eval "v=\"\${$n:-$DEF}\""
  if is_num "$v"; then rc=0; else rc=1; fi
  KOU_RC=$rc
  printf '  甲(現行 ${X:-既定}) 出目=「%s」 rc=%s 判=%s\n' "$v" "${rc}" "$([ "$rc" -eq 0 ] && printf 通 || printf 鳴)"
}

otsu(){
  local n="$1" o rc tai b wak
  o=$(tai_wake "$n"); rc=$?
  tai=${o%%	*}; b=$(printf '%s' "$o" | cut -f2); wak=${o##*	}
  OTSU_RC=$rc; OTSU_TAI=$tai
  printf '  乙(三態器 tai_wake) 態=%s 生値 %s byte rc=%s\n' "$tai" "$b" "${rc}"
  case "$rc" in
    (4) printf '     出目=★未設定★ ―― 既定 %s を当てる。★「当てた」と言ふ。★\n' "$DEF" ;;
    (3) printf '     出目=★空文字★ ―― 設定は在るが値が無い(★誤設定の疑ひ★・未設定とは別物)\n' ;;
    (2) printf '     出目=★空白のみ★ ―― 設定も値も在るが數でない(★誤設定★)\n' ;;
    (1) printf '     出目=★數でない★ ―― 鳴る\n' ;;
    (0) printf '     出目=數 ―― ★検めて通した★\n' ;;
  esac
  printf '     分かれた所 = %s\n' "$wak"
}

hikaku(){
  if [ "$KOU_RC" -eq 0 ] && [ "$OTSU_RC" -ne 0 ]; then
    printf '  ★割れ★ 甲 rc=0(通) ／ 乙 rc=%s(%s) ―― ★甲の出目では「検めて通した」と「既定で埋めた」が同じ顔をする。★\n' "${OTSU_RC}" "$OTSU_TAI"
  else
    printf '  一致 ―― 甲乙とも同じ事を言つて居る。\n'
  fi
}

printf '★㋐ 空の三態 ―― 甲(現行)と乙(三態器)へ同じ入力を当てる★\n'
printf '刻 = %s / 既定 DEF = %s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$DEF"

printf '\n=== 態一 未設定(unset X) ===\n';        unset X || true; kou X; otsu X; hikaku
printf '\n=== 態二 空文字(X="") ===\n';           X="";   kou X; otsu X; hikaku
printf '\n=== 態三 空白のみ(X=" " 半角空白) ===\n'; X=" ";  kou X; otsu X; hikaku
printf '\n=== 態四 空白のみ(X=TAB) ===\n';        X="	"; kou X; otsu X; hikaku
printf '\n=== 態五 全角空白(X=U+3000) ―― ★空に見えて空でない★ ===\n'; X="　"; kou X; otsu X; hikaku
printf '\n=== 態六 正しき數(X=4096) ===\n';       X="4096"; kou X; otsu X; hikaku
printf '\n=== 態七 數でない(X=abc) ===\n';        X="abc";  kou X; otsu X; hikaku

printf '\n★總括★\n'
printf '  甲は 態一(未設定)と態二(空文字)で ★同じ出目・同じ rc★ を出す ―― 区別できぬ。\n'
printf '  乙は 未設定(rc=4)/空文字(rc=3)/空白のみ(rc=2)/數でない(rc=1)/數(rc=0) の五つを ★rc で分ける★。\n'
printf '  ★穴は is_num に在るのではない。is_num へ ★屆く前に★ ${X:-既定} が空を食ふ事に在る。★\n'
printf '  ★然し乙にも際が在る ―― 態五 全角空白(U+3000・3 byte)は「空白のみ」でなく「中身在り」と判ずる。\n'
printf '    ASCII の SP/TAB しか空白と見て居らぬ故である。害は出ぬ(is_num が rc=1 で鳴る)が、★態の名は誤つて居る。★\n'
