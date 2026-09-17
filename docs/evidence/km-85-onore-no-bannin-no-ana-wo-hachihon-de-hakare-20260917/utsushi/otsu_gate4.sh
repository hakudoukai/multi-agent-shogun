#!/bin/bash
# ★寫し器★ otsu_gate4(型=乙) ―― 生器 scripts/checks/karo_mac_gate4.sh の逐語切片。★生器へは一字も書いて居らぬ★
#   生器 sha16=59cf051d3595fd97 / 切り出した行域=17-17 63-107 / 作つた刻=2026-09-17T11:35:17+0900
#   生器と同じ shell 宣: set -u
set -u
# ===== 寫し ここから(生器 逐語・一字も違へず) =====
say(){ printf '%s\n' "$*" >&2; }
# ★甲(裁 seq322952)★ 閾は ★後段の比較に使ふのと同じ演算子★ で先に検める。
#   旧形 is_num(case glob) は 2^63 以上の十進をも「數」と讀むが、後段の `[ -ge ]` は
#   ★rc=2 で倒れ else へ落ちて通す(fail-open)★ ―― 二つの器が別の答を出す。
#   形: GATE4_MAX_FILE_MB=99999999999999999999 → is_num=通 / [ -ge ]=rc2 → 條⑤ が黙つて通る。
#   ∴ is_num は捨て、`[ "$v" -ge 0 ]` を空打ちし rc<=1 の時のみ「使へる閾」とする。
num_same_op(){ [ "${1:-}" -ge 0 ] 2>/dev/null; [ $? -le 1 ]; }

# ★乙(裁 seq322952)★ 未設定/空文字/空白のみ を ★分けて名指し★、既定へ倒す時は ★必ず刷る★。
#   旧形の `${VAR:-50}` は ★未設定と空文字を一つに混ぜ、黙つて既定へ倒して居た★。
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

fix_threshold GATE4_MAX_FILE_MB 50 MAXF
# ===== 寫し ここまで =====
# ===== 附録(當席が書いた駆動部・寫しに非ず) =====
__uke="${MAXF-《受け皿が立たず》}"
__kbranch=UNRUN
# ↓ 下流 逐語(scripts/checks/karo_mac_gate4.sh:115) ―― 1MB の file を閾(MB)と比べ、條⑤ を鳴らすか決める ／ 前後の括りは當席の物、中は一字も違へず
big=0; mb=1; f=__nise_no_file__
# --- 下流 寫し ここから ---
  if [ "$mb" -ge "$MAXF" ]; then say "★條⑤ 単 file が ${mb} MB(上限 ${MAXF})―― ${f}★"; big=1; fi
# --- 下流 寫し ここまで ---
[ "$big" = 1 ] && __kbranch="TAKEN(條⑤鳴る)" || __kbranch="NOTTAKEN(條⑤黙る)"
__k3="${__read_rc-―}"   # read の rc(在る器のみ)
printf "RESULT\t%s\t%s\t%s\n" "$__uke" "$__kbranch" "$__k3"
