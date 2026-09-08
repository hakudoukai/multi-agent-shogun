#!/usr/bin/env python3
# order89: install.sh の `sed -i 's/\r$//'` が作業樹を汚すかを 陽性/陰性 対で測る。
# 隔離 repo のみ。本物 /mnt/c/DentalBI は ★讀取のみ★（install.sh を讀んで写すだけ）。
import os, pathlib, subprocess, json, hashlib, shutil, time

BASE = pathlib.Path("scratch/ashigaru-third-2-fa06a3a1/o89_lab").resolve()
REAL_INSTALL = pathlib.Path("/mnt/c/DentalBI/scripts/git-hooks/install.sh")
R = {"as_of": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": []}

def run(cmd, cwd=None, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, timeout=60)
    d = {"argv": cmd, "cwd": str(cwd), "rc": p.returncode, "out": p.stdout, "err": p.stderr}
    R["steps"].append(d); return d

def sha16(b): return hashlib.sha256(b).hexdigest()[:16]
def w(path, data, mode=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f: f.write(data)
    if mode: os.chmod(path, mode)

if BASE.exists(): shutil.rmtree(BASE)
BASE.mkdir(parents=True)

# 本物 install.sh を讀んで写す（本物は一指も触れぬ）
INSTALL_SRC = REAL_INSTALL.read_bytes()
R["install_src_sha16"] = sha16(INSTALL_SRC)
R["install_src_bytes"] = len(INSTALL_SRC)

LF   = b"#!/bin/bash\necho lf-hook\nexit 0\n"
CRLF = b"#!/bin/bash\r\necho crlf-hook\r\nexit 0\r\n"

def build(name, attrs):
    """attrs=None なら .gitattributes を置かぬ。置くなら其の中身(bytes)。"""
    wk = BASE / name
    wk.mkdir(parents=True)
    run(["git","init","-q","-b","main"], cwd=wk)
    run(["git","config","user.email","a2@local"], cwd=wk)
    run(["git","config","user.name","a2"], cwd=wk)
    run(["git","config","core.autocrlf","input"], cwd=wk)   # 本物と同じ
    (wk/".git"/"hooks").mkdir(parents=True, exist_ok=True)
    gh = wk/"scripts"/"git-hooks"
    w(gh/"install.sh", INSTALL_SRC, 0o755)
    w(gh/"lf_hook",   LF,   0o755)
    w(gh/"crlf_hook", CRLF, 0o755)
    if attrs is not None:
        w(wk/".gitattributes", attrs)
    run(["git","add","-A"], cwd=wk)
    run(["git","commit","-q","-m","seed"], cwd=wk)
    return wk, gh

def snap(gh, tag, wk):
    d = {"tag": tag}
    for n in ("lf_hook","crlf_hook"):
        b = (gh/n).read_bytes()
        d[n] = {"bytes": len(b), "CRLF": b.count(b"\r\n"), "sha16": sha16(b)}
    d["status"] = run(["git","status","--porcelain"], cwd=wk)["out"]
    return d

out = {}

# ── 場A: .gitattributes 無し（CRLF が追跡簿に載り作業樹にも残る形）──
wkA, ghA = build("noattr", None)
out["A_before"] = snap(ghA, "A_before", wkA)
out["A_install"] = run(["bash","scripts/git-hooks/install.sh"], cwd=wkA)
out["A_after"]  = snap(ghA, "A_after", wkA)

# ── 場B: .gitattributes 有り（本物と同じ scripts/git-hooks/* text eol=lf）──
wkB, ghB = build("withattr", b"scripts/git-hooks/* text eol=lf\n")
out["B_before"] = snap(ghB, "B_before", wkB)
out["B_install"] = run(["bash","scripts/git-hooks/install.sh"], cwd=wkB)
out["B_after"]  = snap(ghB, "B_after", wkB)

R["result"] = out
w(BASE/"o89_result.json", json.dumps(R, ensure_ascii=False, indent=1).encode("utf-8"))

def show(k):
    a, b = out[k+"_before"], out[k+"_after"]
    print("== 場"+k+" ==")
    for n in ("lf_hook","crlf_hook"):
        print("  %-9s before bytes=%3d CRLF=%d sha16=%s" % (n, a[n]["bytes"], a[n]["CRLF"], a[n]["sha16"]))
        print("  %-9s after  bytes=%3d CRLF=%d sha16=%s  %s" % (n, b[n]["bytes"], b[n]["CRLF"], b[n]["sha16"],
              "★変つた★" if a[n]["sha16"]!=b[n]["sha16"] else "不変"))
    print("  status before=[%s]" % a["status"].replace("\n","|"))
    print("  status after =[%s]" % b["status"].replace("\n","|"))
    print("  install rc=%d" % out[k+"_install"]["rc"])
show("A"); show("B")
print("install.sh 写し sha16=%s bytes=%d" % (R["install_src_sha16"], R["install_src_bytes"]))
