#!/usr/bin/env bash
# 一時 worktree の衛生 を検める(警告 のみ・止めぬ)。
# 出典: skills/ephemeral-worktree-hygiene/SKILL.md ・ 2026-09-08 disk 満杯 事故。
set -uo pipefail

REPO="${1:-/Users/momizimac/DentalBI}"
WT_DIR="${REPO}/.claude/worktrees"
FREE_GI="$(df -g "${REPO}" 2>/dev/null | awk 'NR==2{print $4}')"
TMP_N="$(ls -d "${WT_DIR}"/tmp-* 2>/dev/null | wc -l | tr -d ' ')"

# ★数へ分ける★: 「積んで 居る 物」と「今 使はれて 居る 物」を 混ぜると 警告 が鳴り続け
# 読まれなく成る(= 常に鳴る 検 は 鳴らぬ 検 と 同じ)。
# ⑴掃ける= 中身 が commit 済(porcelain 0)★かつ★ 24 時 触られて 居らぬ
# ⑵持主 の言 が要る= 中身 が在る(未追跡/変更)
# ⑶生きて 居る= 24 時 以内 に触られた
SWEEPABLE=0; OWNED=0; LIVE=0
for d in "${WT_DIR}"/tmp-*; do
  [ -d "${d}" ] || continue
  dirty="$(git -C "${d}" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  recent="$(find "${d}" -maxdepth 0 -newermt '-24 hours' 2>/dev/null | wc -l | tr -d ' ')"
  if [ "${dirty}" != "0" ]; then OWNED=$((OWNED+1))
  elif [ "${recent}" != "0" ]; then LIVE=$((LIVE+1))
  else SWEEPABLE=$((SWEEPABLE+1)); fi
done

echo "[worktree-hygiene] free=${FREE_GI:-?}Gi 一時樹=${TMP_N}(掃ける=${SWEEPABLE} / 持主の言が要る=${OWNED} / 生きて居る=${LIVE})"

warn=0
if [ -n "${FREE_GI:-}" ] && [ "${FREE_GI}" -lt 20 ]; then
  echo "[worktree-hygiene] ★警告★ 空き ${FREE_GI}Gi < 20Gi ―― 走らせる 前 に掃け(lsof で使用中 0 を確かめてから)"
  warn=1
fi
# ★掃ける 物 だけ を数へて 警告 する★(生きて 居る 樹・持主 の物 で 鳴らさぬ)
if [ "${SWEEPABLE}" -gt 10 ]; then
  echo "[worktree-hygiene] ★警告★ ★掃ける★ 一時樹 ${SWEEPABLE} > 10 ―― 積み上がつて 居る"
  echo "[worktree-hygiene]   (中身 在り ${OWNED} は ★持主 の言 が要る★・生きて 居る ${LIVE} は ★触れぬ★)"
  warn=1
fi

# 器 の側: 後始末 が在るか
GATE="${REPO}/.claude/worktrees/dino-story-engine/frontend/scripts/dino-check-clean.sh"
if [ -f "${GATE}" ]; then
  for k in "worktree remove" "KEEP" "tmp-dino-clean-"; do
    grep -q "${k}" "${GATE}" || { echo "[worktree-hygiene] ★警告★ ${GATE##*/} に「${k}」が無い=後始末/上限/名 の限り の何れか が欠ける"; warn=1; }
  done
fi

[ "${warn}" -eq 0 ] && echo "[worktree-hygiene] 異常 無し"
exit 0
