#!/usr/bin/env bash
# 断ずる前 の 一 行 確かめ(警告 のみ・止めぬ)。
# 使ひ方: verify_state_before_asserting.sh manifest <path>
#         verify_state_before_asserting.sh push <asked-sha> <branch> [repo]
#         verify_state_before_asserting.sh remote [repo]
set -uo pipefail
mode="${1:-}"; shift || true

case "${mode}" in
  manifest)
    m="${1:-}"; [ -f "${m}" ] || { echo "[verify] manifest 無し: ${m}"; exit 0; }
    echo "[verify] ★形式 を見よ★:"; head -5 "${m}"
    if grep -qi "正規化\|normali" "${m}"; then
      echo "[verify] ★註★ 此 の manifest は ★正規化後★ の sha ―― 生 byte で hash すると 落ちる"
    fi
    if grep -qE '^[0-9a-f]{12}[^0-9a-f]' "${m}"; then
      echo "[verify] ★註★ 12 桁 の頭 が在る ―― 64 桁 で grep すると 見付からぬ"
    fi
    ;;
  push)
    a="${1:-}"; b="${2:-}"; r="${3:-$PWD}"
    # ★己 の入力 が解けたか を先 に見る★ ―― 解けぬ 物 を「無い」と言つて はならぬ
    # (2026-09-08: 本 検 の陽性対照 が 此処 で落ちた。局所 に枝 が無く remote にのみ在る 時、
    #  旧版 は「頭 に無い」と ★偽 を言つた★)。
    ref=""
    for cand in "${b}" "origin/${b}" "refs/heads/${b}" "refs/remotes/origin/${b}"; do
      if git -C "${r}" rev-parse --verify --quiet "${cand}" >/dev/null 2>&1; then ref="${cand}"; break; fi
    done
    if [ -z "${ref}" ]; then
      echo "[verify] ★解決 できぬ★: 枝 '${b}' は 局所 にも origin にも 無い ―― ★『無い』とは 言はず 先 に fetch せよ★"
      exit 0
    fi
    h="$(git -C "${r}" rev-parse "${ref}" 2>/dev/null)"
    echo "[verify] 枝 ${ref} の頭= ${h}"
    if git -C "${r}" merge-base --is-ancestor "${a}" "${ref}" 2>/dev/null; then
      echo "[verify] ${a} は ${ref} に ★在る★"
    else
      echo "[verify] ★警告★ ${a} は ${ref} の ★頭 に無い★ ―― 押すと 求められた 物 と 別 の物 が出る"
    fi
    ;;
  remote)
    r="${1:-$PWD}"
    git -C "${r}" fetch -q origin 2>/dev/null
    echo "[verify] origin/main= $(git -C "${r}" rev-parse --short origin/main 2>/dev/null || echo '?') (fetch 済)"
    ;;
  *)
    echo "usage: $0 manifest <path> | push <sha> <branch> [repo] | remote [repo]" >&2
    ;;
esac
exit 0
