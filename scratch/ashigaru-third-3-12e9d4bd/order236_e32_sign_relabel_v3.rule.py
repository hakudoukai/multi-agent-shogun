# -*- coding: utf-8 -*-
# order236 E32 v3 : for every 語(sign) instrument, pull the literal signs it matched on.
# a number produced by such an instrument counts THAT literal, not the thing. read-only.
import io, os, re, glob, collections
D = u"scratch/ashigaru-third-3-12e9d4bd"
AST = re.compile(r"\bast\.")
# string literals: both quote kinds, u-prefixed or not (floor(16))
LIT = re.compile(r"u?[\"']([^\"'\n]{1,40})[\"']")
# lines where a literal is used as a matcher
USE = re.compile(r"(\bin\s+(ln|line|s|t|src|txt|body)\b|re\.(search|match|findall)|\.count\(|\.startswith\(|\.find\(|\.endswith\()")
SKIP = re.compile(r"^[\s\W_]*$|^(utf-8|scratch|ashigaru|md|py|git|w|r|rb|wb|\.md|\.py|\d+)$")
rows = []
for f in sorted(glob.glob(os.path.join(D, u"*.rule.py"))):
    src = io.open(f, encoding="utf-8").read()
    if AST.search(src): continue
    sigs = []
    for ln in src.split(chr(10)):
        if not USE.search(ln): continue
        if ln.strip().startswith(u"#"): continue
        for m in LIT.findall(ln):
            if SKIP.match(m): continue
            if m not in sigs: sigs.append(m)
    rows.append((os.path.basename(f), sigs))
tot = len(rows); withsig = [r for r in rows if r[1]]
print("== 語 instruments = %d / of which carry a literal sign = %d ==" % (tot, len(withsig)))
print("")
allsig = collections.Counter()
for nm, sigs in withsig:
    for s in sigs: allsig[s] += 1
print("== the signs themselves (literal, times used across instruments) ==")
for s, c in allsig.most_common():
    print("  %2d  %s" % (c, s))
print("")
print("== instrument -> its signs ==")
for nm, sigs in withsig:
    print("-- %s" % nm)
    print("   %s" % (u" / ".join(sigs[:10]) if sigs else u"-"))
print("")
print("distinct signs = %d" % len(allsig))
