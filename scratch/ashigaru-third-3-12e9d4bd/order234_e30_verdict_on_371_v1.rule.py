# -*- coding: utf-8 -*-
# order234 / E30 -- should the 371-line hand pass be fired?  cost / gain / does the B,D zero survive
import io, os, re, glob, collections, time

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
        ks = [k for k in KIND if k in wtext(f, i, 3)]
        if len(ks) == 1:
            cand.append((f, i, ks[0], ln))

out = []
def w(s): out.append(s)

# ---------- (1) COST : merged, not naive ----------
w(u"== cost : lines actually to be read ==")
for n in (3, 5):
    span = collections.defaultdict(set)
    for f, i, k, ln in cand:
        for j in range(max(1, i - n), min(len(docs[f]), i + n) + 1):
            span[f].add(j)
    tot = sum(len(v) for v in span.values())
    ch  = 0
    for f, js in span.items():
        for j in js:
            ch += len(docs[f][j - 1])
    w(u"  window=%d  naive=%d  merged=%d  saved=%d  papers=%d  chars=%d"
      % (n, len(cand) * (2 * n + 1), tot, len(cand) * (2 * n + 1) - tot, len(span), ch))

# ---------- (2) GAIN : coverage / spread ----------
w(u"")
w(u"== gain : how far the control reaches ==")
mother = len([1 for f in docs if f not in LOT for ln in docs[f] if HIT in ln])
w(u"  mother rows (outside lot)   = %d" % mother)
w(u"  control now  12 -> %.2f%% of mother" % (100.0 * 12 / mother))
w(u"  control then 65 -> %.2f%% of mother" % (100.0 * 65 / mother))
w(u"  papers  now = 2   then = %d" % (len(set(f for f, i, k, ln in cand)) + 2))

w(u"  -- home spread --")
w(u"     now (12) : all from 2 lot papers")
hm = collections.Counter(home_of(ln) for f, i, k, ln in cand)
w(u"     then(53) : %s" % u" ".join(u"%s:%d" % (a, b) for a, b in hm.most_common()))

w(u"  -- order band spread of the 53 --")
bd = collections.Counter()
for f, i, k, ln in cand:
    m = re.match(r"^order([0-9]+)_", f)
    bd[(u"order%s0x" % m.group(1)[:-1]) if m else u"non-order"] += 1
for a, b in sorted(bd.items()):
    w(u"     %-12s %d" % (a, b))

# ---------- (3) does the B/D zero survive?  proxy, with its GATE measured first ----------
PB = [u"\u5e8a",                       # floor
      u"\u8b80\u53d6\u306e\u307f",  # read-only
      u"\u7981",                       # forbidden
      u"\u89e6\u308c\u306c",         # must not touch
      u"\u8ae1\u308b"]                # must ask the karo
PD = [u"\u66f8\u304d\u65b9",         # my notation
      u"\u8a18\u6cd5",                # notation
      u"\u5df1\u306e\u7b46",         # my own pen
      u"\u66d6\u6627",                # ambiguous
      u"\u66f8\u304d\u640d"]         # mis-written

w(u"")
w(u"== gate of the proxy vocabulary (measure BEFORE applying) ==")
for nm, vs in ((u"B-proxy", PB), (u"D-proxy", PD)):
    for v in vs:
        nl = 0; nf = 0
        for f in docs:
            c = len([1 for ln in docs[f] if v in ln])
            nl += c
            if c: nf += 1
        w(u"  %-8s %-14s lines=%-6d papers=%d" % (nm, v, nl, nf))

w(u"")
w(u"== proxy applied to the 53 (window=3) ==")
cb = 0; cd = 0; both = 0; none = 0
perk = collections.defaultdict(collections.Counter)
for f, i, k, ln in cand:
    t = wtext(f, i, 3)
    hb = any(v in t for v in PB); hd = any(v in t for v in PD)
    if hb and hd: both += 1
    elif hb: cb += 1
    elif hd: cd += 1
    else: none += 1
    perk[k][u"B" if hb else u"-"] += 0
    perk[k][(u"B" if hb else u"") + (u"D" if hd else u"") or u"none"] += 1
w(u"  B-proxy only = %d" % cb)
w(u"  D-proxy only = %d" % cd)
w(u"  both         = %d" % both)
w(u"  neither      = %d" % none)
for k in KIND:
    w(u"  marker U+%04X : %s" % (ord(k),
      u" ".join(u"%s:%d" % (a, b) for a, b in perk[k].most_common() if b)))

# positive control on the proxy: does it fire on the 12 known lot rows?
w(u"")
w(u"== proxy on the known 12 (positive control of the proxy itself) ==")
lot = []
for f in LOT:
    for i, ln in enumerate(docs[f], 1):
        if HIT in ln: lot.append((f, i, ln))
c2 = collections.Counter()
for f, i, ln in lot:
    t = wtext(f, i, 3)
    c2[(u"B" if any(v in t for v in PB) else u"") + (u"D" if any(v in t for v in PD) else u"") or u"none"] += 1
w(u"  lot rows = %d  ->  %s" % (len(lot), u" ".join(u"%s:%d" % (a, b) for a, b in c2.most_common())))

io.open(os.path.join(D, u"order234_e30_verdict_on_371_v1.raw.txt"), "w",
        encoding="utf-8").write(chr(10).join(out) + chr(10))
print(chr(10).join(out))
