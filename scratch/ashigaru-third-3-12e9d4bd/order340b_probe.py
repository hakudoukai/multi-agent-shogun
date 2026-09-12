# order340 v2 tsuiho probe : does SQL COALESCE alone stop the fall at L171/L220 ?
import subprocess, re, io, os
REPO = "/mnt/c/DentalBI"
REF = "origin/main"
CHK = "backend/utils/abbreviation_checker.py"

def show(path):
    return subprocess.check_output(["git", "show", REF + ":" + path], cwd=REPO).decode("utf-8")

s = show(CHK)
L = s.split(chr(10))
print("FILE=" + CHK + " wc=" + str(s.count(chr(10))) + " split=" + str(len(L)))

def seg(a, b, tag):
    print("---- " + tag + " L" + str(a) + "-L" + str(b))
    for i in range(a, b + 1):
        if 1 <= i <= len(L):
            print(str(i) + ": " + L[i - 1])

# 1. def lines
print("==== DEFS")
for i, ln in enumerate(L, 1):
    t = ln.strip()
    if t.startswith("def ") or t.startswith("async def "):
        print(str(i) + ": " + t)

# 2. three key identifiers, boundary form
print("==== KEY HITS (boundary)")
CLS = "[^A-Za-z0-9_]"
for key in ["official", "corrections", "detail_required"]:
    pat = "(^|" + CLS + ")" + key + "($|" + CLS + ")"
    hits = [i for i, ln in enumerate(L, 1) if re.search(pat, ln)]
    print(key + " lines=" + str(len(hits)) + " " + str(hits))

# 3. .get( lines
print("==== DOT-GET LINES")
for i, ln in enumerate(L, 1):
    if ".get(" in ln:
        print(str(i) + ": " + ln.strip())

# 4. rpc / supabase call lines
print("==== RPC LINES")
for i, ln in enumerate(L, 1):
    if "rpc(" in ln or "get_abbreviation_rules" in ln:
        print(str(i) + ": " + ln.strip())

# 5. len( lines
print("==== LEN LINES")
for i, ln in enumerate(L, 1):
    if "len(" in ln:
        print(str(i) + ": " + ln.strip())

# 6. cache api
print("==== CACHE API")
for i, ln in enumerate(L, 1):
    t = ln.strip()
    if t.startswith("def set_cache") or t.startswith("def get_cached_rules") or t.startswith("def clear_cache") or t.startswith("def _empty_rules"):
        print("DEF " + str(i) + ": " + t)

seg(55, 130, "loaders")
seg(131, 145, "cache api body")
seg(160, 185, "L171 area")
seg(208, 232, "L220 area")
