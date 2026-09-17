#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★門の前に己で掃く★ ―― 條②(行末空白) 條③(CR混入) 條④(EOF改行 丁度1)を先に測る。
門に教はるのではなく、己で直せる物は先に直す。直せぬ物(器の自産物)は ★宣して除く★(第四の道)。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
RAW = os.path.join(BUNDLE, "raw")
sys.path.insert(0, RAW)
from kaki import kaku, kaku_tsv          # noqa: E402

NOZOKU_KEI = ("MANIFEST.txt", "_gate/")


def aruki(root):
    out = []
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for f in sorted(fn):
            full = os.path.join(dp, f)
            if os.path.isfile(full) and not os.path.islink(full):
                out.append(os.path.relpath(full, root))
    return sorted(out)


def main():
    rows, naru = [], []
    for rel in aruki(BUNDLE):
        p = os.path.join(BUNDLE, rel)
        b = open(p, "rb").read()
        n = len(b)
        cr = b.count(b"\r")
        matsu = 0
        for ln in b.split(b"\n"):
            if ln.rstrip(b" \t") != ln:
                matsu += 1
        if n == 0:
            eof = "0byte"
        elif not b.endswith(b"\n"):
            eof = "改行無"
        elif b.endswith(b"\n\n"):
            eof = "改行2以上"
        else:
            eof = "丁度1"
        warui = (cr > 0) or (matsu > 0) or (eof != "丁度1")
        jogai = rel == "MANIFEST.txt" or rel.startswith("_gate/")
        rows.append([rel, n, matsu, cr, eof, "鳴る" if warui else "清", "除外形" if jogai else "本文"])
        if warui:
            naru.append((rel, matsu, cr, eof, jogai))
    print("束 %s" % os.path.relpath(BUNDLE, os.path.dirname(os.path.dirname(BUNDLE))))
    print("歩いた本 %d" % len(rows))
    print("★鳴る本 %d★" % len(naru))
    for rel, matsu, cr, eof, jogai in naru:
        print("  %s 行末空白%d CR%d EOF=%s %s" % (rel, matsu, cr, eof, "(除外形)" if jogai else "★本文★"))
    honbun_naru = [x for x in naru if not x[4]]
    print("★本文で鳴る本 = %d★ ―― 0 でなければ ★己で直せ★" % len(honbun_naru))
    kaku_tsv(os.path.join(RAW, "85_zensa.tsv"), rows,
             header=["path", "bytes", "行末空白の行", "CR", "EOF", "判", "形"])
    return 0 if not honbun_naru else 1


if __name__ == "__main__":
    sys.exit(main())
