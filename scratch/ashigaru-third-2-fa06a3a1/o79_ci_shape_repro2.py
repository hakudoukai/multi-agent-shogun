#!/usr/bin/env python3
"""order79 走2: ①直し無し版の対照 (PR#140 の Upserted 0 を再現するか) ②fetch-depth を 1 に落とした時
③squash merge 形 (直線 commit)。本物 CI 0・DB 0・push 0・作り物 repo は席の scratch 内。"""
import subprocess, shutil, io, contextlib, importlib.util
from pathlib import Path

SCR = Path(__file__).resolve().parent
LAB = SCR / "o79_lab2"
GIT = ["-c","user.name=lab","-c","user.email=lab@example.invalid",
       "-c","commit.gpgsign=false","-c","init.defaultBranch=main"]
def g(cwd,*a,check=True):
    r=subprocess.run(["git"]+GIT+list(a),cwd=str(cwd),capture_output=True,text=True)
    if check and r.returncode!=0: raise SystemExit(f"git {a} rc={r.returncode}\n{r.stderr}")
    return r

spec=importlib.util.spec_from_file_location("v3om",SCR/"o78_v3_originmain.py")
v3=importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)

def prefix_changed_paths(repo_root):
    """★PR#143 以前★ の振舞ひ (第一親の塊を持たぬ)。逐語は v3:549-556 のみ。"""
    r=subprocess.run(["git","diff","--name-only","origin/main...HEAD"],
                     cwd=str(repo_root),capture_output=True,text=True)
    if r.returncode!=0:
        r=subprocess.run(["git","diff","--name-only","HEAD~1","HEAD"],
                         cwd=str(repo_root),capture_output=True,text=True)
        return v3._names(r.stdout)
    return v3._names(r.stdout)

if LAB.exists(): shutil.rmtree(LAB)
LAB.mkdir(parents=True)

def build(kind):
    """kind='merge' = --no-ff 合流 / kind='squash' = main 上の直線 commit"""
    root=LAB/kind; root.mkdir()
    bare=root/"origin.git"; bare.mkdir(); g(bare,"init","--bare","-b","main")
    src=root/"src"; src.mkdir(); g(src,"init","-b","main")
    def w(rel,t):
        p=src/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(t,encoding="utf-8")
    w("scripts/a.py","A\n"); g(src,"add","-A"); g(src,"commit","-m","c1")
    w("scripts/b.py","B\n"); g(src,"add","-A"); g(src,"commit","-m","c2 main tip")
    if kind=="merge":
        g(src,"checkout","-b","feat")
        w("scripts/feat1.py","F1\n"); w("frontend/src/feat2.ts","F2\n")
        g(src,"add","-A"); g(src,"commit","-m","c3")
        g(src,"checkout","main")
        g(src,"merge","--no-ff","feat","-m","Merge pull request #999")
    else:
        w("scripts/feat1.py","F1\n"); w("frontend/src/feat2.ts","F2\n")
        g(src,"add","-A"); g(src,"commit","-m","squashed PR #999")
    M=g(src,"rev-parse","HEAD").stdout.strip()
    g(src,"remote","add","origin",str(bare)); g(src,"push","-q","origin","main")
    return bare,M

def checkout_v4(bare,M,depth,ws):
    g(ws,"init","-b","main"); g(ws,"remote","add","origin",str(bare))
    g(ws,"-c","protocol.version=2","fetch","--no-tags","--prune",
      "--no-recurse-submodules",f"--depth={depth}","origin",f"+{M}:refs/remotes/origin/main")
    g(ws,"checkout","--progress","--force","-B","main","refs/remotes/origin/main")

cases=[("merge",2,"直し在り"),("merge",2,"直し無し"),("merge",1,"直し在り"),
       ("squash",2,"直し在り"),("squash",1,"直し在り")]
built={}
rows=[]
for kind,depth,ver in cases:
    if kind not in built: built[kind]=build(kind)
    bare,M=built[kind]
    ws=LAB/f"ws_{kind}_d{depth}_{'fix' if ver=='直し在り' else 'nofix'}"; ws.mkdir()
    checkout_v4(bare,M,depth,ws)
    hp=subprocess.run(["git","rev-parse","--verify","-q","HEAD^1"],cwd=str(ws),
                      capture_output=True,text=True)
    buf=io.StringIO()
    with contextlib.redirect_stderr(buf):
        got = v3.changed_paths_from_git(ws) if ver=="直し在り" else prefix_changed_paths(ws)
    rows.append(dict(kind=kind,depth=depth,ver=ver,
                     has_p1=(hp.returncode==0),
                     fired=("CHANGED_ONLY_FIRST_PARENT" in buf.getvalue()),
                     n=len(got),files=sorted(got)))

out=["| 合流の形 | fetch-depth | 版 | HEAD^1 在り | 発火 | 返した本数 |","|---|---|---|---|---|---|"]
for r in rows:
    out.append("| {kind} | {depth} | {ver} | {has_p1} | {fired} | {n} |".format(**r))
out.append("")
for r in rows: out.append(f"{r['kind']}/d{r['depth']}/{r['ver']}: {r['files']}")
print("\n".join(out))
