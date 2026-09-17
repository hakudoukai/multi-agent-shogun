#!/bin/bash
# km-91 _after/03 ―― 生器 L58 の比較器を ★逐語のまま★ 切り出して単体で叩く。
#   生器 scripts/stop_hook_inbox.sh:58 の一行を一字も変へず写した(下の verbatim)。
set -u
num_same_op() { [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }

probe() {  # $1=札 $2=値
  local tag="$1" v="$2" inner innerrc outrc
  [ "$v" -ge 0 ] 2>/dev/null; innerrc=$?
  if num_same_op "$v"; then outrc=0; else outrc=1; fi
  printf '%-14s\t内 [ v -ge 0 ] rc=%s\t比較器 出目=%s\n' \
    "$tag" "$innerrc" "$( [ "$outrc" -eq 0 ] && echo '通' || echo '止' )"
}

echo "# 03 比較器 単体 ―― 生器 L58 逐語:"
echo '#   num_same_op() { [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }'
echo "# bash=$(bash --version|head -1)"
echo "# 「通」= num_same_op が真 = 既定 10 へ倒さず ★其の値のまま read -t へ渡す★"
echo
echo "## 陰性(守る筈 = 通つてよい)"
probe "10" "10"
probe "0" "0"
echo "既定(未設定)   \t―― 比較器へ届かぬ: L64 の \${VAR:-10} が 10 に解く ∴ 実質 10 と同じ"
echo
echo "## 陽性(開く筈 = 止まるべきが通つてゐないか)"
probe "-5" "-5"
probe "-1" "-1"
echo
echo "## 境"
probe "空文字" ""
probe "空白のみ" " "
probe "abc" "abc"
probe "010" "010"
probe "2^63超(20桁)" "99999999999999999999"
probe "可視印␊既在" "1␊0"
probe "改行入り" "$(printf '1\n0')"
