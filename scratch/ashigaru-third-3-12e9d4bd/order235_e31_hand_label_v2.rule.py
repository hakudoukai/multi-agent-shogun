# -*- coding: utf-8 -*-
# order235 / E31 v2 -- per-stage merged read cost + emit the LOT 12 windows
import io, os, re, glob, collections
D   = u"scratch/ashigaru-third-3-12e9d4bd"
HIT = u"測定不能"
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
    ls = docs[f]; return chr(10).join(ls[max(0, i-1-n):min(len(ls), i+n)])
cand = []
for f in sorted(docs):
    if f in LOT: continue
    for i, ln in enumerate(docs[f], 1):
        if HIT not in ln: continue
        if home_of(ln) in (u"hyou", u"kinotai", u"inyou"): continue
        if len([k for k in KIND if k in window(f, i, N)]) == 1:
            cand.append((f, i, ln))
out = []
def w(s): out.append(s)
w(u"== per-stage merged read cost (window=%d) ==" % N)
STAGE = 12; run = collections.defaultdict(set); cum = 0
for s0 in range(0, len(cand), STAGE):
    grp = cand[s0:s0+STAGE]
    st = collections.defaultdict(set)
    for f, i, ln in grp:
        for j in range(max(1, i-N), min(len(docs[f]), i+N)+1):
            st[f].add(j); run[f].add(j)
    own = sum(len(v) for v in st.values()); cum = sum(len(v) for v in run.values())
    w(u"STAGE %d : cand %2d..%2d  stage_lines=%3d  cumulative=%3d  papers=%d"
      % (s0//STAGE+1, s0+1, s0+len(grp), own, cum, len(st)))
w(u"total merged = %d / papers = %d / cand = %d" % (cum, len(run), len(cand)))
w(u"")
w(u"== the LOT 12 (existing positive control) ==")
n = 0
for f in LOT:
    for i, ln in enumerate(docs[f], 1):
        if HIT not in ln: continue
        n += 1
        ks = [k for k in KIND if k in window(f, i, N)]
        w(u"---- L%02d  %s:%d  home=%s  signs_in_window=%s"
          % (n, f, i, home_of(ln), u",".join(u"U+%04X" % ord(k) for k in ks) or u"-"))
        a = max(1, i-N); b = min(len(docs[f]), i+N)
        for j in range(a, b+1):
            w(u"%s %5d| %s" % (u">>" if j == i else u"  ", j, docs[f][j-1]))
        w(u"")
io.open(os.path.join(D, u"order235_e31_hand_label_v2.raw.txt"), "w",
        encoding="utf-8").write(chr(10).join(out) + chr(10))
print(chr(10).join(out[:12]))
print("... lot lines emitted = %d" % n)
