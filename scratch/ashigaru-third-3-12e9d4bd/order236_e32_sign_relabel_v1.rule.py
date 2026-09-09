# -*- coding: utf-8 -*-
# order236 E32 v1 : classify my own 102 instruments into 形(ast) / 語(sign) / 帳(ledger)
# and say what each one's net was cast over. read-only, no product run.
import io, os, re, glob, collections
D = u"scratch/ashigaru-third-3-12e9d4bd"
rules = sorted(glob.glob(os.path.join(D, u"*.rule.py")))
AST = re.compile(r"\bast\.")
TXT = re.compile(r"(in ln\b|in line\b|re\.(search|match|findall|split|sub)|\.count\(|\.startswith\(|\.find\(|\.endswith\(|in t\b|in s\b)")
# what the net was cast over
OVER_MD  = re.compile(r'u?"[^"]*\.md"|\*\.md|glob[^\n]*\.md')
OVER_PY  = re.compile(r'u?"[^"]*\.py"|\*\.py|\.py\b')
OVER_GIT = re.compile(r"git show|subprocess|check_output|rev-parse")
rows = []
for f in rules:
    src = io.open(f, encoding="utf-8").read()
    a = len(AST.findall(src)); t = len(TXT.findall(src))
    kind = u"kei" if a > 0 else (u"go" if t > 0 else u"cho")
    over = []
    if OVER_MD.search(src):  over.append(u"md")
    if OVER_PY.search(src):  over.append(u"py")
    if OVER_GIT.search(src): over.append(u"git")
    rows.append((os.path.basename(f), kind, a, t, u"+".join(over) or u"-", len(src.split(chr(10)))))
n = collections.Counter(r[1] for r in rows)
print("== 102 instruments by kind ==")
print("  kei(ast/shape) = %d" % n[u"kei"])
print("  go (sign/word) = %d" % n[u"go"])
print("  cho(ledger)    = %d" % n[u"cho"])
print("  total          = %d" % len(rows))
print("")
over_by_kind = collections.defaultdict(collections.Counter)
for nm, k, a, t, ov, ln in rows: over_by_kind[k][ov] += 1
print("== what the net was cast over ==")
for k in (u"kei", u"go", u"cho"):
    print("  %s : %s" % (k, dict(over_by_kind[k])))
print("")
print("== the 語(sign) instruments, ordered by name ==")
i = 0
for nm, k, a, t, ov, ln in rows:
    if k != u"go": continue
    i += 1
    print("  %02d %-52s text=%-3d over=%-8s lines=%d" % (i, nm, t, ov, ln))
print("")
print("== paper families fed by 語 instruments (prefix before _v) ==")
fam = collections.defaultdict(list)
for nm, k, a, t, ov, ln in rows:
    base = re.sub(r"_v\d+\.rule\.py$", u"", nm)
    fam[base].append(k)
gof = sorted(b for b, ks in fam.items() if all(x == u"go" for x in ks))
kef = sorted(b for b, ks in fam.items() if any(x == u"kei" for x in ks))
chf = sorted(b for b, ks in fam.items() if all(x == u"cho" for x in ks))
print("  families all-語  = %d" % len(gof))
print("  families with 形 = %d" % len(kef))
print("  families all-帳  = %d" % len(chf))
print("")
print("  -- all-語 families --")
for b in gof: print("     %s" % b)
print("  -- families with 形 --")
for b in kef: print("     %s" % b)
