# -*- coding: utf-8 -*-
# order265 -- (A) reproduce the 197-net (o261c extraction net) on today's corpus,
#             (B) classify the 191 CAUGHT numbers by the order264 rule, unbent.
# read-only. no file is written by this instrument.
#
# ORDER264 RULE (copied verbatim in meaning; NOT bent here):
#   per LINE:
#     DECL  = line starts with '#' AND carries JOU/JO AND the next non-empty line is NOT a heading
#     UNDEC = line starts with '#' but lacks JOU/JO, OR its next non-empty line IS a heading
#     MENT  = line does not start with '#'
#   per NUMBER: any DECL -> DECL ; else any MENT -> MENT ; else UNDEC
# BOUNDARY: jou 443 -- prev char and next char must both be OUTSIDE DIGSET.
import io, os, re, glob
DIR = "scratch/ashigaru-third-3-12e9d4bd"
DIG = [chr(c) for c in (0x4E00,0x4E8C,0x4E09,0x56DB,0x4E94,0x516D,0x4E03,0x516B,0x4E5D)]
TEN = chr(0x5341); HUN = chr(0x767E)
JOU = chr(0x689D); JO = chr(0x6761); STAR = chr(0x2605)
DIGSET = u"".join(DIG) + TEN + HUN
BOUND = set(DIGSET)
NA = u"(?![" + DIGSET + u"])"
def kan(n):
    h = n // 100; t = (n // 10) % 10; o = n % 10; s = u""
    if h: s += (u"" if h == 1 else DIG[h-1]) + HUN
    if t: s += (u"" if t == 1 else DIG[t-1]) + TEN
    if o: s += DIG[o-1]
    return s
DGT = {}
for i, c in enumerate(DIG): DGT[c] = i + 1
def kan2int(t):
    n = 0
    if HUN in t:
        a, t = t.split(HUN, 1); n += (DGT.get(a, 1) if a else 1) * 100
    if TEN in t:
        a, t = t.split(TEN, 1); n += (DGT.get(a, 1) if a else 1) * 10
    if t: n += DGT.get(t[-1], 0)
    return n
FILES = sorted(glob.glob(os.path.join(DIR, "order*.md")))
CORP = []
for f in FILES:
    CORP.append((os.path.basename(f),
                 io.open(f, encoding="utf-8", errors="replace").read().split(chr(10))))
print("== corpus ==")
print("order*.md = %d ; lines = %d" % (len(CORP), sum(len(x[1]) for x in CORP)))

# ---- (A) reproduce the 197-net: o261c extraction forms, greedy KAN+, 100..999 ----
KAN = u"[" + DIGSET + u"]+"
EX = [re.compile(u"^#+ .*A3 [" + JOU + JO + u"] (" + KAN + u")"),
      re.compile(u"^- " + re.escape(u"**") + u"(" + KAN + u")" + re.escape(u"**")),
      re.compile(u"^- " + STAR + u"(" + KAN + u")" + STAR)]
known = set()
for _, lines in CORP:
    for L in lines:
        for rx in EX:
            m = rx.match(L)
            if m:
                v = kan2int(m.group(1))
                if 100 <= v <= 999: known.add(v)
print("== (A) 197-net reproduced on today's corpus ==")
print("known jou from order*.md = %d" % len(known))
insp = sorted(v for v in known if 169 <= v <= 420)
print("of which inside span 169..420 = %d" % len(insp))
print("outside span = %s" % sorted(v for v in known if not (169 <= v <= 420)))

# ---- boundary-checked occurrence scan (jou 443) ----
def okb(ln, j, L):
    if j > 0 and ln[j-1] in BOUND: return False
    if j + L < len(ln) and ln[j+L] in BOUND: return False
    return True
def hits(K):
    out = []
    L = len(K)
    for name, lines in CORP:
        for i, ln in enumerate(lines):
            j = ln.find(K)
            while j >= 0:
                if okb(ln, j, L):
                    out.append((name, i, ln)); break
                j = ln.find(K, j + 1)
    return out
pa = re.compile(u"^#+ .*A3 [" + JOU + JO + u"] " )
def caught_forms(K, occ):
    fs = set()
    for name, i, ln in occ:
        if re.match(u"^#+ .*A3 [" + JOU + JO + u"] " + re.escape(K) + NA, ln): fs.add("kou")
        if re.match(u"^- " + re.escape(u"**" + K) + NA, ln): fs.add("otsu")
        if re.match(u"^- " + STAR + re.escape(K) + NA, ln): fs.add("hei")
    return fs
def nxt_head(lines, i):
    j = i + 1
    while j < len(lines) and lines[j].strip() == u"": j += 1
    return j < len(lines) and lines[j].startswith(u"#")
BYNAME = dict(CORP)
def line_class(name, i, ln):
    if ln.startswith(u"#"):
        if (JOU not in ln) and (JO not in ln): return "UNDEC"
        if nxt_head(BYNAME[name], i): return "UNDEC"
        return "DECL"
    return "MENT"

# ---- (B) the 191 caught: classify by order264 rule ----
CAUGHT = []; UNC = []
CLS = {"DECL": [], "MENT": [], "UNDEC": []}
FORMCLS = {}
for n in range(169, 421):
    K = kan(n)
    occ = hits(K)
    fs = caught_forms(K, occ)
    if fs:
        CAUGHT.append(n)
        cs = set(line_class(a, b, c) for a, b, c in occ)
        k = "DECL" if "DECL" in cs else ("MENT" if "MENT" in cs else "UNDEC")
        CLS[k].append(n)
        key = (",".join(sorted(fs)), k)
        FORMCLS[key] = FORMCLS.get(key, 0) + 1
    else:
        UNC.append(n)
print("== (B) span 169..420 ==")
print("CAUGHT = %d ; UNCAUGHT = %d ; total = %d" % (len(CAUGHT), len(UNC), len(CAUGHT)+len(UNC)))
assert len(CAUGHT) + len(UNC) == 252, "SUM252"
print("-- caught, classified by the order264 rule (unbent) --")
for k in ("DECL", "MENT", "UNDEC"):
    print("  %-5s = %d" % (k, len(CLS[k])))
assert sum(len(CLS[k]) for k in CLS) == len(CAUGHT), "SUMCAUGHT"
print("  MENT nums  = %s" % CLS["MENT"])
print("  UNDEC nums = %s" % CLS["UNDEC"])
print("-- cross: which form caught it x how the rule judged it --")
for key in sorted(FORMCLS):
    print("  form=%-14s rule=%-5s n=%d" % (key[0], key[1], FORMCLS[key]))

# ---- controls ----
print("== NEGCTRL (must NOT match) ==")
ng = 0
for a, b in ((190,197),(200,201),(220,225),(240,244)):
    KA = kan(a); KB = kan(b); j = KB.find(KA)
    m = (j >= 0 and okb(KB, j, len(KA)))
    print("  K(%d)=%s inside K(%d)=%s -> matched=%s (want False)" % (a, KA, b, KB, m))
    if not m: ng += 1
print("  NEGCTRL %s" % ("tootta" if ng == 4 else "TOORANU"))
print("== POSCTRL (F2 heading-no / F6 kajou-bun / F7 ji-no-bun) ==")
pg = 0
for tag, n in (("F2",181),("F6",200),("F7",184)):
    h = hits(kan(n))
    print("  %s n=%d hits=%d" % (tag, n, len(h)))
    if len(h) >= 1: pg += 1
print("  POSCTRL %s" % ("tootta" if pg == 3 else "TOORANU"))
