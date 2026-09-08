
# order95 走③: 差 10 の因を「段の数」で切る（讀取のみ・DB0・push0）
# 2段 = INCLUDE -> EXCLUDE_PATTERNS（o85 §6 の表の形と当席が見る）
# 3段 = EXCLUDE_DIRS -> INCLUDE -> EXCLUDE_PATTERNS（order48 の count() の形）
import pathlib, fnmatch
S48 = pathlib.Path("scratch/ashigaru-third-2-fa06a3a1/order48_n_by_commit.py")
ns={}; exec(compile("\n".join(S48.read_text(encoding="utf-8").split("\n")[0:40]), str(S48), "exec"), ns)
git, consts, g2re = ns["git"], ns["consts"], ns["g2re"]

def keep(paths, INC, EXC, EXD, use_dirs):
    inc=[g2re(p) for p in INC]; exc=list(EXC); exd=set(EXD or set())
    out=set()
    for rel in paths:
        if not rel: continue
        if use_dirs and exd and any(part in exd for part in rel.split("/")): continue
        if not any(r.match(rel) for r in inc): continue
        if any(fnmatch.fnmatch(rel, p) for p in exc): continue
        out.add(rel)
    return out

for C in ("32b145934","9daaafde1","620df477e"):
    tree=git("ls-tree","-r","--name-only",C).split("\n")
    c=consts(C)
    I,E,D = c["INCLUDE_PATTERNS"], c["EXCLUDE_PATTERNS"], c.get("EXCLUDE_DIRS",set())
    s3=keep(tree,I,E,D,True); s2=keep(tree,I,E,D,False)
    d=sorted(s2-s3)
    print("commit %s : 3段 N=%d / 2段 N=%d / 差=%d" % (C,len(s3),len(s2),len(s2)-len(s3)))
    if C=="32b145934":
        print("  ★EXCLUDE_DIRS に食はれ かつ INCLUDE を通る path（2段のみが拾ふ）★ 本数=%d" % len(d))
        for p in d: print("   +",p)
        print("  当該 path の dir 成分（何の帯に当たつたか）:")
        exd=set(D)
        for p in d:
            hit=[x for x in p.split("/") if x in exd]
            print("   ",p," <- ",hit)
