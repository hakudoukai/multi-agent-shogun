# -*- coding: utf-8 -*-
# order266 -- wide net (karo saiketsu 2): OLD three forms + "A3 no JOU NNN" form.
# reads only scratch/ashigaru-third-3-12e9d4bd/order*.md . writes nothing.
# OLD net is the verbatim net of o261c_sweep40.rule.py (reproduced in order265_net191).
import io, re, glob, hashlib

DIG = [chr(c) for c in (0x4E00,0x4E8C,0x4E09,0x56DB,0x4E94,0x516D,0x4E03,0x516B,0x4E5D)]
TEN = chr(0x5341); HUN = chr(0x767E)
JOU = chr(0x689D); JO = chr(0x6761); STAR = chr(0x2605); NO = chr(0x306E)
DIGSET = u"".join(DIG) + TEN + HUN
BOUND = set(DIGSET)
KAN = u"[" + DIGSET + u"]+"

def kan(n):
    h = n // 100; t = (n // 10) % 10; o = n % 10; s = u""
    if h: s += (u"" if h == 1 else DIG[h-1]) + HUN
    if t: s += (u"" if t == 1 else DIG[t-1]) + TEN
    if o: s += DIG[o-1]
    return s

def val(s):
    n = 0; cur = 0
    for ch in s:
        if ch in DIG: cur = DIG.index(ch) + 1
        elif ch == HUN: n += (cur if cur else 1) * 100; cur = 0
        elif ch == TEN: n += (cur if cur else 1) * 10; cur = 0
    return n + cur

A3DIR = "scratch/ashigaru-third-3-12e9d4bd/"
FILES = sorted(glob.glob(A3DIR + "order*.md"))

KOU  = re.compile(u"^#+ .*A3 [" + JOU + JO + u"] (" + KAN + u")")
OTSU = re.compile(u"^- " + re.escape(u"**") + u"(" + KAN + u")" + re.escape(u"**"))
HEI  = re.compile(u"^- " + STAR + u"(" + KAN + u")" + STAR)
NEWF = re.compile(u"^#+ .*A3 " + NO + u"[" + JOU + JO + u"] (" + KAN + u")")
OLD  = [("kou", KOU), ("otsu", OTSU), ("hei", HEI)]
WIDE = OLD + [("kou2", NEWF)]

def sweep(forms):
    got = {}
    for f in FILES:
        for ln in io.open(f, encoding="utf-8").read().split(chr(10)):
            for nm, rx in forms:
                m = rx.match(ln)
                if m:
                    v = val(m.group(1))
                    if 100 <= v <= 999:
                        got.setdefault(v, set()).add(nm)
    return got

nl = 0
for f in FILES:
    nl += len(io.open(f, encoding="utf-8").read().split(chr(10))) - 1
print("== 0 haha ==")
print("  files order*.md = %d ; lines(wc) = %d" % (len(FILES), nl))

oldg = sweep(OLD); newg = sweep(WIDE)
old = set(oldg); new = set(newg)
print("== 1 old net (o261c form, unchanged) ==")
print("  old total = %d" % len(old))
print("== 2 wide net (old + A3 no JOU) ==")
print("  new total = %d" % len(new))
assert old <= new, "CONTAIN"
print("  assert old subset of new = tootta (old=%d all inside new)" % len(old))
add = sorted(new - old)
print("  newly caught n = %d ; list = %s" % (len(add), ",".join(str(x) for x in add)))

SPAN = (169, 420)
ins = sorted(x for x in new if SPAN[0] <= x <= SPAN[1])
out = sorted(x for x in new if not (SPAN[0] <= x <= SPAN[1]))
print("== 3 span 169..420 (wide net) ==")
print("  inside = %d ; outside = %d ; total = %d" % (len(ins), len(out), len(new)))
print("  outside list = %s" % ",".join(str(x) for x in out))
oins = sorted(x for x in old if SPAN[0] <= x <= SPAN[1])
print("  (old net inside span = %d)" % len(oins))

print("== 4 POSCTRL 438..447 must be 10/10 in wide net ==")
hit = [x for x in range(438, 448) if x in new]
miss = [x for x in range(438, 448) if x not in new]
print("  hit = %d/10 ; miss = %s" % (len(hit), ",".join(str(x) for x in miss) if miss else "none"))
print("  POSCTRL %s" % ("tootta" if len(hit) == 10 else "TOORANU"))
for x in (438, 447):
    print("  form of %d = %s" % (x, ",".join(sorted(newg.get(x, set())))))

print("== 5 NEGCTRL-a (order264 boundary 4, verbatim) ==")
def okb(ln, j, L):
    if j > 0 and ln[j-1] in BOUND: return False
    if j + L < len(ln) and ln[j+L] in BOUND: return False
    return True
ng = 0
for a, b in ((190,197),(200,201),(220,225),(240,244)):
    KA = kan(a); KB = kan(b); j = KB.find(KA)
    m = (j >= 0 and okb(KB, j, len(KA)))
    print("  K(%d)=%s inside K(%d)=%s -> matched=%s (want False)" % (a, KA, b, KB, m))
    if not m: ng += 1
print("  NEGCTRL-a %s (%d/4)" % ("tootta" if ng == 4 else "TOORANU", ng))

print("== 6 NEGCTRL-b (wide net must not catch these 4 synthetic lines) ==")
NEG = [u"### " + STAR + u"A3 " + NO + JOU + u" " + kan(999) + STAR,
       u"A3 " + NO + JOU + u" " + kan(438) + u" ha ji-no-bun",
       u"### " + STAR + u"A3 " + NO + JOU + STAR,
       u"- " + kan(438) + u" (no star, no bold)"]
nb = 0
for ln in NEG:
    hits = [nm for nm, rx in WIDE if rx.match(ln)]
    print("  %s -> %s" % (ln[:34], ",".join(hits) if hits else "none"))
    if not hits: nb += 1
print("  NEGCTRL-b %s (%d/4)" % ("tootta" if nb == 4 else "TOORANU", nb))

print("== 7 N2 (jissoku, koku 2026-09-10) ==")
UTSUSHI = 45
print("  A3 wide net = %d ; utsushi = %d (A2 25 / karo 20 ; ami mi-soku) ; N2 = %d"
      % (len(new), UTSUSHI, len(new) + UTSUSHI))
print("  N (2026-09-09) = 253 (fudou)")
print("  mikomi 310 - N2 = %d" % (310 - (len(new) + UTSUSHI)))
h = hashlib.sha256(io.open(A3DIR + "order266_net_wide.rule.py", "rb").read()).hexdigest()[:16]
print("== 8 self ==")
print("  self sha16 = %s" % h)
