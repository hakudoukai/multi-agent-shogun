#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""束の巻 digest ―― 根(argv[1])の下を歩き、常なる file のみを sha256 で綴じる。

★根は argv から取る(焼き込まぬ)★。深さは無限(os.walk)。
★常なる file(S_ISREG)のみ数へる★ ―― FIFO/device は「止」に成り得る故、
開かずに lstat/stat で判じ、非regular は ★別欄で名指す★(0 と混ぜぬ)。
巻 digest = sha256( 各行「<sha256> <bytes> <path bytes>」を NUL で綴つた物 )。
path は byte で綴る故、改行を含む名でも巻は崩れぬ(刷る時のみ escape する)。

出力: stdout に 刻/根/本数/非regular/巻digest と、明細(--mei 指定時)
rc   : 0=歩けた / 2=根が無い
"""
import hashlib, os, stat, sys, time

def main(argv):
    if len(argv) < 2:
        print("usage: 10_taba_sha.py <根> [--mei]", file=sys.stderr); return 2
    root = argv[1]
    mei = "--mei" in argv[2:]
    if not os.path.isdir(root):
        print("★根が無い: %s★" % root, file=sys.stderr); return 2
    rows, hijou = [], []
    for dp, dns, fns in os.walk(root):
        dns.sort(); fns.sort()
        for fn in fns:
            p = os.path.join(dp, fn)
            st = os.lstat(p)
            if stat.S_ISLNK(st.st_mode):
                hijou.append((p, "符(symlink)")); continue
            if not stat.S_ISREG(st.st_mode):
                hijou.append((p, "常なる file に非ず mode=%o" % st.st_mode)); continue
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for buf in iter(lambda: fh.read(1 << 20), b""):
                    h.update(buf)
            rel = os.path.relpath(p, root)
            rows.append((rel, h.hexdigest(), st.st_size))
    rows.sort(key=lambda r: r[0].encode("utf-8"))
    maki = hashlib.sha256()
    for rel, sha, n in rows:
        maki.update(("%s %d " % (sha, n)).encode("utf-8"))
        maki.update(rel.encode("utf-8"))
        maki.update(b"\0")
    print("刻 %s" % time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    print("根 %s" % os.path.abspath(root))
    print("深さ 無限(os.walk)")
    print("本数(常なる file) %d" % len(rows))
    print("非regular %d" % len(hijou))
    for p, r in hijou:
        print("  ★非regular★ %s ―― %s" % (p, r))
    print("巻digest sha256=%s" % maki.hexdigest())
    if mei:
        for rel, sha, n in rows:
            print("%s %d %s" % (sha, n, rel.encode("unicode_escape").decode("ascii")))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
