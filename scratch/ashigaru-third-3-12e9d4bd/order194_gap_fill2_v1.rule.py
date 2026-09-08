# -*- coding: utf-8 -*-
u"""追補其の三: (1) 拡張子の ★全★ 内訳(絞り無し) (2) 作業樹の byte が動くかを ★同じ走の中で二度測つて★ 実証
讀取のみ・走行 0・書込 0・DB 0。
"""
import os, io, hashlib
TREE = u"/home/hakudoukai/a3/wt-bundle-fix4"
SKIPD = set([u"node_modules", u".git", u".venv", u"venv", u"__pycache__"])

def pass_once():
    walked = 0; ok = set(); bad = {}
    for dp, dn, fn in os.walk(TREE):
        dn[:] = [x for x in dn if x not in SKIPD]
        for f in fn:
            ap = os.path.join(dp, f); rel = os.path.relpath(ap, TREE)
            walked += 1
            try:
                io.open(ap, encoding="utf-8").read()
                ok.add(rel)
            except Exception as e:
                bad[rel] = type(e).__name__
    return walked, ok, bad

w1, ok1, bad1 = pass_once()
w2, ok2, bad2 = pass_once()

print(u"## (1) 拡張子の ★全★ 内訳（絞り無し・第一走）")
print(u"walked=%d readable=%d unreadable=%d" % (w1, len(ok1), len(bad1)))
ext = {}
for rel in bad1:
    e = (os.path.splitext(rel)[1] or u"(拡張子なし)").lower()
    ext[e] = ext.get(e, 0) + 1
tot = 0
for e, n in sorted(ext.items(), key=lambda x: (-x[1], x[0])):
    print(u"  %-16s %5d" % (e, n)); tot += n
print(u"ext_kinds=%d  ext_sum=%d  (母数 %d と一致=%s)" % (len(ext), tot, len(bad1), tot == len(bad1)))

print(u"")
print(u"## (2) 二度測り（同じ走の中・器を一字も変へず）")
print(u"walked: 1st=%d 2nd=%d  同じ=%s" % (w1, w2, w1 == w2))
print(u"readable: 1st=%d 2nd=%d  差=%d" % (len(ok1), len(ok2), len(ok2) - len(ok1)))
a = sorted(ok1 - ok2); b = sorted(ok2 - ok1)
print(u"1st_only=%d 2nd_only=%d" % (len(a), len(b)))
for r in a[:15]: print(u"  1st_only | %s" % r)
for r in b[:15]: print(u"  2nd_only | %s" % r)

print(u"")
print(u"## (3) 讀めなんだ集合の ★指紋★（次回比較の種・名は紙へ写さぬ）")
h = hashlib.sha256(); h.update(u"\n".join(sorted(bad1)).encode("utf-8"))
print(u"unreadable_set_sha256=%s  n=%d" % (h.hexdigest(), len(bad1)))
h2 = hashlib.sha256(); h2.update(u"\n".join(sorted(ok1)).encode("utf-8"))
print(u"readable_set_sha256=%s  n=%d" % (h2.hexdigest(), len(ok1)))
