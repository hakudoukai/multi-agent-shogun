#!/usr/bin/env bash
# km_hako_hantei.sh ―― 砂場の出目を★期する表と突合して 正 N/N を刷る★器
#
#   argv: <砂場の dir> <版の札: 前版|後版>
#
# 期する物（fixture 十一形・raw/40_fixtures.txt と同じ）:
#   顔  … 表（stdout）の Inbox 欄
#   診断 … stderr の一行（no-key / bad-shape / parse-fail）
#   母數 … 「★messages鍵無=N★(内 空帳=M)」の在不在と値
# ★前版は「鍵無の語が母數行に無い・no-key 行が 0 本」ことを期する★＝器自身の陰性対照。
set -uo pipefail
SAND="${1:?Usage: km_hako_hantei.sh <砂場> <前版|後版>}"
FUDA="${2:?}"
OUT="$SAND/out.txt"; ERR="$SAND/err.txt"
[[ -f "$OUT" && -f "$ERR" ]] || { echo "Error: 砂場に out.txt / err.txt が無い: $SAND" >&2; exit 2; }

SEKI="hideyoshi:2 ashigaru1:0 ashigaru2:0 ashigaru3:0 ieyasu:S takenaka:! maeda:S ashigaru5:0 ashigaru6:0 ashigaru7:0 ashigaru8:-"
OK=0; NG=0; TOTAL=0
say() { printf '  %-4s %s\n' "$1" "$2"; }
chk() { # $1=題 $2=期 $3=実
    TOTAL=$((TOTAL + 1))
    if [[ "$2" == "$3" ]]; then OK=$((OK + 1)); say 正 "$1  期=$2 実=$3"
    else NG=$((NG + 1)); say ★否★ "$1  期=$2 実=$3"; fi
}
echo "=== 判定 札=${FUDA} 砂場=${SAND} ==="
echo "■ 表の顔（十一席）"
for kv in $SEKI; do
    s="${kv%%:*}"; want="${kv##*:}"
    got=$(awk -v s="$s" '$1==s {print $NF}' "$OUT" | head -1)
    chk "顔 $s" "$want" "${got:-（無）}"
done
echo "■ stderr の診断行（本数）"
chk "no-key 行"    "$( [[ "$FUDA" == 前版 ]] && echo 0 || echo 3 )" "$(grep -c 'no-key' "$ERR" || true)"
chk "bad-shape 行" 2 "$(grep -c 'bad-shape' "$ERR" || true)"
chk "parse-fail 行" 1 "$(grep -c 'parse-fail' "$ERR" || true)"
echo "■ 母數行の常設欄"
if [[ "$FUDA" == 前版 ]]; then
    chk "鍵無欄の在否" "無" "$(grep -q 'messages鍵無' "$ERR" && echo 在 || echo 無)"
else
    chk "鍵無欄の在否" "在" "$(grep -q 'messages鍵無' "$ERR" && echo 在 || echo 無)"
    chk "鍵無の値" "★messages鍵無=3★(内 空帳=1)" \
        "$(grep -o '★messages鍵無=[0-9]*★(内 空帳=[0-9]*)' "$ERR" | head -1)"
    chk "註の行" 1 "$(grep -c '★註★ messages 鍵の無い箱' "$ERR" || true)"
fi
echo "--- 正=${OK}/${TOTAL}  否=${NG} ---"
[[ "$NG" -eq 0 ]] || exit 1
