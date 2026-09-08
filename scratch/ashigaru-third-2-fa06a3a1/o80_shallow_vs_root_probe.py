#!/usr/bin/env python3
"""order80 の下拵へ: 「shallow ゆゑ HEAD^1 が無い」と「root commit ゆゑ親が無い」を
★書換 0 で★ 見分けられるかの実測。案文の判別式が現に効くかを測るのみ。DB0・push0・本物CI0。"""
import subprocess, shutil
from pathlib import Path
SCR=Path(__file__).resolve().parent; LAB=SCR/"o80_lab"
GIT=["-c","user.name=lab","-c","user.email=lab@example.invalid",
     "-c","commit.gpgsign=false","-c","init.defaultBranch=main"]
def g(cwd,*a,check=True):
    r=subprocess.run(["git"]+GIT+list(a),cwd=str(cwd),capture_output=True,text=True)
    if check and r.returncode!=0: raise SystemExit(f"git {a} rc={r.returncode}\n{r.stderr}")
    return r

if LAB.exists(): shutil.rmtree(LAB)
LAB.mkdir(parents=True)
bare=LAB/"origin.git"; bare.mkdir(); g(bare,"init","--bare","-b","main")
src=LAB/"src"; src.mkdir(); g(src,"init","-b","main")
def w(rel,t):
    p=src/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(t,encoding="utf-8")
w("scripts/a.py","A\n"); g(src,"add","-A"); g(src,"commit","-m","c1 root")
ROOT=g(src,"rev-parse","HEAD").stdout.strip()
w("scripts/b.py","B\n"); g(src,"add","-A"); g(src,"commit","-m","c2")
w("scripts/c.py","C\n"); g(src,"add","-A"); g(src,"commit","-m","c3 tip")
TIP=g(src,"rev-parse","HEAD").stdout.strip()
g(src,"remote","add","origin",str(bare)); g(src,"push","-q","origin","main")

def co(ws,sha,depth):
    ws.mkdir(); g(ws,"init","-b","main"); g(ws,"remote","add","origin",str(bare))
    args=["-c","protocol.version=2","fetch","--no-tags","--prune","--no-recurse-submodules"]
    if depth: args.append(f"--depth={depth}")
    else: args.append("--unshallow-not-used") if False else None
    args+= ["origin",f"+{sha}:refs/remotes/origin/main"]
    g(ws,*[a for a in args if a])
    g(ws,"checkout","--progress","--force","-B","main","refs/remotes/origin/main")

def probe(ws):
    p1=g(ws,"rev-parse","--verify","-q","HEAD^1",check=False)
    body=g(ws,"cat-file","-p","HEAD").stdout
    has_parent_line=any(l.startswith("parent ") for l in body.splitlines())
    shallow=(ws/".git"/"shallow").exists()
    return dict(head_p1_rc=p1.returncode, parent_line=has_parent_line, shallow=shallow)

cases=[("甲 tip depth1 (shallow ゆゑ HEAD^1 無し)",TIP,1),
       ("乙 tip depth2 (HEAD^1 在り)",TIP,2),
       ("丙 root commit depth1 (親が元から無い)",ROOT,1),
       ("丁 root commit depth2 (親が元から無い)",ROOT,2)]
rows=[]
for i,(name,sha,d) in enumerate(cases):
    ws=LAB/f"ws{i}"; co(ws,sha,d); r=probe(ws)
    # 案文の判別式: HEAD^1 が解けぬ 且つ commit body に parent 行が在る => shallow が因 => 声を上げる
    speak = (r["head_p1_rc"]!=0) and r["parent_line"]
    rows.append(dict(name=name,**r,speak=speak))
out=["| 形 | shallow file | HEAD^1 rc | commit body に parent 行 | 判別式 = 声を上げる |","|---|---|---|---|---|"]
for r in rows:
    out.append("| {name} | {shallow} | {head_p1_rc} | {parent_line} | {speak} |".format(**r))
print("\n".join(out))
