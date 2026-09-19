#!/usr/bin/env bash
# km_hako_ryoutaishou.sh ―― 箱の同型（messages 鍵無 vs 空）を ★前後二版★ で両対照する器
#
#   argv: <走らせる版の file> [<札>]
#   例  : bash kiki/km_hako_ryoutaishou.sh /tmp/km_zenban.sh 前版
#
# ★稼働中の箱には触れぬ★ ―― mktemp -d の砂場へ scripts/ lib/ config/ を写し、
# 束の fixtures/*.yaml を砂場の queue/inbox/ へ置いて project 路を走らせる。
# 出目: 砂場の path / argv / rc / 母數行 を stdout へ逐語で刷る。
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
BUNDLE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${1:?Usage: km_hako_ryoutaishou.sh <走らせる版の file> [札]}"
FUDA="${2:-無札}"

[[ -f "$SRC" ]] || { echo "Error: 走らせる版が無い: $SRC" >&2; exit 2; }

SAND="$(mktemp -d /tmp/km_hako_XXXXXX)"
mkdir -p "$SAND/scripts" "$SAND/queue/inbox"
# ★写すのは読む物だけ★（scripts/ は丸ごと・lib/ と config/ も器が読む）
cp -R "$REPO/lib" "$SAND/lib"
cp -R "$REPO/config" "$SAND/config"
for f in "$REPO"/scripts/*.sh; do cp "$f" "$SAND/scripts/"; done
[[ -d "$REPO/scripts/checks" ]] && cp -R "$REPO/scripts/checks" "$SAND/scripts/checks"
# ★器の python を砂場へ★ ―― 無いと PYTHON_AVAILABLE=false で箱を一つも読まぬ
#   （実測: 写さずに走らせた前版は「器無=11／箱: 数に非ざる顔=11」＝箱の中身を一切見て居らぬ）
# ★写さず 読取の symlink を張る★ ―― .venv は pyvenv.cfg と site-packages で一体ゆゑ
#   bin/python3 だけ写すと sys.prefix が砂場を指し yaml が落ちる（実測で確めた）。
if [[ -d "$REPO/.venv" ]]; then
    ln -s "$REPO/.venv" "$SAND/.venv"
fi
if [[ -x "$SAND/.venv/bin/python3" ]]; then
    PY_OK="在り（$("$SAND/.venv/bin/python3" -c 'import sys;print(sys.version.split()[0])' 2>&1)）"
else
    PY_OK="★無し★"
fi

# ★測る版を据ゑる★（scripts/ の下ゆゑ SCRIPT_DIR は砂場の根を指す）
cp "$SRC" "$SAND/scripts/km_hako_target.sh"
# ★fixtures を箱へ★
#   KM_HAKO_ONLY="hideyoshi ashigaru1" と与へれば其の席のみ置く（★常設の陰性対照★ ――
#   鍵在の箱だけを置いた走で「messages鍵無=0」が刷られる事を測る為）。
ONLY="${KM_HAKO_ONLY:-}"
n_fx=0
for f in "$BUNDLE"/fixtures/*.yaml; do
    [[ -e "$f" ]] || continue
    bn="$(basename "$f" .yaml)"
    if [[ -n "$ONLY" ]]; then
        keep=false
        for k in $ONLY; do [[ "$k" == "$bn" ]] && keep=true; done
        $keep || continue
    fi
    cp "$f" "$SAND/queue/inbox/${bn}.yaml"
    n_fx=$((n_fx + 1))
done

echo "=== 札=${FUDA} ==="
echo "走らせた版   = ${SRC}"
echo "版の sha256  = $(shasum -a 256 "$SRC" | awk '{print $1}')"
echo "砂場         = ${SAND}"
echo "砂場の python = ${PY_OK}"
echo "置いた箱     = ${n_fx} 本（KM_HAKO_ONLY="${ONLY:-（無指定＝悉く）}"）"
echo "箱の一覧     :"
for f in "$SAND"/queue/inbox/*.yaml; do
    printf '  %-24s %6s byte\n' "$(basename "$f")" "$(wc -c < "$f" | tr -d ' ')"
done
echo "cwd          = ${SAND}"
echo 'argv         = bash scripts/km_hako_target.sh'
set +e
( cd "$SAND" && bash scripts/km_hako_target.sh ) >"$SAND/out.txt" 2>"$SAND/err.txt"
RC=$?
set -e
echo "rc           = ${RC}"
echo "--- 母數行（stderr より抜く）---"
grep '^\[agent_status\]' "$SAND/err.txt" || echo "（母數行 無し）"
echo "--- 表の Inbox 欄（stdout・席と顔のみ）---"
awk 'NF>=3 && ($1 ~ /^(hideyoshi|ashigaru[0-9]|ieyasu|takenaka|maeda)$/) {printf "  %-12s %s\n", $1, $NF}' "$SAND/out.txt"
echo "--- stdout 行数=$(grep -c '' "$SAND/out.txt" || true) / stderr 行数=$(grep -c '' "$SAND/err.txt" || true) ---"
echo "砂場は消さぬ（検分の為）: ${SAND}"
