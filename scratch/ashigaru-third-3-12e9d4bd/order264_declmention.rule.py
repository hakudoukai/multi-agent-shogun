# -*- coding: utf-8 -*-
# o264 (a): split the 48 net-fault numbers into DECL / MENT / UNDEC.
# RULE (fixed BEFORE application; not to be bent afterwards):
#   per LINE:
#     DECL  = line starts with '#' AND carries JOU/JO AND the next non-empty line is NOT a heading
#     UNDEC = line starts with '#' but lacks JOU/JO, OR its next non-empty line IS a heading
#     MENT  = line does not start with '#'
#   per NUMBER (aggregation): any DECL -> DECL ; else any MENT -> MENT ; else UNDEC
import io, glob

D = "scratch/ashigaru-third-3-12e9d4bd/"
files = sorted(glob.glob(D + "order*.md"))
DIG = [chr(c) for c in (0x4E00, 0x4E8C, 0x4E09, 0x56DB, 0x4E94, 0x516D, 0x4E03, 0x516B, 0x4E5D)]
TEN = chr(0x5341); HUN = chr(0x767E)
JOU = chr(0x689D); JO = chr(0x6761)
BOUND = set(DIG) | set([TEN, HUN])

def kan(n):
    h = n // 100; t = (n // 10) % 10; o = n % 10
    s = u""
    if h: s += (u"" if h == 1 else DIG[h - 1]) + HUN
    if t: s += (u"" if t == 1 else DIG[t - 1]) + TEN
    if o: s += DIG[o - 1]
    return s

docs = [(f, io.open(f, encoding="utf-8").read().split(chr(10))) for f in files]

def next_nonempty_is_heading(lines, i):
    j = i + 1
    while j < len(lines) and lines[j].strip() == u"":
        j += 1
    if j >= len(lines): return False
    return lines[j].startswith(u"#")

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
                out.append((f, i, ln, lines)); break
    return out

def line_class(f, i, ln, lines):
    if ln.startswith(u"#"):
        if (JOU not in ln) and (JO not in ln): return "UNDEC"
        if next_nonempty_is_heading(lines, i): return "UNDEC"
        return "DECL"
    return "MENT"

def verdict(K):
    ms = mentions(K)
    cs = [(line_class(f, i, ln, lines), f, i, ln) for f, i, ln, lines in ms]
    for want in ("DECL", "MENT", "UNDEC"):
        for c, f, i, ln in cs:
            if c == want:
                return want, len(cs), f, i + 1, ln
    return "UNDEC", 0, "", 0, u""

print("=== RULE (written before application) ===")
print("DECL: heading line carrying JOU/JO whose next non-empty line is not a heading")
print("MENT: non-heading line (prose / list body / table cell)")
print("UNDEC: heading without JOU/JO, or heading followed by another heading")
print("aggregate per number: any DECL -> DECL ; else any MENT -> MENT ; else UNDEC")

# POSITIVE CONTROL: one each of the forms the previous net DROPPED (rule 442)
print("=== POSCTRL (F2 / F6 / F7, one each) ===")
CTRL = [(181, "F2 midashi-no"), (200, "F6 kajou"), (184, "F7 jibun")]
ok = True
for n, tag in CTRL:
    v, cnt, f, i, ln = verdict(kan(n))
    good = cnt >= 1
    if not good: ok = False
    print("%s n=%d hits=%d verdict=%s %s:%d | %s" % (tag, n, cnt, v, f.split("/")[-1], i, ln[:100]))
print("POSCTRL " + ("tootta" if ok else "TOORANU"))

NF = [181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,
      201,202,203,204,205,206,219,220,224,225,226,227,228,229,230,232,234,235,236,237,
      238,239,240,244,245,246,263,275]
assert len(NF) == 48, "NF=%d" % len(NF)

cnt = {"DECL": 0, "MENT": 0, "UNDEC": 0}
print("=== ONE LINE PER ITEM (n=48) ===")
for n in NF:
    v, k, f, i, ln = verdict(kan(n))
    cnt[v] += 1
    print("n=%d %s hits=%d %s:%d | %s" % (n, v, k, f.split("/")[-1], i, ln[:90]))
print("=== COUNTS ===")
print("DECL=%d MENT=%d UNDEC=%d total=%d" % (cnt["DECL"], cnt["MENT"], cnt["UNDEC"],
                                             cnt["DECL"] + cnt["MENT"] + cnt["UNDEC"]))
assert cnt["DECL"] + cnt["MENT"] + cnt["UNDEC"] == 48, "SUM"
