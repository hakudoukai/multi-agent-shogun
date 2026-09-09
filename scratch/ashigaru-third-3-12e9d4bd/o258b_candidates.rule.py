# -*- coding: utf-8 -*-
# o258b -- print the negative-side candidate 條 lines for hand judgement,
#          the A2 number set, and the 61 uncaught numbers. read-only.
import io, os, re, glob
DIG = {u"一":1,u"二":2,u"三":3,u"四":4,u"五":5,u"六":6,u"七":7,u"八":8,u"九":9}
def kan2int(t):
    n = 0
    m = re.match(u"^([一二三四五六七八九]?)百(.*)$", t)
    if m:
        n += (DIG.get(m.group(1), 1)) * 100; t = m.group(2)
    m = re.match(u"^([一二三四五六七八九]?)十(.*)$", t)
    if m:
        n += (DIG.get(m.group(1), 1)) * 10; t = m.group(2)
    if t:
        if t not in DIG: return None
        n += DIG[t]
    return n
KAN = u"[一二三四五六七八九十百]+"
A3DIR = "scratch/ashigaru-third-3-12e9d4bd"
FORMS = [re.compile(u"^#+ .*A3 [條条] (" + KAN + u")"),
         re.compile(u"^- \\*\\*(" + KAN + u")\\*\\*"),
         re.compile(u"^- ★(" + KAN + u")★")]
lines_of = {}
src_of = {}
for p in sorted(glob.glob(os.path.join(A3DIR, "order*.md"))):
    for ln in io.open(p, encoding="utf-8").read().split(chr(10)):
        for rx in FORMS:
            m = rx.match(ln)
            if not m: continue
            v = kan2int(m.group(1))
            if v is None or v < 100 or v > 999: continue
            if v not in lines_of:
                lines_of[v] = ln.strip(); src_of[v] = os.path.basename(p)
            break
nums = sorted(lines_of)
want = [255,300,315,316,319,323,370,270,276,279,335,398]
print("== candidate 條 lines (trigger fired) ==")
for v in want:
    s = lines_of.get(v, "")
    print("[%d] %s :: %s" % (v, src_of.get(v,"-"), s[:230]))
print("== A2 number set ==")
a2 = set()
for ln in io.open("scratch/ashigaru-third-2-fa06a3a1/o97_handover_index_v1.md", encoding="utf-8").read().split(chr(10)):
    m = re.match(u"^\\|[ ]*([0-9]{1,3})[ ]*\\|", ln)
    if m: a2.add(int(m.group(1)))
print("  set == 1..25 ? %s ; n=%d ; sorted=%s" % (a2 == set(range(1,26)), len(a2), sorted(a2)))
print("== uncaught numbers in 169..420 ==")
miss = sorted(set(range(169,421)) - set(nums))
print("  n=%d" % len(miss))
print("  %s" % ",".join(str(x) for x in miss))
