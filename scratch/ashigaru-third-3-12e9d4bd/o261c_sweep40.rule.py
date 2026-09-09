# -*- coding: utf-8 -*-
# o261c -- extend the SAME net (己の條 lines) onto 40 unscanned non-order papers. read-only.
import io, os, re, glob, hashlib
DIR = "scratch/ashigaru-third-3-12e9d4bd"
DIG = {u"一":1,u"二":2,u"三":3,u"四":4,u"五":5,u"六":6,u"七":7,u"八":8,u"九":9}
def kan2int(t):
    n = 0
    if u"百" in t:
        a, t = t.split(u"百", 1)
        n += (DIG.get(a, 1) if a else 1) * 100
    if u"十" in t:
        a, t = t.split(u"十", 1)
        n += (DIG.get(a, 1) if a else 1) * 10
    if t:
        n += DIG.get(t[-1], 0)
    return n
KAN = u"[一二三四五六七八九十百]+"
FORMS = [("kou", re.compile(u"^#+ .*A3 [條条] (" + KAN + u")")),
         ("otsu", re.compile(u"^- \\*\\*(" + KAN + u")\\*\\*")),
         ("hei", re.compile(u"^- ★(" + KAN + u")★"))]
TRIG = {"m1": [u"知らぬ", u"見当が付かぬ", u"一件も無い", u"新しく見えた"],
        "m2": [u"母無し", u"測れず", u"現に無い"],
        "m3": [u"不確かさ"]}
orders = set(os.path.basename(x) for x in glob.glob(os.path.join(DIR, "order*.md")))
allmd = sorted(x for x in glob.glob(os.path.join(DIR, "*.md"))
               if os.path.basename(x) not in orders)
N = len(allmd)
idx = sorted(set(int(round(i * (N - 1) / 39.0)) for i in range(40)))
sample = [allmd[i] for i in idx]
print("non-order papers = %d ; sample = %d" % (N, len(sample)))
print("sample name-list sha16 = %s"
      % hashlib.sha256(("\n".join(os.path.basename(x) for x in sample)).encode("utf-8")).hexdigest()[:16])
known = set()
for f in sorted(glob.glob(os.path.join(DIR, "order*.md"))):
    for L in io.open(f, encoding="utf-8", errors="replace").read().split(chr(10)):
        for _, rx in FORMS:
            m = rx.match(L)
            if m:
                v = kan2int(m.group(1))
                if 100 <= v <= 999:
                    known.add(v)
print("known 條 from order*.md = %d" % len(known))
new_nums = set(); jou_lines = []; tot_lines = 0
carrier = 0
for f in sample:
    lines = io.open(f, encoding="utf-8", errors="replace").read().split(chr(10))
    tot_lines += len(lines)
    got = 0
    for L in lines:
        for _, rx in FORMS:
            m = rx.match(L)
            if m:
                v = kan2int(m.group(1))
                if 100 <= v <= 999:
                    jou_lines.append((os.path.basename(f), v, L))
                    got += 1
                    if v not in known:
                        new_nums.add(v)
    if got:
        carrier += 1
print("條-form lines found in the 40 = %d ; carrier papers = %d ; lines read = %d"
      % (len(jou_lines), carrier, tot_lines))
print("of those, numbers NOT already in the 191 = %d -> %s"
      % (len(new_nums), ",".join(str(x) for x in sorted(new_nums))))
hits = dict((k, 0) for k in TRIG)
shown = []
for b, v, L in jou_lines:
    if v in known:
        continue
    for k, ws in TRIG.items():
        if any(w in L for w in ws):
            hits[k] += 1
            shown.append((k, b, v, L.strip()[:200]))
print("== negative-side hits among the NEW 條 lines only ==")
for k in ("m1", "m2", "m3"):
    print("  %s = %d ; per_paper(40) = %.4f  (o258 measured: m1 0.0588 / m2 0.0490 / m3 0.0000)"
          % (k, hits[k], hits[k] / 40.0))
for k, b, v, t in shown[:20]:
    print("  [%s][%s:%d] %s" % (k, b, v, t))
