# -*- coding: utf-8 -*-
# order241 / E37: F8(unit-gap) と F9(prev-line) の ★偽陽性★ を手で當てる為の抽出器。
# 走 0 / 讀取のみ / 一時 file 0。gap_v1 を exec で読み込み、測る部は一字も変へぬ(條 o174)。
import io, os, re, sys, contextlib, collections

D = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(D, u"order239_e35_gap_v1.rule.py")
g = {"__name__": "__main__"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(io.open(G, encoding="utf-8").read(), G, "exec"), g)

scan = g["scan"]; mask = g["mask"]; F6 = g["F6"]; F8 = g["F8"]; OLDBO = g["OLDBO"]

def collect(docs):
    only8 = []; only9 = []
    for lines in docs:
        for (i, w, ln) in scan(lines):
            m = mask(ln)
            prev = mask(lines[i-1]) if i > 0 else u""
            h6 = bool(F6.search(m)); h8 = bool(F8.search(m))
            h9 = bool(OLDBO.search(prev) or F6.search(prev) or F8.search(prev))
            if h8 and not h6 and not h9:
                only8.append((w, F8.search(m).group(0), ln.strip(), u""))
            elif h9 and not h6 and not h8:
                mm = OLDBO.search(prev) or F6.search(prev) or F8.search(prev)
                only9.append((w, mm.group(0), ln.strip(), lines[i-1].strip()))
    return only8, only9

for name in (u"letters", u"papers"):
    o8, o9 = collect(g[name])
    print(u"[%s] only_F8=%d only_F9=%d" % (name, len(o8), len(o9)))

o8, o9 = collect(g["letters"])
print(u"")
print(u"=== letters: F8 単独 12 件 ===")
for k, (w, hit, ln, _) in enumerate(o8[:12]):
    print(u"%2d [%s] F8=%r" % (k+1, w, hit))
    print(u"    %s" % ln[:150])
print(u"")
print(u"=== letters: F9 単独 12 件 ===")
for k, (w, hit, ln, prv) in enumerate(o9[:12]):
    print(u"%2d [%s] prev_hit=%r" % (k+1, w, hit))
    print(u"    prev: %s" % prv[:130])
    print(u"    cur : %s" % ln[:130])
