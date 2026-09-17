#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""㋐-0 ★根を固定する器★ ―― 走査の前に「何処を・何時・何本・rc幾つ」を紙へ置く。

歩き根は argv[1] ―― ★一本★(既定 = <repo>/docs/evidence)。深さ無制限(実測値を刷る)。
★S_ISREG 以外は開かぬ★(FIFO を open すると「止」に成る ―― km-114 で 10分止まつた)。
非通常が在れば ★本数だけでなく名を刷る★(「1本在つた」は名無しでは検められぬ)。

出 = raw/00_ne.txt / raw/00_hijoujou.tsv / raw/00_file_ichiran.tsv
"""
import os
import stat
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from kaki import kaku, kaku_tsv, esc  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(BUNDLE)))


def main(argv):
    walk_root = os.path.abspath(argv[1]) if argv[1:] else os.path.join(REPO, "docs", "evidence")
    outdir = os.path.abspath(argv[2]) if argv[2:] else os.path.join(BUNDLE, "raw")
    os.makedirs(outdir, exist_ok=True)
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    files, hijou, dirs = [], [], 0
    deepest = 0
    total = 0
    for dp, dns, fns in os.walk(walk_root):
        dirs += 1
        d = dp[len(walk_root):].count(os.sep)
        if d > deepest:
            deepest = d
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, walk_root)
            try:
                st = os.lstat(p)
            except OSError as e:
                hijou.append((rel, "lstat 不能", type(e).__name__))
                continue
            m = st.st_mode
            if stat.S_ISREG(m):
                files.append((rel, st.st_size))
                total += st.st_size
            else:
                kind = ("symlink" if stat.S_ISLNK(m) else
                        "fifo" if stat.S_ISFIFO(m) else
                        "socket" if stat.S_ISSOCK(m) else
                        "chardev" if stat.S_ISCHR(m) else
                        "blockdev" if stat.S_ISBLK(m) else "不明")
                tgt = ""
                if stat.S_ISLNK(m):
                    try:
                        tgt = os.readlink(p)
                    except OSError:
                        tgt = "(readlink 不能)"
                hijou.append((rel, kind, tgt))

    t1 = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    kaku_tsv(os.path.join(outdir, "00_file_ichiran.tsv"),
             [(esc(r), b) for r, b in sorted(files)],
             header=["rel_path_esc", "bytes"])
    kaku_tsv(os.path.join(outdir, "00_hijoujou.tsv"),
             [(esc(a), b, esc(c)) for a, b, c in sorted(hijou)],
             header=["rel_path_esc", "種", "註_or_symlink先"])

    L = []
    L.append("★根の固定 ―― 走査の前に置く★")
    L.append("歩き根(絶対)= %s" % walk_root)
    L.append("歩き根は★一本★である(第二の根を歩いて居らぬ)")
    L.append("刻(歩き始め)= %s" % t0)
    L.append("刻(歩き終り)= %s" % t1)
    L.append("dir数= %d" % dirs)
    L.append("file数(S_ISREG のみ)= %d" % len(files))
    L.append("byte和(S_ISREG のみ)= %d" % total)
    L.append("最深(歩き根を 0 とする)= %d" % deepest)
    L.append("非通常(S_ISREG でない物)= %d 本 ―― 名は raw/00_hijoujou.tsv" % len(hijou))
    warui = [(r, b) for r, b in files if any(c in r for c in "\t\r\n")]
    L.append("★行器を壊す名★(TAB/改行を含む)= %d 本" % len(warui))
    for r, b in sorted(warui):
        L.append("  壊す名: %s  bytes=%d" % (esc(r), b))
    L.append("  ∴ 本弾の TSV は rel_path_esc(\\t \\n \\r \\\\ へ逃がした形)で書く。")
    L.append("  ★素の TSV で数へると byte欄が 5 ずれ、行が +2 に成る(実測)★")
    mine = [(r, b) for r, b in files if r.startswith(os.path.basename(BUNDLE) + os.sep)]
    L.append("★己の束(本弾)が母数に入つて居る★= %d 本 / %d byte ―― 除いた数ではない" %
             (len(mine), sum(b for _, b in mine)))
    for rel, kind, tgt in sorted(hijou):
        L.append("  非通常: %s  種=%s  %s" % (rel, kind, tgt))
    L.append("")
    L.append("★此の数が意味せぬ事★")
    L.append("・queue/ 配下・他席の worktree・他 repo は★歩いて居らぬ★(0 ではなく★測つて居らぬ★)")
    L.append("・byte和 は disk 上の実体の和であつて、git object の大きさではない")
    L.append("・file数 は★此の刻★の disk 状態である ―― 走る席が在れば次の刻には動く")
    kaku(os.path.join(outdir, "00_ne.txt"), "\n".join(L))
    print("00_ne rc=0 file=%d dir=%d byte=%d 深=%d 非通常=%d" %
          (len(files), dirs, total, deepest, len(hijou)))
    return 0


sys.exit(main(sys.argv))
