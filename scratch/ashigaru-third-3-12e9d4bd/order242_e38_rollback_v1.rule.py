# -*- coding: utf-8 -*-
# order242 / E38: F8/F9 の手當て精度(7/12・3/12)を 之迄の「母有」の数へ当て直す器。
# 走 0 / 讀取のみ / 一時 file 0。gap_v1 を exec で読み込み、測る部は一字も変へぬ(條 o174)。
# ★割り戻しは ★推し★ である。器が刷る値は観測に非ず、仮定を通した数である。
import io, os, contextlib, collections

D = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(D, u"order239_e35_gap_v1.rule.py")
g = {"__name__": "__main__"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(io.open(G, encoding="utf-8").read(), G, "exec"), g)
scan = g["scan"]; mask = g["mask"]; F6 = g["F6"]; F8 = g["F8"]; OLDBO = g["OLDBO"]

def partition(docs):
    c = collections.Counter()
    for lines in docs:
        for (i, w, ln) in scan(lines):
            m = mask(ln)
            prev = mask(lines[i-1]) if i > 0 else u""
            h6 = bool(F6.search(m)); h8 = bool(F8.search(m))
            h9 = bool(OLDBO.search(prev) or F6.search(prev) or F8.search(prev))
            c[u"T"] += 1
            if not (h6 or h8 or h9):
                c[u"residue"] += 1; continue
            c[u"covered"] += 1
            if h6:                 c[u"A_F6any"] += 1
            elif h8 and not h9:    c[u"B_F8only"] += 1
            elif h9 and not h8:    c[u"C_F9only"] += 1
            else:                  c[u"D_both"] += 1
    return c

def roll(c, p8, p9, drop_A=False):
    A = 0 if drop_A else c[u"A_F6any"]
    both = 1.0 - (1.0 - p8) * (1.0 - p9)   # ★独立の仮定★(未検証)
    v = A + c[u"B_F8only"] * p8 + c[u"C_F9only"] * p9 + c[u"D_both"] * both
    return v, 100.0 * v / c[u"T"]

CASES = [
    (u"上限(割り戻さず)",        1.0,       1.0,      False),
    (u"行基準(11/12, 8/11)",   11/12.0,   8/11.0,   False),
    (u"当たり基準(7/12, 3/12)", 7/12.0,    3/12.0,   False),
    (u"感度 -1件づつ",          6/12.0,    2/12.0,   False),
    (u"感度 +1件づつ",          8/12.0,    4/12.0,   False),
    (u"極小(F6 も 0 と置く)",    7/12.0,    3/12.0,   True),
]

for name in (u"letters", u"papers"):
    c = partition(g[name])
    print(u"== %s == T=%d covered=%d residue=%d | A_F6=%d B_F8only=%d C_F9only=%d D_both=%d"
          % (name, c[u"T"], c[u"covered"], c[u"residue"],
             c[u"A_F6any"], c[u"B_F8only"], c[u"C_F9only"], c[u"D_both"]))
    for lab, p8, p9, dA in CASES:
        v, pct = roll(c, p8, p9, dA)
        print(u"   %-24s %8.3f  %5.1f%%" % (lab, v, pct))
    print(u"")
