#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""控 ―― 測る相手の束を ★凍らせる★(歩いた根・刻・非通常 file の數を隠さず書く)。

相手は二つ:
  甲 = 第47弾の束(肥えた儘・96 本 10,938,664 byte と第48弾の紙に在る)
  乙 = 第48弾で ★痩せさせた写し★(97 本 3,041,808 byte ―― 束級の閾の 29.0%)
★乙こそ本弾の的である★ ―― 束級が通る束の中に、部材級が鳴る部材が在るか。
"""
import hashlib, os, sys, time

def kazoe(p):
    n = os.path.getsize(p)
    g = 0
    owari = True
    with open(p, "rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            g += b.count(b"\n")
            owari = b.endswith(b"\n")
    if n > 0 and not owari:
        g += 1
    return n, g

def aruku(root):
    reg, hi, na = [], [], []
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            st = os.lstat(p)
            import stat as S
            if not S.S_ISREG(st.st_mode):
                hi.append((p, oct(st.st_mode)))
                continue
            if "\n" in f or "\t" in f:
                na.append(p)
            reg.append(p)
    return sorted(reg), hi, na

print("刻(歩いた) = %s" % time.strftime("%Y-%m-%dT%H:%M:%S"))
tsv = sys.argv[1]
rows = []
for fuda, root in [("甲", sys.argv[2]), ("乙", sys.argv[3])]:
    print("―― %s 根 = %s" % (fuda, root))
    if not os.path.isdir(root):
        print("   ★根が無い★")
        continue
    reg, hi, na = aruku(root)
    wa = 0
    for p in reg:
        n, g = kazoe(p)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        wa += n
        rows.append((fuda, os.path.relpath(p, root), n, g, h))
    print("   常なる file = %d 本 / byte和 = %d" % (len(reg), wa))
    print("   ★非通常 file = %d 本★(0 でなく数へた) / ★名に改行・tab = %d 本★" % (len(hi), len(na)))
    for p, m in hi:
        print("     非通常: %s mode=%s" % (p, m))
with open(tsv, "w", encoding="utf-8") as fh:
    fh.write("fuda\trel\tbytes\tlines\tsha256\n")
    for r in rows:
        fh.write("%s\t%s\t%d\t%d\t%s\n" % r)
print("控 = %s(%d 行 ―― 冠一行を含む)" % (tsv, len(rows) + 1))
