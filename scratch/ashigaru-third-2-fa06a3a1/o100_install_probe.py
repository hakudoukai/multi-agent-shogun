#!/usr/bin/env python3
# o100_install_probe.py -- order100 (L)
# 問: install.sh を走らせた時 .git/hooks に何が増え 何が残り 何が書き換はるか。
# 対を三組で測る。★本物の樹 /mnt/c/DentalBI は讀取のみ(copy 元)★。書くのは scratch 下の隔離樹だけ。
import hashlib, os, pathlib, shutil, subprocess, sys, time

REAL = pathlib.Path("/mnt/c/DentalBI/scripts/git-hooks")
BASE = pathlib.Path(__file__).resolve().parent / ("o100_tree_%d_%d" % (int(time.time()), os.getpid()))

def sha(b): return hashlib.sha256(b).hexdigest()[:16]
def rd(p): return pathlib.Path(p).read_bytes()
def wr(p, b):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as f: f.write(b)

def hooks_state(root):
    d = pathlib.Path(root) / ".git" / "hooks"
    out = {}
    for f in sorted(d.iterdir()):
        if f.name.endswith(".sample"): continue
        out[f.name] = (sha(f.read_bytes()), oct(f.stat().st_mode & 0o777))
    return out

def build(root, with_guard):
    root = pathlib.Path(root)
    subprocess.run(["/usr/bin/git", "init", "-q", str(root)], check=True)
    gh = root / "scripts" / "git-hooks"
    gh.mkdir(parents=True)
    # 本物から copy(讀取のみ)
    wr(gh / "install.sh", rd(REAL / "install.sh"))
    wr(gh / "pre-push",   rd(REAL / "pre-push"))
    # 対③: CRLF 入りの src(陽性) と LF のみの src(陰性)
    if with_guard:
        g = rd(pathlib.Path(__file__).resolve().parent / "o90_pre-push.bak-guard")
        g_crlf = g.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")   # 確と CRLF にする
        wr(gh / "pre-push.bak-guard", g_crlf)
    wr(gh / "lf-only-probe", b"#!/bin/bash\n# LF only\nexit 0\n")     # 対③ 陰性
    # 対②: .git/hooks に先に置く二本
    wr(root / ".git" / "hooks" / "pre-push", "MARKER-A src-にも在る名\n".encode("utf-8"))               # 陰性=上書きされる筈
    wr(root / ".git" / "hooks" / "pre-push.bak-loadshed-20260907", "MARKER-B src-に無い名\n".encode("utf-8"))  # 陽性=残る筈
    return gh

def run_arm(name, with_guard):
    root = BASE / name
    gh = build(root, with_guard)
    src_before = {p.name: sha(p.read_bytes()) for p in sorted(gh.iterdir())}
    before = hooks_state(root)
    r = subprocess.run(["/bin/bash", str(gh / "install.sh")], capture_output=True, text=True, cwd=str(root))
    after = hooks_state(root)
    src_after = {p.name: sha(p.read_bytes()) for p in sorted(gh.iterdir())}
    return dict(name=name, rc=r.returncode, out=r.stdout.strip(), err=r.stderr.strip(),
                before=before, after=after, src_before=src_before, src_after=src_after, root=str(root))

print("BASE=", BASE)
res = {}
for nm, wg in (("pos_guard_有", True), ("neg_guard_無", False)):
    res[nm] = run_arm(nm, wg)

for nm, a in res.items():
    print("=" * 8, nm, "rc=", a["rc"])
    print("  install.sh stdout:", a["out"].replace("\n", " | "))
    if a["err"]: print("  stderr:", a["err"][:200])
    print("  .git/hooks 前:", sorted(a["before"].keys()))
    print("  .git/hooks 後:", sorted(a["after"].keys()))
    grew = sorted(set(a["after"]) - set(a["before"]))
    print("  ★増えた★:", grew)
    for k in sorted(set(a["before"]) & set(a["after"])):
        same = a["before"][k][0] == a["after"][k][0]
        print("   両方に在る", k, "sha 同=", same, "mode", a["before"][k][1], "->", a["after"][k][1])
    for k in sorted(a["after"]):
        print("   後 mode", k, a["after"][k][1])
    print("  src 書換(sed -i):")
    for k in sorted(a["src_before"]):
        print("   ", k, a["src_before"][k], "->", a["src_after"].get(k), "変=", a["src_before"][k] != a["src_after"].get(k))

# 対①の判定
pos = res["pos_guard_有"]; neg = res["neg_guard_無"]
print("=" * 8, "★対①(見立て①: src に置けば .git/hooks へ配られる)★")
print("  陽性 .bak-guard 増えた =", "pre-push.bak-guard" in (set(pos["after"]) - set(pos["before"])))
print("  陰性 .bak-guard 増えた =", "pre-push.bak-guard" in (set(neg["after"]) - set(neg["before"])))
print("=" * 8, "★対②(見立て②: src に無い名は消えぬ)★")
for a in (pos, neg):
    k = "pre-push.bak-loadshed-20260907"
    print(" ", a["name"], "残つた =", k in a["after"], "sha 不変 =", a["before"].get(k, ("",))[0] == a["after"].get(k, ("x",))[0])
    print(" ", a["name"], "src に在る名 pre-push は上書きされた =", a["before"]["pre-push"][0] != a["after"]["pre-push"][0])
print("=" * 8, "★対③(install.sh L17 sed -i が src を書き換へるか)★")
print("  陽性(CRLF 入り .bak-guard) 変つた =", pos["src_before"].get("pre-push.bak-guard") != pos["src_after"].get("pre-push.bak-guard"))
print("  陰性(LF のみ lf-only-probe) 変つた =", pos["src_before"]["lf-only-probe"] != pos["src_after"]["lf-only-probe"])
print("  陰性(LF のみ install.sh 自身) 変つた =", pos["src_before"]["install.sh"] != pos["src_after"]["install.sh"])
print("走=本器 1 process(内の git/bash 呼出は o98 と同じ数へ方で 走に数へぬ)")
