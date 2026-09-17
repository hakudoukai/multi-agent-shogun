# -*- coding: utf-8 -*-
"""㋕ 重なり ―― 割当群の中で tip が他の tip の ★祖先★ に成つて居る対を悉く名指し、鎖を描く。
併せて ★60 本全体★ に対しても両向きを測る(己の 14 本の外に子孫が在れば、其れが仕分けを決める)。

  usage: python3 driver/40_kusari.py <母數tsv> <roster tsv> <出目dir>

  ★向きを取り違へぬ★: 「A が B の祖先」= `git merge-base --is-ancestor A B` rc=0 かつ A!=B。
  ★祖先である事は「内容が末端の木に在る事」を保証せぬ★ ―― 末端が後で戻して居れば、
  歴史には在るが木には無い。∴ 対毎に ★A が入れた path が末端の木で同じ blob か★ を検める。
  出目: 41_kusari.tsv(対) / 42_shison.tsv(60本に対する両向き) / 43_naiyou.tsv(内容の存否)
"""
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from importlib import import_module  # noqa: E402

K = import_module("00_kaki")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def is_anc(a, b):
    return git("merge-base", "--is-ancestor", a, b)[0] == 0


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for i, ln in enumerate(fh):
            ln = ln.rstrip("\n")
            if i == 0 or not ln.strip():
                continue
            rows.append(ln.split("\t"))
    return rows


def blob_of(rev, path):
    rc, out, _ = git("rev-parse", "%s:%s" % (rev, path))
    return out.strip() if rc == 0 else "★無★"


def main():
    if len(sys.argv) < 4:
        sys.stderr.write(__doc__)
        return 2
    bogen_tsv, roster_tsv, outdir = sys.argv[1:4]
    mine = [(r[1], r[2]) for r in read_tsv(bogen_tsv) if len(r) > 2 and r[0].isdigit()]
    roster = [(r[0], r[1]) for r in read_tsv(roster_tsv) if len(r) > 1]

    # ⑴ 割当 14 本の中の対
    pairs = []
    for asha, aname in mine:
        for bsha, bname in mine:
            if asha == bsha:
                continue
            if is_anc(asha, bsha):
                n = git("rev-list", "--count", "%s..%s" % (asha, bsha))[1].strip()
                pairs.append([aname, bname, n, "A は B の真の祖先"])
    K.kaku_tsv(outdir + "/41_kusari.tsv", pairs,
               header=["A(祖先)", "B(子孫)", "B..A間のcommit数", "判"])

    # ⑵ 60 本全体に対する両向き(★己の 14 本の外の子孫★が仕分けを決める)
    rows, naiyou = [], []
    for sha, name in mine:
        anc = [tn for ts, tn in roster if ts != sha and is_anc(ts, sha)]
        des = [tn for ts, tn in roster if ts != sha and is_anc(sha, ts)]
        same = [tn for ts, tn in roster if ts == sha and tn != name]
        rows.append([name, len(anc), len(des), " ".join(des) if des else "(無)",
                     " ".join(same) if same else "(無)"])
        # 子孫が在るなら、内容が其の木に残つて居るかを検める
        for dn in des:
            dsha = dict((n, s) for s, n in roster)[dn]
            rc, out, _ = git("diff", "-z", "--name-only", "%s..%s" % (sha, dsha))
            ps = [x for x in out.split("\0") if x]
            ok = sum(1 for p in ps if blob_of(sha, p) == blob_of(dsha, p))
            naiyou.append([name, dn, len(ps), ok, len(ps) - ok])
    K.kaku_tsv(outdir + "/42_shison.tsv", rows,
               header=["branch", "60本中の祖先tip数", "60本中の子孫tip数", "子孫の名", "同一shaの別名"])
    K.kaku_tsv(outdir + "/43_naiyou.tsv", naiyou,
               header=["A", "子孫X", "A..X差分path数", "blob同一", "blob相違"])
    sys.stderr.write("14本中の対=%d / 子孫を持つ枝=%d / 同一shaの別名を持つ枝=%d\n"
                     % (len(pairs), sum(1 for r in rows if r[2] > 0),
                        sum(1 for r in rows if r[4] != "(無)")))
    return 0


sys.exit(main())
