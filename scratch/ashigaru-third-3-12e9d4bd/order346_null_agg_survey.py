# 令346 の網（撃つ前に此処へ鋳る・逐語）
#  集約 ＝ 行の集まりを一つの値へ畳む函のうち ★空の時 null を返す物★
#    ＝ jsonb_agg json_agg jsonb_object_agg json_object_agg array_agg string_agg
#       sum max min avg bool_and bool_or every
#    count は空でも 0 を返す ∴ 母の外（数へぬ）
#  当たり ＝ 上の名の直後に開き括弧が来る形。境界は英数と下線以外の明示クラス。大小文字は無視する
#  母の外 ＝ 行註(--) 帯註(/* */) 単引用の文字列の中に在る当たり（$tag$ の中は code ∴ 母の内）
#  守り ＝ 其の当たりを括弧の対応で外へ辿つた時 包む呼びの何れかが coalesce である事
#  辿りの上限 ＝ 其の当たりを含む CREATE FUNCTION の頭まで
#  分けられぬ ＝ 何れの CREATE FUNCTION にも属さぬ当たり
import io
import re
import hashlib

SRC = ("/home/hakudoukai/karo3/wt-abbrev-guard-20260912/supabase/migrations/"
       "20260909170000_snapshot_live_public_functions.sql")
s = io.open(SRC, encoding="utf-8", newline="").read()
b = s.encode("utf-8")
print("FILE lines=%d bytes=%d sha256first16=%s" % (
    s.count(chr(10)), len(b), hashlib.sha256(b).hexdigest()[:16]))

n = len(s)
mask = [False] * n
i = 0
dq = re.compile(r"\$[A-Za-z_0-9]*\$")
while i < n:
    c = s[i]
    if c == "-" and s[i:i + 2] == "--":
        j = s.find(chr(10), i)
        j = n if j < 0 else j
        for k in range(i, j):
            mask[k] = True
        i = j
        continue
    if c == "/" and s[i:i + 2] == "/*":
        j = s.find("*/", i + 2)
        j = n if j < 0 else j + 2
        for k in range(i, j):
            mask[k] = True
        i = j
        continue
    if c == "'":
        j = i + 1
        while j < n:
            if s[j] == "'":
                if s[j:j + 2] == "''":
                    j += 2
                    continue
                j += 1
                break
            j += 1
        for k in range(i, min(j, n)):
            mask[k] = True
        i = j
        continue
    if c == "$":
        m = dq.match(s, i)
        if m:
            i = m.end()
            continue
    i += 1
print("MASK masked chars=%d of %d" % (sum(1 for x in mask if x), n))

fre = re.compile(r"(?im)^[ \t]*CREATE[ \t]+(?:OR[ \t]+REPLACE[ \t]+)?FUNCTION[ \t]+([A-Za-z0-9_.]+)")
funcs = [(m.start(), m.group(1)) for m in fre.finditer(s) if not mask[m.start()]]
print("FUNCS total=%d" % len(funcs))


def line_of(p):
    return s.count(chr(10), 0, p) + 1


def owner(p):
    got = None
    for st, nm in funcs:
        if st <= p:
            got = (st, nm)
        else:
            break
    return got


def enclosing(p, floor):
    out = []
    depth = 0
    j = p - 1
    while j >= floor:
        if mask[j]:
            j -= 1
            continue
        c = s[j]
        if c == ")":
            depth += 1
        elif c == "(":
            if depth == 0:
                k = j - 1
                while k >= 0 and s[k] in " \t\r\n":
                    k -= 1
                e = k
                while k >= 0 and (s[k].isalnum() or s[k] == "_"):
                    k -= 1
                out.append(s[k + 1:e + 1].lower())
            else:
                depth -= 1
        j -= 1
    return out


AGG = ["jsonb_agg", "json_agg", "jsonb_object_agg", "json_object_agg",
       "array_agg", "string_agg", "sum", "max", "min", "avg",
       "bool_and", "bool_or", "every"]
hits = []
for a in AGG:
    pat = re.compile("(?i)(?<![A-Za-z0-9_])" + a + "(?![A-Za-z0-9_])[ \t\r\n]*\\(")
    for m in pat.finditer(s):
        hits.append((m.start(), a))
hits.sort()
print("HITS raw=%d" % len(hits))

out_of = [h for h in hits if mask[h[0]]]
live = [h for h in hits if not mask[h[0]]]
print("HITS in comment or literal (bogai)=%d / live=%d" % (len(out_of), len(live)))

guarded = []
naked = []
undec = []
for p, a in live:
    o = owner(p)
    if o is None:
        undec.append((p, a, "no function"))
        continue
    enc = enclosing(p, o[0])
    if "coalesce" in enc:
        guarded.append((p, a, o[1]))
    else:
        naked.append((p, a, o[1]))
print("SPLIT guarded=%d naked=%d undecidable=%d (unit=hit)" % (
    len(guarded), len(naked), len(undec)))

byname = {}
for p, a in live:
    byname[a] = byname.get(a, 0) + 1
print("BYNAME " + " ".join("%s=%d" % (k, byname[k]) for k in sorted(byname)))

gf = sorted(set(x[2] for x in guarded))
nf = sorted(set(x[2] for x in naked))
print("FUNCS with guarded=%d / with naked=%d (unit=function)" % (len(gf), len(nf)))

print("---- naked list (line / agg / function)")
for p, a, f in naked:
    print("   L%d %s in %s" % (line_of(p), a, f))
print("---- guarded list (line / agg / function)")
for p, a, f in guarded:
    print("   L%d %s in %s" % (line_of(p), a, f))
print("---- undecidable")
for p, a, w in undec:
    print("   L%d %s (%s)" % (line_of(p), a, w))
print("DONE")
