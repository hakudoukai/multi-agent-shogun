#!/bin/bash
# 40_ichiyou.sh ―― ★㋑「番人段は一様18」を破る★
#   專任2 は番人片を抜き出して18回走らせた。∴ 彼の「一様」は★段(body)の一様★であり、
#   生器の中で閾が受ける扱ひの一様ではない。當席は生器(★凍結版★)の中で四軸を測る。
#     ①段    : fix_threshold / num_same_op / env_state の sha16 ―― 四器で同じか
#     ②口    : _th_say の行先 ―― stderr か LOG か・冠は何か
#     ③受け皿: fix_threshold NAME 既定 ★出先★ ―― 出先が NAME 自身か別名か
#     ④残存  : 番人を通した後に猶 ${NAME:-既定} が残るか
# 使ひ方: 40_ichiyou.sh <器path>...      ★引数は凍結版を渡せ(生器を読むな)★
# ★己の疵(前版)★: $1 を閾一覧tsv と誤り、器path を一覧として読んだ。
#   ∴ 全行が器名不明となり ★測れぬ:器名不明★ を12行刷った。本版は argv から器を取る。
# ★己の疵(本版の初手)★: 番人列の抽出を [A-Z_]+:[0-9]+ と書き、★ESCALATE_PHASE1/2★ を取り落した
#   (名に數字が入る ―― 18閾の筈が16と出た)。[A-Z0-9_]+ へ直した。
set -u
[ $# -ge 1 ] || { echo '★測れぬ:器が渡されて居らぬ★' >&2; exit 2; }

dan_sha() {  # ①段 ―― 番人三片を抜き、sha16 を刷る
  awk '/^(fix_threshold|num_same_op|env_state)\(\)/{p=1} p{print} /^}$/{p=0}' "$1" | shasum -a 256 | cut -c1-16
}
dan_gyou() { awk '/^(fix_threshold|num_same_op|env_state)\(\)/{p=1} p{n++} /^}$/{p=0} END{print n+0}' "$1"; }

printf '#=== ①段 ―― 四器で番人の body は一様か ===\n'
printf '#器\t段sha16\t段行\n'
first=''
for f in "$@"; do
  s=$(dan_sha "$f"); [ -n "$first" ] || first="$s"
  printf '%s\t%s\t%s\n' "$(basename "$f")" "$s" "$(dan_gyou "$f")"
done
onaji=0; for f in "$@"; do [ "$(dan_sha "$f")" = "$first" ] || onaji=1; done
[ "$onaji" -eq 0 ] && printf '判①\t★段は一様(四器で sha16 同一)★ ―― 專任2 の申し立ては此処では★破れなんだ★\n' \
                   || printf '判①\t★段が割れた★\n'

printf '\n#=== ①対照 ―― 檢出子は差を見附けられるか ===\n'
SAYA="${TMPDIR:-/tmp}/km51_40_$$"; mkdir -p "$SAYA"
one=$1; cp "$one" "$SAYA/pos.sh"
# ★陽性対照★: 段の中の一字を書き換へた偽器を拵へ、同じ檢出子に掛ける(★生器へは一字も書かぬ★)
sed 's/fail-closed/fail-CLOSED/' "$one" > "$SAYA/pos.sh"
printf '陽性対照(段を一字変へた偽器)\t%s\t%s\n' "$(dan_sha "$SAYA/pos.sh")" \
  "$([ "$(dan_sha "$SAYA/pos.sh")" != "$(dan_sha "$one")" ] && echo '★差を検出した(対照成立)★' || echo '★対照が落ちた ―― 檢出子は差を見ぬ★')"
cp "$one" "$SAYA/neg.sh"
printf '陰性対照(同じ中身を写しただけ)\t%s\t%s\n' "$(dan_sha "$SAYA/neg.sh")" \
  "$([ "$(dan_sha "$SAYA/neg.sh")" = "$(dan_sha "$one")" ] && echo '★同一と出た(対照成立)★' || echo '★対照が落ちた★')"
rm -rf "$SAYA"

printf '\n#=== ②口 ―― 倒した事を何処へ言ふか ===\n'
printf '#器\t_th_say の定義\t行先\t冠\n'
for f in "$@"; do
  d=$(grep -m1 -E '^_th_say\(\)' "$f")
  case "$d" in
    *'>&2'*) saki='stderr' ;;
    *'log '*|*'log "'*) saki='★LOG file(stderr に非ず)★' ;;
    *) saki='★測れぬ★' ;;
  esac
  kan=$(printf '%s' "$d" | grep -oE '\[[a-z_]+\]' | head -1); [ -n "$kan" ] || kan='★冠無し★'
  printf '%s\t%s\t%s\t%s\n' "$(basename "$f")" "$d" "$saki" "$kan"
done

printf '\n#=== ③受け皿・④残存 ―― 閾ごと ===\n'
printf '#閾名\t器\t受け皿\t受け皿は己か\t残存${NAME:-}_件\t判\n'
for f in "$@"; do
  ki=$(basename "$f")
  # 番人列(for _t in … done)の中は 名←名。直呼びは NAME 既定 出先。
  {
    awk '/for _t in/{p=1} p{print} /^done$/{if(p){p=0}}' "$f" \
      | grep -oE '[A-Z0-9_]+:[0-9]+' | sed 's/:.*//' | sed 's/$/\t己/'
    grep -E '^[ 	]*fix_threshold [A-Z_]+ ' "$f" \
      | sed -E 's/^[ 	]*fix_threshold ([A-Z_]+) [^ ]+ ([A-Za-z_]+).*/\1\t\2/'
  } | while IFS=$'\t' read -r na ukez; do
    [ -n "$na" ] || continue
    if [ "$ukez" = '己' ]; then ukez="$na"; ono='★己へ書戻す(子も清まる)★'
    elif [ "$ukez" = "$na" ]; then ono='★己へ書戻す(子も清まる)★'
    else ono="★別名($ukez) ―― 環境の毒は其の儘・子へ継ぐ★"; fi
    zan=$(grep -cE "\\\$\{$na[:=-]" "$f")
    han='OK'; [ "$zan" -gt 0 ] && han="★残存既定 ${zan}件★"
    case "$ono" in *別名*) han="$han/★受け皿が別名★";; esac
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$na" "$ki" "$ukez" "$ono" "$zan" "$han"
  done
done
