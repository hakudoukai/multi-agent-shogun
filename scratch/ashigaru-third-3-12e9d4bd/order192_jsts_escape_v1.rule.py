# -*- coding: utf-8 -*-
u"""order192 繰越: 試験の逃げ道を ★js/ts の別母集団★ で数へる（py の悉皆とは別帳）。
併せて 追補其の三 §三 の指紋を ★分の桁★ で当て直す。讀取のみ・走行 0・書込 0・DB 0。
数へ方: 行を 1 と数へる(床30)。境界は明示クラス(床⒅)。大小文字の軸 = 当てて居らぬ(床25)。
"""
import os, io, re, hashlib
TREE = u"/home/hakudoukai/a3/wt-bundle-fix4"
SKIPD = set([u"node_modules", u".git", u".venv", u"venv", u"__pycache__", u"dist", u"build"])
EXT = (u".js", u".jsx", u".ts", u".tsx", u".mjs", u".cjs")
B = u"[^A-Za-z0-9_$]"
PATS = [
    (u"it.skip",        re.compile(u"(^|" + B + u")it\\.skip" + u"(" + B + u"|$)")),
    (u"test.skip",      re.compile(u"(^|" + B + u")test\\.skip" + u"(" + B + u"|$)")),
    (u"describe.skip",  re.compile(u"(^|" + B + u")describe\\.skip" + u"(" + B + u"|$)")),
    (u"it.todo",        re.compile(u"(^|" + B + u")it\\.todo" + u"(" + B + u"|$)")),
    (u"test.todo",      re.compile(u"(^|" + B + u")test\\.todo" + u"(" + B + u"|$)")),
    (u"xit",            re.compile(u"(^|" + B + u")xit" + u"(" + B + u"|$)")),
    (u"xdescribe",      re.compile(u"(^|" + B + u")xdescribe" + u"(" + B + u"|$)")),
    (u"it.only",        re.compile(u"(^|" + B + u")it\\.only" + u"(" + B + u"|$)")),
    (u"test.only",      re.compile(u"(^|" + B + u")test\\.only" + u"(" + B + u"|$)")),
    (u"describe.only",  re.compile(u"(^|" + B + u")describe\\.only" + u"(" + B + u"|$)")),
    (u"test.fixme",     re.compile(u"(^|" + B + u")test\\.fixme" + u"(" + B + u"|$)")),
    (u"test.fail",      re.compile(u"(^|" + B + u")test\\.fail" + u"(" + B + u"|$)")),
]

def walk():
    ok = set(); bad = set(); files = []
    for dp, dn, fn in os.walk(TREE):
        dn[:] = [x for x in dn if x not in SKIPD]
        for f in fn:
            ap = os.path.join(dp, f); rel = os.path.relpath(ap, TREE)
            try:
                src = io.open(ap, encoding="utf-8").read(); ok.add(rel)
            except Exception:
                bad.add(rel); continue
            if rel.lower().endswith(EXT):
                files.append((rel, src))
    return ok, bad, files

ok, bad, files = walk()
print(u"## §零 母数")
print(u"js/ts 系 file(SKIPD=%s を外す) = %d 枚" % (u",".join(sorted(SKIPD)), len(files)))
tf = [(r, s) for r, s in files if (u"/test" in u"/" + r.lower() or u"/__tests__/" in u"/" + r
      or os.path.basename(r).lower().startswith(u"test")
      or u".test." in os.path.basename(r).lower() or u".spec." in os.path.basename(r).lower())]
print(u"うち 試験らしき枚(名で判ず) = %d 枚" % len(tf))
print(u"")
print(u"## §一 逃げ道の度数（★行を 1 と数へる★・母集団 = js/ts 全 %d 枚）" % len(files))
tot = {}
per = {}
for name, rx in PATS:
    n = 0; fs = set()
    for rel, src in files:
        for i, l in enumerate(src.split(u"\n")):
            if rx.search(l):
                n += 1; fs.add(rel)
    tot[name] = n; per[name] = len(fs)
for name, _ in PATS:
    print(u"  %-16s 行=%4d  枚=%3d" % (name, tot[name], per[name]))
print(u"  ---- 合計行=%d ----" % sum(tot.values()))
print(u"")
print(u"## §二 当たつた file（枚>0 の物のみ・rel|sha256|wc|当たり行）")
seen = {}
for name, rx in PATS:
    for rel, src in files:
        hits = [i + 1 for i, l in enumerate(src.split(u"\n")) if rx.search(l)]
        if hits:
            seen.setdefault(rel, {})[name] = hits
for rel in sorted(seen):
    src = dict(files)[rel]
    h = hashlib.sha256(); h.update(io.open(os.path.join(TREE, rel), "rb").read())
    wc = io.open(os.path.join(TREE, rel), "rb").read().count(b"\n")
    kinds = u" ".join([u"%s:%d" % (k, len(v)) for k, v in sorted(seen[rel].items())])
    print(u"  %s | %s | wc=%d | %s" % (rel, h.hexdigest(), wc, kinds))
print(u"当たつた枚 = %d" % len(seen))
print(u"")
print(u"## §三 指紋を ★分の桁★ で当て直す（追補其の三 §三 との対）")
h1 = hashlib.sha256(); h1.update(u"\n".join(sorted(bad)).encode("utf-8"))
h2 = hashlib.sha256(); h2.update(u"\n".join(sorted(ok)).encode("utf-8"))
print(u"※ 本走の SKIPD は dist/build を足して居る ∴ 其の儘は比べられぬ（母数が違ふ）")
print(u"unreadable_set_sha256(本走)=%s n=%d" % (h1.hexdigest(), len(bad)))
print(u"readable_set_sha256(本走)=%s n=%d" % (h2.hexdigest(), len(ok)))
