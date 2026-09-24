#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 86本の 0byte を commit object から列挙し、raw/sizes.tsv（再走）と突き合はせて ㋐/㋑/㋒ に切る。
# argv: repo commit target_path sizes.tsv out_tsv out_summary
import sys, subprocess, re
from collections import Counter
repo, commit, target, sizes_p, out_tsv, out_sum = sys.argv[1:7]
def git(*a):
    return subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True).stdout
lines = git("ls-tree", "-r", "-l", commit, "--", target).decode("utf-8").splitlines()
allf, zero = [], []
for ln in lines:
    meta, path = ln.split("\t", 1)
    mode, typ, blob, size = meta.split()
    allf.append(path)
    if size == "0":
        zero.append((path, blob))
sizes = {}
for ln in open(sizes_p, encoding="utf-8"):
    s, sha, p = ln.rstrip("\n").split("\t")
    sizes[p] = int(s)
STREAM = re.compile(r"^(source|process_unread|agent_is_busy_direct)\.(stdout|stderr)$")
rows, cls = [], Counter()
pre = target.rstrip("/") + "/"
for path, blob in zero:
    rel = path[len(pre):]
    parts = rel.split("/")
    top, scen, inner = parts[0], parts[1], "/".join(parts[2:])
    ver, cli = scen.split("_")[0], scen.split("_")[1]
    base = parts[-1]
    repro_key = f"neg_{scen}/{inner}"
    repro = sizes.get(repro_key)
    pos_key = f"pos_{ver}_{cli}_absent/{inner}"
    pos = sizes.get(pos_key)
    m = STREAM.match(base)
    if m:
        rc_path = f"{pre}{top}/{scen}/{m.group(1)}.rc"
        try:
            rcv = git("show", f"{commit}:{rc_path}").decode().strip()
        except subprocess.CalledProcessError:
            rcv = "MISSING"
        sib = f"{m.group(1)}.rc={rcv}"
        instr_ok = bool(re.fullmatch(r"-?\d+", rcv))
        if repro is None:
            c, why = "㋑", "再走に同名file無"
        elif repro > 0:
            c, why = "㋒", f"再走で {repro}byte"
        elif not instr_ok:
            c, why = "㋑", "原の同段 rc 欠"
        elif pos is None or pos == 0:
            c, why = "㋑", "陽性對照で非空に成らぬ(捕へる器の疵)"
        else:
            c, why = "㋐", "再走0byte・同段rc在・陽性對照>0"
    else:  # flags/shogun_idle_testagent
        sib = "touch(driver L62-64 相当)"
        codex_flag = [k for k in sizes if k.startswith(f"neg_{ver}_codex") and k.endswith("/flags/shogun_idle_testagent")]
        if repro is None:
            c, why = "㋑", "再走に flag 無"
        elif repro > 0:
            c, why = "㋒", f"再走で {repro}byte"
        elif cli != "claude" or codex_flag:
            c, why = "㋑", "codex でも flag が立つ(對照が効かぬ)"
        else:
            c, why = "㋐", "再走0byte(claude のみ touch)・codex 場面に flag 0件"
            pos = f"codex_flag={len(codex_flag)}"
    cls[c] += 1
    rows.append((rel, blob, base, sib, repro_key, repro, pos_key if m else "neg_*_codex*/flags", pos, c, why))
with open(out_tsv, "w", encoding="utf-8") as f:
    f.write("rel\tblob\tbasename\t同段\t再走key\t再走byte\t陽性key\t陽性byte\t類\t根\n")
    for r in rows:
        f.write("\t".join("" if x is None else str(x) for x in r) + "\n")
bb = Counter((r[2], r[8]) for r in rows)
with open(out_sum, "w", encoding="utf-8") as f:
    f.write(f"commit={commit}\ntarget={target}\nls_tree_total={len(allf)}\nzero_total(母數)={len(zero)}\n")
    for k in ("㋐", "㋑", "㋒"):
        f.write(f"{k}={cls[k]}/{len(zero)}\n")
    f.write(f"sum_check={sum(cls.values())}=={len(zero)} -> {sum(cls.values())==len(zero)}\n")
    for (b, c), n in sorted(bb.items()):
        f.write(f"basename={b}\t類={c}\t{n}\n")
    f.write(f"blob_all_empty={all(b=='e69de29bb2d1d6434b8b29ae775ad8c2e48c5391' for _,b in zero)}\n")
