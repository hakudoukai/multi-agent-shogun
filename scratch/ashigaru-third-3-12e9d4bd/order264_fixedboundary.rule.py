# -*- coding: utf-8 -*-
# o264 (b): SAME nets, BOUNDARY REPAIRED, applied to all 61.
# Repair: the previous boundary excluded only a trailing TEN. It did NOT exclude a
# trailing digit 1..9 or HUN, so 190 matched inside 197, 200 inside 201, 220 inside 225.
# New boundary: char before and char after K must both be outside {1..9, TEN, HUN}.
import io, glob, re

D = "scratch/ashigaru-third-3-12e9d4bd/"
files = sorted(glob.glob(D + "order*.md"))
DIG = [chr(c) for c in (0x4E00, 0x4E8C, 0x4E09, 0x56DB, 0x4E94, 0x516D, 0x4E03, 0x516B, 0x4E5D)]
TEN = chr(0x5341); HUN = chr(0x767E)
JOU = chr(0x689D); JO = chr(0x6761); STAR = chr(0x2605)
DIGSET = u"".join(DIG) + TEN + HUN
BOUND = set(DIGSET)

def kan(n):
    h = n // 100; t = (n // 10) % 10; o = n % 10
    s = u""
    if h: s += (u"" if h == 1 else DIG[h - 1]) + HUN
    if t: s += (u"" if t == 1 else DIG[t - 1]) + TEN
    if o: s += DIG[o - 1]
    return s

docs = [(f, io.open(f, encoding="utf-8").read().split(chr(10))) for f in files]
NA = u"(?![" + DIGSET + u"])"

def okb(ln, j, L):
    if j > 0 and ln[j - 1] in BOUND: return False
    if j + L < len(ln) and ln[j + L] in BOUND: return False
    return True

def mentions(K):
    out = []; L = len(K)
    for f, lines in docs:
        for i, ln in enumerate(lines):
            st = 0
            while True:
                j = ln.find(K, st)
                if j < 0: break
                st = j + 1
                if not okb(ln, j, L): continue
                out.append((f, i, ln, lines)); break
    return out

def caught(K):
    pa = re.compile(u"^#+ .*A3 [" + JOU + JO + u"] " + re.escape(K) + NA)
    pb = re.compile(u"^- " + re.escape(u"**" + K) + NA)
    pc = re.compile(u"^- " + STAR + re.escape(K) + NA)
    out = []
    for f, lines in docs:
        for i, ln in enumerate(lines):
            if pa.match(ln) or pb.match(ln) or pc.match(ln):
                out.append((f, i + 1, ln))
    return out

def nxt_head(lines, i):
    j = i + 1
    while j < len(lines) and lines[j].strip() == u"": j += 1
    return j < len(lines) and lines[j].startswith(u"#")

def line_class(i, ln, lines):
    if ln.startswith(u"#"):
        if (JOU not in ln) and (JO not in ln): return "UNDEC"
        if nxt_head(lines, i): return "UNDEC"
        return "DECL"
    return "MENT"

# ---- controls ----
print("=== NEGCTRL (boundary) ===")
bad = [(190, 197), (200, 201), (220, 225), (240, 244)]
allok = True
for a, b in bad:
    Ka, Kb = kan(a), kan(b)
    j = Kb.find(Ka)
    hit = (j == 0 and okb(Kb, 0, len(Ka)))
    if hit: allok = False
    print("K(%d)=%s inside K(%d)=%s -> matched=%s (want False)" % (a, Ka, b, Kb, hit))
print("NEGCTRL " + ("tootta" if allok else "TOORANU"))

print("=== POSCTRL (F2 / F6 / F7, one each) ===")
pc_ok = True
for n, tag in ((181, "F2"), (200, "F6"), (184, "F7")):
    m = mentions(kan(n))
    if not m: pc_ok = False
    f, i, ln, lines = m[0]
    print("%s n=%d hits=%d %s:%d | %s" % (tag, n, len(m), f.split("/")[-1], i + 1, ln[:90]))
print("POSCTRL " + ("tootta" if pc_ok else "TOORANU"))

UNC = list(range(181, 207)) + list(range(219, 249)) + [263] + list(range(272, 276))
assert len(UNC) == 61, "UNC"

b = {"CAUGHT": [], "JUMP": [], "NETFAULT": [], "UNDECIDABLE": []}
for n in UNC:
    K = kan(n); c = caught(K); m = mentions(K)
    if c: k = "CAUGHT"
    elif not m: k = "JUMP"
    else:
        k = "NETFAULT" if any((JOU in ln or JO in ln) for _, _, ln, _ in m) else "UNDECIDABLE"
    b[k].append(n)
print("=== THREE KINDS (boundary repaired) ===")
for k in ("CAUGHT", "JUMP", "NETFAULT", "UNDECIDABLE"):
    print("%s = %d nums=%s" % (k, len(b[k]), b[k]))
assert sum(len(v) for v in b.values()) == 61, "SUM61"

print("=== (a) DECL / MENT / UNDEC over NETFAULT, one line per item ===")
cnt = {"DECL": 0, "MENT": 0, "UNDEC": 0}
for n in b["NETFAULT"]:
    ms = mentions(kan(n))
    cs = [(line_class(i, ln, lines), f, i + 1, ln) for f, i, ln, lines in ms]
    v = None
    for want in ("DECL", "MENT", "UNDEC"):
        for cc, f, i, ln in cs:
            if cc == want: v = (want, f, i, ln); break
        if v: break
    if not v: v = ("UNDEC", "", 0, u"")
    cnt[v[0]] += 1
    print("n=%d %s hits=%d %s:%d | %s" % (n, v[0], len(cs), v[1].split("/")[-1], v[2], v[3][:80]))
print("DECL=%d MENT=%d UNDEC=%d total=%d" % (cnt["DECL"], cnt["MENT"], cnt["UNDEC"], sum(cnt.values())))

print("=== (b) UNDECIDABLE forms, one line per item ===")
for n in b["UNDECIDABLE"]:
    ms = mentions(kan(n))
    if not ms:
        print("n=%d NO-MENTION" % n); continue
    f, i, ln, lines = ms[0]
    head = ln.lstrip()[:6]
    fm = "G1 kuro-hoshi-2" if ln.startswith(u"- " + STAR + STAR) else (
         "G2 hoshi2-kuro" if ln.startswith(u"- **" + STAR) else (
         "G3 midashi" if ln.startswith(u"#") else "G4 hoka"))
    print("n=%d %s hits=%d %s:%d | %s" % (n, fm, len(ms), f.split("/")[-1], i + 1, ln[:80]))
