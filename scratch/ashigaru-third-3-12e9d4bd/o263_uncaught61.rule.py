# -*- coding: utf-8 -*-
# o263: classify the 61 uncaught numbers in span 169..420 into three kinds.
import io, glob, re

D = "scratch/ashigaru-third-3-12e9d4bd/"
files = sorted(glob.glob(D + "order*.md"))

DIG = [chr(c) for c in (0x4E00, 0x4E8C, 0x4E09, 0x56DB, 0x4E94, 0x516D, 0x4E03, 0x516B, 0x4E5D)]
TEN = chr(0x5341); HUN = chr(0x767E)
JOU = chr(0x689D); JO = chr(0x6761); STAR = chr(0x2605)
BOUND = set(DIG) | set([TEN, HUN])

def kan(n):
    h = n // 100; t = (n // 10) % 10; o = n % 10
    s = u""
    if h: s += (u"" if h == 1 else DIG[h - 1]) + HUN
    if t: s += (u"" if t == 1 else DIG[t - 1]) + TEN
    if o: s += DIG[o - 1]
    return s

docs = []
for f in files:
    docs.append((f, io.open(f, encoding="utf-8").read().split(chr(10))))
NLINES = sum(len(x[1]) for x in docs)

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
                out.append((f, i + 1, ln)); break
    return out

def caught(K):
    pa = re.compile(u"^#+ .*A3 [" + JOU + JO + u"] " + re.escape(K))
    pb = re.compile(u"^- " + re.escape(u"**" + K + u"**"))
    pc = re.compile(u"^- " + STAR + re.escape(K) + STAR)
    out = []
    for f, lines in docs:
        for i, ln in enumerate(lines):
            if pa.match(ln) or pb.match(ln) or pc.match(ln):
                out.append((f, i + 1, ln))
    return out

# positive control: four numbers known to be minted A3 rules
CTRL = [255, 286, 323, 370]
ctrl_hit = {n: len(caught(kan(n))) for n in CTRL}
print("files=%d lines=%d" % (len(files), NLINES))
print("kan_sample 169=%s 206=%s 263=%s 420=%s" % (kan(169), kan(206), kan(263), kan(420)))
print("POSCTRL %s" % ctrl_hit)
assert all(v >= 1 for v in ctrl_hit.values()), "POSCTRL_FAIL"

UNC = list(range(181, 207)) + list(range(219, 249)) + [263] + list(range(272, 276))
assert len(UNC) == 61, "UNC=%d" % len(UNC)

buckets = {"CAUGHT": [], "JUMP": [], "NETFAULT": [], "UNDECIDABLE": []}
rep = {}
forms = []
for n in UNC:
    K = kan(n); c = caught(K); m = mentions(K)
    if c:
        cls = "CAUGHT"
    elif not m:
        cls = "JUMP"
    else:
        has = any((JOU in ln or JO in ln) for _, _, ln in m)
        cls = "NETFAULT" if has else "UNDECIDABLE"
    buckets[cls].append(n)
    if cls not in rep and (m or c):
        src = c if c else m
        rep[cls] = (n, src[0][0], src[0][1], src[0][2][:150])
    if cls == "NETFAULT" and len(forms) < 6:
        forms.append((n, m[0][0], m[0][1], m[0][2][:150]))

print("=== THREE KINDS ===")
for k in ("CAUGHT", "JUMP", "NETFAULT", "UNDECIDABLE"):
    print("%s = %d  nums=%s" % (k, len(buckets[k]), buckets[k]))
assert sum(len(v) for v in buckets.values()) == 61, "SUM"
print("=== REPRESENTATIVE (one line each) ===")
for k in ("CAUGHT", "NETFAULT", "UNDECIDABLE"):
    if k in rep:
        n, f, i, ln = rep[k]
        print("%s n=%d %s:%d | %s" % (k, n, f.split("/")[-1], i, ln))
    else:
        print("%s : none" % k)
print("=== NETFAULT FORMS (one line per form) ===")
for n, f, i, ln in forms:
    print("n=%d %s:%d | %s" % (n, f.split("/")[-1], i, ln))
