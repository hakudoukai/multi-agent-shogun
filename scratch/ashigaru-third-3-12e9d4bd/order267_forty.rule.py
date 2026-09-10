# -*- coding: utf-8 -*-
# order267 (ka) : split the remaining 40 by FORM, and date the 21 of 181..201.
# nets are the order264/order266 nets, unchanged. reads order*.md only. writes nothing.
import io, glob, re, os, time

D = "scratch/ashigaru-third-3-12e9d4bd/"
FILES = sorted(glob.glob(D + "order*.md"))
DIG = [chr(c) for c in (0x4E00,0x4E8C,0x4E09,0x56DB,0x4E94,0x516D,0x4E03,0x516B,0x4E5D)]
TEN = chr(0x5341); HUN = chr(0x767E); SEN = chr(0x5343)
JOU = chr(0x689D); JO = chr(0x6761); STAR = chr(0x2605); NO = chr(0x306E)
DIGSET = u"".join(DIG) + TEN + HUN
BOUND = set(DIGSET)
NA = u"(?![" + DIGSET + u"])"
KANC = u"[" + DIGSET + u"]+"

def kan(n):
    h = n//100; t = (n//10)%10; o = n%10; s = u""
    if h: s += (u"" if h == 1 else DIG[h-1]) + HUN
    if t: s += (u"" if t == 1 else DIG[t-1]) + TEN
    if o: s += DIG[o-1]
    return s

DOCS = [(f, io.open(f, encoding="utf-8").read().split(chr(10))) for f in FILES]

def okb(ln, j, L):
    if j > 0 and ln[j-1] in BOUND: return False
    if j + L < len(ln) and ln[j+L] in BOUND: return False
    return True

def mentions(K):
    out = []; L = len(K)
    for f, lines in DOCS:
        for i, ln in enumerate(lines):
            st = 0
            while True:
                j = ln.find(K, st)
                if j < 0: break
                st = j + 1
                if not okb(ln, j, L): continue
                out.append((f, i, ln)); break
    return out

def caught_wide(K):
    pa = re.compile(u"^#+ .*A3 [" + JOU + JO + u"] " + re.escape(K) + NA)
    pb = re.compile(u"^- " + re.escape(u"**" + K) + NA)
    pc = re.compile(u"^- " + STAR + re.escape(K) + NA)
    pd = re.compile(u"^#+ .*A3 " + NO + u"[" + JOU + JO + u"] " + re.escape(K) + NA)
    out = []
    for f, lines in DOCS:
        for i, ln in enumerate(lines):
            if pa.match(ln) or pb.match(ln) or pc.match(ln) or pd.match(ln):
                out.append((f, i+1, ln))
    return out

UNC = list(range(181,207)) + list(range(219,249)) + [263] + list(range(272,276))
assert len(UNC) == 61, "UNC61"

print("== 0 haha ==")
nl = sum(len(l) - 1 for _, l in DOCS)
print("  files order*.md = %d ; lines(wc) = %d" % (len(FILES), nl))

now_caught = [n for n in UNC if caught_wide(kan(n))]
rest = [n for n in UNC if n not in now_caught]
print("== 1 of the 61, how many does the WIDE net now catch ==")
print("  caught = %d ; rest = %d" % (len(now_caught), len(rest)))
assert len(rest) == 40, "REST40"
print("  caught list = %s" % ",".join(str(x) for x in now_caught))
print("  rest list   = %s" % ",".join(str(x) for x in rest))

def has_jou(ln): return (JOU in ln) or (JO in ln)

BK = {"F2": [], "F6": [], "F7": [], "G": []}
DET = []
for n in rest:
    K = kan(n); ms = mentions(K)
    f2 = [m for m in ms if m[2].startswith(u"#") and has_jou(m[2])]
    f6 = [m for m in ms if m[2].startswith(u"- ") and has_jou(m[2])]
    f7 = [m for m in ms if (not m[2].startswith(u"#")) and (not m[2].startswith(u"- ")) and has_jou(m[2])]
    if f2: k = "F2"; pick = f2[0]
    elif f6: k = "F6"; pick = f6[0]
    elif f7: k = "F7"; pick = f7[0]
    else: k = "G"; pick = ms[0] if ms else (u"", 0, u"")
    BK[k].append(n); DET.append((n, k, len(ms), pick))
print("== 2 the 40 by FORM (order264 kitei-tanni) ==")
for k, nm in (("F2", "midashi (jou-go ari, wide net no soto)"),
              ("F6", "kajou no bun-chuu"),
              ("F7", "ji-no-bun"),
              ("G", "handan shi-enu")):
    print("  %s %-34s n=%d nums=%s" % (k, nm, len(BK[k]), ",".join(str(x) for x in BK[k])))
tot = sum(len(BK[k]) for k in BK)
print("  sum = %d" % tot)
assert tot == 40, "SUM40"

print("== 3 the 40, one line each ==")
for n, k, h, pick in DET:
    f, i, ln = pick
    print("  n=%d %s hits=%d %s:%d | %s" % (n, k, h, f.split("/")[-1] if f else "-", i+1, ln[:76]))

print("== 4 G no uchiwake (kata betsu) ==")
for n in BK["G"]:
    ms = mentions(kan(n))
    f, i, ln = ms[0]
    fm = ("G1 kuro2" if ln.startswith(u"- " + STAR + STAR) else
          "G2 hoshi2-kuro" if ln.startswith(u"- " + u"**" + STAR) else
          "G3 midashi-jou-nashi" if ln.startswith(u"#") else "G4 hoka")
    print("  n=%d %s hits=%d %s:%d | %s" % (n, fm, len(ms), f.split("/")[-1], i+1, ln[:70]))

print("== 5 POSCTRL (one each of F2/F6/F7 must have >=1 mention) ==")
pg = 0
for k in ("F2", "F6", "F7"):
    if BK[k]:
        n = BK[k][0]; m = mentions(kan(n))
        print("  %s n=%d hits=%d" % (k, n, len(m)))
        if m: pg += 1
    else:
        print("  %s EMPTY" % k)
print("  POSCTRL %s (%d/3)" % ("tootta" if pg == 3 else "TOORANU", pg))

print("== 6 NEGCTRL (oki-naoshi: han-gai / katachi-kuzure) ==")
NEG = [(u"han-gai 4keta", u"### " + STAR + u"A3 " + NO + JOU + u" " + SEN + u"五百" + STAR),
       (u"katachi space nashi", u"### " + STAR + u"A3" + NO + JOU + u" " + kan(438) + STAR),
       (u"katachi hyphen space nashi", u"-" + STAR + kan(438) + STAR),
       (u"katachi hoshi ippon", u"- *" + kan(438) + u"*")]
PATS = [re.compile(u"^#+ .*A3 [" + JOU + JO + u"] (" + KANC + u")"),
        re.compile(u"^- " + re.escape(u"**") + u"(" + KANC + u")" + re.escape(u"**")),
        re.compile(u"^- " + STAR + u"(" + KANC + u")" + STAR),
        re.compile(u"^#+ .*A3 " + NO + u"[" + JOU + JO + u"] (" + KANC + u")")]
ng = 0
for nm, ln in NEG:
    hit = [j for j, rx in enumerate(PATS) if rx.match(ln)]
    print("  %-28s %s -> %s" % (nm, ln[:30], hit if hit else "none"))
    if not hit: ng += 1
print("  NEGCTRL %s (%d/4)" % ("tootta" if ng == 4 else "TOORANU", ng))
print("  (o266 boundary NEGCTRL was 4/4 ; not re-run here)")

print("== 7 the 21 of 181..201 : which shot forged them, and when ==")
RX_AS = re.compile(u"as_of " + chr(96) + u"([0-9T:+-]+)" + chr(96))
def koku(f):
    s = io.open(f, encoding="utf-8").read()
    m = RX_AS.search(s)
    if m: return m.group(1), "as_of"
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(f))), "mtime"
ks = []
for n in range(181, 202):
    c = caught_wide(kan(n))
    if not c:
        print("  n=%d NO-CATCH" % n); continue
    f, i, ln = c[0]
    kk, src = koku(f)
    ks.append(kk)
    print("  n=%d %s:%d koku=%s(%s) | %s" % (n, f.split("/")[-1], i, kk, src, ln[:56]))
if ks:
    print("  obi no haba : saiko=%s / saishin=%s" % (min(ks), max(ks)))
