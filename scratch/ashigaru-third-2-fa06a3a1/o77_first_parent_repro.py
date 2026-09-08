#!/usr/bin/env python3
"""order77 の規: 三点記法が「己と己の差」になる形を作り物の小 repo で再現する。

讀取のみ・DB 0・network 0・本樹に触れぬ (作る repo は本 script の隣 o77_repro/)。
1 = file 1 本。
"""
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent / "o77_repro" / "fp"


def g(*a):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, (a, r.stderr)
    return r.stdout


def build():
    if ROOT.parent.exists():
        shutil.rmtree(ROOT.parent)
    (ROOT / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(ROOT)], capture_output=True, text=True)
    g("config", "user.email", "a2@example.invalid")
    g("config", "user.name", "a2")
    (ROOT / "scripts" / "base.py").write_text("b = 1\n")
    g("add", "-A"); g("commit", "-q", "-m", "base")
    g("checkout", "-q", "-b", "feature")
    (ROOT / "scripts" / "added.py").write_text("a = 1\n")
    g("add", "-A"); g("commit", "-q", "-m", "feature")
    g("checkout", "-q", "main")
    g("merge", "-q", "--no-ff", "-m", "merge feature", "feature")
    sha = g("rev-parse", "HEAD").strip()
    g("update-ref", "refs/remotes/origin/main", sha)   # main へ押した後の形
    return sha


def measure():
    for label, args in (("三点 origin/main...HEAD", ["diff", "--name-only", "origin/main...HEAD"]),
                        ("第一親 HEAD^1 HEAD", ["diff", "--name-only", "HEAD^1", "HEAD"])):
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
        names = [x for x in r.stdout.strip().split("\n") if x]
        print(f"{label}: rc={r.returncode} 本数={len(names)} {names}")


if __name__ == "__main__":
    build()
    measure()
