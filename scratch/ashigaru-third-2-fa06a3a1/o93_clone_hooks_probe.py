#!/usr/bin/env python3
# order93: 「別 clone なら hooks も別か」を陽性/陰性 対で測る（隔離のみ・network 0・本物不触）
import subprocess, pathlib, shutil, os, json

BASE = pathlib.Path("scratch/ashigaru-third-2-fa06a3a1/o93_lab").resolve()
if BASE.exists(): shutil.rmtree(BASE)
BASE.mkdir(parents=True)

ENV = dict(os.environ)
ENV.update({"GIT_AUTHOR_NAME":"a2","GIT_AUTHOR_EMAIL":"a2@lab",
            "GIT_COMMITTER_NAME":"a2","GIT_COMMITTER_EMAIL":"a2@lab",
            "GIT_TERMINAL_PROMPT":"0","GIT_CONFIG_NOSYSTEM":"1"})

def run(a, cwd=None, check=True):
    r = subprocess.run(a, cwd=cwd, env=ENV, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit("FAILED %s rc=%d\n%s\n%s" % (a, r.returncode, r.stdout, r.stderr))
    return r

def w(p, data, mode=None):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as f: f.write(data)
    if mode is not None: p.chmod(mode)

res = {}

# ① remote 役の bare（local path のみ ∴ network 0）
bare = BASE/"bare.git"
run(["git","init","--quiet","--bare",str(bare)])

# ② 作業 clone X（local path clone）
X = BASE/"X"
run(["git","clone","--quiet",str(bare),str(X)])
w(X/"seed.txt", b"seed\n")
run(["git","add","-A"], cwd=X); run(["git","commit","--quiet","-m","seed"], cwd=X)
run(["git","push","--quiet","origin","HEAD:refs/heads/main"], cwd=X)
res["X_hooks"] = run(["git","rev-parse","--git-path","hooks"], cwd=X).stdout.strip()

# ③ X の hooks へ門を置く（隔離の X ―― 本物ではない）
GATE = b'#!/bin/bash\necho "X-GATE fired"\nexit 1\n'
w(X/".git"/"hooks"/"pre-push", GATE, 0o755)

# ④ 陰性対照 = worktree W（X から張る・common dir を共有する筈）
W = BASE/"W"
run(["git","worktree","add","--quiet",str(W),"-b","wt"], cwd=X)
res["W_git_dir"]        = run(["git","rev-parse","--git-dir"], cwd=W).stdout.strip()
res["W_git_common_dir"] = run(["git","rev-parse","--git-common-dir"], cwd=W).stdout.strip()
res["W_hooks"]          = run(["git","rev-parse","--git-path","hooks"], cwd=W).stdout.strip()
w(W/"w.txt", b"w\n"); run(["git","add","-A"], cwd=W); run(["git","commit","--quiet","-m","w"], cwd=W)
rW = run(["git","push","origin","HEAD:refs/heads/wt"], cwd=W, check=False)
res["W_push_rc"]   = rW.returncode
res["W_gate_seen"] = ("X-GATE fired" in (rW.stdout + rW.stderr))

# ⑤ 陽性 = 別 clone Y（common dir が別の筈）
Y = BASE/"Y"
run(["git","clone","--quiet",str(bare),str(Y)])
res["Y_git_dir"]        = run(["git","rev-parse","--git-dir"], cwd=Y).stdout.strip()
res["Y_git_common_dir"] = run(["git","rev-parse","--git-common-dir"], cwd=Y).stdout.strip()
res["Y_hooks"]          = run(["git","rev-parse","--git-path","hooks"], cwd=Y).stdout.strip()
yh = Y/".git"/"hooks"
res["Y_pre_push_exists"] = (yh/"pre-push").exists()
res["Y_hooks_files"]     = sorted(p.name for p in yh.iterdir()) if yh.exists() else []
w(Y/"y.txt", b"y\n"); run(["git","add","-A"], cwd=Y); run(["git","commit","--quiet","-m","y"], cwd=Y)
rY = run(["git","push","origin","HEAD:refs/heads/y"], cwd=Y, check=False)
res["Y_push_rc"]   = rY.returncode
res["Y_gate_seen"] = ("X-GATE fired" in (rY.stdout + rY.stderr))

# ⑥ 判定材料（当席は判定語を書かぬ・値のみ）
res["hooks_same_X_W"] = (res["X_hooks"] == res["W_hooks"])
res["hooks_same_X_Y"] = (res["X_hooks"] == res["Y_hooks"])

with open(BASE/"o93_result.json","w",encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
for k,v in res.items(): print("%-20s %s" % (k, v))
