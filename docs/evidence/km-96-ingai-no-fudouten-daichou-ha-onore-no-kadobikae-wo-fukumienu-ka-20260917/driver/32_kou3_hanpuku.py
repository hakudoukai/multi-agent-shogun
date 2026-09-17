#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""甲3 ―― ★不動点を實際に狩る★。

臺帳 M が己の行 `path=<己> sha256=H …` を持つ時、欲しいのは H = sha256(M(H))。
64hex を 64hex で置換する故 ★byte 長は不変★ ∴ 写像 g: H ↦ sha256(M(H)) は
64hex の上の写像であり、不動点の有無は「g に不動点が在るか」に帰する。
本器は g を反復して當てに行く(argv[2] 回)。一致すれば ★不動点は在る★ が示され、
悉く外れれば ★此の反復では届かぬ★ が示される(「一般に無い」の證ではない ―― 其の別は紙に書く)。

usage: 32_kou3_hanpuku.py <臺帳> <反復数>
rc: 0=不動点に到達 / 1=到達せず / 2=器の誤り
"""
import hashlib, re, sys, time

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr); return 2
    man, n = argv[1], int(argv[2])
    pat = re.compile(rb"(path=" + re.escape(man.split("/")[-1].encode()) + rb" sha256=)([0-9a-f]{64})")
    print("刻 %s" % time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    mita = {}
    for i in range(1, n + 1):
        data = open(man, "rb").read()
        m = pat.search(data)
        if not m:
            print("★己の行が取れぬ(己の行が無いか、sha 欄が 64hex でない)★", file=sys.stderr); return 2
        ima = m.group(2).decode()
        h = sha(man)                       # 今の file 全体の sha
        itchi = (ima == h)
        print("反復%02d 載せた値=%s… / 實の sha=%s… / 一致=%s / 長=%d"
              % (i, ima[:16], h[:16], "★是★" if itchi else "非", len(data)))
        if itchi:
            print("★不動点に到達した(反復 %d)★" % i); return 0
        if h in mita:
            print("★輪に入つた ―― 反復%02d で見た値へ戻つた(周期 %d)★" % (mita[h], i - mita[h]))
            return 1
        mita[h] = i
        open(man, "wb").write(pat.sub(lambda mm: mm.group(1) + h.encode(), data, count=1))
    print("★%d 反復で不動点に届かず ―― 値は悉く相異(輪も無し)★" % n)
    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
