#!/usr/bin/env bash
# 一時 worktree の衛生 を検める(警告 のみ・止めぬ)。
# 出典: skills/ephemeral-worktree-hygiene/SKILL.md ・ 2026-09-08 disk 満杯 事故。
set -uo pipefail

REPO="${1:-/Users/momizimac/DentalBI}"
WT_DIR="${REPO}/.claude/worktrees"
FREE_GI="$(df -g "${REPO}" 2>/dev/null | awk 'NR==2{print $4}')"
TMP_N="$(ls -d "${WT_DIR}"/tmp-* 2>/dev/null | wc -l | tr -d ' ')"

echo "[worktree-hygiene] free=${FREE_GI:-?}Gi 一時樹=${TMP_N}"

warn=0
if [ -n "${FREE_GI:-}" ] && [ "${FREE_GI}" -lt 20 ]; then
  echo "[worktree-hygiene] ★警告★ 空き ${FREE_GI}Gi < 20Gi ―― 走らせる 前 に掃け(lsof で使用中 0 を確かめてから)"
  warn=1
fi
if [ "${TMP_N}" -gt 10 ]; then
  echo "[worktree-hygiene] ★警告★ 一時樹 ${TMP_N} > 10 ―― 積み上がつて 居る 疑ひ"
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
