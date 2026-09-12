# order339 probe -- 板354dc26f「COALESCE 欠落は現に害を成すか」を走らせず字で測る器
# 席 ashigaru-third-3 / 令339 / 走0・DB0・MCP0・讀取のみ・値は写さず行番と形のみ
import re, subprocess

REPO = "/mnt/c/DentalBI"
REF = "origin/main"
SNAP = "supabase/migrations/20260909170000_snapshot_live_public_functions.sql"
CONS = "backend/utils/abbreviation_checker.py"

def show(path):
    return subprocess.check_output(["git", "show", REF + ":" + path], cwd=REPO).decode("utf-8", "replace")

def lines_hit(s, pat):
    r = re.compile(pat)
    return sum(1 for ln in s.split(chr(10)) if r.search(ln))

def occurrences(s, pat):
    return len(re.findall(pat, s))

s = show(SNAP)
L = s.split(chr(10))
print("== 母（ref=%s / path=%s） ==" % (REF, SNAP))
print("tip16=%s" % subprocess.check_output(["git", "rev-parse", REF], cwd=REPO).decode().strip()[:16])
print("blob16=%s" % subprocess.check_output(["git", "rev-parse", REF + ":" + SNAP], cwd=REPO).decode().strip()[:16])
print("(1) 行数 wc=%d split片=%d" % (s.count(chr(10)), len(L)))
print("(2) 函 = %d (網: 行頭から CREATE OR REPLACE FUNCTION)" % lines_hit(s, "CREATE OR REPLACE FUNCTION"))
print("(3) COALESCE 行数=%d 総出現=%d (床30: 数へた単位が別)"
      % (lines_hit(s, "COALESCE"), occurrences(s, "COALESCE")))
print("(4) jsonb agg 行数=%d 総出現=%d" % (lines_hit(s, "jsonb" + "_agg"), occurrences(s, "jsonb" + "_agg")))
print("(5) 字面 COALESCE 直後に jsonb agg = %d" % occurrences(s, "COALESCE[(]jsonb" + "_agg"))

# 函の域
heads = []
for i, ln in enumerate(L):
    m = re.search("CREATE OR REPLACE FUNCTION public[.]([A-Za-z0-9_]+)", ln)
    if m:
        heads.append((i + 1, m.group(1)))
def owner(n):
    cur = "?"
    for (ln, nm) in heads:
        if ln <= n:
            cur = nm
        else:
            break
    return cur

print("== jsonb agg の一つづつ ―― 直前行が COALESCE で包むか ==")
bare = []
wrapped = []
for i, ln in enumerate(L):
    if ("jsonb" + "_agg") in ln:
        n = i + 1
        prev = L[i - 1] if i > 0 else ""
        w = "COALESCE" in prev
        (wrapped if w else bare).append((n, owner(n)))
print("包まれた=%d / 裸=%d" % (len(wrapped), len(bare)))
print("裸の在り処: " + ", ".join(["L%d(%s)" % (n, o) for n, o in bare]))
print("包みの函: " + ",".join(sorted(set([o for n, o in wrapped]))))

# 消費側
c = show(CONS)
CL = c.split(chr(10))
print("== 消費側 path=%s 行=%d ==" % (CONS, c.count(chr(10))))
for i, ln in enumerate(CL):
    if re.search("[.]get[(][^)]*, *[[][]]", ln) or re.search("for [A-Za-z_]+ in (corrections|detail_required)", ln):
        print("  L%d %s" % (i + 1, ln.strip()[:78]))
