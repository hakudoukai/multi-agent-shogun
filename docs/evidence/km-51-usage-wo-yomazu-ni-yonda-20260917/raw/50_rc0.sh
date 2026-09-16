#!/bin/sh
# ㋓ ―― ★rc=0 で通る誤り★ の族を、己の束の中で現に鳴らして見せる。
P=/opt/homebrew/bin/python3
K=raw/20_keiyaku.py
echo "=== 丁: 照合器が「否」と鳴いても、走らせた殻の rc は 0 ==="
sh raw/34_taishou.sh > /dev/null 2>&1
echo "  34_taishou.sh 全体の rc = $? ／ 其の出力の中の 否 の数 = $(grep -c '^\[否\]' raw/35_taishou.out)"
echo "  ―― ★同じ 0 が「誤り無し」と「誤りを見つけた」の両方を着る★"
echo "  観測できる欄: 在る(標準出力の [否] の行)。然れど ★rc だけ見る者には無い★。"
echo "--- 丁の治し: 判を rc に載せる(--kibishi) ---"
$P $K --kibishi --cmd 'sb write letter gunshi-mac "胴の文"' > /dev/null 2>&1
echo "  陽性(誤形) rc = $?  ★1 で鳴る★"
$P $K --kibishi --cmd 'sb write letter "胴の文" --to gunshi-mac' > /dev/null 2>&1
echo "  陰性(正形) rc = $?  ★0 で黙る★"

echo "=== 戊: py_compile は rc=0 で通り、走らせた時に死ぬ ==="
cat > raw/52_rei_kowareta.py <<'EOF'
# ★作り物(fixture)★ ―― 戊の陽性対照。字は正しく、走れば死ぬ。
import shlex
print(len(shlex.split('sb write letter "本文')))      # ★閉ぢぬ引用★ ゆゑ ValueError
EOF
$P -m py_compile raw/52_rei_kowareta.py > /dev/null 2>&1
echo "  py_compile の rc = $?  ★0(通る)★"
$P raw/52_rei_kowareta.py > /dev/null 2>&1
echo "  走らせた時の rc = $?  ★1(死ぬ)★"
echo "  観測できる欄: ★無い★ ―― compile の出目に、実行時の契約違反を映す欄は無い。"
echo "  (之が己の疵 51-A の形。初版は compile を通り、corpus を食はせた時に ValueError で倒れた)"
