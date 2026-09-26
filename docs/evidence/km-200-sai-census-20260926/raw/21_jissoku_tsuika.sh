#!/bin/bash
# km-200 追加実測（REVISE⑤・2026-09-26）―― 20_jissoku.sh で測らなかった路を、★板・箱・DB へ出さぬ形のみ★で測る。
#   E sb-* 他6本 : ⒜⒝⒞ は --dry-run 付き（胴の門 L223 は creds と送信より前）。
#                  ⒟ は usage で return 0 に落ちる形（args<4・L166）だけ。sb-karo-mac の ⒟ は後ろに
#                  --requires-response を足すゆゑ args=4 に成り送信の路へ入り得る ∴ ★走らせない（字面のみ）★。
#   F inbox_write 稼働木版の後段 : IW_DEFERRAL_TEST_ONLY=1（DEFERRAL gate の直後で exit 0）と
#                  IW_DEAD_TEST_ONLY=1（dead-inbox gate の直後で exit 0）。其の後の増幅 guard・bridge・flock 書込は★走らせない★。
#   G mac_send.py : 標 "x" で空の本文 → L83 で rc3（subprocess より前）。cwd は空の dir（万一 L85 に達しても inbox_write が無い）。
# 使ひ方: bash raw/21_jissoku_tsuika.sh <束の dir> <空の cwd dir>
set -u
D="$1"; S="$D/raw/seed"; W="$2"
IW="$HOME/multi-agent-shogun/scripts/inbox_write.sh"; MS="$HOME/bin/mac_send.py"
raw() { local v; v="$(cat "$2"; printf x)"; printf -v "$1" '%s' "${v%x}"; }
row() { local name="$1"; shift; local out rc; out="$("$@" 2>&1)"; rc=$?; printf '%s | rc=%s | %s\n' "$name" "$rc" "$(printf '%s' "$out" | tr '\n' ' ' | cut -c1-120)"; }
raw E0 $S/e0_0byte.txt; raw E1 $S/e1_kuuhaku.txt; raw E2 $S/e2_kaigyou.txt; raw C $S/c_jitsu.txt
[ "${#E0}" -eq 0 ] && [ "${#E1}" -eq 3 ] && [ "${#E2}" -eq 1 ] && [ "${#C}" -eq 29 ] || { echo "★種の字数が合はぬ★" >&2; exit 9; }
[ -d "$W" ] && [ -z "$(ls -A "$W")" ] || { echo "★cwd が空の dir でない★" >&2; exit 9; }
echo "# 刻 $(date '+%Y-%m-%dT%H:%M:%S%z')  E0=${#E0}字 E1=${#E1}字 E2=${#E2}字 C=${#C}字"
echo "## E sb-* 他6本（⒜⒝⒞ は --dry-run・⒟ は usage 形のみ）"
for w in sb-ashigaru-mac-2 sb-ashigaru-mac-3 sb-gunshi-mac sb-shogun-mac sb-karo-mac sb-gakushu-bucho; do
  for p in "⒜0byte:$E0" "⒝空白のみ:$E1" "⒞改行のみ:$E2"; do
    row "E $w ${p%%:*}" "$HOME/bin/$w" write letter "${p#*:}" --to karo-mac --dry-run
  done
  row "E $w ⒟引数其の物が無い" "$HOME/bin/$w"
  row "E $w ⒟write のみ" "$HOME/bin/$w" write
  if [ "$w" != sb-karo-mac ]; then
    row "E $w ⒟write letter のみ" "$HOME/bin/$w" write letter
  else
    echo "E $w ⒟write letter のみ | 未実走 | 字面: 後ろに --requires-response が付き args=4・本文が「--」始まりで L186 die の筈"
  fi
done
echo "## F inbox_write 稼働木版の後段（止まり木2つ）"
for p in "⒜0byte:$E0" "⒝空白のみ:$E1" "⒞改行のみ:$E2" "対照:$C"; do
  row "F DEFERRAL argv ${p%%:*}" env IW_DEFERRAL_TEST_ONLY=1 bash "$IW" karo-mac "${p#*:}" report_received ashigaru-mac-1
done
for f in e0_0byte e1_kuuhaku e2_kaigyou c_jitsu; do
  row "F DEFERRAL stdin $f" sh -c 'IW_DEFERRAL_TEST_ONLY=1 INBOX_WRITE_CONTENT_STDIN=1 bash "$1" karo-mac "" report_received ashigaru-mac-1 < "$2"' _ "$IW" "$S/$f.txt"
done
for p in "⒝空白のみ:$E1" "⒞改行のみ:$E2" "対照:$C"; do
  row "F DEAD karo-mac(死箱) ${p%%:*}" env IW_DEAD_TEST_ONLY=1 bash "$IW" karo-mac "${p#*:}" report_received ashigaru-mac-1
  row "F DEAD ashigaru-mac-2(生箱) ${p%%:*}" env IW_DEAD_TEST_ONLY=1 bash "$IW" ashigaru-mac-2 "${p#*:}" report_received ashigaru-mac-1
done
echo "## G mac_send.py（標 x・cwd=空 dir）"
for f in e0_0byte e1_kuuhaku e2_kaigyou c_jitsu; do
  row "G send $f" sh -c 'cd "$1" && /usr/bin/python3 -B "$2" send "$3" x' _ "$W" "$MS" "$S/$f.txt"
done
# 対照: 標 km-200 は対照の本文に在る → L83 を越え L85 へ。cwd に scripts/ が無いゆゑ bash が rc127 → rc4（箱へは書けぬ）
row "G send 対照(標 km-200)" sh -c 'cd "$1" && /usr/bin/python3 -B "$2" send "$3" km-200' _ "$W" "$MS" "$S/c_jitsu.txt"
row "G ⒟引数無し" sh -c 'cd "$1" && /usr/bin/python3 -B "$2"' _ "$W" "$MS"
row "G ⒟send のみ" sh -c 'cd "$1" && /usr/bin/python3 -B "$2" send' _ "$W" "$MS"
[ -z "$(ls -A "$W")" ] && echo "# cwd は空のまま（何も書かれていない）" || echo "★cwd に物が生じた★"
