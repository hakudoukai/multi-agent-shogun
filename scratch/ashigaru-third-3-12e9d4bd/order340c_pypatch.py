# order340 v2 tsuiho : forge the python-side guard patch (do NOT apply)
import subprocess, io, os
REPO = "/mnt/c/DentalBI"
REF = "origin/main"
CHK = "backend/utils/abbreviation_checker.py"
OUT = "/home/hakudoukai/multi-agent-shogun/scratch/ashigaru-third-3-12e9d4bd/order340_py_guard.patch"

s = subprocess.check_output(["git", "show", REF + ":" + CHK], cwd=REPO).decode("utf-8")
L = s.split(chr(10))
print("wc=" + str(s.count(chr(10))) + " split=" + str(len(L)))

print("---- normalizer L233-L256")
for i in range(233, 257):
    print(str(i) + ": " + L[i - 1])

def line(n):
    return L[n - 1]

# --- assert the anchors are what we measured
A244, A245, A246, A247 = line(244), line(245), line(246), line(247)
assert '"official": data.get("official", [])' in A245, A245
assert '"corrections": data.get("corrections", [])' in A246, A246
assert '"detail_required": data.get("detail_required", [])' in A247, A247
B168 = line(168)
assert B168.strip() == 'corrections = _cache.get("corrections", [])', B168
C217 = line(217)
assert C217.strip() == 'detail_required = _cache.get("detail_required", [])', C217
print("ANCHORS_OK=3")

def repl(ln):
    # ".get(X, [])"  ->  ".get(X) or []"
    a = ln.find(".get(")
    b = ln.find(", [])", a)
    assert a >= 0 and b > a, ln
    return ln[:b] + ") or []" + ln[b + len(", [])"):]

H = []
def hunk(start, count_old, count_new, olds, news_map):
    H.append("@@ -" + str(start) + "," + str(count_old) + " +" + str(start) + "," + str(count_new) + " @@")
    for n in olds:
        if n in news_map:
            H.append("-" + line(n))
        else:
            H.append(" " + line(n))
    # emit added lines in place: rebuild properly below
H = []

def build_hunk(first, last, changed):
    out = ["@@ -" + str(first) + "," + str(last - first + 1) + " +" + str(first) + "," + str(last - first + 1) + " @@"]
    pend = []
    for n in range(first, last + 1):
        if n in changed:
            pend.append(n)
            out.append("-" + line(n))
        else:
            if pend:
                for m in pend:
                    out.append("+" + repl(line(m)))
                pend = []
            out.append(" " + line(n))
    if pend:
        for m in pend:
            out.append("+" + repl(line(m)))
    return out

body = []
body.append("diff --git a/" + CHK + " b/" + CHK)
body.append("--- a/" + CHK)
body.append("+++ b/" + CHK)
body += build_hunk(165, 171, set([168]))
body += build_hunk(214, 220, set([217]))
body += build_hunk(243, 249, set([245, 246, 247]))
p = chr(10).join(body) + chr(10)
io.open(OUT, "w", encoding="utf-8", newline=chr(10)).write(p)
print("---- PATCH")
print(p)
import hashlib
print("patch_lines=" + str(p.count(chr(10))) + " bytes=" + str(len(p.encode("utf-8"))) + " sha256_16=" + hashlib.sha256(p.encode("utf-8")).hexdigest()[:16])
print("minus=" + str(len([x for x in p.split(chr(10)) if x.startswith("-") and not x.startswith("---")])) + " plus=" + str(len([x for x in p.split(chr(10)) if x.startswith("+") and not x.startswith("+++")])))
