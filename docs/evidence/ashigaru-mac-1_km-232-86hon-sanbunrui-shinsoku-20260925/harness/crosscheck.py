#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 場面ごとに「原の 0byte 集合」と「再走の 0byte 集合」を両向きに比べる。
# argv: repo commit target sizes.tsv
import sys, subprocess
repo, commit, target, sizes_p = sys.argv[1:5]
out = subprocess.run(["git","-C",repo,"ls-tree","-r","-l",commit,"--",target],check=True,capture_output=True).stdout.decode()
pre = target.rstrip("/")+"/"
orig = {}
for ln in out.splitlines():
    meta, path = ln.split("\t",1); size = meta.split()[3]
    rel = path[len(pre):].split("/")
    if rel[0] not in ("03_results_contaminated_prefix","04_results_authoritative"): continue
    orig.setdefault((rel[0],rel[1]),{})["/".join(rel[2:])] = int(size)
rep = {}
for ln in open(sizes_p,encoding="utf-8"):
    s,_,p = ln.rstrip("\n").split("\t")
    if "/" not in p or not p.startswith("neg_"): continue
    sc, inner = p.split("/",1)
    rep.setdefault(sc[4:],{})[inner] = int(s)
bad = 0
print("top\tscene\t原0\t再0\t原のみ0\t再のみ0\t一致")
for (top,sc),d in sorted(orig.items()):
    o0 = {k for k,v in d.items() if v==0}
    r = rep.get(sc,{})
    r0 = {k for k,v in r.items() if v==0}
    a, b = sorted(o0-r0), sorted(r0-o0)
    ok = not a and not b
    bad += (not ok)
    print(f"{top}\t{sc}\t{len(o0)}\t{len(r0)}\t{','.join(a) or '-'}\t{','.join(b) or '-'}\t{ok}")
print(f"scenes={len(orig)} mismatch={bad} orig_zero_total={sum(sum(1 for v in d.values() if v==0) for d in orig.values())}")
sys.exit(1 if bad else 0)
