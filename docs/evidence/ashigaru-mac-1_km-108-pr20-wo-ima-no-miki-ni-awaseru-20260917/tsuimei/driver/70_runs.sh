#!/bin/bash
# 70_runs.sh ―― 追命 ㋒(讀み手を直に・base 無/有) と ㋔(門を 4c99ff7c の版で・BASE 無/有) を 束内相対の臺帳へ当てる。
#   $1=束の絶對path $2=臺帳(束内相対) $3=捨て worktree(4c99ff7c)
#   ㋒ の出目は raw/70_*, raw/71_* へ(臺帳の後に建てる最終臺帳へ入る)。㋔ の控は mon_<HHMMSS>_<札>.{log,err,rc}(臺帳外)。
set -u
B="$1"; MAN="$2"; WT="$3"
V="$WT/scripts/checks/karo_mac_manifest_verify.py"; G="$WT/scripts/checks/karo_mac_dasumae_gate.sh"
paths_of(){ grep -v '^#' "$B/$MAN" | sed -n 's/^path=\(.*\) sha256=.*/\1/p'; }
cd "$B" || exit 9
printf 'verify=%s sha256=%s lines=%s\n' "$V" "$(shasum -a 256 < "$V" | cut -c1-64)" "$(wc -l < "$V" | tr -d ' ')" > raw/69_instruments.txt
printf 'gate=%s sha256=%s lines=%s\n' "$G" "$(shasum -a 256 < "$G" | cut -c1-64)" "$(wc -l < "$G" | tr -d ' ')" >> raw/69_instruments.txt
printf 'cwd=%s manifest=%s manifest_sha256=%s 刻=%s\n' "$PWD" "$MAN" "$(shasum -a 256 < "$MAN" | cut -c1-64)" "$(date '+%Y-%m-%dT%H:%M:%S%z')" >> raw/69_instruments.txt
# ㋒-1 讀み手を直に・argv に base 無
python3 -B "$V" "$MAN" > raw/70_verify_nobase.out 2> raw/70_verify_nobase.err; echo "rc=$?" > raw/70_verify_nobase.rc
# ㋒-2 讀み手を直に・argv に base "." 有
python3 -B "$V" "$MAN" . > raw/71_verify_base_dot.out 2> raw/71_verify_base_dot.err; echo "rc=$?" > raw/71_verify_base_dot.rc
# ㋒-補 讀み手を直に・cwd=repo 根(束内相対の臺帳を絶對 path で)・base 無
REPO="$(cd "$B/../../../.." && pwd)"
(cd "$REPO" && python3 -B "$V" "$B/$MAN") > raw/72_verify_nobase_cwdrepo.out 2> raw/72_verify_nobase_cwdrepo.err; echo "rc=$?" > raw/72_verify_nobase_cwdrepo.rc
# ㋔ 門(4c99ff7c 版 9cd550fc)を BASE 有/無 で
run(){ local fuda="$1" base="$2" ts log; ts="$(date '+%H%M%S')"; log="mon_${ts}_${fuda}"
  { printf 'fuda=%s\ngate=%s\ngate_sha256=%s\nverify_sibling_sha256=%s\ncwd=%s\nBASE=%s\n刻=%s\n' "$fuda" "$G" "$(shasum -a 256 < "$G" | cut -c1-64)" "$(shasum -a 256 < "$V" | cut -c1-64)" "$PWD" "$base" "$(date '+%Y-%m-%dT%H:%M:%S%z')"; } > "${log}.log"
  local -a argv; argv=(); while IFS= read -r p; do argv+=("$p"); done < <(paths_of)
  if [ "$base" = "-" ]; then env -u KM_GATE_MANIFEST_BASE bash "$G" "$MAN" "${argv[@]}" >> "${log}.log" 2> "${log}.err"
  else KM_GATE_MANIFEST_BASE="$base" bash "$G" "$MAN" "${argv[@]}" >> "${log}.log" 2> "${log}.err"; fi
  local rc=$?; printf 'gate_rc=%s\n' "$rc" | tee -a "${log}.log" > "${log}.rc"; printf '%s rc=%s log=%s\n' "$fuda" "$rc" "$log"; sleep 1; }
run m4c99_base   "."
run m4c99_nobase "-"
