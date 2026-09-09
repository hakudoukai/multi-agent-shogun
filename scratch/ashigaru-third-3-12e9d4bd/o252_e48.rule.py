# -*- coding: utf-8 -*-
# E48 ―― 母を 15 迄 埋めよ。単位A(条)/単位B(事例)を別々に数へ、門を二形で出す。
import io, re, math, hashlib, collections, glob

def rd(p): return io.open(p, encoding='utf-8').read()
def stamp(p):
    s = rd(p); b = io.open(p, 'rb').read()
    return (p, len(s.split(chr(10))) - 1, len(s.split(chr(10))),
            hashlib.sha256(b).hexdigest()[:16], len(b))

A3DIR = "scratch/ashigaru-third-3-12e9d4bd/"
A2IDX = "scratch/ashigaru-third-2-fa06a3a1/o97_handover_index_v1.md"
A2CLS = "scratch/ashigaru-third-2-fa06a3a1/o257_order66_classify.py"
KARO  = "scratch/karo-third-12e9d4bd/reboot_checkpoint_20260906_1431.md"
BOX   = "queue/inbox/ashigaru-third-3.yaml"

print("== 1 stamps ==")
for p in [A2IDX, A2CLS, KARO, BOX]:
    print("  %s wc=%d split=%d sha16=%s B=%d" % stamp(p))

KAN = u"[一二三四五六七八九十百]+"
n_jou = set()
for f in sorted(glob.glob(A3DIR + "order*.md")):
    for ln in rd(f).split(chr(10)):
        m = re.match(u'^#+ .*A3 (?:條|条) (' + KAN + u')(?![一-十])', ln) \
            or re.match(u'^- \\*\\*(' + KAN + u')\\*\\*', ln) \
            or re.match(u'^- ★(' + KAN + u')★', ln)
        if m: n_jou.add(m.group(1))
a2 = [l for l in rd(A2IDX).split(chr(10)) if re.match(u'^\\| \\d+ \\|', l)]
kj = set(re.findall(u'作法\\(家老\\)★(' + KAN + u')条目★', rd(KARO)))
print("== 2 unitA denominator (E46 was 158/17/20=195) ==")
print("  A3=%d A2=%d karo=%d total=%d" % (len(n_jou), len(a2), len(kj),
                                          len(n_jou) + len(a2) + len(kj)))
NEW8 = [u"三百八十八", u"三百八十九", u"三百九十", u"三百九十一",
        u"三百九十二", u"三百九十三", u"三百九十四", u"三百九十五"]
print("  new A3 jou 388-395 present = %d/8" % sum(1 for x in NEW8 if x in n_jou))

rows = re.findall(u'^\\s*(\\d+):\\s*\\(u"([^"]*)",\\s*u"([^"]*)",\\s*u"([^"]*)"\\)', rd(A2CLS), re.M)
cat = collections.Counter(r[1] for r in rows)
strad = [r for r in rows if u"跨がず" in r[1]]
kind = collections.Counter(r[2] for r in strad)
act = sum(v for k, v in kind.items() if u"実測" in k)
print("== 3 A2 51 labels (unit trap) ==")
print("  rows=%d ; %s" % (len(rows), u" / ".join(u"%s=%d" % (k, v) for k, v in cat.items())))
print("  straddle=%d -> ACTS=%d narration=%d" % (len(strad), act, len(strad) - act))
print("  one phenomenon counts as 1(jou) / %d(acts) / %d(labels)" % (act, len(strad)))

NA, F1 = 12, 2                       # unitA: 11 + A2 dan19
NB = 10 + act + 1 + 2                # 10 jou(>=1) + dan17 acts + dan19 act + A1 two
print("== 4 unitB lower bound ==")
print("  NB = 10 + %d + 1 + 2 = %d" % (act, NB))

def gateE47(p0):
    return int(math.ceil(math.log(0.05) / math.log(1.0 - p0)))
def gateP0(f1, a=0.05):
    return int(math.ceil(f1 / a))
print("== 5 two gates ==")
for nm, N in ((u"unitA", NA), (u"unitB", NB)):
    p0 = float(F1) / N
    print("  %s N=%d f1=%d p0=%.4f | E47gate needN=%d short=%d | p0<=0.05 gate needN=%d short=%d"
          % (nm, N, F1, p0, gateE47(p0), gateE47(p0) - N, gateP0(F1), gateP0(F1) - N))
print("== 6 why the E47 gate recedes (limit) ==")
for N in (11, 12, 15, 20, 40, 100, 1000):
    p0 = float(F1) / N
    print("  N=%5d p0=%.4f (1-p0)^N=%.4f  need=%d" % (N, p0, (1 - p0) ** N, gateE47(p0)))
print("  limit (1-f1/N)^N -> exp(-f1) = %.4f  (f1=2)" % math.exp(-2))
for f1 in (1, 2, 3, 4):
    print("  f1=%d -> exp(-f1)=%.4f  passes 0.05? %s" % (f1, math.exp(-f1),
          u"yes" if math.exp(-f1) <= 0.05 else u"no"))
