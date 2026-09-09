# -*- coding: utf-8 -*-
# o258 -- one sweep: (3) recount the 206, (2) measure yield per source,
#         and pull out negative-side candidates from the 條 lines themselves.
# read-only. no product run.
import io, os, re, glob, collections

DIG = {u"一":1,u"二":2,u"三":3,u"四":4,u"五":5,u"六":6,u"七":7,u"八":8,u"九":9}
def kan2int(t):
    n = 0
    m = re.match(u"^([一二三四五六七八九]?)百(.*)$", t)
    if m:
        n += (DIG.get(m.group(1), 1)) * 100
        t = m.group(2)
    m = re.match(u"^([一二三四五六七八九]?)十(.*)$", t)
    if m:
        n += (DIG.get(m.group(1), 1)) * 10
        t = m.group(2)
    if t:
        if t not in DIG:
            return None
        n += DIG[t]
    return n

KAN = u"[一二三四五六七八九十百]+"
A3DIR = "scratch/ashigaru-third-3-12e9d4bd"
papers = sorted(glob.glob(os.path.join(A3DIR, "order*.md")))
FORMS = [
    ("kou", re.compile(u"^#+ .*A3 [條条] (" + KAN + u")")),
    ("otsu", re.compile(u"^- \\*\\*(" + KAN + u")\\*\\*")),
    ("hei", re.compile(u"^- ★(" + KAN + u")★")),
]
hit = {}                      # num -> (form, paper, line)
per_paper = collections.Counter()
form_uniq = collections.defaultdict(set)
lines_of = {}
for p in papers:
    try:
        txt = io.open(p, encoding="utf-8").read()
    except Exception:
        continue
    for ln in txt.split(chr(10)):
        for fname, rx in FORMS:
            m = rx.match(ln)
            if not m:
                continue
            v = kan2int(m.group(1))
            if v is None or v < 100 or v > 999:
                continue
            form_uniq[fname].add(v)
            if v not in hit:
                hit[v] = (fname, os.path.basename(p))
                per_paper[os.path.basename(p)] += 1
                lines_of[v] = ln.strip()
            break
print("== A3 papers scanned ==")
print("order*.md count = %d" % len(papers))
print("== A3 forms (unique numbers) ==")
for fname, _ in FORMS:
    print("  %-5s uniq=%d" % (fname, len(form_uniq[fname])))
nums = sorted(hit)
print("  union uniq = %d   min=%s max=%s" % (len(nums), nums[0] if nums else "-", nums[-1] if nums else "-"))
span = set(range(169, 421))
print("  span 169..420 = %d ; caught in span = %d ; MISSING in span = %d"
      % (len(span), len(span & set(nums)), len(span - set(nums))))
print("  caught outside span = %d" % len(set(nums) - span))

print("== yield per paper (papers that carry at least one 條) ==")
carriers = [k for k in per_paper if per_paper[k] > 0]
tot = sum(per_paper.values())
print("  carrier papers = %d / %d ; 條 = %d ; yield per carrier = %.3f ; per paper scanned = %.3f"
      % (len(carriers), len(papers), tot, float(tot)/len(carriers) if carriers else 0.0,
         float(tot)/len(papers) if papers else 0.0))

A2IDX = "scratch/ashigaru-third-2-fa06a3a1/o97_handover_index_v1.md"
KARO = "scratch/karo-third-12e9d4bd/reboot_checkpoint_20260906_1431.md"
def stat(p):
    if not os.path.exists(p):
        return None
    b = io.open(p, "rb").read()
    import hashlib
    return (b.count(chr(10).encode()), len(b), hashlib.sha256(b).hexdigest()[:16])

print("== A2 dan ==")
s = stat(A2IDX)
print("  path stat wc=%s B=%s sha16=%s" % (s if s else ("-","-","-")))
a2 = set()
if s:
    t = io.open(A2IDX, encoding="utf-8").read()
    for ln in t.split(chr(10)):
        m = re.match(u"^\\|[ ]*([0-9]{1,3})[ ]*\\|", ln)
        if m:
            a2.add(int(m.group(1)))
    print("  table-row form uniq numbers = %d  max=%s" % (len(a2), max(a2) if a2 else "-"))

print("== karo jou ==")
s = stat(KARO)
print("  path stat wc=%s B=%s sha16=%s" % (s if s else ("-","-","-")))
karo = set()
if s:
    t = io.open(KARO, encoding="utf-8").read()
    rx = re.compile(u"作法\\(家老\\)★(" + KAN + u")条目★")
    for m in rx.finditer(t):
        v = kan2int(m.group(1))
        if v:
            karo.add(v)
    print("  form uniq = %d  min=%s max=%s" % (len(karo), min(karo) if karo else "-", max(karo) if karo else "-"))

print("== denominator ==")
print("  A3=%d  A2=%d  KARO=%d  TOTAL=%d" % (len(nums), len(a2), len(karo), len(nums)+len(a2)+len(karo)))

print("== negative-side candidates inside the 條 lines themselves ==")
TRIG = {
    "m1": [u"知らぬ", u"見当が付かぬ", u"一件も無い", u"新しく見えた"],
    "m2": [u"母無し", u"測れず", u"現に無い"],
    "m3": [u"不確かさ"],
}
for key in ("m1", "m2", "m3"):
    got = [v for v in nums if any(w in lines_of[v] for w in TRIG[key])]
    print("  %s trigger hits among %d 條 lines = %d  -> %s"
          % (key, len(nums), len(got), ",".join(str(x) for x in sorted(got)[:20])))
