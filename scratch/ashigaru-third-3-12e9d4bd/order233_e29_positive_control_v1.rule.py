# -*- coding: utf-8 -*-
# order233 / E29 -- positive control: how far can it be grown without a run
# read-only. no product run. writes its own raw next to itself.
import io, os, re, glob, collections

D   = u"scratch/ashigaru-third-3-12e9d4bd"
HIT = u"\u6e2c\u5b9a\u4e0d\u80fd"          # the target word
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

def window(f, i, n):
    ls = docs[f]
    a = max(0, i - 1 - n); b = min(len(ls), i + n)
    return chr(10).join(ls[a:b])

hits = []
for f in sorted(docs):
    for i, ln in enumerate(docs[f], 1):
        if HIT in ln:
            hits.append((f, i, ln))

out = []
def w(s): out.append(s)

w(u"== corpus ==")
w(u"md files      = %d" % len(docs))
w(u"hit lines     = %d" % len(hits))
w(u"outside lot   = %d" % len([h for h in hits if h[0] not in LOT]))

# --- (1) where can answers be taken from: is the class already written by me? ---
for n in (0, 3, 5):
    cnt = collections.Counter()
    per = collections.Counter()
    for f, i, ln in hits:
        if f in LOT: continue
        wtxt = window(f, i, n)
        ks = [k for k in KIND if k in wtxt]
        if   len(ks) == 0: cnt[u"none"] += 1
        elif len(ks) == 1: cnt[u"one"] += 1; per[ks[0]] += 1
        else:              cnt[u"multi"] += 1
    w(u"")
    w(u"== self-labeled  window=%d ==" % n)
    w(u"  one(cheap)  = %d" % cnt[u"one"])
    w(u"  multi       = %d" % cnt[u"multi"])
    w(u"  none(costly)= %d" % cnt[u"none"])
    for k in KIND:
        w(u"  U+%04X : %d" % (ord(k), per[k]))

# --- (2) where do the cheap ones live (window=3) ---
w(u"")
w(u"== cheap ones by home  window=3 ==")
hm = collections.Counter(); pp = collections.Counter()
for f, i, ln in hits:
    if f in LOT: continue
    ks = [k for k in KIND if k in window(f, i, 3)]
    if len(ks) == 1:
        hm[home_of(ln)] += 1; pp[f] += 1
for k, v in hm.most_common():
    w(u"  %-10s %d" % (k, v))
w(u"  -- top papers --")
for k, v in pp.most_common(10):
    w(u"  %-52s %d" % (k, v))

# --- (3) does the B/D zero survive?  count cheap ones per class, by home ---
w(u"")
w(u"== per-class cheap ones, by home  window=3 ==")
tb = collections.defaultdict(collections.Counter)
for f, i, ln in hits:
    if f in LOT: continue
    ks = [k for k in KIND if k in window(f, i, 3)]
    if len(ks) == 1:
        tb[ks[0]][home_of(ln)] += 1
for k in KIND:
    w(u"  U+%04X  total=%d  %s" % (ord(k), sum(tb[k].values()),
        u" ".join(u"%s:%d" % (a, b) for a, b in tb[k].most_common())))

# --- (4) exclude rows that merely quote the definition (kinotai/hyou) ---
w(u"")
w(u"== cheap ones excluding hyou+kinotai+inyou  window=3 ==")
tb2 = collections.Counter()
for f, i, ln in hits:
    if f in LOT: continue
    if home_of(ln) in (u"hyou", u"kinotai", u"inyou"): continue
    ks = [k for k in KIND if k in window(f, i, 3)]
    if len(ks) == 1:
        tb2[ks[0]] += 1
w(u"  total = %d" % sum(tb2.values()))
for k in KIND:
    w(u"  U+%04X : %d" % (ord(k), tb2[k]))

# --- (5) the existing 12: are they self-labeled? ---
w(u"")
w(u"== the existing 12 (lot papers) ==")
lot_hits = [h for h in hits if h[0] in LOT]
w(u"  lot hit lines = %d" % len(lot_hits))
c2 = collections.Counter()
for f, i, ln in lot_hits:
    ks = [k for k in KIND if k in window(f, i, 3)]
    c2[len(ks)] += 1
for k in sorted(c2):
    w(u"  labels_in_window=%d : %d" % (k, c2[k]))

io.open(os.path.join(D, u"order233_e29_positive_control_v1.raw.txt"), "w",
        encoding="utf-8").write(chr(10).join(out) + chr(10))
print(chr(10).join(out))
