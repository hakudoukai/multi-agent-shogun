#!/bin/bash
# 60_gate_runs.sh ―― 門を ★PR#20 幹の版(9cd550fc)★ で、己の束(束内相対の臺帳)へ当てる。
#   $1 = 束の絶對path  $2 = 臺帳(束内相対)  $3 = 捨て worktree(純 PR#20 幹 0bb92e2b)  $4 = 捨て worktree(main+PR#20 を merge し 二本を HEAD 側へ解いた樹)
#   出目は 控 mon_<HHMMSS>_<札>.log/.err/.rc へ(★臺帳へ入れぬ・走る毎に別名★)。
#   札: pure  = 純 PR#20 幹(門 9cd550fc + 讀み手 b19ec9ea/127行)
#       merged= 解いた後の樹(門 9cd550fc + 讀み手 ebfc4c0e/198行 = 提案する merge の結果)
#       base  = KM_GATE_MANIFEST_BASE=. 有 / nobase = 無 / nobase_root = 無 かつ cwd=repo根
set -u
B="$1"; MAN="$2"; WT_PURE="$3"; WT_MERGED="$4"
REPO="$(cd "$(dirname "$0")/../../../.." && pwd)"
paths_of(){ grep -v '^#' "$B/$MAN" | sed -n 's/^path=\(.*\) sha256=.*/\1/p'; }
run(){  # $1=札 $2=門path $3=BASE(有なら "." / 無なら "-") $4=cwd
  local fuda="$1" gate="$2" base="$3" wd="$4" ts log
  ts="$(date '+%H%M%S')"; log="$B/mon_${ts}_${fuda}"
  { printf 'fuda=%s\ngate=%s\ngate_sha256=%s\nverify_sibling_sha256=%s\ncwd=%s\nBASE=%s\n刻=%s\n' "$fuda" "$gate" "$(shasum -a 256 < "$gate" | cut -c1-64)" "$(shasum -a 256 < "$(dirname "$gate")/karo_mac_manifest_verify.py" | cut -c1-64)" "$wd" "$base" "$(date '+%Y-%m-%dT%H:%M:%S%z')"; } > "${log}.log"
  local man_arg="$MAN"; [ "$wd" = "$B" ] || man_arg="$B/$MAN"
  local -a argv; argv=()
  while IFS= read -r p; do [ "$wd" = "$B" ] && argv+=("$p") || argv+=("$B/$p"); done < <(paths_of)
  if [ "$base" = "-" ]; then
    (cd "$wd" && env -u KM_GATE_MANIFEST_BASE bash "$gate" "$man_arg" "${argv[@]}") >> "${log}.log" 2> "${log}.err"
  else
    (cd "$wd" && KM_GATE_MANIFEST_BASE="$base" bash "$gate" "$man_arg" "${argv[@]}") >> "${log}.log" 2> "${log}.err"
  fi
  local rc=$?
  printf 'gate_rc=%s\n' "$rc" | tee -a "${log}.log" > "${log}.rc"
  printf '%s rc=%s log=%s\n' "$fuda" "$rc" "$(basename "$log")"
  sleep 1
}
run pure_base    "$WT_PURE/scripts/checks/karo_mac_dasumae_gate.sh"   "." "$B"
run pure_nobase  "$WT_PURE/scripts/checks/karo_mac_dasumae_gate.sh"   "-" "$B"
run pure_nobase_root "$WT_PURE/scripts/checks/karo_mac_dasumae_gate.sh" "-" "$REPO"
run merged_base   "$WT_MERGED/scripts/checks/karo_mac_dasumae_gate.sh" "." "$B"
run merged_nobase "$WT_MERGED/scripts/checks/karo_mac_dasumae_gate.sh" "-" "$B"
