
# order95: §12 残 2 を測る（讀取のみ・DB 0・push 0）
# 借り: order48_n_by_commit.py の L1-40（git / consts / g2re）を exec で再利用。
# 写し: 判定 3 段は同器の count() L47-56 の逐語。kept+=1 を keep.append(rel) に変へた。
#       ★元器は前紙(o85 §9)の証拠ゆゑ書き換へぬと判じ、写す方を選んだ。紙に開示する。★
import pathlib, fnmatch, json, subprocess

SRCF = pathlib.Path("scratch/ashigaru-third-2-fa06a3a1/order48_n_by_commit.py")
lines = SRCF.read_text(encoding="utf-8").split("\n")
borrowed = "\n".join(lines[0:40])          # L1-40
ns = {}
exec(compile(borrowed, str(SRCF), "exec"), ns)
git, consts, g2re = ns["git"], ns["consts"], ns["g2re"]

def keep_set(paths, c):
    """判定 3 段 = order48 count() L47-56 の逐語（順・演算子とも同じ）。集合を返す。"""
    inc=[g2re(p) for p in c.get("INCLUDE_PATTERNS",[])]
    exc=list(c.get("EXCLUDE_PATTERNS",[]))
    exd=set(c.get("EXCLUDE_DIRS",set()) or set())
    keep=[]; tot=0; dirdrop=0; incdrop=0; excdrop=0
    for rel in paths:
        if not rel: continue
        tot+=1
        if exd and any(part in exd for part in rel.split("/")):
            dirdrop+=1; continue
        if not any(r.match(rel) for r in inc):
            incdrop+=1; continue
        if any(fnmatch.fnmatch(rel, p) for p in exc):
            excdrop+=1; continue
        keep.append(rel)
    return set(keep), dict(tracked=tot,dirdrop=dirdrop,incdrop=incdrop,excdrop=excdrop,N=len(keep))

def tree_paths(commit):
    return git("ls-tree","-r","--name-only",commit).split("\n")

A="9daaafde1"; B="32b145934"
cA=consts(A); cB=consts(B)

print("### 走① 10 本の path")
same = {k:(cA.get(k)==cB.get(k)) for k in ("INCLUDE_PATTERNS","EXCLUDE_PATTERNS","EXCLUDE_DIRS")}
print("定数 逐語同一:", same)
sA,rA = keep_set(tree_paths(A), cA)
sB,rB = keep_set(tree_paths(B), cB)
print("N(%s)=%d  N(%s)=%d  差=%d" % (A,rA["N"],B,rB["N"],rB["N"]-rA["N"]))
onlyB = sorted(sB-sA); onlyA = sorted(sA-sB)
print("B のみ(増えた) 本数=%d / A のみ(消えた) 本数=%d" % (len(onlyB),len(onlyA)))
print("--- B のみ ---")
for p_ in onlyB: print("  +",p_)
print("--- A のみ ---")
for p_ in onlyA: print("  -",p_)

print()
print("### 走② tree 対 index（今の時点のみ・当時の index は戻せぬ）")
cH=consts("HEAD")
head = git("rev-parse","--short","HEAD").strip()
sT,rT = keep_set(tree_paths("HEAD"), cH)
sI,rI = keep_set(git("ls-files").split("\n"), cH)
print("HEAD=%s  N(tree)=%d  N(index)=%d  差=%d" % (head,rT["N"],rI["N"],rI["N"]-rT["N"]))
dT = sorted(sT-sI); dI = sorted(sI-sT)
print("tree のみ 本数=%d / index のみ 本数=%d" % (len(dT),len(dI)))
for p_ in dT[:20]: print("  tree only:",p_)
for p_ in dI[:20]: print("  index only:",p_)
st = git("status","--porcelain").strip()
print("status --porcelain 行数=%d" % (len(st.split("\n")) if st else 0))
