# order341 : measure what the GO packet needs (read only, no apply, no check)
import subprocess, re, hashlib, io
REPO = "/mnt/c/DentalBI"
REF = "origin/main"
SNAP = "supabase/migrations/20260909170000_snapshot_live_public_functions.sql"
CHK = "backend/utils/abbreviation_checker.py"
TST = "tests/test_abbreviations.py"
CLS = "[^A-Za-z0-9_]"

def g(args):
    return subprocess.check_output(["git"] + args, cwd=REPO).decode("utf-8")

def show(p):
    return g(["show", REF + ":" + p])

# 1. which migrations define the function
mig = [x for x in g(["ls-tree", "-r", "--name-only", REF, "supabase/migrations/"]).split(chr(10)) if x.strip()]
print("MIGRATIONS=" + str(len(mig)))
pat = "(^|" + CLS + ")get_abbreviation_rules($|" + CLS + ")"
hit = []
for m in mig:
    s = show(m)
    ls = s.split(chr(10))
    cre = [i for i, ln in enumerate(ls, 1) if re.search(pat, ln) and "CREATE" in ln.upper()]
    men = [i for i, ln in enumerate(ls, 1) if re.search(pat, ln)]
    if men:
        hit.append((m, len(ls), men, cre))
for m, n, men, cre in hit:
    print("FILE=" + m + " split=" + str(n) + " mentions=" + str(len(men)) + " " + str(men) + " CREATE_lines=" + str(cre))
print("DEFINING_FILES=" + str(len([1 for m, n, men, cre in hit if cre])))

# 2. snapshot function body range
s = show(SNAP)
ls = s.split(chr(10))
print("SNAP split=" + str(len(ls)))
print("L722=" + ls[721][:90])
print("L723=" + ls[722][:90])
print("L761=" + ls[760])
tail = [i for i in range(724, 800) if ls[i - 1].strip() == "$function$;"]
print("first_$function$;_after_723=" + str(tail[0] if tail else None))

# 3. name collision for the new migration stamp
print("STAMP_20260912150000_exists=" + str(any("20260912150000" in m for m in mig)))
print("LAST_MIGRATION=" + sorted(mig)[-1])

# 4. which keys are actually iterated in the checker
c = show(CHK)
cl = c.split(chr(10))
for key in ["official", "corrections", "detail_required"]:
    p2 = "(^|" + CLS + ")" + key + "($|" + CLS + ")"
    hits = [i for i, ln in enumerate(cl, 1) if re.search(p2, ln)]
    itr = [i for i in hits if cl[i - 1].strip().startswith("for ")]
    print("KEY " + key + " lines=" + str(hits) + " for_lines=" + str(itr))

# 5. test file shape
t = show(TST)
tl = t.split(chr(10))
defs = [(i, ln.strip()) for i, ln in enumerate(tl, 1) if ln.strip().startswith("def ")]
print("TEST split=" + str(len(tl)) + " defs=" + str(len(defs)))
for i, d in defs:
    print("  " + str(i) + ": " + d)

# 6. the two patches on disk
for p in ["order340_coalesce_3keys.patch", "order340_py_guard.patch"]:
    b = io.open("/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-3-12e9d4bd/" + p, "rb").read()
    txt = b.decode("utf-8")
    print("PATCH " + p + " lines=" + str(txt.count(chr(10))) + " bytes=" + str(len(b)) + " sha256_16=" + hashlib.sha256(b).hexdigest()[:16] + " newfile=" + str("new file mode" in txt) + " hunks=" + str(txt.count("@@ -")))
