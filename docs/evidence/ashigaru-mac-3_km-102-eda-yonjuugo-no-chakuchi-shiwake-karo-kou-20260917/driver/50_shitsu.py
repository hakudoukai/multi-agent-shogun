# -*- coding: utf-8 -*-
"""㋔ の下拵へ ―― ★着地させたら main に何が齎されるか★ と ★捨てたら何が失はれるか★ を path 毎に測る。

  usage: python3 driver/50_shitsu.py <母數tsv> <sokutei tsv> <main sha> <repo根> <出目dir>

  一本の枝の ⑵(自前)の path を三つの木と引き比べる:
    甲 main の木   : 同一 / 相違 / main に無し   → ★main に齎す物★ = 相違+無し
    乙 作業樹(disk): 同一 / 相違 / disk に無し   → ★現物が手許に在るか★
  ★disk の blob は git を通さず己で算ける★(sha1("blob <n>\\0"+bytes)) ―― index を触らぬ為。
  ★「disk に在る」は「記録が残る」ではない★ ―― 枝を捨てれば ★誰が何時何故★ 置いたかの記録は失はれる。
  出目: 51_shitsu.tsv(枝毎) / 52_path.tsv(path 毎・非 docs のみ)
"""
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from importlib import import_module  # noqa: E402

K = import_module("00_kaki")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def tree_map(rev):
    # ★--full-tree が要る★: `git ls-tree` は ★cwd の prefix で絞る★ ―― 束(docs/evidence/…)の中から
    # 呼ぶと、其の path が枝の木に無い限り ★rc=0 の儘 空★ を返す(黙つた零)。
    # 實測: 束の中 0 records / --full-tree 1670 records(同じ commit)。`git diff` は prefix で絞らぬ(1167=1167)。
    rc, out, _ = git("ls-tree", "-r", "-z", "--full-tree", rev)
    m = {}
    if rc != 0:
        return m
    for rec in out.split("\0"):
        if not rec.strip():
            continue
        meta, path = rec.split("\t", 1)
        mode, typ, sha = meta.split()
        m[path] = sha
    return m


def disk_blob(root, path):
    fp = os.path.join(root, path)
    try:
        if not os.path.isfile(fp) or os.path.islink(fp):
            return None
        with open(fp, "rb") as fh:
            b = fh.read()
    except OSError:
        return "★讀めぬ★"
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(b))
    h.update(b)
    return h.hexdigest()


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for i, ln in enumerate(fh):
            ln = ln.rstrip("\n")
            if i == 0 or not ln.strip():
                continue
            rows.append(ln.split("\t"))
    return rows


def main():
    if len(sys.argv) < 6:
        sys.stderr.write(__doc__)
        return 2
    bogen_tsv, sok_tsv, main_sha, root, outdir = sys.argv[1:6]
    mine = [(r[1], r[2]) for r in read_tsv(bogen_tsv) if len(r) > 2 and r[0].isdigit()]
    kiten = {}
    for r in read_tsv(sok_tsv):
        kiten[r[0]] = r[11]          # ★key は branch(第1欄)★ ―― sha40(第2欄)で引いて ★基点が引けぬ★ に倒れた(fail-closed で鳴つた)
    roster = {}
    for r in read_tsv(outdir + "/21_roster.tsv"):
        roster[r[1]] = r[0]
    mainmap = tree_map(main_sha)
    # ★陽性対照★ ―― 空の木を「main に無し」と読み違へぬ為、先に木が引けて居る事を検める(fail-closed)。
    if len(mainmap) < 2 or "CLAUDE.md" not in mainmap:
        sys.stderr.write("★main の木が引けぬ(件数=%d)★ ―― 一行も書かず止まる\n" % len(mainmap))
        return 5

    rows, prows = [], []
    for sha, name in mine:
        bsha = roster.get(kiten.get(name, ""), "")
        if not bsha:
            rows.append([name, "★基点が引けぬ★"] + ["-"] * 8)
            continue
        rc, out, _ = git("diff", "-z", "--name-only", "%s..%s" % (bsha, sha))
        paths = [x for x in out.split("\0") if x]
        xmap = tree_map(sha)
        if len(xmap) < 2:
            sys.stderr.write("★枝の木が引けぬ: %s★ ―― 一行も書かず止まる\n" % name)
            return 5
        same_main = diff_main = none_main = 0
        same_disk = diff_disk = none_disk = 0
        for p in paths:
            xb = xmap.get(p)
            mb = mainmap.get(p)
            db = disk_blob(root, p)
            if xb is None:
                none_main += 1  # 枝で消された path(木に無い)
            elif mb is None:
                none_main += 1
            elif mb == xb:
                same_main += 1
            else:
                diff_main += 1
            if db is None:
                none_disk += 1
            elif xb is not None and db == xb:
                same_disk += 1
            else:
                diff_disk += 1
            if not p.startswith("docs/"):
                prows.append([name, p,
                              "同一" if (mb and xb and mb == xb) else ("main に無し" if mb is None else "★相違★"),
                              "同一" if (db and xb and db == xb) else ("disk に無し" if db is None else "★相違★")])
        rows.append([name, len(paths), same_main, diff_main, none_main,
                     diff_main + none_main, same_disk, diff_disk, none_disk,
                     "%.0f%%" % (100.0 * same_disk / len(paths)) if paths else "-"])
    K.kaku_tsv(outdir + "/51_shitsu.tsv", rows, header=[
        "branch", "(2)path数", "main同一", "main相違", "mainに無し",
        "★mainへ齎す★", "disk同一", "disk相違", "diskに無し", "disk同一率"])
    K.kaku_tsv(outdir + "/52_path.tsv", prows, header=["branch", "path", "vs_main", "vs_disk"])
    sys.stderr.write("枝=%d / 非docs path 行=%d\n" % (len(rows), len(prows)))
    return 0


sys.exit(main())
