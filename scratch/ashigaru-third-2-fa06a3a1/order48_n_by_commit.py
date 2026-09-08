
import ast, fnmatch, re, subprocess, sys, math
REPO = "/mnt/c/DentalBI"
SRC = "scripts/sync_source_cache.py"

def git(*a):
    return subprocess.run(["/usr/bin/git","-C",REPO,*a],capture_output=True,text=True,check=True).stdout

def consts(commit):
    try:
        src = git("show", f"{commit}:{SRC}")
    except subprocess.CalledProcessError:
        return None
    tree = ast.parse(src)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ("INCLUDE_PATTERNS","EXCLUDE_PATTERNS","EXCLUDE_DIRS","BATCH_SIZE"):
                try:
                    out[name] = ast.literal_eval(node.value)
                except Exception:
                    pass
    return out

def g2re(pattern):
    out=["^"]; i=0
    while i < len(pattern):
        c=pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:[^/]+/)*"); i+=3
        elif c=="*":
            out.append("[^/]*"); i+=1
        elif c=="?":
            out.append("[^/]"); i+=1
        else:
            out.append(re.escape(c)); i+=1
    out.append("$")
    return re.compile("".join(out))

def count(commit, c):
    inc=[g2re(p) for p in c.get("INCLUDE_PATTERNS",[])]
    exc=list(c.get("EXCLUDE_PATTERNS",[]))
    exd=set(c.get("EXCLUDE_DIRS",set()) or set())
    files = git("ls-tree","-r","--name-only",commit).split("\n")
    tot=0; kept=0; dirdrop=0; incdrop=0; excdrop=0
    for rel in files:
        if not rel: continue
        tot+=1
        if exd and any(part in exd for part in rel.split("/")):
            dirdrop+=1; continue
        if not any(r.match(rel) for r in inc):
            incdrop+=1; continue
        if any(fnmatch.fnmatch(rel, p) for p in exc):
            excdrop+=1; continue
        kept+=1
    return dict(tracked=tot, dirdrop=dirdrop, incdrop=incdrop, excdrop=excdrop, N=kept)

commits = [l.split()[0] for l in git("log","--oneline","--format=%h %ad %s","--date=short","--",SRC).strip().split("\n")]
print("commit    date       N_tracked  batch(50)  tracked_total  inc  exc  dirs")
for cm in commits:
    c = consts(cm)
    if c is None: continue
    r = count(cm, c)
    bs = c.get("BATCH_SIZE", 50)
    b = math.ceil(r["N"]/bs) if r["N"] else 0
    d = git("log","-1","--format=%ad","--date=short",cm).strip()
    print(f'{cm} {d} {r["N"]:9d} {b:9d} {r["tracked"]:13d}  {len(c.get("INCLUDE_PATTERNS",[]))}  {len(c.get("EXCLUDE_PATTERNS",[]))}  {len(c.get("EXCLUDE_DIRS",set()) or set())}  bs={bs}')
