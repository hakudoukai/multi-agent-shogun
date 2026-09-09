# -*- coding: utf-8 -*-
import io, re, sys, contextlib
g = {}
src = io.open("scratch/ashigaru-third-3-12e9d4bd/order239_e35_gap_v1.rule.py", encoding="utf-8").read()
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(compile(src, "gap_v1", "exec"), g)
scan = g["scan"]; mask = g["mask"]; F6 = g["F6"]; F8 = g["F8"]; OLDBO = g["OLDBO"]
papers = g["papers"]; letters = g["letters"]

def both(docs):
    out = []
    for lines in docs:
        for (i, w, ln) in scan(lines):
            m = mask(ln); prev = mask(lines[i-1]) if i > 0 else u""
            h6 = bool(F6.search(m)); h8 = bool(F8.search(m))
            mm9 = OLDBO.search(prev) or F6.search(prev) or F8.search(prev)
            if h8 and mm9 and not h6:
                out.append((w, F8.search(m).group(0), mm9.group(0), ln.strip(), lines[i-1].strip()))
    return out

for name, docs in ((u"letters", letters), (u"papers", papers)):
    b = both(docs)
    print(u"[%s] D_both=%d" % (name, len(b)))
    if name == u"letters":
        step = max(1, len(b) // 12)
        for k in range(0, min(12 * step, len(b)), step):
            w, a8, a9, ln, prv = b[k]
            print(u"--- #%d w=%s F8=%s F9=%s" % (k // step + 1, w, a8, a9))
            print(u"  cur: %s" % ln[:260])
            print(u"  prv: %s" % prv[:260])
