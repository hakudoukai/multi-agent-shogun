# -*- coding: utf-8 -*-
"""★第八の守り ―― 送つた胴を臺帳から読み返す★。
送つた控(raw/90_dou_<便>.txt)と、`sb read seq <seq>` が返す胴を突き合はせる。
★rc=0 は「届いた」の意であつて「同じ物が載つた」の意ではない★ ―― 故に読み返す。
用法: python3 driver/95_yomikaeshi.py <便=seq> ...
"""
import io, os, subprocess, sys

KI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KI, "driver"))
import kaki as K
SB = os.path.expanduser("~/bin/sb")

gyo = []
for a in sys.argv[1:]:
    bin_, seq = a.split("=")
    okutta = io.open(os.path.join(KI, "raw", "90_dou_%s.txt" % bin_), encoding="utf-8").read().strip()
    p = subprocess.run([SB, "read", "seq", seq], capture_output=True)
    rc = p.returncode
    nama = p.stdout.decode("utf-8", "replace")
    # ★胴が丸ごと含まれて居るか★ で見る(臺帳は頭書きを添へる故 完全一致では測れぬ)
    iru = okutta in nama
    # ★字数も併せ見る★ ―― 「含まれる」だけでは切れて居ても気付かぬ事が在る
    gyo.append((bin_, seq, u"rc=%d" % rc, u"送=%d字" % len(okutta),
                u"臺帳の出=%d字" % len(nama.strip()),
                u"★丸ごと在り★" if iru else u"★欠け又は違ふ★"))
K.kaku_tsv(os.path.join(KI, "raw", "95_yomikaeshi.tsv"), gyo,
           header=(u"便", u"seq", u"読み返しの rc", u"送つた胴の字", u"臺帳が返した全文の字", u"判"))
warui = [g for g in gyo if u"丸ごと" not in g[5]]
for g in gyo:
    print(u" ".join(g))
assert not warui, u"★%d 便が臺帳で一致せぬ★" % len(warui)
