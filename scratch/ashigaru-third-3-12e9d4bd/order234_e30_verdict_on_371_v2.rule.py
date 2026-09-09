# -*- coding: utf-8 -*-
# order234 / E30 v2 -- redo of the proxy with the mis-encoded term corrected (U+8AE1 -> U+8AEE)
import io, os, re, glob, collections

D   = u"scratch/ashigaru-third-3-12e9d4bd"
HIT = u"\u6e2c\u5b9a\u4e0d\u80fd"
A   = chr(0x32D0); B = chr(0x32D1); C = chr(0x32D2); Dk = chr(0x32D3)
KIND = [A, B, C, Dk]
LOT = [u"order226_e21_zero_by_instrument_v1.md", u"order227_e22_loop_in_caller_v1.md"]

docs = {}
for f in sorted(glob.glob(os.path.join(D, u"*.md"))):
    docs[os.path.basename(f)] = io.open(f, encoding="utf-8").read().split(chr(10))

def home_of(line):
    t = line.strip()
    if t.startswith(u"#"):  return u"midashi"
    if t.startswith(u">"):  return u"inyou"
    if t.startswith(u"|"):  return u"hyou"
    if t.startswith(u"-") or t.startswith(u"*") or re.match(r"^[0-9]+[.)]", t): return u"kajou"
    if t.startswith(chr(96)) or line.startswith(u"    "): return u"kinotai"
    return u"jinobun"

def wtext(f, i, n):
    ls = docs[f]
    return chr(10).join(ls[max(0, i - 1 - n):min(len(ls), i + n)])

cand = []
for f in sorted(docs):
    if f in LOT: continue
    for i, ln in enumerate(docs[f], 1):
        if HIT not in ln: continue
        if home_of(ln) in (u"hyou", u"kinotai", u"inyou"): continue
        if len([k for k in KIND if k in wtext(f, i, 3)]) == 1:
            cand.append((f, i, [k for k in KIND if k in wtext(f, i, 3)][0]))

out = []
def w(s): out.append(s)
w(u"== corpus now ==")
w(u"  papers = %d" % len(docs))
w(u"  hit lines = %d  (outside lot = %d)"
  % (sum(len([1 for ln in docs[f] if HIT in ln]) for f in docs),
     sum(len([1 for ln in docs[f] if HIT in ln]) for f in docs if f not in LOT)))
w(u"  candidates = %d" % len(cand))

PB = [u"\u5e8a", u"\u8b80\u53d6\u306e\u307f", u"\u7981",
      u"\u89e6\u308c\u306c", u"\u8aee\u308b"]   # <- corrected U+8AEE
PD = [u"\u66f8\u304d\u65b9", u"\u8a18\u6cd5", u"\u5df1\u306e\u7b46",
      u"\u66d6\u6627", u"\u66f8\u304d\u640d"]

w(u"")
w(u"== gate, each term ==")
for nm, vs in ((u"B", PB), (u"D", PD)):
    for v in vs:
        nl = sum(len([1 for ln in docs[f] if v in ln]) for f in docs)
        nf = len([1 for f in docs if any(v in ln for ln in docs[f])])
        w(u"  %s %-8s lines=%-6d papers=%-4d  (U+%s)"
          % (nm, v, nl, nf, u"+".join(u"%04X" % ord(c) for c in v)))

w(u"")
w(u"== proxy on the 53 (window=3), corrected ==")
c = collections.Counter(); perk = collections.defaultdict(collections.Counter)
for f, i, k in cand:
    t = wtext(f, i, 3)
    lab = (u"B" if any(v in t for v in PB) else u"") + (u"D" if any(v in t for v in PD) else u"")
    lab = lab or u"none"
    c[lab] += 1; perk[k][lab] += 1
for a, b in c.most_common():
    w(u"  %-6s %d" % (a, b))
for k in KIND:
    w(u"  marker U+%04X : %s" % (ord(k), u" ".join(u"%s:%d" % (x, y) for x, y in perk[k].most_common())))

w(u"")
w(u"== term-by-term hits inside the 53 windows ==")
for nm, vs in ((u"B", PB), (u"D", PD)):
    for v in vs:
        n = len([1 for f, i, k in cand if v in wtext(f, i, 3)])
        w(u"  %s %-8s %d" % (nm, v, n))

io.open(os.path.join(D, u"order234_e30_verdict_on_371_v2.raw.txt"), "w",
        encoding="utf-8").write(chr(10).join(out) + chr(10))
print(chr(10).join(out))
