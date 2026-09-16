#!/bin/sh
# ㋒ の静かな対照 ―― ★一通も出さず★、契約照合器(20_keiyaku.py)にだけ掛ける。
#   陽性=鳴るべき形 / 陰性=鳴つてはならぬ形。両方を出さねば「鳴らぬ器」と区別が付かぬ。
P=/opt/homebrew/bin/python3
K=raw/20_keiyaku.py
echo "=== ㋒-1 陽性対照: 家老の誤形(宛先を胴の位置へ) ==="
$P $K --cmd 'sb write letter gunshi-mac "胴の文" --parent-seq 321131'
echo "=== ㋒-2 陰性対照: 正形(--to で名指す) ==="
$P $K --cmd 'sb write letter "胴の文" --to gunshi-mac --parent-seq 321131'
echo "=== ㋒-3 陽性対照(家の器): inbox_write.sh へ引数を一つ欠いて渡す ==="
$P $K --cmd 'bash scripts/inbox_write.sh karo-mac "胴" report_received'
echo "=== ㋒-4 陰性対照(家の器): 正形 ==="
$P $K --cmd 'bash scripts/inbox_write.sh karo-mac "胴" report_received ashigaru-mac-2'
echo "=== ㋒-5 陽性対照(第二形): env は満たすが引数が一つ足らぬ ==="
$P $K --cmd 'INBOX_WRITE_CONTENT_STDIN=1 bash scripts/inbox_write.sh karo-mac report_received ashigaru-mac-2'
echo "=== ㋒-6 陰性対照(第二形): env と __VIA_STDIN__ を備へた正形 ==="
$P $K --cmd 'INBOX_WRITE_CONTENT_STDIN=1 bash scripts/inbox_write.sh karo-mac __VIA_STDIN__ report_received ashigaru-mac-2'
