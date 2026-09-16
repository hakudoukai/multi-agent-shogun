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

# ★2026-09-12 止血(総監督裁 seq307881/307874 ⑴ ―― default-deny 側へ揃へる)★
#   旧版は 數 を取る口に ★|| true★ を置き、器が落ちても ${n:-0} で ★0(=通)★ に倒れた。
#   ∴ 「測れなんだ」が「疵が無い」と同じ顔をした ―― ★赤→青 の向きに開く(fail-open)★。
#   本止血: 數が ★十進の數でない★ か ★grep の rc が 2 以上(器の誤り)★ なら ★落とす★。
#   可逆: 控(…bak-20260912-shiketsu-failopen)へ戻せば旧挙動。
is_num(){ case "${1:-}" in (''|*[!0-9]*) return 1 ;; (*) return 0 ;; esac }

# ★甲(裁 seq322952)★ 閾は ★後段の比較に使ふのと同じ演算子★ で先に検める。
#   is_num(case glob) は 2^63 以上の十進をも「數」と讀むが、後段の `[ -ge ]` は
#   ★rc=2 で倒れ else へ落ちて通す(fail-open)★ ―― 二つの器が別の答を出す。
#   形: DASUMAE_MAX_BYTES=99999999999999999999 → is_num=通 / [ -ge ]=rc2 → 條⑤ が黙つて通つた。
#   ∴ `[ "$v" -ge 0 ]` を空打ちし、rc<=1 の時のみ「使へる閾」とする。
num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }
# ★案甲(第50弾)★ 幅が広過ぎる ―― 上の num_same_op は「0以上か」でなく「數として讀めたか」
#   しか問うて居らぬ([ $? -le 1 ] が 偽(rc=1) をも可とする)。∴ 負値・零・天井無しが素通りする。
#   ★後段と同じ演算子の儘、床と天を課す。★ rc=2(讀めぬ)も || で 1 へ落ちる ―― fail-closed。
num_in_range(){ # $1=値 $2=床 $3=天
  [ "${1:-}" -ge "${2:-0}" ] 2>/dev/null || return 1
  [ "${1:-}" -le "${3:-9223372036854775806}" ] 2>/dev/null || return 1
}
# ★案乙(第50弾)★ 後段の語法が別 ―― DASUMAE_READ_TIMEOUT の後段は [ -ge ] に非ず ★timeout(1)★。
#   故に [ -ge ] で検めると ⑴timeout が受ける 10m を拒み ⑵timeout が拒む「 50 」を通す。
#   ★検め器を後段の器 其の物に替へる。★ 加へて 數として讀める時のみ 床1/天86400 を課す
#   (timeout 0 は ★時限を掛けぬ★ の意ゆゑ ―― 實測 .nama/20_moto.tsv)。
tmo_ok(){ # $1=値 ―― timeout(1) が受けるか
  if [ "${1:-}" -ge 0 ] 2>/dev/null; then
    [ "${1:-}" -ge 1 ] 2>/dev/null || return 1
    [ "${1:-}" -le 86400 ] 2>/dev/null || return 1
  fi
  [ -n "${TIMEOUT_BIN:-}" ] || return 0
  "$TIMEOUT_BIN" "${1:-}" true >/dev/null 2>&1
  [ $? -ne 125 ]
}
# ★案丙(第50弾)★ 門票への行注入 ―― 拒んだ値を ★逐語で★ 刷る故、値が門票を一行 書く。
#   ★形だけ刷り、生は刷らぬ。★ LC_ALL=C の [:print:] は 改行も和字も印字可に非ず
#   ∴ 「門 通。出してよい。」の語も潰れる(實測 .nama/20_moto.tsv koshi_C_locale)。
#   生の byte 数を併記する ―― 截つた事を黙らぬ為。
safe_show(){
  local s="${1:-}" n
  n=$(printf '%s' "$s" | wc -c | tr -d ' ')
  printf '%s' "$s" | LC_ALL=C tr -c '[:print:]' '?' | cut -c1-40
  printf '(生 %s byte)' "$n"
}

# ★乙(裁 seq322952)★ 未設定/空文字/空白のみ を ★分けて名指し★、既定へ倒す時は ★必ず刷る★。
#   註: 「空白のみ」は ASCII の空白類のみを見る(全角空白は value 側へ落ち、比較器が拒む)。
env_state(){
  eval "_es_set=\"\${$1+set}\"; _es_v=\"\${$1-}\""
  if [ -z "${_es_set}" ]; then printf 'unset\n'
  elif [ -z "${_es_v}" ]; then printf 'empty\n'
  elif [ -z "$(printf '%s' "${_es_v}" | tr -d '[:space:]')" ]; then printf 'blank\n'
  else printf 'value\n'; fi
}

# 閾を一本の道で定める ―― $1=変数名 $2=既定 $3=受け皿の変数名
fix_threshold(){
  local name="$1" dflt="$2" out="$3" chk="${4:-num_in_range}" lo="${5:-0}" hi="${6:-1048576}" st raw
  st="$(env_state "$name")"
  eval "raw=\"\${$name-}\""
  case "$st" in
    unset) say "閾 ${name} = 未設定 ―― 既定 ${dflt} を用ゐる(★倒した事を刷る★)"; eval "$out=\$dflt"; return 0 ;;
    empty) say "★閾 ${name} が空文字 ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
    blank) say "★閾 ${name} が空白のみ ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
  esac
  if "$chk" "$raw" "$lo" "$hi"; then eval "$out=\$raw"; return 0; fi
  say "★閾 ${name} が比較器で扱へぬ か 範囲外(「$(safe_show "$raw")」・許 ${lo}..${hi}) ―― 既定 ${dflt} へ倒す(fail-closed)★"
  eval "$out=\$dflt"
}

# ★2026-09-16 裁 seq320321⑴(313209/314012) ―― 「止」を通さぬ(家老mac 自席の器・可逆・事後1便)★
#   由来: 門には第三の出目「止」が在る ―― FIFO/device を `wc -c` が永久に待ち、rc も出ぬ。
#   ★實測(家老mac 2026-09-16)★: `timeout 3 wc -c < "$fifo"` は ★120秒 戻らなんだ★(背に回して止めた)。
#     因 = `<` 再向は ★shell が open() する★ ゆゑ、timeout が exec される ★前に★ 止まる。
#     ∴ 裁の文言「全 read に timeout(10s)」は ★此の形(< 再向)では効かぬ★。上へ申し上げた。
#   ∴ 本形は「時限を付ける」でなく ★開かぬ★ を第一とする:
#     ①-L で符を見(開かぬ) ②実体を readlink -f で確かめ ③/dev/* を拒み
#     ④常なる file でなければ拒み ⑤寸法は ★stat(開かぬ)★ で取り ⑥其れでも時限を被せる。
#   出目が數でなければ ★既存の is_num → 「測れぬは通さぬ(default-deny)」★ へ落ちる。
#   ―― ★新しい落ち枝を作らぬ。既に在る枝へ合流させる。★
#   可逆: 呼出二箇所を `wc -c < "$f"` へ戻せば旧挙動(控 = docs/evidence/karo-mac-gate-hook-fix-20260916/raw/00_gate_BEFORE.sh)。
TIMEOUT_BIN="$(command -v timeout 2>/dev/null || command -v gtimeout 2>/dev/null || true)"
SAFE_SIZE_TMO="${DASUMAE_READ_TIMEOUT:-10}"
# ★閾そのものが數でなければ既定へ倒す(fail-closed) ―― 非數の閾は器を殺さず番人だけ黙らせる★
fix_threshold DASUMAE_READ_TIMEOUT 10 SAFE_SIZE_TMO tmo_ok 1 86400
# ★同じ病が同じ file の L20 に残つて居た ―― 閾 MAXB は素のままであつた(專任3 第40弾 実測・家老 021211 再測)★
#   實測(直す前): DASUMAE_MAX_BYTES=abc → L190 の [ ] が rc=2 → if が偽 → ★「條⑤ 寸法 = byte和 6(閾 abc未満)」を刷り rc=0★。
#   ★肝★ 既定へ倒すだけでは足りぬ。★倒した事を言へ。★ 黙つて倒すのは別の fail-open である(專任3 第40弾 の法)。
fix_threshold DASUMAE_MAX_BYTES 10485760 MAXB num_in_range 0 1099511627776

safe_size(){
  local f="${1:-}" r
  [ -n "$f" ] || { printf 'NOPATH'; return 0; }
  if [ -L "$f" ]; then
    r="$(readlink -f -- "$f" 2>/dev/null || true)"
    [ -n "$r" ] || { printf 'DANGLING'; return 0; }
  else
    r="$f"
  fi
  case "$r" in (/dev/*) printf 'DEVICE'; return 0 ;; esac
  [ -e "$r" ] || { printf 'DANGLING'; return 0; }
  [ -f "$r" ] || { printf 'NOTREG'; return 0; }
  if [ -n "$TIMEOUT_BIN" ]; then
    "$TIMEOUT_BIN" "$SAFE_SIZE_TMO" stat -f %z -- "$r" 2>/dev/null | tr -d ' \n'
  else
    stat -f %z -- "$r" 2>/dev/null | tr -d ' \n'
  fi
}

check_one_file(){
  # $1=file → stdout: "PASS|FAIL <条名> <詳細>" の行を複数出す。rc=0(全PASS)/1(何か落ちた)
  local f="$1" fail=0
  [ -f "$f" ] || { say "★file が無い: ${f}★"; return 2; }

  local ws_n ws_rc
  # ★2026-09-12 止血(総監督裁 seq307918 ―― 條②の CRLF 隠れ)★
  #   旧版の形は $'[ \t]+$' ―― 行末に \r が居ると ★空白は行末に無い★ 事に成り、
  #   ∴ CRLF の紙では末尾空白が ★黙つて 0 行★ に成つた。實測(此の止血の前):
  #     同じ中身で LF=條② 2 行 / ★CRLF=條② 0 行★(條③CR だけが鳴つた)。
  #   本止血: 行末判定を ★\r?$★ にして、\r が在つても無くても行末と読む。
  #   ★偽の青は作れぬ★ ―― 條②を隠す紙は必ず條③を鳴らす故、此の疵は「數を少なく言ふ」疵である。
  #   可逆: 下行の $'[ \t]+\r?$' を $'[ \t]+$' へ戻せば旧挙動。
  ws_n=$(grep -cE $'[ \t]+\r?$' "$f" 2>/dev/null); ws_rc=$?
  if [ "$ws_rc" -ge 2 ] || ! is_num "$ws_n"; then
    say "★條② 測れぬ(grep rc=${ws_rc}・出目「${ws_n}」) ―― ${f}★ ★測れぬは通さぬ(default-deny)★"
    fail=1
  elif [ "$ws_n" -gt 0 ]; then
    say "★末尾空白 ―― ${f} に ${ws_n} 行★"
    fail=1
  fi

  local cr_n cr_rc
  cr_n=$(grep -c $'\r' "$f" 2>/dev/null); cr_rc=$?
  if [ "$cr_rc" -ge 2 ] || ! is_num "$cr_n"; then
    say "★條③ 測れぬ(grep rc=${cr_rc}・出目「${cr_n}」) ―― ${f}★ ★測れぬは通さぬ(default-deny)★"
    fail=1
  elif [ "$cr_n" -gt 0 ]; then
    say "★CR混入 ―― ${f} に ${cr_n} 行★"
    fail=1
  fi

  local sz last1 last2
  sz=$(safe_size "$f")
  if ! is_num "$sz"; then
    say "★條④ 測れぬ(寸法が取れぬ・出目「${sz}」) ―― ${f}★ ★測れぬは通さぬ(default-deny)★"
    return 1
  fi
  if [ "$sz" -eq 0 ]; then
    say "★EOF改行 ―― ${f} は空file(0byte)★"
    fail=1
  else
    last1=$(tail -c1 "$f" 2>/dev/null | xxd -p 2>/dev/null | tr -d ' \n')
    if [ -z "$last1" ]; then
      say "★條④ 測れぬ(末尾一字が取れぬ) ―― ${f}★ ★測れぬは通さぬ(default-deny)★"
      fail=1
    elif [ "$last1" != "0a" ]; then
      say "★EOF改行が無い(0) ―― ${f}★"
      fail=1
    elif [ "$sz" -ge 2 ]; then
      last2=$(tail -c2 "$f" 2>/dev/null | xxd -p 2>/dev/null | tr -d ' \n')
      if [ -z "$last2" ]; then
        say "★條④ 測れぬ(末尾二字が取れぬ) ―― ${f}★ ★測れぬは通さぬ(default-deny)★"
        fail=1
      elif [ "$last2" = "0a0a" ]; then
        say "★EOF改行が複数(末尾に空行) ―― ${f}★"
        fail=1
      fi
    fi
  fi

  return $fail
}

run_gate(){
  # $1=manifest|-- ; shift ; $@=files
  # ★2026-09-16 裁 seq320321⑵(311933) ―― :97 の shift 欠陥を直す(家老mac 自席・可逆)★
  #   旧: `local man="$1"; shift` は $# = 0 の時 ★man が空★ になり shift は rc=1。
  #       set -u 下でも local 代入中の "$1" は落ちず、門は ★台帳も file も無いまま最後まで歩いた★。
  #       (現状の呼び手 三本は悉く2本以上渡して居る ∴ 之は ★潜在★ の疵であり、実害は未だ出て居らぬ。)
  #   本形: 受けた數を先に測り、足らねば ★何も測らずに落とす(default-deny)★。
  if [ "$#" -lt 2 ]; then
    say "★引数不足 ―― 受けた數 $# / 要 2 以上(<manifest|--> <file...>)★ ★測る物が無い。測れぬは通さぬ(default-deny)★"
    return 1
  fi
  local man="$1"; shift
  local files=("$@")
  local fail=0

  if [ "$man" = "--" ]; then
    say "條① 台帳とdiskの差 = スキップ(台帳未指定)"
  else
    # ★2026-09-12 止血(裁 seq307881/307874 ⑴・第二手)★
    #   旧版は基点に ★明示の ""★ を渡して居た。"" は cwd 相対 ―― ∴ 門は ★立つ場所で出目が変つた★。
    #   實測(此の止血の後も残つて居た): 同じ臺帳・同じ file・同じ刻で repo 根 rc=1 / ba_A 配下 rc=0。
    #   ∴ 基点を ★渡さぬ★。照合器の「器の在處から導いた repo 根」既定(cwd に依らぬ)へ委ねる。
    #   可逆: 下行の末尾へ ' ""' を戻せば旧挙動。
    # ★2026-09-17 基点の口 を足す(裁 seq322949)★
    #   束内相対の臺帳(裁322699)は ★既定基点=repo 根★ では悉く「実体無」で落ちる。
    #   實測: 專任1 _after/98_rel_test.txt(既定→実体無2/2・基点明示→一致2/2)／專任3 が同じ L157 を名指した。
    #   ∴ 呼ぶ側が基点を渡せる口を足す。★既定は従前の儘(渡さぬ)★ ――
    #   環境変数 KM_GATE_MANIFEST_BASE が ★set されて居る時のみ★ 渡す
    #   (空文字も「cwd 相対」の明示として通る ―― ${x+set} は空でも set を返す故)。
    #   可逆: 下の if/else を `python3 ... "$man"` の一行へ戻せば旧挙動。
    local vrc
    if [ -n "${KM_GATE_MANIFEST_BASE+set}" ]; then
      python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man" "$KM_GATE_MANIFEST_BASE"
      vrc=$?
      say "條① 基点=★引数 明示★(KM_GATE_MANIFEST_BASE)"
    else
      python3 "$(dirname "$0")/karo_mac_manifest_verify.py" "$man"
      vrc=$?
      say "條① 基点=既定(器の在處から導いた repo 根・cwd に依らぬ) ―― ★倒した事を刷る(裁322952 乙)★"
    fi
    if [ $vrc -eq 0 ]; then
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
    sz=$(safe_size "$f")
    if ! is_num "$sz"; then
      say "★條⑤ 測れぬ(寸法が取れぬ) ―― ${f}★ ★測れぬは通さぬ(default-deny)★"
      fail=1
      sz=0
    fi
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
