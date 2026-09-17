# -*- coding: utf-8 -*-
"""㋔ の一問 ―― ★他枝と同じ file を触つて衝突するか★ を 60 本全体に対して測る。

  usage: python3 driver/60_kasanari.py <母數tsv> <roster tsv> <main sha> <出目dir>

  各 tip の ★自前★ path 集合を ⑵ と同じ則(60本中の真の祖先で `rev-list --count` 最小)で作り、
  己の 14 本の集合と交はりを取る。
  ★交はりが在る=必ず衝突する、ではない★ ―― 同じ file の ★同じ行★ を別々に変へた時のみ衝突する。
  ∴ 之は ★衝突し得る所★ の一覧であつて、衝突の数ではない(数の規律3)。
  出目: 61_kasanari.tsv(己の枝 × 相手の枝 × 共有path数 × 例) / 62_kasanari_matome.tsv(己の枝毎)
"""
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from importlib import import_module  # noqa: E402

K = import_module("00_kaki")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for i, ln in enumerate(fh):
            ln = ln.rstrip("\n")
            if i == 0 or not ln.strip():
                continue
            rows.append(ln.split("\t"))
    return rows


def jimae(sha, roster):
    """⑵ と同じ則で自前 path 集合を作る。祖先 tip が無ければ None(★測れぬ★)。"""
    anc = []
    for tsha, tname in roster:
        if tsha == sha:
            continue
        if git("merge-base", "--is-ancestor", tsha, sha)[0] == 0:
            n = int(git("rev-list", "--count", "%s..%s" % (tsha, sha))[1].strip() or 0)
            anc.append((n, tname, tsha))
    if not anc:
        return None
    anc.sort(key=lambda t: (t[0], t[1]))
    rc, out, _ = git("diff", "-z", "--name-only", "%s..%s" % (anc[0][2], sha))
    if rc != 0:
        return None
    return set(x for x in out.split("\0") if x)


def main():
    if len(sys.argv) < 5:
        sys.stderr.write(__doc__)
        return 2
    bogen_tsv, roster_tsv, main_sha, outdir = sys.argv[1:5]
    mine = [(r[1], r[2]) for r in read_tsv(bogen_tsv) if len(r) > 2 and r[0].isdigit()]
    roster = [(r[0], r[1]) for r in read_tsv(roster_tsv) if len(r) > 1]
    mineset = set(s for s, _ in mine)

    sets = {}
    for sha, name in roster:
        sets[name] = jimae(sha, roster)

    rows, matome = [], []
    for sha, name in mine:
        ms = sets.get(name)
        if ms is None:
            matome.append([name, "★測れぬ★", "-", "-", "-"])
            continue
        hit, uchi, soto = 0, 0, 0
        allshare = set()
        for osha, oname in roster:
            if oname == name:
                continue
            os_ = sets.get(oname)
            if not os_:
                continue
            sh = ms & os_
            if sh:
                hit += 1
                allshare |= sh
                if osha in mineset:
                    uchi += 1
                else:
                    soto += 1
                rows.append([name, oname, "己の組" if osha in mineset else "他の組",
                             len(sh), sorted(sh)[0]])
        nondocs = sorted(p for p in allshare if not p.startswith("docs/"))
        matome.append([name, len(ms), hit, "%d/%d" % (uchi, soto),
                       ("★" + " ".join(nondocs) + "★") if nondocs else "(器の重なり無し)"])
    K.kaku_tsv(outdir + "/61_kasanari.tsv", rows,
               header=["己の枝", "相手の枝", "組", "共有path数", "例(辞書順の頭)"])
    K.kaku_tsv(outdir + "/62_kasanari_matome.tsv", matome,
               header=["branch", "自前path数", "重なる枝の数", "内訳(己の組/他の組)", "非docsの共有path"])
    sys.stderr.write("行=%d / 枝=%d / 自前が測れぬ tip=%d\n"
                     % (len(rows), len(matome), sum(1 for v in sets.values() if v is None)))
    return 0


sys.exit(main())
