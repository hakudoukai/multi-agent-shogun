# -*- coding: utf-8 -*-
# order247 / E43 gate: how big are the F8-only and F9-only pools?
# purpose: decide whether the inherited sample size 12 can be replaced by a
# second disjoint sample (replication) or by the whole pool (census).
import io, sys, contextlib
src = io.open("scratch/ashigaru-third-3-12e9d4bd/order239_e35_gap_v1.rule.py",
              encoding="utf-8").read()
g = {"__name__": "__gap__"}
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(compile(src, "gap_v1", "exec"), g)

scan = g["scan"]; mask = g["mask"]
F6 = g["F6"]; F8 = g["F8"]; OLDBO = g["OLDBO"]

def pools(docs):
    o8 = []; o9 = []; both = []; o6 = []
    for lines in docs:
        for (i, w, ln) in scan(lines):
            m = mask(ln)
            prev = mask(lines[i - 1]) if i > 0 else u""
            h6 = bool(F6.search(m))
            h8 = bool(F8.search(m))
            m9 = OLDBO.search(prev) or F6.search(prev) or F8.search(prev)
            if h6:
                o6.append((w, ln.strip()))
            elif h8 and m9:
                both.append((w, ln.strip()))
            elif h8:
                o8.append((w, ln.strip()))
            elif m9:
                o9.append((w, ln.strip()))
    return o6, o8, o9, both

for nm, docs in ((u"letters", g["letters"]), (u"papers", g["papers"])):
    o6, o8, o9, bo = pools(docs)
    print(u"[%s] F6only=%d  F8only=%d  F9only=%d  both=%d" %
          (nm, len(o6), len(o8), len(o9), len(bo)))
    print(u"   -> F8only: 12 sampled = %.1f%% of pool ; second disjoint 12 %s"
          % (100.0 * 12 / max(1, len(o8)), u"reachable" if len(o8) >= 24 else u"NOT reachable"))
    print(u"   -> F9only: 12 sampled = %.1f%% of pool ; second disjoint 12 %s"
          % (100.0 * 12 / max(1, len(o9)), u"reachable" if len(o9) >= 24 else u"NOT reachable"))
