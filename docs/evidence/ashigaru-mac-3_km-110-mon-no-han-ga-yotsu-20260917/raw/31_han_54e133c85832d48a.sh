#!/bin/bash
# karo_mac_dasumae_gate.sh ―― 「出す前」五條を ★落ちた時に止まる★形で当てる(J-2、家老裁 msg_20260909_192913_40b706bf)。
#
# 由来: J-1(合作)三段の内「出す前」段(a2が書いた紙の上の問)を、
#       ★1コマンドへ落とす★ ―― a1「七問を増やしても使はねば零」を実行に移す。
#       既存(gate4=git staged限定・manifest_verify.py=台帳とdiskの差)を数へ、
#       ★無い物だけ★ を新設: 末尾空白/CR混入/EOF改行丁度1/寸法(裁294493 10MB閾)。
#       台帳とdiskの差は manifest_verify.py を其の儘呼ぶ(作り直さず・統べる)。
#
# usage: bash scripts/checks/karo_mac_dasumae_gate.sh <manifest|--> <file...>
#   manifest = 台帳path(照合する台帳が無ければ "--" を渡す→條①はskip扱ひで表示)
#   rc=0 : 五條(または台帳skip時は四條)悉く満つ(出してよい)
#   rc!=0: 何處が落ちたかをstderrへ出して止まる
#
# usage(自己検め): bash scripts/checks/karo_mac_dasumae_gate.sh --selftest
#   陽性対照(9/7 REVISE 280158の形=末尾空白+CR+EOF空行を再現)で必ず鳴るか、
#   負対照(清い紙)で鳴らずに済むかを、器自身に実演させる。
#   之で陽性対照が鳴らねば「器では無い」(a1裁・家老採用)。
set -u
MAXB="${DASUMAE_MAX_BYTES:-10485760}"  # 10MB(裁294493⑸)

say(){ printf '%s\n' "$*" >&2; }

check_one_file(){
  # $1=file → stdout: "PASS|FAIL <条名> <詳細>" の行を複数出す。rc=0(全PASS)/1(何か落ちた)
  local f="$1" fail=0
  [ -f "$f" ] || { say "★file が無い: ${f}★"; return 2; }

  local ws_n
  ws_n=$(grep -cE $'[ \t]+$' "$f" 2>/dev/null || true)
  if [ "${ws_n:-0}" -gt 0 ]; then
    say "★末尾空白 ―― ${f} に ${ws_n} 行★"
    fail=1
  fi

  local cr_n
  cr_n=$(grep -c $'\r' "$f" 2>/dev/null || true)
  if [ "${cr_n:-0}" -gt 0 ]; then
    say "★CR混入 ―― ${f} に ${cr_n} 行★"
    fail=1
  fi

  local sz last1 last2
  sz=$(wc -c < "$f" | tr -d ' ')
  if [ "$sz" -eq 0 ]; then
    say "★EOF改行 ―― ${f} は空file(0byte)★"
    fail=1
  else
    last1=$(tail -c1 "$f" | xxd -p)
    if [ "$last1" != "0a" ]; then
      say "★EOF改行が無い(0) ―― ${f}★"
      fail=1
    elif [ "$sz" -ge 2 ]; then
      last2=$(tail -c2 "$f" | xxd -p)
      if [ "$last2" = "0a0a" ]; then
        say "★EOF改行が複数(末尾に空行) ―― ${f}★"
        fail=1
      fi
    fi
  fi

  return $fail
}

run_gate(){
  # $1=manifest|-- ; shift ; $@=files
  local man="$1"; shift
  local files=("$@")
  local fail=0

  if [ "$man" = "--" ]; then
    say "條① 台帳とdiskの差 = スキップ(台帳未指定)"
  else
    if python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" ""; then
      say "條① 台帳とdiskの差 = 一致(manifest_verify.py rc=0)"
    else
      say "★條① 台帳とdiskの差が落ちた(manifest_verify.py 参照)★"
      fail=1
    fi
  fi

  if [ "${#files[@]}" -eq 0 ]; then
    say "★file が1つも無い★"
    return 2
  fi

  local any_ws=0 any_cr=0 any_eof=0
  for f in "${files[@]}"; do
    local out
    out=$(check_one_file "$f" 2>&1); local rc=$?
    if [ $rc -ne 0 ]; then
      printf '%s\n' "$out" >&2
      fail=1
    fi
  done
  if [ $fail -eq 0 ]; then
    say "條②末尾空白 / 條③CR混入 / 條④EOF改行丁度1 = 全file(${#files[@]}本)通"
  fi

  local total=0
  for f in "${files[@]}"; do
    local sz
    sz=$(wc -c < "$f" | tr -d ' ')
    total=$((total + sz))
  done
  if [ "$total" -ge "$MAXB" ]; then
    say "★條⑤ 寸法 ―― byte和 ${total}(閾 ${MAXB}・裁294493)超★"
    fail=1
  else
    say "條⑤ 寸法 = byte和 ${total}(閾 ${MAXB}未満)"
  fi

  if [ $fail -ne 0 ]; then
    say ""
    say "★出す前 門が落ちた。出すな。★"
    return 1
  fi
  say "★出す前 門 通。出してよい。★"
  return 0
}

selftest(){
  local tdir pos neg rc_pos rc_neg overall=0
  tdir=$(mktemp -d) || { say "★mktempが失敗★"; return 2; }
  pos="$tdir/pos_9_7_revise_280158.md"
  neg="$tdir/neg_clean.md"

  # 陽性対照 ―― 9/7 REVISE 280158 の形(末尾空白・CR・EOF空行)を再現。generic な一字弄りではない。
  printf '見出し行 \r\n本文行(末尾空白)   \r\n最終行。\n\n' > "$pos"

  # 負対照 ―― 清い紙(末尾空白0・CR0・EOF改行丁度1)
  printf '見出し行\n本文行\n最終行。\n' > "$neg"

  say "=== 自己検め(陽性対照=9/7 REVISE 280158の形) ==="
  run_gate -- "$pos" >/dev/null 2>&1; rc_pos=$?
  if [ $rc_pos -ne 0 ]; then
    say "陽性対照 = rc=${rc_pos}(鳴つた・正)"
  else
    say "★陽性対照が鳴らなんだ(rc=0) ―― 之は器では無い★"
    overall=1
  fi

  say "=== 自己検め(負対照=清い紙) ==="
  run_gate -- "$neg" >/dev/null 2>&1; rc_neg=$?
  if [ $rc_neg -eq 0 ]; then
    say "負対照 = rc=0(鳴らず・正)"
  else
    say "★負対照が鳴つた(rc=${rc_neg}) ―― 誤検知★"
    overall=1
  fi

  rm -rf "$tdir"
  if [ $overall -eq 0 ]; then
    say "★自己検め通 ―― 陽性対照は鳴り・負対照は鳴らず。器として使へる。★"
  else
    say "★自己検め落ち ―― 器を直せ。数を出すな。★"
  fi
  return $overall
}

if [ "${1:-}" = "--selftest" ]; then
  selftest
  exit $?
fi

if [ $# -lt 2 ]; then
  say "usage: $0 <manifest|--> <file...>"
  say "       $0 --selftest"
  exit 2
fi

run_gate "$@"
exit $?
