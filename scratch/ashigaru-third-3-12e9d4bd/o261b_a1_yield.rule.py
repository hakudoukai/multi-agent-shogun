# -*- coding: utf-8 -*-
# o261b -- measure the yield of the three shapes on the A1 net (事例記録). read-only.
import io, os, glob, hashlib
ROOT = "/home/hakudoukai/a1/wt-handover-fe-2/reports/handover-fe-6db6fbe1"
TRIG = {"m1": [u"知らぬ", u"見当が付かぬ", u"一件も無い", u"新しく見えた"],
        "m2": [u"母無し", u"測れず", u"現に無い"],
        "m3": [u"不確かさ"]}
allp = sorted(glob.glob(os.path.join(ROOT, "*.md")))
N = len(allp)
idx = sorted(set(int(round(i * (N - 1) / 19.0)) for i in range(20)))
sample = [allp[i] for i in idx]
print("net root basename = %s" % os.path.basename(ROOT))
print("papers present = %d ; sample = %d (evenly spaced over the sorted list)" % (N, len(sample)))
h = hashlib.sha256(("\n".join(os.path.basename(x) for x in sample)).encode("utf-8")).hexdigest()[:16]
print("sample name-list sha16 = %s" % h)
tot_lines = 0
hits = dict((k, 0) for k in TRIG)
carrier = dict((k, 0) for k in TRIG)
m3lines = []
for f in sample:
    lines = io.open(f, encoding="utf-8", errors="replace").read().split(chr(10))
    tot_lines += len(lines)
    seen = dict((k, 0) for k in TRIG)
    for i, L in enumerate(lines):
        for k, ws in TRIG.items():
            if any(w in L for w in ws):
                hits[k] += 1
                seen[k] += 1
                if k == "m3":
                    m3lines.append((os.path.basename(f), i + 1, L.strip()[:220]))
    for k in TRIG:
        if seen[k]:
            carrier[k] += 1
print("lines read = %d" % tot_lines)
for k in ("m1", "m2", "m3"):
    print("  %s hit_lines=%-4d carrier_papers=%-3d per_paper=%.4f per_line=%.6f"
          % (k, hits[k], carrier[k], hits[k] / 20.0, hits[k] / float(tot_lines)))
print("== m3 hit lines verbatim (for hand judgement, 段20) ==")
for b, ln, t in m3lines[:40]:
    print("  [%s:%d] %s" % (b, ln, t))
print("m3 hit line count printed = %d / %d" % (min(40, len(m3lines)), len(m3lines)))
