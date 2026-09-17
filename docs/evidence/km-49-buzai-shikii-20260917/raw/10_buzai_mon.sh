#!/bin/bash
# 10_buzai_mon.sh ―― ★部材級の閾★(第49弾 ㋐)。★束の中に建てた器であり、生器へは一字も据ゑて居らぬ。★
#
# 由来: 生器 scripts/checks/karo_mac_dasumae_gate.sh の 條⑤ は ★束の byte 和★ 一つきり。
#       ∴ 「総和が閾の 29% だから通る」の一言で ★一本 263 万 byte の部材★ が隠れる(第48弾 實測)。
#       本器は ★部材 = 一本の file★ と定め、其の一本に閾を当てる(則 = 01_nori.txt 一・二)。
#
# 部材 = ★一本の常なる file★(dir でも拡張子でも同内容の群でもない ―― 選ばなかつた理由は 01_nori.txt)。
# 閾   = ★1,048,576 byte(1 MiB)= 束級 10,485,760 の 1/10★。env BUZAI_MAX_BYTES で動く。
#        as_of 2026-09-17。由来と不感帯(91,480〜2,632,943)は 01_nori.txt 二。★固定値を焼き込まぬ(裁294493⑸)★
#
# usage: bash 10_buzai_mon.sh <file...>
#        printf '%s\0' <file...> | bash 10_buzai_mon.sh --from0
#          ―― ★NUL で受ける口★(第48弾 ㋖-1 の直し ―― `$(cat 一覧)` は `a b.txt` を二本に割る)
# rc=0 : 閾以上の部材が無い(出してよい)  rc=1 : 閾以上 或いは 測れぬ部材が在る  rc=2 : 引数の誤り
set -u

MAXB="${BUZAI_MAX_BYTES:-1048576}"
say(){ printf '%s\n' "$*" >&2; }

# ★字句同一★ ―― 生器と ★一字も違へぬ★。家老は「五本」と仰せられたが、器で歩けば ★七本★ に在つた:
#   agent_health_check.sh:88 / inbox_watcher.sh:131 / checks/context_usage_warn.sh:35 /
#   redundancy/shogun_report_watcher.sh:31 / checks/karo_mac_gate4.sh:63 /
#   checks/karo_mac_dasumae_gate.sh:29 / watchdogs/enter_restart_common_watchdog.sh:80
#   ―― 8/8 一致(本器を含む)。測りは 11_jiku_doitsu.out。
#   sha256(行・末尾改行を含めず)= 9ebb7840f743508b…(家老裁 322099/322214)
is_num(){ case "${1:-}" in (''|*[!0-9]*) return 1 ;; (*) return 0 ;; esac }

# ★閾が數でなければ既定へ倒し、★倒した事を言ふ★(黙つて倒すのは別の fail-open ―― 生器 L46-49 の法)★
is_num "$MAXB" || { say "★閾 BUZAI_MAX_BYTES が數でない(「${MAXB}」) ―― 既定 1048576 へ倒す(fail-closed)★"; MAXB=1048576; }

TIMEOUT_BIN="$(command -v timeout 2>/dev/null || command -v gtimeout 2>/dev/null || true)"
SAFE_SIZE_TMO="${BUZAI_READ_TIMEOUT:-10}"
is_num "$SAFE_SIZE_TMO" || { say "★閾 BUZAI_READ_TIMEOUT が數でない(「${SAFE_SIZE_TMO}」) ―― 既定 10 へ倒す(fail-closed)★"; SAFE_SIZE_TMO=10; }

# ★開かぬ★ ―― 生器 safe_size と同じ形(門には第三の出目「止」が在る ∴ FIFO/device を開かぬ)
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

FILES=()
if [ "${1:-}" = "--from0" ]; then
  while IFS= read -r -d '' _p; do
    FILES[${#FILES[@]}]="${_p}"
  done
else
  if [ "$#" -lt 1 ]; then
    say "usage: $0 <file...>   /   printf '%s\\0' <file...> | $0 --from0"
    exit 2
  fi
  for _p in "$@"; do
    FILES[${#FILES[@]}]="${_p}"
  done
fi

if [ "${#FILES[@]}" -eq 0 ]; then
  say "★受けた部材が 0 本 ―― 測る物が無い。測れぬは通さぬ(default-deny)★"
  exit 2
fi

fail=0
bosuu=0
koeta=0
hakarenu=0
koeta_wa=0
total=0
for f in "${FILES[@]}"; do
  bosuu=$((bosuu + 1))
  sz="$(safe_size "${f}")"
  if ! is_num "${sz}"; then
    say "★部材級 測れぬ ―― ${f}(出目「${sz}」)★ ★測れぬは通さぬ(default-deny)★"
    hakarenu=$((hakarenu + 1))
    fail=1
    continue
  fi
  total=$((total + sz))
  if [ "${sz}" -ge "$MAXB" ]; then
    say "★部材 閾超 ―― ${f}(${sz} byte・閾 ${MAXB} 以上)★"
    koeta=$((koeta + 1))
    koeta_wa=$((koeta_wa + sz))
    fail=1
  fi
done

say "部材級 = 母數 ${bosuu} 本 / ★閾超 ${koeta} 本★ / 閾超の和 ${koeta_wa} byte / 測れぬ ${hakarenu} 本 / 束の和 ${total} byte(部材閾 ${MAXB})"
if [ "$fail" -ne 0 ]; then
  # ★鳴つた理由を取り違へるな★ ―― 「閾超」と「測れぬ」は別の出目である(㋒ 陽4 で本器が一度取り違へた)。
  if [ "$koeta" -gt 0 ] && [ "$hakarenu" -gt 0 ]; then
    say "★部材級が鳴つた ―― 閾超 ${koeta} 本 と 測れぬ ${hakarenu} 本。束の和が閾未満でも ★中身は健かでない★。★"
  elif [ "$koeta" -gt 0 ]; then
    say "★部材級が鳴つた ―― 閾超 ${koeta} 本。束の和が閾未満でも ★中身は健かでない★。★"
  else
    say "★部材級が鳴つた ―― 閾超は 0 本。鳴つたのは ★測れぬ ${hakarenu} 本★ である(閾の話ではない)。★"
  fi
  exit 1
fi
say "★部材級 通 ―― 閾以上の部材は一本も無い。★"
exit 0
