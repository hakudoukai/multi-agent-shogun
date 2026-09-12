# order344 : compare the proposals pair against the snapshot definition, on text only.
# Read only. No DB, no psql, no apply. Prints line numbers, counts and difference
# types only -- never the SQL text itself. Run count: started exactly once.
import io, hashlib

T = "/home/hakudoukai/karo3/wt-abbrev-guard-20260912/supabase/migrations/"
SNAP = T + "20260909170000_snapshot_live_public_functions.sql"
APPLY = T + "proposals/20260912_get_abbreviation_rules_coalesce_apply.sql"
ROLL = T + "proposals/20260912_get_abbreviation_rules_coalesce_rollback.sql"

def rd(p):
    return io.open(p, encoding="utf-8", newline="").read().split(chr(10))

snap, ap, rb = rd(SNAP), rd(APPLY), rd(ROLL)
print("SNAP total=%d APPLY total=%d ROLL total=%d" % (len(snap), len(ap), len(rb)))

# snapshot 1-indexed L722..L761
S = snap[721:761]
print("SNAP L722-L761 lines=%d" % len(S))
print("SNAP L722 starts with dashes=%s" % str(S[0].startswith("--")))

# rollback: drop the leading note lines that are NOT part of the snapshot block
head = 0
for i, x in enumerate(rb):
    if x.startswith("-- ====="):
        head = i
        break
print("ROLL head note lines dropped=%d (L1-L%d) ; block starts at ROLL L%d" % (head, head, head + 1))
R = rb[head:head + 40]
print("ROLL block lines=%d" % len(R))

def cmp(a, b, an, bn, base_a, base_b):
    d = []
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else None
        y = b[i] if i < len(b) else None
        if x != y:
            t = []
            if x is None or y is None:
                t.append("missing")
            else:
                if x.rstrip() == y.rstrip():
                    t.append("trailing-space")
                if x.strip() == y.strip() and x.rstrip() != y.rstrip():
                    pass
                if x.strip() != y.strip():
                    t.append("content")
            d.append((base_a + i, base_b + i, "+".join(t) or "other"))
    print("%s vs %s : diff lines=%d" % (an, bn, len(d)))
    for p in d:
        print("  DIFF %s L%d <-> %s L%d type=%s" % (an, p[0], bn, p[1], p[2]))
    return d

print("---- A : rollback block vs snapshot L722-L761")
d1 = cmp(R, S, "ROLL", "SNAP", head + 1, 722)
print("IDENTICAL=%s" % str(len(d1) == 0))
print("sha256 first16 ROLLblock=%s SNAPblock=%s" % (
    hashlib.sha256(chr(10).join(R).encode("utf-8")).hexdigest()[:16],
    hashlib.sha256(chr(10).join(S).encode("utf-8")).hexdigest()[:16]))

print("---- B : apply body vs rollback body (CREATE line to end)")
def body(v):
    for i, x in enumerate(v):
        if x.startswith("CREATE OR REPLACE FUNCTION"):
            return i, v[i:]
    return None, []
ai, AB = body(ap)
ri, RB = body(rb)
print("APPLY body starts L%d lines=%d ; ROLL body starts L%d lines=%d" % (ai + 1, len(AB), ri + 1, len(RB)))
d2 = cmp(AB, RB, "APPLY", "ROLL", ai + 1, ri + 1)
co = [p for p in d2 if p[2] == "content"]
ws = [p for p in d2 if p[2] == "trailing-space"]
print("diff content=%d trailing-space=%d" % (len(co), len(ws)))

print("---- C : trailing whitespace census (body only)")
print("APPLY body lines with trailing space=%d" % len([x for x in AB if x != x.rstrip()]))
print("ROLL body lines with trailing space=%d" % len([x for x in RB if x != x.rstrip()]))
print("SNAP block lines with trailing space=%d" % len([x for x in S if x != x.rstrip()]))

print("---- D : COALESCE census")
for n, v in (("APPLY", AB), ("ROLL", RB), ("SNAP", S)):
    print("%s COALESCE occurrences=%d on lines=%s" % (
        n, sum(x.count("COALESCE") for x in v),
        ",".join(str(i + 1) for i, x in enumerate(v) if "COALESCE" in x)))

print("---- E : round trip on text")
print("ROUNDTRIP_TO_SNAPSHOT=%s" % str(len(d1) == 0))
print("DONE")
