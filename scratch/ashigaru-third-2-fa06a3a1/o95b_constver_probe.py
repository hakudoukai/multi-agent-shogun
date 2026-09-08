
# order95 走②': 差 10 の因を「定数の版」で切る（讀取のみ）
# ★o78 を exec せぬ★ = L41 が backend/.env を讀みに行く ゆゑ。定数のみ ast で抜く（secret 不触）。
import pathlib, fnmatch, ast
S48 = pathlib.Path("scratch/ashigaru-third-2-fa06a3a1/order48_n_by_commit.py")
ns={}; exec(compile("\n".join(S48.read_text(encoding="utf-8").split("\n")[0:40]), str(S48), "exec"), ns)
git, consts, g2re = ns["git"], ns["consts"], ns["g2re"]

def consts_from_file(p):
    tree = ast.parse(pathlib.Path(p).read_text(encoding="utf-8"))
    out={}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0], ast.Name):
            nm=node.targets[0].id
            if nm in ("INCLUDE_PATTERNS","EXCLUDE_PATTERNS","EXCLUDE_DIRS"):
                try: out[nm]=ast.literal_eval(node.value)
                except Exception: pass
    return out

def keep(paths, INC, EXC, EXD):
    inc=[g2re(p) for p in INC]; exc=list(EXC); exd=set(EXD or set())
    out=set()
    for rel in paths:
        if not rel: continue
        if exd and any(part in exd for part in rel.split("/")): continue
        if not any(r.match(rel) for r in inc): continue
        if any(fnmatch.fnmatch(rel, p) for p in exc): continue
        out.add(rel)
    return out

C="32b145934"
tree=git("ls-tree","-r","--name-only",C).split("\n")
cA=consts(C)
cB=consts_from_file("scratch/ashigaru-third-2-fa06a3a1/o78_v3_originmain.py")
IA,EA,DA = cA["INCLUDE_PATTERNS"], cA["EXCLUDE_PATTERNS"], cA.get("EXCLUDE_DIRS",set())
IB,EB,DB = cB["INCLUDE_PATTERNS"], cB["EXCLUDE_PATTERNS"], cB.get("EXCLUDE_DIRS",set())

print("本数: INC %d/%d  EXC %d/%d  DIRS %d/%d" % (len(IA),len(IB),len(EA),len(EB),len(DA),len(DB)))
print("INC 逐語同一:", list(IA)==list(IB), "| EXC:", list(EA)==list(EB), "| DIRS:", set(DA)==set(DB))
print("INC  commit版のみ:", sorted(set(IA)-set(IB)), " main版のみ:", sorted(set(IB)-set(IA)))
print("EXC  commit版のみ:", sorted(set(EA)-set(EB)), " main版のみ:", sorted(set(EB)-set(EA)))
print("DIRS commit版のみ:", sorted(set(DA)-set(DB)), " main版のみ:", sorted(set(DB)-set(DA)))

sA=keep(tree,IA,EA,DA); sB=keep(tree,IB,EB,DB)
print()
print("同じ tree %s: commit版定数 N=%d / main版定数 N=%d / 差=%d" % (C,len(sA),len(sB),len(sB)-len(sA)))
onlyB=sorted(sB-sA); onlyA=sorted(sA-sB)
print("main版のみが拾ふ=%d / commit版のみが拾ふ=%d" % (len(onlyB),len(onlyA)))
for p in onlyB: print("  +",p)
for p in onlyA: print("  -",p)
