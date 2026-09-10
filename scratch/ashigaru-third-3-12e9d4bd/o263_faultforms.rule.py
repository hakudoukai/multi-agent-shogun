# -*- coding: utf-8 -*-
# o263 second pass: census the FORMS of the net fault, one line per form.
import io, glob, re

D = "scratch/ashigaru-third-3-12e9d4bd/"
files = sorted(glob.glob(D + "order*.md"))
DIG = [chr(c) for c in (0x4E00, 0x4E8C, 0x4E09, 0x56DB, 0x4E94, 0x516D, 0x4E03, 0x516B, 0x4E5D)]
TEN = chr(0x5341); HUN = chr(0x767E)
JOU = chr(0x689D); JO = chr(0x6761); STAR = chr(0x2605); NO = chr(0x306E)
REI = chr(0x4EE4); DAI = chr(0x7B2C); SETSU = chr(0xFF53)
BOUND = set(DIG) | set([TEN, HUN])

def kan(n):
    h = n // 100; t = (n // 10) % 10; o = n % 10
    s = u""
    if h: s += (u"" if h == 1 else DIG[h - 1]) + HUN
    if t: s += (u"" if t == 1 else DIG[t - 1]) + TEN
    if o: s += DIG[o - 1]
    return s

docs = [(f, io.open(f, encoding="utf-8").read().split(chr(10))) for f in files]

def mentions(K):
    out = []; L = len(K)
    for f, lines in docs:
        for i, ln in enumerate(lines):
            st = 0
            while True:
                j = ln.find(K, st)
                if j < 0: break
                st = j + 1
                if j > 0 and ln[j - 1] in BOUND: continue
                if j + L < len(ln) and ln[j + L] == TEN: continue
                out.append((f, i + 1, ln, j)); break
    return out

# forms, tested in order; first match wins
def form_of(K, f, i, ln, j):
    pre = ln[:j]
    if ln.startswith(u"#") and (JOU in pre or JO in pre):
        return u"F1 midashi" if (u"A3 " + JOU) in pre or (u"A3 " + JO) in pre else u"F2 midashi-no"
    if ln.startswith(u"#"):
        return u"F3 midashi-nojou"
    if pre.endswith(DAI) or (ln[j+len(K):j+len(K)+1] == REI):
        return u"F4 rei-series"
    if ln.startswith(u"|"):
        return u"F5 table-cell"
    if ln.startswith(u"- ") or ln.startswith(u"  - "):
        return u"F6 kajou"
    return u"F7 jibun"

UNC = list(range(181, 207)) + list(range(219, 249)) + [263] + list(range(272, 276))
assert len(UNC) == 61, "UNC"

NF = [181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,
      201,202,203,204,205,206,219,220,224,225,226,227,228,229,230,232,234,235,236,237,
      238,239,240,244,245,246,263,275]
UD = [221,222,223,231,233,241,242,243,247,248,272,273,274]
assert len(NF) == 48 and len(UD) == 13, "SPLIT"

cens = {}; rep = {}
for n in NF:
    K = kan(n)
    best = None
    for f, i, ln, j in mentions(K):
        if JOU in ln or JO in ln:
            best = (f, i, ln, j); break
    if best is None: continue
    f, i, ln, j = best
    fm = form_of(K, f, i, ln, j)
    cens[fm] = cens.get(fm, 0) + 1
    if fm not in rep:
        rep[fm] = (n, f.split("/")[-1], i, ln[:160])

print("=== NETFAULT FORM CENSUS (n=48) ===")
tot = 0
for fm in sorted(cens):
    print("%s = %d" % (fm, cens[fm])); tot += cens[fm]
print("form_total=%d" % tot)
print("=== ONE LINE PER FORM ===")
for fm in sorted(rep):
    n, f, i, ln = rep[fm]
    print("%s | n=%d %s:%d | %s" % (fm, n, f, i, ln))

# undecidable: show what the mention actually is
print("=== UNDECIDABLE sample (no jou/jo on the line) ===")
seen = 0
for n in UD:
    K = kan(n); m = mentions(K)
    if m and seen < 4:
        f, i, ln, j = m[0]
        print("n=%d cnt=%d %s:%d | %s" % (n, len(m), f.split("/")[-1], i, ln[:150])); seen += 1
print("UD_with_zero_mention=%d" % sum(1 for n in UD if not mentions(kan(n))))
