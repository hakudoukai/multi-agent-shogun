#!/bin/bash
# 22_taihi.sh ―― ★束級(生器 條⑤)と部材級(本器)を ★同じ束★ へ当てて出目を並べる★(㋑)。
# usage: bash 22_taihi.sh <束の根> <控へ先の冠>
# ★生器へは一字も書かぬ★ ―― 呼ぶだけ。閾も env で上書きせぬ(生の既定で走らせる)。
set -u
ROOT="${1:?根}"
KAN="${2:?冠}"
KI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${KI}/../../../.." && pwd)"

# ★NUL で渡す(第48弾 ㋖-1 の直し ―― 空白を含む名が二本に割れる)★
find "$ROOT" -type f -print0 > "${KAN}_argv.nul"
HON=$(tr -dc '\0' < "${KAN}_argv.nul" | wc -c | tr -d ' ')
printf '受けた部材 = %s 本(NUL 区切り・根 %s)\n' "$HON" "$ROOT"

printf '\n=== 甲 束級(生器 karo_mac_dasumae_gate.sh・閾 10485760・臺帳は -- で skip) ===\n'
xargs -0 bash "${REPO}/scripts/checks/karo_mac_dasumae_gate.sh" -- < "${KAN}_argv.nul" > "${KAN}_soukyu.out" 2> "${KAN}_soukyu.err"
printf '束級 rc=%s\n' "$?"
grep -E '條⑤' "${KAN}_soukyu.err" || printf '★條⑤ の行が出目に無い★\n'

printf '\n=== 乙 部材級(本器 10_buzai_mon.sh・閾 1048576) ===\n'
bash "${KI}/10_buzai_mon.sh" --from0 < "${KAN}_argv.nul" > "${KAN}_buzai.out" 2> "${KAN}_buzai.err"
printf '部材級 rc=%s\n' "$?"
cat "${KAN}_buzai.err"
