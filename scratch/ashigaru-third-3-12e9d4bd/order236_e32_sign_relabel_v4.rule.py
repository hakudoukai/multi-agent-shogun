# -*- coding: utf-8 -*-
# order236 E32 v4 : the live load-bearing numbers -- every 答 line of the E-series papers,
# with the kind of instrument that produced it. read-only.
import io, os, re, glob, collections
D = u"scratch/ashigaru-third-3-12e9d4bd"
AST = re.compile(r"\bast\.")
kind = {}
for f in sorted(glob.glob(os.path.join(D, u"*.rule.py"))):
    src = io.open(f, encoding="utf-8").read()
    base = re.sub(r"_v\d+\.rule\.py$", u"", os.path.basename(f))
    k = u"kei" if AST.search(src) else u"go"
    kind[base] = u"kei" if (kind.get(base) == u"kei" or k == u"kei") else u"go"
NUM = re.compile(r"[0-9][0-9,]*")
pat = re.compile(r"^order(1[6-9][0-9]|2[0-9][0-9])_")
rows = []
for p in sorted(glob.glob(os.path.join(D, u"order*.md"))):
    b = os.path.basename(p)
    if not pat.match(b): continue
    base = re.sub(r"_v\d+\.md$", u"", b)
    k = kind.get(base, u"?")
    ls = io.open(p, encoding="utf-8").read().split(chr(10))
    ans = u""
    for ln in ls[:30]:
        if (u"本弾の答" in ln or ln.strip().startswith(u"★答")) and NUM.search(ln):
            ans = ln.strip(); break
    if ans: rows.append((b, k, ans))
print("== E-series papers carrying an explicit 答 line : %d ==" % len(rows))
c = collections.Counter(r[1] for r in rows)
print("   by instrument kind: %s" % dict(c))
print("")
for b, k, ans in rows:
    print("-- [%s] %s" % (k, b))
    print("   nums=%s" % ",".join(NUM.findall(ans)[:14]))
    print("   %s" % ans[:230])
    print("")
