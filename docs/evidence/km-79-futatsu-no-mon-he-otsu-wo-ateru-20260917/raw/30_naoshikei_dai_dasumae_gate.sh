#!/bin/bash
# ★台 ―― scripts/checks/karo_mac_dasumae_gate.sh から機械で切り出した(手写しに非ず)★
set -u
say(){ printf '%s\n' "$*" >&2; }
num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }

# ★乙(裁 seq322952)★ 未設定/空文字/空白のみ を ★分けて名指し★、既定へ倒す時は ★必ず刷る★。
#   註: 「空白のみ」は tr -d '[:space:]' で見る。★此の註は先に誤つて居た★ ――
#   「全角空白(U+3000)は value 側へ落ちる」と書いて在つたが、BSD tr は之を空白と讀む。
#   實測(km-79): printf '　' | tr -d '[:space:]' → ★空★ ∴ ④全角空白は ★blank 側★ へ落ちる。
env_state(){
  eval "_es_set=\"\${$1+set}\"; _es_v=\"\${$1-}\""
  if [ -z "${_es_set}" ]; then printf 'unset\n'
  elif [ -z "${_es_v}" ]; then printf 'empty\n'
  elif [ -z "$(printf '%s' "${_es_v}" | tr -d '[:space:]')" ]; then printf 'blank\n'
  else printf 'value\n'; fi
}

# 閾を一本の道で定める ―― $1=変数名 $2=既定 $3=受け皿の変数名
fix_threshold(){
  local name="$1" dflt="$2" out="$3" st raw vp
  st="$(env_state "$name")"
  eval "raw=\"\${$name-}\""
  case "$st" in
    unset) say "閾 ${name} = 未設定 ―― 既定 ${dflt} を用ゐる(★倒した事を刷る★)"; eval "$out=\$dflt"; return 0 ;;
    empty) say "★閾 ${name} が空文字 ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
    blank) say "★閾 ${name} が空白のみ ―― 既定 ${dflt} へ倒す(fail-closed)★"; eval "$out=\$dflt"; return 0 ;;
  esac
  if num_same_op "$raw"; then eval "$out=\$raw"; return 0; fi
  # ★乙 行注入の封じ(裁 seq323980⑵ ―― 兄弟器 scripts/redundancy/shogun_report_watcher.sh L63-69 と同形)★
  #   値は env 由来ゆゑ改行を含み得、★己の判定の道(stderr)へ偽の報せ行を一本生む★。
  #   實測(本器・km-79 raw/20・21): 現形は ⑦改行注入 で ★報せ行 2(期待1)・注入痕 1★ であつた。
  #   乙=可視印(␊␍␉)へ置換(UTF-8 正・fork 無し・bash 3.2 可)。甲(0xB6)は UTF-8 不正ゆゑ採らず。
  #   ★印の曖昧性★=値が元から印を含めば注入と區別できぬ ∴ 其の時は ★刷らずに★ 倒す(fail-closed)。
  case "$raw" in
    *␊*|*␍*|*␉*) say "★閾 ${name} が可視印(␊␍␉)を既に含む ―― 値を刷らず既定 ${dflt} へ倒す(fail-closed・裁 seq323980⑵)★"; eval "$out=\$dflt"; return 0 ;;
  esac
  vp="${raw//$'\n'/␊}"; vp="${vp//$'\r'/␍}"; vp="${vp//$'\t'/␉}"
  say "★閾 ${name} を比較器が扱へぬ(「${vp}」) ―― 既定 ${dflt} へ倒す(fail-closed)★"
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
fix_threshold KM79_PROBE 50 OUT
printf %s\\n "${OUT}"
