# -*- coding: utf-8 -*-
# order233 / E29 v2 -- is the marker really the 3/4-way class, or a generic bullet?
import io, os, re, glob, collections

D   = u"scratch/ashigaru-third-3-12e9d4bd"
HIT = u"\u6e2c\u5b9a\u4e0d\u80fd"
A   = chr(0x32D0); B = chr(0x32D1); C = chr(0x32D2); Dk = chr(0x32D3)
KIND = [A, B, C, Dk]
LOT = [u"order226_e21_zero_by_instrument_v1.md", u"order227_e22_loop_in_caller_v1.md"]

# vocabulary that only the 3/4-way class uses (from the wording of the rule itself)
ANCHOR = [u"\u5668\u304c\u53ca\u3070\u306c",      # instrument cannot reach
          u"\u539f\u7406\u7684",                    # in principle
          u"\u5e8a\u306b\u4f9d\u308a",             # forbidden by the floor
          u"\u672a\u3060\u5668",                    # instrument not yet built
          u"\u4f5c\u308c\u3070",                    # if built, it reaches
          u"\u66f8\u304d\u65b9"]                    # my own notation was poor

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

def window(f, i, n):
    ls = docs[f]
    a = max(0, i - 1 - n); b = min(len(ls), i + n)
    return chr(10).join(ls[a:b])

out = []
def w(s): out.append(s)

# --- scale of the confound: how often do the markers appear at all? ---
tot_mark_lines = 0; near_hit = 0
for f in sorted(docs):
    for i, ln in enumerate(docs[f], 1):
        if any(k in ln for k in KIND):
            tot_mark_lines += 1
            lo = max(0, i - 1 - 3); hi = min(len(docs[f]), i + 3)
            if any(HIT in x for x in docs[f][lo:hi]): near_hit += 1
w(u"== marker lines in corpus ==")
w(u"  lines containing any marker      = %d" % tot_mark_lines)
w(u"  of which within 3 lines of HIT   = %d" % near_hit)
w(u"  of which NOT near HIT (generic)  = %d" % (tot_mark_lines - near_hit))

# --- the 53 candidates, one by one, with the anchor test ---
cand = []
for f in sorted(docs):
    if f in LOT: continue
    for i, ln in enumerate(docs[f], 1):
        if HIT not in ln: continue
        if home_of(ln) in (u"hyou", u"kinotai", u"inyou"): continue
        wt = window(f, i, 3)
        ks = [k for k in KIND if k in wt]
        if len(ks) != 1: continue
        anc = [a for a in ANCHOR if a in wt]
        cand.append((f, i, ks[0], len(anc), home_of(ln)))

w(u"")
w(u"== candidates (window=3, home filtered) ==")
w(u"  total = %d" % len(cand))
ca = collections.Counter(); cn = collections.Counter()
for f, i, k, na, hm in cand:
    (ca if na else cn)[k] += 1
for k in KIND:
    w(u"  U+%04X : anchored=%d  bare=%d" % (ord(k), ca[k], cn[k]))
w(u"  anchored total = %d / bare total = %d" % (sum(ca.values()), sum(cn.values())))

w(u"")
w(u"== candidate list ==")
for f, i, k, na, hm in cand:
    w(u"  %-56s :%-5d U+%04X anc=%d %s" % (f, i, ord(k), na, hm))

io.open(os.path.join(D, u"order233_e29_positive_control_v2.raw.txt"), "w",
        encoding="utf-8").write(chr(10).join(out) + chr(10))
print(chr(10).join(out))
