# -*- coding: utf-8 -*-
"""納め便を組み ★字数を python3 の len で測る★(札の條=300字)。

  usage: python3 -B driver/97_fumi.py <束の根>
rc=0 = 條を満つ / rc=7 = ★300字超 ∴ 一字も書かず止まる(fail-closed)★
胴の中の數は ★raw から引く★(手で打てば古びる)。
"""
import os
import sys
from importlib import import_module

sys.path.insert(0, __file__.rsplit("/", 1)[0])
K = import_module("00_kaki")

JOU = 300


def load(p):
    rows, h = [], None
    for ln in open(p, encoding="utf-8"):
        c = ln.rstrip("\n").split("\t")
        if h is None:
            h = c
            continue
        if c and c[0]:
            rows.append(dict(zip(h, c)))
    return rows


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    raw = os.path.join(root, "raw")
    sw = load(raw + "/81_shiwake.tsv")
    ry = load(raw + "/37_ryoumuki.tsv")
    ku = load(raw + "/41_kusari.tsv") if os.path.getsize(raw + "/41_kusari.tsv") > 60 else []
    n = len(sw)
    kou = sum(1 for r in sw if r["甲乙丙"].startswith("甲"))
    otsu = sum(1 for r in sw if r["甲乙丙"].startswith("乙"))
    hei = sum(1 for r in sw if r["甲乙丙"].startswith("丙"))
    butsu = [r for r in ry if r["★自前 ∩ main側★"] != "0"]
    mtxt = open(raw + "/36_ryoumuki_main.txt", encoding="utf-8").read().split("\n")
    mc = [x.split("= ", 1)[1] for x in mtxt if x.startswith("main 側 commit")][0]
    mf = [x.split("= ", 1)[1] for x in mtxt if x.startswith("main 側 file")][0]
    ichi = open(os.path.join(root, "README.md"), encoding="utf-8").read().split("\n")[0]
    rc = ichi.split("門 rc=")[1].split(" ")[0]

    hon = (
        "專任3 km-102 納。割当%d本=★悉く甲(着地)★乙%d丙%d。"
        "拠り所五つ悉く外れ＝★捨てて良い證が立たぬ★の意、PR可の證に非ず。判は軍師。"
        "鎖0対・%d本悉く末端∴末端のみ着地は効かぬ。"
        "main側も分岐点から%scommit%sfile進み衝突は%d本のみ(km-82/lot48)。"
        "★臺帳の器 karo_mac_manifest_append.py は main にも60枝にも無くdiskのみ★"
        "門の器もmainに無し∴器を運ぶ枝が先。"
        "束=docs/evidence/ashigaru-mac-3_km-102…/ 門rc=%s。軍師mac死箱ゆゑ代送乞ふ。"
        % (n, otsu, hei, n, mc, mf, len(butsu), rc)
    )
    ji = len(hon)
    sys.stderr.write("字数=%d(條 %d)\n" % (ji, JOU))
    if ji > JOU:
        sys.stderr.write("★條を超えた ∴ 一字も書かず止まる(超過 %d 字)★\n" % (ji - JOU))
        K.kaku(os.path.join(raw, "96_fumi_shitagaki.txt"),
               "★條超過ゆゑ本便に非ず(下書)★ 字数=%d / 條=%d\n\n%s" % (ji, JOU, hon))
        return 7
    K.kaku(os.path.join(raw, "96_fumi.txt"), hon)
    K.kaku(os.path.join(raw, "96_fumi_ji.txt"),
           "字数(python3 len)=%d\n條=%d\n残り=%d\n測つた胴=raw/96_fumi.txt" % (ji, JOU, JOU - ji))
    return 0


sys.exit(main())
