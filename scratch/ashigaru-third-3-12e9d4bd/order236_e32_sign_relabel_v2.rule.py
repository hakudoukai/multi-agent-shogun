# -*- coding: utf-8 -*-
# order236 E32 v2 : pull the headline numbers of every 語(sign)-based paper family
# and mark what the number actually counts. read-only.
import io, os, re, glob, collections
D = u"scratch/ashigaru-third-3-12e9d4bd"
AST = re.compile(r"\bast\.")
fam_kind = {}
for f in sorted(glob.glob(os.path.join(D, u"*.rule.py"))):
    src = io.open(f, encoding="utf-8").read()
    base = re.sub(r"_v\d+\.rule\.py$", u"", os.path.basename(f))
    k = u"kei" if AST.search(src) else u"go"
    fam_kind[base] = u"kei" if (fam_kind.get(base) == u"kei" or k == u"kei") else u"go"

NUM = re.compile(r"[0-9][0-9,]*")
def headline(path):
    ls = io.open(path, encoding="utf-8").read().split(chr(10))
    for ln in ls[:40]:
        if u"答" in ln and NUM.search(ln): return ln.strip()
    for ln in ls[:40]:
        if ln.startswith(u"**") and NUM.search(ln): return ln.strip()
    for ln in ls[:60]:
        if NUM.search(ln) and not ln.startswith(u"#") and len(ln.strip()) > 20: return ln.strip()
    return u""

papers = sorted(glob.glob(os.path.join(D, u"*.md")))
by_fam = collections.defaultdict(list)
for p in papers:
    b = os.path.basename(p); base = re.sub(r"_v\d+\.md$", u"", b)
    by_fam[base].append(p)

go_fams = sorted(b for b, k in fam_kind.items() if k == u"go")
hit = 0; miss = []
print("== headline numbers of 語(sign)-based paper families ==")
for b in go_fams:
    ps = by_fam.get(b, [])
    if not ps:
        miss.append(b); continue
    p = sorted(ps)[-1]
    h = headline(p)
    ns = NUM.findall(h)
    if not ns: miss.append(b); continue
    hit += 1
    print("-- %s" % os.path.basename(p))
    print("   nums=%s" % (",".join(ns[:12])))
    print("   %s" % (h[:150]))
print("")
print("families 語 = %d / with paper+num = %d / without = %d" % (len(go_fams), hit, len(miss)))
print("without: %s" % ", ".join(miss))
