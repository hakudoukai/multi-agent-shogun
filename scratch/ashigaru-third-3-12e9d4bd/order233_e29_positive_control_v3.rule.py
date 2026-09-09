# -*- coding: utf-8 -*-
# order233 / E29 v3 -- powered test: the 4-way class did not exist before order228.
# a marker in a paper older than the coinage cannot be the class.
import io, os, re, glob, collections, time

D   = u"scratch/ashigaru-third-3-12e9d4bd"
HIT = u"\u6e2c\u5b9a\u4e0d\u80fd"
A   = chr(0x32D0); B = chr(0x32D1); C = chr(0x32D2); Dk = chr(0x32D3)
KIND = [A, B, C, Dk]
LOT = [u"order226_e21_zero_by_instrument_v1.md", u"order227_e22_loop_in_caller_v1.md"]
COIN = u"order228_e24_caller_outside_dir_v1.md"   # where the 4-way class was coined

docs = {}; mt = {}
for f in sorted(glob.glob(os.path.join(D, u"*.md"))):
    b = os.path.basename(f)
    docs[b] = io.open(f, encoding="utf-8").read().split(chr(10))
    mt[b] = os.path.getmtime(f)

cut = mt[COIN]

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

w(u"== coinage cut ==")
w(u"  paper = %s" % COIN)
w(u"  mtime = %s" % time.strftime(u"%Y-%m-%dT%H:%M:%S", time.localtime(cut)))
w(u"  papers older than cut = %d / newer or equal = %d"
  % (len([1 for b in mt if mt[b] < cut]), len([1 for b in mt if mt[b] >= cut])))

# the 53 candidates split by the cut
cand = []
for f in sorted(docs):
    if f in LOT: continue
    for i, ln in enumerate(docs[f], 1):
        if HIT not in ln: continue
        if home_of(ln) in (u"hyou", u"kinotai", u"inyou"): continue
        ks = [k for k in KIND if k in window(f, i, 3)]
        if len(ks) != 1: continue
        cand.append((f, i, ks[0], mt[f] >= cut))

w(u"")
w(u"== the 53 candidates split by the cut ==")
old = collections.Counter(); new = collections.Counter()
for f, i, k, isnew in cand:
    (new if isnew else old)[k] += 1
w(u"  before coinage (cannot be the class) = %d" % sum(old.values()))
for k in KIND:
    w(u"    U+%04X : %d" % (ord(k), old[k]))
w(u"  at/after coinage (may be the class)  = %d" % sum(new.values()))
for k in KIND:
    w(u"    U+%04X : %d" % (ord(k), new[k]))
w(u"  -- the at/after ones, one by one --")
for f, i, k, isnew in cand:
    if isnew:
        w(u"    %-56s :%-5d U+%04X" % (f, i, ord(k)))

# whole-corpus: HIT lines in papers written at/after the coinage
w(u"")
w(u"== HIT lines by era ==")
eo = 0; en = 0
for f in sorted(docs):
    if f in LOT: continue
    c = len([1 for ln in docs[f] if HIT in ln])
    if mt[f] >= cut: en += c
    else: eo += c
w(u"  before coinage = %d" % eo)
w(u"  at/after       = %d" % en)

# how much re-reading would 53 cost: how many papers, how many lines to read at window 3
w(u"")
w(u"== cost of hand-labelling the 53 ==")
pf = collections.Counter()
for f, i, k, isnew in cand: pf[f] += 1
w(u"  distinct papers = %d" % len(pf))
w(u"  lines to read at window 3 (7 lines each, no overlap merge) = %d" % (len(cand) * 7))
w(u"  max per paper = %d" % (max(pf.values()) if pf else 0))

io.open(os.path.join(D, u"order233_e29_positive_control_v3.raw.txt"), "w",
        encoding="utf-8").write(chr(10).join(out) + chr(10))
print(chr(10).join(out))
