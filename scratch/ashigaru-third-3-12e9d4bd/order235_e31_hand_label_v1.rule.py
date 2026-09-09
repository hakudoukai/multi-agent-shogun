# -*- coding: utf-8 -*-
# order235 / E31 -- emit the 53 candidate windows for HAND labelling.
# read-only. no product run. writes its own raw next to itself.
import io, os, re, glob, collections

D   = u"scratch/ashigaru-third-3-12e9d4bd"
HIT = u"測定不能"          # the target word
A   = chr(0x32D0); B = chr(0x32D1); C = chr(0x32D2); Dk = chr(0x32D3)
KIND = [A, B, C, Dk]
LOT = [u"order226_e21_zero_by_instrument_v1.md", u"order227_e22_loop_in_caller_v1.md"]
N   = 3

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

cand = []
for f in sorted(docs):
    if f in LOT: continue
    for i, ln in enumerate(docs[f], 1):
        if HIT not in ln: continue
        if home_of(ln) in (u"hyou", u"kinotai", u"inyou"): continue
        ks = [k for k in KIND if k in window(f, i, N)]
        if len(ks) == 1:
            cand.append((f, i, ks[0], ln))

# merged reading span (window 3), per paper
span = collections.defaultdict(set)
for f, i, k, ln in cand:
    for j in range(max(1, i - N), min(len(docs[f]), i + N) + 1):
        span[f].add(j)
tot = sum(len(v) for v in span.values())

out = []
def w(s): out.append(s)
w(u"== order235 / E31  hand-label material ==")
w(u"candidates = %d / papers = %d / merged read lines = %d" % (len(cand), len(span), tot))
w(u"")
# stages of 12
STAGE = 12
for s0 in range(0, len(cand), STAGE):
    grp = cand[s0:s0 + STAGE]
    w(u"########## STAGE %d  (cand %d..%d) ##########" % (s0 // STAGE + 1, s0 + 1, s0 + len(grp)))
    for idx, (f, i, k, ln) in enumerate(grp, s0 + 1):
        w(u"---- #%02d  %s:%d  sign=U+%04X  home=%s" % (idx, f, i, ord(k), home_of(ln)))
        a = max(1, i - N); b = min(len(docs[f]), i + N)
        for j in range(a, b + 1):
            mark = u">>" if j == i else u"  "
            w(u"%s %5d| %s" % (mark, j, docs[f][j - 1]))
        w(u"")
io.open(os.path.join(D, u"order235_e31_hand_label_v1.raw.txt"), "w",
        encoding="utf-8").write(chr(10).join(out) + chr(10))
print(u"cand=%d papers=%d merged=%d out_lines=%d" % (len(cand), len(span), tot, len(out)))
