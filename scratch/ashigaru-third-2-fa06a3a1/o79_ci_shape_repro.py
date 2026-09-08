#!/usr/bin/env python3
"""order79: CI の形 (actions/checkout@v4 fetch-depth:2) で v3 の第一親の直しが発火するかの実測。
本物の CI は走らせぬ。DB へ触れぬ。push せぬ。作り物 repo は席の scratch 内のみ。"""
import subprocess, sys, shutil, io, contextlib, importlib.util
from pathlib import Path

SCR = Path(__file__).resolve().parent
LAB = SCR / "o79_lab"
GIT = ["-c", "user.name=lab", "-c", "user.email=lab@example.invalid",
       "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]

def g(cwd, *args, check=True):
    r = subprocess.run(["git"] + GIT + list(args), cwd=str(cwd),
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"git {args} rc={r.returncode}\n{r.stderr}")
    return r

# v3 (origin/main 抽出) を import。main() は走らせぬ。
spec = importlib.util.spec_from_file_location("v3om", SCR / "o78_v3_originmain.py")
v3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)

if LAB.exists(): shutil.rmtree(LAB)
LAB.mkdir(parents=True)

# ── 作り物の「遠隔」と「源」 ──────────────────────────────
bare = LAB / "origin.git"; bare.mkdir()
g(bare, "init", "--bare", "-b", "main")
src = LAB / "src"; src.mkdir()
g(src, "init", "-b", "main")
def w(rel, txt):
    p = src / rel; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(txt, encoding="utf-8")

w("scripts/a.py", "A\n"); w("frontend/src/x.ts", "X\n")
g(src, "add", "-A"); g(src, "commit", "-m", "c1 base")
w("scripts/b.py", "B\n")
g(src, "add", "-A"); g(src, "commit", "-m", "c2 main tip before merge")
g(src, "checkout", "-b", "feat")
w("scripts/feat1.py", "F1\n"); w("frontend/src/feat2.ts", "F2\n")
g(src, "add", "-A"); g(src, "commit", "-m", "c3 on feat")
g(src, "checkout", "main")
g(src, "merge", "--no-ff", "feat", "-m", "Merge pull request #999 from lab/feat")
M = g(src, "rev-parse", "HEAD").stdout.strip()
g(src, "remote", "add", "origin", str(bare))
g(src, "push", "-q", "origin", "main")     # ★作り物の bare 宛のみ★ 本物の remote へは押さぬ

# ── checkout@v4 の再現 ────────────────────────────────
def shape_ko(ws):   # 甲 = branch push 形 (remote-tracking ref を作り -B main)
    g(ws, "init", "-b", "main"); g(ws, "remote", "add", "origin", str(bare))
    g(ws, "-c", "protocol.version=2", "fetch", "--no-tags", "--prune",
      "--no-recurse-submodules", "--depth=2", "origin", f"+{M}:refs/remotes/origin/main")
    g(ws, "checkout", "--progress", "--force", "-B", "main", "refs/remotes/origin/main")

def shape_otsu(ws): # 乙 = detached sha 形 (remote-tracking ref を作らぬ)
    g(ws, "init", "-b", "main"); g(ws, "remote", "add", "origin", str(bare))
    g(ws, "-c", "protocol.version=2", "fetch", "--no-tags", "--prune",
      "--no-recurse-submodules", "--depth=2", "origin", M)
    g(ws, "checkout", "--force", M)

def shape_hei(ws):  # 丙 = 深さ無制限 + ref 在り (対照)
    g(ws, "clone", "-q", str(bare), ".")

rows = []
for name, fn in (("甲 branch形 depth2", shape_ko),
                 ("乙 detached形 depth2", shape_otsu),
                 ("丙 full clone 対照", shape_hei)):
    ws = LAB / ("ws_" + name.split()[0]); ws.mkdir()
    fn(ws)
    three = subprocess.run(["git","diff","--name-only","origin/main...HEAD"],
                           cwd=str(ws), capture_output=True, text=True)
    head = v3._rev_parse(ws, "HEAD"); base = v3._rev_parse(ws, "origin/main")
    shallow = (ws / ".git" / "shallow").exists()
    detached = g(ws, "symbolic-ref", "-q", "HEAD", check=False).returncode != 0
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        got = v3.changed_paths_from_git(ws)
    fired = "CHANGED_ONLY_FIRST_PARENT" in buf.getvalue()
    rows.append(dict(name=name, shallow=shallow, detached=detached,
                     three_rc=three.returncode,
                     three_n=len(v3._names(three.stdout)),
                     head=head[:9], base=(base[:9] if base else "(解けぬ)"),
                     eq=(bool(head) and head == base), fired=fired,
                     n=len(got), files=sorted(got)))

out = ["| 形 | shallow | detached | 三点rc | 三点本数 | HEAD | origin/main | 一致 | 発火 | 返した本数 |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    out.append("| {name} | {shallow} | {detached} | {three_rc} | {three_n} | {head} | {base} | {eq} | {fired} | {n} |".format(**r))
out.append("")
for r in rows:
    out.append(f"{r['name']}: files={r['files']}")
print("\n".join(out))
