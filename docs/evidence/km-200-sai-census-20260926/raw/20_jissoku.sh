#!/bin/bash
# km-200 再測（2026-09-26）―― 空の四形を器に当てる。★板へ出さぬ形のみ★で走らせる。
#   agent_letter: --dry-run（L310 で送らずに return 0）。胴の門 L223 は dry-run より前。
#   inbox_write : IW_NAME_TEST_ONLY=1（L75 で exit 0・箱へ書かぬ）。胴の門 L29 は L75 より前。稼働木の版のみ。
#   board_write : 引数無しのみ（L31 で rc2・POST に達せぬ）。
# 使ひ方: bash raw/20_jissoku.sh <束の dir>   出力は stdout（1行1件: 名 | rc | 出力の頭120字）
set -u
D="$1"; S="$D/raw/seed"
AL="$HOME/bin/agent_letter.py"; SB="$HOME/bin/sb-ashigaru-mac-1"; IW="$HOME/multi-agent-shogun/scripts/inbox_write.sh"; BW="$HOME/bin/board_write.py"
# file の中身を末尾改行ごと取る（$() は末尾改行を落とすゆゑ x を継いで剥ぐ）
# ★外側の $() でも末尾改行が落ちるゆゑ、関数で返さず変数へ直に剥ぐ（1度目は E2=0字 に潰れた・_first/）★
raw() { local v; v="$(cat "$2"; printf x)"; printf -v "$1" '%s' "${v%x}"; }
row() { local name="$1"; shift; local out rc; out="$("$@" 2>&1)"; rc=$?; printf '%s | rc=%s | %s\n' "$name" "$rc" "$(printf '%s' "$out" | tr '\n' ' ' | cut -c1-120)"; }
raw E0 $S/e0_0byte.txt; raw E1 $S/e1_kuuhaku.txt; raw E2 $S/e2_kaigyou.txt; raw C $S/c_jitsu.txt
[ "${#E0}" -eq 0 ] && [ "${#E1}" -eq 3 ] && [ "${#E2}" -eq 1 ] && [ "${#C}" -eq 29 ] || { echo "★種の字数が合はぬ E0=${#E0} E1=${#E1} E2=${#E2} C=${#C}★" >&2; exit 9; }
echo "# 刻 $(date '+%Y-%m-%dT%H:%M:%S%z')  E0=${#E0}字 E1=${#E1}字 E2=${#E2}字 C=${#C}字"
echo "## A agent_letter.py 直・argv 形（env -i・creds 無し・--dry-run）"
for p in "⒜0byte:$E0" "⒝空白のみ:$E1" "⒞改行のみ:$E2" "対照:$C"; do
  row "A ${p%%:*}" env -i PATH=/usr/bin:/bin HOME="$HOME" /usr/bin/python3 -B "$AL" ashigaru-mac-1 mac_pc letter "${p#*:}" --to karo-mac --dry-run
done
row "A ⒟引数無し(letter の後が無い)" env -i PATH=/usr/bin:/bin HOME="$HOME" /usr/bin/python3 -B "$AL" ashigaru-mac-1 mac_pc letter
row "A ⒟引数無し(letter も無い)" env -i PATH=/usr/bin:/bin HOME="$HOME" /usr/bin/python3 -B "$AL" ashigaru-mac-1 mac_pc
echo "## A2 agent_letter.py 直・--content-file 形（新しい路・9/19 には無かつた）"
for f in e0_0byte e1_kuuhaku e2_kaigyou c_jitsu; do
  row "A2 $f" env -i PATH=/usr/bin:/bin HOME="$HOME" /usr/bin/python3 -B "$AL" ashigaru-mac-1 mac_pc letter --content-file "$S/$f.txt" --to karo-mac --dry-run
done
row "A2 ⒟file 無し(旗のみ)" env -i PATH=/usr/bin:/bin HOME="$HOME" /usr/bin/python3 -B "$AL" ashigaru-mac-1 mac_pc letter --content-file
echo "## B sb-ashigaru-mac-1 経由（--dry-run・POST 前に return）"
row "B ⒜0byte" "$SB" write letter "$E0" --to karo-mac --dry-run
row "B ⒝空白のみ" "$SB" write letter "$E1" --to karo-mac --dry-run
row "B ⒞改行のみ" "$SB" write letter "$E2" --to karo-mac --dry-run
row "B ⒟write letter のみ" "$SB" write letter
row "B ⒟write のみ" "$SB" write
row "B ⒟引数其の物が無い" "$SB"
echo "## C inbox_write.sh 稼働木の版（IW_NAME_TEST_ONLY=1・箱へ書かぬ）"
for p in "⒜0byte:$E0" "⒝空白のみ:$E1" "⒞改行のみ:$E2" "対照:$C"; do
  row "C argv ${p%%:*}" env IW_NAME_TEST_ONLY=1 bash "$IW" karo-mac "${p#*:}" report_received ashigaru-mac-1
done
for f in e0_0byte e1_kuuhaku e2_kaigyou c_jitsu; do
  row "C stdin $f" sh -c 'IW_NAME_TEST_ONLY=1 INBOX_WRITE_CONTENT_STDIN=1 bash "$1" karo-mac "" report_received ashigaru-mac-1 < "$2"' _ "$IW" "$S/$f.txt"
done
row "C ⒟胴の位置を抜く" env IW_NAME_TEST_ONLY=1 bash "$IW" karo-mac report_received ashigaru-mac-1
echo "## D board_write.py（引数無しのみ・kv 有りは板へ PATCH ゆゑ走らせぬ）"
row "D ⒟引数無し" /usr/bin/python3 -B "$BW"
