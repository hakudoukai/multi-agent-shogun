#!/bin/bash
# ★生器に一字も書いて居らぬ事★ を porcelain と sha で示す(專任2 km-93)。
# 生器 = scripts/ 配下 ・ ~/bin 配下 ・ settings.json
set -u
cd "$(git rev-parse --show-toplevel)" || exit 2
printf '刻 %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')"
printf 'HEAD %s / 枝 %s\n' "$(git rev-parse --short HEAD)" "$(git rev-parse --abbrev-ref HEAD)"

printf '\n==== git porcelain ―― scripts/ ・ .claude/settings.json ====\n'
git status --porcelain -- scripts .claude/settings.json
rc=$?
printf 'porcelain rc=%s\n' "$rc"
n=$(git status --porcelain -- scripts .claude/settings.json | grep -c ''); rcn=$?
printf '★scripts/ + settings.json の porcelain 行 = %s★ (grep rc=%s ―― 0行なら grep rc=1)\n' "$n" "$rcn"

printf '\n==== ★本弾が触れて居らぬ證★ ―― 家老が 13:15 に測つた値との突合 ====\n'
f=scripts/checks/karo_mac_manifest_verify.py
now=$(shasum -a 256 "$f" | cut -c1-16)
gyou=$(grep -c '' "$f")
printf '  %s\n' "$f"
printf '    家老の宣(13:15) sha16=a507c998c7bd6485 / 198行\n'
printf '    今の実測        sha16=%s / %s行\n' "$now" "$gyou"
if [ "$now" = "a507c998c7bd6485" ] && [ "$gyou" = "198" ]; then
  printf '    ★一致 ∴ 本弾は此の器へ一字も書いて居らぬ★\n'
else
  printf '    ★相異 ―― 誰かが此の刻の間に書いた。名指して報せよ★\n'
fi

printf '\n==== scripts/ 配下で ★M(作業樹の差分)★ を持つ器と其の sha16 ====\n'
git status --porcelain -- scripts | while IFS= read -r line; do
  st=${line:0:2}; p=${line:3}
  p=${p%\"}; p=${p#\"}
  if [ -f "$p" ]; then
    printf '  %s %s sha16=%s\n' "$st" "$p" "$(shasum -a 256 "$p" | cut -c1-16)"
  else
    printf '  %s %s (file 無)\n' "$st" "$p"
  fi
done

printf '\n==== ~/bin 配下 ―― 本弾の刻より後に触られた物 ====\n'
# 本弾の起し = 13:16(task assigned_at)。之より新しい mtime の物を名指す。
found=$(find "$HOME/bin" -maxdepth 1 -type f -newermt '2026-09-17 13:16:00' 2>/dev/null | grep -c ''); rcf=$?
printf '  13:16 以降に mtime が動いた物 = %s 本 (grep rc=%s)\n' "$found" "$rcf"
find "$HOME/bin" -maxdepth 1 -type f -newermt '2026-09-17 13:16:00' 2>/dev/null | sed 's|^|    |'
printf '  ★註★ 之は mtime の話であり ★中身が変つたか★ の話ではない ―― ~/bin は git 外ゆゑ porcelain で測れぬ。\n'

printf '\n==== 本弾が足した物(untracked)は束一つだけか ====\n'
git status --porcelain --untracked-files=normal | grep '^??' | sed 's|^|  |'
printf '\n了 %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')"
