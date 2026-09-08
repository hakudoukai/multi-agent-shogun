
import subprocess, sys, shutil, importlib.util
from pathlib import Path

BASE = Path("scratch/ashigaru-third-2-fa06a3a1/o83_lab").resolve()
if BASE.exists(): shutil.rmtree(BASE)
BASE.mkdir(parents=True)

def g(cwd,*a,check=True):
    return subprocess.run(["git"]+list(a),cwd=str(cwd),capture_output=True,text=True,check=check)

# ---- v3 (origin/main 抽出) を読み込む ----
V3 = Path("scratch/ashigaru-third-2-fa06a3a1/o78_v3_originmain.py").resolve()
spec = importlib.util.spec_from_file_location("v3", str(V3))
v3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)

# ---- 作り物 upstream ----
up = BASE/"upstream"; up.mkdir()
g(up,"init","-b","main"); g(up,"config","user.email","a2@lab"); g(up,"config","user.name","a2")
def w(p,s):
    f=up/p; f.parent.mkdir(parents=True,exist_ok=True); f.write_text(s,encoding="utf-8")

w("scripts/a.py","print(1)\n"); w("backend/x.py","print(2)\n")
w("frontend/src/app/c.ts","export const c=1\n"); w("README.md","# r\n")
g(up,"add","-A"); g(up,"commit","-m","c1")
w("scripts/b.py","print(3)\n"); g(up,"add","-A"); g(up,"commit","-m","c2")
w("scripts/c.py","print(4)\n"); g(up,"add","-A"); g(up,"commit","-m","c3 tip")
TIP = g(up,"rev-parse","HEAD").stdout.strip()
PREV = g(up,"rev-parse","HEAD~1").stdout.strip()
OLD  = g(up,"rev-parse","HEAD~2").stdout.strip()

bare = BASE/"bare.git"
g(BASE,"clone","--bare",str(up),str(bare))

# ---- CI の形で取る (checkout@v4 + fetch-depth: 2) ----
ws = BASE/"ws"; ws.mkdir()
g(ws,"init","-b","main"); g(ws,"remote","add","origin",str(bare))
g(ws,"-c","protocol.version=2","fetch","--no-tags","--prune","--no-recurse-submodules",
  "--depth=2","origin","+%s:refs/remotes/origin/main"%TIP)
g(ws,"checkout","--progress","--force","-B","main","refs/remotes/origin/main")

local = set(v3.collect_files(ws))
print("== 作り物 repo ==")
print("  collect_files =", sorted(local))
print("  TIP=",TIP[:9]," PREV(第一親)=",PREV[:9]," OLD(depth2 の外)=",OLD[:9])
print("  commit_exists(PREV)=", v3.commit_exists(ws,PREV), " commit_exists(OLD)=", v3.commit_exists(ws,OLD))

# ---- 作り物 DB (元素 = DB の行) ----
cached = set(local) | {
  "frontend/src/other/branch_only.ts",   # 他の枝にのみ在る (INCLUDE に当たる)
  "scripts/branch_only.py",              # 同上
  "backend/gone.py",                     # 履歴で消えた (INCLUDE に当たる)
  "README.md",                           # repo に在る (一段目で落ちる)
  "docs/notes.txt",                      # DB にのみ在り INCLUDE に当たらぬ
  "notes/free.md",                       # 同上
}
print("  作り物 DB 行数 =", len(cached), "(内 現樹に在る =", len(cached & local), ")")

def branch(no_stale, prev_commit_from_db, label):
    # ★模擬★: prev_commit を DB から取る所は返り値を差し込んだ模擬である (v3:701-703 は呼ばぬ)
    if no_stale:
        return label, "STALE_SKIPPED", 0, []
    prev = prev_commit_from_db
    src = "db" if prev else "none"
    if prev and not v3.commit_exists(ws, prev):
        prev = None; src = "unresolvable"
    if not prev:
        stale = v3.compute_stale_paths(cached, local)
        return label, "FULL_SCAN(source=%s)"%src, len(stale), sorted(stale)
    stale = v3.stale_paths_from_git(ws, prev, local)
    return label, "GIT_DIFF(source=%s)"%src, len(stale), sorted(stale)

print("\n== --no-stale が在る/外れた時の分れ ==")
rows = [
  branch(True,  TIP,  "甲 --no-stale 在り (CI の現形)"),
  branch(False, None, "乙 外れ + DB が返さぬ"),
  branch(False, OLD,  "丙 外れ + 返つた commit が clone の外 (depth2)"),
  branch(False, PREV, "丁 外れ + 返つた commit が clone に在る"),
]
for lab,br,n,items in rows:
    print("  %-34s -> %-28s stale=%d %s" % (lab,br,n,items[:6]))

# ---- 二段の網 (上限 vs 実数) ----
one = {c for c in cached if c not in local}
two = v3.compute_stale_paths(cached, local)
print("\n== 二段の網 (元素 = DB の行) ==")
print("  一段目のみ (SQL で数へられる上限) =", len(one), sorted(one))
print("  二段目まで (器が現に消す数)       =", len(two), sorted(two))
print("  差 (INCLUDE に当たらぬゆゑ残る)   =", len(one-two), sorted(one-two))
