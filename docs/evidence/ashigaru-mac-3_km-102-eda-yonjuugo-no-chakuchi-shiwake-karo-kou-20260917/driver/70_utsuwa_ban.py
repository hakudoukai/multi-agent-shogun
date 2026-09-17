# -*- coding: utf-8 -*-
"""㋓ の拠り所⑥(退行)を測る ―― 争ふ器 path が ★60 本の内 何処に何版在るか★ を一枚に並べる。

  usage: python3 driver/70_utsuwa_ban.py <roster tsv> <main sha> <repo根> <出目dir> <path...>
  ★「測れぬ」と書く前に測る★ ―― disk の版が ★何処の枝にも無い(=未commit)★ か否かは、
  60 本の木を引けば判る。判つた事を「判らぬ」と書けば其れ自体が疵。
  出目: 71_utsuwa_ban.tsv(path × 版 × 其の版を持つ枝)
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


def blob(rev, path):
    rc, out, _ = git("rev-parse", "%s:%s" % (rev, path))
    return out.strip() if rc == 0 else None


def disk_blob(root, path):
    fp = os.path.join(root, path)
    if not os.path.isfile(fp):
        return None
    b = open(fp, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(b))
    h.update(b)
    return h.hexdigest()


def main():
    if len(sys.argv) < 6:
        sys.stderr.write(__doc__)
        return 2
    roster_tsv, main_sha, root, outdir = sys.argv[1:5]
    paths = sys.argv[5:]
    roster = []
    with open(roster_tsv, encoding="utf-8") as fh:
        for i, ln in enumerate(fh):
            if i == 0 or not ln.strip():
                continue
            c = ln.rstrip("\n").split("\t")
            roster.append((c[0], c[1]))

    rows = []
    for p in paths:
        ver = {}
        for sha, name in roster:
            b = blob(sha, p)
            if b:
                ver.setdefault(b, []).append(name)
        mb = blob(main_sha, p)
        db = disk_blob(root, p)
        for b, names in sorted(ver.items(), key=lambda kv: -len(kv[1])):
            rows.append([p, b[:12], len(names),
                         "★main と同一★" if b == mb else "-",
                         "★disk と同一★" if b == db else "-",
                         " ".join(sorted(names))[:300]])
        rows.append([p, "(main)", "-", mb[:12] if mb else "★main に無し★", "-", "-"])
        rows.append([p, "(disk)", "-", db[:12] if db else "★disk に無し★",
                     "★何れかの枝に在り★" if db in ver else "★何れの枝にも無し(未commit)★", "-"])
    K.kaku_tsv(outdir + "/71_utsuwa_ban.tsv", rows,
               header=["path", "版(blob頭12)", "其の版を持つ枝数", "main", "disk", "枝の名"])
    sys.stderr.write("path=%d / 行=%d\n" % (len(paths), len(rows)))
    return 0


sys.exit(main())
