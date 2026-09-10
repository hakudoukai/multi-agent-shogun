# -*- coding: utf-8 -*-
# order268 : (ka) split F2 13 into jou-midashi / obi-midashi / sonota
#            (ki) G13 chikugo + "if the G forms were put into the rule, how many more"
# the o266 net is NOT changed here. the G form is applied in a SEPARATE function.
import io, glob, re

D = "scratch/ashigaru-third-3-12e9d4bd/"
FILES = sorted(glob.glob(D + "order*.md"))
DIG = [chr(c) for c in (0x4E00,0x4E8C,0x4E09,0x56DB,0x4E94,0x516D,0x4E03,0x516B,0x4E5D)]
TEN = chr(0x5341); HUN = chr(0x767E); SEN = chr(0x5343)
JOU = chr(0x689D); JO = chr(0x6761); STAR = chr(0x2605); NO = chr(0x306E)
DIGSET = u"".join(DIG) + TEN + HUN
BOUND = set(DIGSET)
NA = u"(?![" + DIGSET + u"])"
RUNSET = DIGSET + SEN  # v2 : SEN wo kuwaeru no wa nums_in dake ; ami (KOU/OTSU/HEI/NEWF/G1/G2) no DIGSET wa fuhen
RUN = re.compile(u"[" + RUNSET + u"]+")

def kan(n):
    h = n//100; t = (n//10)%10; o = n%10; s = u""
    if h: s += (u"" if h == 1 else DIG[h-1]) + HUN
    if t: s += (u"" if t == 1 else DIG[t-1]) + TEN
    if o: s += DIG[o-1]
    return s

def val(s):
    n = 0; cur = 0
    for ch in s:
        if ch in DIG: cur = DIG.index(ch) + 1
        elif ch == HUN: n += (cur if cur else 1) * 100; cur = 0
        elif ch == SEN: n += (cur if cur else 1) * 1000; cur = 0
        elif ch == TEN: n += (cur if cur else 1) * 10; cur = 0
    return n + cur

DOCS = [(f, io.open(f, encoding="utf-8").read().split(chr(10))) for f in FILES]
print("== 0 haha ==")
print("  files order*.md = %d ; lines(wc) = %d" % (len(FILES), sum(len(l)-1 for _, l in DOCS)))

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

def has_jou(ln): return (JOU in ln) or (JO in ln)

def nums_in(ln):
    out = []
    for m in RUN.finditer(ln):
        v = val(m.group(0))
        if 100 <= v <= 999 and v not in out: out.append(v)
    return out

F2 = [219,225,226,228,229,234,235,237,238,239,244,246,263]
assert len(F2) == 13, "F2-13"
print("== 1 ka : F2 13 wo mittsu ni waru (jou461 wo ki ni otosu) ==")
B = {"JOU": [], "OBI": [], "SONOTA": []}
ROWS = []
for n in F2:
    ms = [m for m in mentions(kan(n)) if m[2].startswith(u"#") and has_jou(m[2])]
    f, i, ln = ms[0]
    ns = nums_in(ln)
    k = "JOU" if len(ns) == 1 else ("OBI" if len(ns) >= 2 else "SONOTA")
    B[k].append(n)
    ROWS.append((n, k, len(ns), ns, f.split("/")[-1], i+1, len(ms)))
for k, nm in (("JOU", "jou no midashi (ban hitotsu)"),
              ("OBI", "obi no midashi (ban futatsu ijou)"),
              ("SONOTA", "sonota (ban zero)")):
    print("  %-6s %-34s n=%d nums=%s" % (k, nm, len(B[k]), ",".join(str(x) for x in B[k])))
tot = sum(len(B[k]) for k in B)
print("  sum = %d" % tot)
assert tot == 13, "SUM13"
assert (len(B["JOU"]), len(B["OBI"]), len(B["SONOTA"])) == (10, 3, 0), "KA-FUHEN"
print("  v2 chuu : monosashi (nums_in ni SEN) wo ugokashita ga KA no wari wa 10/3/0 no mama (assert)")
print("== 2 ka-2 : ban no kazu to gyou no kazu wo betsu ran ni (jou461) ==")
gy = set()
allban = 0
for n, k, c, ns, fn, i, h in ROWS:
    gy.add((fn, i)); allban += c
    print("  n=%3d %-6s ban=%d %s %s:%d (midashi-gensei %d)" % (n, k, c, ns, fn, i, h))
print("  hon no kazu = 13 ; gyou no kazu (soui naru) = %d ; ban no kazu (gou) = %d" % (len(gy), allban))
print("== 3 ka-3 : onaji gyou wo futatsu no hon ga motsu rei ==")
from collections import defaultdict
d = defaultdict(list)
for n, k, c, ns, fn, i, h in ROWS: d[(fn, i)].append(n)
for key in sorted(d, key=lambda x: (x[0], x[1])):
    if len(d[key]) > 1:
        print("  %s:%d <- n=%s" % (key[0], key[1], ",".join(str(x) for x in d[key])))
print("== 4 ki : G13 (kitei he wa IRENU ; katachi wa betsu kansuu de ateru) ==")
G13 = [221,222,223,231,233,241,242,243,247,248,272,273,274]
assert len(G13) == 13, "G-13"
G1 = re.compile(u"^- " + STAR + STAR + u"([" + DIGSET + u"]+)" + STAR + STAR)
G2 = re.compile(u"^- " + re.escape(u"**") + STAR + u"([" + DIGSET + u"]+)" + STAR)
def sweep(forms):
    got = {}
    for f, lines in DOCS:
        for ln in lines:
            for nm, rx in forms:
                m = rx.match(ln)
                if m:
                    v = val(m.group(1))
                    if 100 <= v <= 999: got.setdefault(v, set()).add(nm)
    return got
KOU  = re.compile(u"^#+ .*A3 [" + JOU + JO + u"] ([" + DIGSET + u"]+)")
OTSU = re.compile(u"^- " + re.escape(u"**") + u"([" + DIGSET + u"]+)" + re.escape(u"**"))
HEI  = re.compile(u"^- " + STAR + u"([" + DIGSET + u"]+)" + STAR)
NEWF = re.compile(u"^#+ .*A3 " + NO + u"[" + JOU + JO + u"] ([" + DIGSET + u"]+)")
WIDE = [("kou", KOU), ("otsu", OTSU), ("hei", HEI), ("kou2", NEWF)]
wide = set(sweep(WIDE).keys())
plus = sweep(WIDE + [("g1", G1), ("g2", G2)])
allp = set(plus.keys())
add = sorted(allp - wide)
print("  wide net (fuhen) = %d" % len(wide))
print("  wide + G forms   = %d" % len(allp))
print("  MIKOMI : fueru hon = %d" % len(add))
print("  fueru ban = %s" % ",".join(str(x) for x in add))
print("  uchi G13 ni fukumareru = %d ; G13 no soto = %d"
      % (len([x for x in add if x in G13]), len([x for x in add if x not in G13])))
print("  chuu : kono kazu wa MIKOMI (kitei wa kaete inai ; betsu kansuu de ateta dake)")
print("== 5 ki-2 : G13 ichiken ichigyou ==")
for n in G13:
    ms = mentions(kan(n))
    f, i, ln = ms[0]
    fm = ("G1" if ln.startswith(u"- " + STAR + STAR) else
          "G2" if ln.startswith(u"- " + u"**" + STAR) else "G?")
    print("  n=%3d %s hits=%d %s:%d" % (n, fm, len(ms), f.split("/")[-1], i+1))
print("== 6 POSCTRL ==")
p1 = len(nums_in(u"## " + STAR + JOU + u" " + kan(225) + u"〜" + kan(228) + STAR)) == 2
p2 = len(nums_in(u"### " + STAR + JOU + u" " + kan(237) + STAR)) == 1
print("  obi(2 ban) -> %s ; jou(1 ban) -> %s" % (p1, p2))
print("  POSCTRL %s (%d/2)" % ("tootta" if (p1 and p2) else "TOORANU", int(p1) + int(p2)))
print("== 7 NEGCTRL (han-gai / katachi-kuzure) ==")
n1 = nums_in(u"## " + STAR + JOU + u" 千五百" + STAR) == []
n2 = G1.match(u"-" + STAR + STAR + kan(221) + STAR + STAR) is None
n3 = G2.match(u"- *" + STAR + kan(231) + STAR) is None
print("  han-gai 4keta -> %s ; G1 space nashi -> %s ; G2 hoshi ippon -> %s" % (n1, n2, n3))
print("  NEGCTRL %s (%d/3)" % ("tootta" if (n1 and n2 and n3) else "TOORANU", int(n1)+int(n2)+int(n3)))
