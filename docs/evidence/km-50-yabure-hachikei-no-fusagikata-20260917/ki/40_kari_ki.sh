#!/bin/bash
# 40_kari_ki.sh ―― 門を当てる為の ★仮の樹★ を建てる(本 repo の index を一字も動かさぬ為)。
#
# 何故 repo の外か: gate4.sh は `git diff --cached` を見る ―― 即ち ★index に触れねば測れぬ★。
#   本 repo の index を動かすのは「生器への変更 0」の條に反する。
#   又 束の中に .git を作ると 家老の `git add -f <束>` が gitlink を掴む。
#   ∴ ★repo の外・home 直下の隠れ dir★ に建て、path を紙に明記する(再現の為)。
#
# usage: bash 40_kari_ki.sh [樹の在處]   既定 = $HOME/.km50_kari_ki
set -eu
W="${1:-$HOME/.km50_kari_ki}"
rm -rf "$W"
mkdir -p "$W"
cd "$W"
git init -q -b main .
git config user.email a3@example.invalid
git config user.name kari
printf 'hajime\n' > 00_hajime.txt
git add 00_hajime.txt
git -c commit.gpgsign=false commit -q -m 'kari: hajime'
git update-ref refs/remotes/origin/main HEAD        # 條① の「遠の枝」を満たす(仮)
printf 'kiyoi ichi gyou\n' > 01_kiyoi.txt           # 末尾空白なし・CR なし・EOF 改行丁度1
git add 01_kiyoi.txt                                # ★staged = 1 本★
printf '樹 %s\n' "$W"
printf '枝 %s\n' "$(git rev-parse --abbrev-ref HEAD)"
printf 'staged %s 本\n' "$(git diff --cached --name-only | grep -c .)"
printf '寸法 %s byte\n' "$(wc -c < 01_kiyoi.txt | tr -d ' ')"
