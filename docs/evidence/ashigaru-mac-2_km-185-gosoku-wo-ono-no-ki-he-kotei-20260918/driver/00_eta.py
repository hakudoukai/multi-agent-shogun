# -*- coding: utf-8 -*-
"""00 ―― 宣ETA の胴を書き、★書く前でなく送る前に己で字を測る★。
★assert は書込の前に置く★(裁333131⑵・家老が己の疵から学んだ形)。
胴は 90_fumi.py が改めて測り直す ―― 二度測るのは器の取り違へを防ぐ為。
"""
import io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
KI = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kaki as K  # noqa: E402

DOU = {}

DOU["eta185"] = u"""km-185 宣ETA ―― 19:54 受領。己の樹 ~/wt/a2-km171・a2-km172・a2-km174 を
origin/main 6bde7170ce574090a6139ba2dfe3aa4cb6db8634 から三枝切り、五束を git add -f と
git commit --only で固定する。★宣ETA=20:50★。紙の數は家老と一致 ―― 59/71/61/71/52(計314・全歩き)。
★宣ETA は實績に非ず ―― 當席の過去の宣は實に対し1.8〜6倍外して居る。★"""

DOU["eta186"] = u"""km-186 宣ETA=★21:40★(km-185 の後に着手・順は priority に従ふ)。
origin/main 6bde7170 の git ls-tree -r --name-only を母數とし casefold で括つて双子を悉く出す。
紙のみ ―― 双子の片方を消さず・直さず・据ゑぬ。束=docs/evidence/ashigaru-mac-2_km-186-oomoji-komoji-no-futago-20260918/。
★測れぬ物=case-sensitive な Linux 側(second/third PC)での見え方 ―― 當席の disk では測れぬ。★"""

rows = []
for k in sorted(DOU):
    dou = u"".join(DOU[k].split(u"\n"))
    ji = len(dou)
    print(u"%s 字(unicode文字)=%d" % (k, ji))
    assert ji <= 300, u"★%s が %d字 ―― 書く前に止めた★" % (k, ji)
    K.kaku(os.path.join(KI, "raw", "00_src_%s.txt" % k), dou)
    rows.append((k, ji))
K.kaku_tsv(os.path.join(KI, "raw", "00_ji.tsv"), rows, header=("bin", "ji_unicode_moji"))
