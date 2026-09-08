#!/usr/bin/env bash
# 断ずる前 の 一 行 確かめ(警告 のみ・止めぬ)。
# 使ひ方: verify_state_before_asserting.sh manifest <path>
#         verify_state_before_asserting.sh push <asked-sha> <branch> [repo]
#         verify_state_before_asserting.sh remote [repo]
#         verify_state_before_asserting.sh letter <file>   ← ★便 を出す前 に己 を斬る★
#         verify_state_before_asserting.sh paper  <file>   ← ★測つた 紙 に『版』が在るか★
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
  paper)
    # ★2026-09-08 B0-15★: 家老 の門 の四点⑴ は「紙 の commit」を記すが
    # ★測つた 製品 の版★ を記す 欄 が無かつた。故 に B5-15 の「1 話 101.9 秒」が
    # ★何 の版 の秒 か 辿れず★、後 で 8 行 版 の秒 と判つた(今 は 14 行)。
    # ★秒・fps・字数 は 台本 の版 に付く★ ―― 版 の無い 測定 は 後 で引けぬ。
    f="${1:-}"; [ -f "${f}" ] || { echo "[verify] 紙 無し: ${f}"; exit 0; }
    t="$(cat "${f}")"
    if printf '%s' "${t}" | grep -qE '[0-9]+(\.[0-9]+)? ?(秒|ms|fps|字/秒)'; then
      # ★此 の器 は「版 が在るか」を判ぜぬ★ ―― 三 度 試みて 三 度 とも 判ぜなんだ:
      #   ⑴ hex 7-40 桁 → ★板 の番号★ に当つた(48235904 / 8c2d7119)
      #   ⑵ sha256 を除く → 紙 の sha と 製品 の commit が ★同 じ形★
      #   ⑶ 『commit』の語 + hex → B5-15 は 語 を 1 度 持つ が ★版 を留めて 居らぬ★
      # ∴ ★判ずる 振り を せぬ★。★測定 が在る 事 だけ を告げ、判 は 人 に返す★。
      echo "[verify] ★測定 が在る(秒/fps/字/秒)★ ―― ★問へ: 此 の数 は ★何 の版★ の数 か★"
      echo "         ★秒 は台本 の版 に付く★(B0-15: 『1 話 101.9 秒』は ★8 行 版★ の秒・今 は 14 行)"
      echo "         ★此 の器 は版 の有無 を判ぜぬ(hex も 語 も 版 と紛れる)★ ―― ★人 が見よ★"
      hit=1
    else
      echo "[verify] 紙 ―― 秒/fps の主張 は見当らぬ(版 の検 は課さず)"
    fi
    ;;
  letter)
    # ★本日 十三度 同型 を踏んだ 故 に 器 に させる(2026-09-08)★
    # 「書くだけでは直らぬ」を 己 で証した ―― 之 は其 の機構 で ある。止めぬ・警告 のみ。
    f="${1:-}"; [ -f "${f}" ] || { echo "[verify] 便 無し: ${f}"; exit 0; }
    t="$(cat "${f}")"; hit=0
    # ⑴ 未 push・残り を言ふ なら fetch を先 に走らせたか
    if printf '%s' "${t}" | grep -qE '未 ?push|残り|待ち|pending'; then
      last="$(find "${TMPDIR:-/tmp}" -maxdepth 1 -name '.vsba_fetch_*' -newermt '-10 minutes' 2>/dev/null | head -1)"
      [ -n "${last}" ] || { echo "[verify] ★止まれ★ 便 が「未 push/残り」を言ふ ―― ★10 分 内 の fetch の跡 が無い★"; echo "         → git fetch -q origin && touch \"${TMPDIR:-/tmp}/.vsba_fetch_$$\" を先 に"; hit=1; }
    fi
    # ⑵ 数 を言ふ なら 母數 を併せ書いたか
    if printf '%s' "${t}" | grep -qE '[0-9]+ ?(件|本|紙|file|行)'; then
      printf '%s' "${t}" | grep -qE '母數|母数|中|/[0-9]+|分母' || { echo "[verify] ★註★ 数 を言うて 居るが ★母數 が無い★(『67 紙』が実 73・内 1 は器 自身 で 72 で あつた)"; hit=1; }
    fi
    # ⑶ 0 を言ふ なら rc を添へたか
    if printf '%s' "${t}" | grep -qE '(^|[^0-9])0 ?(件|本|行)|該当 ?無|無一致'; then
      printf '%s' "${t}" | grep -qE 'rc ?=' || { echo "[verify] ★註★ 0 を言うて 居るが ★rc が無い★(0/0 は 数 に非ず 器 の不調 の報せ)"; hit=1; }
    fi
    # ⑷ ★「未測/無し/誰も〜せぬ」を言ふ なら 既 に在る 紙 を掃いたか★
    #    (2026-09-08 B0-14: 家老 は「キラモン の秒 は未測」と書いた が ―― 席 が前日 に
    #     実測 して 居り、★其の数 は家老 自身 の状況板 に載つて 居た★。十五 度目 の同型。)
    if printf '%s' "${t}" | grep -qE '未測|未計測|測つて 居らぬ|測られて 居らぬ|誰 ?も|一度 ?も|初めて|存在 ?せぬ'; then
      # ★掃いた 跡 が 便 の中 に在れば 黙る★ ―― 常 に鳴る 註 は 読まれなく成る。
      # ★抑へ は「掃いた と言ふ 語」だけ に限る★ ―― B 番号 や「既 に」で黙らせると
      # ★誤 便 其の物 が素通り する★(実測: 本日 の l13『キラモン の秒 は未測』が通つた)。
      if printf '%s' "${t}" | grep -qE '掃い|grep|queue/reports|実測 済|測 ?済|確かめ'; then
        :
      else
        echo "[verify] ★註★ 「未測/無し」を言うて 居る ―― ★出す前 に 己 の板 と 席 の紙 を掃いたか★"
        echo "         → grep -rl '<其の物 の名>' queue/reports/ docs/ ; ★己 の状況板 も母數 に入れよ★"
        hit=1
      fi
    fi
    [ "${hit}" = 0 ] && echo "[verify] 便 ―― 四 つ の常 の穴(fetch・母數・rc・既知)は 見当らぬ"
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
